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

"""Agent OS tools integration for ADK."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import ADK tools - use more robust import method
try:
    # Try direct import first (when ADK is properly installed)
    from google.adk.tools.base_tool import BaseTool
    from google.adk.tools.base_toolset import BaseToolset
    from google.adk.tools.tool_context import ToolContext
except ImportError:
    # Fallback: Add src directory only if direct import fails
    import sys
    from pathlib import Path as PathLib
    
    # Find ADK source directory relative to this file
    current_dir = PathLib(__file__).parent
    adk_src_dir = current_dir.parent.parent.parent / "src"
    
    if adk_src_dir.exists():
        sys.path.insert(0, str(adk_src_dir))
        try:
            from google.adk.tools.base_tool import BaseTool
            from google.adk.tools.base_toolset import BaseToolset
            from google.adk.tools.tool_context import ToolContext
        except ImportError as e:
            raise ImportError(
                f"Could not import ADK tools. Please ensure ADK is installed or "
                f"PYTHONPATH includes the ADK source directory. Error: {e}"
            ) from e
    else:
        raise ImportError(
            f"ADK source directory not found at {adk_src_dir}. "
            f"Please ensure ADK is installed or set PYTHONPATH correctly."
        )


class AgentOsReadTool(BaseTool):
    """Tool for reading files in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read the contents of a file. Use this to examine files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
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


class AgentOsWriteTool(BaseTool):
    """Tool for writing files in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a file. Use this to create or update files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
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


class AgentOsGrepTool(BaseTool):
    """Tool for searching files using grep in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="grep_search",
            description="Search for patterns in files using grep. Use this to find specific content across files.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="grep_search",
            description="Search for patterns in files using grep. Use this to find specific content across files.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "pattern": types.Schema(
                        type=types.Type.STRING,
                        description="Pattern to search for"
                    ),
                    "file_path": types.Schema(
                        type=types.Type.STRING,
                        description="File or directory to search in (default: '.')"
                    ),
                    "case_sensitive": types.Schema(
                        type=types.Type.BOOLEAN,
                        description="Whether search is case sensitive (default: False)"
                    ),
                    "max_lines": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of result lines to return (default: 50)"
                    )
                },
                required=["pattern"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        pattern = args.get("pattern")
        file_path = args.get("file_path", ".")
        case_sensitive = args.get("case_sensitive", False)
        max_lines = args.get("max_lines", 50)

        if not pattern:
            return {"error": "pattern is required"}

        try:
            cmd = ["grep", "-n"]
            if not case_sensitive:
                cmd.append("-i")
            cmd.extend([pattern, file_path])

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            if lines and lines[0] == "":
                lines = lines[1:]
            
            # Limit results
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                truncated = True
            else:
                truncated = False

            return {
                "matches": lines,
                "pattern": pattern,
                "file_path": file_path,
                "total_matches": len(lines),
                "truncated": truncated,
            }
        except subprocess.TimeoutExpired:
            return {"error": "Search timed out"}
        except Exception as e:
            return {"error": f"Error searching: {str(e)}"}


class AgentOsGlobTool(BaseTool):
    """Tool for finding files using glob patterns in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="glob_search",
            description="Find files matching a glob pattern. Use this to discover files in the project.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="glob_search",
            description="Find files matching a glob pattern. Use this to discover files in the project.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "pattern": types.Schema(
                        type=types.Type.STRING,
                        description="Glob pattern to match files (e.g., '*.py', '**/*.md')"
                    ),
                    "directory": types.Schema(
                        type=types.Type.STRING,
                        description="Directory to search in (default: '.')"
                    ),
                    "max_files": types.Schema(
                        type=types.Type.INTEGER,
                        description="Maximum number of files to return (default: 100)"
                    )
                },
                required=["pattern"]
            )
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        pattern = args.get("pattern")
        directory = args.get("directory", ".")
        max_files = args.get("max_files", 100)

        if not pattern:
            return {"error": "pattern is required"}

        try:
            from glob import glob
            
            search_path = os.path.join(directory, pattern)
            files = glob(search_path, recursive=True)
            
            # Limit results
            if len(files) > max_files:
                files = files[:max_files]
                truncated = True
            else:
                truncated = False

            return {
                "files": files,
                "pattern": pattern,
                "directory": directory,
                "total_files": len(files),
                "truncated": truncated,
            }
        except Exception as e:
            return {"error": f"Error searching files: {str(e)}"}


class AgentOsBashTool(BaseTool):
    """Tool for executing bash commands in Agent OS workflows."""

    def __init__(self):
        super().__init__(
            name="bash_command",
            description="Execute bash commands. Use this to run shell commands, git operations, and other system tasks.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        from google.genai import types
        return types.FunctionDeclaration(
            name="bash_command",
            description="Execute bash commands. Use this to run shell commands, git operations, and other system tasks.",
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


class AgentOsToolset(BaseToolset):
    """Toolset containing all Agent OS tools."""

    def __init__(self):
        super().__init__()
        self.tools = [
            AgentOsReadTool(),
            AgentOsWriteTool(),
            AgentOsGrepTool(),
            AgentOsGlobTool(),
            AgentOsBashTool(),
        ]

    async def get_tools(self, readonly_context=None) -> List[BaseTool]:
        """Return all tools in this toolset."""
        return self.tools

    @classmethod
    def from_config(cls, config, config_abs_path: str):
        """Create an AgentOsToolset from configuration.
        
        Args:
            config: The configuration object (unused for this simple toolset)
            config_abs_path: Absolute path to the config file (unused)
            
        Returns:
            AgentOsToolset: A new instance of the toolset
        """
        return cls()


# Convenience function to create the toolset
def create_agent_os_toolset() -> AgentOsToolset:
    """Create an Agent OS toolset with all available tools."""
    return AgentOsToolset()
