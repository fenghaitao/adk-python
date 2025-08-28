"""
Unit Tests for arithmetic module.
"""

import os
import sys

import pytest

# Dynamically adjust PYTHONPATH to include src
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from calculator.arithmetic import add
from calculator.arithmetic import divide
from calculator.arithmetic import multiply
from calculator.arithmetic import subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, -1) == -2
    assert add(0, 5) == 5


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(-3, -2) == -1


def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(0, 3) == 0
    assert multiply(-1, 10) == -10


def test_divide():
    assert divide(10, 2) == 5
    assert divide(-10, 2) == -5
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(5, 0)
