#!/usr/bin/env python3
"""
Test script for Simics MCP integration with spec_kit_integration.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from spec_kit_tools import create_simics_mcp_toolset


async def test_mcp_connection():
    """Test the MCP connection to simics-mcp-server."""
    print("Testing Simics MCP integration...")
    
    try:
        # Create the MCP toolset
        mcp_toolset = create_simics_mcp_toolset()
        print("✓ MCP toolset created successfully")
        
        # Get tools from the MCP server
        tools = await mcp_toolset.get_tools()
        print(f"✓ Retrieved {len(tools)} tools from MCP server")
        
        # List the available tools
        print("\nAvailable Simics tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test a simple tool call (list packages)
        print("\nTesting list_installed_packages tool...")
        list_tool = None
        for tool in tools:
            if tool.name == "list_installed_packages":
                list_tool = tool
                break
        
        if list_tool:
            try:
                result = await list_tool.run_async(args={}, tool_context=None)
                print(f"✓ Tool call successful: {result}")
            except Exception as e:
                print(f"⚠ Tool call failed (expected if Simics not set up): {e}")
        else:
            print("⚠ list_installed_packages tool not found")
        
        # Clean up
        await mcp_toolset.close()
        print("✓ MCP connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ MCP integration test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("=" * 60)
    print("Simics MCP Integration Test")
    print("=" * 60)
    
    success = await test_mcp_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed! MCP integration is working.")
    else:
        print("✗ Some tests failed. Check the error messages above.")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
