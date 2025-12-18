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

This module provides tools for OpenSpec operations including file operations,
directory listing, and bash command execution.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from google.adk.tools import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext


class OpenSpecToolset(BaseToolset):
    """Toolset for OpenSpec operations."""

    def __init__(self):
        super().__init__()
        self.name = "openspec_toolset"
        self._tools = []

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
  for OpenSpec workflows.

  Returns:
    OpenSpecToolset: Configured toolset with file and bash tools for OpenSpec operations

  Design Rationale:
    OpenSpec needs file operations and command execution capabilities. This toolset provides:
    1. File reading (full file)
    2. File writing and replacement
    3. Directory listing
    4. Bash command execution (for text analysis with grep, wc, etc.)
  """
  return OpenSpecToolset()
