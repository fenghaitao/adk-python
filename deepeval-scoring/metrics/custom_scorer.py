# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Custom scorer for prompt optimization using our domain-specific metrics.

This scorer uses evaluate_score from score.py to perform comprehensive evaluation
of DML implementations during prompt optimization.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Union
from pathlib import Path
import sys

from deepeval.dataset.golden import Golden, ConversationalGolden
from deepeval.optimizer.scorer import Scorer
from deepeval.optimizer.types import PromptConfiguration, ModuleId

# Import evaluate_score from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from score import evaluate_score


class CustomScorer(Scorer):
    """Custom scorer using comprehensive evaluation for DML code.

    This scorer overrides the parent Scorer class to use our domain-specific
    evaluation system (score.py) instead of individual metrics. It integrates
    with DeepEval's prompt optimization algorithms while providing detailed
    feedback from multiple evaluation dimensions.

    The scorer:
    1. Generates actual output using the model callback
    2. Evaluates using score.py's evaluate_score function
    3. Stores detailed results for feedback generation
    4. Returns overall scores for optimization
    """

    def __init__(
        self,
        model_callback,
        metrics,
        max_concurrent: int = 10,
        throttle_seconds: float = 0.0,
        evaluation_model: str = "iflow/qwen3-coder-plus",
        scoring_mode: str = "llm",
        device: str = "wdt",
        agent: str = "adk-python",
        mlflow_tracker=None,
    ):
        """Initialize the custom scorer.

        Args:
            model_callback: Callback function to generate outputs
            metrics: List of metrics (kept for compatibility, not used)
            max_concurrent: Maximum concurrent evaluations
            throttle_seconds: Throttle between evaluations
            evaluation_model: LLM model to use for evaluation
            scoring_mode: Scoring mode (llm, deterministic, hybrid)
            device: Device name for evaluation (e.g., wdt, uart, pci)
            agent: Agent type for behavior evaluation
            mlflow_tracker: Optional MLflow tracker for logging
        """
        # Initialize parent class
        super().__init__(
            model_callback=model_callback,
            metrics=metrics,
            max_concurrent=max_concurrent,
            throttle_seconds=throttle_seconds,
            objective_scalar=None,
        )

        self.evaluation_model = evaluation_model
        self.scoring_mode = scoring_mode
        self.device = device
        self.agent = agent
        self.mlflow_tracker = mlflow_tracker

        # Store results for each (prompt_configuration_id, workdir) combination
        # Key: (prompt_config_id, workdir), Value: evaluation results
        self.results: Dict[tuple, Dict] = {}

    def _score_one(
        self,
        prompt_configuration: PromptConfiguration,
        golden: Union[Golden, ConversationalGolden],
    ) -> float:
        """Score one golden example by generating output and evaluating.

        This method overrides the parent implementation to:
        1. Generate actual output using model callback
        2. Use evaluate_score to get comprehensive evaluation
        3. Store results in self.results for feedback
        4. Return overall score for optimization

        Args:
            prompt_configuration: Current prompt configuration
            golden: Golden example with input/expected output
  
        Returns:
            Overall score (0.0 to 1.0)
        """
        # Generate actual output using the model callback
        # This returns the path to actual_out/itemX/adk_openspec_project
        actual_output = self.generate(prompt_configuration.prompts, golden)

        # Use the actual_output path as workdir for evaluation
        # This should be the path to the adk_openspec_project folder
        workdir = actual_output

        # Use the device name passed during initialization
        device_name = self.device

        # Get reference path from golden.expected_output
        reference_dir = str(golden.expected_output) if golden.expected_output else None

        # Create result key using prompt configuration ID and workdir
        result_key = (prompt_configuration.id, workdir)

        try:
            # Use evaluate_score to get comprehensive evaluation
            eval_results = evaluate_score(
                workdir=workdir,
                device=device_name,
                model=self.evaluation_model,
                output="score_temp.md",  # Temporary output
                format="json",
                result_only=False,  # Include behavior evaluation
                behavior_only=False,
                scoring_mode=self.scoring_mode,
                agent=self.agent,
                reference_dir=reference_dir,
                mlflow_tracker=self.mlflow_tracker,  # Pass MLflow tracker
            )

            # Store results for feedback generation using (prompt_config_id, workdir) key
            self.results[result_key] = eval_results

            # Return overall score
            return eval_results["overall_score"]
  
        except Exception as e:
            print(f"⚠️  Warning: Failed to evaluate {workdir}: {e}")
            # Store error in results using (prompt_config_id, workdir) key
            self.results[result_key] = {
                "overall_score": 0.0,
                "error": str(e)
            }
            return 0.0

    def get_minibatch_feedback(
        self,
        prompt_configuration: PromptConfiguration,
        module: ModuleId,
        minibatch: Union[List[Golden], List[ConversationalGolden]],
    ) -> str:
        """Generate feedback from a minibatch of golden examples.

        This method overrides the parent implementation to:
        1. Score each golden in the minibatch (calls _score_one)
        2. Collect metric reasons from self.results
        3. Return aggregated feedback for prompt improvement

        Args:
            prompt_configuration: Current prompt configuration
            module: Module identifier
            minibatch: List of golden examples
   
        Returns:
            Feedback string with metric reasons
        """
        reasons: List[str] = []

        for golden in minibatch:
            # The workdir is returned by model_callback and used in _score_one
            # Extract it from golden.actual_output which points to the project path
            workdir = str(golden.actual_output)

            # Create result key using prompt configuration ID and workdir
            result_key = (prompt_configuration.id, workdir)

            # Check if result already exists, if not, score the golden
            if result_key not in self.results:
                # Score the golden (this will populate self.results)
                self._score_one(prompt_configuration, golden)

            # Collect reasons from results
            if result_key in self.results:
                eval_results = self.results[result_key]
 
                # Check for errors
                if "error" in eval_results:
                    reasons.append(f"Evaluation Error: {eval_results['error']}")
                    continue

                # Collect reasons from code evaluation
                if "code_results" in eval_results and eval_results["code_results"]:
                    code_results = eval_results["code_results"]
                    for metric_name, metric_result in code_results.get("metrics", {}).items():
                        if "reason" in metric_result and metric_result["reason"]:
                            reasons.append(f"{metric_name}: {metric_result['reason']}")

                # Collect reasons from behavior evaluation
                if "behavior_results" in eval_results and eval_results["behavior_results"]:
                    behavior_results = eval_results["behavior_results"]
                    for metric_name, metric_result in behavior_results.get("metrics", {}).items():
                        if "reason" in metric_result and metric_result["reason"]:
                            reasons.append(f"{metric_name}: {metric_result['reason']}")

                # Collect reasons from deterministic evaluation
                if "deterministic_results" in eval_results and eval_results["deterministic_results"]:
                    det_results = eval_results["deterministic_results"]
                    if "issues" in det_results:
                        for issue in det_results["issues"][:3]:  # Limit to top 3 issues
                            reasons.append(f"Deterministic Issue: {issue}")

        # Remove duplicates while preserving order
        if not reasons:
            return ""

        unique: List[str] = []
        seen = set()
        for reason in reasons:
            if reason not in seen:
                unique.append(reason)
                seen.add(reason)

        # Return top 8 reasons (configurable limit)
        return "\n---\n".join(unique[:8])
