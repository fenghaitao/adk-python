"""
Module: arithmetic
Description: Implements basic arithmetic operations.
"""


def add(a: float, b: float) -> float:
    """Adds two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtracts second number from the first."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divides the first number by the second. Handles division by zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
