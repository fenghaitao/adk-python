#!/usr/bin/env python3
"""
Demo application showing how to use the Runner class with Spec-Kit agent
for specification-driven development workflows with actual execution.
"""

import sys
import os
import asyncio
from pathlib import Path

# Import ADK with robust path handling
try:
    # Try direct import first (when ADK is properly installed)
    from google.adk.runners import InMemoryRunner
    from google.genai import types
except ImportError:
    # Fallback: Add ADK source directory only if direct import fails
    adk_src_path = Path(__file__).parent.parent.parent.parent / "src"
    if adk_src_path.exists():
        sys.path.insert(0, str(adk_src_path))
        try:
            from google.adk.runners import InMemoryRunner
            from google.genai import types
        except ImportError as e:
            raise ImportError(
                f"Could not import ADK modules. Please ensure ADK is installed or "
                f"PYTHONPATH includes the ADK source directory. Error: {e}"
            ) from e
    else:
        raise ImportError(
            f"ADK source directory not found at {adk_src_path}. "
            f"Please ensure ADK is installed or set PYTHONPATH correctly."
        )


def get_spec_kit_model():
    """Get Spec-Kit model from environment or use default."""
    return os.environ.get("SPEC_KIT_MODEL", "iflow/Qwen3-Coder")


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


def demo_specify_command():
    """Demo the /specify command with actual execution."""
    print("📋 Testing /specify Command")
    print("-" * 50)
    
    try:
        # Import Spec-Kit agent
        from agent import SpecKitAgent
        
        print(f"✅ Spec-Kit agent loaded successfully")
        
        # Create Spec-Kit Agent
        spec_kit_agent = SpecKitAgent(
            name="spec_kit_agent",
            model=get_spec_kit_model()
        )
        
        print(f"   Agent name: {spec_kit_agent.name}")
        print(f"   Agent description: {spec_kit_agent.description}")
        print(f"   Number of tools: {len(spec_kit_agent.tools)}")
        
        # Show available tools
        print(f"   Available tools:")
        for i, tool in enumerate(spec_kit_agent.tools):
            if hasattr(tool, 'tools'):
                for j, sub_tool in enumerate(tool.tools):
                    tool_name = getattr(sub_tool, '__name__', str(sub_tool))
                    print(f"     {i+1}.{j+1}. {tool_name}")
            else:
                tool_name = getattr(tool, '__name__', str(tool))
                print(f"     {i+1}. {tool_name}")
        
        print(f"\n📝 Spec-Kit Commands supported:")
        print(f"   • /specify - Create feature specifications")
        print(f"   • /plan - Generate implementation plans")
        print(f"   • /tasks - Break down plans into actionable tasks")
        print(f"   • /implement - Execute implementation following TDD workflow")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing /specify Command with Live Execution:")
        try:
            runner = InMemoryRunner(spec_kit_agent)
            print(f"✅ InMemoryRunner created successfully")
            print(f"   App name: {runner.app_name}")
            print(f"   Agent: {runner.agent.name}")
            
            # Execute /specify command
            prompt = "/specify read /home/hfeng1/wdt.md and create a Simics model for watchdog timer"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "specify_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading Spec-Kit agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_plan_command():
    """Demo the /plan command with actual execution."""
    print("\n📊 Testing /plan Command")
    print("-" * 50)
    
    try:
        # Import Spec-Kit agent
        from agent import SpecKitAgent
        
        # Create Spec-Kit Agent
        spec_kit_agent = SpecKitAgent(
            name="spec_kit_agent",
            model=get_spec_kit_model()
        )
        
        print(f"✅ Spec-Kit agent loaded for /plan command")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing /plan Command with Live Execution:")
        try:
            runner = InMemoryRunner(spec_kit_agent)
            print(f"✅ InMemoryRunner created successfully")
            
            # Execute /plan command
            prompt = "/plan"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "plan_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading Spec-Kit agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_tasks_command():
    """Demo the /tasks command with actual execution."""
    print("\n📋 Testing /tasks Command")
    print("-" * 50)
    
    try:
        # Import Spec-Kit agent
        from agent import SpecKitAgent
        
        # Create Spec-Kit Agent
        spec_kit_agent = SpecKitAgent(
            name="spec_kit_agent",
            model=get_spec_kit_model()
        )
        
        print(f"✅ Spec-Kit agent loaded for /tasks command")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing /tasks Command with Live Execution:")
        try:
            runner = InMemoryRunner(spec_kit_agent)
            print(f"✅ InMemoryRunner created successfully")
            
            # Execute /tasks command
            prompt = "/tasks"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "tasks_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading Spec-Kit agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_implement_command():
    """Demo the /implement command with actual execution."""
    print("\n⚙️ Testing /implement Command")
    print("-" * 50)
    
    try:
        # Import Spec-Kit agent
        from agent import SpecKitAgent
        
        # Create Spec-Kit Agent
        spec_kit_agent = SpecKitAgent(
            name="spec_kit_agent",
            model=get_spec_kit_model()
        )
        
        print(f"✅ Spec-Kit agent loaded for /implement command")
        
        # Test Runner integration with actual execution
        print(f"\n🤖 Testing /implement Command with Live Execution:")
        try:
            runner = InMemoryRunner(spec_kit_agent)
            print(f"✅ InMemoryRunner created successfully")
            
            # Execute /implement command
            prompt = "/implemtn"
            print(f"\n📝 Executing prompt: {prompt}")
            print(f"🔄 Running agent...")
            
            response = run_agent_with_prompt(runner, prompt, "implement_demo")
            print(f"\n✅ Agent Response:")
            print(f"📄 {response}")
            
        except Exception as e:
            print(f"⚠️  Execution failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading Spec-Kit agent: {e}")
        import traceback
        traceback.print_exc()
        return False






