#!/usr/bin/env python3
"""
Debug version of the MCP Development Workflow Demo
"""

import asyncio
import os
import sys
import traceback

# Import our MCP multi-agent system
from agent import agent as root_agent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


async def debug_mcp_development_workflow():
    """Debug the MCP-enhanced development workflow with more detailed error reporting."""

    print("🔧 MCP Multi-Agent Development Workflow Debug Demo")
    print("=" * 60)

    # Set up ADK services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()

    # Create runner
    runner = Runner(
        app_name="mcp_dev_demo",
        agent=root_agent,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service,
    )

    # Simple test scenario
    test_scenario = {
        "title": "📋 Simple Calculator with MCP",
        "spec": """
Create a simple Python calculator that can add and subtract two numbers.
""",
        "description": "Simple calculator for debugging.",
    }

    print(f"🎯 Running: {test_scenario['title']}")
    print("=" * 70)
    print("🔄 Processing with MCP-enhanced multi-agent system...")

    try:
        # Create session
        print("Creating session...")
        session = await session_service.create_session(
            app_name="mcp_dev_demo", user_id="demo_user"
        )
        print(f"Session created with ID: {session.id}")

        # Run the specification through MCP-enhanced workflow
        print("Starting workflow execution...")
        response_parts = []
        content = types.Content(
            role="user", parts=[types.Part(text=test_scenario["spec"])]
        )

        async for response in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=content,
        ):
            print(f"Received response: {response}")
            if hasattr(response, "content") and response.content:
                for part in response.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_parts.append(part.text)
                        print(f"📍 Progress: {part.text[:100]}...")

        print(f"✅ MCP development workflow completed!")
        print(f"📄 Full response:")
        print("=" * 70)
        for part in response_parts:
            print(part)
            print("-" * 50)

    except Exception as e:
        print(f"❌ Error during MCP workflow: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print("Traceback:")
        traceback.print_exc()
        print(
            "Note: This demo requires proper ADK setup with API keys and MCP servers."
        )


if __name__ == "__main__":
    print("MCP Multi-Agent Development Workflow Debug Demo")
    print("=" * 45)
    print("Running debug version to identify timeout issues...")

    try:
        asyncio.run(debug_mcp_development_workflow())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        traceback.print_exc()
        print("Make sure you have ADK properly installed and MCP servers configured.")
