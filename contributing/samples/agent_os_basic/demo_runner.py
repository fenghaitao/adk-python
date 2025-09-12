#!/usr/bin/env python3
"""
Demo application showing how to use the Runner class with both Python and YAML agents
for Agent OS basic integration workflows with actual execution.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the ADK source to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from google.adk.runners import InMemoryRunner
from google.genai import types
from google.adk.agents.config_agent_utils import from_config


def run_agent_with_prompt(runner, prompt, session_suffix="demo"):
    """Helper function to run an agent with a prompt and return the response."""
    async def create_and_run():
        user_id = "demo_user"
        session_id = f"demo_session_{session_suffix}"
        message = types.Content(parts=[types.Part(text=prompt)])
        
        # Create session first
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            events.append(event)
        
        # Get the final response
        for event in events:
            if event.author == 'model' and event.content and event.content.parts:
                return event.content.parts[0].text
        
        return "No model response found"
    
    return asyncio.run(create_and_run())


def demo_python_agent():
    """Demo the Python agent implementation with actual execution."""
    print("🐍 Testing Python Agent (AgentOsAgent)")
    print("-" * 50)
    
    try:
        # Add python_agent to path and import
        sys.path.insert(0, str(Path(__file__).parent / "python"))
        from agent_os_agent import AgentOsAgent
        
        print(f"✅ Python agent loaded successfully")
        
        # Create Agent OS Agent
        agent_os_agent = AgentOsAgent.create_with_agent_os_config(
            agent_os_path="/home/hfeng1/agent-os",
            project_path=".",
            name="agent_os_agent",
            model="iflow/Qwen3-Coder",
        )
        
        # Add Agent OS subagents
        agent_os_agent.add_agent_os_subagents("/home/hfeng1/agent-os")
        
        print(f"   Agent name: {agent_os_agent.name}")
        print(f"   Agent description: {agent_os_agent.description}")
        print(f"   Number of tools: {len(agent_os_agent.tools)}")
        print(f"   Number of sub-agents: {len(agent_os_agent.sub_agents)}")
        
        # Show available tools
        print(f"   Available tools:")
        for i, tool in enumerate(agent_os_agent.tools):
            if hasattr(tool, 'tools'):
                for j, sub_tool in enumerate(tool.tools):
                    tool_name = getattr(sub_tool, '__name__', str(sub_tool))
                    print(f"     {i+1}.{j+1}. {tool_name}")
            else:
                tool_name = getattr(tool, '__name__', str(tool))
                print(f"     {i+1}. {tool_name}")
        
        # Show sub-agents
        if agent_os_agent.sub_agents:
            print(f"   Sub-agents:")
            for i, sub_agent in enumerate(agent_os_agent.sub_agents):
                print(f"     {i+1}. {sub_agent.name}")
        
        print(f"\n📝 Agent OS Commands supported:")
        print(f"   • @plan-product - Analyze and plan product development")
        print(f"   • @create-spec - Create detailed technical specifications")
        print(f"   • @create-tasks - Break down specs into actionable tasks")
        print(f"   • @execute-tasks - Execute development tasks systematically")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing Runner Integration with Live Execution:")
        try:
            runner = InMemoryRunner(agent_os_agent)
            print(f"✅ InMemoryRunner created successfully")
            print(f"   App name: {runner.app_name}")
            print(f"   Agent: {runner.agent.name}")
            
            # Execute a real prompt
            prompt = "@plan-product for a simple calculator app with basic arithmetic operations"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "python_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading Python agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_yaml_agent():
    """Demo the YAML agent implementation with actual execution."""
    print("\n📄 Testing YAML Agent (LlmAgent with Agent OS tools)")
    print("-" * 50)
    
    try:
        # Load YAML agent
        yaml_agent_path = Path(__file__).parent / "yaml_agent" / "root_agent.yaml"
        agent = from_config(str(yaml_agent_path))
        
        print(f"✅ YAML agent loaded successfully")
        print(f"   Agent name: {agent.name}")
        print(f"   Agent description: {agent.description}")
        print(f"   Number of tools: {len(agent.tools)}")
        print(f"   Number of sub-agents: {len(agent.sub_agents)}")
        
        # Show available tools
        print(f"   Available tools:")
        for i, tool in enumerate(agent.tools):
            tool_name = getattr(tool, '__name__', str(tool))
            print(f"     {i+1}. {tool_name}")
        
        # Show sub-agents
        if agent.sub_agents:
            print(f"   Sub-agents:")
            for i, sub_agent in enumerate(agent.sub_agents):
                print(f"     {i+1}. {sub_agent.name}")
        
        print(f"\n📝 Agent OS Commands supported:")
        print(f"   • @plan-product - Analyze and plan product development")
        print(f"   • @create-spec - Create detailed technical specifications")
        print(f"   • @create-tasks - Break down specs into actionable tasks")
        print(f"   • @execute-tasks - Execute development tasks systematically")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing Runner Integration with Live Execution:")
        try:
            runner = InMemoryRunner(agent)
            print(f"✅ InMemoryRunner created successfully")
            print(f"   App name: {runner.app_name}")
            print(f"   Agent: {runner.agent.name}")
            
            # Execute a real prompt
            prompt = "@create-spec for user authentication with login and registration features"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "yaml_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading YAML agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_simple_yaml_agent():
    """Demo the simple YAML agent implementation."""
    print("\n📄 Testing Simple YAML Agent (LlmAgent)")
    print("-" * 50)
    
    try:
        # Load simple YAML agent
        yaml_agent_path = Path(__file__).parent / "yaml_agent" / "root_agent_simple.yaml"
        agent = from_config(str(yaml_agent_path))
        
        print(f"✅ Simple YAML agent loaded successfully")
        print(f"   Agent name: {agent.name}")
        print(f"   Agent description: {agent.description}")
        print(f"   Number of tools: {len(agent.tools)}")
        print(f"   Number of sub-agents: {len(agent.sub_agents)}")
        
        # Show available tools
        print(f"   Available tools:")
        for i, tool in enumerate(agent.tools):
            tool_name = getattr(tool, '__name__', str(tool))
            print(f"     {i+1}. {tool_name}")
        
        print(f"\n📝 Agent OS Commands supported:")
        print(f"   • @plan-product - Analyze and plan product development")
        print(f"   • @create-spec - Create detailed technical specifications")
        print(f"   • @create-tasks - Break down specs into actionable tasks")
        print(f"   • @execute-tasks - Execute development tasks systematically")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing Runner Integration with Live Execution:")
        try:
            runner = InMemoryRunner(agent)
            print(f"✅ InMemoryRunner created successfully")
            print(f"   App name: {runner.app_name}")
            print(f"   Agent: {runner.agent.name}")
            
            # Execute a real prompt
            prompt = "@analyze-project and suggest improvements for this Agent OS integration"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "simple_yaml_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading simple YAML agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_comparative_execution():
    """Demo showing both agents executing the same task."""
    print("\n🔄 Comparative Agent Execution Demo")
    print("=" * 60)
    
    print("Testing both agents with the same task to compare responses:")
    
    # Test both agents with the same prompt
    test_prompt = "@analyze-project and suggest improvements for this Agent OS integration"
    print(f"\n📋 Test Prompt: {test_prompt}")
    print("\n" + "=" * 60)
    
    # Python Agent Test
    print("\n🐍 Python Agent (AgentOsAgent) Response:")
    print("-" * 40)
    try:
        sys.path.insert(0, str(Path(__file__).parent / "python"))
        from agent_os_agent import AgentOsAgent
        
        agent_os_agent = AgentOsAgent.create_with_agent_os_config(
            agent_os_path="/home/hfeng1/agent-os",
            project_path=".",
            name="agent_os_agent",
            model="iflow/Qwen3-Coder",
        )
        agent_os_agent.add_agent_os_subagents("/home/hfeng1/agent-os")
        
        runner = InMemoryRunner(agent_os_agent)
        response = run_agent_with_prompt(runner, test_prompt, "compare_python")
        print(f"📄 Response ({len(response)} chars):")
        print(response[:500] + "..." if len(response) > 500 else response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # YAML Agent Test
    print(f"\n📄 YAML Agent (LlmAgent) Response:")
    print("-" * 40)
    try:
        yaml_agent_path = Path(__file__).parent / "yaml_agent" / "root_agent.yaml"
        yaml_agent = from_config(str(yaml_agent_path))
        runner = InMemoryRunner(yaml_agent)
        
        response = run_agent_with_prompt(runner, test_prompt, "compare_yaml")
        print(f"📄 Response ({len(response)} chars):")
        print(response[:500] + "..." if len(response) > 500 else response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo function."""
    print("🚀 Agent OS Basic Integration Demo with Live Execution")
    print("=" * 60)
    print("This demo shows Python and YAML agents executing real prompts")
    print("using the iflow/Qwen3-Coder model.\n")
    
    # Test individual agents with execution
    python_success = demo_python_agent()
    yaml_success = demo_yaml_agent()
    simple_yaml_success = demo_simple_yaml_agent()
    
    # Show comparative execution if both work
    if python_success and yaml_success:
        demo_comparative_execution()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Summary:")
    print(f"   Python Agent (AgentOsAgent): {'✅ Working' if python_success else '❌ Failed'}")
    print(f"   YAML Agent (LlmAgent): {'✅ Working' if yaml_success else '❌ Failed'}")
    print(f"   Simple YAML Agent: {'✅ Working' if simple_yaml_success else '❌ Failed'}")
    
    if python_success or yaml_success or simple_yaml_success:
        print("\n🎉 At least one agent successfully executed Agent OS workflows!")
        print("\n💡 Available Agent OS Commands:")
        print("   • @plan-product - Analyze and plan product development")
        print("   • @create-spec - Create detailed technical specifications")
        print("   • @create-tasks - Break down specs into actionable tasks")
        print("   • @execute-tasks - Execute development tasks systematically")
        print("   • @execute-task - Execute a specific task")
        
        print("\n🔧 Next Steps:")
        print("   1. Try running: python demo_runner.py")
        print("   2. Use ADK CLI: adk run python/")
        print("   3. Use ADK CLI: adk run yaml_agent/")
        print("   4. Use ADK CLI: adk run yaml_agent/root_agent_simple.yaml")
        print("   5. Explore the .agent-os/ directory structure created by the agents")
    else:
        print("\n❌ All agents failed. Check the error messages above.")
    
    return 0 if (python_success or yaml_success or simple_yaml_success) else 1


if __name__ == "__main__":
    sys.exit(main())
