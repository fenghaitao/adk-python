"""
Task class for individual task representation in the Task Manager application.
"""
from datetime import datetime
import json
from typing import Optional, Dict

class Task:
    def __init__(self, task_id: int, description: str, status: str = "Pending",
                 created_date: Optional[datetime] = None, due_date: Optional[str] = None, priority: Optional[str] = None):
        """
        Initialize a Task object.
        :param task_id: Unique identifier for the task.
        :param description: Description of the task.
        :param status: Status of the task ("Pending" or "Completed").
        :param created_date: Timestamp when the task was created.
        :param due_date: Optional due date for the task.
        :param priority: Priority level of the task ("Low", "Medium", "High").
        """
        self.id = task_id
        self.description = description
        self.status = status
        self.created_date = created_date or datetime.now()
        self.due_date = due_date
        self.priority = priority

    def to_dict(self) -> Dict:
        """Convert the task object to a dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "created_date": self.created_date.isoformat(),
            "due_date": self.due_date,
            "priority": self.priority
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        """Create a task object from a dictionary."""
        return Task(
            task_id=data["id"],
            description=data["description"],
            status=data.get("status", "Pending"),
            created_date=datetime.fromisoformat(data["created_date"]),
            due_date=data.get("due_date"),
            priority=data.get("priority")
        )

    def __str__(self) -> str:
        """String representation of the task."""
        priority_str = f" (Priority: {self.priority})" if self.priority else ""
        due_date_str = f" (Due: {self.due_date})" if self.due_date else ""
        return f"{self.id}. [{self.status.upper()}] {self.description}{due_date_str}{priority_str}"