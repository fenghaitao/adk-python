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

"""Instruction following metric using DeepEval."""

from __future__ import annotations

from typing import List, Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from .llm_utils import call_llm_for_evaluation


class InstructionFollowingMetric(BaseMetric):
  """Evaluates how well an agent follows given instructions.
  
  Checks:
  - Adherence to specified workflow steps
  - Proper use of tools and commands
  - Following best practices and guidelines
  - Completing required tasks
  - Error handling and recovery
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
    """Evaluate instruction following.
    
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
    context_str = "\n\n".join([
      f"Context {i+1}:\n{c}" for i, c in enumerate(context)
    ])
    
    return f"""Evaluate how well the agent followed the given instructions based on the session log.

AGENT INSTRUCTIONS:
{instructions}

ADDITIONAL CONTEXT:
{context_str}

AGENT SESSION LOG:
{session_log}

Evaluate the agent's behavior on these criteria (each worth equal weight):
1. **Workflow Adherence**: Agent follows the specified workflow steps and procedures
2. **Tool Usage**: Proper use of recommended tools, commands, and utilities
3. **Best Practices**: Follows guidelines, conventions, and best practices mentioned in instructions
4. **Task Completion**: Successfully completes required tasks and objectives
5. **Error Handling**: Appropriately handles errors, recovers from failures, and follows error procedures

For each criterion, assign:
- 1.0 = Fully followed instructions with excellent execution
- 0.5 = Partially followed instructions or minor deviations
- 0.0 = Did not follow instructions or major deviations

Return JSON:
{{
  "criteria_scores": {{
    "workflow_adherence": <score>,
    "tool_usage": <score>,
    "best_practices": <score>,
    "task_completion": <score>,
    "error_handling": <score>
  }},
  "overall_score": <average of all criteria>,
  "reason": "<detailed explanation of how well the agent followed instructions, with specific examples from the session log>"
}}"""
  
  def is_successful(self) -> bool:
    """Check if metric passed threshold."""
    return self.success
  
  @property
  def __name__(self):
    return "Instruction Following"