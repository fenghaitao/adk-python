#!/usr/bin/env python3
"""Standalone test for JSON analysis tools."""

import asyncio
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
adk_src_dir = current_dir.parent.parent.parent / "src"
if adk_src_dir.exists():
  sys.path.insert(0, str(adk_src_dir))

from json_analysis_tools import (
  JsonSessionMetricsTool,
  JsonErrorPatternTool,
  JsonSessionQueryTool,
)


async def test_tools():
  """Test JSON analysis tools with a real session file."""
  
  # Find a session file - use the apply session that has build/test attempts
  session_file = "/home/hfeng1/demo/adk_openspec_project/adk_openspec_apply_agent/apply_implement-wdt-watchdog_20251218_175839.session.json"
  
  print("=" * 80)
  print("Testing JSON Analysis Tools")
  print("=" * 80)
  print(f"Session file: {session_file}")
  print()
  
  # Test 1: Extract Session Metrics
  print("-" * 80)
  print("TEST 1: Extract Session Metrics")
  print("-" * 80)
  
  metrics_tool = JsonSessionMetricsTool()
  try:
    result = await metrics_tool.run_async(
      args={"session_file": session_file},
      tool_context=None
    )
    print("✅ SUCCESS")
    print(f"Result: {result}")
    print()
  except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()
  
  # Test 2: Extract Error Patterns
  print("-" * 80)
  print("TEST 2: Extract Error Patterns")
  print("-" * 80)
  
  error_tool = JsonErrorPatternTool()
  try:
    result = await error_tool.run_async(
      args={"session_file": session_file, "max_examples": 3},
      tool_context=None
    )
    print("✅ SUCCESS")
    print(f"Result: {result}")
    print()
  except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()
  
  # Test 3: Query Session Data
  print("-" * 80)
  print("TEST 3: Query Session Data (tool_calls)")
  print("-" * 80)
  
  query_tool = JsonSessionQueryTool()
  try:
    result = await query_tool.run_async(
      args={"session_file": session_file, "query_type": "tool_calls", "limit": 5},
      tool_context=None
    )
    print("✅ SUCCESS")
    print(f"Result: {result}")
    print()
  except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()
  
  # Test 4: Query Session Data (event_count)
  print("-" * 80)
  print("TEST 4: Query Session Data (event_count)")
  print("-" * 80)
  
  try:
    result = await query_tool.run_async(
      args={"session_file": session_file, "query_type": "event_count", "limit": 10},
      tool_context=None
    )
    print("✅ SUCCESS")
    print(f"Result: {result}")
    print()
  except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()
  
  print("=" * 80)
  print("All tests completed")
  print("=" * 80)


if __name__ == "__main__":
  asyncio.run(test_tools())
