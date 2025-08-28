"""
TaskManager class for managing tasks in the Task Manager application.
"""
import os
import json
from typing import List, Optional
from datetime import datetime
from .task import Task

class TaskManager:
    def __init__(self, data_file: str):
        """
        Initialize the TaskManager with a specified data file for persistence.
        :param data_file: Path to the JSON file for data persistence.
        """
        self.data_file = data_file
        self.tasks = []
        self._load_tasks()

    def _load_tasks(self):
        """Load tasks from the JSON data file."""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self._save_tasks()  # Initialize the file if it doesn't exist

        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                self.tasks = [Task.from_dict(task) for task in data]
        except (json.JSONDecodeError, FileNotFoundError):
            # Handle corrupt or missing data file
            self.tasks = []

    def _save_tasks(self):
        """Save tasks to the JSON data file."""
        with open(self.data_file, 'w') as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    def add_task(self, description: str, due_date: Optional[str] = None, priority: Optional[str] = None):
        """Add a new task to the task list."""
        task_id = 1 if not self.tasks else self.tasks[-1].id + 1
        task = Task(task_id=task_id, description=description, due_date=due_date, priority=priority)
        self.tasks.append(task)
        self._save_tasks()
        return task

    def list_tasks(self, status: Optional[str] = None, sort_key: Optional[str] = None) -> List[Task]:
        """List tasks with optional filtering and sorting."""
        tasks = self.tasks
        if status:
            tasks = [task for task in tasks if task.status.lower() == status.lower()]

        if sort_key:
            if sort_key == "created":
                tasks.sort(key=lambda t: t.created_date)
            elif sort_key == "due":
                tasks.sort(key=lambda t: t.due_date or datetime.max)
            elif sort_key == "priority":
                priority_order = {"High": 1, "Medium": 2, "Low": 3, None: 4}
                tasks.sort(key=lambda t: priority_order[t.priority])

        return tasks

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        task = self._find_task_by_id(task_id)
        if task and task.status.lower() == "pending":
            task.status = "Completed"
            self._save_tasks()
            return True
        return False

    def remove_task(self, task_id: int) -> bool:
        """Remove a task by its ID."""
        task = self._find_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self._save_tasks()
            return True
        return False

    def _find_task_by_id(self, task_id: int) -> Optional[Task]:
        """Find a task by its unique ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None