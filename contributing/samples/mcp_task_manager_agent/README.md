# Task Manager MCP Agent

This example demonstrates how to create a comprehensive MCP (Model Context Protocol) server and agent for task management. The example includes a custom MCP server that provides task management functionality and an agent that uses these tools to help users organize their work.

## Features

### MCP Server (`task_manager_server.py`)
The custom MCP server provides the following tools:

- **create_task**: Create new tasks with title, description, priority, and due date
- **list_tasks**: List all tasks with optional filtering by status or priority
- **get_task**: Get detailed information about a specific task
- **update_task_status**: Update task status (pending, in_progress, completed)
- **update_task_priority**: Update task priority (low, medium, high)
- **delete_task**: Delete tasks that are no longer needed
- **get_tasks_due_soon**: Find tasks due within a specified number of days
- **get_task_stats**: Get statistics about task completion and distribution

### Agent (`agent.py`)
The agent acts as a helpful task management assistant that:

- Helps users create well-structured tasks
- Provides organized views of task lists
- Reminds users about upcoming deadlines
- Tracks progress and provides completion statistics
- Suggests task management best practices

## Setup and Usage

### Prerequisites
Make sure you have the required dependencies installed:
```bash
pip install mcp fastmcp
```

### Running the Example

1. **Start the MCP Server**
   ```bash
   cd contributing/samples/mcp_task_manager_agent
   python task_manager_server.py
   ```
   
   The server will start on `http://localhost:3001` and display available tools.

2. **Run the Agent**
   In a separate terminal:
   ```bash
   cd contributing/samples/mcp_task_manager_agent
   adk agent run agent.py
   ```

### Example Interactions

Here are some example conversations you can have with the task management agent:

**Creating Tasks:**
- "Create a task to review the quarterly report with high priority, due next Friday"
- "Add a task called 'Team meeting preparation' with medium priority"

**Managing Tasks:**
- "Show me all my high priority tasks"
- "List all pending tasks"
- "Mark task_1 as completed"
- "What tasks are due this week?"

**Getting Insights:**
- "Show me my task statistics"
- "What tasks are due soon?"
- "Give me an overview of all my tasks"

## Key MCP Concepts Demonstrated

### 1. Custom MCP Server
This example shows how to create a custom MCP server using FastMCP with:
- Multiple tool definitions with proper type hints
- Error handling and validation
- In-memory data storage (easily extensible to databases)
- Graceful shutdown handling

### 2. Tool Design Patterns
- **CRUD Operations**: Create, Read, Update, Delete for tasks
- **Filtering and Search**: List tasks with various filters
- **Analytics**: Statistics and reporting functionality
- **Time-based Queries**: Finding tasks due within timeframes

### 3. Agent Integration
- Using `MCPToolset` to connect to the custom server
- Tool filtering to expose only relevant functionality
- Comprehensive instructions for natural task management conversations

### 4. Data Modeling
The task data structure includes:
```python
{
    "id": "task_1",
    "title": "Task title",
    "description": "Task description", 
    "priority": "high|medium|low",
    "status": "pending|in_progress|completed",
    "created_at": "2025-01-XX...",
    "due_date": "2025-01-XX",
    "completed_at": "2025-01-XX..."
}
```

## Extending the Example

This example can be extended in many ways:

### Server Enhancements
- Add persistent storage (SQLite, PostgreSQL, etc.)
- Implement task categories/tags
- Add task dependencies and subtasks
- Include file attachments
- Add user authentication and multi-user support
- Implement task templates

### Agent Improvements
- Add natural language date parsing
- Implement smart task suggestions
- Add integration with calendar systems
- Include productivity analytics
- Add task import/export functionality

### Additional Tools
- Task search with full-text search
- Bulk operations (bulk update, bulk delete)
- Task templates and recurring tasks
- Time tracking integration
- Notification and reminder systems

## Architecture Notes

### MCP Server Design
- Uses FastMCP for easy HTTP-based MCP server creation
- Implements proper error handling and validation
- Uses SSE (Server-Sent Events) transport for real-time communication
- Maintains clean separation between tool logic and data storage

### Agent Design
- Uses `SseConnectionParams` for connecting to the MCP server
- Implements comprehensive instructions for natural conversations
- Uses tool filtering to expose only relevant functionality
- Designed for conversational task management workflows

This example demonstrates the power and flexibility of MCP for creating domain-specific tools and agents that can work together seamlessly.