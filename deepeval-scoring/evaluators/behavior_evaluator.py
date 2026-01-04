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

"""Agent behavior evaluator."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from deepeval import evaluate
from deepeval.test_case import LLMTestCase

import sys
sys.path.append(str(Path(__file__).parent.parent))

from metrics.documentation_usage import DocumentationUsageMetric
from parsers.session_parser import SessionParser


class BehaviorEvaluator:
  """Evaluates agent behavior using DeepEval metrics."""
  
  def __init__(self, workdir: str, device_name: str, model: str):
    self.workdir = Path(workdir)
    self.device_name = device_name
    self.model = model
    
    # Initialize parsers
    self.session_parser = SessionParser()
  
  def evaluate(self) -> Optional[Dict]:
    """Run agent behavior evaluation."""
    # Load session log
    session_log = self._load_session_log()
    if not session_log:
      return None
    
    # Load spec and code for context
    spec = self._load_spec()
    dml_code = self._load_dml_code()
    
    # Create test case
    test_case = LLMTestCase(
      input=spec,
      actual_output=dml_code,
      context=[session_log]
    )
    
    # Create metrics
    metrics = [
      DocumentationUsageMetric(
        model=self.model,
        threshold=0.8,
        session_log=session_log
      )
    ]
    
    # Run evaluation
    results = evaluate([test_case], metrics)
    
    # Process results
    return self._process_results(results)
  
  def _load_session_log(self) -> str:
    """Load agent session log."""
    # Look for session logs in common locations
    log_paths = [
      self.workdir / "apply.log",
      self.workdir / "session.log",
      self.workdir / "openspec" / "session.log",
    ]
    
    # Also check qodercli-apply directory for session logs
    qodercli_apply_dir = self.workdir / "qodercli-apply"
    if qodercli_apply_dir.exists():
      # Find the most recent session log
      session_logs = sorted(qodercli_apply_dir.glob("*session*.txt"), reverse=True)
      if session_logs:
        log_paths.insert(0, session_logs[0])
    
    for log_path in log_paths:
      if log_path.exists():
        return log_path.read_text()
    
    return ""
  
  def _load_spec(self) -> str:
    """Load specification."""
    spec_files = list((self.workdir / "openspec" / "specs").rglob("spec.md"))
    if spec_files:
      return spec_files[0].read_text()
    return ""
  
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
