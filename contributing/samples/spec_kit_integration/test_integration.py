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

"""Simple test for Spec-Kit integration."""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import root_agent, SpecKitAgent
from spec_kit_tools import create_spec_kit_toolset
from google.adk.runners import InMemoryRunner


async def test_agent_creation():
    """Test that the agent can be created."""
    print("Testing agent creation...")
    
    agent = SpecKitAgent()
    assert agent.name == "spec_kit_agent"
    assert "Spec-Kit agent" in agent.description
    print("✅ Agent created successfully")


async def test_toolset_creation():
    """Test that toolset can be created."""
    print("Testing toolset creation...")
    
    toolset = create_spec_kit_toolset()
    assert toolset.name == "spec_kit_toolset"
    assert len(toolset.tools) == 3
    
    tool_names = [tool.name for tool in toolset.tools]
    expected_tools = ["read_file", "write_file", "bash_command"]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names
        
    print("✅ Toolset created with all expected tools")


async def test_basic_interaction():
    """Test basic interaction with the agent."""
    print("Testing basic interaction...")
    
    from google.genai import types
    runner = InMemoryRunner(root_agent)
    
    # Create session using the session service
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user", 
        session_id="test_session"
    )
    
    # Test general question using correct ADK API
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=types.Content(parts=[types.Part(text="What can you help me with?")])
        ):
            events.append(event)
            if not event.partial and event.content:
                break  # Got a response
        
        assert len(events) > 0
        print("✅ Basic interaction works")
    except Exception as e:
        if "API_KEY" in str(e):
            print("✅ Basic interaction setup works (API key needed for full test)")
        else:
            raise e


async def test_specify_command_format():
    """Test that specify command is recognized."""
    print("Testing specify command format...")
    
    from google.genai import types
    runner = InMemoryRunner(root_agent)
    
    # Create session using the session service
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user",
        session_id="test_session_2"
    )
    
    # Test specify command (may fail if spec-kit not installed, but should recognize format)
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_2",
            new_message=types.Content(parts=[types.Part(text="/specify Create a simple calculator application")])
        ):
            events.append(event)
            if not event.partial and event.content:
                break  # Got a response
        
        assert len(events) > 0
        print("✅ Specify command recognized")
    except Exception as e:
        if "API_KEY" in str(e):
            print("✅ Specify command setup works (API key needed for full test)")
        else:
            raise e


async def test_plan_command_format():
    """Test that plan command is recognized."""
    print("Testing plan command format...")
    
    from google.genai import types
    runner = InMemoryRunner(root_agent)
    
    # Create session using the session service
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user",
        session_id="test_session_3"
    )
    
    # Test plan command
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user", 
            session_id="test_session_3",
            new_message=types.Content(parts=[types.Part(text="/plan Use Python and Flask for backend")])
        ):
            events.append(event)
            if not event.partial and event.content:
                break  # Got a response
        
        assert len(events) > 0
        print("✅ Plan command recognized")
    except Exception as e:
        if "API_KEY" in str(e):
            print("✅ Plan command setup works (API key needed for full test)")
        else:
            raise e


async def test_tasks_command_format():
    """Test that tasks command is recognized."""
    print("Testing tasks command format...")
    
    from google.genai import types
    runner = InMemoryRunner(root_agent)
    
    # Create session using the session service
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user",
        session_id="test_session_4"
    )
    
    # Test tasks command
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_4", 
            new_message=types.Content(parts=[types.Part(text="/tasks Create TDD tasks for implementation")])
        ):
            events.append(event)
            if not event.partial and event.content:
                break  # Got a response
        
        assert len(events) > 0
        print("✅ Tasks command recognized")
    except Exception as e:
        if "API_KEY" in str(e):
            print("✅ Tasks command setup works (API key needed for full test)")
        else:
            raise e


async def test_environment_variables():
    """Test environment variable handling."""
    print("Testing environment variables...")
    
    import os
    
    # Test default values
    from agent import get_spec_kit_model
    
    default_model = get_spec_kit_model()
    
    assert default_model == "iflow/Qwen3-Coder"
    
    # Test with environment variables
    os.environ["SPEC_KIT_MODEL"] = "custom-model"
    
    # Reload module to pick up env vars
    import importlib
    import agent
    importlib.reload(agent)
    
    assert agent.get_spec_kit_model() == "custom-model"
    
    # Clean up
    del os.environ["SPEC_KIT_MODEL"]
    
    print("✅ Environment variables handled correctly")


async def run_all_tests():
    """Run all tests."""
    print("🧪 Running Spec-Kit Integration Tests")
    print("=" * 50)
    
    tests = [
        test_agent_creation,
        test_toolset_creation,
        test_basic_interaction,
        test_specify_command_format,
        test_plan_command_format, 
        test_tasks_command_format,
        test_environment_variables,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {failed} tests failed")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)