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

"""Example deepeval tests for LLM applications.

This module demonstrates how to write deepeval tests with multiple metrics
including AnswerRelevancyMetric, FaithfulnessMetric, and ContextualRelevancyMetric.
Uses iflow or GitHub Copilot models through LiteLLM.
"""

from __future__ import annotations

import os
import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
)
from deepeval.models import LiteLLMModel
from deepeval.test_case import LLMTestCase


# Skip all tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.getenv("IFLOW_API_KEY"),
    reason="IFLOW_API_KEY not set - set it to run these example tests"
)


# Configure model based on available API keys
def get_evaluation_model():
  """Get the appropriate LLM model for evaluation.
  
  Returns:
    LiteLLMModel configured for iflow.
  """
  return LiteLLMModel(
      model="dashscope/qwen3-coder-plus",
      api_key=os.getenv("IFLOW_API_KEY"),
      base_url="https://apis.iflow.cn/v1/"
  )


# Mock LLM application function
# Replace this with your actual LLM application
def llm_app(query: str, context: list[str] | None = None) -> str:
  """Simulates an LLM application response.
  
  Args:
    query: The user's input question.
    context: Optional retrieval context for RAG applications.
    
  Returns:
    The LLM's response.
  """
  # This is a placeholder - replace with your actual LLM call
  responses = {
      "What is DSPy?": (
          "DSPy is a framework for programming language models that provides "
          "a systematic approach to building LLM applications."
      ),
      "What does DSPy stand for?": (
          "DSPy stands for Declarative Self-improving Python, a framework "
          "designed for programming with language models."
      ),
      "How does ADK help with agent development?": (
          "ADK (Agent Development Kit) is a Python toolkit that makes agent "
          "development feel more like software development, providing tools "
          "for building, evaluating, and deploying AI agents."
      ),
  }
  return responses.get(query, "I don't have information about that.")


# Test cases for answer relevancy
answer_relevancy_test_cases = [
    LLMTestCase(
        input="What is DSPy?",
        actual_output=llm_app("What is DSPy?"),
        expected_output=(
            "DSPy is a framework for programming language models."
        ),
    ),
    LLMTestCase(
        input="What does DSPy stand for?",
        actual_output="DSPy stands for Declarative Self-improving Python.",
        expected_output=(
            "DSPy stands for Declarative Self-improving Python."
        ),
    ),
]


@pytest.mark.parametrize("test_case", answer_relevancy_test_cases)
def test_llm_app_answer_relevancy(test_case: LLMTestCase):
  """Tests that LLM responses are relevant to the input questions.
  
  Uses AnswerRelevancyMetric to evaluate how relevant the model's answer
  is to the input question.
  """
  model = get_evaluation_model()
  metric = AnswerRelevancyMetric(threshold=0.7, model=model)
  assert_test(test_case, metrics=[metric])


# Test cases for RAG applications with context
rag_test_cases = [
    LLMTestCase(
        input="How does ADK help with agent development?",
        actual_output=llm_app("How does ADK help with agent development?"),
        expected_output=(
            "ADK provides tools for building, evaluating, and deploying "
            "AI agents with a code-first approach."
        ),
        retrieval_context=[
            "ADK is a code-first Python toolkit for building AI agents.",
            "ADK makes agent development feel like software development.",
            "ADK provides tools for evaluation and deployment.",
        ],
    ),
]


@pytest.mark.parametrize("test_case", rag_test_cases)
def test_llm_app_faithfulness(test_case: LLMTestCase):
  """Tests that LLM responses are faithful to the retrieval context.
  
  Uses FaithfulnessMetric to ensure the model's answer is grounded in
  the provided context and doesn't hallucinate information.
  """
  model = get_evaluation_model()
  metric = FaithfulnessMetric(threshold=0.7, model=model)
  assert_test(test_case, metrics=[metric])


@pytest.mark.parametrize("test_case", rag_test_cases)
def test_llm_app_contextual_relevancy(test_case: LLMTestCase):
  """Tests that the retrieval context is relevant to the input.
  
  Uses ContextualRelevancyMetric to evaluate whether the retrieved
  context is actually relevant to answering the question.
  """
  model = get_evaluation_model()
  metric = ContextualRelevancyMetric(threshold=0.7, model=model)
  assert_test(test_case, metrics=[metric])


# Combined test with multiple metrics
@pytest.mark.parametrize("test_case", rag_test_cases)
def test_llm_app_combined_metrics(test_case: LLMTestCase):
  """Tests LLM responses with multiple metrics simultaneously.
  
  Evaluates answer relevancy, faithfulness, and contextual relevancy
  in a single test to ensure comprehensive quality assessment.
  """
  model = get_evaluation_model()
  metrics = [
      AnswerRelevancyMetric(threshold=0.7, model=model),
      FaithfulnessMetric(threshold=0.7, model=model),
      ContextualRelevancyMetric(threshold=0.7, model=model),
  ]
  assert_test(test_case, metrics=metrics)
