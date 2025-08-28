"""
Unit Tests for advanced module.
"""

import os
import sys

import pytest

# Dynamically adjust PYTHONPATH to include src
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
)

from calculator.advanced import factorial
from calculator.advanced import power
from calculator.advanced import square_root


def test_power():
    assert power(2, 3) == 8
    assert power(5, 0) == 1
    assert power(-2, 3) == -8


def test_square_root():
    assert square_root(4) == 2
    assert square_root(16) == 4
    with pytest.raises(
        ValueError, match="Cannot compute square root of a negative number."
    ):
        square_root(-4)


def test_factorial():
    assert factorial(5) == 120
    assert factorial(0) == 1
    with pytest.raises(
        ValueError, match="Factorial is not defined for negative numbers."
    ):
        factorial(-3)
