#!/usr/bin/env python3
"""Example of using Agent OS Agent with Agent OS integration."""

import asyncio
import os
from pathlib import Path

import sys

# Import agent with relative path handling
try:
    # Try importing from the parent directory structure
    sys.path.insert(0, str(Path(__file__).parent.parent / "python"))
    from agent_os_agent import AgentOsAgent
except ImportError as e:
    raise ImportError(
        f"Could not import AgentOsAgent. Please ensure you're running from the correct directory "
        f"or set PYTHONPATH to include the python directory. Error: {e}"
    ) from e
from google.adk.runners import InMemoryRunner
from google.genai import types


def get_agent_os_path():
    """Get Agent OS path from environment or use default."""
    # Default to .agent-os directory (users install agent-os here)
    default_path = ".agent-os"
    return os.environ.get("AGENT_OS_PATH", default_path)


def get_agent_os_model():
    """Get Agent OS model from environment or use default."""
    return os.environ.get("AGENT_OS_MODEL", "iflow/Qwen3-Coder")


async def main():
    """Example usage of Agent OS Agent with Agent OS integration."""
    
    # Set up paths
    agent_os_path = get_agent_os_path()
    project_path = "."
    
    # Create Agent OS Agent with Agent OS configuration
    agent_os_agent = AgentOsAgent.create_with_agent_os_config(
        agent_os_path=agent_os_path,
        project_path=project_path,
        name="agent_os_agent",
        model=get_agent_os_model(),
    )
    
    # Add Agent OS subagents
    agent_os_agent.add_agent_os_subagents(agent_os_path)
    
    # Create a runner
    runner = InMemoryRunner(agent_os_agent)
    
    # Example conversation
    print("🤖 Agent OS Agent with Agent OS Integration")
    print("=" * 50)
    
    # Create sessions for each example
    session1 = await runner.session_service.create_session(
        app_name="InMemoryRunner",
        user_id="user1",
        session_id="session1"
    )
    session2 = await runner.session_service.create_session(
        app_name="InMemoryRunner",
        user_id="user1",
        session_id="session2"
    )
    session3 = await runner.session_service.create_session(
        app_name="InMemoryRunner",
        user_id="user1",
        session_id="session3"
    )
    
    # Example 1: Plan a new product
    print("\n📋 Example 1: Planning a new product")
    print("-" * 30)
    
    print("Processing request...")
    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=types.Content(parts=[types.Part(text="I want to plan a new task management application. Can you help me create the product documentation using Agent OS workflows?")])
    ):
        print(f"Event: {event}")
    
    # Example 2: Create a spec
    print("\n📝 Example 2: Creating a specification")
    print("-" * 30)
    
    print("Processing request...")
    async for event in runner.run_async(
        user_id="user1",
        session_id="session2",
        new_message=types.Content(parts=[types.Part(text="Create a spec for user authentication feature with the following requirements: email/password login, password reset, and user registration.")])
    ):
        print(f"Event: {event}")
    
    # Example 3: File operations
    print("\n📁 Example 3: File operations")
    print("-" * 30)
    
    print("Processing request...")
    async for event in runner.run_async(
        user_id="user1",
        session_id="session3",
        new_message=types.Content(parts=[types.Part(text="Create a simple Python file called hello.py with a hello world function and run it to test.")])
    ):
        print(f"Event: {event}")


if __name__ == "__main__":
    asyncio.run(main())
