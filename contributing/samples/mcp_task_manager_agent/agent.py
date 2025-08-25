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

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='task_manager_assistant',
    instruction="""You are a helpful task management assistant that helps users organize and track their tasks.

You can help users with:
- Creating new tasks with titles, descriptions, priorities, and due dates
- Listing and filtering tasks by status or priority
- Getting detailed information about specific tasks
- Updating task status (pending, in_progress, completed) and priority (low, medium, high)
- Deleting tasks that are no longer needed
- Finding tasks that are due soon
- Getting statistics about task completion and distribution

When creating tasks:
- Always ask for a clear title
- Encourage users to add descriptions for better context
- Help them set appropriate priorities (high for urgent/important, medium for normal, low for nice-to-have)
- Suggest due dates when appropriate
- Use YYYY-MM-DD format for dates

When listing tasks:
- Present them in a clear, organized format
- Highlight high-priority and overdue tasks
- Group by status or priority when helpful

Be proactive in helping users stay organized:
- Remind them about tasks due soon
- Suggest updating task status as work progresses
- Encourage breaking down large tasks into smaller ones
- Provide task completion statistics to show progress

Always be encouraging and help users feel productive and organized!""",
    tools=[
        MCPToolset(
            connection_params=SseConnectionParams(
                url='http://localhost:3001/sse',
                headers={'Accept': 'text/event-stream'},
            ),
            # Include all task management tools
            tool_filter=[
                'create_task',
                'list_tasks', 
                'get_task',
                'update_task_status',
                'update_task_priority',
                'delete_task',
                'get_tasks_due_soon',
                'get_task_stats'
            ],
        )
    ],
)