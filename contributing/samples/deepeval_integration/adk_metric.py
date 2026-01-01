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

"""DeepEval metric powered by ADK agents.

This module provides AdkMetric, which wraps an ADK LlmAgent
to perform evaluations within DeepEval's framework.
"""

from __future__ import annotations

from typing import Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel, Field


class EvaluationScore(BaseModel):
  """Evaluation score schema for ADK agent output."""
  
  score: float = Field(
    ...,
    ge=0.0,
    le=1.0,
    description="Score from 0 to 1"
  )
  reason: str = Field(..., description="Explanation for the score")


class AdkMetric(BaseMetric):
  """DeepEval metric powered by an ADK agent.
  
  This metric wraps an ADK LlmAgent to perform evaluations,
  allowing you to use ADK's agent capabilities within
  DeepEval's evaluation framework.
  
  Example:
    ```python
    from google.adk.agents.llm_agent import LlmAgent
    from adk_metric import AdkMetric, EvaluationScore
    
    # Create ADK agent
    evaluator_agent = LlmAgent(
      name="evaluator",
      model="gemini-2.0-flash-exp",
      instruction="Evaluate if the answer is relevant to the question.",
      output_schema=EvaluationScore
    )
    
    # Wrap as DeepEval metric
    metric = AdkMetric(
      name="Answer Relevancy",
      agent=evaluator_agent,
      threshold=0.7
    )
    
    # Use in DeepEval
    from deepeval.test_case import LLMTestCase
    test_case = LLMTestCase(
      input="What's the weather?",
      actual_output="Paris is sunny at 24°C"
    )
    metric.measure(test_case)
    print(f"Score: {metric.score}, Reason: {metric.reason}")
    ```
  """

  def __init__(
    self,
    name: str,
    agent: LlmAgent,
    threshold: float = 0.5,
    async_mode: bool = True,
    strict_mode: bool = False,
    verbose_mode: bool = False,
  ):
    """Initialize AdkMetric.
    
    Args:
      name: Name of the metric
      agent: ADK LlmAgent to use for evaluation
      threshold: Score threshold for success (0-1)
      async_mode: Whether to use async evaluation
      strict_mode: If True, threshold is set to 1.0
      verbose_mode: Whether to print verbose logs
    
    Raises:
      ValueError: If agent doesn't have EvaluationScore output schema
    """
    self.name = name
    self.agent = agent
    self.threshold = 1 if strict_mode else threshold
    self.async_mode = async_mode
    self.strict_mode = strict_mode
    self.verbose_mode = verbose_mode
    self.evaluation_model = agent.model
    
    # Ensure agent has correct output schema
    if agent.output_schema != EvaluationScore:
      raise ValueError(
        f"ADK agent must have output_schema=EvaluationScore, "
        f"got {agent.output_schema}"
      )

  def measure(
    self,
    test_case: LLMTestCase,
    _show_indicator: bool = True,
    _in_component: bool = False,
    _log_metric_to_confident: bool = True,
  ) -> float:
    """Measure the test case using the ADK agent.
    
    Args:
      test_case: DeepEval test case to evaluate
      _show_indicator: Whether to show progress indicator
      _in_component: Whether this is a component-level evaluation
      _log_metric_to_confident: Whether to log to Confident AI
    
    Returns:
      Score from 0 to 1
    """
    # Build prompt from test case
    prompt = self._build_prompt(test_case)
    
    # Run ADK agent using InMemoryRunner
    runner = InMemoryRunner(agent=self.agent)
    
    # Create a session and run the agent
    user_id = "deepeval_user"
    session_id = "deepeval_session"
    
    # Create the session first
    import asyncio
    session = asyncio.run(
      runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
      )
    )
    
    # Run the agent
    new_message = types.Content(parts=[types.Part(text=prompt)])
    events = list(runner.run(
      user_id=user_id,
      session_id=session_id,
      new_message=new_message
    ))
    
    # Extract the final response
    final_event = None
    for event in reversed(events):
      if event.author == 'model' and not event.partial:
        final_event = event
        break
    
    if not final_event:
      raise ValueError("No response from ADK agent")
    
    # Parse the structured output from the event
    # When using output_schema, the structured data is in the event's content
    if hasattr(final_event, 'structured_output') and final_event.structured_output:
      output = final_event.structured_output
    elif final_event.content and final_event.content.parts:
      # Try to parse from text if structured_output not available
      import json
      text_content = ""
      for part in final_event.content.parts:
        if hasattr(part, 'text') and part.text:
          text_content += part.text
      
      if text_content:
        try:
          output_dict = json.loads(text_content)
          output = EvaluationScore(**output_dict)
        except (json.JSONDecodeError, Exception):
          raise ValueError(f"Could not parse agent output: {text_content}")
      else:
        raise ValueError("No text content in agent response")
    else:
      raise ValueError("No structured output or content in agent response")
    
    self.score = output.score
    self.reason = output.reason
    self.success = self.score >= self.threshold
    
    if _log_metric_to_confident:
      from deepeval.metrics.api import metric_data_manager
      metric_data_manager.post_metric_if_enabled(self, test_case)
    
    return self.score

  async def a_measure(
    self,
    test_case: LLMTestCase,
    _show_indicator: bool = True,
    _in_component: bool = False,
    _log_metric_to_confident: bool = True,
  ) -> float:
    """Async measure the test case using the ADK agent.
    
    Args:
      test_case: DeepEval test case to evaluate
      _show_indicator: Whether to show progress indicator
      _in_component: Whether this is a component-level evaluation
      _log_metric_to_confident: Whether to log to Confident AI
    
    Returns:
      Score from 0 to 1
    """
    prompt = self._build_prompt(test_case)
    
    runner = InMemoryRunner(agent=self.agent)
    
    user_id = "deepeval_user"
    session_id = "deepeval_session"
    
    # Create the session
    session = await runner.session_service.create_session(
      app_name=runner.app_name,
      user_id=user_id,
      session_id=session_id
    )
    
    # Run the agent async
    new_message = types.Content(parts=[types.Part(text=prompt)])
    events = []
    async for event in runner.run_async(
      user_id=user_id,
      session_id=session_id,
      new_message=new_message
    ):
      events.append(event)
    
    # Extract the final response
    final_event = None
    for event in reversed(events):
      # The author is the agent name, not 'model'
      if event.author == self.agent.name and not event.partial:
        final_event = event
        break
    
    if not final_event:
      raise ValueError("No response from ADK agent")
    
    # Parse the structured output from the event
    if hasattr(final_event, 'structured_output') and final_event.structured_output:
      output = final_event.structured_output
    elif final_event.content and final_event.content.parts:
      # Try to parse from text if structured_output not available
      import json
      text_content = ""
      for part in final_event.content.parts:
        if hasattr(part, 'text') and part.text:
          text_content += part.text
      
      if text_content:
        try:
          output_dict = json.loads(text_content)
          output = EvaluationScore(**output_dict)
        except (json.JSONDecodeError, Exception):
          raise ValueError(f"Could not parse agent output: {text_content}")
      else:
        raise ValueError("No text content in agent response")
    else:
      raise ValueError("No structured output or content in agent response")
    
    self.score = output.score
    self.reason = output.reason
    self.success = self.score >= self.threshold
    
    if _log_metric_to_confident:
      from deepeval.metrics.api import metric_data_manager
      metric_data_manager.post_metric_if_enabled(self, test_case)
    
    return self.score

  def _build_prompt(self, test_case: LLMTestCase) -> str:
    """Build evaluation prompt from test case.
    
    Args:
      test_case: DeepEval test case
    
    Returns:
      Formatted prompt string
    """
    prompt_parts = []
    
    if test_case.input:
      prompt_parts.append(f"Input: {test_case.input}")
    
    if test_case.actual_output:
      prompt_parts.append(f"Actual Output: {test_case.actual_output}")
    
    if test_case.expected_output:
      prompt_parts.append(f"Expected Output: {test_case.expected_output}")
    
    if test_case.retrieval_context:
      context_str = "\n".join(test_case.retrieval_context)
      prompt_parts.append(f"Context:\n{context_str}")
    
    if test_case.context:
      additional_context = "\n".join(test_case.context)
      prompt_parts.append(f"Additional Context:\n{additional_context}")
    
    return "\n\n".join(prompt_parts)

  def is_successful(self) -> bool:
    """Check if the metric passed the threshold.
    
    Returns:
      True if score >= threshold, False otherwise
    """
    if self.error is not None:
      self.success = False
    else:
      try:
        self.success = self.score >= self.threshold
      except TypeError:
        self.success = False
    return self.success

  @property
  def __name__(self):
    """Return the metric name."""
    return self.name
