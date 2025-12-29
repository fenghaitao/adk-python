#!/usr/bin/env python3
"""
Simics Setup Script
Description: Setup Simics Project environment and generate DML device code using MCP tools

Usage: ./run_simics_setup.py <proj_dir_path> <device_name>
  proj_dir_path: Absolute path to workspace root directory
                 (Simics project will be created at <proj_dir_path>/simics-project)
  device_name:   Name of the device to generate

Prerequisites:
  - Register XML must exist at: <proj_dir_path>/specs/<branch>/*<device_name>*.xml

Example:
  ./run_simics_setup.py /path/to/workspace wdt
  
  This will:
    - Search for register XML: /path/to/workspace/specs/<branch>/*wdt*.xml
    - Create Simics project at: /path/to/workspace/simics-project/
    - Generate DML device code
"""

import asyncio
import sys
import os
import subprocess
from pathlib import Path
import glob


def get_adk_root():
    """Get ADK_ROOT from environment variable."""
    adk_root = os.environ.get('ADK_ROOT')
    if not adk_root:
        print("Error: ADK_ROOT environment variable not set")
        sys.exit(1)
    return Path(adk_root)


def get_current_branch(proj_dir_path: str = None):
    """Get current git branch name from workspace directory.
    
    Args:
        proj_dir_path: Optional workspace root directory path to get branch from.
                      If None, uses current directory.
    """
    try:
        cmd = ['git', 'branch', '--show-current']
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=proj_dir_path  # Run git command in workspace directory
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting git branch from {proj_dir_path}: {e}")
        sys.exit(1)


async def setup_simics_project(proj_dir_path: str, device_name: str):
    """Setup Simics project and generate DML registers.
    
    Args:
        proj_dir_path: Workspace root directory path
        device_name: Name of the device to generate
        
    Prerequisites:
        - Register XML must exist at: <proj_dir_path>/specs/<branch>/*<device_name>*.xml
        
    Creates:
        - Simics project at: <proj_dir_path>/simics-project
        - DML device code generated from the register XML
    """
    
    # Add spec_kit_tools to Python path
    adk_root = get_adk_root()
    spec_kit_tools_dir = adk_root / "contributing" / "samples" / "spec_kit_integration"
    sys.path.insert(0, str(spec_kit_tools_dir))
    
    # Import after adding to path
    from spec_kit_tools import create_simics_mcp_toolset
    
    # Construct simics project path inside workspace
    simics_proj_path = str(Path(proj_dir_path) / "simics-project")
    print(f"Workspace root: {proj_dir_path}")
    print(f"Simics project will be created at: {simics_proj_path}")
    
    # Get current git branch for XML path (from workspace directory)
    branch = get_current_branch(proj_dir_path)
    specs_dir = Path(proj_dir_path) / "specs" / branch
    
    # Search for register XML file containing device name
    xml_pattern = str(specs_dir / f"*{device_name}*.xml")
    xml_files = glob.glob(xml_pattern)
    
    if not xml_files:
        print(f"\n✗ Error: No register XML found matching pattern: {xml_pattern}")
        print(f"Please ensure a register XML file containing '{device_name}' exists in {specs_dir}")
        return False
    
    if len(xml_files) > 1:
        print(f"\n⚠ Warning: Multiple XML files found matching pattern:")
        for f in xml_files:
            print(f"  - {f}")
        print(f"Using the first one: {xml_files[0]}")
    
    reg_xml = xml_files[0]
    
    print("")
    print("=== Simics Setup Configuration ===")
    print(f"Workspace Root:  {proj_dir_path}")
    print(f"Simics Project:  {simics_proj_path}")
    print(f"Device Name:     {device_name}")
    print(f"Git Branch:      {branch}")
    print(f"Register XML:    {reg_xml} ✓")
    print("==================================")
    print("")
    
    try:
        # Create the MCP toolset
        print("Connecting to Simics MCP server...")
        mcp_toolset = create_simics_mcp_toolset()
        
        # Get tools from the MCP server
        tools = await mcp_toolset.get_tools()
        print(f"✓ Connected to MCP server ({len(tools)} tools available)")
        
        # Find the required tools
        create_project_tool = None
        generate_registers_tool = None
        
        for tool in tools:
            if tool.name == "create_simics_project":
                create_project_tool = tool
            elif tool.name == "generate_dml_registers":
                generate_registers_tool = tool
        
        if not create_project_tool:
            print("✗ Error: create_simics_project tool not found")
            return False
        
        if not generate_registers_tool:
            print("✗ Error: generate_dml_registers tool not found")
            return False
        
        # Step 1: Create Simics Project
        print("\nStep 1: Creating Simics project...")
        try:
            result = await create_project_tool.run_async(
                args={"project_path": simics_proj_path},
                tool_context=None
            )
            print(f"✓ Project created: {result}")
        except Exception as e:
            print(f"✗ Failed to create project: {e}")
            return False
        
        # Step 2: Generate DML Registers
        print("\nStep 2: Generating DML registers...")
        try:
            result = await generate_registers_tool.run_async(
                args={
                    "project_path": simics_proj_path,
                    "reg_xml": reg_xml,
                    "device_name": device_name
                },
                tool_context=None
            )
            print(f"✓ DML registers generated: {result}")
        except Exception as e:
            print(f"✗ Failed to generate DML registers: {e}")
            return False
        
        # Clean up
        await mcp_toolset.close()
        print("\n✓ MCP connection closed")
        
        print("\n=== Setup Complete ===")
        print("Simics project setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    # Check arguments
    if len(sys.argv) != 3:
        print("Usage: ./run_simics_setup.py <proj_dir_path> <device_name>")
        print("  proj_dir_path: Absolute path to workspace root directory")
        print("                 (Simics project will be created at <proj_dir_path>/simics-project)")
        print("  device_name:   Name of the device to generate")
        print("\nPrerequisites:")
        print("  - Register XML must exist at: <proj_dir_path>/specs/<branch>/*<device_name>*.xml")
        print("\nExample:")
        print("  ./run_simics_setup.py /path/to/workspace wdt")
        print("\nThis will:")
        print("  - Search for register XML matching: /path/to/workspace/specs/<branch>/*wdt*.xml")
        print("  - Create Simics project at: /path/to/workspace/simics-project/")
        print("  - Generate DML device code")
        sys.exit(1)
    
    proj_dir_path = sys.argv[1]
    device_name = sys.argv[2]
    
    print("=" * 60)
    print("Simics Project Setup Script")
    print("=" * 60)
    
    success = await setup_simics_project(proj_dir_path, device_name)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All steps completed successfully!")
    else:
        print("✗ Setup failed. Check the error messages above.")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
