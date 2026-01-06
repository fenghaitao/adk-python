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
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric

import sys
sys.path.append(str(Path(__file__).parent.parent))

from metrics.agent_behavior import AgentBehaviorMetric
from parsers.session_parser import SessionParser


class BehaviorEvaluator:
  """Evaluates agent behavior using DeepEval metrics."""
  
  def __init__(self, workdir: str, device_name: str, model: str, agent: str):
    self.workdir = Path(workdir)
    self.device_name = device_name
    self.model = model
    self.agent = agent
    
    # Validate that agent is provided
    if not self.agent:
      print("❌ Error: Agent type is required for behavior evaluation")
      print("   Use --agent parameter to specify agent type (e.g., rovodev, copilot-cli, kiro-cli, adk-python)")
      exit(1)
    
    # Initialize parsers
    self.session_parser = SessionParser()
  
  def _create_g_eval_metrics(self) -> List[GEval]:
    """Create G-Eval metrics for agent behavior evaluation."""
    
    # Handle iflow models properly for G-Eval
    model_for_g_eval = self._get_model_for_g_eval()
    
    # Standard rubric for behavioral assessment
    behavior_rubric = [
      Rubric(score_range=(9, 10), expected_outcome="Excellent performance with clear evidence of best practices"),
      Rubric(score_range=(7, 8), expected_outcome="Good performance with minor areas for improvement"),
      Rubric(score_range=(5, 6), expected_outcome="Adequate performance meeting basic requirements"),
      Rubric(score_range=(3, 4), expected_outcome="Below average performance with notable issues"),
      Rubric(score_range=(0, 2), expected_outcome="Poor performance failing to meet requirements")
    ]
    
    # Strict rubric for critical aspects (safety, compliance) - commented out for future use
    # strict_rubric = [
    #   Rubric(score_range=(8, 10), expected_outcome="Fully compliant with all requirements and best practices"),
    #   Rubric(score_range=(5, 7), expected_outcome="Mostly compliant with minor deviations"),
    #   Rubric(score_range=(0, 4), expected_outcome="Non-compliant or significant deviations from requirements")
    # ]
    
    metrics = []
    
    # Instruction Following - Core behavioral metric (mandatory)
    metrics.append(GEval(
      name="Instruction Following",
      evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
      criteria="""Evaluate how well the agent followed the given instructions and guidelines. 
      Consider: adherence to specified workflow steps, proper execution sequence, 
      completion of required tasks, and following procedural requirements.""",
      rubric=behavior_rubric,
      model=model_for_g_eval,
      threshold=0.7
    ))
    
    # Additional metrics commented out for now - can be enabled later if needed
    # 
    # # 2. Tool and Resource Usage
    # metrics.append(GEval(
    #   name="Tool Usage Effectiveness",
    #   evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    #   criteria="""Evaluate the agent's effectiveness in using available tools, commands, and resources.
    #   Consider: appropriate tool selection, correct usage patterns, efficient resource utilization,
    #   and proper integration of tool outputs into the workflow.""",
    #   rubric=behavior_rubric,
    #   model=model_for_g_eval,
    #   threshold=0.7
    # ))
    # 
    # # 3. Documentation and Knowledge Usage
    # metrics.append(GEval(
    #   name="Documentation Usage",
    #   evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT],
    #   criteria="""Evaluate how effectively the agent used available documentation and knowledge resources.
    #   Consider: proactive reading before implementation, consulting relevant sections,
    #   applying documented best practices, and efficient information gathering.""",
    #   rubric=behavior_rubric,
    #   model=model_for_g_eval,
    #   threshold=0.7
    # ))
    # 
    # # 4. Problem Solving and Error Handling
    # metrics.append(GEval(
    #   name="Problem Solving",
    #   evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    #   criteria="""Evaluate the agent's problem-solving approach and error handling capabilities.
    #   Consider: systematic debugging approach, appropriate error recovery,
    #   learning from failures, and adaptive problem-solving strategies.""",
    #   rubric=behavior_rubric,
    #   model=model_for_g_eval,
    #   threshold=0.6
    # ))
    # 
    # # 5. Process Efficiency and Quality
    # metrics.append(GEval(
    #   name="Process Efficiency",
    #   evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    #   criteria="""Evaluate the efficiency and quality of the agent's execution process.
    #   Consider: minimal unnecessary steps, logical progression, time management,
    #   and overall workflow optimization.""",
    #   rubric=behavior_rubric,
    #   model=model_for_g_eval,
    #   threshold=0.6
    # ))
    # 
    # # 6. Safety and Compliance (Strict evaluation)
    # metrics.append(GEval(
    #   name="Safety and Compliance",
    #   evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    #   criteria="""Evaluate the agent's adherence to safety protocols and compliance requirements.
    #   Consider: following security best practices, avoiding risky operations,
    #   proper validation and verification, and maintaining system integrity.""",
    #   rubric=strict_rubric,
    #   model=model_for_g_eval,
    #   threshold=0.8,
    #   strict_mode=True
    # ))
    
    return metrics
  
  def _get_model_for_g_eval(self):
    """Get appropriate model instance for G-Eval metrics.
    
    G-Eval requires a DeepEvalBaseLLM instance, so we need to convert
    iflow and GitHub Copilot model strings to proper LiteLLMModel instances.
    """
    if self.model.startswith("iflow/"):
      # Import here to avoid circular imports
      from deepeval.models import LiteLLMModel
      import os
      
      # Convert iflow model to LiteLLM format
      model_name = self.model.replace("iflow/", "dashscope/")
      
      # Check if API key is available
      api_key = os.getenv("IFLOW_API_KEY")
      if not api_key:
        raise ValueError(
          "IFLOW_API_KEY environment variable not set. "
          "Please set it with: export IFLOW_API_KEY='your-key'"
        )
      
      # Create LiteLLMModel instance for iflow
      return LiteLLMModel(
        model=model_name,
        api_key=api_key,
        base_url="https://apis.iflow.cn/v1/",
        generation_kwargs={
          "temperature": 0.0,
          # Disable problematic parameters for iFlow/Dashscope
          "logprobs": False,
          "top_logprobs": None
        }
      )
    elif self.model.startswith("github_copilot/"):
      # Import here to avoid circular imports
      from deepeval.models import LiteLLMModel
      import os
      
      # GitHub Copilot models use the model name as-is
      model_name = self.model
      
      # Create LiteLLMModel instance for GitHub Copilot (no API key required)
      return LiteLLMModel(
        model=model_name,
        generation_kwargs={
          "extra_headers": {
            "Editor-Version": "vscode/1.85.0",
            "Copilot-Integration-Id": "vscode-chat"
          }
        }
      )
    else:
      # For standard models (GPT-4, etc.), return the model string and let DeepEval handle it
      # DeepEval will check for appropriate API keys (OPENAI_API_KEY, etc.)
      return self.model
  
  def _create_test_case(self, instructions: str, session_log: str, context: Optional[List[str]] = None) -> LLMTestCase:
    """Create LLMTestCase from our agent behavior data.
    
    Mapping:
    - instructions -> INPUT (what the agent was supposed to do)
    - session_log -> ACTUAL_OUTPUT (what the agent actually did)
    - context -> CONTEXT (additional context like documentation, specs)
    """
    return LLMTestCase(
      input=instructions,
      actual_output=session_log,
      context=context or []
    )
  
  def evaluate(self) -> Optional[Dict]:
    """Run agent behavior evaluation with G-Eval metrics."""
    # Load agent instructions and session log
    instructions = self._load_agent_instructions()
    session_log = self._load_session_log()
    
    if not instructions or not session_log:
      print(f"⚠️  Skipping behavior evaluation: missing instructions or session log")
      return None
    
    # Create test case with proper mapping
    test_case = self._create_test_case(instructions, session_log)
    
    # Create metrics list
    metrics = []
    
    # Add our custom AgentBehaviorMetric (for comparison and detailed criteria)
    metrics.append(AgentBehaviorMetric(
      model=self.model,
      threshold=0.7
    ))
    
    # Add G-Eval metrics (now mandatory - only Instruction Following)
    print("🔍 Adding G-Eval Instruction Following metric...")
    g_eval_metrics = self._create_g_eval_metrics()
    metrics.extend(g_eval_metrics)
    print(f"   Added {len(g_eval_metrics)} G-Eval metric")
    
    print(f"📊 Running evaluation with {len(metrics)} metrics...")
    
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
      "kiro-cli": "powers/openspec-propose/POWER.md",
      "adk-python": "contributing/samples/openspec_integration/apply_agent_instruction.md",
      "qodercli": "powers/openspec-apply/POWER.md"
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
    
    elif self.agent == "adk-python":
      # Look for adk-python session logs in adk_openspec_apply_agent directory
      adk_apply_dir = self.workdir / "adk_openspec_apply_agent"
      if adk_apply_dir.exists():
        # Find the most recent session log matching apply_*.session.txt pattern
        session_logs = sorted(adk_apply_dir.glob("apply_*.session.txt"), reverse=True)
        if session_logs:
          return session_logs[0].read_text()
    
    elif self.agent == "qodercli":
      # Look for qodercli session logs in qodercli-apply directory
      qodercli_dir = self.workdir / "qodercli-apply"
      if qodercli_dir.exists():
        # Find the most recent session log matching qodercli-apply-session_*.txt
        session_logs = sorted(qodercli_dir.glob("qodercli-apply-session_*.txt"), reverse=True)
        if session_logs:
          return session_logs[0].read_text()
    
    # No session log found for this agent
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
