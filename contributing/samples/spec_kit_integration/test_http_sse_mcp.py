#!/usr/bin/env python3
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

"""Test script for HTTP SSE MCP server integration."""

import asyncio
import sys
from pathlib import Path

# Add ADK to path if needed
current_dir = Path(__file__).parent
adk_src_dir = current_dir.parent.parent.parent / "src"
if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))

from spec_kit_tools import create_http_sse_mcp_toolset


async def test_http_sse_mcp_connection():
    """Test connecting to the HTTP SSE MCP server."""
    print("Testing HTTP SSE MCP server connection...")
    
    try:
        # Create the toolset
        toolset = create_http_sse_mcp_toolset()
        print("✓ Created HTTP SSE MCP toolset")
        
        # Try to get tools from the server
        print("Attempting to connect to http://127.0.0.1:8051/sse...")
        tools = await toolset.get_tools()
        
        print(f"✓ Successfully connected! Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Test tool execution if available
        if tools:
            first_tool = tools[0]
            print(f"\nTesting tool: {first_tool.name}")
            # Note: We would need to know the expected parameters for the tool
            # This is just a connection test
        
        # Clean up
        await toolset.close()
        print("✓ Connection closed successfully")
        
        return True
        
    except ConnectionError as e:
        print(f"✗ Connection failed: {e}")
        print("Make sure the HTTP SSE MCP server is running on http://127.0.0.1:8051/sse")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_mcp_servers():
    """Test using multiple MCP servers simultaneously."""
    print("\nTesting multiple MCP servers...")
    
    from spec_kit_tools import create_simics_mcp_toolset, create_spec_kit_toolset
    
    toolsets = []
    
    # Add spec-kit toolset
    spec_toolset = create_spec_kit_toolset()
    toolsets.append(("Spec-Kit", spec_toolset))
    
    # Try Simics MCP
    try:
        simics_toolset = create_simics_mcp_toolset()
        toolsets.append(("Simics MCP", simics_toolset))
    except Exception as e:
        print(f"Simics MCP not available: {e}")
    
    # Try HTTP SSE MCP
    try:
        http_sse_toolset = create_http_sse_mcp_toolset()
        toolsets.append(("HTTP SSE MCP", http_sse_toolset))
    except Exception as e:
        print(f"HTTP SSE MCP not available: {e}")
    
    print(f"Testing {len(toolsets)} toolsets:")
    
    total_tools = 0
    for name, toolset in toolsets:
        try:
            tools = await toolset.get_tools()
            print(f"  ✓ {name}: {len(tools)} tools")
            total_tools += len(tools)
            
            # Clean up MCP toolsets
            if hasattr(toolset, 'close'):
                await toolset.close()
                
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    print(f"\nTotal tools available: {total_tools}")
    return total_tools > 0


async def main():
    """Main test function."""
    print("HTTP SSE MCP Integration Test")
    print("=" * 40)
    
    # Test individual HTTP SSE connection
    http_sse_success = await test_http_sse_mcp_connection()
    
    # Test multiple servers
    multi_success = await test_multiple_mcp_servers()
    
    print("\n" + "=" * 40)
    if http_sse_success:
        print("✓ HTTP SSE MCP server integration working!")
    else:
        print("✗ HTTP SSE MCP server not accessible")
        print("\nTo start the server, run:")
        print("  # Make sure the MCP server is running on http://127.0.0.1:8051/sse")
    
    if multi_success:
        print("✓ Multiple MCP server integration working!")
    else:
        print("✗ Issues with multiple MCP server setup")


if __name__ == "__main__":
    asyncio.run(main())