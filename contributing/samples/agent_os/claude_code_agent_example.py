#!/usr/bin/env python3
"""Example of using Agent OS Agent with Agent OS integration."""

import asyncio
import os
from pathlib import Path

from google.adk.agents import AgentOsAgent
from google.adk.runners import Runner


async def main():
    """Example usage of Agent OS Agent with Agent OS integration."""
    
    # Set up paths
    agent_os_path = "/home/hfeng1/agent-os"
    project_path = "."
    
    # Create Agent OS Agent with Agent OS configuration
    agent_os_agent = AgentOsAgent.create_with_agent_os_config(
        agent_os_path=agent_os_path,
        project_path=project_path,
        name="agent_os_agent",
        model="gemini-2.0-flash",
    )
    
    # Add Agent OS subagents
    agent_os_agent.add_agent_os_subagents(agent_os_path)
    
    # Create a runner
    runner = Runner()
    
    # Example conversation
    print("🤖 Agent OS Agent with Agent OS Integration")
    print("=" * 50)
    
    # Example 1: Plan a new product
    print("\n📋 Example 1: Planning a new product")
    print("-" * 30)
    
    response = await runner.run_async(
        agent=agent_os_agent,
        user_input="I want to plan a new task management application. Can you help me create the product documentation using Agent OS workflows?"
    )
    
    print("Response:", response)
    
    # Example 2: Create a spec
    print("\n📝 Example 2: Creating a specification")
    print("-" * 30)
    
    response = await runner.run_async(
        agent=agent_os_agent,
        user_input="Create a spec for user authentication feature with the following requirements: email/password login, password reset, and user registration."
    )
    
    print("Response:", response)
    
    # Example 3: File operations
    print("\n📁 Example 3: File operations")
    print("-" * 30)
    
    response = await runner.run_async(
        agent=agent_os_agent,
        user_input="Create a simple Python file called hello.py with a hello world function and run it to test."
    )
    
    print("Response:", response)


if __name__ == "__main__":
    asyncio.run(main())
