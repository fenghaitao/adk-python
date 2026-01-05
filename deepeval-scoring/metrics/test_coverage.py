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

"""Test coverage metric using DeepEval."""

from __future__ import annotations

from typing import List, Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from .llm_utils import call_llm_for_evaluation


class TestCoverageMetric(BaseMetric):
  """Evaluates test quality and coverage.
  
  Checks:
  - All registers have tests
  - Edge cases covered
  - Error conditions tested
  - Integration tests present
  - Test quality and clarity
  """
  
  def __init__(
      self,
      model: str = "iflow/qwen3-coder-plus",
      threshold: float = 0.7,
      include_reason: bool = True,
      test_files: Optional[List[str]] = None,
      async_mode: bool = False
  ):
    self.model = model
    self.threshold = threshold
    self.include_reason = include_reason
    self.test_files = test_files or []
    self.evaluation_model = model
    self.score = 0.0
    self.reason = None
    self.success = False
    self.criteria_scores = {}
    self.async_mode = async_mode
  
  def measure(self, test_case: LLMTestCase) -> float:
    """Evaluate test coverage.
    
    Args:
      test_case: LLMTestCase with:
        - input: Specification requirements
        - actual_output: Generated DML code
        - context: Test best practices and guidelines
    
    Returns:
      Score from 0.0 to 1.0
    """
    # Extract data
    spec_requirements = test_case.input
    dml_code = test_case.actual_output
    context = test_case.context or []
    test_files = self.test_files or []
    
    # Build evaluation prompt
    prompt = self._build_prompt(spec_requirements, dml_code, test_files, context)
    
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
      spec: str,
      code: str,
      test_files: List[str],
      context: List[str]
  ) -> str:
    """Build evaluation prompt."""
    tests_str = "\n\n".join([
      f"Test File {i+1}:\n{t}" for i, t in enumerate(test_files)
    ])
    
    context_str = "\n\n".join([
      f"Context {i+1}:\n{c}" for i, c in enumerate(context)
    ])
    
    return f"""Evaluate the test coverage and quality for this DML implementation.

SPECIFICATION:
{spec}

ADDITIONAL CONTEXT:
{context_str}

DML CODE:
{code}

TEST FILES:
{tests_str}

Evaluate the tests on these criteria (each worth equal weight):
1. **Register Coverage**: All registers have dedicated tests
2. **Edge Cases**: Boundary conditions and edge cases tested
3. **Error Handling**: Error conditions and invalid inputs tested
4. **Integration Tests**: Device behavior tested in realistic scenarios
5. **Test Quality**: Tests are clear, maintainable, and well-structured

For each criterion, assign:
- 1.0 = Fully covered with high-quality tests
- 0.5 = Partially covered or tests need improvement
- 0.0 = Not covered or poor quality tests

Return JSON:
{{
  "criteria_scores": {{
    "register_coverage": <score>,
    "edge_cases": <score>,
    "error_handling": <score>,
    "integration_tests": <score>,
    "test_quality": <score>
  }},
  "overall_score": <average of all criteria>,
  "reason": "<detailed explanation with specific examples of what's covered and what's missing>"
}}"""
  
  def is_successful(self) -> bool:
    """Check if metric passed threshold."""
    return self.success
  
  @property
  def __name__(self):
    return "Test Coverage"
