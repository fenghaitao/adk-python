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

"""Simple test script for the Python configuration without LLM calls."""

import sys
from pathlib import Path

# Add the python directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from agent import root_agent


def test_agent():
    """Test the Agent OS agent configuration without LLM calls."""
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
    
    print("\n✅ Python configuration test completed successfully!")
    print("\n📝 Usage:")
    print("  - Run with ADK: adk run contributing/samples/agent_os_basic/python")
    print("  - Import in code: from contributing.samples.agent_os_basic.python import root_agent")


if __name__ == "__main__":
    test_agent()
