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


async def test_detailed_error_extractor():
  """Test the detailed build error extractor."""
  print("\n" + "="*80)
  print("Testing JsonBuildErrorExtractorTool (Detailed)")
  print("="*80)
  
  from json_analysis_tools import JsonBuildErrorExtractorTool
  
  tool = JsonBuildErrorExtractorTool()
  
  # Test with the actual session file
  session_file = "/home/hfeng1/demo/adk_openspec_project/adk_openspec_apply_agent/apply_implement-wdt-watchdog_20251218_175839.session.json"
  
  print(f"\nTesting with: {session_file}")
  
  try:
    result = await tool.run_async(
      args={"session_file": session_file},
      tool_context=None
    )
    
    print("✅ SUCCESS")
    print(f"\nSuccess: {result.get('success')}")
    if result.get('success'):
      print(f"Total build attempts: {result.get('total_build_attempts')}")
      print(f"Failed builds: {result.get('failed_builds')}")
      print(f"Successful builds: {result.get('successful_builds')}")
      
      print("\n--- Build Attempts (first 3) ---")
      for attempt in result.get('build_attempts', [])[:3]:
        print(f"\nAttempt {attempt['attempt_number']}:")
        print(f"  Success: {attempt['success']}")
        print(f"  Total errors: {attempt['total_errors']}")
        if attempt['error_types']:
          print(f"  Error types:")
          for err_type, data in attempt['error_types'].items():
            print(f"    - {err_type}: {data['count']} occurrences")
            if data['examples']:
              print(f"      Example: {data['examples'][0][:80]}...")
      
      print("\n--- Fix Analysis ---")
      fix_analysis = result.get('fix_analysis', {})
      print(f"Total fix cycles: {fix_analysis.get('total_fix_cycles')}")
      for cycle in fix_analysis.get('fix_cycles', [])[:3]:
        print(f"\nFix cycle {cycle['from_attempt']} → {cycle['to_attempt']}:")
        print(f"  Fixed: {cycle['fixed_error_types']}")
        print(f"  Persisted: {cycle['persisted_error_types']}")
        print(f"  New: {cycle['new_error_types']}")
        print(f"  Build succeeded: {cycle['build_succeeded']}")
    else:
      print(f"Error: {result.get('error')}")
    print()
  except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    print()


if __name__ == "__main__":
  print("Running basic JSON tools tests...")
  asyncio.run(test_tools())
  
  print("\n\nRunning detailed error extractor test...")
  asyncio.run(test_detailed_error_extractor())
