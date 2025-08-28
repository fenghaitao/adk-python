"""
Integration tests for the CLI module.
"""
import pytest
import subprocess

def run_cli_command(command):
    """Helper function to run CLI commands."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

def test_cli_add_task():
    """Test adding a task using the CLI."""
    command = "python -m task_manager.src.cli add \"CLI Task\" --due 2024-02-15 --priority high"
    stdout, _ = run_cli_command(command)
    assert "Task added:" in stdout

def test_cli_list_tasks():
    """Test listing tasks using the CLI."""
    command = "python -m task_manager.src.cli list"
    stdout, _ = run_cli_command(command)
    assert "PENDING" in stdout