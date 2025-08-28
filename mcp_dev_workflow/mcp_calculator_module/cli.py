"""
Calculator Command-Line Interface (CLI).

Provides an interactive way for users to perform operations using the calculator module.
Implements memory functions and history persistence.

Author: MCP
"""

import logging
import sys

from calculator import add
from calculator import CalculatorMemory
from calculator import divide
from calculator import factorial
from calculator import multiply
from calculator import power
from calculator import read_history
from calculator import save_history
from calculator import square_root
from calculator import subtract


def calculator_cli():
    """Run the calculator in command-line mode."""
    memory = CalculatorMemory()

    while True:
        try:
            print("\nWelcome to MCP Calculator!")
            print("Select an operation:")
            print("1. Add")
            print("2. Subtract")
            print("3. Multiply")
            print("4. Divide")
            print("5. Power")
            print("6. Square Root")
            print("7. Factorial")
            print("8. Memory Store")
            print("9. Memory Recall")
            print("10. Memory Clear")
            print("11. View History")
            print("12. Quit")

            choice = input("Enter your choice (1-12): ")

            if choice == "12":
                print("Goodbye!")
                break

            if choice in {"1", "2", "3", "4", "5"}:
                num1 = float(input("Enter the first number: "))
                num2 = float(input("Enter the second number: "))

                if choice == "1":
                    result = add(num1, num2)
                    operation = f"{num1} + {num2}"
                elif choice == "2":
                    result = subtract(num1, num2)
                    operation = f"{num1} - {num2}"
                elif choice == "3":
                    result = multiply(num1, num2)
                    operation = f"{num1} * {num2}"
                elif choice == "4":
                    result = divide(num1, num2)
                    operation = f"{num1} / {num2}"
                elif choice == "5":
                    result = power(num1, num2)
                    operation = f"{num1} ^ {num2}"

                print(f"Result: {result}")
                save_history(operation, result)

            elif choice == "6":
                num = float(input("Enter the number: "))
                result = square_root(num)
                print(f"Result: {result}")
                save_history(f"sqrt({num})", result)

            elif choice == "7":
                num = int(input("Enter an integer: "))
                result = factorial(num)
                print(f"Result: {result}")
                save_history(f"{num}!", result)

            elif choice == "8":
                value = float(input("Enter the value to store in memory: "))
                memory.store(value)
                print("Value stored in memory.")

            elif choice == "9":
                value = memory.recall()
                print(f"Recalled value: {value}")

            elif choice == "10":
                memory.clear()
                print("Memory cleared.")

            elif choice == "11":
                history = read_history()
                print("Calculation History:")
                print(history)

            else:
                print("Invalid choice. Please try again.")

        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            print("An error occurred. Please try again.")


if __name__ == "__main__":
    calculator_cli()
