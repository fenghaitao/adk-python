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

"""Simics MCP tools module for OpenSpec integration.

This module provides Simics MCP toolset for hardware device modeling within
the OpenSpec workflow. It reuses the proven implementation from spec_kit_integration
to maintain consistency and avoid code duplication.

The Simics MCP toolset provides access to:
- Simics project management tools (create_simics_project, add_dml_device_skeleton)
- Build and test tools (build_simics_project, run_simics_test)
- RAG documentation search (perform_rag_query for DML, Python API, and Simics docs)
- Package management tools (list_installed_packages, get_simics_version)

All tools connect to the Simics MCP server via SSE (Server-Sent Events) on port 8051.
"""

from __future__ import annotations


def create_simics_mcp_toolset():
    """Create a MCP toolset for Simics operations using SSE connection.

    This function imports and returns the Simics MCP toolset from spec_kit_integration,
    which provides all necessary tools for hardware device modeling:
    - Simics project management (create, build, test)
    - RAG documentation search (DML, Python API, Simics docs)
    - Package management and version checking

    Returns:
      MCPToolset: Configured toolset with Simics MCP tools connected via SSE

    Raises:
      Exception: If Simics MCP server cannot be connected at http://127.0.0.1:8051/sse

    Connection Details:
      - Transport: SSE (Server-Sent Events)
      - URL: http://127.0.0.1:8051/sse
      - Connection timeout: 10 seconds
      - Read timeout: 300 seconds (for long-running builds/tests)

    Design Rationale:
      OpenSpec and spec-kit both need identical Simics MCP integration. By reusing
      the spec_kit_integration implementation, we:
      1. Avoid code duplication
      2. Leverage proven, tested Simics MCP connection logic
      3. Maintain consistency across spec-driven samples
      4. Simplify maintenance (single source of truth)
      5. Ensure both integrations benefit from improvements

    Note:
      The Simics MCP server must be running before using this toolset. The server
      provides both Simics tools AND RAG documentation search from a single endpoint.
      See README.md for server setup instructions.

    Example:
      >>> # In agent initialization
      >>> try:
      ...     from .simics_mcp_tools import create_simics_mcp_toolset
      ...     tools.append(create_simics_mcp_toolset())
      ...     print("✓ Simics MCP tools loaded (includes RAG documentation search)")
      ... except Exception as e:
      ...     print(f"ℹ Simics MCP tools not available: {e}")
      ...     print("  (Software projects will work normally)")
    """
    # Import Simics MCP toolset from spec_kit_integration
    # Using absolute import to access sibling sample directory
    try:
        # Try relative import first (when loaded as a package)
        from ..spec_kit_integration.spec_kit_tools import create_simics_mcp_toolset
    except (ImportError, ValueError):
        # Fall back to absolute import (when loaded by ADK)
        from spec_kit_integration.spec_kit_tools import create_simics_mcp_toolset

    # Reuse the same toolset - OpenSpec uses identical Simics MCP integration
    # This provides both Simics tools AND RAG documentation search
    return create_simics_mcp_toolset()