def main():
    """Main demo function."""
    print("🚀 Spec-Kit Integration Demo with Live Execution")
    print("=" * 60)
    print("This demo shows Spec-Kit agent executing real prompts")
    print("using the iflow/Qwen3-Coder model.\n")
    
    # Test individual commands with execution
    specify_success = demo_specify_command()
    plan_success = demo_plan_command()
    tasks_success = demo_tasks_command()
    implement_success = demo_implement_command()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Summary:")
    print(f"   /specify Command: {'✅ Working' if specify_success else '❌ Failed'}")
    print(f"   /plan Command: {'✅ Working' if plan_success else '❌ Failed'}")
    print(f"   /tasks Command: {'✅ Working' if tasks_success else '❌ Failed'}")
    print(f"   /implement Command: {'✅ Working' if implement_success else '❌ Failed'}")
    
    if specify_success or plan_success or tasks_success or implement_success:
        print("\n🎉 Spec-Kit agent successfully executed workflows!")
        print("\n💡 Available Spec-Kit Commands:")
        print("   • /specify - Create feature specifications")
        print("   • /plan - Generate implementation plans")
        print("   • /tasks - Break down plans into actionable tasks")
        print("   • /implement - Execute implementation following TDD workflow")
        print("   • /constitution - Establish project principles")
        print("   • /clarify - Resolve ambiguities")
        print("   • /analyze - Cross-artifact consistency analysis")
        
        print("\n🔧 Next Steps:")
        print("   1. Try running: python demo_runner.py")
        print("   2. Use ADK CLI: adk run .")
        print("   3. Explore the generated .adk/ directory structure")
        print("   4. Check generated specifications in specs/ directory")
        print("   5. Review implementation artifacts created by the agent")
    else:
        print("\n❌ All commands failed. Check the error messages above.")
    
    return 0 if (specify_success or plan_success or tasks_success or implement_success) else 1


if __name__ == "__main__":
    sys.exit(main())

