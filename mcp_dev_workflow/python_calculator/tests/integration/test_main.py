"""
Integration Tests for Calculator CLI (main module).
"""

import os
import subprocess
import sys

import pytest

# Dynamically adjust PYTHONPATH to ensure src is included
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)


def get_main_path():
    """Helper to get the absolute path of main.py."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/main.py"))


def run_cli_command(args):
    """Helper function to run CLI commands."""
    result = subprocess.run(
        ["python3", get_main_path()] + args, capture_output=True, text=True
    )
    return result


def test_cli_add():
    result = run_cli_command(["add", "-a", "5", "-b", "10"])
    assert "Result: 15.0" in result.stdout


def test_cli_divide_by_zero():
    result = run_cli_command(["divide", "-a", "5", "-b", "0"])
    assert "Error: Cannot divide by zero." in result.stdout


def test_cli_invalid_operation():
    result = run_cli_command(["unknown", "-a", "5"])
    assert "usage:" in result.stderr
