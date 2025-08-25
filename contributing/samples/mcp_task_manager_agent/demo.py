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

"""
Demo script for the Task Manager MCP Agent.

This script demonstrates how to interact with the task manager agent programmatically.
Make sure to start the MCP server first by running:
    python task_manager_server.py
"""

import asyncio
from agent import root_agent


async def demo_task_management():
    """Demonstrate various task management capabilities."""
    
    print("🚀 Task Manager Agent Demo")
    print("=" * 50)
    
    # Demo conversations
    conversations = [
        "Create a task called 'Prepare presentation' with high priority, due in 3 days",
        "Add a task to 'Review code changes' with medium priority",
        "Create a low priority task 'Organize desk' with description 'Clean and organize workspace'",
        "Show me all my tasks",
        "What are my high priority tasks?",
        "Mark the presentation task as in progress",
        "Show me tasks due soon",
        "Give me my task statistics",
        "Update the code review task to high priority",
        "Mark the desk organization task as completed",
        "Show me all my tasks again"
    ]
    
    for i, user_input in enumerate(conversations, 1):
        print(f"\n📝 Step {i}: {user_input}")
        print("-" * 40)
        
        try:
            response = await root_agent.run_async(user_input)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between requests for readability
        await asyncio.sleep(1)
    
    print("\n✅ Demo completed!")
    print("\nTry running the agent interactively with:")
    print("    adk agent run agent.py")


if __name__ == "__main__":
    print("Make sure the MCP server is running first:")
    print("    python task_manager_server.py")
    print("\nStarting demo in 3 seconds...")
    
    import time
    time.sleep(3)
    
    asyncio.run(demo_task_management())