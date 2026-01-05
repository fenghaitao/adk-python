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

"""Documentation usage metric using DeepEval."""

from __future__ import annotations

from typing import Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from .llm_utils import call_llm_for_evaluation


class DocumentationUsageMetric(BaseMetric):
  """Evaluates how well the agent used documentation.
  
  Checks:
  - Documentation was read before implementation
  - Relevant sections were consulted
  - Best practices from docs were followed
  - Efficient documentation usage
  """
  
  def __init__(
      self,
      model: str = "iflow/qwen3-coder-plus",
      threshold: float = 0.8,
      include_reason: bool = True,
      session_log: Optional[str] = None,
      async_mode: bool = False
  ):
    self.model = model
    self.threshold = threshold
    self.include_reason = include_reason
    self.session_log = session_log
    self.evaluation_model = model
    self.score = 0.0
    self.reason = None
    self.success = False
    self.criteria_scores = {}
    self.async_mode = async_mode
  
  def measure(self, test_case: LLMTestCase) -> float:
    """Evaluate documentation usage.
    
    Args:
      test_case: LLMTestCase with:
        - input: Specification requirements
        - actual_output: Generated DML code
        - context: Session log showing agent actions
    
    Returns:
      Score from 0.0 to 1.0
    """
    spec_requirements = test_case.input
    dml_code = test_case.actual_output
    session_log = self.session_log or (
      test_case.context[0] if test_case.context else ""
    )
    
    # Build evaluation prompt
    prompt = self._build_prompt(spec_requirements, dml_code, session_log)
    
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
  
  def _build_prompt(self, spec: str, code: str, session_log: str) -> str:
    """Build evaluation prompt."""
    return f"""Evaluate how effectively the agent used documentation during implementation.

SPECIFICATION:
{spec}

GENERATED CODE:
{code}

SESSION LOG (showing agent actions):
{session_log}

Evaluate documentation usage on these criteria (each worth equal weight):
1. **Proactive Reading**: Agent read docs before attempting implementation
2. **Relevant Sections**: Agent consulted appropriate documentation sections
3. **Best Practices Applied**: Code reflects patterns from documentation
4. **Efficiency**: Agent didn't waste time reading irrelevant docs
5. **Problem Solving**: Agent used docs to resolve issues

For each criterion, assign:
- 1.0 = Excellent documentation usage
- 0.5 = Some documentation usage but could be better
- 0.0 = Poor or no documentation usage

Return JSON:
{{
  "criteria_scores": {{
    "proactive_reading": <score>,
    "relevant_sections": <score>,
    "best_practices_applied": <score>,
    "efficiency": <score>,
    "problem_solving": <score>
  }},
  "overall_score": <average of all criteria>,
  "reason": "<detailed explanation with specific examples from the session log>"
}}"""
  
  
  def is_successful(self) -> bool:
    """Check if metric passed threshold."""
    return self.success
  
  @property
  def __name__(self):
    return "Documentation Usage"
