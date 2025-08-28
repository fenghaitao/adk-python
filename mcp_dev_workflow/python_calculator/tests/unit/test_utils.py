"""
Unit Tests for utils module.
"""

import os
import sys

import pytest

# Dynamically adjust PYTHONPATH to include src
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from calculator.utils import History
from calculator.utils import Memory


def test_memory():
    mem = Memory()

    with pytest.raises(ValueError, match="No value stored in memory."):
        mem.recall()

    mem.store(42)
    assert mem.recall() == 42

    mem.clear()
    with pytest.raises(ValueError, match="No value stored in memory."):
        mem.recall()


def test_history(tmp_path):
    history_path = tmp_path / "test_history.txt"
    hist = History(file_path=str(history_path))

    assert hist.read() == []

    hist.append("test1")
    hist.append("test2")

    assert hist.read() == ["test1\n", "test2\n"]
