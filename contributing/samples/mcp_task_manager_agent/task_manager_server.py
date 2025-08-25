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

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Create an MCP server for task management
mcp = FastMCP("Task Manager Server", host="localhost", port=3001)

# In-memory task storage (in a real implementation, you'd use a database)
tasks: Dict[str, Dict] = {}
task_counter = 1


@mcp.tool(description="Create a new task")
def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: Optional[str] = None
) -> str:
    """Create a new task with title, description, priority, and optional due date.
    
    Args:
        title: The task title
        description: Optional task description
        priority: Task priority (low, medium, high)
        due_date: Optional due date in YYYY-MM-DD format
    
    Returns:
        Task ID of the created task
    """
    global task_counter
    
    if priority not in ["low", "medium", "high"]:
        return "Error: Priority must be 'low', 'medium', or 'high'"
    
    task_id = f"task_{task_counter}"
    task_counter += 1
    
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "due_date": due_date,
        "completed_at": None
    }
    
    tasks[task_id] = task
    return f"Created task '{title}' with ID: {task_id}"


@mcp.tool(description="List all tasks")
def list_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> str:
    """List all tasks, optionally filtered by status or priority.
    
    Args:
        status: Optional status filter (pending, completed, in_progress)
        priority: Optional priority filter (low, medium, high)
    
    Returns:
        Formatted list of tasks
    """
    if not tasks:
        return "No tasks found."
    
    filtered_tasks = list(tasks.values())
    
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]
    
    if priority:
        filtered_tasks = [t for t in filtered_tasks if t["priority"] == priority]
    
    if not filtered_tasks:
        return f"No tasks found with the specified filters (status: {status}, priority: {priority})."
    
    # Sort by priority and creation date
    priority_order = {"high": 3, "medium": 2, "low": 1}
    filtered_tasks.sort(
        key=lambda x: (priority_order.get(x["priority"], 0), x["created_at"]),
        reverse=True
    )
    
    result = "Tasks:\n"
    for task in filtered_tasks:
        due_info = f" (Due: {task['due_date']})" if task['due_date'] else ""
        result += f"- [{task['id']}] {task['title']} - {task['status']} ({task['priority']} priority){due_info}\n"
        if task['description']:
            result += f"  Description: {task['description']}\n"
    
    return result


@mcp.tool(description="Get details of a specific task")
def get_task(task_id: str) -> str:
    """Get detailed information about a specific task.
    
    Args:
        task_id: The ID of the task to retrieve
    
    Returns:
        Detailed task information
    """
    if task_id not in tasks:
        return f"Task '{task_id}' not found."
    
    task = tasks[task_id]
    result = f"Task Details for {task_id}:\n"
    result += f"Title: {task['title']}\n"
    result += f"Description: {task['description']}\n"
    result += f"Status: {task['status']}\n"
    result += f"Priority: {task['priority']}\n"
    result += f"Created: {task['created_at']}\n"
    
    if task['due_date']:
        result += f"Due Date: {task['due_date']}\n"
    
    if task['completed_at']:
        result += f"Completed: {task['completed_at']}\n"
    
    return result


@mcp.tool(description="Update task status")
def update_task_status(task_id: str, status: str) -> str:
    """Update the status of a task.
    
    Args:
        task_id: The ID of the task to update
        status: New status (pending, in_progress, completed)
    
    Returns:
        Confirmation message
    """
    if task_id not in tasks:
        return f"Task '{task_id}' not found."
    
    if status not in ["pending", "in_progress", "completed"]:
        return "Error: Status must be 'pending', 'in_progress', or 'completed'"
    
    tasks[task_id]["status"] = status
    
    if status == "completed":
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
    else:
        tasks[task_id]["completed_at"] = None
    
    return f"Updated task '{task_id}' status to '{status}'"


