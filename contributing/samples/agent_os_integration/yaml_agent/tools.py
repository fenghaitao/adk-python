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

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from google.adk.tools.tool_context import ToolContext


# Root Agent Tools
def create_product_mission(
    product_name: str,
    description: str,
    target_users: str,
    key_features: List[str],
    tool_context: ToolContext
) -> str:
    """Create a product mission document following Agent OS structure.
    
    Args:
        product_name: Name of the product
        description: Brief product description
        target_users: Description of target user base
        key_features: List of key product features
        
    Returns:
        Status message about mission creation
    """
    mission_content = f"""# Product Mission

## Pitch

{description}

## Target Users

{target_users}

## Key Features

{chr(10).join(f"- {feature}" for feature in key_features)}

## Success Metrics

- User adoption rate
- Feature utilization
- User satisfaction scores
- Performance benchmarks

## Timeline

- Phase 1: Core functionality (Month 1-2)
- Phase 2: Advanced features (Month 3-4)
- Phase 3: Optimization & scaling (Month 5-6)
"""

    # Create .agent-os directory structure
    agent_os_dir = Path(".agent-os")
    product_dir = agent_os_dir / "product"
    product_dir.mkdir(parents=True, exist_ok=True)
    
    # Write mission file
    mission_file = product_dir / "mission.md"
    mission_file.write_text(mission_content)
    
    # Create mission-lite.md
    mission_lite = f"""# {product_name}

{description}

**Target Users**: {target_users}

**Key Features**: {', '.join(key_features)}
"""
    
    mission_lite_file = product_dir / "mission-lite.md"
    mission_lite_file.write_text(mission_lite)
    
    return f"✅ Created product mission for '{product_name}' in .agent-os/product/"


def create_technical_spec(
    feature_name: str,
    requirements: str,
    acceptance_criteria: List[str],
    tool_context: ToolContext
) -> str:
    """Create a detailed technical specification.
    
    Args:
        feature_name: Name of the feature
        requirements: Detailed requirements description
        acceptance_criteria: List of acceptance criteria
        
    Returns:
        Status message about spec creation
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    spec_name = f"{date_str}-{feature_name.lower().replace(' ', '-')}"
    
    spec_content = f"""# {feature_name} Specification

## Overview

{requirements}

## Technical Requirements

### Functional Requirements
- Core functionality implementation
- User interface components
- Data handling and storage
- Integration points

### Non-Functional Requirements
- Performance benchmarks
- Security considerations
- Scalability requirements
- Accessibility standards

## Acceptance Criteria

{chr(10).join(f"- {criteria}" for criteria in acceptance_criteria)}

## Implementation Plan

### Phase 1: Foundation
- Set up project structure
- Implement core components
- Basic functionality

### Phase 2: Enhancement
- Advanced features
- User interface polish
- Integration testing

### Phase 3: Optimization
- Performance tuning
- Security hardening
- Documentation

## Testing Strategy

- Unit tests for core functionality
- Integration tests for system components
- User acceptance testing
- Performance testing

## Dependencies

- External libraries and frameworks
- Third-party services
- Infrastructure requirements

## Risks and Mitigation

- Technical risks and solutions
- Timeline risks and contingencies
- Resource constraints and alternatives
"""

    # Create spec directory
    agent_os_dir = Path(".agent-os")
    specs_dir = agent_os_dir / "specs" / spec_name
    specs_dir.mkdir(parents=True, exist_ok=True)
    
    # Write spec file
    spec_file = specs_dir / "spec.md"
    spec_file.write_text(spec_content)
    
    # Create spec-lite.md
    spec_lite = f"""# {feature_name}

{requirements}

## Acceptance Criteria
{chr(10).join(f"- {criteria}" for criteria in acceptance_criteria)}
"""
    
    spec_lite_file = specs_dir / "spec-lite.md"
    spec_lite_file.write_text(spec_lite)
    
    return f"✅ Created technical specification '{feature_name}' in .agent-os/specs/{spec_name}/"


def create_task_breakdown(
    spec_name: str,
    tasks: List[str],
    tool_context: ToolContext
) -> str:
    """Create a task breakdown for a specification.
    
    Args:
        spec_name: Name of the specification
        tasks: List of tasks to complete
        
    Returns:
        Status message about task creation
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    spec_folder = f"{date_str}-{spec_name.lower().replace(' ', '-')}"
    
    tasks_content = f"""# {spec_name} - Task Breakdown

## Tasks

{chr(10).join(f"- [ ] {task}" for task in tasks)}

## Task Status

- **Total Tasks**: {len(tasks)}
- **Completed**: 0
- **In Progress**: 0
- **Pending**: {len(tasks)}

## Notes

- Tasks should be completed in order when possible
- Mark tasks as complete with [x] when finished
- Add notes and comments as needed

## Completion Criteria

All tasks must be completed and tested before marking the specification as done.
"""

    # Find or create spec directory
    agent_os_dir = Path(".agent-os")
    specs_dir = agent_os_dir / "specs" / spec_folder
    specs_dir.mkdir(parents=True, exist_ok=True)
    
    # Write tasks file
    tasks_file = specs_dir / "tasks.md"
    tasks_file.write_text(tasks_content)
    
    return f"✅ Created task breakdown for '{spec_name}' with {len(tasks)} tasks"


