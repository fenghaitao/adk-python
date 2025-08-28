"""
Unit tests for calculator.py.

Tests all basic and advanced operations, memory functions, and error cases.
"""

from mcp_calculator_module.calculator import add
from mcp_calculator_module.calculator import CalculatorMemory
from mcp_calculator_module.calculator import divide
from mcp_calculator_module.calculator import factorial
from mcp_calculator_module.calculator import multiply
from mcp_calculator_module.calculator import power
from mcp_calculator_module.calculator import square_root
from mcp_calculator_module.calculator import subtract
import pytest


def test_add():
    assert add(2, 3) == 5
    assert add(-3, 3) == 0


def test_subtract():
    assert subtract(10, 5) == 5
    assert subtract(0, 10) == -10


def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-4, 2.5) == -10.0


def test_divide():
    assert divide(10, 2) == 5
    with pytest.raises(ValueError):
        divide(10, 0)


def test_power():
    assert power(2, 3) == 8
    assert power(4, 0.5) == 2


def test_square_root():
    assert square_root(16) == 4
    with pytest.raises(ValueError):
        square_root(-1)


def test_factorial():
    assert factorial(5) == 120
    with pytest.raises(ValueError):
        factorial(-5)


def test_memory():
    memory = CalculatorMemory()

    # Test store and recall
    memory.store(100)
    assert memory.recall() == 100

    memory.store(50.5)
    assert memory.recall() == 50.5

    # Test clear
    memory.clear()
    assert memory.recall() == 0.0
