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
    from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, SseConnectionParams
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
        from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, SseConnectionParams
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
            description=(
                "Write content to a file. BEHAVIOR: "
                "If file exists and overwrite=False (default), content will be APPENDED to the file. "
                "If overwrite=True, the ENTIRE file will be REPLACED. "
                "Use append mode (overwrite=False) to ADD new code. "
                "Use overwrite mode only when you want to REPLACE the complete file content. "
                "⚠️ WARNING: overwrite=True will DELETE all existing content!"
            ),
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="write_file",
                description=(
                    "Write content to a file. BEHAVIOR: "
                    "If file exists and overwrite=False (default), content will be APPENDED to the file. "
                    "If overwrite=True, the ENTIRE file will be REPLACED with the provided content. "
                    "Use append mode (overwrite=False) to ADD new code. "
                    "Use overwrite mode only when you want to REPLACE the complete file. "
                    "⚠️ WARNING: overwrite=True will DELETE all existing content!"
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="Path to the file to write"
                        ),
                        "content": types.Schema(
                            type=types.Type.STRING,
                            description="Content to write. In append mode (overwrite=False), this is added to the end. In overwrite mode (overwrite=True), this REPLACES all existing content."
                        ),
                        "overwrite": types.Schema(
                            type=types.Type.BOOLEAN,
                            description=(
                                "False (default): APPEND content to end of file if it exists. "
                                "True: REPLACE entire file content (⚠️ DELETES existing content). "
                                "Only use True when you have the COMPLETE file content to write."
                            )
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
            file_exists = os.path.exists(file_path)
            
            # Get original file size for validation
            original_size = 0
            if file_exists:
                original_size = os.path.getsize(file_path)
            
            # Create directory if it doesn't exist
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            # IMPROVED LOGIC: If file exists and overwrite=False, APPEND instead of error
            if file_exists and not overwrite:
                # APPEND mode - add content to end of file
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(content)
                new_size = os.path.getsize(file_path)
                return {
                    "success": True, 
                    "file_path": file_path, 
                    "mode": "append",
                    "bytes_written": len(content),
                    "original_size": original_size,
                    "new_size": new_size
                }
            else:
                # OVERWRITE mode - replace entire file
                # Add safety check: warn if file is being significantly reduced
                new_content_size = len(content.encode('utf-8'))
                
                if file_exists and original_size > 0:
                    size_reduction_pct = ((original_size - new_content_size) / original_size) * 100
                    
                    # Create backup if file is shrinking by more than 50%
                    if size_reduction_pct > 50:
                        from datetime import datetime
                        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        import shutil
                        shutil.copy2(file_path, backup_path)
                        
                        warning_msg = (
                            f"⚠️ WARNING: File size reduction detected!\n"
                            f"  Original: {original_size} bytes\n"
                            f"  New: {new_content_size} bytes\n"
                            f"  Reduction: {size_reduction_pct:.1f}%\n"
                            f"  Backup saved: {backup_path}\n"
                            f"  This may be unintentional code deletion!"
                        )
                        print(warning_msg)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                
                new_size = os.path.getsize(file_path)
                return {
                    "success": True, 
                    "file_path": file_path,
                    "mode": "overwrite" if file_exists else "create",
                    "bytes_written": new_content_size,
                    "original_size": original_size if file_exists else 0,
                    "new_size": new_size,
                    "backup_created": file_exists and original_size > 0 and ((original_size - new_content_size) / original_size * 100) > 50
                }
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}


