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
import os
from typing import AsyncGenerator
from typing import Generator
from typing import Optional
from typing import List, Dict, Any
import tiktoken

from google.genai import types
from typing_extensions import override
from litellm import acompletion

from ...agents.invocation_context import InvocationContext
from ...events.event import Event
from ...models.llm_request import LlmRequest
from ._base_llm_processor import BaseLlmRequestProcessor
from .functions import remove_client_function_call_id
from .functions import REQUEST_EUC_FUNCTION_CALL_NAME


# Context management configuration
_CONTEXT_MAX_TOKENS = 128000  # Maximum tokens before condensation
_CONTEXT_KEEP_SYSTEM_MESSAGES = 2  # Always preserve first N system messages
_CONTEXT_KEEP_RECENT_TURNS = 6  # Always preserve last N user-assistant pairs
_CONTEXT_SUMMARIZATION_MODEL = "github_copilot/gpt-5-mini"  # Model for summarization
_CONTEXT_ENABLE_CONDENSATION = True  # Enable/disable context condensation
_CONTEXT_HARD_LIMIT_TOKENS = 120000  # Hard limit - must fit after condensation (leave 8K for response)
_CONTEXT_MAX_RECENT_EVENTS = 50  # Maximum number of recent events to keep after last function call
_CONTEXT_MAX_TOOL_OUTPUT_TOKENS = 2000  # Maximum tokens per tool output (truncate larger ones)
_CONTEXT_SUMMARY_PROMPT = {"simple": """You are maintaining a context-aware summary for an ongoing conversation.
Analyze the conversation history and create a comprehensive summary that preserves:

1. USER_CONTEXT: Essential user requirements, goals, and preferences
2. TASK_TRACKING: Active tasks, their IDs, status, and progress
3. COMPLETED_WORK: What has been accomplished so far
4. PENDING_TASKS: What still needs to be done
5. CURRENT_STATE: Important variables, data, configurations
6. CODE_STATE: File paths, function names, key code changes
7. DECISIONS_MADE: Important choices and their reasoning
8. ERRORS_RESOLVED: Problems encountered and solutions
9. TOOLS_USED: Tools and functions invoked and result, file operation history

Create a structured summary that captures the essential context:""",
                            "vscode": """Your task is to create a comprehensive, detailed summary of the entire conversation that captures all essential information needed to seamlessly continue the work without any loss of context. This summary will be used to compact the conversation while preserving critical technical details, decisions, and progress.<br />

	## Recent Context Analysis<br />

	Pay special attention to the most recent agent commands and tool executions that led to this summarization being triggered. Include:<br />
	- **Last Agent Commands**: What specific actions/tools were just executed<br />
	- **Tool Results**: Key outcomes from recent tool calls (truncate if very long, but preserve essential information)<br />
	- **Immediate State**: What was the system doing right before summarization<br />
	- **Triggering Context**: What caused the token budget to be exceeded<br />

	## Analysis Process<br />

	Before providing your final summary, wrap your analysis in `&lt;analysis&gt;` tags to organize your thoughts systematically:<br />

	1. **Chronological Review**: Go through the conversation chronologically, identifying key phases and transitions<br />
	2. **Intent Mapping**: Extract all explicit and implicit user requests, goals, and expectations<br />
	3. **Technical Inventory**: Catalog all technical concepts, tools, frameworks, and architectural decisions<br />
	4. **Code Archaeology**: Document all files, functions, and code patterns that were discussed or modified<br />
	5. **Progress Assessment**: Evaluate what has been completed vs. what remains pending<br />
	6. **Context Validation**: Ensure all critical information for continuation is captured<br />
	7. **Recent Commands Analysis**: Document the specific agent commands and tool results from the most recent operations<br />

	## Summary Structure<br />

	Your summary must include these sections in order, following the exact format below:<br />

	<Tag name='analysis'>
		[Chronological Review: Walk through conversation phases: initial request → exploration → implementation → debugging → current state]<br />
		[Intent Mapping: List each explicit user request with message context]<br />
		[Technical Inventory: Catalog all technologies, patterns, and decisions mentioned]<br />
		[Code Archaeology: Document every file, function, and code change discussed]<br />
		[Progress Assessment: What's done vs. pending with specific status]<br />
		[Context Validation: Verify all continuation context is captured]<br />
		[Recent Commands Analysis: Last agent commands executed, tool results (truncated if long), immediate pre-summarization state]<br />
	</Tag><br />

	<Tag name='summary'>
		1. Conversation Overview:<br />
		- Primary Objectives: [All explicit user requests and overarching goals with exact quotes]<br />
		- Session Context: [High-level narrative of conversation flow and key phases]<br />
		- User Intent Evolution: [How user's needs or direction changed throughout conversation]<br />

		2. Technical Foundation:<br />
		- [Core Technology 1]: [Version/details and purpose]<br />
		- [Framework/Library 2]: [Configuration and usage context]<br />
		- [Architectural Pattern 3]: [Implementation approach and reasoning]<br />
		- [Environment Detail 4]: [Setup specifics and constraints]<br />

		3. Codebase Status:<br />
		- [File Name 1]:<br />
		- Purpose: [Why this file is important to the project]<br />
		- Current State: [Summary of recent changes or modifications]<br />
		- Key Code Segments: [Important functions/classes with brief explanations]<br />
		- Dependencies: [How this relates to other components]<br />
		- [File Name 2]:<br />
		- Purpose: [Role in the project]<br />
		- Current State: [Modification status]<br />
		- Key Code Segments: [Critical code blocks]<br />
		- [Additional files as needed]<br />

		4. Problem Resolution:<br />
		- Issues Encountered: [Technical problems, bugs, or challenges faced]<br />
		- Solutions Implemented: [How problems were resolved and reasoning]<br />
		- Debugging Context: [Ongoing troubleshooting efforts or known issues]<br />
		- Lessons Learned: [Important insights or patterns discovered]<br />

		5. Progress Tracking:<br />
		- Completed Tasks: [What has been successfully implemented with status indicators]<br />
		- Partially Complete Work: [Tasks in progress with current completion status]<br />
		- Validated Outcomes: [Features or code confirmed working through testing]<br />

		6. Active Work State:<br />
		- Current Focus: [Precisely what was being worked on in most recent messages]<br />
		- Recent Context: [Detailed description of last few conversation exchanges]<br />
		- Working Code: [Code snippets being modified or discussed recently]<br />
		- Immediate Context: [Specific problem or feature being addressed before summary]<br />

		7. Recent Operations:<br />
		- Last Agent Commands: [Specific tools/actions executed just before summarization with exact command names]<br />
		- Tool Results Summary: [Key outcomes from recent tool executions - truncate long results but keep essential info]<br />
		- Pre-Summary State: [What the agent was actively doing when token budget was exceeded]<br />
		- Operation Context: [Why these specific commands were executed and their relationship to user goals]<br />

		8. Continuation Plan:<br />
		- [Pending Task 1]: [Details and specific next steps with verbatim quotes]<br />
		- [Pending Task 2]: [Requirements and continuation context]<br />
		- [Priority Information]: [Which tasks are most urgent or logically sequential]<br />
		- [Next Action]: [Immediate next step with direct quotes from recent messages]<br />
	</Tag><br />

	## Quality Guidelines<br />

	- **Precision**: Include exact filenames, function names, variable names, and technical terms<br />
	- **Completeness**: Capture all context needed to continue without re-reading the full conversation<br />
	- **Clarity**: Write for someone who needs to pick up exactly where the conversation left off<br />
	- **Verbatim Accuracy**: Use direct quotes for task specifications and recent work context<br />
	- **Technical Depth**: Include enough detail for complex technical decisions and code patterns<br />
	- **Logical Flow**: Present information in a way that builds understanding progressively<br />

	This summary should serve as a comprehensive handoff document that enables seamless continuation of all active work streams while preserving the full technical and contextual richness of the original conversation."""}

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


