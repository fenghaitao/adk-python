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

"""ADK-based Answer Relevancy metric.

This module provides an ADK implementation of DeepEval's
AnswerRelevancyMetric, using ADK agents for multi-step evaluation.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel, Field


class Statements(BaseModel):
  """Schema for statement extraction."""
  
  statements: List[str] = Field(
    ...,
    description="List of statements from the actual output"
  )


class AnswerRelevancyVerdict(BaseModel):
  """Schema for relevancy verdict."""
  
  verdict: Literal["yes", "no", "idk"] = Field(
    ...,
    description="yes=relevant, no=irrelevant, idk=ambiguous"
  )
  reason: Optional[str] = Field(
    default=None,
    description="Reason for no/idk verdicts"
  )


class Verdicts(BaseModel):
  """Schema for all verdicts."""
  
  verdicts: List[AnswerRelevancyVerdict] = Field(
    ...,
    description="List of verdicts for each statement"
  )


class ReasonOutput(BaseModel):
  """Schema for final reason generation."""
  
  reason: str = Field(..., description="Explanation for the score")


class AdkAnswerRelevancyMetric(BaseMetric):
  """ADK-based Answer Relevancy metric.
  
  This metric replicates DeepEval's AnswerRelevancyMetric using
  ADK agents for each evaluation step:
  1. Extract statements from actual_output
  2. Generate verdicts for each statement
  3. Calculate score based on verdicts
  4. Generate reason for the score
  
  Example:
    ```python
    from adk_answer_relevancy import AdkAnswerRelevancyMetric
    
    metric = AdkAnswerRelevancyMetric(
      model="github_copilot/gpt-4.1",
      threshold=0.5
    )
    
    from deepeval.test_case import LLMTestCase
    test_case = LLMTestCase(
      input="What's the capital of France?",
      actual_output="Paris is the capital. The Eiffel Tower is there."
    )
    
    metric.measure(test_case)
    print(f"Score: {metric.score}, Reason: {metric.reason}")
    ```
  """

  def __init__(
    self,
    model: str = "iflow/qwen3-coder-plus",
    threshold: float = 0.5,
    include_reason: bool = True,
    async_mode: bool = True,
    strict_mode: bool = False,
    verbose_mode: bool = False,
    api_base: str = None,
    **kwargs
  ):
    """Initialize AdkAnswerRelevancyMetric.
    
    Args:
      model: Model to use for evaluation
      threshold: Score threshold for success (0-1)
      include_reason: Whether to generate reason
      async_mode: Whether to use async evaluation
      strict_mode: If True, threshold is set to 1.0
      verbose_mode: Whether to print verbose logs
      api_base: API base URL (for LiteLLM models)
      **kwargs: Additional arguments for LiteLLM
    """
    self.threshold = 1 if strict_mode else threshold
    self.model_name = model
    self.evaluation_model = model
    self.include_reason = include_reason
    self.async_mode = async_mode
    self.strict_mode = strict_mode
    self.verbose_mode = verbose_mode
    self.api_base = api_base
    self.litellm_kwargs = kwargs
    
    # Create agents for each step
    self._create_agents()

  def _create_agents(self):
    """Create ADK agents for each evaluation step."""
    # Agent 1: Extract statements from actual output
    self.statement_agent = LlmAgent(
      name="statement_extractor",
      model=self.model_name,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
      instruction="""Extract factual statements from the provided text.""",
      output_schema=Statements
    )
    
    # Agent 2: Generate verdicts for statements
    self.verdict_agent = LlmAgent(
      name="verdict_generator",
      model=self.model_name,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
      instruction="""Judge if statements are relevant to the question.""",
      output_schema=Verdicts
    )
    
    # Agent 3: Generate reason for score
    self.reason_agent = LlmAgent(
      name="reason_generator",
      model=self.model_name,
      disallow_transfer_to_parent=True,
      disallow_transfer_to_peers=True,
      instruction="""Explain the relevancy score.""",
      output_schema=ReasonOutput
    )

  def measure(
    self,
    test_case: LLMTestCase,
    _show_indicator: bool = True,
    _in_component: bool = False,
    _log_metric_to_confident: bool = True,
  ) -> float:
    """Measure the test case.
    
    Args:
      test_case: DeepEval test case to evaluate
      _show_indicator: Whether to show progress indicator
      _in_component: Whether this is a component-level evaluation
      _log_metric_to_confident: Whether to log to Confident AI
    
    Returns:
      Score from 0 to 1
    """
    input_text = test_case.input
    actual_output = test_case.actual_output
    
    # Step 1: Extract statements
    self.statements = self._generate_statements(actual_output)
    
    # Step 2: Generate verdicts
    self.verdicts = self._generate_verdicts(input_text, self.statements)
    
    # Step 3: Calculate score
    self.score = self._calculate_score()
    
    # Step 4: Generate reason
    self.reason = self._generate_reason(input_text, self.score)
    
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
    """Async measure the test case.
    
    Args:
      test_case: DeepEval test case to evaluate
      _show_indicator: Whether to show progress indicator
      _in_component: Whether this is a component-level evaluation
      _log_metric_to_confident: Whether to log to Confident AI
    
    Returns:
      Score from 0 to 1
    """
    input_text = test_case.input
    actual_output = test_case.actual_output
    
    # Step 1: Extract statements
    self.statements = await self._a_generate_statements(actual_output)
    
    # Step 2: Generate verdicts
    self.verdicts = await self._a_generate_verdicts(
      input_text, self.statements
    )
    
    # Step 3: Calculate score
    self.score = self._calculate_score()
    
    # Step 4: Generate reason
    self.reason = await self._a_generate_reason(input_text, self.score)
    
    self.success = self.score >= self.threshold
    
    if _log_metric_to_confident:
      from deepeval.metrics.api import metric_data_manager
      metric_data_manager.post_metric_if_enabled(self, test_case)
    
    return self.score

  def _generate_statements(self, actual_output: str) -> List[str]:
    """Extract statements from actual output.
    
    Args:
      actual_output: The actual output text
    
    Returns:
      List of statements
    """
    # Use LiteLLM for all models - ADK agents with output_schema
    # have issues with some models returning acknowledgment text
    return self._generate_statements_litellm(actual_output)
  
  def _generate_statements_litellm(self, actual_output: str) -> List[str]:
    """Extract statements using LiteLLM (for GitHub Copilot and OpenAI-compatible APIs)."""
    import litellm
    import json
    
    prompt = f"""Extract factual statements from the following text. Break it down into individual claims.

