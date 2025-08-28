"""
CLI for interacting with the Task Manager application.
"""
import sys
import argparse
from .task_manager import TaskManager

def main():
    # Initialize the TaskManager with the data file location
    task_manager = TaskManager(data_file="data/tasks.json")

    parser = argparse.ArgumentParser(description="Task Manager CLI")

    subparsers = parser.add_subparsers(dest="command")

    # Add task command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", type=str, help="Task description")
    add_parser.add_argument("--due", type=str, help="Task due date in YYYY-MM-DD format", required=False)
    add_parser.add_argument("--priority", type=str, choices=["low", "medium", "high"], help="Task priority", required=False)

    # List tasks command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", type=str, choices=["pending", "completed"], help="Filter tasks by status", required=False)
    list_parser.add_argument("--sort", type=str, choices=["created", "due", "priority"], help="Sort tasks by key", required=False)

    # Complete task command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("task_id", type=int, help="ID of the task to complete")

    # Remove task command
    remove_parser = subparsers.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("task_id", type=int, help="ID of the task to remove")

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "add":
        task = task_manager.add_task(description=args.description, due_date=args.due, priority=args.priority)
        print(f"Task added: #{task.id} - {task.description}")

    elif args.command == "list":
        tasks = task_manager.list_tasks(status=args.status, sort_key=args.sort)
        for task in tasks:
            print(task)

    elif args.command == "complete":
        success = task_manager.complete_task(args.task_id)
        if success:
            print(f"Task #{args.task_id} marked as completed")
        else:
            print(f"Task #{args.task_id} not found or already completed")

    elif args.command == "remove":
        success = task_manager.remove_task(args.task_id)
        if success:
            print(f"Task #{args.task_id} removed")
        else:
            print(f"Task #{args.task_id} not found")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()