def _truncate_tool_output(text: str, max_tokens: int = _CONTEXT_MAX_TOOL_OUTPUT_TOKENS) -> str:
  """Truncate long tool outputs while preserving key information.
  
  Strategy: Keep first and last portions, insert truncation marker in middle.
  This preserves error messages (often at end) and context (at beginning).
  """
  try:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
      return text
    
    # Keep first 60% and last 40% of allowed tokens
    first_tokens = int(max_tokens * 0.6)
    last_tokens = int(max_tokens * 0.4)
    
    first_text = encoding.decode(tokens[:first_tokens])
    last_text = encoding.decode(tokens[-last_tokens:])
    
    truncated_count = len(tokens) - max_tokens
    return f"{first_text}\n\n[... {truncated_count} tokens truncated ...]\n\n{last_text}"
  except:
    # Fallback: simple character-based truncation
    if len(text) <= max_tokens * 4:  # ~4 chars per token
      return text
    
    max_chars = max_tokens * 4
    first_chars = int(max_chars * 0.6)
    last_chars = int(max_chars * 0.4)
    
    return f"{text[:first_chars]}\n\n[... content truncated ...]\n\n{text[-last_chars:]}"


def _extract_text_from_content(content: Any, truncate_tools: bool = False) -> str:
  """Extract text from content object, including function calls and responses.

  This function extracts all meaningful text content including:
  - Regular text parts
  - Function call information (name and arguments)
  - Function response information (name and results)
  
  Args:
    content: Content object to extract text from
    truncate_tools: If True, truncate large tool outputs to avoid context overflow
  """
  if hasattr(content, 'parts') and content.parts:
    texts = []
    for part in content.parts:
      # Extract regular text
      if hasattr(part, 'text') and part.text:
        text = part.text
        if truncate_tools:
          text = _truncate_tool_output(text)
        texts.append(text)

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
            if truncate_tools:
              result_str = _truncate_tool_output(result_str)
            elif len(result_str) > 200:
              result_str = result_str[:200] + "..."
            texts.append(f"[Function Response: {func_name} returned {result_str}]")
          except:
            result_preview = str(func_result)
            if truncate_tools:
              result_preview = _truncate_tool_output(result_preview)
            else:
              result_preview = result_preview[:200]
              if len(str(func_result)) > 200:
                result_preview += "..."
            texts.append(f"[Function Response: {func_name} returned {result_preview}]")
        else:
          texts.append(f"[Function Response: {func_name}]")

    return ' '.join(texts)
  elif hasattr(content, 'text') and content.text:
    text = content.text
    if truncate_tools:
      text = _truncate_tool_output(text)
    return text
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