def analyze_project_structure(
    project_path: str,
    tool_context: ToolContext
) -> str:
    """Analyze the current project structure and provide insights.
    
    Args:
        project_path: Path to the project directory to analyze
        
    Returns:
        Analysis of the project structure
    """
    current_dir = Path(project_path)
    
    # Analyze directory structure
    directories = []
    files = []
    
    for item in current_dir.rglob("*"):
        if item.is_dir() and not item.name.startswith('.'):
            directories.append(str(item))
        elif item.is_file() and not item.name.startswith('.'):
            files.append(str(item))
    
    # Check for Agent OS structure
    agent_os_dir = Path(".agent-os")
    has_agent_os = agent_os_dir.exists()
    
    analysis = f"""# Project Structure Analysis

## Overview
- **Total Directories**: {len(directories)}
- **Total Files**: {len(files)}
- **Agent OS Structure**: {'✅ Present' if has_agent_os else '❌ Missing'}

## Directory Structure
{chr(10).join(f"- {d}" for d in sorted(directories)[:10])}
{'...' if len(directories) > 10 else ''}

## Key Files
{chr(10).join(f"- {f}" for f in sorted(files)[:10])}
{'...' if len(files) > 10 else ''}

## Agent OS Status
"""

    if has_agent_os:
        # Analyze Agent OS structure
        product_dir = agent_os_dir / "product"
        specs_dir = agent_os_dir / "specs"
        
        analysis += f"""
- **Product Directory**: {'✅' if product_dir.exists() else '❌'}
- **Specs Directory**: {'✅' if specs_dir.exists() else '❌'}
"""
        
        if specs_dir.exists():
            specs = list(specs_dir.iterdir())
            analysis += f"- **Specifications**: {len(specs)} found\n"
            for spec in specs[:5]:
                analysis += f"  - {spec.name}\n"
    else:
        analysis += """
- Agent OS structure not initialized
- Run @plan-product to set up the structure
"""

    return analysis


# Claude Code Agent Tools
def create_file_structure(
    project_name: str,
    structure: Dict[str, str],
    tool_context: ToolContext
) -> str:
    """Create a file and directory structure for a project.
    
    Args:
        project_name: Name of the project
        structure: Dictionary mapping file paths to content
        
    Returns:
        Status message about structure creation
    """
    created_files = []
    created_dirs = []
    
    for file_path, content in structure.items():
        path = Path(file_path)
        
        # Create parent directories
        if path.parent != Path("."):
            path.parent.mkdir(parents=True, exist_ok=True)
            if str(path.parent) not in created_dirs:
                created_dirs.append(str(path.parent))
        
        # Create file
        path.write_text(content)
        created_files.append(str(path))
    
    return f"""🔨 **Creating**: Project structure for {project_name}

**Created Directories**: {len(created_dirs)}
{chr(10).join(f"- {d}" for d in created_dirs)}

**Created Files**: {len(created_files)}
{chr(10).join(f"- {f}" for f in created_files)}

✅ **Completed**: File structure creation"""


def implement_feature(
    feature_name: str,
    implementation_details: str,
    file_changes: Dict[str, str],
    tool_context: ToolContext
) -> str:
    """Implement a specific feature with file changes.
    
    Args:
        feature_name: Name of the feature to implement
        implementation_details: Details about the implementation
        file_changes: Dictionary mapping file paths to new content
        
    Returns:
        Status message about feature implementation
    """
    modified_files = []
    
    for file_path, content in file_changes.items():
        path = Path(file_path)
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file content
        path.write_text(content)
        modified_files.append(str(path))
    
    return f"""🔨 **Implementing**: {feature_name}

**Implementation Details**:
{implementation_details}

**Modified Files**: {len(modified_files)}
{chr(10).join(f"- {f}" for f in modified_files)}

✅ **Completed**: Feature implementation"""


