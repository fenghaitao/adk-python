import json
import os
from typing import List, Optional
from .task import Task

class TaskManager:
    """
    Manages a collection of tasks, including CRUD operations and data persistence.
    """

    DATA_FILE = "./task_manager/data/tasks.json"

    def __init__(self):
        self.tasks: List[Task] = []
        self.load_tasks()

    def add_task(self, description: str, due_date: Optional[str] = None, priority: str = "Low") -> Task:
        """Adds a new task to the task manager."""
        task = Task(description=description, due_date=due_date, priority=priority)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """Lists tasks, optionally filtering by status."""
        if status:
            return [task for task in self.tasks if task.status.lower() == status.lower()]
        return self.tasks

    def complete_task(self, task_id: str) -> bool:
        """Marks a task as completed by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                task.mark_completed()
                self.save_tasks()
                return True
        return False

    def remove_task(self, task_id: str) -> bool:
        """Removes a task from the manager by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                self.save_tasks()
                return True
        return False

    def save_tasks(self):
        """Saves all tasks to a JSON file."""
        os.makedirs(os.path.dirname(self.DATA_FILE), exist_ok=True)
        with open(self.DATA_FILE, "w", encoding="utf-8") as file:
            json.dump([task.to_dict() for task in self.tasks], file, indent=4)

    def load_tasks(self):
        """Loads tasks from a JSON file."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as file:
                    task_data = json.load(file)
                    self.tasks = [Task.from_dict(data) for data in task_data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.tasks = []