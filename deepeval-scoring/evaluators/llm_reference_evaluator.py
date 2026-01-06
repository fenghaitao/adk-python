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

"""LLM-powered reference evaluator using DeepEval metrics for golden reference comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import (
  GEval,
  ExactMatchMetric,
  JsonCorrectnessMetric,
  ArgumentCorrectnessMetric,
  PromptAlignmentMetric,
  HallucinationMetric,
  FaithfulnessMetric
)
from deepeval.metrics.g_eval import Rubric


class LLMReferenceEvaluator:
  """LLM-powered evaluator comparing generated code against golden reference."""
  
  def __init__(self, workdir: str, device_name: str, model: str, reference_dir: Optional[str] = None):
    self.workdir = Path(workdir)
    self.device_name = device_name
    self.model = model
    self.reference_dir = Path(reference_dir) if reference_dir else None
  
  def evaluate(self) -> Optional[Dict]:
    """Run LLM-powered reference comparison evaluation."""
    
    # Load generated and reference implementations
    generated_code = self._load_generated_code()
    reference_code = self._load_reference_code()
    
    if not generated_code:
      print("⚠️  No generated code found for evaluation")
      return None
    
    if not reference_code:
      print("⚠️  No reference implementation found for comparison")
      return None
    
    print(f"🤖 Running LLM-powered reference comparison...")
    print(f"   Generated code: {len(generated_code)} chars")
    print(f"   Reference code: {len(reference_code)} chars")
    print(f"   Using model: {self.model}")
    
    # Create test case for reference comparison
    test_case = LLMTestCase(
      input=f"Compare the generated DML implementation against the golden reference for {self.device_name} device",
      actual_output=generated_code,
      expected_output=reference_code,
      context=[
        f"Device: {self.device_name}",
        "Task: DML device implementation comparison",
        "Focus: Structural similarity, functional correctness, and code quality"
      ]
    )
    
    # Create LLM-powered metrics for reference comparison
    metrics = self._create_reference_metrics()
    
    print(f"📊 Running evaluation with {len(metrics)} LLM-powered metrics...")
    
    # Run evaluation
    results = evaluate([test_case], metrics)
    
    # Process results
    return self._process_results(results)
  
  def _create_reference_metrics(self) -> List:
    """Create LLM-powered metrics for reference comparison."""
    
    # Get model instance for metrics
    model_for_eval = self._get_model_for_eval()
    
    metrics = []
    
    # 1. Structural Equivalence using G-Eval
    metrics.append(GEval(
      name="Structural Equivalence",
      evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT, LLMTestCaseParams.CONTEXT],
      criteria="""Evaluate how well the generated DML code matches the structural organization of the reference implementation.
      Consider: register definitions, method signatures, field declarations, interface specifications, 
      overall code organization, and architectural patterns. Focus on structural similarity rather than exact syntax.""",
      rubric=[
        Rubric(score_range=(9, 10), expected_outcome="Excellent structural match with all key elements present and properly organized"),
        Rubric(score_range=(7, 8), expected_outcome="Good structural similarity with minor organizational differences"),
        Rubric(score_range=(5, 6), expected_outcome="Adequate structure covering most essential elements"),
        Rubric(score_range=(3, 4), expected_outcome="Partial structural match with notable missing elements"),
        Rubric(score_range=(0, 2), expected_outcome="Poor structural similarity with major architectural differences")
      ],
      model=model_for_eval,
      threshold=0.7
    ))
    
    # 2. Functional Correctness using G-Eval
    metrics.append(GEval(
      name="Functional Correctness",
      evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT, LLMTestCaseParams.CONTEXT],
      criteria="""Evaluate how well the generated code implements the same functionality as the reference implementation.
      Consider: register read/write behaviors, side effects, timing logic, event handling, error conditions,
      state management, and overall device behavior. Focus on functional equivalence and correctness.""",
      rubric=[
        Rubric(score_range=(9, 10), expected_outcome="Functionally equivalent with all behaviors correctly implemented"),
        Rubric(score_range=(7, 8), expected_outcome="Mostly correct functionality with minor behavioral differences"),
        Rubric(score_range=(5, 6), expected_outcome="Core functionality present but some behaviors may differ"),
        Rubric(score_range=(3, 4), expected_outcome="Partial functionality with notable behavioral gaps"),
        Rubric(score_range=(0, 2), expected_outcome="Significant functional differences or incorrect behaviors")
      ],
      model=model_for_eval,
      threshold=0.7
    ))
    
    # 3. Code Quality and Style using G-Eval
    metrics.append(GEval(
      name="Code Quality Match",
      evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT, LLMTestCaseParams.CONTEXT],
      criteria="""Evaluate how well the generated code matches the quality and style standards of the reference implementation.
      Consider: naming conventions, code organization, documentation quality, error handling patterns,
      DML best practices, and overall code craftsmanship. Compare against reference standards.""",
      rubric=[
        Rubric(score_range=(9, 10), expected_outcome="Excellent code quality matching or exceeding reference standards"),
        Rubric(score_range=(7, 8), expected_outcome="Good code quality with consistent style and practices"),
        Rubric(score_range=(5, 6), expected_outcome="Adequate code quality meeting basic standards"),
        Rubric(score_range=(3, 4), expected_outcome="Below reference quality with style or practice issues"),
        Rubric(score_range=(0, 2), expected_outcome="Poor code quality significantly below reference standards")
      ],
      model=model_for_eval,
      threshold=0.7
    ))
    
    # 4. Implementation Completeness using G-Eval
    metrics.append(GEval(
      name="Implementation Completeness",
      evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT, LLMTestCaseParams.CONTEXT],
      criteria="""Evaluate how completely the generated implementation covers all aspects present in the reference.
      Consider: all registers implemented, all required methods present, complete functionality coverage,
      proper error handling, edge case coverage, and no missing critical components.""",
      rubric=[
        Rubric(score_range=(9, 10), expected_outcome="Complete implementation covering all reference aspects"),
        Rubric(score_range=(7, 8), expected_outcome="Nearly complete with only minor omissions"),
        Rubric(score_range=(5, 6), expected_outcome="Most functionality present but some gaps exist"),
        Rubric(score_range=(3, 4), expected_outcome="Partial implementation with notable missing components"),
        Rubric(score_range=(0, 2), expected_outcome="Incomplete implementation missing major functionality")
      ],
      model=model_for_eval,
      threshold=0.7
    ))
    
    # 5. Faithfulness to Reference (using DeepEval's FaithfulnessMetric)
    metrics.append(FaithfulnessMetric(
      model=model_for_eval,
      threshold=0.7
    ))
    
    # 6. Hallucination Detection (using DeepEval's HallucinationMetric)
    metrics.append(HallucinationMetric(
      model=model_for_eval,
      threshold=0.7
    ))
    
    # 7. Argument Correctness for Method Signatures
    metrics.append(ArgumentCorrectnessMetric(
      model=model_for_eval,
      threshold=0.8
    ))
    
    return metrics
  
  def _get_model_for_eval(self):
    """Get appropriate model instance for evaluation metrics."""
    if self.model.startswith("iflow/"):
      from deepeval.models import LiteLLMModel
      import os
      
      model_name = self.model.replace("iflow/", "dashscope/")
      api_key = os.getenv("IFLOW_API_KEY")
      if not api_key:
        raise ValueError("IFLOW_API_KEY environment variable not set")
      
      return LiteLLMModel(
        model=model_name,
        api_key=api_key,
        base_url="https://apis.iflow.cn/v1/"
      )
    elif self.model.startswith("github_copilot/"):
      from deepeval.models import LiteLLMModel
      
      return LiteLLMModel(
        model=self.model,
        generation_kwargs={
          "extra_headers": {
            "Editor-Version": "vscode/1.85.0",
            "Copilot-Integration-Id": "vscode-chat"
          }
        }
      )
    else:
      return self.model
  
  def _load_generated_code(self) -> str:
    """Load the generated DML implementation."""
    dml_files = list(self.workdir.glob(f"**/{self.device_name}.dml"))
    if not dml_files:
      dml_files = list(self.workdir.glob("**/*.dml"))
    
    if not dml_files:
      return ""
    
    try:
      return dml_files[0].read_text()
    except Exception as e:
      print(f"⚠️  Error reading generated DML file: {e}")
      return ""
  
  def _load_reference_code(self) -> str:
    """Load the golden reference DML implementation."""
    if not self.reference_dir:
      # Auto-discover reference directories
      possible_ref_dirs = [
        self.workdir / "reference",
        self.workdir / "golden",
        self.workdir / "expected",
        self.workdir.parent / "reference" / self.device_name,
        self.workdir.parent / "golden" / self.device_name
      ]
      
      for ref_dir in possible_ref_dirs:
        if ref_dir.exists():
          self.reference_dir = ref_dir
          break
    
    if not self.reference_dir or not self.reference_dir.exists():
      return ""
    
    # Look for DML files in reference directory
    ref_dml_files = list(self.reference_dir.glob(f"**/{self.device_name}.dml"))
    if not ref_dml_files:
      ref_dml_files = list(self.reference_dir.glob("**/*.dml"))
    
    if not ref_dml_files:
      return ""
    
    try:
      return ref_dml_files[0].read_text()
    except Exception as e:
      print(f"⚠️  Error reading reference DML file: {e}")
      return ""
  
  def _process_results(self, results) -> Dict:
    """Process evaluation results."""
    metric_results = {}
    total_score = 0.0
    
    # Extract test_results from EvaluationResult
    test_results = results.test_results if hasattr(results, 'test_results') else results
    
    for result in test_results:
      for metric_result in result.metrics_data:
        metric_name = metric_result.name
        metric_results[metric_name] = {
          "score": metric_result.score,
          "reason": getattr(metric_result, "reason", ""),
          "success": metric_result.success,
          "threshold": getattr(metric_result, "threshold", 0.0),
          "category": "llm_reference_based"
        }
        total_score += metric_result.score
    
    overall_score = total_score / len(metric_results) if metric_results else 0.0
    
    return {
      "overall_score": overall_score,
      "metrics": metric_results,
      "evaluation_type": "llm_reference_based",
      "reference_available": True,
      "test_case_count": len(test_results)
    }