Text: "{actual_output}"

Return a JSON object with a "statements" array containing the extracted statements.
Example: {{"statements": ["statement 1", "statement 2"]}}"""
    
    # Convert model name for iflow
    model_name = self.model_name
    if model_name.startswith("iflow/"):
      model_name = model_name.replace("iflow/", "dashscope/")
    
    # Build completion kwargs
    completion_kwargs = {
      "model": model_name,
      "messages": [{"role": "user", "content": prompt}],
      "response_format": {"type": "json_object"}
    }
    
    # Add GitHub Copilot headers if needed
    if self.model_name.startswith("github_copilot/"):
      completion_kwargs["extra_headers"] = {
        "Editor-Version": "vscode/1.85.0",
        "Copilot-Integration-Id": "vscode-chat"
      }
    
    # Add iflow api_base if using iflow model
    if self.model_name.startswith("iflow/"):
      completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
      import os
      completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    
    # Add api_base if provided
    if self.api_base:
      completion_kwargs["api_base"] = self.api_base
    
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = litellm.completion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    return data.get("statements", [])
  
  def _generate_statements_adk(self, actual_output: str) -> List[str]:
    """Extract statements using ADK agents (for iflow and other models)."""
    import time
    prompt = f"""Extract all factual statements from this text:

"{actual_output}"

