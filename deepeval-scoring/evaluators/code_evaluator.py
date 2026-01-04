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
    context = self._load_context()
    
    # Create test case
    test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      context=context
    )
    
    # Create metrics
    metrics = [
      CodeCorrectnessMetric(model=self.model, threshold=0.8),
      TestCoverageMetric(
        model=self.model,
        threshold=0.7,
        test_files=test_files
      ),
      CodeStyleMetric(model=self.model, threshold=0.9)
    ]
    
    # Run evaluation
    results = evaluate([test_case], metrics)
    
    # Process results
    return self._process_results(results)
  
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
    # Find spec.md in openspec/specs/
    spec_files = list((self.workdir / "openspec" / "specs").rglob("spec.md"))
    if spec_files:
      return spec_files[0].read_text()
    return ""
  
  def _load_context(self) -> List[str]:
    """Load additional context."""
    context = []
    
    # Load XML registers
    xml_files = list(self.workdir.glob("*.xml"))
    if xml_files:
      context.append(f"XML Registers:\n{xml_files[0].read_text()}")
    
    # Load proposal
    proposal_files = list(
      (self.workdir / "openspec" / "changes").rglob("proposal.md")
    )
    if proposal_files:
      context.append(f"Proposal:\n{proposal_files[0].read_text()}")
    
    # Load tasks
    tasks_files = list(
      (self.workdir / "openspec" / "changes").rglob("tasks.md")
    )
    if tasks_files:
      context.append(f"Tasks:\n{tasks_files[0].read_text()}")
    
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
