import argparse
from task_manager.task_manager import TaskManager

def main():
    manager = TaskManager()

    parser = argparse.ArgumentParser(description="Task Manager Command Line Interface")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add Task Command
    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("description", type=str, help="Description of the task.")
    add_parser.add_argument("--due", type=str, help="Optional due date (YYYY-MM-DD).")
    add_parser.add_argument("--priority", type=str, choices=["low", "medium", "high"], default="low", help="Task priority.")

    # List Tasks Command
    list_parser = subparsers.add_parser("list", help="List tasks.")
    list_parser.add_argument("--status", type=str, choices=["pending", "completed"], help="Filter by task status.")

    # Complete Task Command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed.")
    complete_parser.add_argument("task_id", type=str, help="ID of the task to complete.")

    # Remove Task Command
    remove_parser = subparsers.add_parser("remove", help="Remove a task.")
    remove_parser.add_argument("task_id", type=str, help="ID of the task to remove.")

    args = parser.parse_args()

    if args.command == "add":
        task = manager.add_task(description=args.description, due_date=args.due, priority=args.priority)
        print(f"Task added: #{task.id} - {task.description}")

    elif args.command == "list":
        tasks = manager.list_tasks(status=args.status)
        for task in tasks:
            print(f"{task.id}. [{task.status.upper()}] {task.description} (Due: {task.due_date}, Priority: {task.priority})")

    elif args.command == "complete":
        if manager.complete_task(args.task_id):
            print(f"Task #{args.task_id} marked as completed.")
        else:
            print(f"Task with ID {args.task_id} not found.")

    elif args.command == "remove":
        if manager.remove_task(args.task_id):
            print(f"Task #{args.task_id} removed.")
        else:
            print(f"Task with ID {args.task_id} not found.")

if __name__ == "__main__":
    main()