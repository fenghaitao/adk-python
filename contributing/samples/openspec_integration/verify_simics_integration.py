#!/usr/bin/env python3
"""Verification script for Simics-OpenSpec integration."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openspec_integration.agent import OpenSpecAgent, detect_hardware_project


async def verify_integration():
  """Verify the Simics-OpenSpec integration."""
  print("=" * 70)
  print("Simics-OpenSpec Integration Verification")
  print("=" * 70)
  print()

  # Test 1: Hardware Detection
  print("Test 1: Hardware Detection Function")
  print("-" * 70)
  test_cases = [
    ("Create a watchdog timer device", True),
    ("Add ARM processor support", True),
    ("Build user authentication", False),
  ]
  
  for text, expected in test_cases:
    result = detect_hardware_project(text)
    status = "✓" if result == expected else "✗"
    print(f'{status} "{text}" -> {result}')
  print()

  # Test 2: Agent Creation
  print("Test 2: Agent Creation")
  print("-" * 70)
  try:
    agent = OpenSpecAgent()
    print(f"✓ Agent created successfully")
    print(f"  Name: {agent.name}")
    print(f"  Model: {agent.model}")
    print(f"  Description: {agent.description}")
    print(f"  Number of toolsets: {len(agent.tools)}")
    print()
  except Exception as e:
    print(f"✗ Failed to create agent: {e}")
    return False

  # Test 3: Available Tools
  print("Test 3: Available Tools")
  print("-" * 70)
  for toolset in agent.tools:
    toolset_name = toolset.name if hasattr(toolset, "name") else type(toolset).__name__
    print(f"Toolset: {toolset_name}")
    
    try:
      tools = await toolset.get_tools()
      print(f"  ✓ {len(tools)} tools available")
      for tool in tools[:10]:  # Show first 10
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        print(f"    - {tool_name}")
      if len(tools) > 10:
        print(f"    ... and {len(tools) - 10} more")
    except Exception as e:
      print(f"  ✗ Error getting tools: {e}")
    print()

  # Test 4: Check for Simics-specific tools
  print("Test 4: Simics-Specific Tools Check")
  print("-" * 70)
  expected_simics_tools = [
    "get_simics_version",
    "create_simics_project",
    "add_dml_device_skeleton",
    "build_simics_project",
    "run_simics_test",
    "perform_rag_query",
  ]
  
  all_tools = []
  for toolset in agent.tools:
    try:
      tools = await toolset.get_tools()
      all_tools.extend([t.name if hasattr(t, 'name') else str(t) for t in tools])
    except:
      pass
  
  for tool_name in expected_simics_tools:
    if tool_name in all_tools:
      print(f"✓ {tool_name} available")
    else:
      print(f"✗ {tool_name} NOT available")
  print()

  print("=" * 70)
  print("Verification Complete!")
  print("=" * 70)
  return True


if __name__ == "__main__":
  success = asyncio.run(verify_integration())
  sys.exit(0 if success else 1)
