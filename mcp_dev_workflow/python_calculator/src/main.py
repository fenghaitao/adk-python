"""
Module: main
Description: Command-line interface for the Python calculator.
"""

import argparse

from calculator.advanced import factorial
from calculator.advanced import power
from calculator.advanced import square_root
from calculator.arithmetic import add
from calculator.arithmetic import divide
from calculator.arithmetic import multiply
from calculator.arithmetic import subtract
from calculator.utils import History
from calculator.utils import Memory


def main():
    memory = Memory()
    history = History()

    parser = argparse.ArgumentParser(description="Python Calculator CLI")
    parser.add_argument(
        "operation",
        type=str,
        choices=["add", "subtract", "multiply", "divide", "power", "sqrt", "factorial"],
        help="Operation to perform.",
    )
    parser.add_argument("-a", "--num1", type=float, help="The first number.")
    parser.add_argument(
        "-b", "--num2", type=float, help="The second number (if applicable)."
    )
    parser.add_argument(
        "--store", action="store_true", help="Stores the result in memory."
    )

    args = parser.parse_args()

    try:
        result = None
        if args.operation == "add":
            result = add(args.num1, args.num2)
        elif args.operation == "subtract":
            result = subtract(args.num1, args.num2)
        elif args.operation == "multiply":
            result = multiply(args.num1, args.num2)
        elif args.operation == "divide":
            result = divide(args.num1, args.num2)
        elif args.operation == "power":
            result = power(args.num1, args.num2)
        elif args.operation == "sqrt":
            result = square_root(args.num1)
        elif args.operation == "factorial":
            result = factorial(int(args.num1))

        if result is not None:
            print(f"Result: {result}")
            history.append(f"{args.operation}({args.num1}, {args.num2}) = {result}")

            if args.store:
                memory.store(result)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