@mcp.tool(description="Update task priority")
def update_task_priority(task_id: str, priority: str) -> str:
    """Update the priority of a task.
    
    Args:
        task_id: The ID of the task to update
        priority: New priority (low, medium, high)
    
    Returns:
        Confirmation message
    """
    if task_id not in tasks:
        return f"Task '{task_id}' not found."
    
    if priority not in ["low", "medium", "high"]:
        return "Error: Priority must be 'low', 'medium', or 'high'"
    
    tasks[task_id]["priority"] = priority
    return f"Updated task '{task_id}' priority to '{priority}'"


@mcp.tool(description="Delete a task")
def delete_task(task_id: str) -> str:
    """Delete a task.
    
    Args:
        task_id: The ID of the task to delete
    
    Returns:
        Confirmation message
    """
    if task_id not in tasks:
        return f"Task '{task_id}' not found."
    
    task_title = tasks[task_id]["title"]
    del tasks[task_id]
    return f"Deleted task '{task_title}' (ID: {task_id})"


@mcp.tool(description="Get tasks due soon")
def get_tasks_due_soon(days: int = 7) -> str:
    """Get tasks that are due within the specified number of days.
    
    Args:
        days: Number of days to look ahead (default: 7)
    
    Returns:
        List of tasks due soon
    """
    if not tasks:
        return "No tasks found."
    
    today = datetime.now().date()
    cutoff_date = today + timedelta(days=days)
    
    due_soon = []
    for task in tasks.values():
        if task['due_date'] and task['status'] != 'completed':
            try:
                due_date = datetime.fromisoformat(task['due_date']).date()
                if today <= due_date <= cutoff_date:
                    due_soon.append(task)
            except ValueError:
                continue  # Skip tasks with invalid date format
    
    if not due_soon:
        return f"No tasks due within the next {days} days."
    
    # Sort by due date
    due_soon.sort(key=lambda x: x['due_date'])
    
    result = f"Tasks due within the next {days} days:\n"
    for task in due_soon:
        days_until_due = (datetime.fromisoformat(task['due_date']).date() - today).days
        urgency = "TODAY" if days_until_due == 0 else f"in {days_until_due} days"
        result += f"- [{task['id']}] {task['title']} - Due {urgency} ({task['priority']} priority)\n"
    
    return result


@mcp.tool(description="Get task statistics")
def get_task_stats() -> str:
    """Get statistics about all tasks.
    
    Returns:
        Task statistics summary
    """
    if not tasks:
        return "No tasks found."
    
    total = len(tasks)
    by_status = {"pending": 0, "in_progress": 0, "completed": 0}
    by_priority = {"low": 0, "medium": 0, "high": 0}
    
    for task in tasks.values():
        by_status[task["status"]] = by_status.get(task["status"], 0) + 1
        by_priority[task["priority"]] = by_priority.get(task["priority"], 0) + 1
    
    result = f"Task Statistics:\n"
    result += f"Total Tasks: {total}\n\n"
    result += f"By Status:\n"
    result += f"  - Pending: {by_status['pending']}\n"
    result += f"  - In Progress: {by_status['in_progress']}\n"
    result += f"  - Completed: {by_status['completed']}\n\n"
    result += f"By Priority:\n"
    result += f"  - High: {by_priority['high']}\n"
    result += f"  - Medium: {by_priority['medium']}\n"
    result += f"  - Low: {by_priority['low']}\n"
    
    completion_rate = (by_status['completed'] / total * 100) if total > 0 else 0
    result += f"\nCompletion Rate: {completion_rate:.1f}%"
    
    return result


# Main entry point with graceful shutdown handling
if __name__ == "__main__":
    try:
        print("Starting Task Manager MCP Server on http://localhost:3001...")
        print("Available tools: create_task, list_tasks, get_task, update_task_status,")
        print("                update_task_priority, delete_task, get_tasks_due_soon, get_task_stats")
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
        print("Server has been shut down.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        print("Thank you for using the Task Manager MCP Server!")