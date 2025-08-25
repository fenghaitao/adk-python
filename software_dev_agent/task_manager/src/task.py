from datetime import date
from typing import Optional
import uuid

class Task:
    """
    Represents a task in the Task Manager application.
    """

    def __init__(self, description: str, due_date: Optional[str] = None, priority: str = "Low"):
        if not description.strip():
            raise ValueError("Task description cannot be empty.")

        self.id = str(uuid.uuid4())  # Unique identifier
        self.description = description.strip()
        self.status = "Pending"
        self.created_date = str(date.today())
        self.due_date = due_date.strip() if due_date else None
        self.priority = priority.capitalize()

        if priority.lower() not in ["low", "medium", "high"]:
            raise ValueError("Priority must be 'Low', 'Medium', or 'High'.")

    def mark_completed(self):
        """Marks the task as completed."""
        self.status = "Completed"

    def to_dict(self):
        """Converts the task to a dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "created_date": self.created_date,
            "due_date": self.due_date,
            "priority": self.priority,
        }

    @staticmethod
    def from_dict(data: dict):
        """Creates a Task instance from a dictionary."""
        task = Task(description=data["description"], due_date=data.get("due_date"), priority=data.get("priority", "Low"))
        task.id = data["id"]
        task.status = data["status"]
        task.created_date = data["created_date"]
        return task
