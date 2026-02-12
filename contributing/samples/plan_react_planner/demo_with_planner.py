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

"""Demo script showing agent behavior WITH PlanReActPlanner.

This script demonstrates an agent that uses structured planning with explicit
tags for planning, reasoning, actions, and final answers.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / 'src'
if src_path.exists():
  sys.path.insert(0, str(src_path))

# Add tests to path for testing utilities
tests_path = Path(__file__).parent.parent.parent.parent / 'tests' / 'unittests'
if tests_path.exists():
  sys.path.insert(0, str(tests_path))

from google.adk.agents.llm_agent import Agent
from google.adk.planners.plan_re_act_planner import PlanReActPlanner
import testing_utils

# Import tools from agent.py
from agent import (
    analyze_research_trends,
    calculate_research_impact,
    get_citation_count,
    search_papers,
)


def print_section(title: str):
  """Print a formatted section header."""
  print('\n' + '=' * 80)
  print(f'  {title}')
  print('=' * 80 + '\n')


def print_event_details(events, show_thoughts: bool = True):
  """Print detailed event information.
  
  Events come in pairs when tools are used:
  - Odd events: Agent's response with thoughts/reasoning + tool call
  - Even events: Tool's response (function response)
  """
  for i, event in enumerate(events, 1):
    if hasattr(event, 'content') and event.content and event.content.parts:
      print(f'\n--- Event {i} (Author: {event.author}) ---')
      for j, part in enumerate(event.content.parts, 1):
        is_thought = hasattr(part, 'thought') and part.thought

        if is_thought and show_thoughts:
          print(f'  [THOUGHT {j}]')
          print(f'  {part.text[:200]}...' if len(part.text) > 200 else f'  {part.text}')
        elif not is_thought and part.text:
          print(f'  [OUTPUT {j}]')
          print(f'  {part.text[:200]}...' if len(part.text) > 200 else f'  {part.text}')
        elif part.function_call:
          print(f'  [TOOL CALL {j}]: {part.function_call.name}')
        elif part.function_response:
          print(f'  [TOOL RESPONSE {j}]: {part.function_response.name}')


def main():
  """Run the demo with planner."""
  query = 'What are the most impactful recent papers on machine learning? Analyze their citation patterns and research trends.'

  print_section('Agent WITH PlanReActPlanner')
  print(f'Query: {query}\n')
  print('This agent uses structured planning with explicit tags:')
  print('  - /*PLANNING*/ for initial plan')
  print('  - /*REASONING*/ for reasoning between actions')
  print('  - /*ACTION*/ for tool calls')
  print('  - /*FINAL_ANSWER*/ for the final response\n')

  # Configuration
  tools = [
      search_papers,
      get_citation_count,
      analyze_research_trends,
      calculate_research_impact,
  ]

  instruction = """
You are a research assistant that helps users understand academic research topics.

Your capabilities:
- Search for academic papers on various topics
- Analyze citation patterns and research impact
- Identify research trends over time
- Provide comprehensive summaries of research areas

Be thorough but concise. Always cite specific papers when making claims.
  """

  agent = Agent(
      model='iflow/qwen3-coder-plus',
      name='research_assistant_planned',
      instruction=instruction,
      tools=tools,
      planner=PlanReActPlanner(),
  )

  runner = testing_utils.InMemoryRunner(agent)
  print('Running query...\n')

  try:
    result = runner.run(query)
    print('\n--- Response Structure ---')
    print(f'Total events: {len(result)}')
    print_event_details(result, show_thoughts=True)

    print('\n--- Final Response (without thoughts) ---')
    if result:
      final_event = result[-1]
      if hasattr(final_event, 'content') and final_event.content:
        for part in final_event.content.parts:
          if part.text and not (hasattr(part, 'thought') and part.thought):
            print(part.text)

  except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

  print_section('Key Characteristics')
  print("""
WITH PLANNER CHARACTERISTICS:
- Explicit planning, reasoning, and action phases
- Reasoning separated as "thoughts" (thought=True)
- Uses structured tags: /*PLANNING*/, /*REASONING*/, /*ACTION*/, /*FINAL_ANSWER*/
- Agent creates explicit plan before acting
- Clear visibility into planning and reasoning
- Higher token usage (explicit planning text)
- Better for debugging and complex workflows

EVENT STRUCTURE:
Events come in pairs when tools are called:
  - Odd events (1, 3, 5...): Agent's THOUGHT (reasoning) + tool call
  - Even events (2, 4, 6...): Tool response
  - Final event: Agent's THOUGHT (/*FINAL_ANSWER*/) + OUTPUT
  
The key difference: Reasoning is marked as THOUGHT and separated from OUTPUT,
making it easy to filter internal reasoning from user-facing responses.
  """)


if __name__ == '__main__':
  main()