async def _summarize_events_with_llm(events: List[Event], summarization_model: str) -> str:
  """Summarize events using an LLM via LiteLLM.

  Args:
    events: List of events to summarize
    summarization_model: Model to use for summarization (default: "github_copilot/gpt-5-mini")

  Returns:
    Summary text generated by the LLM, or fallback summary if LLM fails
  """
  print(f"Summarize conversation history using LLM {summarization_model}...")
  try:
    # Extract conversation content from events
    conversation_text = []
    for event in events:
      if hasattr(event, 'content') and event.content:
        role = getattr(event.content, 'role', 'user')
        text = _extract_text_from_content(event.content)
        if text:
          conversation_text.append(f"[{role.upper()}]: {text}")

    # Prepare summarization prompt
    conversation_str = "\n\n".join(conversation_text)
    prompt_type = os.environ.get('CONTEXT_SUMMARY_PROMPT_TYPE', 'simple')
    system_prompt = _CONTEXT_SUMMARY_PROMPT[prompt_type]

    # Use LiteLLM to generate summary
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"CONVERSATION HISTORY:\n{conversation_str}"}
    ]

    if summarization_model.startswith("github_copilot/"):
        response = await acompletion(
            model=summarization_model,
            messages=messages,
            extra_headers={
                "editor-version": "vscode/1.85.1",
                "Copilot-Integration-Id": "vscode-chat"
            }
          )
    elif summarization_model.startswith("iflow/"):
        summarization_model = summarization_model.replace("iflow/", "dashscope/")
        response = await acompletion(
            model=summarization_model,
            messages=messages,
            api_base="https://apis.iflow.cn/v1/",
            api_key=os.getenv("IFLOW_API_KEY")
          )
    else:
        response = await acompletion(
            model=summarization_model,
            messages=messages
          )

    if response and response.choices and response.choices[0].message.content:
      summary = response.choices[0].message.content.strip()

      # Append summary and conversation to file for debugging/logging
      dbg_summary = os.environ.get('CONTEXT_DEBUG_SUMMARY', 'false').lower() in ('true', '1', 'yes')
      if dbg_summary:
        try:
          with open('context_condensation_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"TIMESTAMP: {__import__('datetime').datetime.now().isoformat()}\n")
            f.write(f"{'='*80}\n\n")
            f.write("CONVERSATION HISTORY:\n")
            f.write(f"{conversation_str}\n\n")
            f.write(f"{'='*80}\n")
            f.write("GENERATED SUMMARY:\n")
            f.write(f"{summary}\n\n")
        except Exception as log_error:
          print(f"⚠️  Failed to write condensation log: {log_error}")

      #print(f"✅ LLM summarization completed: {len(summary)} characters")
      #print(f"Summary Preview:\n{summary[:500]}{'...' if len(summary) > 500 else ''}")
      return summary
    else:
      print(f"⚠️  LLM summarization returned empty response, using fallback")
      return _create_fallback_summary(events)

  except Exception as e:
    print(f"⚠️  LLM summarization failed: {e}, using fallback")
    return _create_fallback_summary(events)


def _find_last_function_call_index(events: List[Event]) -> int:
  """Find the index of the last event that contains a function call.

  Args:
    events: List of events to search

  Returns:
    Index of the last function call event, or -1 if no function calls found
  """
  for i in range(len(events) - 1, -1, -1):
    event = events[i]
    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
      for part in event.content.parts:
        if hasattr(part, 'function_call') and part.function_call:
          return i
  return -1


async def _condense_session_context(
    events: List[Event],
    invocation_id: str = "context_manager"
) -> List[Event]:
  """
  Condense session context with guaranteed token limit enforcement.

  Multi-pass strategy:
  1. Truncate large tool outputs in recent events
  2. Summarize old events before last function call
  3. Keep limited recent events with truncated outputs
  4. If still over limit, recursively condense more aggressively

  Args:
    events: List of session events to potentially condense
    invocation_id: ID for the condensation operation

  Returns:
    Condensed list of events guaranteed to be under hard limit
  """
  # Check environment variables with fallback to global defaults
  enable_condensation = os.environ.get('CONTEXT_ENABLE_CONDENSATION', str(_CONTEXT_ENABLE_CONDENSATION)).lower() in ('true', '1', 'yes')
  max_tokens = int(os.environ.get('CONTEXT_MAX_TOKENS', _CONTEXT_MAX_TOKENS))
  hard_limit = int(os.environ.get('CONTEXT_HARD_LIMIT_TOKENS', _CONTEXT_HARD_LIMIT_TOKENS))
  keep_system_messages = int(os.environ.get('CONTEXT_KEEP_SYSTEM_MESSAGES', _CONTEXT_KEEP_SYSTEM_MESSAGES))
  keep_recent_turns = int(os.environ.get('CONTEXT_KEEP_RECENT_TURNS', _CONTEXT_KEEP_RECENT_TURNS))
  max_recent_events = int(os.environ.get('CONTEXT_MAX_RECENT_EVENTS', _CONTEXT_MAX_RECENT_EVENTS))
  summarization_model = os.environ.get('CONTEXT_SUMMARIZATION_MODEL', _CONTEXT_SUMMARIZATION_MODEL)

  if not enable_condensation:
    return events

  # Estimate tokens from session events
  current_tokens = 0
  for event in events:
    if hasattr(event, 'content') and event.content:
      current_tokens += _estimate_tokens([event.content])

  # Check if condensation is needed
  if current_tokens <= max_tokens:
    return events

  print(f"🔄 Context condensation triggered. Current tokens: {current_tokens}, Max: {max_tokens}, Hard limit: {hard_limit}")

  # STEP 1: Truncate large tool outputs in recent events to reduce immediate bloat
  # This is critical for autonomous agents with massive test logs
  truncated_events = []
  for event in events:
    if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
      # Create new truncated parts
      new_parts = []
      for part in event.content.parts:
        if hasattr(part, 'function_response') and part.function_response:
          # Truncate function response content
          func_resp = part.function_response
          if hasattr(func_resp, 'response') and func_resp.response:
            try:
              result_str = json.dumps(func_resp.response, indent=0)
              if len(result_str) > _CONTEXT_MAX_TOOL_OUTPUT_TOKENS * 4:  # ~4 chars per token
                # Truncate the response
                truncated_result = _truncate_tool_output(result_str, _CONTEXT_MAX_TOOL_OUTPUT_TOKENS)
                # Create new part with truncated response
                new_response = {"output": truncated_result}
                new_part = types.Part.from_function_response(
                    name=func_resp.name,
                    response=new_response
                )
                new_parts.append(new_part)
                continue
            except:
              pass
        new_parts.append(part)
      
      # Create new content with truncated parts if changes were made
      if len(new_parts) != len(event.content.parts) or any(
          new_parts[i] != event.content.parts[i] for i in range(len(new_parts))):
        new_content = types.Content(
            role=event.content.role,
            parts=new_parts
        )
        truncated_events.append(Event(
            invocation_id=event.invocation_id,
            author=event.author,
            content=new_content
        ))
      else:
        truncated_events.append(event)
    else:
      truncated_events.append(event)
  
  # Work with truncated events from now on
  events = truncated_events
  
  # STEP 2: Find the last function call index
  last_func_call_idx = _find_last_function_call_index(events)
  
  # STEP 3: Determine what to keep and what to summarize
  indices = _identify_conversation_turns(events)
  system_to_keep = indices['system'][:keep_system_messages]
  
  if last_func_call_idx <= 0:
    # No function calls - use turn-based strategy
    recent_user_msgs = indices['user'][-keep_recent_turns:]
    recent_assistant_msgs = indices['assistant'][-keep_recent_turns:]
    keep_indices = set(system_to_keep) | set(recent_user_msgs) | set(recent_assistant_msgs)
  else:
    # Have function calls - keep from last function call but limit total to max_recent_events
    # Use min() to start from whichever comes first: the function call or the recent window
    recent_start_idx = min(last_func_call_idx, len(events) - max_recent_events)
    recent_event_indices = list(range(recent_start_idx, len(events)))
    keep_indices = set(system_to_keep) | set(recent_event_indices)
  
  # STEP 3.5: Ensure function call/response pairs are kept together
  # If we keep a function response, we must keep its corresponding function call
  function_call_map = {}  # Maps function response ID to function call event index
  for i, event in enumerate(events):
    if event.get_function_calls():
      for func_call in event.get_function_calls():
        if func_call.id:
          function_call_map[func_call.id] = i
  
  # Check kept events for function responses and ensure their calls are kept
  for i in list(keep_indices):
    if i < len(events) and events[i].get_function_responses():
      for func_response in events[i].get_function_responses():
        if func_response.id and func_response.id in function_call_map:
          call_idx = function_call_map[func_response.id]
          if call_idx not in keep_indices:
            keep_indices.add(call_idx)
            print(f"🔗 Keeping function call event {call_idx} for response in event {i}")
  
  # STEP 3.6: Remove orphaned function calls (calls without responses)
  # If we keep a function call but its response is being summarized, remove the call too
  response_map = {}  # Maps function call ID to response event index
  for i, event in enumerate(events):
    if event.get_function_responses():
      for func_response in event.get_function_responses():
        if func_response.id:
          response_map[func_response.id] = i
  
  # Check kept events for function calls and ensure their responses are also kept
  calls_to_remove = set()
  for i in list(keep_indices):
    if i < len(events) and events[i].get_function_calls():
      for func_call in events[i].get_function_calls():
        if func_call.id:
          # Check if this call's response is in the kept set
          if func_call.id in response_map:
            response_idx = response_map[func_call.id]
            if response_idx not in keep_indices:
              # Response is being summarized, so remove this orphaned call
              calls_to_remove.add(i)
              print(f"🗑️  Removing orphaned function call event {i} (response {response_idx} being summarized)")
              break  # No need to check other calls in this event
  
  # Remove the orphaned calls from keep_indices
  keep_indices -= calls_to_remove
  
  # STEP 4: Summarize events not being kept
  all_indices = set(range(len(events)))
  summarize_indices = sorted(all_indices - keep_indices)
  
  if not summarize_indices:
    # Nothing to summarize but still over limit - must be kept events are too large
    # Fall back to even more aggressive truncation
    print(f"⚠️  Cannot summarize further, kept events exceed limit")
    # Keep only the absolute minimum: system messages + last N events
    emergency_keep = min(20, len(events) // 2)  # Keep at most 20 or half of events
    keep_indices = set(system_to_keep) | set(range(len(events) - emergency_keep, len(events)))
    summarize_indices = sorted(set(range(len(events))) - keep_indices)
    
    if not summarize_indices:
      # Still nothing to summarize - just keep recent events within hard limit
      print(f"⚠️  Emergency truncation: keeping only last {emergency_keep} events")
      return events[-emergency_keep:]
  
  # STEP 5: Create summary of old events
  events_to_summarize = [events[i] for i in summarize_indices]
  summary_text = await _summarize_events_with_llm(events_to_summarize, summarization_model)
  
  # STEP 6: Reconstruct event list
  new_events = []
  
  # Add system messages
  for i in sorted(system_to_keep):
    new_events.append(events[i])
  
  # Add summary
  summary_content = types.Content(
      role='user',
      parts=[types.Part.from_text(
          text=f"[CONTEXT SUMMARY - {len(summarize_indices)} events condensed]\n{summary_text}"
      )]
  )
  new_events.append(Event(
      invocation_id=invocation_id,
      author='context_manager',
      content=summary_content,
  ))
  
  # Add kept recent events (already truncated)
  kept_recent_indices = sorted(keep_indices - set(system_to_keep))
  for i in kept_recent_indices:
    new_events.append(events[i])
  
  # STEP 7: Verify we're under hard limit, recursively condense if needed
  new_tokens = sum(_estimate_tokens([e.content]) for e in new_events if hasattr(e, 'content') and e.content)
  
  print(f"✅ Context condensed: {current_tokens} → {new_tokens} tokens (hard limit: {hard_limit})")
  
  if new_tokens > hard_limit:
    print(f"⚠️  Still over hard limit ({new_tokens} > {hard_limit}), recursive condensation...")
    # Reduce max_recent_events for next pass and recursively condense
    os.environ['CONTEXT_MAX_RECENT_EVENTS'] = str(max(10, max_recent_events // 2))
    os.environ['CONTEXT_KEEP_RECENT_TURNS'] = str(max(2, keep_recent_turns // 2))
    return await _condense_session_context(new_events, invocation_id)
  
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
        # Skip function responses with None IDs
        if function_call_id is not None:
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
    # Skip function responses without IDs (they may be malformed or from condensation)
    if function_response.id is not None:
      function_responses_ids.add(function_response.id)
  
  # If no valid function response IDs found, return events as-is
  if not function_responses_ids:
    print(f"⚠️  Warning: Function responses found but no valid IDs. Skipping rearrangement.")
    return events

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
      # Skip function responses with None IDs
      if function_call_id is not None:
        part_indices_in_merged_event[function_call_id] = idx

  for event in function_response_events[1:]:
    if not event.content.parts:
      raise ValueError('There should be at least one function_response part.')

    for part in event.content.parts:
      if part.function_response:
        function_call_id: str = part.function_response.id  # type: ignore
        # Skip function responses with None IDs
        if function_call_id is not None and function_call_id in part_indices_in_merged_event:
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
