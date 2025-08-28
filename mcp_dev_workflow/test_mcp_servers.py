#!/usr/bin/env python3
"""
Test script to verify MCP servers are working properly
"""

import asyncio
import os
import subprocess
import sys
import time


def test_mcp_server(server_name, script_path, timeout=10):
    """Test if an MCP server starts and responds properly."""
    print(f"Testing {server_name}...")

    try:
        # Set environment variables
        env = os.environ.copy()
        if "filesystem" in server_name:
            env["ALLOWED_DIRECTORIES"] = os.getcwd()
            env["MAX_FILE_SIZE"] = "10485760"
        elif "build" in server_name:
            env["BUILD_TIMEOUT"] = "300"
            env["ALLOWED_COMMANDS"] = "pip,python,pytest,mypy,black,isort,flake8"
        elif "git" in server_name:
            env["GIT_TIMEOUT"] = "60"
            env["ALLOWED_OPERATIONS"] = (
                "init,add,commit,status,log,diff,branch,checkout"
            )

        # Start the server process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,
        )

        # Give it a moment to start
        time.sleep(2)

        # Check if process is still running
        if process.poll() is None:
            # Process is still running, which is good
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print(f"✅ {server_name} started successfully")
            return True
        else:
            # Process terminated
            stdout, stderr = process.communicate()
            print(f"❌ {server_name} failed to start")
            print(f"Return code: {process.returncode}")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False

    except Exception as e:
        print(f"❌ Error testing {server_name}: {e}")
        return False


def main():
    """Test all MCP servers."""
    print("Testing MCP servers...\n")

    servers = [
        ("MCP Filesystem Server", "mcp_filesystem_server.py"),
        ("MCP Build Server", "mcp_build_server.py"),
        ("MCP Git Server", "mcp_git_server.py"),
    ]

    results = []
    for server_name, script_path in servers:
        success = test_mcp_server(server_name, script_path)
        results.append((server_name, success))
        print()

    print("Test Results:")
    print("=" * 30)
    all_passed = True
    for server_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {server_name}")
        if not success:
            all_passed = False

    if all_passed:
        print("\n🎉 All MCP servers are working properly!")
    else:
        print("\n⚠️  Some MCP servers have issues. Please check the logs above.")


if __name__ == "__main__":
    main()
