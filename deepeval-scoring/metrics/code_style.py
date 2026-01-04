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

"""Code style metric using DeepEval."""

from __future__ import annotations

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from .llm_utils import call_llm_for_evaluation


class CodeStyleMetric(BaseMetric):
  """Evaluates code style and best practices.
  
  Checks:
  - DML naming conventions
  - Code organization
  - Documentation quality
  - Best practices adherence
  - Maintainability
  """
  
  def __init__(
      self,
      model: str = "iflow/qwen3-coder-plus",
      threshold: float = 0.9,
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
    """Evaluate code style.
    
    Args:
      test_case: LLMTestCase with:
        - actual_output: Generated DML code
    
    Returns:
      Score from 0.0 to 1.0
    """
    dml_code = test_case.actual_output
    
    # Build evaluation prompt
    prompt = self._build_prompt(dml_code)
    
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
  
  def _build_prompt(self, code: str) -> str:
    """Build evaluation prompt."""
    return f"""Evaluate the code style and best practices of this DML implementation.

DML CODE:
{code}

Evaluate the code on these criteria (each worth equal weight):
1. **Naming Conventions**: Follows DML naming standards (snake_case, descriptive names)
2. **Code Organization**: Logical structure, proper grouping of related code
3. **Documentation**: Clear comments, docstrings for complex logic
4. **Best Practices**: Follows DML idioms and patterns
5. **Maintainability**: Code is readable, modular, and easy to modify

For each criterion, assign:
- 1.0 = Excellent adherence to standards
- 0.5 = Some issues or inconsistencies
- 0.0 = Poor adherence or major issues

Return JSON:
{{
  "criteria_scores": {{
    "naming_conventions": <score>,
    "code_organization": <score>,
    "documentation": <score>,
    "best_practices": <score>,
    "maintainability": <score>
  }},
  "overall_score": <average of all criteria>,
  "reason": "<detailed explanation with specific examples of good and bad practices>"
}}"""
  
  
  def is_successful(self) -> bool:
    """Check if metric passed threshold."""
    return self.success
  
  @property
  def __name__(self):
    return "Code Style"
