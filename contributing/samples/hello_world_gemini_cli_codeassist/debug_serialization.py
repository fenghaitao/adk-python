#!/usr/bin/env python3
"""Debug script to understand JSON serialization issues."""

import json
from agent import root_agent
from google.adk.models.gemini_cli_codeassist import _to_jsonish


def debug_tools():
    """Debug the tool serialization."""
    print("Debugging tool serialization...")
    
    # Get the tools from the agent
    tools = root_agent.tools
    print(f"Number of tools: {len(tools)}")
    
    for i, tool in enumerate(tools):
        print(f"\nTool {i}: {type(tool)}")
        print(f"Tool name: {getattr(tool, 'name', 'N/A')}")
        
        # Try to convert to JSON
        try:
            json_tool = _to_jsonish(tool)
            print(f"Conversion successful: {type(json_tool)}")
            
            # Try to serialize with json.dumps
            json_str = json.dumps(json_tool)
            print(f"JSON serialization successful, length: {len(json_str)}")
            
        except Exception as e:
            print(f"Error converting tool: {e}")
            print(f"Tool attributes: {dir(tool)}")
            
            # Try to find problematic attributes
            if hasattr(tool, '__dict__'):
                for attr_name, attr_value in tool.__dict__.items():
                    try:
                        json.dumps(attr_value)
                    except Exception as attr_error:
                        print(f"  Problematic attribute {attr_name}: {type(attr_value)} - {attr_error}")


if __name__ == "__main__":
    debug_tools()