def run_tests(
    test_command: str,
    test_path: str,
    tool_context: ToolContext
) -> str:
    """Run tests and analyze results.
    
    Args:
        test_command: Command to run tests
        test_path: Path to test files
        
    Returns:
        Test execution results
    """
    try:
        result = subprocess.run(
            test_command.split(),
            cwd=test_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return f"""🧪 **Testing**: Running test suite

**Command**: {test_command}
**Path**: {test_path}
**Exit Code**: {result.returncode}

**Output**:
{result.stdout}

**Errors**:
{result.stderr}

**Status**: {'✅ PASSED' if result.returncode == 0 else '❌ FAILED'}
"""
    
    except subprocess.TimeoutExpired:
        return "🧪 **Testing**: Test execution timed out after 60 seconds"
    except Exception as e:
        return f"🧪 **Testing**: Error running tests: {str(e)}"


def manage_git_workflow(
    action: str,
    branch_name: str,
    commit_message: str,
    tool_context: ToolContext
) -> str:
    """Manage git workflow operations.
    
    Args:
        action: Git action to perform (branch, commit, push, etc.)
        branch_name: Name of the branch for branch operations
        commit_message: Commit message for commit operations
        
    Returns:
        Status message about git operation
    """
    try:
        if action == "create_branch" and branch_name:
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                text=True
            )
            return f"🌿 **Git**: Created and switched to branch '{branch_name}'"
            
        elif action == "commit" and commit_message:
            # Add all changes
            subprocess.run(["git", "add", "."], capture_output=True)
            
            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True
            )
            return f"🌿 **Git**: Committed changes with message: '{commit_message}'"
            
        elif action == "status":
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            return f"🌿 **Git**: Repository status:\n{result.stdout}"
            
        else:
            return f"🌿 **Git**: Unknown action '{action}'"
            
    except Exception as e:
        return f"🌿 **Git**: Error performing {action}: {str(e)}"


def update_task_status(
    spec_name: str,
    task_index: int,
    completed: bool,
    tool_context: ToolContext
) -> str:
    """Update the status of a specific task.
    
    Args:
        spec_name: Name of the specification
        task_index: Index of the task to update (0-based)
        completed: Whether the task is completed
        
    Returns:
        Status message about task update
    """
    # Find the spec directory
    agent_os_dir = Path(".agent-os")
    specs_dir = agent_os_dir / "specs"
    
    if not specs_dir.exists():
        return "❌ No specs directory found"
    
    # Find matching spec folder
    spec_folders = [d for d in specs_dir.iterdir() if spec_name.lower() in d.name.lower()]
    
    if not spec_folders:
        return f"❌ No specification found matching '{spec_name}'"
    
    spec_folder = spec_folders[0]
    tasks_file = spec_folder / "tasks.md"
    
    if not tasks_file.exists():
        return f"❌ No tasks.md file found in {spec_folder}"
    
    # Read and update tasks
    content = tasks_file.read_text()
    lines = content.split('\n')
    
    task_lines = [i for i, line in enumerate(lines) if line.strip().startswith('- [')]
    
    if task_index >= len(task_lines):
        return f"❌ Task index {task_index} out of range (0-{len(task_lines)-1})"
    
    line_index = task_lines[task_index]
    current_line = lines[line_index]
    
    if completed:
        lines[line_index] = current_line.replace('- [ ]', '- [x]')
        status = "completed"
    else:
        lines[line_index] = current_line.replace('- [x]', '- [ ]')
        status = "pending"
    
    # Write updated content
    tasks_file.write_text('\n'.join(lines))
    
    return f"✅ **Completed**: Updated task {task_index} to {status} in {spec_folder.name}"


def create_documentation(
    doc_type: str,
    title: str,
    content: str,
    tool_context: ToolContext
) -> str:
    """Create documentation files.
    
    Args:
        doc_type: Type of documentation (README, API, etc.)
        title: Title of the documentation
        content: Content of the documentation
        
    Returns:
        Status message about documentation creation
    """
    if doc_type.lower() == "readme":
        file_path = Path("README.md")
    else:
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True)
        file_path = docs_dir / f"{title.lower().replace(' ', '_')}.md"
    
    doc_content = f"""# {title}

{content}

---
*Generated by Agent OS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    file_path.write_text(doc_content)
    
    return f"📁 **Creating**: {doc_type} documentation at {file_path}"