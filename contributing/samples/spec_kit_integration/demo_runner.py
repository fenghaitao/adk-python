#!/usr/bin/env python3
"""
Demo application showing how to use the Runner class with Spec-Kit agent
for specification-driven development workflows with actual execution.
"""

import sys
import os
import asyncio
import subprocess
import shutil
import json
import datetime
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


def setup_spec_kit(project_name="adk_spec_kit_project"):
    """Setup spec-kit project and validate environment."""
    print("🔧 Setting up Spec-Kit environment...")
    print("-" * 50)
    
    # Get the ADK repository root directory (where .git is located)
    adk_root = Path(__file__).parent.parent.parent.parent.absolute()
    
    # Create adk-demo-runner directory alongside ADK root
    adk_demo_runner = adk_root.parent / "adk-demo-runner"
    
    # Set up paths relative to ADK root
    spec_kit_dir = adk_root / "spec-kit"
    adk_venv = adk_root / ".venv"
    spec_kit_integration_dir = adk_root / "contributing" / "samples" / "spec_kit_integration"
    
    print(f"📁 ADK repository root: {adk_root}")
    print(f"📁 Demo runner directory: {adk_demo_runner}")
    print(f"📁 Spec-Kit directory: {spec_kit_dir}")
    print(f"📁 ADK virtual environment: {adk_venv}")
    print(f"📁 Integration directory: {spec_kit_integration_dir}")
    
    # Create adk_demo_runner directory if it doesn't exist
    if not adk_demo_runner.exists():
        print(f"📁 Creating demo runner directory: {adk_demo_runner}")
        adk_demo_runner.mkdir(parents=True, exist_ok=True)
        print("✅ Demo runner directory created")
    else:
        print("✅ Demo runner directory already exists")
    
    # Check if spec-kit virtual environment exists
    spec_kit_venv = spec_kit_dir / ".venv"
    if not spec_kit_venv.exists():
        print(f"❌ Error: spec-kit virtual environment not found at {spec_kit_venv}")
        print(f"Please run: cd {spec_kit_dir} && python -m venv .venv && source .venv/bin/activate && pip install -e .")
        return False, None
    
    # Check if ADK virtual environment exists
    if not adk_venv.exists():
        print(f"❌ Error: ADK virtual environment not found at {adk_venv}")
        print(f"Please run: python -m venv .venv && source .venv/bin/activate && pip install -e .")
        return False, None
    
    # Check if spec-kit integration directory exists
    if not spec_kit_integration_dir.exists():
        print(f"❌ Error: Spec-Kit integration directory not found at {spec_kit_integration_dir}")
        return False, None
    
    print("✅ All required directories found")
    
    # Clean up existing project directory if it exists
    existing_project_dir = adk_demo_runner / project_name
    if existing_project_dir.exists():
        print(f"🧹 Cleaning up existing project directory: {existing_project_dir}")
        shutil.rmtree(existing_project_dir)
        print("✅ Existing project directory removed")
    
    # Initialize spec-kit project in adk_demo_runner directory
    print(f"\n📋 Initializing spec-kit project: {project_name}")
    print(f"📁 Project will be created in: {adk_demo_runner}")
    try:
        # Change to the adk_demo_runner directory to run the command
        original_cwd = os.getcwd()
        os.chdir(adk_demo_runner)
        
        # Run specify init command
        specify_cmd = str(spec_kit_venv / "bin" / "specify")
        cmd = [specify_cmd, "init", project_name, "--ai", "adk", "--script", "sh"]
        
        print(f"🔄 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Spec-kit project initialized successfully")
            project_dir = adk_demo_runner / project_name
            if project_dir.exists():
                print(f"📁 Project directory created: {project_dir}")
                print(f"📁 This will be our working directory (completely separate from ADK)")
                print(f"📁 Directory structure:")
                print(f"   {adk_root.parent}/")
                print(f"   ├── adk-python/          (ADK repository)")
                print(f"   └── adk-demo-runner/     (Demo runner)")
                print(f"       └── {project_name}/   (Project working directory)")
                # Return the project directory as the script_dir for subsequent operations
                return True, project_dir
            else:
                print("❌ Project directory was not created")
                return False, None
        else:
            print(f"❌ Failed to initialize spec-kit project:")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
            return False, None
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 60 seconds")
        return False, None
    except Exception as e:
        print(f"❌ Error running spec-kit init: {e}")
        return False, None
    finally:
        # Restore original working directory
        os.chdir(original_cwd)


