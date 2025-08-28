"""
Module: errors
Description: Custom error classes for the calculator.
"""


class CalculatorError(Exception):
    """Base class for all calculator errors."""

    pass


class InvalidInputError(CalculatorError):
    """Raised when the input is invalid."""

    pass


class DivisionByZeroError(CalculatorError):
    """Raised when attempting to divide by zero."""

    pass
