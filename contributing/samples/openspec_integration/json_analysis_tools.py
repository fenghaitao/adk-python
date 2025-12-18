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

"""JSON analysis tools for meta_improve_json_agent.

This module provides Python-based tools for analyzing session JSON files
without using bash commands.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.adk.tools import BaseTool
from google.adk.tools.tool_context import ToolContext
from pydantic import BaseModel, Field


class SessionMetrics(BaseModel):
  """Metrics extracted from a session."""
  session_file: str
  start_time: str
  end_time: str
  duration_minutes: float
  total_events: int
  build_attempts: int
  build_failures: int
  test_runs: int
  test_failures: int
  tool_calls: Dict[str, int]


class ErrorPattern(BaseModel):
  """An error pattern found in the session."""
  error_type: str
  count: int
  examples: List[str]


class JsonSessionMetricsTool(BaseTool):
  """Extract metrics from a JSON session file."""

  def __init__(self):
    super().__init__(
      name="extract_session_metrics",
      description=(
        "Extract comprehensive metrics from a session JSON file including "
        "build attempts, test runs, duration, and tool usage statistics. "
        "Returns structured data about the session execution."
      ),
    )

  class InputSchema(BaseModel):
    """Input schema for extract_session_metrics."""
    session_file: str = Field(
      ...,
      description="Path to the session JSON file to analyze"
    )

  async def run(
    self,
    context: ToolContext,
    session_file: str,
  ) -> Dict[str, Any]:
    """Extract metrics from session JSON file."""
    try:
      file_path = Path(session_file)
      if not file_path.exists():
        return {
          "success": False,
          "error": f"Session file not found: {session_file}"
        }

      with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)

      events = session_data.get('events', [])
      
      # Extract timestamps
      start_time = None
      end_time = None
      for event in events:
        timestamp = event.get('timestamp')
        if timestamp:
          if not start_time:
            start_time = timestamp
          end_time = timestamp

      # Calculate duration
      duration_minutes = 0.0
      if start_time and end_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration_minutes = (end_dt - start_dt).total_seconds() / 60.0

      # Count tool calls
      tool_calls = Counter()
      build_attempts = 0
      build_failures = 0
      test_runs = 0
      test_failures = 0

      for event in events:
        event_type = event.get('type')
        
        if event_type == 'tool_call':
          tool_name = event.get('tool_name', 'unknown')
          tool_calls[tool_name] += 1
          
          if tool_name == 'build_simics_project':
            build_attempts += 1
          elif tool_name == 'run_simics_test':
            test_runs += 1
            
        elif event_type == 'tool_result':
          tool_name = event.get('tool_name', 'unknown')
          result = event.get('result', {})
          
          if tool_name == 'build_simics_project':
            if isinstance(result, dict):
              success = result.get('success', True)
              if not success:
                build_failures += 1
          elif tool_name == 'run_simics_test':
            # Check for test failures in result
            if isinstance(result, dict):
              output = str(result.get('output', ''))
              if 'failed' in output.lower():
                test_failures += 1

      metrics = SessionMetrics(
        session_file=session_file,
        start_time=start_time or "unknown",
        end_time=end_time or "unknown",
        duration_minutes=round(duration_minutes, 1),
        total_events=len(events),
        build_attempts=build_attempts,
        build_failures=build_failures,
        test_runs=test_runs,
        test_failures=test_failures,
        tool_calls=dict(tool_calls)
      )

      return {
        "success": True,
        "metrics": metrics.model_dump()
      }

    except json.JSONDecodeError as e:
      return {
        "success": False,
        "error": f"Failed to parse JSON: {str(e)}"
      }
    except Exception as e:
      return {
        "success": False,
        "error": f"Error extracting metrics: {str(e)}"
      }


class JsonErrorPatternTool(BaseTool):
  """Extract error patterns from a JSON session file."""

  def __init__(self):
    super().__init__(
      name="extract_error_patterns",
      description=(
        "Extract and analyze error patterns from a session JSON file. "
        "Identifies compilation errors, test failures, and other error types "
        "with their frequencies and examples."
      ),
    )

  class InputSchema(BaseModel):
    """Input schema for extract_error_patterns."""
    session_file: str = Field(
      ...,
      description="Path to the session JSON file to analyze"
    )
    max_examples: int = Field(
      3,
      description="Maximum number of examples to include per error type"
    )

  async def run(
    self,
    context: ToolContext,
    session_file: str,
    max_examples: int = 3,
  ) -> Dict[str, Any]:
    """Extract error patterns from session JSON file."""
    try:
      file_path = Path(session_file)
      if not file_path.exists():
        return {
          "success": False,
          "error": f"Session file not found: {session_file}"
        }

      with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)

      events = session_data.get('events', [])
      
      # Collect errors by type
      error_patterns = {}
      
      for event in events:
        event_type = event.get('type')
        
        if event_type == 'tool_result':
          tool_name = event.get('tool_name', 'unknown')
          result = event.get('result', {})
          
          # Extract errors from build results
          if tool_name == 'build_simics_project':
            if isinstance(result, dict):
              error_msg = result.get('error', '')
              output = result.get('output', '')
              
              # Parse compilation errors
              error_text = error_msg or output
              if error_text:
                self._extract_compilation_errors(
                  error_text,
                  error_patterns,
                  max_examples
                )
          
          # Extract errors from test results
          elif tool_name == 'run_simics_test':
            if isinstance(result, dict):
              output = str(result.get('output', ''))
              if 'failed' in output.lower():
                error_type = 'test_failure'
                if error_type not in error_patterns:
                  error_patterns[error_type] = {
                    'count': 0,
                    'examples': []
                  }
                error_patterns[error_type]['count'] += 1
                if len(error_patterns[error_type]['examples']) < max_examples:
                  # Extract test name
                  for line in output.split('\n'):
                    if 'failed' in line.lower():
                      error_patterns[error_type]['examples'].append(
                        line.strip()
                      )
                      break

      # Convert to list format
      patterns = []
      for error_type, data in error_patterns.items():
        patterns.append(ErrorPattern(
          error_type=error_type,
          count=data['count'],
          examples=data['examples'][:max_examples]
        ))

      # Sort by count (most frequent first)
      patterns.sort(key=lambda x: x.count, reverse=True)

      return {
        "success": True,
        "error_patterns": [p.model_dump() for p in patterns],
        "total_error_types": len(patterns),
        "total_errors": sum(p.count for p in patterns)
      }

    except json.JSONDecodeError as e:
      return {
        "success": False,
        "error": f"Failed to parse JSON: {str(e)}"
      }
    except Exception as e:
      return {
        "success": False,
        "error": f"Error extracting error patterns: {str(e)}"
      }

  def _extract_compilation_errors(
    self,
    error_text: str,
    error_patterns: Dict,
    max_examples: int
  ):
    """Extract compilation error patterns from error text."""
    lines = error_text.split('\n')
    
    for line in lines:
      if 'error:' in line.lower():
        # Extract error type
        if 'unknown identifier' in line:
          error_type = 'unknown_identifier'
        elif 'unknown template' in line:
          error_type = 'unknown_template'
        elif 'name collision' in line:
          error_type = 'name_collision'
        elif 'non-boolean condition' in line:
          error_type = 'non_boolean_condition'
        elif 'type mismatch' in line:
          error_type = 'type_mismatch'
        else:
          error_type = 'other_compilation_error'
        
        if error_type not in error_patterns:
          error_patterns[error_type] = {
            'count': 0,
            'examples': []
          }
        
        error_patterns[error_type]['count'] += 1
        if len(error_patterns[error_type]['examples']) < max_examples:
          error_patterns[error_type]['examples'].append(line.strip())


class JsonSessionQueryTool(BaseTool):
  """Query specific information from a JSON session file."""

  def __init__(self):
    super().__init__(
      name="query_session_data",
      description=(
        "Query specific information from a session JSON file using JSONPath-like "
        "queries. Can extract tool calls, agent messages, timestamps, and other "
        "structured data from the session."
      ),
    )

  class InputSchema(BaseModel):
    """Input schema for query_session_data."""
    session_file: str = Field(
      ...,
      description="Path to the session JSON file to query"
    )
    query_type: str = Field(
      ...,
      description=(
        "Type of query: 'tool_calls', 'agent_messages', 'user_messages', "
        "'tool_results', 'timestamps', 'event_count'"
      )
    )
    filter_tool: Optional[str] = Field(
      None,
      description="Filter by specific tool name (for tool_calls/tool_results)"
    )
    limit: int = Field(
      10,
      description="Maximum number of results to return"
    )

  async def run(
    self,
    context: ToolContext,
    session_file: str,
    query_type: str,
    filter_tool: Optional[str] = None,
    limit: int = 10,
  ) -> Dict[str, Any]:
    """Query session JSON file."""
    try:
      file_path = Path(session_file)
      if not file_path.exists():
        return {
          "success": False,
          "error": f"Session file not found: {session_file}"
        }

      with open(file_path, 'r', encoding='utf-8') as f:
        session_data = json.load(f)

      events = session_data.get('events', [])
      results = []

      if query_type == 'tool_calls':
        for event in events:
          if event.get('type') == 'tool_call':
            tool_name = event.get('tool_name')
            if not filter_tool or tool_name == filter_tool:
              results.append({
                'tool_name': tool_name,
                'timestamp': event.get('timestamp'),
                'arguments': event.get('arguments', {})
              })
              if len(results) >= limit:
                break

      elif query_type == 'tool_results':
        for event in events:
          if event.get('type') == 'tool_result':
            tool_name = event.get('tool_name')
            if not filter_tool or tool_name == filter_tool:
              results.append({
                'tool_name': tool_name,
                'timestamp': event.get('timestamp'),
                'result': event.get('result', {})
              })
              if len(results) >= limit:
                break

      elif query_type == 'agent_messages':
        for event in events:
          if event.get('type') == 'agent_message':
            results.append({
              'timestamp': event.get('timestamp'),
              'content': event.get('content', '')
            })
            if len(results) >= limit:
              break

      elif query_type == 'user_messages':
        for event in events:
          if event.get('type') == 'user_message':
            results.append({
              'timestamp': event.get('timestamp'),
              'content': event.get('content', '')
            })
            if len(results) >= limit:
              break

      elif query_type == 'timestamps':
        for event in events[:limit]:
          results.append({
            'type': event.get('type'),
            'timestamp': event.get('timestamp')
          })

      elif query_type == 'event_count':
        event_types = Counter(event.get('type') for event in events)
        results = [
          {'event_type': k, 'count': v}
          for k, v in event_types.most_common(limit)
        ]

      return {
        "success": True,
        "query_type": query_type,
        "filter_tool": filter_tool,
        "results": results,
        "result_count": len(results),
        "total_events": len(events)
      }

    except json.JSONDecodeError as e:
      return {
        "success": False,
        "error": f"Failed to parse JSON: {str(e)}"
      }
    except Exception as e:
      return {
        "success": False,
        "error": f"Error querying session: {str(e)}"
      }
