#!/usr/bin/env python3
"""
MCP Server Implementations for Development Workflow
==================================================

This module contains MCP (Model Context Protocol) server implementations
for various development operations including filesystem, build, and git operations.
"""

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class MCPFilesystemServer:
    """MCP server for enhanced filesystem operations."""

    def __init__(
        self, allowed_directories: List[str] = None, max_file_size: str = "10MB"
    ):
        self.allowed_directories = allowed_directories or [os.getcwd()]
        self.max_file_size = self._parse_size(max_file_size)

    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes."""
        size_str = size_str.upper()
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        else:
            return int(size_str)

    def _is_allowed_path(self, path: str) -> bool:
        """Check if path is within allowed directories."""
        abs_path = os.path.abspath(path)
        return any(
            abs_path.startswith(os.path.abspath(allowed))
            for allowed in self.allowed_directories
        )

    async def read_file(
        self, file_path: str, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Read file content with enhanced error handling."""
        try:
            if not self._is_allowed_path(file_path):
                return {"error": f"Access denied to {file_path}"}

            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}

            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                return {"error": f"File too large: {file_size} bytes"}

            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()

            return {
                "content": content,
                "size": file_size,
                "encoding": encoding,
                "path": file_path,
            }
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    async def write_file(
        self, file_path: str, content: str, encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Write file content with validation."""
        try:
            if not self._is_allowed_path(file_path):
                return {"error": f"Access denied to {file_path}"}

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)

            return {
                "success": True,
                "path": file_path,
                "size": len(content.encode(encoding)),
            }
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}

    async def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List directory contents with metadata."""
        try:
            if not self._is_allowed_path(dir_path):
                return {"error": f"Access denied to {dir_path}"}

            if not os.path.exists(dir_path):
                return {"error": f"Directory not found: {dir_path}"}

            items = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                stat = os.stat(item_path)
                items.append(
                    {
                        "name": item,
                        "path": item_path,
                        "type": "directory" if os.path.isdir(item_path) else "file",
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    }
                )

            return {"items": items, "path": dir_path}
        except Exception as e:
            return {"error": f"Error listing directory: {str(e)}"}

    async def create_directory(self, dir_path: str) -> Dict[str, Any]:
        """Create directory with parents."""
        try:
            if not self._is_allowed_path(dir_path):
                return {"error": f"Access denied to {dir_path}"}

            os.makedirs(dir_path, exist_ok=True)
            return {"success": True, "path": dir_path}
        except Exception as e:
            return {"error": f"Error creating directory: {str(e)}"}


class MCPBuildServer:
    """MCP server for build and compilation operations."""

    def __init__(self, build_timeout: int = 300, allowed_commands: List[str] = None):
        self.build_timeout = build_timeout
        self.allowed_commands = allowed_commands or [
            "pip",
            "python",
            "pytest",
            "mypy",
            "black",
            "isort",
            "flake8",
        ]

    def _is_allowed_command(self, command: str) -> bool:
        """Check if command is allowed."""
        return command.split()[0] in self.allowed_commands

    async def run_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Run build command with timeout and validation."""
        try:
            if not self._is_allowed_command(command):
                return {"error": f"Command not allowed: {command}"}

            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.build_timeout
                )

                return {
                    "returncode": process.returncode,
                    "stdout": stdout.decode("utf-8"),
                    "stderr": stderr.decode("utf-8"),
                    "command": command,
                }
            except asyncio.TimeoutError:
                process.kill()
                return {"error": f"Command timed out after {self.build_timeout}s"}

        except Exception as e:
            return {"error": f"Error running command: {str(e)}"}

    async def install_dependencies(
        self, requirements_file: str, cwd: str = None
    ) -> Dict[str, Any]:
        """Install Python dependencies."""
        command = f"pip install -r {requirements_file}"
        return await self.run_command(command, cwd)

    async def run_tests(
        self, test_path: str = "tests", cwd: str = None
    ) -> Dict[str, Any]:
        """Run pytest with coverage."""
        command = f"python -m pytest {test_path} -v --cov=src --cov-report=term-missing"
        return await self.run_command(command, cwd)

    async def check_code_quality(
        self, src_path: str = "src", cwd: str = None
    ) -> Dict[str, Any]:
        """Run code quality checks."""
        results = {}

        # Run mypy
        mypy_result = await self.run_command(f"mypy {src_path}", cwd)
        results["mypy"] = mypy_result

        # Run black check
        black_result = await self.run_command(f"black --check {src_path}", cwd)
        results["black"] = black_result

        # Run isort check
        isort_result = await self.run_command(f"isort --check-only {src_path}", cwd)
        results["isort"] = isort_result

        return results

    async def format_code(
        self, src_path: str = "src", cwd: str = None
    ) -> Dict[str, Any]:
        """Format code using black and isort."""
        results = {}

        # Format with black
        black_result = await self.run_command(f"black {src_path}", cwd)
        results["black"] = black_result

        # Sort imports with isort
        isort_result = await self.run_command(f"isort {src_path}", cwd)
        results["isort"] = isort_result

        return results


class MCPGitServer:
    """MCP server for git version control operations."""

    def __init__(self, git_timeout: int = 60, allowed_operations: List[str] = None):
        self.git_timeout = git_timeout
        self.allowed_operations = allowed_operations or [
            "init",
            "add",
            "commit",
            "status",
            "log",
            "diff",
            "branch",
            "tag",
        ]

    def _is_allowed_operation(self, operation: str) -> bool:
        """Check if git operation is allowed."""
        return operation in self.allowed_operations

    async def run_git_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Run git command with validation."""
        try:
            git_cmd = (
                command.split()[1] if command.startswith("git ") else command.split()[0]
            )
            if not self._is_allowed_operation(git_cmd):
                return {"error": f"Git operation not allowed: {git_cmd}"}

            full_command = (
                f"git {command}" if not command.startswith("git ") else command
            )

            process = await asyncio.create_subprocess_shell(
                full_command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.git_timeout
                )

                return {
                    "returncode": process.returncode,
                    "stdout": stdout.decode("utf-8"),
                    "stderr": stderr.decode("utf-8"),
                    "command": full_command,
                }
            except asyncio.TimeoutError:
                process.kill()
                return {"error": f"Git command timed out after {self.git_timeout}s"}

        except Exception as e:
            return {"error": f"Error running git command: {str(e)}"}

    async def init_repository(self, cwd: str = None) -> Dict[str, Any]:
        """Initialize git repository."""
        return await self.run_git_command("init", cwd)

    async def add_files(self, files: str = ".", cwd: str = None) -> Dict[str, Any]:
        """Add files to git staging."""
        return await self.run_git_command(f"add {files}", cwd)

    async def commit_changes(self, message: str, cwd: str = None) -> Dict[str, Any]:
        """Commit staged changes."""
        # Escape the commit message
        escaped_message = message.replace('"', '\\"')
        return await self.run_git_command(f'commit -m "{escaped_message}"', cwd)

    async def get_status(self, cwd: str = None) -> Dict[str, Any]:
        """Get git repository status."""
        return await self.run_git_command("status --porcelain", cwd)

    async def get_log(self, limit: int = 10, cwd: str = None) -> Dict[str, Any]:
        """Get git commit log."""
        return await self.run_git_command(f"log --oneline -n {limit}", cwd)

    async def create_gitignore(
        self, patterns: List[str], cwd: str = None
    ) -> Dict[str, Any]:
        """Create .gitignore file with common patterns."""
        try:
            gitignore_content = "\n".join(
                [
                    "# Byte-compiled / optimized / DLL files",
                    "__pycache__/",
                    "*.py[cod]",
                    "*$py.class",
                    "",
                    "# Distribution / packaging",
                    ".Python",
                    "build/",
                    "develop-eggs/",
                    "dist/",
                    "downloads/",
                    "eggs/",
                    ".eggs/",
                    "lib/",
                    "lib64/",
                    "parts/",
                    "sdist/",
                    "var/",
                    "wheels/",
                    "*.egg-info/",
                    ".installed.cfg",
                    "*.egg",
                    "",
                    "# PyInstaller",
                    "*.manifest",
                    "*.spec",
                    "",
                    "# Unit test / coverage reports",
                    "htmlcov/",
                    ".tox/",
                    ".coverage",
                    ".coverage.*",
                    ".cache",
                    "nosetests.xml",
                    "coverage.xml",
                    "*.cover",
                    ".hypothesis/",
                    ".pytest_cache/",
                    "",
                    "# Virtual environments",
                    ".env",
                    ".venv",
                    "env/",
                    "venv/",
                    "ENV/",
                    "env.bak/",
                    "venv.bak/",
                    "",
                    "# IDE",
                    ".vscode/",
                    ".idea/",
                    "*.swp",
                    "*.swo",
                    "*~",
                    "",
                    "# OS",
                    ".DS_Store",
                    "Thumbs.db",
                    "",
                    "# Custom patterns",
                ]
                + patterns
            )

            gitignore_path = os.path.join(cwd or ".", ".gitignore")
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)

            return {"success": True, "path": gitignore_path}
        except Exception as e:
            return {"error": f"Error creating .gitignore: {str(e)}"}


