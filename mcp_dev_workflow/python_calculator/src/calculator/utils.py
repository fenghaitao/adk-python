"""
Module: utils
Description: Implements utility functions such as memory operations and calculation history.
"""

import os


class Memory:
    """Handles memory functions: store, recall, and clear."""

    def __init__(self):
        self.memory = None

    def store(self, value: float) -> None:
        self.memory = value

    def recall(self) -> float:
        if self.memory is None:
            raise ValueError("No value stored in memory.")
        return self.memory

    def clear(self) -> None:
        self.memory = None


class History:
    """Handles calculation history with persistence using MCP file storage."""

    def __init__(self, file_path: str = "history.txt"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as file:
                pass

    def append(self, record: str) -> None:
        with open(self.file_path, "a") as file:
            file.write(record + "\n")

    def read(self) -> list[str]:
        with open(self.file_path, "r") as file:
            return file.readlines()
