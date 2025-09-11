#!/usr/bin/env python3
"""Safe example of using Agent OS Agent with Agent OS integration."""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from .agent_os_agent import AgentOsAgent
from google.adk.runners import Runner


async def main():
    """Example usage of Agent OS Agent with Agent OS integration."""
    
    print("🤖 Agent OS Agent Example")
    print("=" * 50)
    
    # Set up paths
    agent_os_path = "/home/hfeng1/agent-os"
    project_path = "."
    
    print(f"Agent OS path: {agent_os_path}")
    print(f"Project path: {project_path}")
    
    try:
        # Create Agent OS Agent with Agent OS configuration
        print("\n1. Creating Agent OS Agent...")
        agent_os_agent = AgentOsAgent.create_with_agent_os_config(
            agent_os_path=agent_os_path,
            project_path=project_path,
            name="agent_os_agent",
            model="iflow/Qwen3-Coder",
        )
        print(f"✓ Created agent: {agent_os_agent.name}")
        print(f"✓ Model: {agent_os_agent.model}")
        print(f"✓ Tools: {len(agent_os_agent.tools)}")
        
        # Add Agent OS subagents
        print("\n2. Adding Agent OS subagents...")
        agent_os_agent.add_agent_os_subagents(agent_os_path)
        print(f"✓ Added {len(agent_os_agent.sub_agents)} subagents")
        
        # Show subagent details
        for subagent in agent_os_agent.sub_agents:
            print(f"   - {subagent.name}: {subagent.description}")
        
        # Create a runner
        print("\n3. Creating runner...")
        runner = Runner()
        print("✓ Runner created")
        
        # Test the agent without LLM calls first
        print("\n4. Testing agent configuration...")
        print(f"✓ Agent instruction length: {len(agent_os_agent.instruction)} characters")
        print(f"✓ Agent has Agent OS tools: {any('agent_os' in str(tool) for tool in agent_os_agent.tools)}")
        
        # Show available tools
        print("\n5. Available tools:")
        for toolset in agent_os_agent.tools:
            if hasattr(toolset, 'tools'):
                for tool in toolset.tools:
                    print(f"   - {tool.name}: {tool.description}")
        
        print("\n6. Testing tools directly...")
        await test_tools_directly(agent_os_agent)
        
        print("\n" + "=" * 50)
        print("🎉 Agent OS Agent setup completed successfully!")
        print("\nNote: To use the agent with LLM calls, you need to:")
        print("1. Set up Google Cloud authentication")
        print("2. Configure API keys for the Gemini model")
        print("3. Ensure proper network access to Google's APIs")
        
        # Uncomment the following lines to test with actual LLM calls
        # (requires proper authentication setup)
        """
        print("\n7. Testing with LLM calls...")
        try:
            response = await runner.run_async(
                agent=agent_os_agent,
                user_input="Hello! Can you tell me about your capabilities?"
            )
            print("Response:", response)
        except Exception as e:
            print(f"LLM call failed (expected without auth): {e}")
        """
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_tools_directly(agent):
    """Test the agent's tools directly without LLM calls."""
    print("   Testing Agent OS tools...")
    
    # Get the toolset
    toolset = None
    for tool in agent.tools:
        if hasattr(tool, 'tools') and len(tool.tools) > 0:
            toolset = tool
            break
    
    if not toolset:
        print("   ❌ No tools found")
        return
    
    # Mock tool context
    class MockToolContext:
        pass
    
    tool_context = MockToolContext()
    
    try:
        # Test write_file tool
        write_tool = toolset.tools[1]  # AgentOsWriteTool
        test_content = "# Agent OS Agent Test File\nprint('Hello from Agent OS Agent!')\n"
        
        result = await write_tool.run_async(
            args={
                "file_path": "./test_agent_output.py",
                "content": test_content,
                "overwrite": False
            },
            tool_context=tool_context
        )
        
        if result.get("success"):
            print("   ✓ write_file tool works")
            
            # Test read_file tool
            read_tool = toolset.tools[0]  # AgentOsReadTool
            result = await read_tool.run_async(
                args={"file_path": "./test_agent_output.py"},
                tool_context=tool_context
            )
            
            if "content" in result:
                print("   ✓ read_file tool works")
            
            # Test grep_search tool
            grep_tool = toolset.tools[2]  # AgentOsGrepTool
            result = await grep_tool.run_async(
                args={
                    "pattern": "Agent OS",
                    "file_path": "./test_agent_output.py",
                    "case_sensitive": False
                },
                tool_context=tool_context
            )
            
            if "matches" in result:
                print("   ✓ grep_search tool works")
            
            # Test bash_command tool
            bash_tool = toolset.tools[4]  # AgentOsBashTool
            result = await bash_tool.run_async(
                args={
                    "command": "python ./test_agent_output.py",
                    "working_directory": "."
                },
                tool_context=tool_context
            )
            
            if result.get("return_code") == 0:
                print("   ✓ bash_command tool works")
                print(f"   ✓ Script output: {result.get('stdout', '').strip()}")
            
            # Clean up
            try:
                os.remove("./test_agent_output.py")
                print("   ✓ Cleaned up test file")
            except:
                pass
        else:
            print(f"   ❌ write_file tool failed: {result.get('error')}")
            
    except Exception as e:
        print(f"   ❌ Tool test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
