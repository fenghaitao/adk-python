# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""OpenSpec tools module for ADK integration.

This module provides tools for OpenSpec operations, including the
SpecKitReadRangeTool for chunked file reading to handle large files
efficiently without exceeding LLM context windows.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from google.adk.tools import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext


class SpecKitReadRangeTool(BaseTool):
    """Tool for reading a byte range from a file (chunked reading).

    Useful for processing large files (e.g., session JSON) in sections to
    avoid exceeding LLM context windows.
    """

    def __init__(self):
        super().__init__(
            name="read_file_range",
            description=(
                "Read a byte range from a file. Use this to stream large files in"
                " chunks. Provide offset (start byte) and length (max bytes)."
            ),
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="read_file_range",
                description=(
                    "Read a byte range from a file. Use this to stream large files"
                    " in chunks. Provide offset (start byte) and length (max bytes)."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="Path to the file to read"
                        ),
                        "offset": types.Schema(
                            type=types.Type.INTEGER,
                            description="Start byte offset (default: 0)"
                        ),
                        "length": types.Schema(
                            type=types.Type.INTEGER,
                            description="Maximum bytes to read (default: 65536)"
                        ),
                        "encoding": types.Schema(
                            type=types.Type.STRING,
                            description="Text encoding for decoding bytes (default: utf-8)"
                        )
                    },
                    required=["file_path"]
                )
            )
        except ImportError:
            return None

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        file_path = args.get("file_path")
        offset = int(args.get("offset", 0))
        length = int(args.get("length", 65536))
        encoding = args.get("encoding", "utf-8")

        if not file_path:
            return {"error": "file_path is required"}
        if offset < 0:
            return {"error": "offset must be >= 0"}
        if length <= 0:
            return {"error": "length must be > 0"}

        try:
            total_size = os.path.getsize(file_path)
            if offset > total_size:
                # Return empty chunk at EOF
                return {
                    "content": "",
                    "start_offset": offset,
                    "end_offset": offset,
                    "total_size": total_size,
                    "eof": True,
                }

            with open(file_path, "rb") as f:
                f.seek(offset)
                data = f.read(length)
                chunk = data.decode(encoding, errors="replace")
                end_offset = offset + len(data)
                eof = end_offset >= total_size
                return {
                    "content": chunk,
                    "start_offset": offset,
                    "end_offset": end_offset,
                    "total_size": total_size,
                    "eof": eof,
                }
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": f"Error reading file range: {str(e)}"}


class OpenSpecToolset(BaseToolset):
    """Toolset for OpenSpec operations with chunked file reading capability."""

    def __init__(self):
        super().__init__()
        self.name = "openspec_toolset"
        self._tools = [
            SpecKitReadRangeTool(),
        ]

        # Import and add spec_kit tools
        try:
            # Try relative import first (when loaded as a package)
            from ..spec_kit_integration.spec_kit_tools import (
                SpecKitReadTool,
                SpecKitWriteTool,
                SpecKitBashTool,
                SpecKitListDirectoryTool,
                SpecKitFileReplaceTool,
            )
        except (ImportError, ValueError):
            # Fall back to absolute import (when loaded by ADK)
            try:
                from spec_kit_integration.spec_kit_tools import (
                    SpecKitReadTool,
                    SpecKitWriteTool,
                    SpecKitBashTool,
                    SpecKitListDirectoryTool,
                    SpecKitFileReplaceTool,
                )
            except ImportError:
                # Create the toolset from spec_kit_integration sample instead
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'spec_kit_integration'))
                try:
                    from spec_kit_tools import (
                        SpecKitReadTool,
                        SpecKitWriteTool,
                        SpecKitBashTool,
                        SpecKitListDirectoryTool,
                        SpecKitFileReplaceTool,
                    )
                finally:
                    sys.path.pop(0)

        # Add the essential spec_kit tools
        self._tools.extend([
            SpecKitReadTool(),
            SpecKitWriteTool(),
            SpecKitBashTool(),
            SpecKitListDirectoryTool(),
            SpecKitFileReplaceTool(),
        ])

    async def get_tools(self, readonly_context=None) -> list:
        """Return the list of tools in this toolset."""
        return self._tools


def create_openspec_toolset():
  """Create a toolset for OpenSpec operations.

  This function creates an OpenSpecToolset that provides all necessary tools
  for OpenSpec workflows, including the new SpecKitReadRangeTool for chunked
  file reading to handle large files efficiently.

  Returns:
    OpenSpecToolset: Configured toolset with file and bash tools for OpenSpec operations

  Design Rationale:
    OpenSpec needs file operations and command execution capabilities, plus
    the ability to handle large files in chunks. This toolset provides:
    1. File reading (both full and chunked)
    2. File writing and replacement
    3. Directory listing
    4. Bash command execution
    5. Efficient large file processing
  """
  return OpenSpecToolset()
