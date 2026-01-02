#!/usr/bin/env python3
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

"""Test script for ADK Answer Relevancy metric."""

from __future__ import annotations

from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

from adk_answer_relevancy import AdkAnswerRelevancyMetric


def main():
  """Test ADK Answer Relevancy metric against DeepEval's version."""
  
  # Create test case
  test_case = LLMTestCase(
    input="What's the capital of France?",
    actual_output="The capital of France is Paris, a beautiful city known for the Eiffel Tower."
  )
  
  print("Testing ADK Answer Relevancy Metric...")
  print(f"Input: {test_case.input}")
  print(f"Output: {test_case.actual_output}")
  print()
  
  # Test ADK version with iflow model (using ADK agents)
  print("=== ADK Answer Relevancy (iflow/qwen3-coder-plus) ===")
  adk_metric = AdkAnswerRelevancyMetric(
    model="iflow/qwen3-coder-plus",
    threshold=0.5
  )
  adk_score = adk_metric.measure(test_case)
  print(f"Score: {adk_score}")
  print(f"Statements: {adk_metric.statements}")
  print(f"Verdicts: {adk_metric.verdicts}")
  print(f"Reason: {adk_metric.reason}")
  print()
  
  # Test DeepEval version
  print("=== DeepEval Answer Relevancy (openai gpt-4.1) ===")
  deepeval_metric = AnswerRelevancyMetric(model="gpt-4.1", threshold=0.5)
  deepeval_score = deepeval_metric.measure(test_case)
  print(f"Score: {deepeval_score}")
  print(f"Statements: {deepeval_metric.statements}")
  print(f"Verdicts: {deepeval_metric.verdicts}")
  print(f"Reason: {deepeval_metric.reason}")
  print()
  
  # Compare
  print("=== Comparison ===")
  print(f"ADK Score: {adk_score}")
  print(f"DeepEval Score: {deepeval_score}")
  print(f"Difference: {abs(adk_score - deepeval_score)}")
  print(f"Reason: {adk_metric.reason}")
  print()
  
  # Test DeepEval version
  print("=== DeepEval Answer Relevancy (openai gpt-4.1) ===")
  deepeval_metric = AnswerRelevancyMetric(model="gpt-4.1", threshold=0.5)
  deepeval_score = deepeval_metric.measure(test_case)
  print(f"Score: {deepeval_score}")
  print(f"Statements: {deepeval_metric.statements}")
  print(f"Verdicts: {deepeval_metric.verdicts}")
  print(f"Reason: {deepeval_metric.reason}")
  print()
  
  # Compare
  print("=== Comparison ===")
  print(f"ADK Score: {adk_score}")
  print(f"DeepEval Score: {deepeval_score}")
  print(f"Difference: {abs(adk_score - deepeval_score)}")


if __name__ == "__main__":
  main()
