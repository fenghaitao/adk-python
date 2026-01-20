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

This scorer wraps our custom metrics (CodeCorrectnessMetric, TestCoverageMetric, etc.)
and provides a unified interface compatible with DeepEval's optimization algorithms.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path

from deepeval.test_case import LLMTestCase

from .code_correctness import CodeCorrectnessMetric
from .test_coverage import TestCoverageMetric
from .code_style import CodeStyleMetric
from .agent_behavior import AgentBehaviorMetric
from .compilation_metric import CompilationMetric
from .test_pass_rate_metric import TestPassRateMetric


class CustomScorer:
    """Custom scorer using domain-specific metrics for DML code evaluation.
    
    This scorer combines multiple metrics to evaluate the quality of generated
    DML implementations based on specifications. It's designed to work with
    DeepEval's prompt optimization algorithms.
    
    Metrics:
    - CodeCorrectnessMetric: Evaluates if code correctly implements the spec
    - TestCoverageMetric: Checks test coverage and quality
    - CodeStyleMetric: Evaluates code style and best practices
    - AgentBehaviorMetric: Evaluates agent's problem-solving approach
    - CompilationMetric: Checks if code compiles successfully
    - TestPassRateMetric: Measures test pass rate
    """
    
    def __init__(
        self,
        model: str = "iflow/qwen3-coder-plus",
        weights: Optional[Dict[str, float]] = None
    ):
        """Initialize the custom scorer.
        
        Args:
            model: LLM model to use for evaluation
            weights: Weight for each metric (must sum to 1.0)
                    Default: equal weights for all metrics
        """
        self.model = model
        
        # Default weights if not provided
        if weights is None:
            weights = {
                "Code Correctness": 0.25,
                "Test Coverage": 0.20,
                "Code Style": 0.15,
                "Agent Behavior": 0.15,
                "Compilation": 0.15,
                "Test Pass Rate": 0.10
            }
        
        # Validate weights sum to 1.0
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0 (got {total_weight})")
        
        self.weights = weights
        
        # Initialize metrics
        self.metrics = {
            "Code Correctness": CodeCorrectnessMetric(model=model, threshold=0.8),
            "Test Coverage": TestCoverageMetric(model=model, threshold=0.7),
            "Code Style": CodeStyleMetric(model=model, threshold=0.9),
            "Agent Behavior": AgentBehaviorMetric(model=model, threshold=0.7),
            "Compilation": CompilationMetric(model=model, threshold=1.0),
            "Test Pass Rate": TestPassRateMetric(model=model, threshold=0.5)
        }
    
    def score_implementation(
        self,
        project_path: str,
        device_name: str
    ) -> Dict[str, float]:
        """Score a DML implementation at the given project path.
        
        Args:
            project_path: Path to the adk_openspec_project directory
            device_name: Name of the device being implemented
            
        Returns:
            Dictionary containing:
            - overall_score: Weighted average of all metrics
            - metric_scores: Individual metric scores
            - metric_reasons: Reasons for each metric score (if available)
        """
        project_path = Path(project_path)
        
        # Create a test case for evaluation
        # The actual_output will be populated from the project files
        test_case = LLMTestCase(
            input=str(project_path),
            actual_output=None,  # Will be loaded by metrics
            expected_output=str(project_path)  # Reference implementation path
        )
        
        # Evaluate each metric
        metric_scores = {}
        metric_reasons = {}
        
        for metric_name, metric in self.metrics.items():
            try:
                # Measure the metric
                metric.measure(test_case)
                metric_scores[metric_name] = metric.score
                
                # Get reason if available
                if hasattr(metric, 'reason') and metric.reason:
                    metric_reasons[metric_name] = metric.reason
                    
            except Exception as e:
                print(f"⚠️  Warning: Failed to evaluate {metric_name}: {e}")
                metric_scores[metric_name] = 0.0
                metric_reasons[metric_name] = f"Evaluation failed: {str(e)}"
        
        # Calculate weighted overall score
        overall_score = sum(
            metric_scores.get(name, 0.0) * weight
            for name, weight in self.weights.items()
        )
        
        return {
            "overall_score": overall_score,
            "metric_scores": metric_scores,
            "metric_reasons": metric_reasons,
            "weights": self.weights
        }
    
    def score_test_case(self, test_case: LLMTestCase) -> float:
        """Score a single test case (for DeepEval compatibility).
        
        Args:
            test_case: LLMTestCase containing input and expected output
            
        Returns:
            Overall weighted score (0.0 to 1.0)
        """
        # Extract project path from test case
        project_path = test_case.input
        device_name = Path(project_path).parent.name
        
        # Score the implementation
        results = self.score_implementation(project_path, device_name)
        return results["overall_score"]
    
    def get_metric_list(self) -> List:
        """Get list of metric objects for DeepEval optimizer.
        
        Returns:
            List of metric instances
        """
        return list(self.metrics.values())
    
    def get_metric_names(self) -> List[str]:
        """Get list of metric names.
        
        Returns:
            List of metric names
        """
        return list(self.metrics.keys())
    
    def __call__(self, test_case: LLMTestCase) -> float:
        """Make scorer callable for DeepEval compatibility.
        
        Args:
            test_case: LLMTestCase to evaluate
            
        Returns:
            Overall weighted score
        """
        return self.score_test_case(test_case)
