"""
This module implements a Python calculator with basic and advanced operations. It leverages MCP file handling
tools for functionality like history persistence and logging.

Author: MCP
"""

from dataclasses import dataclass
from dataclasses import field
import logging
import math

# Configure logging
logging.basicConfig(
    filename="calculator.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
)


def add(a: float, b: float) -> float:
    """Add two numbers."""
    logging.info(f"Adding {a} and {b}")
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    logging.info(f"Subtracting {b} from {a}")
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    logging.info(f"Multiplying {a} and {b}")
    return a * b


def divide(a: float, b: float) -> float:
    """
    Divide two numbers. Raises ValueError if division by zero is attempted.
    """
    if b == 0:
        logging.error("Attempted division by zero")
        raise ValueError("Cannot divide by zero")
    logging.info(f"Dividing {a} by {b}")
    return a / b


def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    logging.info(f"Raising {base} to the power of {exponent}")
    return math.pow(base, exponent)


def square_root(value: float) -> float:
    """Calculate the square root of a number."""
    if value < 0:
        logging.error("Attempted to calculate square root of a negative number")
        raise ValueError("Cannot calculate square root of a negative number")
    logging.info(f"Calculating square root of {value}")
    return math.sqrt(value)


def factorial(value: int) -> int:
    """Calculate the factorial of a number."""
    if value < 0:
        logging.error("Attempted to calculate factorial of a negative number")
        raise ValueError("Cannot calculate factorial of a negative number")
    logging.info(f"Calculating factorial of {value}")
    return math.factorial(value)


@dataclass
class CalculatorMemory:
    """Class to manage calculator memory functions."""

    memory: float = field(default=0.0)

    def store(self, value: float):
        logging.info(f"Storing value {value} in memory")
        self.memory = value

    def recall(self) -> float:
        logging.info(f"Recalling value {self.memory} from memory")
        return self.memory

    def clear(self):
        logging.info("Clearing memory")
        self.memory = 0.0


def save_history(operation: str, result: float):
    """Save a calculation history to persistent storage."""
    from functions import write_file

    history_entry = f"{operation} = {result}\n"
    logging.info("Saving history to file")
    try:
        write_file(content=history_entry, path="calculation_history.log")
    except Exception as e:
        logging.error(f"Failed to save history: {e}")
        raise


def read_history() -> str:
    """Read history from persistent storage."""
    from functions import read_file

    logging.info("Reading history from file")
    try:
        return read_file(path="calculation_history.log").get("content", "")
    except Exception as e:
        logging.error(f"Failed to read history: {e}")
        raise