# =============================================================================
# MCP SERVER FACTORY AND MANAGEMENT
# =============================================================================


class MCPServerManager:
    """Manages MCP server instances and operations."""

    def __init__(self):
        self.servers = {}

    def create_filesystem_server(self, config: Dict[str, Any]) -> MCPFilesystemServer:
        """Create and register filesystem server."""
        server = MCPFilesystemServer(
            allowed_directories=config.get("allowed_directories", [os.getcwd()]),
            max_file_size=config.get("max_file_size", "10MB"),
        )
        self.servers["filesystem"] = server
        return server

    def create_build_server(self, config: Dict[str, Any]) -> MCPBuildServer:
        """Create and register build server."""
        server = MCPBuildServer(
            build_timeout=int(config.get("build_timeout", 300)),
            allowed_commands=config.get("allowed_commands", "").split(","),
        )
        self.servers["build"] = server
        return server

    def create_git_server(self, config: Dict[str, Any]) -> MCPGitServer:
        """Create and register git server."""
        server = MCPGitServer(
            git_timeout=int(config.get("git_timeout", 60)),
            allowed_operations=config.get("allowed_operations", "").split(","),
        )
        self.servers["git"] = server
        return server

    def get_server(self, server_type: str):
        """Get server instance by type."""
        return self.servers.get(server_type)


