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

from __future__ import annotations

import copy
import json
from typing import AsyncGenerator
from typing import Generator
from typing import Optional
from typing import List, Dict, Any
import tiktoken

from google.genai import types
from typing_extensions import override

from ...agents.invocation_context import InvocationContext
from ...events.event import Event
from ...models.llm_request import LlmRequest
from ._base_llm_processor import BaseLlmRequestProcessor
from .functions import remove_client_function_call_id
from .functions import REQUEST_EUC_FUNCTION_CALL_NAME


# Context management configuration
_CONTEXT_MAX_TOKENS = 800000  # Maximum tokens before condensation
_CONTEXT_KEEP_SYSTEM_MESSAGES = 2  # Always preserve first N system messages
_CONTEXT_KEEP_RECENT_TURNS = 6  # Always preserve last N user-assistant pairs
_CONTEXT_SUMMARIZATION_MODEL = "gemini-2.0-flash"  # Model for summarization
_CONTEXT_ENABLE_CONDENSATION = True  # Enable/disable context condensation


def _estimate_tokens(contents: List[Any]) -> int:
  """Estimate token count for content list using tiktoken.

  Considers text, function calls, and function responses in token estimation.
  """
  try:
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    total_tokens = 0

    for content in contents:
      if hasattr(content, 'parts') and content.parts:
        for part in content.parts:
          # Count text tokens
          if hasattr(part, 'text') and part.text:
            total_tokens += len(encoding.encode(part.text))

          # Count function call tokens (name + arguments)
          if hasattr(part, 'function_call') and part.function_call:
            func_call = part.function_call
            # Function name tokens
            if hasattr(func_call, 'name') and func_call.name:
              total_tokens += len(encoding.encode(func_call.name))
            # Function arguments tokens (JSON serialized)
            if hasattr(func_call, 'args') and func_call.args:
              try:
                args_str = json.dumps(func_call.args)
                total_tokens += len(encoding.encode(args_str))
              except:
                # Fallback if args is already a string
                total_tokens += len(encoding.encode(str(func_call.args)))

          # Count function response tokens (name + response)
          if hasattr(part, 'function_response') and part.function_response:
            func_resp = part.function_response
            # Function name tokens
            if hasattr(func_resp, 'name') and func_resp.name:
              total_tokens += len(encoding.encode(func_resp.name))
            # Function response tokens (JSON serialized)
            if hasattr(func_resp, 'response') and func_resp.response:
              try:
                resp_str = json.dumps(func_resp.response)
                total_tokens += len(encoding.encode(resp_str))
              except:
                # Fallback if response is already a string
                total_tokens += len(encoding.encode(str(func_resp.response)))

      elif hasattr(content, 'text') and content.text:
        total_tokens += len(encoding.encode(content.text))

    return total_tokens

  except Exception as e:
    # Fallback: rough estimation if tiktoken fails
    total_chars = 0

    for content in contents:
      if hasattr(content, 'parts') and content.parts:
        for part in content.parts:
          # Count text characters
          if hasattr(part, 'text') and part.text:
            total_chars += len(part.text)

          # Count function call characters
          if hasattr(part, 'function_call') and part.function_call:
            func_call = part.function_call
            if hasattr(func_call, 'name') and func_call.name:
              total_chars += len(func_call.name)
            if hasattr(func_call, 'args') and func_call.args:
              total_chars += len(str(func_call.args))

          # Count function response characters
          if hasattr(part, 'function_response') and part.function_response:
            func_resp = part.function_response
            if hasattr(func_resp, 'name') and func_resp.name:
              total_chars += len(func_resp.name)
            if hasattr(func_resp, 'response') and func_resp.response:
              total_chars += len(str(func_resp.response))

      elif hasattr(content, 'text') and content.text:
        total_chars += len(content.text)

    # Rough estimate: ~4 chars per token
    return total_chars // 4


def _identify_conversation_turns(events: List[Event]) -> Dict[str, List[int]]:
  """Identify different types of messages from session events."""
  system_indices = []
  user_indices = []
  assistant_indices = []

  for i, event in enumerate(events):
    if hasattr(event, 'content') and event.content:
      role = getattr(event.content, 'role', 'unknown')
      if role == 'system':
        system_indices.append(i)
      elif role == 'user':
        user_indices.append(i)
      elif role in ['assistant', 'model']:
        assistant_indices.append(i)

  return {
      'system': system_indices,
      'user': user_indices,
      'assistant': assistant_indices
  }


