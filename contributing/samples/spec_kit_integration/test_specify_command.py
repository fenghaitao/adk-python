#!/usr/bin/env python3
"""Test script to verify the /specify command works correctly with ADK agent."""

import asyncio
import os
import sys
from pathlib import Path

# Import the agent
from agent import root_agent

async def test_specify_command():
    """Test the /specify command with a simple feature description."""
    
    # Set working directory to the project root
    os.chdir(Path(__file__).parent)
    
    # Test the /specify command
    test_message = "/specify Create a simple user profile management system that allows users to view and edit their basic information"
    
    print("Testing /specify command with ADK agent...")
    print(f"Message: {test_message}")
    print("=" * 80)
    
    try:
        # Send the message to the agent
        response = await root_agent.send_message(test_message)
        
        print("Agent Response:")
        print(response)
        print("=" * 80)
        
        # Check if the response contains expected elements
        if "read_file" in str(response).lower():
            print("✅ Agent attempted to read command file")
        else:
            print("❌ Agent did not attempt to read command file")
            
        if "bash_command" in str(response).lower():
            print("✅ Agent attempted to run script")
        else:
            print("❌ Agent did not attempt to run script")
            
        if "spec" in str(response).lower():
            print("✅ Agent mentioned specifications")
        else:
            print("❌ Agent did not mention specifications")
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False
        
    return True

if __name__ == "__main__":
    asyncio.run(test_specify_command())