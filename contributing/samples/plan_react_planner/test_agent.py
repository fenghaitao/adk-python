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

"""Tests for the PlanReActPlanner example agent."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent.parent / 'src'
if src_path.exists():
  sys.path.insert(0, str(src_path))

import pytest
from google.adk.runners import Runner

from agent import root_agent


def test_agent_initialization():
  """Test that the agent initializes correctly with PlanReActPlanner."""
  assert root_agent is not None
  assert root_agent.name == 'research_assistant'
  assert root_agent.planner is not None
  assert root_agent.planner.__class__.__name__ == 'PlanReActPlanner'


def test_agent_has_tools():
  """Test that the agent has the expected tools."""
  assert len(root_agent.tools) == 4
  tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in root_agent.tools]
  assert 'search_papers' in tool_names
  assert 'get_citation_count' in tool_names
  assert 'analyze_research_trends' in tool_names
  assert 'calculate_research_impact' in tool_names


@pytest.mark.skip(reason='Requires API key and makes actual LLM calls')
def test_agent_simple_query():
  """Test agent with a simple query (requires API key)."""
  runner = Runner()
  result = runner.run(
      root_agent, 'Find papers on machine learning and tell me about them.'
  )

  assert result is not None
  assert result.response is not None
  assert len(result.response) > 0

  # Check that planning tags appear in the response
  has_planning = False
  for event in result.events:
    if hasattr(event, 'response_parts'):
      for part in event.response_parts:
        if part.text and '/*PLANNING*/' in part.text:
          has_planning = True
          break

  # Note: Planning tags might not always appear depending on model behavior
  # This is informational rather than a strict requirement
  if has_planning:
    print('✓ Agent used explicit planning')
  else:
    print('ℹ Agent responded without explicit planning tags')


@pytest.mark.skip(reason='Requires API key and makes actual LLM calls')
def test_agent_complex_query():
  """Test agent with a complex multi-step query (requires API key)."""
  runner = Runner()
  result = runner.run(
      root_agent,
      'Compare the research impact between machine learning and quantum computing. '
      'Include citation analysis and trend data.',
  )

  assert result is not None
  assert result.response is not None

  # Check for thought separation
  has_thoughts = False
  for event in result.events:
    if hasattr(event, 'response_parts'):
      for part in event.response_parts:
        if hasattr(part, 'thought') and part.thought:
          has_thoughts = True
          break

  if has_thoughts:
    print('✓ Agent separated reasoning as thoughts')
  else:
    print('ℹ No explicit thoughts found in response')


if __name__ == '__main__':
  # Run basic tests without pytest
  print('Testing PlanReActPlanner example agent...\n')

  print('1. Testing agent initialization...')
  test_agent_initialization()
  print('   ✓ Agent initialized correctly\n')

  print('2. Testing agent tools...')
  test_agent_has_tools()
  print('   ✓ All tools present\n')

  print('All basic tests passed!')
  print('\nTo run full tests with LLM calls:')
  print('  pytest contributing/samples/plan_react_planner/test_agent.py -v')
