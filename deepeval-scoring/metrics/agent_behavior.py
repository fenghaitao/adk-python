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

"""Agent behavior metric using DeepEval."""

from __future__ import annotations

from typing import List, Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from .llm_utils import call_llm_for_evaluation


class AgentBehaviorMetric(BaseMetric):
  """Evaluates overall agent behavior including instruction following and documentation usage.
  
  Checks:
  - Adherence to specified workflow steps
  - Proper use of tools and commands
  - Following best practices and guidelines
  - Completing required tasks
  - Error handling and recovery
  - Documentation was read before implementation
  - Relevant sections were consulted
  - Best practices from docs were followed
  - Efficient documentation usage
  """
  
  def __init__(
      self,
      model: str = "iflow/qwen3-coder-plus",
      threshold: float = 0.7,
      include_reason: bool = True,
      async_mode: bool = False
  ):
    self.model = model
    self.threshold = threshold
    self.include_reason = include_reason
    self.evaluation_model = model
    self.score = 0.0
    self.reason = None
    self.success = False
    self.criteria_scores = {}
    self.async_mode = async_mode
  
  def measure(self, test_case: LLMTestCase) -> float:
    """Evaluate agent behavior.
    
    Args:
      test_case: LLMTestCase with:
        - input: Agent instructions/guidelines
        - actual_output: Agent session log
        - context: Additional context (spec, code, etc.)
    
    Returns:
      Score from 0.0 to 1.0
    """
    # Extract data
    instructions = test_case.input
    session_log = test_case.actual_output
    context = test_case.context or []
    
    # Build evaluation prompt
    prompt = self._build_prompt(instructions, session_log, context)
    
    # Call LLM for evaluation
    response = call_llm_for_evaluation(prompt, self.model)
    
    # Parse response
    self.score = response["score"]
    self.reason = response["reason"] if self.include_reason else None
    self.criteria_scores = response.get("criteria_scores", {})
    self.success = self.score >= self.threshold
    
    return self.score
  
  async def a_measure(self, test_case: LLMTestCase, _show_indicator: bool = True) -> float:
    """Async version of measure - calls synchronous version."""
    return self.measure(test_case)
  
  def _build_prompt(
      self,
      instructions: str,
      session_log: str,
      context: List[str]
  ) -> str:
    """Build evaluation prompt."""
    return f"""Evaluate the agent's behavior and process adherence based on the session log and instructions.

AGENT INSTRUCTIONS:
{instructions}

AGENT SESSION LOG:
{session_log}

Evaluate how well the agent followed the prescribed process and used available resources. Focus on PROCESS EVALUATION, not output quality.

Evaluate the agent's behavior on these criteria (each worth equal weight):

**Instruction Following (50% weight):**
1. **Workflow Adherence**: Agent follows the specified workflow steps and procedures in the correct order
2. **Tool Usage**: Proper and effective use of recommended tools, commands, and utilities
3. **Task Completion**: Successfully completes all required process steps and objectives
4. **Error Handling**: Appropriately handles errors, recovers from failures, and follows error procedures

**Documentation Usage (50% weight):**
5. **Proactive Reading**: Agent reads documentation and instructions BEFORE attempting implementation
6. **Best Practices Applied**: Agent demonstrates understanding and application of documented best practices
7. **Problem Solving**: Agent uses available documentation and resources to resolve issues and questions
8. **Efficiency**: Agent consults relevant sections systematically without wasting time on irrelevant material

For each criterion, assign:
- 1.0 = Excellent performance with clear evidence in session log
- 0.5 = Adequate performance or minor deviations from best practices
- 0.0 = Poor performance, major deviations, or failure to follow process

Return JSON:
{{
  "criteria_scores": {{
    "workflow_adherence": <score>,
    "tool_usage": <score>,
    "task_completion": <score>,
    "error_handling": <score>,
    "proactive_reading": <score>,
    "best_practices_applied": <score>,
    "problem_solving": <score>,
    "efficiency": <score>
  }},
  "overall_score": <average of all criteria>,
  "reason": "<detailed explanation focusing on PROCESS QUALITY: how well the agent followed instructions, used documentation, and executed the workflow. Provide specific examples from the session log showing good/poor process adherence.>"
}}"""
  
  def is_successful(self) -> bool:
    """Check if metric passed threshold."""
    return self.success
  
  @property
  def __name__(self):
    return "Agent Behavior"