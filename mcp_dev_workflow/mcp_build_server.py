#!/usr/bin/env python3
"""
MCP Build Server
Provides build and compilation operations through MCP protocol
"""

import asyncio
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from mcp.server import NotificationOptions
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import EmbeddedResource
from mcp.types import ImageContent
from mcp.types import Resource
from mcp.types import TextContent
from mcp.types import Tool
import mcp.types as types

# Initialize the MCP server
server = Server("build-server")

# Get configuration from environment
BUILD_TIMEOUT = int(os.getenv("BUILD_TIMEOUT", "300"))  # 5 minutes default
ALLOWED_COMMANDS = os.getenv(
    "ALLOWED_COMMANDS", "pip,python,pytest,mypy,black,isort"
).split(",")


def is_command_allowed(command: str) -> bool:
    """Check if the command is in the allowed list."""
    return command in ALLOWED_COMMANDS


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available build tools."""
    return [
        Tool(
            name="run_command",
            description="Execute a build command",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"},
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Command arguments",
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for the command",
                        "default": ".",
                    },
                },
                "required": ["command"],
            },
        ),
        Tool(
            name="install_dependencies",
            description="Install Python dependencies from requirements.txt",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements_file": {
                        "type": "string",
                        "description": "Path to requirements file",
                        "default": "requirements.txt",
                    }
                },
            },
        ),
        Tool(
            name="run_tests",
            description="Run pytest tests",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Path to test files or directory",
                        "default": "tests/",
                    },
                    "coverage": {
                        "type": "boolean",
                        "description": "Run with coverage",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="lint_code",
            description="Run code linting with flake8, mypy, black, and isort",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to lint",
                        "default": ".",
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Auto-fix issues where possible",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="build_package",
            description="Build Python package",
            inputSchema={
                "type": "object",
                "properties": {
                    "build_type": {
                        "type": "string",
                        "enum": ["wheel", "sdist", "both"],
                        "description": "Type of build",
                        "default": "wheel",
                    }
                },
            },
        ),
    ]


async def run_subprocess(cmd: List[str], cwd: str = ".") -> Dict[str, Any]:
    """Run a subprocess and return the result."""
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=BUILD_TIMEOUT
        )

        return {
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8"),
            "stderr": stderr.decode("utf-8"),
        }
    except asyncio.TimeoutError:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {BUILD_TIMEOUT} seconds",
        }
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "run_command":
            command = arguments["command"]
            args = arguments.get("args", [])
            working_directory = arguments.get("working_directory", ".")

            if not is_command_allowed(command):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Command '{command}' is not allowed"
                    )
                ]

            cmd = [command] + args
            result = await run_subprocess(cmd, working_directory)

            output = f"Command: {' '.join(cmd)}\n"
            output += f"Return code: {result['returncode']}\n"
            output += f"Working directory: {working_directory}\n\n"

            if result["stdout"]:
                output += f"STDOUT:\n{result['stdout']}\n"
            if result["stderr"]:
                output += f"STDERR:\n{result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "install_dependencies":
            requirements_file = arguments.get("requirements_file", "requirements.txt")

            if not os.path.exists(requirements_file):
                return [
                    types.TextContent(
                        type="text",
                        text=f"Error: Requirements file {requirements_file} not found",
                    )
                ]

            cmd = ["pip", "install", "-r", requirements_file]
            result = await run_subprocess(cmd)

            output = f"Installing dependencies from {requirements_file}\n"
            output += f"Return code: {result['returncode']}\n\n"

            if result["stdout"]:
                output += f"STDOUT:\n{result['stdout']}\n"
            if result["stderr"]:
                output += f"STDERR:\n{result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "run_tests":
            test_path = arguments.get("test_path", "tests/")
            coverage = arguments.get("coverage", False)

            if coverage:
                cmd = [
                    "python",
                    "-m",
                    "pytest",
                    test_path,
                    "--cov=.",
                    "--cov-report=term-missing",
                ]
            else:
                cmd = ["python", "-m", "pytest", test_path, "-v"]

            result = await run_subprocess(cmd)

            output = f"Running tests: {' '.join(cmd)}\n"
            output += f"Return code: {result['returncode']}\n\n"

            if result["stdout"]:
                output += f"STDOUT:\n{result['stdout']}\n"
            if result["stderr"]:
                output += f"STDERR:\n{result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "lint_code":
            path = arguments.get("path", ".")
            fix = arguments.get("fix", False)

            results = []

            # Run black
            if fix:
                black_cmd = ["black", path]
            else:
                black_cmd = ["black", "--check", path]

            black_result = await run_subprocess(black_cmd)
            results.append(
                f"Black formatting:\nReturn code: {black_result['returncode']}\n{black_result['stdout']}\n{black_result['stderr']}\n"
            )

            # Run isort
            if fix:
                isort_cmd = ["isort", path]
            else:
                isort_cmd = ["isort", "--check-only", path]

            isort_result = await run_subprocess(isort_cmd)
            results.append(
                f"Isort imports:\nReturn code: {isort_result['returncode']}\n{isort_result['stdout']}\n{isort_result['stderr']}\n"
            )

            # Run flake8
            flake8_cmd = ["flake8", path]
            flake8_result = await run_subprocess(flake8_cmd)
            results.append(
                f"Flake8 linting:\nReturn code: {flake8_result['returncode']}\n{flake8_result['stdout']}\n{flake8_result['stderr']}\n"
            )

            # Run mypy
            mypy_cmd = ["mypy", path]
            mypy_result = await run_subprocess(mypy_cmd)
            results.append(
                f"MyPy type checking:\nReturn code: {mypy_result['returncode']}\n{mypy_result['stdout']}\n{mypy_result['stderr']}\n"
            )

            return [types.TextContent(type="text", text="\n".join(results))]

        elif name == "build_package":
            build_type = arguments.get("build_type", "wheel")

            if build_type == "wheel":
                cmd = ["python", "-m", "build", "--wheel"]
            elif build_type == "sdist":
                cmd = ["python", "-m", "build", "--sdist"]
            else:  # both
                cmd = ["python", "-m", "build"]

            result = await run_subprocess(cmd)

            output = f"Building package: {' '.join(cmd)}\n"
            output += f"Return code: {result['returncode']}\n\n"

            if result["stdout"]:
                output += f"STDOUT:\n{result['stdout']}\n"
            if result["stderr"]:
                output += f"STDERR:\n{result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP build server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="build-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
