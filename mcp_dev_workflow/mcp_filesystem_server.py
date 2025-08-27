#!/usr/bin/env python3
"""
MCP Filesystem Server
Provides file system operations through MCP protocol
"""

import asyncio
import json
import os
from pathlib import Path
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
server = Server("filesystem-server")

# Get allowed directories from environment
ALLOWED_DIRECTORIES = os.getenv("ALLOWED_DIRECTORIES", os.getcwd()).split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default


def is_path_allowed(path: str) -> bool:
    """Check if the path is within allowed directories."""
    abs_path = os.path.abspath(path)
    for allowed_dir in ALLOWED_DIRECTORIES:
        if abs_path.startswith(os.path.abspath(allowed_dir)):
            return True
    return False


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available filesystem tools."""
    return [
        Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file",
                    },
                },
                "required": ["path", "content"],
            },
        ),
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to create",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to delete",
                    }
                },
                "required": ["path"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "read_file":
            path = arguments["path"]
            if not is_path_allowed(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Access denied to {path}"
                    )
                ]

            if not os.path.exists(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: File {path} does not exist"
                    )
                ]

            if os.path.getsize(path) > MAX_FILE_SIZE:
                return [
                    types.TextContent(
                        type="text", text=f"Error: File {path} is too large"
                    )
                ]

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return [types.TextContent(type="text", text=content)]

        elif name == "write_file":
            path = arguments["path"]
            content = arguments["content"]

            if not is_path_allowed(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Access denied to {path}"
                    )
                ]

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return [
                types.TextContent(type="text", text=f"Successfully wrote to {path}")
            ]

        elif name == "list_directory":
            path = arguments["path"]
            if not is_path_allowed(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Access denied to {path}"
                    )
                ]

            if not os.path.exists(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Directory {path} does not exist"
                    )
                ]

            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"[DIR] {item}")
                else:
                    size = os.path.getsize(item_path)
                    items.append(f"[FILE] {item} ({size} bytes)")

            return [types.TextContent(type="text", text="\n".join(items))]

        elif name == "create_directory":
            path = arguments["path"]
            if not is_path_allowed(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Access denied to {path}"
                    )
                ]

            os.makedirs(path, exist_ok=True)
            return [
                types.TextContent(
                    type="text", text=f"Successfully created directory {path}"
                )
            ]

        elif name == "delete_file":
            path = arguments["path"]
            if not is_path_allowed(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: Access denied to {path}"
                    )
                ]

            if not os.path.exists(path):
                return [
                    types.TextContent(
                        type="text", text=f"Error: File {path} does not exist"
                    )
                ]

            os.remove(path)
            return [types.TextContent(type="text", text=f"Successfully deleted {path}")]

        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool {name}")]

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP filesystem server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="filesystem-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
