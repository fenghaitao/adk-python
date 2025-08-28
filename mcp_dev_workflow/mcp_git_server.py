#!/usr/bin/env python3
"""
MCP Git Server
Provides git version control operations through MCP protocol
"""

import asyncio
import json
import os
from pathlib import Path
import subprocess
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
server = Server("git-server")

# Get configuration from environment
GIT_TIMEOUT = int(os.getenv("GIT_TIMEOUT", "60"))  # 1 minute default
ALLOWED_OPERATIONS = os.getenv(
    "ALLOWED_OPERATIONS", "init,add,commit,status,log,diff,branch,checkout,push,pull"
).split(",")


def is_operation_allowed(operation: str) -> bool:
    """Check if the git operation is in the allowed list."""
    return operation in ALLOWED_OPERATIONS


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available git tools."""
    return [
        Tool(
            name="git_init",
            description="Initialize a new git repository",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to initialize repository",
                    }
                },
            },
        ),
        Tool(
            name="git_status",
            description="Get git repository status",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    }
                },
            },
        ),
        Tool(
            name="git_add",
            description="Add files to git staging area",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Files to add (use '.' for all)",
                    },
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    },
                },
                "required": ["files"],
            },
        ),
        Tool(
            name="git_commit",
            description="Commit staged changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message"},
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="git_log",
            description="Show git commit history",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_count": {
                        "type": "integer",
                        "description": "Maximum number of commits to show",
                    },
                    "oneline": {
                        "type": "boolean",
                        "description": "Show one line per commit",
                    },
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    },
                },
            },
        ),
        Tool(
            name="git_diff",
            description="Show changes between commits, commit and working tree, etc",
            inputSchema={
                "type": "object",
                "properties": {
                    "staged": {
                        "type": "boolean",
                        "description": "Show staged changes",
                    },
                    "file": {"type": "string", "description": "Specific file to diff"},
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    },
                },
            },
        ),
        Tool(
            name="git_branch",
            description="List, create, or delete branches",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "delete"],
                        "description": "Branch action",
                    },
                    "branch_name": {
                        "type": "string",
                        "description": "Branch name for create/delete actions",
                    },
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    },
                },
            },
        ),
        Tool(
            name="git_checkout",
            description="Switch branches or restore working tree files",
            inputSchema={
                "type": "object",
                "properties": {
                    "branch_or_file": {
                        "type": "string",
                        "description": "Branch name or file path",
                    },
                    "create_branch": {
                        "type": "boolean",
                        "description": "Create new branch",
                    },
                    "path": {
                        "type": "string",
                        "description": "Repository path",
                    },
                },
                "required": ["branch_or_file"],
            },
        ),
    ]


async def run_git_command(cmd: List[str], cwd: str = ".") -> Dict[str, Any]:
    """Run a git command and return the result."""
    try:
        process = await asyncio.create_subprocess_exec(
            "git",
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=GIT_TIMEOUT
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
            "stderr": f"Git command timed out after {GIT_TIMEOUT} seconds",
        }
    except Exception as e:
        return {"returncode": -1, "stdout": "", "stderr": str(e)}


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        path = arguments.get("path", ".")

        if name == "git_init":
            if not is_operation_allowed("init"):
                return [
                    types.TextContent(
                        type="text", text="Error: git init operation not allowed"
                    )
                ]

            result = await run_git_command(["init"], path)

            output = f"Git init in {path}\n"
            output += f"Return code: {result['returncode']}\n"
            if result["stdout"]:
                output += f"Output: {result['stdout']}\n"
            if result["stderr"]:
                output += f"Error: {result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_status":
            if not is_operation_allowed("status"):
                return [
                    types.TextContent(
                        type="text", text="Error: git status operation not allowed"
                    )
                ]

            result = await run_git_command(["status", "--porcelain"], path)

            if result["returncode"] == 0:
                if result["stdout"].strip():
                    output = f"Git status (modified files):\n{result['stdout']}"
                else:
                    output = "Working tree clean"
            else:
                output = f"Error getting git status: {result['stderr']}"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_add":
            if not is_operation_allowed("add"):
                return [
                    types.TextContent(
                        type="text", text="Error: git add operation not allowed"
                    )
                ]

            files = arguments["files"]
            cmd = ["add"] + files
            result = await run_git_command(cmd, path)

            output = f"Git add {' '.join(files)}\n"
            output += f"Return code: {result['returncode']}\n"
            if result["stdout"]:
                output += f"Output: {result['stdout']}\n"
            if result["stderr"]:
                output += f"Error: {result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_commit":
            if not is_operation_allowed("commit"):
                return [
                    types.TextContent(
                        type="text", text="Error: git commit operation not allowed"
                    )
                ]

            message = arguments["message"]
            result = await run_git_command(["commit", "-m", message], path)

            output = f"Git commit with message: '{message}'\n"
            output += f"Return code: {result['returncode']}\n"
            if result["stdout"]:
                output += f"Output: {result['stdout']}\n"
            if result["stderr"]:
                output += f"Error: {result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_log":
            if not is_operation_allowed("log"):
                return [
                    types.TextContent(
                        type="text", text="Error: git log operation not allowed"
                    )
                ]

            max_count = arguments.get("max_count", 10)
            oneline = arguments.get("oneline", True)

            cmd = ["log", f"--max-count={max_count}"]
            if oneline:
                cmd.append("--oneline")

            result = await run_git_command(cmd, path)

            if result["returncode"] == 0:
                output = f"Git log (last {max_count} commits):\n{result['stdout']}"
            else:
                output = f"Error getting git log: {result['stderr']}"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_diff":
            if not is_operation_allowed("diff"):
                return [
                    types.TextContent(
                        type="text", text="Error: git diff operation not allowed"
                    )
                ]

            staged = arguments.get("staged", False)
            file_path = arguments.get("file")

            cmd = ["diff"]
            if staged:
                cmd.append("--staged")
            if file_path:
                cmd.append(file_path)

            result = await run_git_command(cmd, path)

            if result["returncode"] == 0:
                if result["stdout"].strip():
                    output = f"Git diff:\n{result['stdout']}"
                else:
                    output = "No differences found"
            else:
                output = f"Error getting git diff: {result['stderr']}"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_branch":
            if not is_operation_allowed("branch"):
                return [
                    types.TextContent(
                        type="text", text="Error: git branch operation not allowed"
                    )
                ]

            action = arguments.get("action", "list")
            branch_name = arguments.get("branch_name")

            if action == "list":
                cmd = ["branch", "-a"]
            elif action == "create":
                if not branch_name:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: branch_name required for create action",
                        )
                    ]
                cmd = ["branch", branch_name]
            elif action == "delete":
                if not branch_name:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: branch_name required for delete action",
                        )
                    ]
                cmd = ["branch", "-d", branch_name]

            result = await run_git_command(cmd, path)

            output = f"Git branch {action}\n"
            output += f"Return code: {result['returncode']}\n"
            if result["stdout"]:
                output += f"Output: {result['stdout']}\n"
            if result["stderr"]:
                output += f"Error: {result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        elif name == "git_checkout":
            if not is_operation_allowed("checkout"):
                return [
                    types.TextContent(
                        type="text", text="Error: git checkout operation not allowed"
                    )
                ]

            branch_or_file = arguments["branch_or_file"]
            create_branch = arguments.get("create_branch", False)

            cmd = ["checkout"]
            if create_branch:
                cmd.append("-b")
            cmd.append(branch_or_file)

            result = await run_git_command(cmd, path)

            output = f"Git checkout {branch_or_file}\n"
            output += f"Return code: {result['returncode']}\n"
            if result["stdout"]:
                output += f"Output: {result['stdout']}\n"
            if result["stderr"]:
                output += f"Error: {result['stderr']}\n"

            return [types.TextContent(type="text", text=output)]

        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP git server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="git-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
