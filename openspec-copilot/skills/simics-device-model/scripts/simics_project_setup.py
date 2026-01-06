#!/usr/bin/env python3
"""
Simics Project Setup Script

Creates Simics project structure and dummy device model from IP-XACT register XML.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Global variable to store installed packages
INSTALLED_PACKAGES: Dict[str, Dict[str, str]] = {}


def get_installed_simics_pkgs() -> Dict[str, Dict[str, str]]:
  """
  Get all installed Simics packages by running ispm packages --list-installed.
  
  Returns:
    Dictionary mapping package numbers to package information including name and installation path.
  """
  global INSTALLED_PACKAGES
  
  ispm_path = Path.home() / ".simics-mcp-server" / "ispm"
  
  if not ispm_path.exists():
    print(f"Error: ispm not found at {ispm_path}", file=sys.stderr)
    sys.exit(1)
  
  try:
    result = subprocess.run(
      [str(ispm_path), "packages", "--list-installed"],
      capture_output=True,
      text=True,
      check=True
    )
    
    packages = {}
    lines = result.stdout.strip().split('\n')
    
    # Parse the output to extract package information
    # Expected format varies, but we need to extract package number and path
    for line in lines:
      if line.strip() and not line.startswith('#'):
        # Parse package information
        # Format might be: "1000 simics-6.0.123 /path/to/installation"
        parts = line.split()
        if len(parts) >= 3:
          pkg_number = parts[0]
          pkg_info = {
            'number': pkg_number,
            'name': parts[1],
            'version': parts[2] if len(parts) > 2 else '',
            'path': parts[3] if len(parts) > 3 else ''
          }
          packages[pkg_number] = pkg_info
    
    INSTALLED_PACKAGES = packages
    return packages
    
  except subprocess.CalledProcessError as e:
    print(f"Error running ispm: {e}", file=sys.stderr)
    print(f"stderr: {e.stderr}", file=sys.stderr)
    sys.exit(1)
  except Exception as e:
    print(f"Error getting installed packages: {e}", file=sys.stderr)
    sys.exit(1)


def create_simics_project(project_root: Path) -> Path:
  """
  Create Simics project structure using package 1000's project-setup.
  
  Args:
    project_root: Root directory where to create the project
    
  Returns:
    Path to the created simics-project directory
  """
  if not INSTALLED_PACKAGES:
    get_installed_simics_pkgs()
  
  # Find package 1000
  pkg_1000 = INSTALLED_PACKAGES.get('1000')
  
  if not pkg_1000:
    print("Error: Simics package 1000 not found in installed packages", file=sys.stderr)
    sys.exit(1)
  
  pkg_1000_path = Path(pkg_1000['path'])
  project_setup_bin = pkg_1000_path / "bin" / "project-setup"
  
  if not project_setup_bin.exists():
    print(f"Error: project-setup not found at {project_setup_bin}", file=sys.stderr)
    sys.exit(1)
  
  simics_project_path = project_root / "simics-project"
  
  try:
    # Run project-setup to create the project
    result = subprocess.run(
      [str(project_setup_bin), str(simics_project_path)],
      cwd=str(project_root),
      capture_output=True,
      text=True,
      check=True
    )
    
    print(f"Created Simics project at {simics_project_path}", file=sys.stderr)
    return simics_project_path
    
  except subprocess.CalledProcessError as e:
    print(f"Error creating Simics project: {e}", file=sys.stderr)
    print(f"stdout: {e.stdout}", file=sys.stderr)
    print(f"stderr: {e.stderr}", file=sys.stderr)
    sys.exit(1)


def create_dummy_device(simics_project_path: Path, device_name: str) -> Path:
  """
  Create a dummy device module in the Simics project.
  
  Args:
    simics_project_path: Path to the simics-project directory
    device_name: Name of the device to create
    
  Returns:
    Path to the created device module directory
  """
  # Check if simics-project exists, if not create it
  project_setup_bin = simics_project_path / "bin" / "project-setup"
  
  if not project_setup_bin.exists():
    # Simics project doesn't exist, create it first
    project_root = simics_project_path.parent
    print(f"Simics project not found at {simics_project_path}, creating it first...", file=sys.stderr)
    create_simics_project(project_root)
  
  try:
    # Run project-setup with device flags from simics-project directory
    result = subprocess.run(
      [
        "./bin/project-setup",
        "--with-cmake",
        "--without-gmake",
        "--device",
        device_name
      ],
      cwd=str(simics_project_path),
      capture_output=True,
      text=True,
      check=True
    )
    
    device_module_path = simics_project_path / "modules" / device_name
    print(f"Created dummy device '{device_name}' at {device_module_path}", file=sys.stderr)
    return device_module_path
    
  except subprocess.CalledProcessError as e:
    print(f"Error creating dummy device: {e}", file=sys.stderr)
    print(f"stdout: {e.stdout}", file=sys.stderr)
    print(f"stderr: {e.stderr}", file=sys.stderr)
    sys.exit(1)


def init_device(simics_project_path: Path, device_name: str, ipxact_xml_path: Path) -> None:
  """
  Initialize device from IP-XACT XML by generating DML and test files.
  
  Args:
    simics_project_path: Path to the simics-project directory
    device_name: Name of the device
    ipxact_xml_path: Path to the IP-XACT XML file
  """
  try:
    # Import ipxact_gen functions
    script_dir = Path(__file__).parent
    ipxact_gen_path = script_dir / "ipxact_gen.py"
    
    if not ipxact_gen_path.exists():
      print(f"Error: ipxact_gen.py not found at {ipxact_gen_path}", file=sys.stderr)
      sys.exit(1)
    
    # Import the module
    import importlib.util
    spec = importlib.util.spec_from_file_location("ipxact_gen", ipxact_gen_path)
    ipxact_gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ipxact_gen)
    
    # Get device module path
    device_module_path = simics_project_path / "modules" / device_name
    
    if not device_module_path.exists():
      print(f"Error: Device module path not found at {device_module_path}", file=sys.stderr)
      sys.exit(1)
    
    # Parse IP-XACT and generate DML files
    device = ipxact_gen.parse_ipxact_registers(str(ipxact_xml_path), device_name)
    ipxact_gen.gen_dml_from_regs(device, str(device_module_path))
    ipxact_gen.gen_test_from_xml(device, str(device_module_path))
    
    print(f"Initialized device '{device_name}' from IP-XACT XML", file=sys.stderr)
    print(f"Generated DML files: {device_name}.dml and {device_name}-registers.dml", file=sys.stderr)
    print(f"Generated test files in {device_module_path}/test/", file=sys.stderr)
    
  except Exception as e:
    print(f"Error initializing device from IP-XACT: {e}", file=sys.stderr)
    sys.exit(1)


def main():
  """Main entry point for the script."""
  parser = argparse.ArgumentParser(
    description="Setup Simics project and create dummy device model"
  )
  parser.add_argument(
    "device_name",
    help="Name of the device to create"
  )
  parser.add_argument(
    "--json",
    action="store_true",
    help="Output results in JSON format"
  )
  parser.add_argument(
    "--project-root",
    type=Path,
    default=Path.cwd(),
    help="Root directory for the project (default: current directory)"
  )
  parser.add_argument(
    "--ipxact-xml",
    type=Path,
    help="Path to IP-XACT XML file for device initialization (optional)"
  )
  
  args = parser.parse_args()
  
  # Get installed packages
  packages = get_installed_simics_pkgs()
  
  # Create Simics project
  simics_project_path = create_simics_project(args.project_root)
  
  # Create dummy device
  device_module_path = create_dummy_device(simics_project_path, args.device_name)
  
  # Initialize device from IP-XACT if provided
  if args.ipxact_xml:
    if not args.ipxact_xml.exists():
      print(f"Error: IP-XACT XML file not found at {args.ipxact_xml}", file=sys.stderr)
      sys.exit(1)
    init_device(simics_project_path, args.device_name, args.ipxact_xml)
  
  # Output results
  if args.json:
    output = {
      "device_name": args.device_name,
      "project_root": str(args.project_root),
      "simics_project_path": str(simics_project_path),
      "device_module_path": str(device_module_path),
      "packages_count": len(packages)
    }
    print(json.dumps(output))
  else:
    print(f"Device Name: {args.device_name}")
    print(f"Project Root: {args.project_root}")
    print(f"Simics Project: {simics_project_path}")
    print(f"Device Module: {device_module_path}")
    print(f"Installed Packages: {len(packages)}")


if __name__ == "__main__":
  main()
