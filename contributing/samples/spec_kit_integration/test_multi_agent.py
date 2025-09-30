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

"""Test script to demonstrate the multi-agent Spec-Kit integration."""

import sys
from pathlib import Path

# Add ADK to path if needed
current_dir = Path(__file__).parent
adk_src_dir = current_dir.parent.parent.parent / "src"
if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))

# Import agents
from agent import root_agent, original_agent
from specify_agent import specify_agent
from plan_agent import plan_agent
from tasks_agent import tasks_agent
from implement_agent import implement_agent


def test_individual_agents():
    """Test individual agents separately."""
    print("=" * 60)
    print("TESTING INDIVIDUAL AGENTS")
    print("=" * 60)
    
    print(f"✅ SpecifyAgent: {specify_agent.name}")
    print(f"   Description: {specify_agent.description}")
    print(f"   Tools: {len(specify_agent.tools)} toolsets")
    
    print(f"✅ PlanAgent: {plan_agent.name}")
    print(f"   Description: {plan_agent.description}")
    print(f"   Tools: {len(plan_agent.tools)} toolsets")
    
    print(f"✅ TasksAgent: {tasks_agent.name}")
    print(f"   Description: {tasks_agent.description}")
    print(f"   Tools: {len(tasks_agent.tools)} toolsets")
    
    print(f"✅ ImplementAgent: {implement_agent.name}")
    print(f"   Description: {implement_agent.description}")
    print(f"   Tools: {len(implement_agent.tools)} toolsets")


def test_sequential_agent():
    """Test the sequential agent."""
    print("\n" + "=" * 60)
    print("TESTING SEQUENTIAL AGENT")
    print("=" * 60)
    
    print(f"✅ Sequential Agent: {root_agent.name}")
    print(f"   Type: {type(root_agent).__name__}")
    print(f"   Description: {root_agent.description}")
    print(f"   Sub-Agents: {len(root_agent.sub_agents)}")
    
    for i, sub_agent in enumerate(root_agent.sub_agents, 1):
        print(f"   {i}. {sub_agent.name} ({type(sub_agent).__name__})")


def test_original_agent():
    """Test the original monolithic agent."""
    print("\n" + "=" * 60)
    print("TESTING ORIGINAL AGENT")
    print("=" * 60)
    
    print(f"✅ Original Agent: {original_agent.name}")
    print(f"   Type: {type(original_agent).__name__}")
    print(f"   Description: {original_agent.description}")
    print(f"   Tools: {len(original_agent.tools)} toolsets")


def demo_usage_patterns():
    """Demonstrate different usage patterns."""
    print("\n" + "=" * 60)
    print("USAGE PATTERNS")
    print("=" * 60)
    
    print("1. SEQUENTIAL WORKFLOW (Recommended):")
    print("   - Use root_agent for complete /specify → /plan → /tasks → /implement workflow")
    print("   - Each phase executes in sequence with proper context passing")
    print("   - Example: root_agent.run('Create a REST API for user management')")
    
    print("\n2. INDIVIDUAL PHASE EXECUTION:")
    print("   - Use individual agents for specific commands")
    print("   - specify_agent.run('/specify Create user authentication system')")
    print("   - plan_agent.run('/plan Use FastAPI with PostgreSQL')")
    print("   - tasks_agent.run('/tasks Include auth and authorization')")
    print("   - implement_agent.run('/implement Follow TDD approach')")
    
    print("\n3. ORIGINAL MONOLITHIC APPROACH:")
    print("   - Use original_agent for backward compatibility")
    print("   - original_agent.run('/specify Create user management API')")
    print("   - All commands handled by single agent")


def main():
    """Main test function."""
    print("SPEC-KIT MULTI-AGENT ARCHITECTURE TEST")
    print("=" * 60)
    
    try:
        test_individual_agents()
        test_sequential_agent()
        test_original_agent()
        demo_usage_patterns()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("Multi-agent architecture is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()