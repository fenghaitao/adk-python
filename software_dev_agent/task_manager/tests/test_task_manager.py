"""
Unit tests for the TaskManager class.
"""
import pytest
import os
import json
from task_manager.src.task_manager import TaskManager

def test_add_task():
    """Test adding a new task."""
    manager = TaskManager("test_tasks.json")
    manager.tasks = []  # Clear existing tasks
    task = manager.add_task("New Task", due_date="2024-02-15", priority="Medium")
    assert task.id == 1
    assert task.description == "New Task"
    assert task.priority == "Medium"

def test_list_tasks():
    """Test listing tasks."""
    manager = TaskManager("test_tasks.json")
    manager.tasks = []
    manager.add_task("Task 1", priority="High")
    manager.add_task("Task 2", priority="Low")
    tasks = manager.list_tasks(sort_key="priority")
    assert len(tasks) == 2
    assert tasks[0].priority == "High"

def test_save_and_load_tasks():
    """Test saving and loading tasks to/from a file."""
    test_file = "test_tasks.json"
    manager = TaskManager(test_file)
    manager.tasks = []
    manager.add_task("Persisted Task")

    # Save tasks
    manager._save_tasks()
    assert os.path.exists(test_file)

    # Load tasks
    manager._load_tasks()
    assert len(manager.tasks) == 1
    assert manager.tasks[0].description == "Persisted Task"

    # Cleanup
    os.remove(test_file)