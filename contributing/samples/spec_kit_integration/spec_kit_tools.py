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

"""Spec-Kit tools for ADK integration."""

import os
import subprocess
import json
from pathlib import Path
from typing import Any, Dict, Optional, List

# Import ADK tools
try:
    from google.adk.tools.base_tool import BaseTool
    from google.adk.tools.base_toolset import BaseToolset
    from google.adk.tools.tool_context import ToolContext
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
    from mcp import StdioServerParameters
except ImportError:
    import sys
    current_dir = Path(__file__).parent
    adk_src_dir = current_dir.parent.parent.parent / "src"
    if adk_src_dir.exists():
        sys.path.insert(0, str(adk_src_dir))
        from google.adk.tools.base_tool import BaseTool
        from google.adk.tools.base_toolset import BaseToolset
        from google.adk.tools.tool_context import ToolContext
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
        from mcp import StdioServerParameters


class SpecKitReadTool(BaseTool):
    """Tool for reading files in Spec-Kit workflows."""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a file. Use this to examine files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="read_file",
                description="Read the contents of a file. Use this to examine files in the project.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="Path to the file to read"
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
        if not file_path:
            return {"error": "file_path is required"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "file_path": file_path}
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}


class SpecKitWriteTool(BaseTool):
    """Tool for writing files in Spec-Kit workflows."""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file. Use this to create or update files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="write_file",
                description="Write content to a file. Use this to create or update files in the project.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="Path to the file to write"
                        ),
                        "content": types.Schema(
                            type=types.Type.STRING,
                            description="Content to write to the file"
                        ),
                        "overwrite": types.Schema(
                            type=types.Type.BOOLEAN,
                            description="Whether to overwrite if file exists (default: False)"
                        )
                    },
                    required=["file_path", "content"]
                )
            )
        except ImportError:
            return None

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        file_path = args.get("file_path")
        content = args.get("content", "")
        overwrite = args.get("overwrite", False)

        if not file_path:
            return {"error": "file_path is required"}

        try:
            # Check if file exists and overwrite is False
            if os.path.exists(file_path) and not overwrite:
                return {"error": f"File already exists: {file_path}. Set overwrite=True to overwrite."}

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "file_path": file_path, "bytes_written": len(content)}
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}


class SpecKitBashTool(BaseTool):
    """Tool for executing bash commands in Spec-Kit workflows."""

    def __init__(self):
        super().__init__(
            name="bash_command",
            description="Execute bash commands. Use this to run shell commands, git operations, and spec-kit scripts.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="bash_command",
                description="Execute bash commands. Use this to run shell commands, git operations, and spec-kit scripts.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "command": types.Schema(
                            type=types.Type.STRING,
                            description="Bash command to execute"
                        ),
                        "working_directory": types.Schema(
                            type=types.Type.STRING,
                            description="Directory to run command in (default: '.')"
                        ),
                        "timeout": types.Schema(
                            type=types.Type.INTEGER,
                            description="Timeout in seconds (default: 60)"
                        )
                    },
                    required=["command"]
                )
            )
        except ImportError:
            return None

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        command = args.get("command")
        working_directory = args.get("working_directory", ".")
        timeout = args.get("timeout", 60)

        if not command:
            return {"error": "command is required"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "working_directory": working_directory,
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": f"Error executing command: {str(e)}"}


class SpecKitToolset(BaseToolset):
    """Toolset for spec-kit commands using basic file and bash tools."""

    def __init__(self):
        super().__init__()
        self.name = "spec_kit_toolset"
        self.tools = [
            SpecKitReadTool(),
            SpecKitWriteTool(),
            SpecKitBashTool()
        ]

    async def get_tools(self, readonly_context=None):
        """Return all tools in this toolset."""
        return self.tools


def create_simics_mcp_toolset() -> MCPToolset:
    """Create a MCP toolset that connects to the simics-mcp-server."""
    current_dir = Path(__file__).parent
    simics_server_dir = current_dir / "simics-mcp-server"
    server_script = simics_server_dir / "run_server.py"
    
    # Create stdio connection parameters for the simics-mcp-server
    simics_python = simics_server_dir / ".venv" / "bin" / "python3"
    pyvenv_cfg = simics_server_dir / ".venv" / "pyvenv.cfg"
    python_version_dir = None

    if pyvenv_cfg.exists():
        pyvenv_lines = pyvenv_cfg.read_text(encoding="utf-8").splitlines()
        for line in pyvenv_lines:
            if line.startswith("version ="):
                version_value = line.split("=", 1)[1].strip()
                if version_value:
                    major_minor = ".".join(version_value.split(".")[:2])
                    python_version_dir = (
                        simics_server_dir / ".venv" / "lib" / f"python{major_minor}"
                    )
                break

    if python_version_dir is None:
        lib_dir = simics_server_dir / ".venv" / "lib"
        if lib_dir.exists():
            for path in lib_dir.iterdir():
                if path.is_dir() and path.name.startswith("python"):
                    python_version_dir = path
                    break

    if python_version_dir is None:
        raise FileNotFoundError(
            "Unable to determine Python version directory for simics-mcp-server virtualenv."
        )

    site_packages_dir = python_version_dir / "site-packages"
    if not site_packages_dir.exists():
        raise FileNotFoundError(
            "Unable to locate site-packages directory within the simics-mcp-server virtualenv."
        )

    server_env = os.environ.copy()
    existing_pythonpath = server_env.get("PYTHONPATH")
    if existing_pythonpath:
        server_env["PYTHONPATH"] = f"{site_packages_dir}:{existing_pythonpath}"
    else:
        server_env["PYTHONPATH"] = str(site_packages_dir)

    server_params = StdioServerParameters(
        command=str(simics_python),
        args=[str(server_script), "--transport", "stdio"],
        env=server_env
    )
    
    connection_params = StdioConnectionParams(
        server_params=server_params,
        timeout=10.0
    )
    
    # Filter for specific Simics tools we want to expose
    tool_filter = [
        "create_simics_project",
        "install_simics_package", 
        "list_installed_packages",
        "search_packages",
        "uninstall_simics_package",
        "get_simics_version"
    ]
    
    return MCPToolset(
        connection_params=connection_params,
        tool_filter=tool_filter
    )


def create_spec_kit_toolset() -> SpecKitToolset:
    """Create a spec-kit toolset."""
    return SpecKitToolset()