Break it into individual statements. Each statement should be a complete claim."""
    
    runner = InMemoryRunner(agent=self.statement_agent)
    user_id = "deepeval_user"
    session_id = f"stmt_{int(time.time() * 1000000)}"
    
    import asyncio
    asyncio.run(
      runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
      )
    )
    
    new_message = types.Content(parts=[types.Part(text=prompt)])
    events = list(runner.run(
      user_id=user_id,
      session_id=session_id,
      new_message=new_message
    ))
    
    output = self._extract_structured_output(
      events, self.statement_agent.name, Statements
    )
    return output.statements

  async def _a_generate_statements(
    self, actual_output: str
  ) -> List[str]:
    """Async extract statements from actual output.
    
    Args:
      actual_output: The actual output text
    
    Returns:
      List of statements
    """
    # Use LiteLLM for all models - ADK agents with output_schema
    # have issues with some models returning acknowledgment text
    return await self._a_generate_statements_litellm(actual_output)
  
  async def _a_generate_statements_litellm(
    self, actual_output: str
  ) -> List[str]:
    """Async extract statements using LiteLLM (for GitHub Copilot and OpenAI-compatible APIs)."""
    import litellm
    import json
    
    prompt = f"""Extract factual statements from the following text. Break it down into individual claims.

Text: "{actual_output}"

Return a JSON object with a "statements" array containing the extracted statements.
Example: {{"statements": ["statement 1", "statement 2"]}}"""
    
    # Convert model name for iflow
    model_name = self.model_name
    if model_name.startswith("iflow/"):
      model_name = model_name.replace("iflow/", "dashscope/")
    
    # Build completion kwargs
    completion_kwargs = {
      "model": model_name,
      "messages": [{"role": "user", "content": prompt}],
      "response_format": {"type": "json_object"}
    }
    
    # Add GitHub Copilot headers if needed
    if self.model_name.startswith("github_copilot/"):
      completion_kwargs["extra_headers"] = {
        "Editor-Version": "vscode/1.85.0",
        "Copilot-Integration-Id": "vscode-chat"
      }
    
    # Add iflow api_base if using iflow model
    if self.model_name.startswith("iflow/"):
      completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
      import os
      completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    
    # Add api_base if provided
    if self.api_base:
      completion_kwargs["api_base"] = self.api_base
    
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = await litellm.acompletion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    return data.get("statements", [])
  
  async def _a_generate_statements_adk(
    self, actual_output: str
  ) -> List[str]:
    """Async extract statements using ADK agents (for iflow and other models)."""
    import time
    prompt = f"""Extract all factual statements from this text:

"{actual_output}"

Break it into individual statements. Each statement should be a complete claim."""
    
    runner = InMemoryRunner(agent=self.statement_agent)
    user_id = "deepeval_user"
    session_id = f"stmt_{int(time.time() * 1000000)}"
    
    await runner.session_service.create_session(
      app_name=runner.app_name,
      user_id=user_id,
      session_id=session_id
    )
    
    new_message = types.Content(parts=[types.Part(text=prompt)])
    events = []
    async for event in runner.run_async(
      user_id=user_id,
      session_id=session_id,
      new_message=new_message
    ):
      events.append(event)
    
    output = self._extract_structured_output(
      events, self.statement_agent.name, Statements
    )
    return output.statements

  def _generate_verdicts(
    self, input_text: str, statements: List[str]
  ) -> List[AnswerRelevancyVerdict]:
    """Generate verdicts for statements.
    
    Args:
      input_text: The input question/prompt
      statements: List of statements to evaluate
    
    Returns:
      List of verdicts
    """
    if len(statements) == 0:
      return []
    
    import litellm
    import json
    
    statements_str = "\n".join([f"{i+1}. {s}" for i, s in enumerate(statements)])
    prompt = f"""For each statement below, determine if it's relevant to answering this question: "{input_text}"

Statements:
{statements_str}

For each statement, provide a verdict:
- "yes" if the statement directly addresses the question
- "no" if the statement is irrelevant
- "idk" if the statement is ambiguous or supporting info

Provide a "reason" field ONLY for "no" or "idk" verdicts.