def _extract_text_from_content(content: Any) -> str:
  """Extract text from content object, including function calls and responses.

  This function extracts all meaningful text content including:
  - Regular text parts
  - Function call information (name and arguments)
  - Function response information (name and results)
  """
  if hasattr(content, 'parts') and content.parts:
    texts = []
    for part in content.parts:
      # Extract regular text
      if hasattr(part, 'text') and part.text:
        texts.append(part.text)

      # Extract function call information
      if hasattr(part, 'function_call') and part.function_call:
        func_call = part.function_call
        func_name = getattr(func_call, 'name', 'unknown_function')
        func_args = getattr(func_call, 'args', {})
        try:
          args_str = json.dumps(func_args, indent=0)
          # Limit length to avoid overwhelming the summary
          if len(args_str) > 200:
            args_str = args_str[:200] + "..."
          texts.append(f"[Function Call: {func_name}({args_str})]")
        except:
          texts.append(f"[Function Call: {func_name}]")

      # Extract function response information
      if hasattr(part, 'function_response') and part.function_response:
        func_resp = part.function_response
        func_name = getattr(func_resp, 'name', 'unknown_function')
        func_result = getattr(func_resp, 'response', None)
        if func_result:
          try:
            result_str = json.dumps(func_result, indent=0)
            # Limit length to avoid overwhelming the summary
            if len(result_str) > 200:
              result_str = result_str[:200] + "..."
            texts.append(f"[Function Response: {func_name} returned {result_str}]")
          except:
            result_preview = str(func_result)[:200]
            if len(str(func_result)) > 200:
              result_preview += "..."
            texts.append(f"[Function Response: {func_name} returned {result_preview}]")
        else:
          texts.append(f"[Function Response: {func_name}]")

    return ' '.join(texts)
  elif hasattr(content, 'text') and content.text:
    return content.text
  return str(content)


def _create_fallback_summary(events: List[Event]) -> str:
  """Create a simple summary when LLM summarization is not available."""
  summary = "CONVERSATION SUMMARY:\n"
  user_messages = []
  assistant_messages = []

  for event in events:
    if hasattr(event, 'content') and event.content:
      role = getattr(event.content, 'role', 'unknown')
      text = _extract_text_from_content(event.content)

      if role == 'user':
        user_messages.append(text)
      elif role in ['assistant', 'model']:
        assistant_messages.append(text)

  summary += f"USER REQUESTS: {' | '.join(user_messages[-3:])}\n"
  summary += f"ASSISTANT ACTIONS: {' | '.join(assistant_messages[-3:]) if assistant_messages else '[No responses]'}\n"
  summary += f"TOTAL EXCHANGES: {len(user_messages)} user messages, {len(assistant_messages)} assistant responses"

  return summary


