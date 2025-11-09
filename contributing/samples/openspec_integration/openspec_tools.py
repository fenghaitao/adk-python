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

This module provides tools for OpenSpec operations by reusing the proven
toolset from spec_kit_integration. OpenSpec and spec-kit both require
identical file operations (read, write) and bash command execution, so
we leverage the existing implementation to avoid code duplication and
maintain consistency across spec-driven development samples.
"""

from __future__ import annotations


def create_openspec_toolset():
  """Create a toolset for OpenSpec operations.

  This function imports and returns the spec_kit toolset, which provides
  all the necessary tools for OpenSpec workflows:
  - read_file: Read file contents from the filesystem
  - write_file: Write or create files
  - bash_command: Execute shell commands

  Returns:
    Toolset: Configured toolset with file and bash tools for OpenSpec operations

  Design Rationale:
    OpenSpec and spec-kit both need identical file operations and command
    execution capabilities. By reusing the spec_kit_integration toolset, we:
    1. Avoid code duplication
    2. Leverage proven, tested implementations
    3. Maintain consistency across spec-driven samples
    4. Simplify maintenance (single source of truth)
  """
  # Import tools from spec_kit_integration
  # Using absolute import to access sibling sample directory
  try:
    # Try relative import first (when loaded as a package)
    from ..spec_kit_integration.spec_kit_tools import create_spec_kit_toolset
  except (ImportError, ValueError):
    # Fall back to absolute import (when loaded by ADK)
    from spec_kit_integration.spec_kit_tools import create_spec_kit_toolset

  # Reuse the same toolset - OpenSpec uses identical file operations
  return create_spec_kit_toolset()
