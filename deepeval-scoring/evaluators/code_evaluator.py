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

"""Code quality evaluator."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, FaithfulnessMetric, HallucinationMetric, ArgumentCorrectnessMetric
from deepeval.metrics.g_eval import Rubric

import sys
sys.path.append(str(Path(__file__).parent.parent))

from metrics.code_correctness import CodeCorrectnessMetric
from metrics.test_coverage import TestCoverageMetric
from metrics.code_style import CodeStyleMetric
from parsers.dml_parser import DMLParser
from parsers.test_parser import TestParser
from parsers.spec_parser import SpecParser


class CodeEvaluator:
  """Evaluates code quality using DeepEval metrics."""
  
  def __init__(self, workdir: str, device_name: str, model: str, reference_dir: Optional[str] = None):
    self.workdir = Path(workdir)
    self.device_name = device_name
    self.model = model
    self.reference_dir = Path(reference_dir) if reference_dir else None
    
    # Initialize parsers
    self.dml_parser = DMLParser()
    self.test_parser = TestParser()
    self.spec_parser = SpecParser()
  
  def evaluate(self) -> Dict:
    """Run code quality evaluation."""
    # Load files
    dml_code = self._load_dml_code()
    test_files = self._load_test_files()
    spec = self._load_spec()
    
    # Check if reference is available
    reference_code = self._load_reference_code() if self.reference_dir else None
    
    # Load metric-specific contexts
    correctness_context = self._load_correctness_context()
    style_context = self._load_style_context()
    test_context = self._load_test_context()
    
    # Create test cases with metric-specific contexts
    correctness_test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      expected_output=reference_code,  # Include reference if available
      context=correctness_context
    )
    
    style_test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      expected_output=reference_code,  # Include reference if available
      context=style_context
    )
    
    test_coverage_test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      context=test_context
    )
    
    # Create standard metrics
    metrics_to_run = []
    test_cases_to_run = []
    
    # Standard code quality metrics
    correctness_metric = CodeCorrectnessMetric(model=self.model, threshold=0.8)
    style_metric = CodeStyleMetric(model=self.model, threshold=0.9)
    coverage_metric = TestCoverageMetric(
      model=self.model,
      threshold=0.7,
      test_files=test_files
    )
    
    metrics_to_run.extend([correctness_metric, style_metric, coverage_metric])
    test_cases_to_run.extend([correctness_test_case, style_test_case, test_coverage_test_case])
    
    # Add reference comparison metrics if reference is available
    if reference_code:
      print("   Adding LLM reference comparison metrics...")
      reference_metrics = self._create_reference_metrics(reference_code)
      
      # Load comprehensive context for reference comparison
      reference_context = self._load_reference_context()
      
      # Create reference comparison test case with rich context
      reference_test_case = LLMTestCase(
        input=f"Compare the generated DML implementation against the golden reference for {self.device_name} device",
        actual_output=dml_code,
        expected_output=reference_code,
        context=reference_context
      )
      
      # Add reference metrics and test cases
      for metric in reference_metrics:
        metrics_to_run.append(metric)
        test_cases_to_run.append(reference_test_case)
    
    # Run all evaluations
    print(f"   Running {len(metrics_to_run)} code quality metrics...")
    all_results = []
    
    for i, (test_case, metric) in enumerate(zip(test_cases_to_run, metrics_to_run)):
      result = evaluate([test_case], [metric])
      all_results.append(result)
    
    # Combine results
    combined_results = self._combine_metric_results(all_results)
    
    return self._process_results(combined_results)
  
  def _combine_metric_results(self, results_list) -> object:
    """Combine results from multiple separate metric evaluations."""
    # Create a mock results object that combines all metrics
    class CombinedResults:
      def __init__(self, results_list):
        self.test_results = []
        
        # Combine all test results from different evaluations
        for results in results_list:
          test_results = results.test_results if hasattr(results, 'test_results') else results
          if test_results:
            self.test_results.extend(test_results)
    
    return CombinedResults(results_list)
  
  def _load_dml_code(self) -> str:
    """Load DML implementation."""
    dml_path = (
      self.workdir / 
      "simics-project" / 
      "modules" / 
      self.device_name / 
      f"{self.device_name}.dml"
    )
    if not dml_path.exists():
      return ""
    return dml_path.read_text()
  
  def _load_test_files(self) -> List[str]:
    """Load test files."""
    test_dir = (
      self.workdir / 
      "simics-project" / 
      "modules" / 
      self.device_name / 
      "test"
    )
    if not test_dir.exists():
      return []
    return [
      f.read_text() 
      for f in test_dir.glob("s-*.py")
    ]
  
  def _load_spec(self) -> str:
    """Load specification."""
    # First, look for spec.md in openspec/specs/
    specs_dir = self.workdir / "openspec" / "specs"
    if specs_dir.exists():
      spec_files = list(specs_dir.rglob("spec.md"))
      if spec_files:
        if len(spec_files) == 1:
          return spec_files[0].read_text()
        else:
          # Combine multiple spec files
          combined_spec = []
          for spec_file in spec_files:
            combined_spec.append(f"# {spec_file.parent.name}")
            combined_spec.append(spec_file.read_text())
            combined_spec.append("")
          return "\n".join(combined_spec)
    
    # If not found, look in openspec/changes/
    changes_dir = self.workdir / "openspec" / "changes"
    if changes_dir.exists():
      spec_files = list(changes_dir.rglob("spec.md"))
      if spec_files:
        if len(spec_files) == 1:
          return spec_files[0].read_text()
        else:
          # Combine multiple spec files
          combined_spec = []
          for spec_file in spec_files:
            combined_spec.append(f"# {spec_file.parent.name}")
            combined_spec.append(spec_file.read_text())
            combined_spec.append("")
          return "\n".join(combined_spec)
    
    return ""
  
  def _load_context(self) -> List[str]:
    """Load additional context including DML knowledge and best practices."""
    # This method provides general context - specific metrics may need targeted context
    context = []
    
    # Get the adk-python root directory (parent of deepeval-scoring)
    adk_root = Path(__file__).parent.parent.parent
    
    # Load DML Best Practices Index (provides overview of DML patterns)
    dml_index_path = adk_root / "openspec-memories" / "00_DML_Best_Practices_Index.md"
    if dml_index_path.exists():
      print(f"   📚 Loading: {dml_index_path}")
      context.append(f"DML Best Practices Index:\n{dml_index_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {dml_index_path}")
    
    # Load DML Anti-Patterns (CRITICAL - prevents major implementation mistakes)
    anti_patterns_path = adk_root / "openspec-memories" / "02_DML_Anti_Patterns.md"
    if anti_patterns_path.exists():
      print(f"   📚 Loading: {anti_patterns_path}")
      context.append(f"DML Anti-Patterns (CRITICAL):\n{anti_patterns_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {anti_patterns_path}")
    
    return context
  
  def _load_correctness_context(self) -> List[str]:
    """Load context specific to code correctness evaluation."""
    context = []
    print("   🔍 Loading correctness context...")
    
    # Get the adk-python root directory (parent of deepeval-scoring)
    adk_root = Path(__file__).parent.parent.parent
    
    # Anti-patterns - CRITICAL for correctness
    anti_patterns_path = adk_root / "openspec-memories" / "02_DML_Anti_Patterns.md"
    if anti_patterns_path.exists():
      print(f"   📚 Loading: {anti_patterns_path}")
      context.append(f"DML Anti-Patterns (CRITICAL):\n{anti_patterns_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {anti_patterns_path}")
    
    # Modeling philosophy - core principles
    philosophy_path = adk_root / "openspec-memories" / "01_Simics_Modeling_Philosophy.md"
    if philosophy_path.exists():
      print(f"   📚 Loading: {philosophy_path}")
      context.append(f"Simics Modeling Philosophy:\n{philosophy_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {philosophy_path}")
    
    # Timer modeling - for timer/watchdog devices
    timer_path = adk_root / "openspec-memories" / "04_DML_Timing_Timer_Modeling.md"
    if timer_path.exists():
      print(f"   📚 Loading: {timer_path}")
      context.append(f"DML Timing and Timer Modeling:\n{timer_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {timer_path}")
    
    # Common patterns - correct implementation examples
    patterns_path = adk_root / "openspec-memories" / "06_DML_Common_Patterns.md"
    if patterns_path.exists():
      print(f"   📚 Loading: {patterns_path}")
      context.append(f"DML Common Patterns:\n{patterns_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {patterns_path}")
    
    return context
  
  def _load_style_context(self) -> List[str]:
    """Load context specific to code style evaluation."""
    context = []
    print("   🎨 Loading style context...")
    
    # Get the adk-python root directory (parent of deepeval-scoring)
    adk_root = Path(__file__).parent.parent.parent
    
    # Best practices index - style guidelines
    index_path = adk_root / "openspec-memories" / "00_DML_Best_Practices_Index.md"
    if index_path.exists():
      print(f"   📚 Loading: {index_path}")
      context.append(f"DML Best Practices Index:\n{index_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {index_path}")
    
    # Basic syntax - proper DML structure
    syntax_path = adk_root / "openspec-memories" / "03_DML_Basic_Syntax.md"
    if syntax_path.exists():
      print(f"   📚 Loading: {syntax_path}")
      context.append(f"DML Basic Syntax:\n{syntax_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {syntax_path}")
    
    # Register access scope - organization patterns
    scope_path = adk_root / "openspec-memories" / "07_DML_Register_Access_Scope.md"
    if scope_path.exists():
      print(f"   📚 Loading: {scope_path}")
      context.append(f"DML Register Access Scope:\n{scope_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {scope_path}")
    
    return context
  
  def _load_test_context(self) -> List[str]:
    """Load context specific to test coverage evaluation."""
    context = []
    print("   🧪 Loading test context...")
    
    # Get the adk-python root directory (parent of deepeval-scoring)
    adk_root = Path(__file__).parent.parent.parent
    
    # Test best practices index
    test_index_path = adk_root / "openspec-memories" / "00_Test_Best_Practices_Index.md"
    if test_index_path.exists():
      print(f"   📚 Loading: {test_index_path}")
      context.append(f"Test Best Practices Index:\n{test_index_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {test_index_path}")
    
    # Register access testing
    test_register_path = adk_root / "openspec-memories" / "03_Test_Register_Access.md"
    if test_register_path.exists():
      print(f"   📚 Loading: {test_register_path}")
      context.append(f"Test Register Access:\n{test_register_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {test_register_path}")
    
    # Test configuration setup
    test_config_path = adk_root / "openspec-memories" / "02_Test_Configuration_Setup.md"
    if test_config_path.exists():
      print(f"   📚 Loading: {test_config_path}")
      context.append(f"Test Configuration Setup:\n{test_config_path.read_text()}")
    else:
      print(f"   ⚠️  Missing: {test_config_path}")
    
    return context
  
  def _load_reference_context(self) -> List[str]:
    """Load context specific to reference comparison evaluation."""
    context = [
      f"Device: {self.device_name}",
      "Task: Compare the generated DML implementation against the golden reference",
      "Focus: Structural similarity, functional correctness, and implementation completeness",
      "Instructions: Analyze both implementations and identify similarities, differences, and areas where the generated code matches or deviates from the reference."
    ]
    
    return context
  
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
          "threshold": getattr(metric_result, "threshold", 0.0)
        }
        total_score += metric_result.score
    
    return {
      "overall_score": total_score / len(metric_results) if metric_results else 0.0,
      "metrics": metric_results,
      "test_case_count": len(test_results)
    }
  
  def _create_reference_metrics(self, reference_code: str) -> List:
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
      name="Functional Correctness vs Reference",
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
    
    # 3. Implementation Completeness using G-Eval
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
    
    # 4. Faithfulness to Reference (using DeepEval's FaithfulnessMetric)
    # Note: FaithfulnessMetric requires retrieval_context, so we'll skip it for now
    # and rely on the G-Eval metrics for comprehensive reference comparison
    # metrics.append(FaithfulnessMetric(
    #   model=model_for_eval,
    #   threshold=0.7
    # ))
    
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
        base_url="https://apis.iflow.cn/v1/",
        generation_kwargs={
          "temperature": 0.1,  # Slightly higher for more consistent JSON
          # Disable problematic parameters for iFlow/Dashscope
          "logprobs": False,
          "top_logprobs": None
        }
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
  
  def _load_reference_code(self) -> Optional[str]:
    """Load the golden reference DML implementation."""
        
    if not self.reference_dir or not self.reference_dir.exists():
      return None
    
    # First, try to find the reference DML file in the same project structure
    # e.g., examples/wdt_dbg152/adk_openspec_project/simics-project/modules/wdt/wdt.dml
    structured_ref_path = (
      self.reference_dir / 
      "adk_openspec_project" / 
      "simics-project" / 
      "modules" / 
      self.device_name / 
      f"{self.device_name}.dml"
    )
    
    if structured_ref_path.exists():
      try:
        return structured_ref_path.read_text()
      except Exception as e:
        print(f"⚠️  Error reading structured reference DML file: {e}")
    
    # Fallback: Look for DML files anywhere in reference directory
    ref_dml_files = list(self.reference_dir.glob(f"**/{self.device_name}.dml"))
    if not ref_dml_files:
      ref_dml_files = list(self.reference_dir.glob("**/*.dml"))
    
    if not ref_dml_files:
      print(f"⚠️  No reference DML files found in {self.reference_dir}")
      return None
    
    try:
      # Use the first matching DML file
      ref_file = ref_dml_files[0]
      print(f"📁 Using reference DML file: {ref_file}")
      return ref_file.read_text()
    except Exception as e:
      print(f"⚠️  Error reading reference DML file: {e}")
      return None
