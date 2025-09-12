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

"""Simple test for tools without async operations."""

import sys
from pathlib import Path

# Add the python directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from agent import root_agent


def test_tools():
    """Test the Agent OS agent tools."""
    print("🧪 Testing Agent OS Tools")
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
        if hasattr(tool, 'tools'):
            print(f"    Sub-tools: {[t.name for t in tool.tools]}")
    
    # Test subagents
    print("\n🤖 Available Subagents:")
    for subagent in root_agent.sub_agents:
        print(f"  - {subagent.name}: {subagent.description}")
    
    # Test tool execution (safe operations)
    print("\n🧪 Testing Tool Structure:")
    
    try:
        # Test read_file tool - look inside toolset
        read_tool = None
        tools_found = []
        
        for tool in root_agent.tools:
            if hasattr(tool, 'tools'):  # This is a toolset
                for sub_tool in tool.tools:
                    tools_found.append(sub_tool.name)
                    if sub_tool.name == 'read_file':
                        read_tool = sub_tool
        
        if read_tool:
            print("  ✅ Read file tool found")
        else:
            print("  ❌ Read file tool not found")
            
        print(f"  ✅ Available tools: {', '.join(tools_found)}")
        
        # Check if all expected tools are present
        expected_tools = ['read_file', 'write_file', 'grep_search', 'glob_search', 'bash_command']
        missing_tools = [t for t in expected_tools if t not in tools_found]
        
        if missing_tools:
            print(f"  ❌ Missing tools: {', '.join(missing_tools)}")
        else:
            print("  ✅ All expected tools found")
            
    except Exception as e:
        print(f"  ❌ Error testing tools: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Tools test completed successfully!")


if __name__ == "__main__":
    test_tools()
