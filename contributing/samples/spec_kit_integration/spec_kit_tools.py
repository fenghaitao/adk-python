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


def truncate_content(content: str, max_length: int = 128000) -> str:
    """
    Truncate content to prevent token limit issues.
    
    Args:
        content: The content to truncate
        max_length: Maximum character length (default 50K chars ≈ 12.5K tokens)
    
    Returns:
        Truncated content with truncation notice if needed
    """
    if len(content) <= max_length:
        return content
    
    truncated = content[:max_length]
    truncation_notice = f"\n\n[CONTENT TRUNCATED - Original length: {len(content)} chars, showing first {max_length} chars. Use more specific queries to get complete information.]"
    return truncated + truncation_notice


def truncate_json_response(json_str: str, max_file_entries: int = 5) -> str:
    """
    Truncate JSON responses from MCP tools to prevent token limit issues.
    
    Args:
        json_str: JSON string response
        max_file_entries: Maximum number of file entries to include
    
    Returns:
        Truncated JSON string
    """
    try:
        import json
        data = json.loads(json_str)
        
        # If there are file collections, limit them
        if isinstance(data, dict):
            for key in ['device_files', 'test_files', 'manual_files', 'guide_files']:
                if key in data and isinstance(data[key], dict):
                    files = data[key]
                    if len(files) > max_file_entries:
                        # Keep only the first max_file_entries files
                        limited_files = dict(list(files.items())[:max_file_entries])
                        data[key] = limited_files
                        data[f'{key}_truncated'] = True
                        data[f'{key}_original_count'] = len(files)
                        data[f'{key}_showing_count'] = len(limited_files)
        
        return json.dumps(data, indent=2)
    except Exception:
        # If JSON parsing fails, use simple truncation
        return truncate_content(json_str, 30000)


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

            # Truncate large outputs to prevent token limit issues
            stdout_truncated = truncate_content(result.stdout, max_length=128000)
            stderr_truncated = truncate_content(result.stderr, max_length=32000)

            return {
                "stdout": stdout_truncated,
                "stderr": stderr_truncated,
                "return_code": result.returncode,
                "command": command,
                "working_directory": working_directory,
                "stdout_truncated": len(stdout_truncated) < len(result.stdout),
                "stderr_truncated": len(stderr_truncated) < len(result.stderr),
                "original_stdout_size": len(result.stdout),
                "original_stderr_size": len(result.stderr),
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


class TruncatedMCPToolset(MCPToolset):
    """MCP Toolset wrapper that truncates large responses to prevent token limit issues."""
    
    def __init__(self, connection_params, tool_filter=None):
        super().__init__(connection_params=connection_params, tool_filter=tool_filter)
        self._tools_that_need_truncation = {
            "get_simics_device_example_i2c",
            "get_simics_device_example_ds12887", 
            "get_simics_dml_1_4_reference_manual",
            "get_simics_model_builder_user_guide",
            "list_installed_packages",
            "list_simics_platforms"
        }
    
    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Invoke tool and truncate response if needed."""
        result = await super().invoke_tool(tool_name, arguments)
        
        # Truncate responses from documentation/example tools that return large JSON
        if tool_name in self._tools_that_need_truncation and isinstance(result, str):
            if result.strip().startswith('{') or result.strip().startswith('['):
                # This looks like JSON, apply JSON-specific truncation
                result = truncate_json_response(result, max_file_entries=3)
            else:
                # Apply general truncation
                result = truncate_content(result, max_length=20000)
        
        return result


def create_simics_mcp_toolset() -> TruncatedMCPToolset:
    """Create a MCP toolset that connects to the simics-mcp-server with content truncation."""
    print("Creating Simics MCP toolset...")
    current_dir = Path(__file__).parent
    simics_server_dir = current_dir / "simics-mcp-server"
    server_script = simics_server_dir / "run_server.py"

    # Check if Simics server exists before creating toolset
    if not server_script.exists():
        print(f"Warning: Simics MCP server not found at {server_script}")
        print("Simics tools will not be available")
        # Return empty toolset or handle gracefully
        raise FileNotFoundError(f"Simics MCP server not found: {server_script}")

    # Create stdio connection parameters for the simics-mcp-server
    simics_python = simics_server_dir / ".venv" / "bin" / "python3"
    server_params = StdioServerParameters(
        command=str(simics_python),
        args=[str(server_script), "--transport", "stdio"]
    )

    connection_params = StdioConnectionParams(
        server_params=server_params,
        timeout=300.0
    )

    # Filter for specific Simics tools we want to expose
    tool_filter = [
        # Core project management tools
        "list_installed_packages",
        "list_simics_platforms", 
        "get_simics_version",
        
        # Device modeling and development tools
        "create_simics_project",
        "add_dml_device_skeleton",
        "build_simics_project",
        "run_simics_test",
        
        # Device examples and documentation tools
        "get_simics_device_example_i2c",
        "get_simics_device_example_ds12887",
        "get_simics_dml_1_4_reference_manual",
        "get_simics_model_builder_user_guide",
        
        # Package management tools
        # "install_simics_package",
        # "uninstall_simics_package",
        
        # Simulation control tools
        # "start_simulation",
        # "stop_simulation", 
        # "pause_simulation",
        # "resume_simulation",
        # "list_simulations",
        # "get_simulation_logs",
        
        # Checkpoint management tools
        # "create_checkpoint",
        # "load_checkpoint"
    ]

    return MCPToolset(
        connection_params=connection_params,
        tool_filter=tool_filter
    )


def create_spec_kit_toolset() -> SpecKitToolset:
    """Create a spec-kit toolset."""
    return SpecKitToolset()