async def _condense_session_context(
    events: List[Event],
    invocation_id: str = "context_manager"
) -> List[Event]:
  """
  Condense session context by summarizing middle events and keeping recent ones.

  Args:
    events: List of session events to potentially condense
    invocation_id: ID for the condensation operation

  Returns:
    Condensed list of events with summary injected
  """
  import os
  
  # Check environment variables with fallback to global defaults
  enable_condensation = os.environ.get('CONTEXT_ENABLE_CONDENSATION', str(_CONTEXT_ENABLE_CONDENSATION)).lower() in ('true', '1', 'yes')
  max_tokens = int(os.environ.get('CONTEXT_MAX_TOKENS', _CONTEXT_MAX_TOKENS))
  keep_system_messages = int(os.environ.get('CONTEXT_KEEP_SYSTEM_MESSAGES', _CONTEXT_KEEP_SYSTEM_MESSAGES))
  keep_recent_turns = int(os.environ.get('CONTEXT_KEEP_RECENT_TURNS', _CONTEXT_KEEP_RECENT_TURNS))
  summarization_model = os.environ.get('CONTEXT_SUMMARIZATION_MODEL', _CONTEXT_SUMMARIZATION_MODEL)
  
  if not enable_condensation:
    return events

  # Estimate tokens from session events
  current_tokens = 0
  for event in events:
    if hasattr(event, 'content') and event.content:
      current_tokens += _estimate_tokens([event.content])

  # Check if condensation is needed
  print(f"🔍 Current session token count: {current_tokens}, max: {max_tokens}")
  if current_tokens <= max_tokens:
    return events

  print(f"🔄 Context condensation triggered. Current tokens: {current_tokens}, Max: {max_tokens}")

  # Identify message types
  indices = _identify_conversation_turns(events)

  # Determine what to keep
  keep_indices = set()

  # 1. Always keep system messages (first N)
  system_to_keep = indices['system'][:keep_system_messages]
  keep_indices.update(system_to_keep)

  # 2. Always keep recent conversation turns
  recent_user_msgs = indices['user'][-keep_recent_turns:]
  recent_assistant_msgs = indices['assistant'][-keep_recent_turns:]
  keep_indices.update(recent_user_msgs)
  keep_indices.update(recent_assistant_msgs)

  # 3. Identify content to summarize (everything else)
  all_indices = set(range(len(events)))
  summarize_indices = sorted(all_indices - keep_indices)
  print(f"All {len(all_indices)} events, {len(summarize_indices)} to summarize")
  print(f"System kept: {system_to_keep}, recent user: {recent_user_msgs}, recent assistant: {recent_assistant_msgs}")

  if not summarize_indices:
    return events  # Nothing to summarize

  # 4. Create summary of middle content
  events_to_summarize = [events[i] for i in summarize_indices]
  summary_text = _create_fallback_summary(events_to_summarize)

  # 5. Reconstruct the events list
  new_events = []

  # Add kept system events
  for i in sorted(system_to_keep):
    new_events.append(events[i])

  # Add summary as a system event
  summary_content = types.Content(
      role='system',
      parts=[types.Part.from_text(
          text=f"[CONTEXT SUMMARY - {len(summarize_indices)} events condensed]\n{summary_text}"
      )]
  )
  summary_event = Event(
      invocation_id=invocation_id,
      author='context_manager',
      content=summary_content,
  )
  new_events.append(summary_event)

  # Add kept recent events
  recent_indices = sorted(set(recent_user_msgs + recent_assistant_msgs))
  for i in recent_indices:
    new_events.append(events[i])

  # Log the condensation
  new_tokens = 0
  for event in new_events:
    if hasattr(event, 'content') and event.content:
      new_tokens += _estimate_tokens([event.content])

  print(f"✅ Context condensed: {current_tokens} → {new_tokens} tokens")
  print(f"📝 Summarized {len(summarize_indices)} events, kept {len(keep_indices)} events")

  return new_events


class _ContentLlmRequestProcessor(BaseLlmRequestProcessor):
  """Builds the contents for the LLM request."""

  @override
  async def run_async(
      self, invocation_context: InvocationContext, llm_request: LlmRequest
  ) -> AsyncGenerator[Event, None]:
    from ...agents.llm_agent import LlmAgent

    agent = invocation_context.agent
    if not isinstance(agent, LlmAgent):
      return

    # Condense session context if needed before building contents
    condensed_events = await _condense_session_context(
        invocation_context.session.events,
        invocation_context.invocation_id
    )

    # Temporarily update session events with condensed version
    original_events = invocation_context.session.events
    invocation_context.session.events = condensed_events

    if agent.include_contents == 'default':
      # Include full conversation history
      llm_request.contents = _get_contents(
          invocation_context.branch,
          invocation_context.session.events,
          agent.name,
      )
    else:
      # Include current turn context only (no conversation history)
      llm_request.contents = _get_current_turn_contents(
          invocation_context.branch,
          invocation_context.session.events,
          agent.name,
      )

    # # Restore original events (condensation only affects this request)
    # invocation_context.session.events = original_events

    # Maintain async generator behavior
    if False:  # Ensures it behaves as a generator
      yield  # This is a no-op but maintains generator structure


request_processor = _ContentLlmRequestProcessor()


def _rearrange_events_for_async_function_responses_in_history(
    events: list[Event],
) -> list[Event]:
  """Rearrange the async function_response events in the history."""

  function_call_id_to_response_events_index: dict[str, list[Event]] = {}
  for i, event in enumerate(events):
    function_responses = event.get_function_responses()
    if function_responses:
      for function_response in function_responses:
        function_call_id = function_response.id
        function_call_id_to_response_events_index[function_call_id] = i

  result_events: list[Event] = []
  for event in events:
    if event.get_function_responses():
      # function_response should be handled together with function_call below.
      continue
    elif event.get_function_calls():

      function_response_events_indices = set()
      for function_call in event.get_function_calls():
        function_call_id = function_call.id
        if function_call_id in function_call_id_to_response_events_index:
          function_response_events_indices.add(
              function_call_id_to_response_events_index[function_call_id]
          )
      result_events.append(event)
      if not function_response_events_indices:
        continue
      if len(function_response_events_indices) == 1:
        result_events.append(
            events[next(iter(function_response_events_indices))]
        )
      else:  # Merge all async function_response as one response event
        result_events.append(
            _merge_function_response_events(
                [events[i] for i in sorted(function_response_events_indices)]
            )
        )
      continue
    else:
      result_events.append(event)

  return result_events


