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
from typing import Dict, List

from deepeval import evaluate
from deepeval.test_case import LLMTestCase

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
  
  def __init__(self, workdir: str, device_name: str, model: str):
    self.workdir = Path(workdir)
    self.device_name = device_name
    self.model = model
    
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
    
    # Load metric-specific contexts
    correctness_context = self._load_correctness_context()
    style_context = self._load_style_context()
    test_context = self._load_test_context()
    
    # Create test cases with metric-specific contexts
    correctness_test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      context=correctness_context
    )
    
    style_test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      context=style_context
    )
    
    test_coverage_test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      context=test_context
    )
    
    # Create metrics with specific test cases
    correctness_metric = CodeCorrectnessMetric(model=self.model, threshold=0.8)
    style_metric = CodeStyleMetric(model=self.model, threshold=0.9)
    coverage_metric = TestCoverageMetric(
      model=self.model,
      threshold=0.7,
      test_files=test_files
    )
    
    # Run evaluations separately with appropriate contexts
    correctness_results = evaluate([correctness_test_case], [correctness_metric])
    style_results = evaluate([style_test_case], [style_metric])
    coverage_results = evaluate([test_coverage_test_case], [coverage_metric])
    
    # Combine results
    combined_results = self._combine_metric_results([
      correctness_results,
      style_results,
      coverage_results
    ])
    
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
    
    # Load DML Best Practices Index (provides overview of DML patterns)
    dml_index_path = self.workdir / "openspec-memories" / "00_DML_Best_Practices_Index.md"
    if dml_index_path.exists():
      context.append(f"DML Best Practices Index:\n{dml_index_path.read_text()}")
    
    # Load DML Anti-Patterns (CRITICAL - prevents major implementation mistakes)
    anti_patterns_path = self.workdir / "openspec-memories" / "02_DML_Anti_Patterns.md"
    if anti_patterns_path.exists():
      context.append(f"DML Anti-Patterns (CRITICAL):\n{anti_patterns_path.read_text()}")
    
    return context
  
  def _load_correctness_context(self) -> List[str]:
    """Load context specific to code correctness evaluation."""
    context = []
    
    # Anti-patterns - CRITICAL for correctness
    anti_patterns_path = self.workdir / "openspec-memories" / "02_DML_Anti_Patterns.md"
    if anti_patterns_path.exists():
      context.append(f"DML Anti-Patterns (CRITICAL):\n{anti_patterns_path.read_text()}")
    
    # Modeling philosophy - core principles
    philosophy_path = self.workdir / "openspec-memories" / "01_Simics_Modeling_Philosophy.md"
    if philosophy_path.exists():
      context.append(f"Simics Modeling Philosophy:\n{philosophy_path.read_text()}")
    
    # Timer modeling - for timer/watchdog devices
    timer_path = self.workdir / "openspec-memories" / "04_DML_Timing_Timer_Modeling.md"
    if timer_path.exists():
      context.append(f"DML Timing and Timer Modeling:\n{timer_path.read_text()}")
    
    # Common patterns - correct implementation examples
    patterns_path = self.workdir / "openspec-memories" / "06_DML_Common_Patterns.md"
    if patterns_path.exists():
      context.append(f"DML Common Patterns:\n{patterns_path.read_text()}")
    
    return context
  
  def _load_style_context(self) -> List[str]:
    """Load context specific to code style evaluation."""
    context = []
    
    # Best practices index - style guidelines
    index_path = self.workdir / "openspec-memories" / "00_DML_Best_Practices_Index.md"
    if index_path.exists():
      context.append(f"DML Best Practices Index:\n{index_path.read_text()}")
    
    # Basic syntax - proper DML structure
    syntax_path = self.workdir / "openspec-memories" / "03_DML_Basic_Syntax.md"
    if syntax_path.exists():
      context.append(f"DML Basic Syntax:\n{syntax_path.read_text()}")
    
    # Register access scope - organization patterns
    scope_path = self.workdir / "openspec-memories" / "07_DML_Register_Access_Scope.md"
    if scope_path.exists():
      context.append(f"DML Register Access Scope:\n{scope_path.read_text()}")
    
    return context
  
  def _load_test_context(self) -> List[str]:
    """Load context specific to test coverage evaluation."""
    context = []
    
    # Test best practices index
    test_index_path = self.workdir / "openspec-memories" / "00_Test_Best_Practices_Index.md"
    if test_index_path.exists():
      context.append(f"Test Best Practices Index:\n{test_index_path.read_text()}")
    
    # Register access testing
    test_register_path = self.workdir / "openspec-memories" / "03_Test_Register_Access.md"
    if test_register_path.exists():
      context.append(f"Test Register Access:\n{test_register_path.read_text()}")
    
    # Test configuration setup
    test_config_path = self.workdir / "openspec-memories" / "02_Test_Configuration_Setup.md"
    if test_config_path.exists():
      context.append(f"Test Configuration Setup:\n{test_config_path.read_text()}")
    
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