Return JSON: {{"verdicts": [{{"verdict": "yes"}}, {{"verdict": "no", "reason": "explanation"}}, ...]}}
Generate ONE verdict per statement ({len(statements)} verdicts total)."""
    
    # Convert model name for iflow
    model_name = self.model_name
    if model_name.startswith("iflow/"):
      model_name = model_name.replace("iflow/", "dashscope/")
    
    # Build completion kwargs
    completion_kwargs = {
      "model": model_name,
      "messages": [{"role": "user", "content": prompt}],
      "response_format": {"type": "json_object"}
    }
    
    # Add GitHub Copilot headers if needed
    if self.model_name.startswith("github_copilot/"):
      completion_kwargs["extra_headers"] = {
        "Editor-Version": "vscode/1.85.0",
        "Copilot-Integration-Id": "vscode-chat"
      }
    
    # Add iflow api_base if using iflow model
    if self.model_name.startswith("iflow/"):
      completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
      import os
      completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    
    # Add api_base if provided
    if self.api_base:
      completion_kwargs["api_base"] = self.api_base
    
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = litellm.completion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    verdicts = []
    for v in data.get("verdicts", []):
      verdicts.append(AnswerRelevancyVerdict(**v))
    return verdicts

  async def _a_generate_verdicts(
    self, input_text: str, statements: List[str]
  ) -> List[AnswerRelevancyVerdict]:
    """Async generate verdicts for statements.
    
    Args:
      input_text: The input question/prompt
      statements: List of statements to evaluate
    
    Returns:
      List of verdicts
    """
    if len(statements) == 0:
      return []
    
    import litellm
    import json
    
    statements_str = "\n".join([f"{i+1}. {s}" for i, s in enumerate(statements)])
    prompt = f"""For each statement below, determine if it's relevant to answering this question: "{input_text}"

Statements:
{statements_str}

For each statement, provide a verdict:
- "yes" if the statement directly addresses the question
- "no" if the statement is irrelevant
- "idk" if the statement is ambiguous or supporting info

Provide a "reason" field ONLY for "no" or "idk" verdicts.

Return JSON: {{"verdicts": [{{"verdict": "yes"}}, {{"verdict": "no", "reason": "explanation"}}, ...]}}
Generate ONE verdict per statement ({len(statements)} verdicts total)."""
    
    # Convert model name for iflow
    model_name = self.model_name
    if model_name.startswith("iflow/"):
      model_name = model_name.replace("iflow/", "dashscope/")
    
    # Build completion kwargs
    completion_kwargs = {
      "model": model_name,
      "messages": [{"role": "user", "content": prompt}],
      "response_format": {"type": "json_object"}
    }
    
    # Add GitHub Copilot headers if needed
    if self.model_name.startswith("github_copilot/"):
      completion_kwargs["extra_headers"] = {
        "Editor-Version": "vscode/1.85.0",
        "Copilot-Integration-Id": "vscode-chat"
      }
    
    # Add iflow api_base if using iflow model
    if self.model_name.startswith("iflow/"):
      completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
      import os
      completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    
    # Add api_base if provided
    if self.api_base:
      completion_kwargs["api_base"] = self.api_base
    
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = await litellm.acompletion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    verdicts = []
    for v in data.get("verdicts", []):
      verdicts.append(AnswerRelevancyVerdict(**v))
    return verdicts

  def _generate_reason(self, input_text: str, score: float) -> str:
    """Generate reason for the score.
    
    Args:
      input_text: The input question/prompt
      score: The calculated score
    
    Returns:
      Reason string
    """
    if not self.include_reason:
      return None
    
    import litellm
    import json
    
    irrelevant_statements = []
    for verdict in self.verdicts:
      if verdict.verdict.strip().lower() == "no":
        irrelevant_statements.append(verdict.reason)
    
    irrelevant_str = "\n".join([f"- {s}" for s in irrelevant_statements])
    if not irrelevant_str:
      irrelevant_str = "None - all statements were relevant"
    
    prompt = f"""Explain this answer relevancy score concisely.

Score: {format(score, '.2f')}
Question: {input_text}
Irrelevant statements: {irrelevant_str}

Format: "The score is {format(score, '.2f')} because <reason>."
If nothing is irrelevant, be positive and encouraging.

