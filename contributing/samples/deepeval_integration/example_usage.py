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

"""Example: Using ADK agents with DeepEval."""

from __future__ import annotations

from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from google.adk.agents.llm_agent import LlmAgent

from adk_metric import AdkMetric, EvaluationScore
from adk_answer_relevancy import AdkAnswerRelevancyMetric


def main():
  """Run example evaluation using ADK agent as DeepEval metric."""
  
  # Create ADK evaluator agent using GitHub Copilot's gpt-4.1
  # This uses LiteLLM with OAuth2, no GITHUB_TOKEN needed
  # Note: DeepEval will use OpenAI's gpt-4.1 for Answer Relevancy metric
  # This allows comparing gpt-4.1 (GitHub Copilot) vs gpt-4.1 (OpenAI)
  # 
  # Set disallow_transfer flags to avoid warning when using output_schema
  evaluator_agent = LlmAgent(
    name="helpfulness_evaluator",
    model="github_copilot/gpt-4.1",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    instruction="""
    Evaluate if the answer is helpful and accurate.
    
    Consider:
    - Relevance to the question
    - Accuracy of information
    - Completeness of the answer
    - Clarity of explanation
    
    Provide a score from 0 to 1:
    - 1.0: Perfect answer, highly helpful
    - 0.7-0.9: Good answer, mostly helpful
    - 0.4-0.6: Okay answer, somewhat helpful
    - 0.0-0.3: Poor answer, not helpful
    
    Explain your reasoning clearly.
    """,
    output_schema=EvaluationScore
  )
  
  # Wrap as DeepEval metric
  helpfulness_metric = AdkMetric(
    name="Helpfulness (ADK)",
    agent=evaluator_agent,
    threshold=0.7
  )
  
  # Create ADK-based Answer Relevancy metric
  adk_answer_relevancy = AdkAnswerRelevancyMetric(
    model="github_copilot/gpt-4.1",
    threshold=0.5
  )
  
  # Create test cases
  test_cases = [
    LLMTestCase(
      input="What's the capital of France?",
      actual_output="The capital of France is Paris, a beautiful city known for the Eiffel Tower."
    ),
    LLMTestCase(
      input="How do I make coffee?",
      actual_output="Boil water, add coffee grounds to a filter, pour hot water over the grounds, and let it brew for 4-5 minutes."
    ),
    LLMTestCase(
      input="What's the weather like?",
      actual_output="I don't have access to current weather data."
    )
  ]
  
  # Evaluate with three metrics:
  # 1. Helpfulness (ADK) - simple single-agent evaluation
  # 2. Answer Relevancy (ADK) - multi-step evaluation using ADK
  # 3. Answer Relevancy (DeepEval) - DeepEval's original implementation
  # All using gpt-4.1 for comparison (ADK via GitHub Copilot, DeepEval via OpenAI)
  print("Running evaluation...")
  results = evaluate(
    test_cases,
    metrics=[
      helpfulness_metric,  # ADK single-agent (github_copilot/gpt-4.1)
      adk_answer_relevancy,  # ADK multi-step (github_copilot/gpt-4.1)
      AnswerRelevancyMetric(model="gpt-4.1")  # DeepEval (openai gpt-4.1)
    ]
  )
  
  print("\nEvaluation complete!")
  print(f"Results: {results}")


if __name__ == "__main__":
  main()