def _rearrange_events_for_latest_function_response(
    events: list[Event],
) -> list[Event]:
  """Rearrange the events for the latest function_response.

  If the latest function_response is for an async function_call, all events
  between the initial function_call and the latest function_response will be
  removed.

  Args:
    events: A list of events.

  Returns:
    A list of events with the latest function_response rearranged.
  """
  if not events:
    return events

  function_responses = events[-1].get_function_responses()
  if not function_responses:
    # No need to process, since the latest event is not fuction_response.
    return events

  function_responses_ids = set()
  for function_response in function_responses:
    function_responses_ids.add(function_response.id)

  function_calls = events[-2].get_function_calls()

  if function_calls:
    for function_call in function_calls:
      # The latest function_response is already matched
      if function_call.id in function_responses_ids:
        return events

  function_call_event_idx = -1
  # look for corresponding function call event reversely
  for idx in range(len(events) - 2, -1, -1):
    event = events[idx]
    function_calls = event.get_function_calls()
    if function_calls:
      for function_call in function_calls:
        if function_call.id in function_responses_ids:
          function_call_event_idx = idx
          function_call_ids = {
              function_call.id for function_call in function_calls
          }
          # last response event should only contain the responses for the
          # function calls in the same function call event
          if not function_responses_ids.issubset(function_call_ids):
            raise ValueError(
                'Last response event should only contain the responses for the'
                ' function calls in the same function call event. Function'
                f' call ids found : {function_call_ids}, function response'
                f' ids provided: {function_responses_ids}'
            )
          # collect all function responses from the function call event to
          # the last response event
          function_responses_ids = function_call_ids
          break

  if function_call_event_idx == -1:
    raise ValueError(
        'No function call event found for function responses ids:'
        f' {function_responses_ids}'
    )

  # collect all function response between last function response event
  # and function call event

  function_response_events: list[Event] = []
  for idx in range(function_call_event_idx + 1, len(events) - 1):
    event = events[idx]
    function_responses = event.get_function_responses()
    if function_responses and any([
        function_response.id in function_responses_ids
        for function_response in function_responses
    ]):
      function_response_events.append(event)
  function_response_events.append(events[-1])

  result_events = events[: function_call_event_idx + 1]
  result_events.append(
      _merge_function_response_events(function_response_events)
  )

  return result_events


def _get_contents(
    current_branch: Optional[str], events: list[Event], agent_name: str = ''
) -> list[types.Content]:
  """Get the contents for the LLM request.

  Applies filtering, rearrangement, and content processing to events.

  Args:
    current_branch: The current branch of the agent.
    events: Events to process.
    agent_name: The name of the agent.

  Returns:
    A list of processed contents.
  """
  filtered_events = []
  # Parse the events, leaving the contents and the function calls and
  # responses from the current agent.
  for event in events:
    if (
        not event.content
        or not event.content.role
        or not event.content.parts
        or event.content.parts[0].text == ''
    ):
      # Skip events without content, or generated neither by user nor by model
      # or has empty text.
      # E.g. events purely for mutating session states.

      continue
    if not _is_event_belongs_to_branch(current_branch, event):
      # Skip events not belong to current branch.
      continue
    if _is_auth_event(event):
      # Skip auth events.
      continue
    filtered_events.append(
        _convert_foreign_event(event)
        if _is_other_agent_reply(agent_name, event)
        else event
    )

  # Rearrange events for proper function call/response pairing
  result_events = _rearrange_events_for_latest_function_response(
      filtered_events
  )
  result_events = _rearrange_events_for_async_function_responses_in_history(
      result_events
  )

  # Convert events to contents
  contents = []
  for event in result_events:
    content = copy.deepcopy(event.content)
    remove_client_function_call_id(content)
    contents.append(content)
  return contents


def _get_current_turn_contents(
    current_branch: Optional[str], events: list[Event], agent_name: str = ''
) -> list[types.Content]:
  """Get contents for the current turn only (no conversation history).

  When include_contents='none', we want to include:
  - The current user input
  - Tool calls and responses from the current turn
  But exclude conversation history from previous turns.

  In multi-agent scenarios, the "current turn" for an agent starts from an
  actual user or from another agent.

  Args:
    current_branch: The current branch of the agent.
    events: A list of all session events.
    agent_name: The name of the agent.

  Returns:
    A list of contents for the current turn only, preserving context needed
    for proper tool execution while excluding conversation history.
  """
  # Find the latest event that starts the current turn and process from there
  for i in range(len(events) - 1, -1, -1):
    event = events[i]
    if event.author == 'user' or _is_other_agent_reply(agent_name, event):
      return _get_contents(current_branch, events[i:], agent_name)

  return []