Return JSON: {{"reason": "your explanation"}}"""
    
    # Convert model name for iflow
    model_name = self.model_name
    if model_name.startswith("iflow/"):
      model_name = model_name.replace("iflow/", "dashscope/")
    
    # Build completion kwargs
    completion_kwargs = {
      "model": model_name,
      "messages": [{"role": "user", "content": prompt}],
      "response_format": {"type": "json_object"}
    }
    
    # Add GitHub Copilot headers if needed
    if self.model_name.startswith("github_copilot/"):
      completion_kwargs["extra_headers"] = {
        "Editor-Version": "vscode/1.85.0",
        "Copilot-Integration-Id": "vscode-chat"
      }
    
    # Add iflow api_base if using iflow model
    if self.model_name.startswith("iflow/"):
      completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
      import os
      completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    
    # Add api_base if provided
    if self.api_base:
      completion_kwargs["api_base"] = self.api_base
    
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = litellm.completion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    return data.get("reason", "")
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = litellm.completion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    return data.get("reason", "")

  async def _a_generate_reason(
    self, input_text: str, score: float
  ) -> str:
    """Async generate reason for the score.
    
    Args:
      input_text: The input question/prompt
      score: The calculated score
    
    Returns:
      Reason string
    """
    if not self.include_reason:
      return None
    
    import litellm
    import json
    
    irrelevant_statements = []
    for verdict in self.verdicts:
      if verdict.verdict.strip().lower() == "no":
        irrelevant_statements.append(verdict.reason)
    
    irrelevant_str = "\n".join([f"- {s}" for s in irrelevant_statements])
    if not irrelevant_str:
      irrelevant_str = "None - all statements were relevant"
    
    prompt = f"""Explain this answer relevancy score concisely.

Score: {format(score, '.2f')}
Question: {input_text}
Irrelevant statements: {irrelevant_str}

Format: "The score is {format(score, '.2f')} because <reason>."
If nothing is irrelevant, be positive and encouraging.

Return JSON: {{"reason": "your explanation"}}"""
    
    # Convert model name for iflow
    model_name = self.model_name
    if model_name.startswith("iflow/"):
      model_name = model_name.replace("iflow/", "dashscope/")
    
    # Build completion kwargs
    completion_kwargs = {
      "model": model_name,
      "messages": [{"role": "user", "content": prompt}],
      "response_format": {"type": "json_object"}
    }
    
    # Add GitHub Copilot headers if needed
    if self.model_name.startswith("github_copilot/"):
      completion_kwargs["extra_headers"] = {
        "Editor-Version": "vscode/1.85.0",
        "Copilot-Integration-Id": "vscode-chat"
      }
    
    # Add iflow api_base if using iflow model
    if self.model_name.startswith("iflow/"):
      completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
      import os
      completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    
    # Add api_base if provided
    if self.api_base:
      completion_kwargs["api_base"] = self.api_base
    
    # Add any additional kwargs
    completion_kwargs.update(self.litellm_kwargs)
    
    response = await litellm.acompletion(**completion_kwargs)
    
    content = response.choices[0].message.content
    data = json.loads(content)
    return data.get("reason", "")

  def _calculate_score(self) -> float:
    """Calculate score based on verdicts.
    
    Returns:
      Score from 0 to 1
    """
    number_of_verdicts = len(self.verdicts)
    if number_of_verdicts == 0:
      return 1
    
    relevant_count = 0
    for verdict in self.verdicts:
      if verdict.verdict.strip().lower() != "no":
        relevant_count += 1
    
    score = relevant_count / number_of_verdicts
    return 0 if self.strict_mode and score < self.threshold else score

  def _extract_structured_output(self, events, agent_name, schema_cls):
    """Extract structured output from agent events.
    
    Args:
      events: List of events from agent run
      agent_name: Name of the agent
      schema_cls: Pydantic schema class to parse into
    
    Returns:
      Structured output object
    """
    # Find the final non-partial event from the agent
    final_event = None
    for event in reversed(events):
      # Check for agent name as author (not 'model')
      if event.author == agent_name and not event.partial:
        final_event = event
        break
    
    if not final_event:
      raise ValueError(f"No response from agent {agent_name}")
    
    # When using output_schema, the structured data is in structured_output
    if hasattr(final_event, 'structured_output') and final_event.structured_output:
      return final_event.structured_output
    elif final_event.content and final_event.content.parts:
      import json
      text_content = ""
      for part in final_event.content.parts:
        if hasattr(part, 'text') and part.text:
          text_content += part.text
      
      if text_content:
        try:
          output_dict = json.loads(text_content)
          return schema_cls(**output_dict)
        except json.JSONDecodeError:
          raise ValueError(f"Could not parse output: {text_content}")
      else:
        raise ValueError("No text content in response")
    else:
      raise ValueError("No structured output or content in response")

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
    return "Answer Relevancy (ADK)"
