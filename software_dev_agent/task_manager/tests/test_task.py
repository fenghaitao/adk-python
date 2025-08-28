"""
Unit tests for the Task class.
"""
import pytest
from datetime import datetime
from task_manager.src.task import Task

def test_task_initialization():
    """Test the initialization of a Task object."""
    task = Task(task_id=1, description="Sample Task", due_date="2024-02-15", priority="High")
    assert task.id == 1
    assert task.description == "Sample Task"
    assert task.status == "Pending"
    assert task.due_date == "2024-02-15"
    assert task.priority == "High"

def test_task_to_dict():
    """Test the conversion of a Task object to a dictionary."""
    now = datetime.now()
    task = Task(task_id=1, description="Sample Task", created_date=now)
    task_dict = task.to_dict()
    assert task_dict["id"] == 1
    assert task_dict["description"] == "Sample Task"
    assert task_dict["status"] == "Pending"
    assert datetime.fromisoformat(task_dict["created_date"]) == now

def test_task_from_dict():
    """Test creating a Task object from a dictionary."""
    data = {
        "id": 1,
        "description": "Sample Task",
        "status": "Pending",
        "created_date": datetime.now().isoformat(),
        "due_date": "2024-02-15",
        "priority": "High"
    }
    task = Task.from_dict(data)
    assert task.id == 1
    assert task.description == "Sample Task"
    assert task.status == "Pending"
    assert task.due_date == "2024-02-15"
    assert task.priority == "High"