#!/usr/bin/env python3
"""
OpenSpec Project Setup Script

This script sets up an OpenSpec workflow for any project by:
1. Initializing OpenSpec directory structure (if needed)
2. Creating/updating the specification file in openspec/specs/
3. Creating project.md with context
4. Optionally generating change proposals from existing code

Usage:
    python3 setup_openspec_project.py \\
        --project /path/to/project \\
        --spec hardware_spec.md \\
        --spec-name "Hardware Device" \\
        --context "Simics device modeling project" \\
        --dml modules/device/device.dml
"""

import argparse
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, check=True, capture_output=False):
    """Run a shell command"""
    print(f"Running: {cmd}")
    if capture_output:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"Error: {result.stderr}")
            sys.exit(1)
        return result.stdout
    else:
        result = subprocess.run(cmd, shell=True, cwd=cwd)
        if check and result.returncode != 0:
            sys.exit(1)
        return None


def init_openspec(project_dir, force=False):
    """Initialize OpenSpec in the project directory"""
    openspec_dir = project_dir / "openspec"
    
    if openspec_dir.exists() and not force:
        print(f"✓ OpenSpec directory already exists: {openspec_dir}")
        return
    
    print(f"Initializing OpenSpec in {project_dir}")
    
    # Run openspec init
    venv_path = Path.home() / "wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv"
    openspec_cmd = f"source {venv_path}/bin/activate && openspec init --non-interactive --tools all ."
    
    run_command(f"bash -c '{openspec_cmd}'", cwd=project_dir)
    print(f"✓ OpenSpec initialized")


def setup_spec_file(project_dir, spec_file, spec_name):
    """Copy or link the specification file to openspec/specs/"""
    openspec_specs_dir = project_dir / "openspec" / "specs"
    openspec_specs_dir.mkdir(parents=True, exist_ok=True)
    
    spec_file = Path(spec_file)
    if not spec_file.is_absolute():
        spec_file = project_dir / spec_file
    
    if not spec_file.exists():
        print(f"Error: Spec file not found: {spec_file}")
        sys.exit(1)
    
    # Create a subdirectory for the spec
    spec_subdir = openspec_specs_dir / spec_name.lower().replace(" ", "_")
    spec_subdir.mkdir(parents=True, exist_ok=True)
    
    # Copy the spec file
    dest_spec = spec_subdir / spec_file.name
    shutil.copy2(spec_file, dest_spec)
    
    print(f"✓ Spec file copied to: {dest_spec}")
    
    # Create a README.md in the spec directory
    readme_content = f"""# {spec_name} Specification

This directory contains the hardware specification for {spec_name}.

## Files

- `{spec_file.name}`: Main hardware specification document

## Purpose

This specification defines the register map, behavior, and implementation requirements
for the {spec_name} hardware device.
"""
    
    readme_path = spec_subdir / "README.md"
    readme_path.write_text(readme_content)
    print(f"✓ Created spec README: {readme_path}")
    
    return dest_spec


def create_project_md(project_dir, context, spec_name):
    """Create or update the project.md file"""
    project_md_path = project_dir / "openspec" / "project.md"
    
    content = f"""# Project Context

## Overview

{context}

## Specifications

This project implements {spec_name} as defined in the hardware specification.

## Development Workflow

1. **Specification**: Hardware behavior is defined in `specs/` directory
2. **Changes**: Proposed changes are tracked in `changes/` directory  
3. **Implementation**: Code changes are implemented in the main project
4. **Testing**: Each change includes test cases to verify behavior

## AI Agent Instructions

When implementing changes:
- Read the hardware specification carefully
- Implement register behavior with proper side effects
- Create comprehensive test cases
- Compile and verify the implementation works

## Project Structure

- `modules/`: Device model implementation (DML files)
- `openspec/specs/`: Hardware specifications
- `openspec/changes/`: Change proposals and tasks
- `test/`: Test files for verification
"""
    
    project_md_path.write_text(content)
    print(f"✓ Created project.md: {project_md_path}")


def setup_agents_md(project_dir):
    """Ensure AGENTS.md exists with proper workflow"""
    agents_md_path = project_dir / "openspec" / "AGENTS.md"
    
    if agents_md_path.exists():
        print(f"✓ AGENTS.md already exists: {agents_md_path}")
        return
    
    # The openspec init should have created this, but if not, we can create a basic one
    content = """# AI Agent Workflow for OpenSpec

This file defines how AI agents should work with OpenSpec changes.

## Workflow

1. **Read Specification**: Start by reading the spec file in `specs/` directory
2. **Review Change**: Read the change proposal in `changes/[change-id]/proposal.md`
3. **Implement Code**: Edit the necessary source files
4. **Create Tests**: Add test cases to verify the implementation
5. **Verify**: Compile and run tests to ensure correctness
6. **Complete**: Mark the change as complete

## For Direct Implementation

When given specific implementation instructions:
1. Read the referenced specification files
2. Implement the code as specified
3. Create test files
4. Compile and verify
5. Report completion
"""
    
    agents_md_path.write_text(content)
    print(f"✓ Created AGENTS.md: {agents_md_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Setup OpenSpec project with specifications and context"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="Path to the project directory"
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Path to the hardware specification file (e.g., wdt.md)"
    )
    parser.add_argument(
        "--spec-name",
        required=True,
        help="Name of the specification (e.g., 'Watchdog Timer')"
    )
    parser.add_argument(
        "--context",
        required=True,
        help="Project context description (e.g., 'Simics device modeling project')"
    )
    parser.add_argument(
        "--dml",
        help="Path to DML file (optional, for generating change proposals)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-initialization even if OpenSpec exists"
    )
    
    args = parser.parse_args()
    
    project_dir = Path(args.project).resolve()
    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}")
        sys.exit(1)
    
    print("=" * 70)
    print("OpenSpec Project Setup")
    print("=" * 70)
    print(f"Project: {project_dir}")
    print(f"Spec: {args.spec}")
    print(f"Spec Name: {args.spec_name}")
    print(f"Context: {args.context}")
    print("=" * 70)
    print()
    
    # Step 1: Initialize OpenSpec
    init_openspec(project_dir, force=args.force)
    
    # Step 2: Setup spec file
    spec_path = setup_spec_file(project_dir, args.spec, args.spec_name)
    
    # Step 3: Create project.md
    create_project_md(project_dir, args.context, args.spec_name)
    
    # Step 4: Ensure AGENTS.md exists
    setup_agents_md(project_dir)
    
    print()
    print("=" * 70)
    print("✓✓✓ OpenSpec Project Setup Complete ✓✓✓")
    print("=" * 70)
    print()
    print("Next steps:")
    print()
    print("1. Review the spec file:")
    print(f"   cat {spec_path}")
    print()
    print("2. Create change proposals (if needed):")
    print(f"   cd {project_dir}")
    if args.dml:
        print(f"   python3 run_openspec_from_ddm.py --project . --dml {args.dml} --spec {args.spec}")
    print()
    print("3. Run AI agent with ADK:")
    print(f"   cd {project_dir}")
    print("   adk run adk_openspec_agent")
    print()
    print("OpenSpec directories:")
    print(f"   - Specs: {project_dir}/openspec/specs/")
    print(f"   - Changes: {project_dir}/openspec/changes/")
    print(f"   - Project: {project_dir}/openspec/project.md")
    print()


if __name__ == "__main__":
    main()