class SpecKitFileReplaceTool(BaseTool):
    """Tool for replacing exact strings in files with context validation."""

    def __init__(self):
        super().__init__(
            name="replace_string_in_file",
            description="Replace an exact string in a file with a new string. Use this for precise edits like marking tasks complete or updating specific text. Requires exact match with context.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="replace_string_in_file",
                description="Replace an exact string in a file with a new string. Use this for precise edits like marking tasks complete or updating specific text. Requires exact match with context.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="Absolute path to the file to edit"
                        ),
                        "old_string": types.Schema(
                            type=types.Type.STRING,
                            description="Exact string to find and replace. Include 3-5 lines of context before/after to make match unique."
                        ),
                        "new_string": types.Schema(
                            type=types.Type.STRING,
                            description="String to replace old_string with"
                        ),
                        "expected_replacements": types.Schema(
                            type=types.Type.INTEGER,
                            description="Number of expected replacements (default: 1). Tool will error if actual count differs."
                        )
                    },
                    required=["file_path", "old_string", "new_string"]
                )
            )
        except ImportError:
            return None

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        file_path = args.get("file_path")
        old_string = args.get("old_string")
        new_string = args.get("new_string")
        expected_replacements = args.get("expected_replacements", 1)

        if not file_path or old_string is None or new_string is None:
            return {"error": "file_path, old_string, and new_string are required"}

        # Validate file exists
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {"error": f"File not found: {file_path}"}

        if not file_path_obj.is_file():
            return {"error": f"Path is not a file: {file_path}"}

        # Read file content
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return {"error": f"File is not a valid UTF-8 text file: {file_path}"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

        # Check if old_string exists
        if old_string not in content:
            return {
                "error": f"String not found in file.\nLooking for: {repr(old_string[:200])}\nFile: {file_path}"
            }

        # Count occurrences
        occurrences = content.count(old_string)

        # Validate expected replacements
        if expected_replacements == 1 and occurrences > 1:
            return {
                "error": f"Found {occurrences} occurrences of the string, but expected only 1.\n"
                        f"String: {repr(old_string[:200])}\n"
                        f"File: {file_path}\n"
                        f"Tip: Include more context (3-5 lines before/after) to make the match unique."
            }

        if expected_replacements > 0 and occurrences != expected_replacements:
            return {
                "error": f"Found {occurrences} occurrences, but expected {expected_replacements}.\n"
                        f"String: {repr(old_string[:200])}\n"
                        f"File: {file_path}"
            }

        # Perform replacement
        new_content = content.replace(old_string, new_string, expected_replacements)

        # Write back to file
        try:
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}

        # Success response
        return {
            "success": True,
            "file_path": file_path,
            "replacements": occurrences,
            "old_string_preview": old_string[:100] + ('...' if len(old_string) > 100 else ''),
            "new_string_preview": new_string[:100] + ('...' if len(new_string) > 100 else ''),
            "message": f"Successfully replaced {occurrences} occurrence(s) in {file_path}"
        }


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


