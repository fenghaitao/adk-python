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

from metrics.agent_behavior import AgentBehaviorMetric
from parsers.session_parser import SessionParser


class BehaviorEvaluator:
  """Evaluates agent behavior using DeepEval metrics."""
  
  def __init__(self, workdir: str, device_name: str, model: str, agent: Optional[str] = None):
    self.workdir = Path(workdir)
    self.device_name = device_name
    self.model = model
    self.agent = agent
    
    # Initialize parsers
    self.session_parser = SessionParser()
  
  def evaluate(self) -> Optional[Dict]:
    """Run agent behavior evaluation."""
    # Load agent instructions and session log
    instructions = self._load_agent_instructions()
    session_log = self._load_session_log()
    
    if not instructions or not session_log:
      print(f"⚠️  Skipping behavior evaluation: missing instructions or session log")
      return None
    
    # Create test case - no additional context needed for behavior evaluation
    # We only need instructions (what agent should do) and session log (what agent did)
    test_case = LLMTestCase(
      input=instructions,
      actual_output=session_log,
      context=[]  # No additional context needed for process evaluation
    )
    
    # Create metrics
    metrics = [
      AgentBehaviorMetric(
        model=self.model,
        threshold=0.7
      )
    ]
    
    # Run evaluation
    results = evaluate([test_case], metrics)
    
    # Process results
    return self._process_results(results)
  
  def _load_agent_instructions(self) -> str:
    """Load agent-specific instructions."""
    if not self.agent:
      return ""
    
    # Get the adk-python root directory (parent of deepeval-scoring)
    adk_root = Path(__file__).parent.parent.parent
    
    # Map agent types to their instruction files (relative to adk-python root)
    instruction_files = {
      "rovodev": "powers/openspec-apply/POWER.md",
      "copilot-cli": "contributing/samples/openspec_integration/apply_agent_instruction.md",
      "kiro-cli": "powers/openspec-propose/POWER.md"
    }
    
    instruction_file = instruction_files.get(self.agent)
    if not instruction_file:
      return ""
    
    instruction_path = adk_root / instruction_file
    if instruction_path.exists():
      return instruction_path.read_text()
    
    return ""
  
  def _load_session_log(self) -> str:
    """Load agent session log."""
    if self.agent:
      # Agent-specific session log paths
      if self.agent == "rovodev":
        # Look for rovodev-apply session logs
        rovodev_dir = self.workdir / "rovodev-apply"
        if rovodev_dir.exists():
          # Find the most recent session log matching the pattern
          session_logs = sorted(rovodev_dir.glob("rovodev-apply_*.txt"), reverse=True)
          if session_logs:
            return session_logs[0].read_text()
      
      elif self.agent == "copilot-cli":
        # Look for copilot-cli session logs in log directory
        log_dir = self.workdir / "log"
        if log_dir.exists():
          # Find the most recent session log matching the pattern apply-*.txt
          session_logs = sorted(log_dir.glob("apply-*.txt"), reverse=True)
          if session_logs:
            return session_logs[0].read_text()
      
      elif self.agent == "kiro-cli":
        # Look for kiro-cli session logs in kiro-apply directory
        kiro_apply_dir = self.workdir / "kiro-apply"
        if kiro_apply_dir.exists():
          # Find the most recent session log matching the pattern kiro-apply-session_*.txt
          session_logs = sorted(kiro_apply_dir.glob("kiro-apply-session_*.txt"), reverse=True)
          if session_logs:
            return session_logs[0].read_text()
    
    # Fallback to generic loading
    return self._load_generic_session_log()
  
  def _load_generic_session_log(self) -> str:
    """Load agent session log."""
    # Look for session logs in common locations (only .txt files)
    log_paths = [
      self.workdir / "apply.txt",
      self.workdir / "session.txt",
      self.workdir / "openspec" / "session.txt",
    ]
    
    # Also check qodercli-apply directory for session logs
    qodercli_apply_dir = self.workdir / "qodercli-apply"
    if qodercli_apply_dir.exists():
      # Find the most recent session log (only .txt files)
      session_logs = sorted(qodercli_apply_dir.glob("*session*.txt"), reverse=True)
      if session_logs:
        log_paths.insert(0, session_logs[0])
    
    for log_path in log_paths:
      if log_path.exists():
        return log_path.read_text()
    
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
          "threshold": getattr(metric_result, "threshold", 0.0)
        }
        total_score += metric_result.score
    
    return {
      "overall_score": total_score / len(metric_results) if metric_results else 0.0,
      "metrics": metric_results,
      "test_case_count": len(test_results)
    }