def _is_other_agent_reply(current_agent_name: str, event: Event) -> bool:
  """Whether the event is a reply from another agent."""
  return bool(
      current_agent_name
      and event.author != current_agent_name
      and event.author != 'user'
  )


def _convert_foreign_event(event: Event) -> Event:
  """Converts an event authored by another agent as a user-content event.

  This is to provide another agent's output as context to the current agent, so
  that current agent can continue to respond, such as summarizing previous
  agent's reply, etc.

  Args:
    event: The event to convert.

  Returns:
    The converted event.

  """
  if not event.content or not event.content.parts:
    return event

  content = types.Content()
  content.role = 'user'
  content.parts = [types.Part(text='For context:')]
  for part in event.content.parts:
    # Exclude thoughts from the context.
    if part.text and not part.thought:
      content.parts.append(
          types.Part(text=f'[{event.author}] said: {part.text}')
      )
    elif part.function_call:
      content.parts.append(
          types.Part(
              text=(
                  f'[{event.author}] called tool `{part.function_call.name}`'
                  f' with parameters: {part.function_call.args}'
              )
          )
      )
    elif part.function_response:
      # Otherwise, create a new text part.
      content.parts.append(
          types.Part(
              text=(
                  f'[{event.author}] `{part.function_response.name}` tool'
                  f' returned result: {part.function_response.response}'
              )
          )
      )
    # Fallback to the original part for non-text and non-functionCall parts.
    else:
      content.parts.append(part)

  return Event(
      timestamp=event.timestamp,
      author='user',
      content=content,
      branch=event.branch,
  )


def _merge_function_response_events(
    function_response_events: list[Event],
) -> Event:
  """Merges a list of function_response events into one event.

  The key goal is to ensure:
  1. function_call and function_response are always of the same number.
  2. The function_call and function_response are consecutively in the content.

  Args:
    function_response_events: A list of function_response events.
      NOTE: function_response_events must fulfill these requirements: 1. The
        list is in increasing order of timestamp; 2. the first event is the
        initial function_response event; 3. all later events should contain at
        least one function_response part that related to the function_call
        event.
      Caveat: This implementation doesn't support when a parallel function_call
        event contains async function_call of the same name.

  Returns:
    A merged event, that is
      1. All later function_response will replace function_response part in
          the initial function_response event.
      2. All non-function_response parts will be appended to the part list of
          the initial function_response event.
  """
  if not function_response_events:
    raise ValueError('At least one function_response event is required.')

  merged_event = function_response_events[0].model_copy(deep=True)
  parts_in_merged_event: list[types.Part] = merged_event.content.parts  # type: ignore

  if not parts_in_merged_event:
    raise ValueError('There should be at least one function_response part.')

  part_indices_in_merged_event: dict[str, int] = {}
  for idx, part in enumerate(parts_in_merged_event):
    if part.function_response:
      function_call_id: str = part.function_response.id  # type: ignore
      part_indices_in_merged_event[function_call_id] = idx

  for event in function_response_events[1:]:
    if not event.content.parts:
      raise ValueError('There should be at least one function_response part.')

    for part in event.content.parts:
      if part.function_response:
        function_call_id: str = part.function_response.id  # type: ignore
        if function_call_id in part_indices_in_merged_event:
          parts_in_merged_event[
              part_indices_in_merged_event[function_call_id]
          ] = part
        else:
          parts_in_merged_event.append(part)
          part_indices_in_merged_event[function_call_id] = (
              len(parts_in_merged_event) - 1
          )

      else:
        parts_in_merged_event.append(part)

  return merged_event


def _is_event_belongs_to_branch(
    invocation_branch: Optional[str], event: Event
) -> bool:
  """Event belongs to a branch, when event.branch is prefix of the invocation branch."""
  if not invocation_branch or not event.branch:
    return True
  return invocation_branch.startswith(event.branch)


def _is_auth_event(event: Event) -> bool:
  if not event.content.parts:
    return False
  for part in event.content.parts:
    if (
        part.function_call
        and part.function_call.name == REQUEST_EUC_FUNCTION_CALL_NAME
    ):
      return True
    if (
        part.function_response
        and part.function_response.name == REQUEST_EUC_FUNCTION_CALL_NAME
    ):
      return True
  return False
