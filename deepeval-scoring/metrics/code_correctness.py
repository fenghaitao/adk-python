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

"""Code correctness metric using DeepEval."""

from __future__ import annotations

from typing import List

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from .llm_utils import call_llm_for_evaluation


class CodeCorrectnessMetric(BaseMetric):
  """Evaluates if DML code correctly implements the specification.
  
  Checks:
  - All required registers implemented
  - Event-based timing (not cycle-accurate)
  - Lazy evaluation patterns
  - Interrupt handling
  - Reset logic
  - Session state management
  """
  
  def __init__(
      self,
      model: str = "iflow/qwen3-coder-plus",
      threshold: float = 0.8,
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
    """Evaluate code correctness.
    
    Args:
      test_case: LLMTestCase with:
        - input: Specification requirements
        - actual_output: Generated DML code
        - context: [XML registers, proposal, tasks]
    
    Returns:
      Score from 0.0 to 1.0
    """
    # Extract data
    spec_requirements = test_case.input
    dml_code = test_case.actual_output
    context = test_case.context or []
    
    # Build evaluation prompt
    prompt = self._build_prompt(spec_requirements, dml_code, context)
    
    # Call LLM for evaluation
    response = call_llm_for_evaluation(prompt, self.model)
    
    # Parse response
    self.score = response["score"]
    self.reason = response["reason"] if self.include_reason else None
    self.criteria_scores = response.get("criteria_scores", {})
    self.success = self.score >= self.threshold
    
    return self.score
  
  async def a_measure(self, test_case: LLMTestCase) -> float:
    """Async version of measure - calls synchronous version."""
    return self.measure(test_case)
  
  def _build_prompt(self, spec: str, code: str, context: List[str]) -> str:
    """Build evaluation prompt."""
    context_str = "\n\n".join([
      f"Context {i+1}:\n{c}" for i, c in enumerate(context)
    ])
    
    return f"""Evaluate the correctness of this DML implementation against the specification.

SPECIFICATION:
{spec}

ADDITIONAL CONTEXT:
{context_str}

DML CODE:
{code}

Evaluate the code on these criteria (each worth equal weight):
1. **Register Implementation**: All required registers from spec are implemented
2. **Event-Based Timing**: Uses Simics events, NOT cycle-accurate updates
3. **Lazy Evaluation**: Registers use lazy evaluation where appropriate
4. **Interrupt Handling**: Proper interrupt signal implementation
5. **Reset Logic**: Correct reset signal handling
6. **Session State**: Uses session variables for checkpointing
7. **No Anti-Patterns**: Avoids common DML anti-patterns

For each criterion, assign:
- 1.0 = Fully implemented correctly
- 0.5 = Partially implemented or minor issues
- 0.0 = Not implemented or major issues

Return JSON:
{{
  "criteria_scores": {{
    "register_implementation": <score>,
    "event_based_timing": <score>,
    "lazy_evaluation": <score>,
    "interrupt_handling": <score>,
    "reset_logic": <score>,
    "session_state": <score>,
    "no_anti_patterns": <score>
  }},
  "overall_score": <average of all criteria>,
  "reason": "<detailed explanation of the score with specific examples>"
}}"""
  
  def is_successful(self) -> bool:
    """Check if metric passed threshold."""
    return self.success
  
  @property
  def __name__(self):
    return "Code Correctness"
