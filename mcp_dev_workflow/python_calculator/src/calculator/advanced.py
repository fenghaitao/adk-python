"""
Module: advanced
Description: Implements advanced mathematical operations.
"""

import math


def power(base: float, exponent: float) -> float:
    """Raises a number to a power."""
    return math.pow(base, exponent)


def square_root(number: float) -> float:
    """Calculates the square root of a number."""
    if number < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return math.sqrt(number)


def factorial(number: int) -> int:
    """Calculates the factorial of a number."""
    if number < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    return math.factorial(number)