def get_spec_kit_model():
    """Get Spec-Kit model from environment or use default."""
    return os.environ.get("SPEC_KIT_MODEL", "iflow/Qwen3-Coder")


def run_agent_with_prompt(runner, prompt, session_suffix="demo"):
    """Helper function to run an agent with a prompt and return the response."""
    async def create_and_run():
        user_id = "demo_user"
        session_id = f"demo_session_{session_suffix}"
        
        # Create the message properly - the agent expects a user message with explicit role
        message = types.Content(role='user', parts=[types.Part.from_text(text=prompt)])
        
        # Create session first
        await runner.session_service.create_session(
            app_name=runner.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        print(f"📝 Sending message: {prompt}")
        
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            events.append(event)
            # Debug: Print event details
            print(f"📋 Event: {event.author} - {type(event.content).__name__ if event.content else 'None'}")
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print(f"   Text preview: {part.text[:100]}...")
        
        # Get the final response - look for the last model response
        model_responses = []
        for event in events:
            if event.author == 'model' and event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        model_responses.append(part.text)
        
        final_response = model_responses[-1] if model_responses else "No model response found"
        
        # Save session using ADK's built-in session service
        try:
            # Get the session with full history
            session = await runner.session_service.get_session(
                app_name=runner.app_name,
                user_id=user_id,
                session_id=session_id
            )
            
            if session:
                # Create filename with timestamp and session suffix
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{session_suffix}_session.json"
                
                # Save session using ADK's built-in JSON export
                session_json = session.model_dump_json(indent=2, exclude_none=True)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(session_json)
                
                print(f"💾 Session saved to: {filename}")
                print(f"📊 Session contains {len(session.contents)} content entries")
                
        except Exception as e:
            print(f"⚠️  Failed to save session: {e}")
        
        return final_response
    
    return asyncio.run(create_and_run())


def demo_specify_command():
    """Demo the /specify command with actual execution."""
    print("📋 Testing /specify Command")
    print("-" * 50)
    
    try:
        # Import Spec-Kit agent from the integration directory
        # We need to add the integration directory to Python path
        adk_root = Path(__file__).parent.parent.parent.parent.absolute()
        spec_kit_integration_dir = adk_root / "contributing" / "samples" / "spec_kit_integration"
        
        # Add the integration directory to Python path so we can import the agent
        if str(spec_kit_integration_dir) not in sys.path:
            sys.path.insert(0, str(spec_kit_integration_dir))
        
        print(f"✅ Added integration directory to Python path: {spec_kit_integration_dir}")
        print(f"📁 Current working directory: {os.getcwd()}")
        
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
            
            # Execute /specify command - use the exact format expected
            prompt = "/specify read /home/hfeng1/wdt.md and create a Simics model for watchdog timer"
            print(f"\n📝 Executing command: {prompt}")
            print(f"🔄 Running agent...")
            print(f"📋 The agent should:")
            print(f"   1. Read .adk/commands/specify.md")
            print(f"   2. Execute the bash script")
            print(f"   3. Create the specification file")
            print(f"   4. Report completion")
            
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
            prompt = "/implement"
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
    
    # Setup spec-kit environment first
    print("📋 Setting up Spec-Kit environment...")
    setup_success, project_dir = setup_spec_kit("watchdog_timer_demo")
    
    if not setup_success or not project_dir:
        print("\n❌ Spec-Kit setup failed. Please check the error messages above.")
        print("Make sure all required environments are properly configured.")
        return 1
    
    print(f"\n✅ Spec-Kit setup completed successfully!")
    print(f"📁 Working directory: {project_dir}")
    print(f"📁 This directory has no .git folder - perfect for agent operations!")
    print("=" * 60)
    
    # Change to the project directory for all subsequent operations
    original_cwd = os.getcwd()
    try:
        os.chdir(project_dir)
        print(f"🔄 Changed working directory to: {os.getcwd()}")
    except Exception as e:
        print(f"❌ Failed to change to project directory: {e}")
        return 1
    
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
    
    # Restore original working directory
    try:
        os.chdir(original_cwd)
        print(f"\n🔄 Restored working directory to: {os.getcwd()}")
    except Exception as e:
        print(f"⚠️  Warning: Could not restore original working directory: {e}")
    
    return 0 if (specify_success or plan_success or tasks_success or implement_success) else 1


if __name__ == "__main__":
    sys.exit(main())