# Global server manager instance
mcp_server_manager = MCPServerManager()


# =============================================================================
# MCP TOOL WRAPPER FUNCTIONS
# =============================================================================


async def mcp_read_file(file_path: str) -> str:
    """Read file using MCP filesystem server."""
    server = mcp_server_manager.get_server("filesystem")
    if not server:
        return "Error: Filesystem server not initialized"

    result = await server.read_file(file_path)
    if "error" in result:
        return result["error"]

    return f"Successfully read {result['path']} ({result['size']} bytes):\n{result['content']}"


async def mcp_write_file(file_path: str, content: str) -> str:
    """Write file using MCP filesystem server."""
    server = mcp_server_manager.get_server("filesystem")
    if not server:
        return "Error: Filesystem server not initialized"

    result = await server.write_file(file_path, content)
    if "error" in result:
        return result["error"]

    return f"Successfully wrote {result['size']} bytes to {result['path']}"


async def mcp_run_build_command(command: str, cwd: str = None) -> str:
    """Run build command using MCP build server."""
    server = mcp_server_manager.get_server("build")
    if not server:
        return "Error: Build server not initialized"

    result = await server.run_command(command, cwd)
    if "error" in result:
        return result["error"]

    output = f"Command: {result['command']}\n"
    output += f"Return code: {result['returncode']}\n"
    if result["stdout"]:
        output += f"STDOUT:\n{result['stdout']}\n"
    if result["stderr"]:
        output += f"STDERR:\n{result['stderr']}\n"

    return output


async def mcp_git_operation(operation: str, cwd: str = None) -> str:
    """Perform git operation using MCP git server."""
    server = mcp_server_manager.get_server("git")
    if not server:
        return "Error: Git server not initialized"

    result = await server.run_git_command(operation, cwd)
    if "error" in result:
        return result["error"]

    output = f"Git command: {result['command']}\n"
    output += f"Return code: {result['returncode']}\n"
    if result["stdout"]:
        output += f"Output:\n{result['stdout']}\n"
    if result["stderr"]:
        output += f"Errors:\n{result['stderr']}\n"

    return output
