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

import asyncio
import os
from pathlib import Path
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: MCP library not installed. Please install with: pip install mcp")
    sys.exit(1)

# Create an MCP server with a name
mcp = FastMCP("Filesystem Server", host="localhost", port=3000)

# Get the allowed directory (current directory for this sample)
ALLOWED_PATH = os.path.dirname(os.path.abspath(__file__))


def _is_path_allowed(filepath: str) -> bool:
    """Check if the file path is within the allowed directory."""
    abs_filepath = os.path.abspath(filepath)
    return abs_filepath.startswith(ALLOWED_PATH)


@mcp.tool(description="Read contents of a file")
def read_file(filepath: str) -> str:
    """Read and return the contents of a file.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        Contents of the file as a string
    """
    if not _is_path_allowed(filepath):
        raise ValueError(f"Access denied: {filepath} is outside allowed directory {ALLOWED_PATH}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {filepath}")


@mcp.tool(description="List contents of a directory")
def list_directory(dirpath: str = ".") -> list:
    """List all files and directories in the given directory.
    
    Args:
        dirpath: Path to the directory to list (defaults to current directory)
        
    Returns:
        List of filenames and directory names
    """
    if not _is_path_allowed(dirpath):
        raise ValueError(f"Access denied: {dirpath} is outside allowed directory {ALLOWED_PATH}")
    
    try:
        return os.listdir(dirpath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Directory not found: {dirpath}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {dirpath}")


@mcp.tool(description="Write content to a file")
def write_file(filepath: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        filepath: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success message
    """
    if not _is_path_allowed(filepath):
        raise ValueError(f"Access denied: {filepath} is outside allowed directory {ALLOWED_PATH}")
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except PermissionError:
        raise PermissionError(f"Permission denied: {filepath}")


@mcp.tool(description="Get current working directory")
def get_cwd() -> str:
    """Return the current working directory."""
    return str(Path.cwd())


@mcp.tool(description="Get allowed directory for file operations")
def list_allowed_directories() -> str:
    """Return the allowed directory for file operations."""
    return f"Allowed directory: {ALLOWED_PATH}"


# Main entry point
if __name__ == "__main__":
    try:
        print(f"Starting Filesystem MCP Server...")
        print(f"Allowed directory: {ALLOWED_PATH}")
        print("Server will be available at http://localhost:3000/sse")
        print("Press Ctrl+C to stop the server")
        
        # The MCP run function ultimately uses asyncio.run() internally
        mcp.run(transport="sse")
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully...")
        print("Server has been shut down.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        print("Thank you for using the Filesystem MCP Server!")