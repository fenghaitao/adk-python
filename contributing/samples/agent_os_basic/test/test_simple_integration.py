#!/usr/bin/env python3
"""Simple test for Agent OS integration with ADK."""

import sys
import os
import tempfile
from pathlib import Path

# Add the python directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

# Test the Agent OS tools directly
def test_agent_os_tools():
    """Test Agent OS tools functionality."""
    print("Testing Agent OS Tools...")
    
    try:
        from agent_os_tools import create_agent_os_toolset
        
        # Create toolset
        toolset = create_agent_os_toolset()
        print(f"✓ Created toolset with {len(toolset.tools)} tools")
        
        # Test individual tools
        tool_names = [tool.name for tool in toolset.tools]
        expected_tools = ['read_file', 'write_file', 'grep_search', 'glob_search', 'bash_command']
        
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print(f"✓ Found tool: {expected_tool}")
            else:
                print(f"✗ Missing tool: {expected_tool}")
                return False
        
        print("✓ All expected tools found")
        return True
        
    except Exception as e:
        print(f"✗ Error testing tools: {e}")
        return False

def test_agent_os_agent_creation():
    """Test creating Agent OS Agent."""
    print("\nTesting Agent OS Agent Creation...")
    
    try:
        try:
            from .agent_os_agent import AgentOsAgent
        except ImportError:
            from agent_os_agent import AgentOsAgent
        
        # Create agent
        agent = AgentOsAgent(
            name="test_agent",
            model="gemini-2.0-flash",
        )
        
        print(f"✓ Created agent: {agent.name}")
        print(f"✓ Model: {agent.model}")
        print(f"✓ Tools: {len(agent.tools)}")
        print(f"✓ Description: {agent.description[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        return False

def test_agent_os_config():
    """Test Agent OS configuration loading."""
    print("\nTesting Agent OS Configuration...")
    
    try:
        try:
            from .agent_os_agent import AgentOsAgent
        except ImportError:
            from agent_os_agent import AgentOsAgent
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock Agent OS structure
            agent_os_path = Path(temp_dir) / "agent-os"
            agent_os_path.mkdir()
            config_file = agent_os_path / "config.yml"
            config_file.write_text("agent_os_version: 1.4.1\n")
            
            agent = AgentOsAgent.create_with_agent_os_config(
                agent_os_path=str(agent_os_path),
                project_path=".",
            )
            
            print(f"✓ Created agent with Agent OS config")
            print(f"✓ Agent OS path: {agent_os_path}")
            print(f"✓ Instruction contains 'Agent OS': {'Agent OS' in agent.instruction}")
            
            return True
            
    except Exception as e:
        print(f"✗ Error testing Agent OS config: {e}")
        return False

def test_subagents():
    """Test adding subagents."""
    print("\nTesting Subagents...")
    
    try:
        try:
            from .agent_os_agent import AgentOsAgent
        except ImportError:
            from agent_os_agent import AgentOsAgent
        
        agent = AgentOsAgent(name="test_agent")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_os_path = Path(temp_dir) / "agent-os"
            agent_os_path.mkdir()
            
            agent.add_agent_os_subagents(str(agent_os_path))
            
            print(f"✓ Added {len(agent.sub_agents)} subagents")
            
            subagent_names = [sub.name for sub in agent.sub_agents]
            expected_subagents = ['context_fetcher', 'file_creator', 'project_manager', 'git_workflow', 'test_runner', 'date_checker']
            
            for expected_subagent in expected_subagents:
                if expected_subagent in subagent_names:
                    print(f"✓ Found subagent: {expected_subagent}")
                else:
                    print(f"✗ Missing subagent: {expected_subagent}")
                    return False
            
            return True
            
    except Exception as e:
        print(f"✗ Error testing subagents: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Agent OS Integration Test")
    print("=" * 40)
    
    tests = [
        test_agent_os_tools,
        test_agent_os_agent_creation,
        test_agent_os_config,
        test_subagents,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
