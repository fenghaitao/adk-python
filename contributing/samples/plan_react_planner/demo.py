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

"""Demo script comparing agent behavior with and without PlanReActPlanner.

This script runs the same query with two different agent configurations:
1. Agent WITHOUT planner (baseline)
2. Agent WITH PlanReActPlanner

It highlights the differences in how the agents structure their responses.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / 'src'
if src_path.exists():
  sys.path.insert(0, str(src_path))

from google.adk.agents.llm_agent import Agent
from google.adk.planners.plan_re_act_planner import PlanReActPlanner
from google.adk.runners import Runner

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
  """Print detailed event information."""
  for i, event in enumerate(events, 1):
    if hasattr(event, 'response_parts') and event.response_parts:
      print(f'\n--- Event {i} ---')
      for j, part in enumerate(event.response_parts, 1):
        is_thought = hasattr(part, 'thought') and part.thought

        if is_thought and show_thoughts:
          print(f'\n  [THOUGHT {j}]')
          print(f'  {part.text[:200]}...' if len(part.text) > 200 else f'  {part.text}')
        elif not is_thought and part.text:
          print(f'\n  [OUTPUT {j}]')
          print(f'  {part.text[:200]}...' if len(part.text) > 200 else f'  {part.text}')
        elif part.function_call:
          print(f'\n  [TOOL CALL {j}]: {part.function_call.name}')


def run_comparison():
  """Run the same query with and without PlanReActPlanner."""

  query = 'What are the most impactful recent papers on machine learning? Analyze their citation patterns and research trends.'

  print_section('DEMO: PlanReActPlanner Comparison')
  print(f'Query: {query}\n')

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

  # Agent WITHOUT planner
  print_section('1. Agent WITHOUT Planner (Baseline)')
  print('This agent has no explicit planning structure.')
  print('It will respond naturally based on instructions and tools.\n')

  agent_no_planner = Agent(
      model='iflow/qwen3-coder-plus',
      name='research_assistant_baseline',
      instruction=instruction,
      tools=tools,
  )

  runner = Runner()
  print('Running query...\n')

  try:
    result_no_planner = runner.run(agent_no_planner, query)
    print('\n--- Response Structure ---')
    print(f'Total events: {len(result_no_planner.events)}')
    print_event_details(result_no_planner.events, show_thoughts=False)

    print('\n--- Final Response ---')
    print(result_no_planner.response)

  except Exception as e:
    print(f'Error: {e}')

  # Agent WITH PlanReActPlanner
  print_section('2. Agent WITH PlanReActPlanner')
  print('This agent uses structured planning with explicit tags:')
  print('  - /*PLANNING*/ for initial plan')
  print('  - /*REASONING*/ for reasoning between actions')
  print('  - /*ACTION*/ for tool calls')
  print('  - /*FINAL_ANSWER*/ for the final response\n')

  agent_with_planner = Agent(
      model='iflow/qwen3-coder-plus',
      name='research_assistant_planned',
      instruction=instruction,
      tools=tools,
      planner=PlanReActPlanner(),
  )

  print('Running query...\n')

  try:
    result_with_planner = runner.run(agent_with_planner, query)
    print('\n--- Response Structure ---')
    print(f'Total events: {len(result_with_planner.events)}')
    print_event_details(result_with_planner.events, show_thoughts=True)

    print('\n--- Final Response (without thoughts) ---')
    print(result_with_planner.response)

  except Exception as e:
    print(f'Error: {e}')

  # Summary
  print_section('Key Differences')
  print("""
1. STRUCTURE:
   - Without planner: Natural flow, implicit reasoning
   - With planner: Explicit planning, reasoning, and action phases

2. TRANSPARENCY:
   - Without planner: Reasoning mixed with output
   - With planner: Reasoning separated as "thoughts" (thought=True)

3. PLANNING:
   - Without planner: Agent decides actions on-the-fly
   - With planner: Agent creates explicit plan before acting

4. DEBUGGING:
   - Without planner: Harder to see decision-making process
   - With planner: Clear visibility into planning and reasoning

5. TOKEN USAGE:
   - Without planner: More efficient (no planning overhead)
   - With planner: Higher token usage (explicit planning text)

WHEN TO USE PLANREACTPLANNER:
✓ Complex multi-step workflows
✓ Need to debug agent reasoning
✓ Tasks requiring adaptation based on results
✓ Iterative processes (build → test → fix)

WHEN TO SKIP IT:
✗ Simple, single-step queries
✗ Token-sensitive applications
✗ Already have structured instructions
✗ Need maximum control over output format
  """)


if __name__ == '__main__':
  run_comparison()
