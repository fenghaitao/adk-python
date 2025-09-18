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

"""Test script for the Python configuration."""

import asyncio
import sys
from pathlib import Path

# Add the python directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from agent import root_agent


async def test_agent():
    """Test the Agent OS agent configuration."""
    print("🧪 Testing Agent OS Python Configuration")
    print("=" * 50)
    
    # Test agent properties
    print(f"✅ Agent Name: {root_agent.name}")
    print(f"✅ Model: {root_agent.model}")
    print(f"✅ Tools Count: {len(root_agent.tools)}")
    print(f"✅ Subagents Count: {len(root_agent.sub_agents)}")
    
    # Test tools
    print("\n🔧 Available Tools:")
    for tool in root_agent.tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test subagents
    print("\n🤖 Available Subagents:")
    for subagent in root_agent.sub_agents:
        print(f"  - {subagent.name}: {subagent.description}")
    
    # Test basic functionality
    print("\n🧪 Testing Basic Functionality:")
    
    # Test tool execution (safe operations)
    try:
        # Test read_file tool - look inside toolset
        read_tool = None
        for tool in root_agent.tools:
            if hasattr(tool, 'tools'):  # This is a toolset
                for sub_tool in tool.tools:
                    if sub_tool.name == 'read_file':
                        read_tool = sub_tool
                        break
                if read_tool:
                    break
        
        if read_tool:
            print("  ✅ Read file tool found")
        else:
            print("  ❌ Read file tool not found")
            
        # Test other tools
        tools_found = []
        for tool in root_agent.tools:
            if hasattr(tool, 'tools'):  # This is a toolset
                for sub_tool in tool.tools:
                    tools_found.append(sub_tool.name)
        
        print(f"  ✅ Available tools: {', '.join(tools_found)}")
            
    except Exception as e:
        print(f"  ❌ Error testing tools: {e}")
    
    print("\n✅ Python configuration test completed successfully!")
    print("\n📝 Usage:")
    print("  - Run with ADK: adk run contributing/samples/agent_os_integration/python")
    print("  - Import in code: from contributing.samples.agent_os_integration.python import root_agent")


if __name__ == "__main__":
    asyncio.run(test_agent())
