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
the OpenSpec workflow. It provides a focused set of tools for the OpenSpec
autonomous implementation workflow.

The Simics MCP toolset provides access to:
- Build and test tools (build_simics_project, run_simics_test) - PRIMARY TOOLS
- RAG documentation search (perform_rag_query for DML, Python API, and Simics docs)
- DML compiler tools (checkout_and_build_dmlc, check_with_dmlc)
- Package info tools (list_installed_packages, get_simics_version)

All tools connect to the Simics MCP server via SSE (Server-Sent Events) on port 8051.
"""

from __future__ import annotations

import os
from typing import Optional

# Import ADK MCP tools
try:
  from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
  from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
except ImportError:
  import sys
  from pathlib import Path

  current_dir = Path(__file__).parent
  adk_src_dir = current_dir.parent.parent.parent / "src"
  if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams


def create_simics_mcp_toolset(port: Optional[int] = None) -> MCPToolset:
  """Create a MCP toolset for Simics operations using SSE connection.

  This toolset is optimized for OpenSpec autonomous implementation workflow,
  focusing on build, test, and documentation tools needed during device
  implementation.

  Args:
    port: MCP server port. If not provided, reads from MCP_PORT environment
      variable or defaults to 8051.

  Returns:
    MCPToolset: Configured toolset with Simics MCP tools connected via SSE

  Raises:
    Exception: If Simics MCP server cannot be connected at
      http://127.0.0.1:{port}/sse

  Connection Details:
    - Transport: SSE (Server-Sent Events)
    - URL: http://127.0.0.1:{port}/sse
    - Connection timeout: 10 seconds
    - Read timeout: 300 seconds (for long-running builds/tests)

  Tool Filter Philosophy (OpenSpec-specific):
    OpenSpec workflow focuses on IMPLEMENTATION, not project setup. The agent
    needs:
    1. Build tools - to compile DML code (includes syntax checking)
    2. Test tools - to validate implementation
    3. RAG tools - to search documentation during implementation
    4. Package info - to verify environment

    Tools EXCLUDED (not needed for implementation):
    - Project creation (create_simics_project) - done before OpenSpec
    - Device skeleton (add_dml_device_skeleton) - done before OpenSpec
    - DML compiler tools (checkout_and_build_dmlc, check_with_dmlc) - build
      handles compilation
    - Large documentation (device examples, manuals) - use RAG instead
    - Simulation control - not needed for build/test workflow
    - Package management - environment already set up

  Note:
    The Simics MCP server must be running before using this toolset. The server
    provides both Simics tools AND RAG documentation search from a single
    endpoint. See README.md for server setup instructions.

  Example:
    >>> # In agent initialization
    >>> try:
    ...     from .simics_mcp_tools import create_simics_mcp_toolset
    ...     tools.append(create_simics_mcp_toolset())
    ...     print("✓ Simics MCP tools integrated successfully")
    ... except Exception as e:
    ...     print(f"ℹ Simics MCP tools not available: {e}")
  """
  # Get port from parameter, environment variable, or default
  if port is None:
    port = int(os.environ.get("MCP_PORT", "8051"))

  print(f"Creating Simics MCP toolset connecting to port {port}...")
  connection_params = SseConnectionParams(
      url=f"http://127.0.0.1:{port}/sse",
      headers={"Accept": "text/event-stream"},
      timeout=10.0,
      sse_read_timeout=300.0,
  )

  # OpenSpec-specific tool filter: Focus on implementation tools
  tool_filter = [
      # PRIMARY TOOLS: Build and test (used in every implementation)
      "build_simics_project",  # Build DML device modules
      "run_simics_test",  # Execute test suites
      # RAG query tool (for documentation and source code search during
      # implementation)
      "perform_rag_query",  # Search DML docs, Python API, Simics docs
      # Package info tools (for environment verification)
      "list_installed_packages",  # Check available Simics packages
      "get_simics_version",  # Verify Simics version
      "list_simics_platforms",  # List available platforms
      # EXCLUDED TOOLS (not needed for OpenSpec implementation workflow):
      # - "create_simics_project" - Project setup done before OpenSpec
      # - "add_dml_device_skeleton" - Skeleton created before OpenSpec
      # - "checkout_and_build_dmlc" - DML compiler not needed (build handles it)
      # - "check_with_dmlc" - Build provides syntax checking
      # - "generate_dml_registers" - Auto-generated during build
      # - "get_simics_device_example_*" - Too large, use RAG instead
      # - "get_simics_dml_1_4_reference_manual" - Too large, use RAG instead
      # - "get_simics_model_builder_user_guide" - Too large, use RAG instead
      # - "install_simics_package" - Environment already set up
      # - "start_simulation" - Not needed for build/test workflow
      # - "create_checkpoint" - Not needed for implementation
  ]

  return MCPToolset(connection_params=connection_params, tool_filter=tool_filter)