class SpecKitApplyGitDiffTool(BaseTool):
    """Tool for applying a git diff from JSON format."""

    def __init__(self):
        super().__init__(
            name="apply_git_diff",
            description="Apply a git diff patch from JSON format containing file changes.",
        )

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="apply_git_diff",
                description="Apply a git diff patch from JSON format containing file changes.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "diff_json": types.Schema(
                            type=types.Type.STRING,
                            description="JSON string containing the diff with format: {\"files\": [{\"path\": \"file/path\", \"diff\": \"diff content\"}]}"
                        ),
                        "working_directory": types.Schema(
                            type=types.Type.STRING,
                            description="Directory to apply the diff in (default: '.')"
                        ),
                        "dry_run": types.Schema(
                            type=types.Type.BOOLEAN,
                            description="If true, only check if the patch would apply cleanly without actually applying it (default: False)"
                        )
                    },
                    required=["diff_json"]
                )
            )
        except ImportError:
            return None

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        diff_json_str = args.get("diff_json")
        working_directory = args.get("working_directory", ".")
        dry_run = args.get("dry_run", False)

        if not diff_json_str:
            return {"error": "diff_json is required"}

        try:
            # Parse JSON
            diff_data = json.loads(diff_json_str)
            
            if not isinstance(diff_data, dict) or "files" not in diff_data:
                return {"error": "Invalid JSON format. Expected: {\"files\": [{\"path\": \"...\", \"diff\": \"...\"}]}"}
            
            files = diff_data["files"]
            if not isinstance(files, list):
                return {"error": "Invalid JSON format. 'files' must be a list"}
            
            # Process each file
            results = []
            errors = []
            
            for file_entry in files:
                if not isinstance(file_entry, dict):
                    errors.append({"error": "Invalid file entry format", "entry": file_entry})
                    continue
                
                file_path = file_entry.get("path")
                diff_content = file_entry.get("diff")
                
                if not file_path or not diff_content:
                    errors.append({"error": "Missing 'path' or 'diff' in file entry", "entry": file_entry})
                    continue
                
                # Create a temporary patch file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as patch_file:
                    patch_file.write(diff_content)
                    patch_file_path = patch_file.name
                
                try:
                    # Apply the patch using git apply
                    cmd_parts = ["git", "apply"]
                    
                    if dry_run:
                        cmd_parts.append("--check")
                    
                    cmd_parts.append(patch_file_path)
                    
                    result = subprocess.run(
                        cmd_parts,
                        cwd=working_directory,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        results.append({
                            "file": file_path,
                            "status": "success" if not dry_run else "would_apply",
                            "message": "Patch applied successfully" if not dry_run else "Patch would apply cleanly"
                        })
                    else:
                        errors.append({
                            "file": file_path,
                            "status": "failed",
                            "error": result.stderr,
                            "stdout": result.stdout
                        })
                
                finally:
                    # Clean up temporary patch file
                    try:
                        os.unlink(patch_file_path)
                    except:
                        pass
            
            # Return results
            response = {
                "success": len(errors) == 0,
                "dry_run": dry_run,
                "working_directory": working_directory,
                "files_processed": len(files),
                "files_succeeded": len(results),
                "files_failed": len(errors),
                "results": results
            }
            
            if errors:
                response["errors"] = errors
            
            return response
            
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format: {str(e)}"}
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"error": f"Error applying diff: {str(e)}"}


class SpecKitToolset(BaseToolset):
    """Toolset for spec-kit commands using basic file and bash tools."""

    def __init__(self):
        super().__init__()
        self.name = "spec_kit_toolset"
        self.tools = [
            SpecKitReadTool(),
            SpecKitWriteTool(),
            SpecKitFileReplaceTool(),
            SpecKitBashTool(),
            SpecKitApplyGitDiffTool()
        ]

    async def get_tools(self, readonly_context=None):
        """Return all tools in this toolset."""
        return self.tools


def create_simics_mcp_toolset(port: Optional[int] = None) -> MCPToolset:
    """Create a MCP toolset that connects to the simics-mcp-server with content truncation.

    Args:
        port: MCP server port. If not provided, reads from MCP_PORT environment variable
              or defaults to 8051.
    """
    # Get port from parameter, environment variable, or default
    if port is None:
        port = int(os.environ.get('MCP_PORT', '8051'))

    print(f"Creating Simics MCP toolset connecting to port {port}...")
    connection_params = SseConnectionParams(
        url=f"http://127.0.0.1:{port}/sse",
        headers={"Accept": "text/event-stream"},
        timeout=10.0,
        sse_read_timeout=300.0
    )

    # Filter for specific Simics tools we want to expose
    tool_filter = [
        # Core project management tools
        "list_installed_packages",
        "list_simics_platforms",
        "get_simics_version",

        # Device modeling and development tools
        "create_simics_project",
        # "add_dml_device_skeleton",
        "checkout_and_build_dmlc",
        "check_with_dmlc",
        "build_simics_project",
        "run_simics_test",
        "generate_dml_registers",

        # RAG query tool for documentation and source code search
        "perform_rag_query",

        # Device examples and documentation tools - FILTERED OUT (too large, cause token limit issues)
        # "get_simics_device_example_i2c",
        # "get_simics_device_example_ds12887",
        # "get_simics_dml_1_4_reference_manual",
        # "get_simics_model_builder_user_guide",
        # "get_simics_dml_template",

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
