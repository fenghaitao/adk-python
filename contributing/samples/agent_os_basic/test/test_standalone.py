#!/usr/bin/env python3
"""Standalone test for Agent OS integration components."""

import os
import tempfile
import subprocess
from pathlib import Path

def test_agent_os_tools_standalone():
    """Test Agent OS tools without ADK dependencies."""
    print("Testing Agent OS Tools (Standalone)...")
    
    try:
        # Import only the tools module
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "python"))
        
        from agent_os_tools import (
            AgentOsReadTool, 
            AgentOsWriteTool, 
            AgentOsGrepTool, 
            AgentOsGlobTool, 
            AgentOsBashTool,
            create_agent_os_toolset
        )
        
        # Test individual tools
        tools = [
            AgentOsReadTool(),
            AgentOsWriteTool(),
            AgentOsGrepTool(),
            AgentOsGlobTool(),
            AgentOsBashTool(),
        ]
        
        for tool in tools:
            print(f"✓ Created tool: {tool.name}")
        
        # Test toolset
        toolset = create_agent_os_toolset()
        print(f"✓ Created toolset with {len(toolset.tools)} tools")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_file_operations():
    """Test file operations directly."""
    print("\nTesting File Operations...")
    
    try:
        try:
            from .agent_os_tools import AgentOsReadTool, AgentOsWriteTool
        except ImportError:
            from agent_os_tools import AgentOsReadTool, AgentOsWriteTool
        
        read_tool = AgentOsReadTool()
        write_tool = AgentOsWriteTool()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_content = "Hello, Agent OS!"
            
            # Test write
            class MockToolContext:
                pass
            
            write_result = write_tool.run_async(
                args={
                    "file_path": str(test_file),
                    "content": test_content,
                    "overwrite": False
                },
                tool_context=MockToolContext()
            )
            
            if hasattr(write_result, '__await__'):
                import asyncio
                write_result = asyncio.run(write_result)
            
            print(f"✓ Write result: {write_result}")
            
            # Test read
            read_result = read_tool.run_async(
                args={"file_path": str(test_file)},
                tool_context=MockToolContext()
            )
            
            if hasattr(read_result, '__await__'):
                import asyncio
                read_result = asyncio.run(read_result)
            
            print(f"✓ Read result: {read_result}")
            
            if "content" in read_result and read_result["content"] == test_content:
                print("✓ File operations work correctly")
                return True
            else:
                print("✗ File content mismatch")
                return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_grep_operations():
    """Test grep operations."""
    print("\nTesting Grep Operations...")
    
    try:
        try:
            from .agent_os_tools import AgentOsGrepTool
        except ImportError:
            from agent_os_tools import AgentOsGrepTool
        
        grep_tool = AgentOsGrepTool()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("Hello, World!\nThis is a test.\nAnother line.")
            
            class MockToolContext:
                pass
            
            grep_result = grep_tool.run_async(
                args={
                    "pattern": "test",
                    "file_path": str(test_file),
                    "case_sensitive": False
                },
                tool_context=MockToolContext()
            )
            
            if hasattr(grep_result, '__await__'):
                import asyncio
                grep_result = asyncio.run(grep_result)
            
            print(f"✓ Grep result: {grep_result}")
            
            if "matches" in grep_result and len(grep_result["matches"]) > 0:
                print("✓ Grep operations work correctly")
                return True
            else:
                print("✗ No matches found")
                return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_glob_operations():
    """Test glob operations."""
    print("\nTesting Glob Operations...")
    
    try:
        try:
            from .agent_os_tools import AgentOsGlobTool
        except ImportError:
            from agent_os_tools import AgentOsGlobTool
        
        glob_tool = AgentOsGlobTool()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "test1.txt").touch()
            (Path(temp_dir) / "test2.txt").touch()
            (Path(temp_dir) / "other.py").touch()
            
            class MockToolContext:
                pass
            
            glob_result = glob_tool.run_async(
                args={
                    "pattern": "*.txt",
                    "directory": temp_dir
                },
                tool_context=MockToolContext()
            )
            
            if hasattr(glob_result, '__await__'):
                import asyncio
                glob_result = asyncio.run(glob_result)
            
            print(f"✓ Glob result: {glob_result}")
            
            if "files" in glob_result and len(glob_result["files"]) == 2:
                print("✓ Glob operations work correctly")
                return True
            else:
                print("✗ Unexpected file count")
                return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_bash_operations():
    """Test bash operations."""
    print("\nTesting Bash Operations...")
    
    try:
        try:
            from .agent_os_tools import AgentOsBashTool
        except ImportError:
            from agent_os_tools import AgentOsBashTool
        
        bash_tool = AgentOsBashTool()
        
        class MockToolContext:
            pass
        
        bash_result = bash_tool.run_async(
            args={
                "command": "echo 'Hello, Agent OS!'",
                "working_directory": ".",
                "timeout": 10
            },
            tool_context=MockToolContext()
        )
        
        if hasattr(bash_result, '__await__'):
            import asyncio
            bash_result = asyncio.run(bash_result)
        
        print(f"✓ Bash result: {bash_result}")
        
        if "stdout" in bash_result and "Hello, Agent OS!" in bash_result["stdout"]:
            print("✓ Bash operations work correctly")
            return True
        else:
            print("✗ Unexpected bash output")
            return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("🤖 Agent OS Integration Test (Standalone)")
    print("=" * 50)
    
    tests = [
        test_agent_os_tools_standalone,
        test_file_operations,
        test_grep_operations,
        test_glob_operations,
        test_bash_operations,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
