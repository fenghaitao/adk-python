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

from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext


# Agent OS Root Agent Tools
def create_product_mission(
    product_name: str,
    description: str,
    target_users: str,
    key_features: List[str],
    project_folder: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Create a product mission document following Agent OS structure.
    
    Args:
        product_name: Name of the product
        description: Brief product description
        target_users: Description of target user base
        key_features: List of key product features
        project_folder: Optional project folder path (if None, uses current directory)
        
    Returns:
        Status message about mission creation
    """
    # Determine the base directory
    if project_folder:
        base_dir = Path(project_folder)
    else:
        base_dir = Path(".")
    
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
    agent_os_dir = base_dir / ".agent-os"
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
    
    # Create tech-stack.md placeholder
    tech_stack_content = f"""# Technical Stack

## Application Framework
- Framework: [To be determined]
- Version: [To be determined]

## Database System
- Database: [To be determined]
- Version: [To be determined]

## Frontend
- JavaScript Framework: [To be determined]
- CSS Framework: [To be determined]

## Deployment
- Hosting: [To be determined]
- CI/CD: [To be determined]

---
*This will be populated during the planning phase*
"""
    
    tech_stack_file = product_dir / "tech-stack.md"
    tech_stack_file.write_text(tech_stack_content)
    
    # Create roadmap.md placeholder
    roadmap_content = f"""# Product Roadmap

## Phase 1: Core Functionality
**Goal**: Implement essential features
**Success Criteria**: Basic functionality working

### Features
- [ ] {key_features[0] if key_features else 'Core Feature 1'}
- [ ] {key_features[1] if len(key_features) > 1 else 'Core Feature 2'}
- [ ] {key_features[2] if len(key_features) > 2 else 'Core Feature 3'}

## Phase 2: Advanced Features
**Goal**: Add advanced functionality
**Success Criteria**: Enhanced user experience

### Features
- [ ] Advanced Feature 1
- [ ] Advanced Feature 2
- [ ] Advanced Feature 3

## Phase 3: Optimization & Scaling
**Goal**: Performance and scalability
**Success Criteria**: Production-ready system

### Features
- [ ] Performance optimization
- [ ] Scalability improvements
- [ ] Security hardening
"""
    
    roadmap_file = product_dir / "roadmap.md"
    roadmap_file.write_text(roadmap_content)
    
    return f"""✅ **Product Mission Created**: {product_name}

**Location**: {product_dir.absolute()}
**Files Created**:
- mission.md - Complete product mission
- mission-lite.md - Condensed mission summary
- tech-stack.md - Technical stack placeholder
- roadmap.md - Development roadmap

**Next Steps**:
1. Review and customize the mission documents
2. Update tech-stack.md with your technology choices
3. Modify roadmap.md based on your priorities
4. Use @create-spec to create detailed specifications
"""


def create_technical_spec(
    feature_name: str,
    requirements: str,
    acceptance_criteria: List[str],
    project_folder: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Create a detailed technical specification.
    
    Args:
        feature_name: Name of the feature
        requirements: Detailed requirements description
        acceptance_criteria: List of acceptance criteria
        project_folder: Optional project folder path (if None, uses current directory)
        
    Returns:
        Status message about spec creation
    """
    # Determine the base directory
    if project_folder:
        base_dir = Path(project_folder)
    else:
        base_dir = Path(".")
    
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
    agent_os_dir = base_dir / ".agent-os"
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
    
    # Create sub-specs directory and technical spec
    sub_specs_dir = specs_dir / "sub-specs"
    sub_specs_dir.mkdir(exist_ok=True)
    
    tech_spec_content = f"""# Technical Specification - {feature_name}

## Architecture

[Technical architecture details to be defined]

## Implementation Details

[Detailed implementation steps]

## Dependencies

[External dependencies and requirements]

## API Design

[API endpoints and interfaces]

## Database Schema

[Database design and relationships]

## Security Considerations

[Security requirements and implementation]

---
*This technical specification will be detailed during implementation*
"""
    
    tech_spec_file = sub_specs_dir / "technical-spec.md"
    tech_spec_file.write_text(tech_spec_content)
    
    return f"""✅ **Technical Specification Created**: {feature_name}

**Location**: {specs_dir.absolute()}
**Files Created**:
- spec.md - Complete specification
- spec-lite.md - Condensed specification
- sub-specs/technical-spec.md - Technical details

**Next Steps**:
1. Review and customize the specification
2. Use @create-tasks to break down into actionable tasks
3. Use @execute-tasks to implement the feature
"""


def create_task_breakdown(
    spec_name: str,
    tasks: List[str],
    project_folder: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Create a task breakdown for a specification.
    
    Args:
        spec_name: Name of the specification
        tasks: List of tasks to complete
        project_folder: Optional project folder path (if None, uses current directory)
        
    Returns:
        Status message about task creation
    """
    # Determine the base directory
    if project_folder:
        base_dir = Path(project_folder)
    else:
        base_dir = Path(".")
    
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

## Implementation Guidelines

1. **Code Quality**: Follow project coding standards
2. **Testing**: Write tests for each task
3. **Documentation**: Update documentation as needed
4. **Git Workflow**: Create feature branches for each task
5. **Review**: Code review before marking complete

## Dependencies

- Ensure all dependencies are installed
- Check for conflicts with existing code
- Verify integration points

---
*Generated by Agent OS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    # Find or create spec directory
    agent_os_dir = base_dir / ".agent-os"
    specs_dir = agent_os_dir / "specs" / spec_folder
    specs_dir.mkdir(parents=True, exist_ok=True)
    
    # Write tasks file
    tasks_file = specs_dir / "tasks.md"
    tasks_file.write_text(tasks_content)
    
    # Create implementation notes file
    implementation_notes = f"""# Implementation Notes - {spec_name}

## Development Environment

- **Project Folder**: {base_dir.absolute()}
- **Specification**: {spec_folder}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Quick Start

1. Navigate to project folder: `cd {base_dir.name if base_dir.name != '.' else 'current directory'}`
2. Review tasks in `.agent-os/specs/{spec_folder}/tasks.md`
3. Start with the first task
4. Use @execute-task to work on specific tasks

## File Structure

```
{base_dir.name}/
├── .agent-os/
│   └── specs/
│       └── {spec_folder}/
│           ├── spec.md
│           ├── spec-lite.md
│           ├── tasks.md
│           ├── implementation-notes.md
│           └── sub-specs/
│               └── technical-spec.md
├── src/                  # Source code
├── tests/                # Test files
└── docs/                 # Documentation
```

## Task Management

- Mark completed tasks with `[x]`
- Add progress notes in tasks.md
- Update implementation-notes.md with details
- Create git branches for each major task

---
*This file helps track implementation progress*
"""
    
    notes_file = specs_dir / "implementation-notes.md"
    notes_file.write_text(implementation_notes)
    
    return f"""✅ **Task Breakdown Created**: {spec_name}

**Location**: {specs_dir.absolute()}
**Files Created**:
- tasks.md - Task breakdown with {len(tasks)} tasks
- implementation-notes.md - Implementation guidance

**Next Steps**:
1. Review the task breakdown
2. Use @execute-task to work on specific tasks
3. Use @execute-tasks to work through all tasks systematically
4. Update task status as you complete them

**Available Commands**:
- @execute-task [task_number] - Work on a specific task
- @execute-tasks - Execute all tasks in order
- @analyze-project - Check project status
"""


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
    analysis = "📊 **Project Structure Analysis**\n\n"
    
    # Check for Agent OS structure
    base_path = Path(project_path)
    agent_os_path = base_path / ".agent-os"
    if agent_os_path.exists():
        analysis += "✅ Agent OS structure detected\n"
        
        # Check key directories
        key_dirs = ["product", "specs", "standards", "instructions"]
        for dir_name in key_dirs:
            dir_path = agent_os_path / dir_name
            if dir_path.exists():
                analysis += f"  ✅ {dir_name}/ directory exists\n"
            else:
                analysis += f"  ❌ {dir_name}/ directory missing\n"
    else:
        analysis += "❌ Agent OS structure not found\n"
        analysis += "💡 Consider initializing Agent OS structure\n"
    
    # Check for common project files
    common_files = ["README.md", "package.json", "requirements.txt", "Makefile"]
    analysis += "\n📁 **Project Files:**\n"
    for file_name in common_files:
        if (base_path / file_name).exists():
            analysis += f"  ✅ {file_name}\n"
    
    return analysis


def analyze_existing_product(
    project_path: str,
    product_context: str,
    tool_context: ToolContext
) -> str:
    """Analyze an existing product codebase and prepare for Agent OS installation.
    
    This tool performs a comprehensive analysis of an existing codebase to understand:
    - Current project structure and organization
    - Technology stack and dependencies
    - Implemented features and progress
    - Code patterns and conventions
    - Development workflow and practices
    
    Args:
        project_path: Path to the project directory to analyze
        product_context: Additional context about the product (vision, users, etc.)
        
    Returns:
        Comprehensive analysis report for Agent OS installation
    """
    current_dir = Path(project_path)
    
    # Analyze directory structure
    directories = []
    files = []
    config_files = []
    source_files = []
    
    for item in current_dir.rglob("*"):
        if item.is_dir() and not item.name.startswith('.'):
            directories.append(str(item))
        elif item.is_file() and not item.name.startswith('.'):
            files.append(str(item))
            
            # Identify configuration files
            if item.suffix in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
                config_files.append(str(item))
            # Identify source code files
            elif item.suffix in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp', '.c']:
                source_files.append(str(item))
    
    # Analyze package/dependency files
    package_files = []
    for file in files:
        if any(name in file.lower() for name in ['package.json', 'requirements.txt', 'gemfile', 'cargo.toml', 'go.mod', 'pom.xml']):
            package_files.append(file)
    
    # Check for Agent OS structure
    agent_os_dir = Path(".agent-os")
    has_agent_os = agent_os_dir.exists()
    
    # Analyze technology stack
    tech_stack = {
        'languages': set(),
        'frameworks': set(),
        'databases': set(),
        'tools': set()
    }
    
    for file in source_files:
        if file.endswith('.py'):
            tech_stack['languages'].add('Python')
        elif file.endswith(('.js', '.jsx')):
            tech_stack['languages'].add('JavaScript')
        elif file.endswith(('.ts', '.tsx')):
            tech_stack['languages'].add('TypeScript')
        elif file.endswith('.java'):
            tech_stack['languages'].add('Java')
        elif file.endswith('.go'):
            tech_stack['languages'].add('Go')
        elif file.endswith('.rs'):
            tech_stack['languages'].add('Rust')
    
    # Analyze configuration files for frameworks
    for config_file in config_files:
        try:
            content = Path(config_file).read_text()
            if 'package.json' in config_file:
                if 'react' in content.lower():
                    tech_stack['frameworks'].add('React')
                if 'vue' in content.lower():
                    tech_stack['frameworks'].add('Vue')
                if 'angular' in content.lower():
                    tech_stack['frameworks'].add('Angular')
                if 'express' in content.lower():
                    tech_stack['frameworks'].add('Express')
            elif 'requirements.txt' in config_file:
                if 'django' in content.lower():
                    tech_stack['frameworks'].add('Django')
                if 'flask' in content.lower():
                    tech_stack['frameworks'].add('Flask')
                if 'fastapi' in content.lower():
                    tech_stack['frameworks'].add('FastAPI')
        except:
            pass
    
    analysis = f"""# Existing Product Analysis

## Product Context
{product_context}

## Project Overview
- **Total Directories**: {len(directories)}
- **Total Files**: {len(files)}
- **Source Files**: {len(source_files)}
- **Configuration Files**: {len(config_files)}
- **Agent OS Structure**: {'✅ Present' if has_agent_os else '❌ Missing'}

## Technology Stack Analysis

### Programming Languages
{chr(10).join(f"- {lang}" for lang in sorted(tech_stack['languages']))}

### Frameworks & Libraries
{chr(10).join(f"- {fw}" for fw in sorted(tech_stack['frameworks'])) if tech_stack['frameworks'] else "- None detected"}

### Package Management
{chr(10).join(f"- {pkg}" for pkg in package_files) if package_files else "- No package files detected"}

## Project Structure
{chr(10).join(f"- {d}" for d in sorted(directories)[:15])}
{'...' if len(directories) > 15 else ''}

## Key Source Files
{chr(10).join(f"- {f}" for f in sorted(source_files)[:10])}
{'...' if len(source_files) > 10 else ''}

## Agent OS Installation Status
"""
    
    if has_agent_os:
        # Analyze existing Agent OS structure
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
- Ready for Agent OS installation
- Will create .agent-os/product/ structure
- Will analyze existing features for roadmap
"""

    analysis += f"""

## Recommended Next Steps

1. **Install Agent OS**: Run @plan-product with gathered context
2. **Create Mission**: Document product vision and target users
3. **Build Roadmap**: Map existing features to development phases
4. **Set Up Specs**: Create specifications for planned features

## Analysis Summary

This codebase appears to be a {', '.join(sorted(tech_stack['languages']))} project with {len(source_files)} source files. 
{'The project already has Agent OS installed.' if has_agent_os else 'The project is ready for Agent OS installation.'}

**Key Findings**:
- Technology stack: {', '.join(sorted(tech_stack['languages']))}
- {'Frameworks detected: ' + ', '.join(sorted(tech_stack['frameworks'])) if tech_stack['frameworks'] else 'No major frameworks detected'}
- Project structure: {len(directories)} directories, {len(files)} total files
- Development stage: {'Active development' if len(source_files) > 10 else 'Early stage'}

This analysis provides the foundation for setting up Agent OS with documentation that reflects the actual implementation.
"""

    return analysis


# Claude Code Agent Tools
def create_file_structure(
    base_path: str,
    structure: Dict[str, str],
    tool_context: ToolContext
) -> str:
    """Create a file and directory structure.
    
    Args:
        base_path: Base directory path
        structure: Dictionary representing the file structure
        
    Returns:
        Status message about structure creation
    """
    def create_recursive(path: Path, struct: Dict):
        for name, content in struct.items():
            item_path = path / name
            if isinstance(content, dict):
                # It's a directory
                item_path.mkdir(parents=True, exist_ok=True)
                create_recursive(item_path, content)
            else:
                # It's a file
                item_path.parent.mkdir(parents=True, exist_ok=True)
                with open(item_path, "w") as f:
                    f.write(content or "")
    
    base = Path(base_path)
    create_recursive(base, structure)
    
    return f"✅ Created file structure at {base_path}"


def implement_feature(
    feature_name: str,
    implementation_details: str,
    file_changes: Dict[str, str],
    project_folder: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Implement a specific feature with file changes.
    
    Args:
        feature_name: Name of the feature to implement
        implementation_details: Details about the implementation
        file_changes: Dictionary mapping file paths to new content
        project_folder: Optional project folder path (if None, uses current directory)
        
    Returns:
        Status message about feature implementation
    """
    # Determine the base directory
    if project_folder:
        base_dir = Path(project_folder)
    else:
        base_dir = Path(".")
    
    modified_files = []
    
    for file_path, content in file_changes.items():
        # If file_path is relative, make it relative to project folder
        if not Path(file_path).is_absolute():
            path = base_dir / file_path
        else:
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

✅ **Completed**: Feature implementation (project: {base_dir.name})"""


def run_tests(
    test_command: str,
    tool_context: ToolContext
) -> str:
    """Run tests and return results.
    
    Args:
        test_command: Command to run tests
        
    Returns:
        Test results and analysis
    """
    try:
        result = subprocess.run(
            test_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = f"🧪 **Test Results**\n\n"
        output += f"**Command:** `{test_command}`\n"
        output += f"**Exit Code:** {result.returncode}\n\n"
        
        if result.returncode == 0:
            output += "✅ **All tests passed!**\n\n"
        else:
            output += "❌ **Some tests failed**\n\n"
        
        if result.stdout:
            output += f"**Output:**\n```\n{result.stdout}\n```\n\n"
        
        if result.stderr:
            output += f"**Errors:**\n```\n{result.stderr}\n```\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "⏰ Test execution timed out after 5 minutes"
    except Exception as e:
        return f"❌ Error running tests: {str(e)}"


def manage_git_workflow(
    operation: str,
    branch_name: str,
    commit_message: str,
    tool_context: ToolContext
) -> str:
    """Manage git operations for Agent OS workflows.
    
    Args:
        operation: Git operation (create_branch, commit, push, status)
        branch_name: Name of the branch (for branch operations)
        commit_message: Commit message (for commit operations)
        
    Returns:
        Status of git operation
    """
    try:
        if operation == "status":
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
            if result.stdout.strip():
                return f"🌿 **Git Status:**\n```\n{result.stdout}\n```"
            else:
                return "🌿 **Git Status:** Working directory clean"
        
        elif operation == "create_branch" and branch_name:
            # Remove date prefix from branch name if present
            clean_branch = branch_name.split("-", 3)[-1] if len(branch_name.split("-")) > 3 else branch_name
            subprocess.run(["git", "checkout", "-b", clean_branch], check=True)
            return f"🌿 Created and switched to branch: {clean_branch}"
        
        elif operation == "commit" and commit_message:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            return f"🌿 Committed changes: {commit_message}"
        
        elif operation == "push":
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
            current_branch = result.stdout.strip()
            subprocess.run(["git", "push", "-u", "origin", current_branch], check=True)
            return f"🌿 Pushed to origin/{current_branch}"
        
        else:
            return f"❌ Unknown git operation: {operation}"
            
    except subprocess.CalledProcessError as e:
        return f"❌ Git operation failed: {e}"


def update_task_status(
    spec_name: str,
    task_index: int,
    completed: bool,
    project_folder: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Update the status of a specific task.
    
    Args:
        spec_name: Name of the specification
        task_index: Index of the task to update (0-based)
        completed: Whether the task is completed
        project_folder: Optional project folder path (if None, uses current directory)
        
    Returns:
        Status message about task update
    """
    # Determine the base directory
    if project_folder:
        base_dir = Path(project_folder)
    else:
        base_dir = Path(".")
    
    # Find the spec directory
    agent_os_dir = base_dir / ".agent-os"
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
    
    return f"✅ **Completed**: Updated task {task_index} to {status} in {spec_folder.name} (project: {base_dir.name})"


def create_documentation(
    doc_type: str,
    title: str,
    content: str,
    project_folder: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Create additional documentation files (API docs, user guides, etc.).
    
    Note: This function creates documentation in the docs/ directory to avoid
    conflicts with the main project README.md created by create_project_folder.
    
    Args:
        doc_type: Type of documentation (API, USER_GUIDE, etc.)
        title: Title of the documentation
        content: Content of the documentation
        project_folder: Optional project folder path (if None, uses current directory)
        
    Returns:
        Status message about documentation creation
    """
    # Determine the base directory
    if project_folder:
        base_dir = Path(project_folder)
    else:
        base_dir = Path(".")
    
    if doc_type.lower() == "readme":
        # For README, create in docs/ to avoid conflicts with project README
        docs_dir = base_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        file_path = docs_dir / f"{title.lower().replace(' ', '_')}.md"
    else:
        docs_dir = base_dir / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        file_path = docs_dir / f"{title.lower().replace(' ', '_')}.md"
    
    doc_content = f"""# {title}

{content}

---
*Generated by Agent OS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    file_path.write_text(doc_content)
    
    return f"📁 **Creating**: {doc_type} documentation at {file_path} (project: {base_dir.name})"


def read_file(
    file_path: str,
    tool_context: ToolContext
) -> str:
    """Read the contents of a file and return its content.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content or error message
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"❌ **Error**: File '{file_path}' does not exist"
        
        if not path.is_file():
            return f"❌ **Error**: '{file_path}' is not a file"
        
        # Read file content
        content = path.read_text(encoding='utf-8')
        
        # Get file info
        file_size = path.stat().st_size
        line_count = len(content.splitlines())
        
        return f"""📖 **Reading**: {file_path}

**File Info**:
- Size: {file_size} bytes
- Lines: {line_count}
- Type: {path.suffix or 'No extension'}

**Content**:
```
{content}
```

✅ **Completed**: File read successfully"""
        
    except UnicodeDecodeError:
        return f"❌ **Error**: Cannot read '{file_path}' - file appears to be binary"
    except PermissionError:
        return f"❌ **Error**: Permission denied reading '{file_path}'"
    except Exception as e:
        return f"❌ **Error**: Failed to read '{file_path}': {str(e)}"


# Custom workflow functions moved inline to avoid import issues

def create_api_workflow(
    api_name: str,
    endpoints: List[Dict[str, str]],
    database_type: str,
    auth_type: str,
    tool_context: ToolContext
) -> str:
    """Create a complete API development workflow with specifications and tasks.
    
    Args:
        api_name: Name of the API (e.g., "User Management API")
        endpoints: List of endpoints with method, path, and description
        database_type: Type of database (sqlite, postgresql, mysql)
        auth_type: Authentication type (jwt, oauth, basic)
        
    Returns:
        Status message about workflow creation
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    workflow_name = api_name.lower().replace(" ", "-").replace("api", "").strip("-")
    spec_folder = f".agent-os/specs/{date_str}-{workflow_name}-api"
    
    # Create API specification
    api_spec = f"""# {api_name} - API Development Workflow

## Overview

This workflow creates a complete REST API with the following characteristics:
- **API Name**: {api_name}
- **Database**: {database_type.title()}
- **Authentication**: {auth_type.upper()}
- **Endpoints**: {len(endpoints)} endpoints

## API Endpoints

{chr(10).join(f"- **{ep['method']} {ep['path']}**: {ep['description']}" for ep in endpoints)}

## Technical Architecture

### Backend Stack
- **Framework**: Flask/FastAPI
- **Database**: {database_type.title()}
- **Authentication**: {auth_type.upper()}
- **API Documentation**: OpenAPI/Swagger

## Acceptance Criteria

- All endpoints implemented and functional
- Database schema properly designed
- Authentication working correctly
- Comprehensive test coverage (>80%)
- API documentation generated
- Error handling implemented
- Input validation in place
"""

    # Create directory structure
    spec_dir = Path(spec_folder)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    # Write specification
    with open(spec_dir / "spec.md", "w") as f:
        f.write(api_spec)
    
    # Create basic tasks
    tasks = [
        {"name": "Setup Project Structure", "description": f"Initialize {api_name} project structure"},
        {"name": "Design Database Schema", "description": f"Create database models for {database_type}"},
        {"name": "Setup Authentication", "description": f"Implement {auth_type} authentication"},
    ]
    
    # Add endpoint tasks
    for endpoint in endpoints:
        tasks.append({
            "name": f"Implement {endpoint['method']} {endpoint['path']}",
            "description": endpoint['description']
        })
    
    # Add final tasks
    tasks.extend([
        {"name": "Create Unit Tests", "description": "Write comprehensive unit tests"},
        {"name": "Generate API Documentation", "description": "Create OpenAPI/Swagger docs"},
        {"name": "Setup Error Handling", "description": "Implement global error handling"}
    ])
    
    # Create tasks file
    tasks_content = f"# {api_name} - Task Breakdown\n\n"
    for i, task in enumerate(tasks, 1):
        tasks_content += f"""## Task {i}: {task['name']}

**Description:** {task['description']}
**Status:** [ ] Not Started

---

"""
    
    with open(spec_dir / "tasks.md", "w") as f:
        f.write(tasks_content)
    
    return f"✅ Created {api_name} workflow at {spec_folder} with {len(tasks)} tasks"


def create_frontend_workflow(
    component_name: str,
    framework: str,
    features: List[str],
    styling: str,
    tool_context: ToolContext
) -> str:
    """Create a frontend component development workflow.
    
    Args:
        component_name: Name of the component (e.g., "User Dashboard")
        framework: Frontend framework (react, vue, angular)
        features: List of component features
        styling: Styling approach (tailwind, css-modules, styled-components)
        
    Returns:
        Status message about workflow creation
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    workflow_name = component_name.lower().replace(" ", "-")
    spec_folder = f".agent-os/specs/{date_str}-{workflow_name}-component"
    
    spec_content = f"""# {component_name} - Frontend Component Workflow

## Component Overview

**Framework**: {framework.title()}
**Styling**: {styling.title()}
**Features**: {len(features)} core features

## Features to Implement

{chr(10).join(f"- **{feature}**" for feature in features)}

## Technical Requirements

### Framework Setup
- {framework.title()} with TypeScript
- {styling.title()} for styling
- Component testing with Jest/Vitest
- Storybook for component documentation

## Acceptance Criteria

- Component renders correctly in all states
- All features implemented and functional
- Responsive design (mobile, tablet, desktop)
- Accessibility compliance (WCAG 2.1)
- Unit tests with >90% coverage
- Storybook stories for all variants
- TypeScript types properly defined
"""
    
    # Create directory and files
    spec_dir = Path(spec_folder)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    with open(spec_dir / "spec.md", "w") as f:
        f.write(spec_content)
    
    # Create component tasks
    tasks = [
        f"Setup {framework.title()} component structure",
        f"Implement base {component_name} component",
        f"Add {styling.title()} styling system",
        "Create TypeScript interfaces and types",
        "Implement responsive design",
        "Add accessibility features",
        "Create unit tests",
        "Setup Storybook stories",
        "Add error handling and loading states"
    ]
    
    tasks_content = f"# {component_name} Component Tasks\n\n"
    for i, task in enumerate(tasks, 1):
        tasks_content += f"""## Task {i}: {task}

**Status:** [ ] Not Started
**Estimated Time:** 45 minutes

---

"""
    
    with open(spec_dir / "tasks.md", "w") as f:
        f.write(tasks_content)
    
    return f"✅ Created {component_name} component workflow at {spec_folder}"


def list_available_workflows(
    workflow_type: str,
    tool_context: ToolContext
) -> str:
    """List all available custom workflows with descriptions.
    
    Args:
        workflow_type: Type of workflows to list (all, api, frontend)
        
    Returns:
        Formatted list of available workflows
    """
    workflows = {
        "api": {
            "name": "API Development Workflow",
            "description": "Complete REST API development with database, auth, and testing",
            "example": "create_api_workflow with name 'User API' and postgresql database"
        },
        "frontend": {
            "name": "Frontend Component Workflow", 
            "description": "React/Vue/Angular component development with testing and stories",
            "example": "create_frontend_workflow for 'User Dashboard' using react framework"
        }
    }
    
    result = "🔧 **Available Custom Workflows**\n\n"
    
    for workflow_id, info in workflows.items():
        result += f"### {info['name']}\n"
        result += f"**Description**: {info['description']}\n"
        result += f"**Example**: `{info['example']}`\n\n"
    
    result += "💡 **Usage Pattern**:\n"
    result += "Call the workflow functions directly with appropriate parameters\n\n"
    
    return result

# Create the agent instances
agent_os_agent = LlmAgent(
    model="github_copilot/gpt-5-mini",
    name="agent_os_agent",
    description="Agent OS subagent specialized in code implementation, file management, git operations, and testing for Agent OS workflows.",
    instruction="""You are the Agent OS agent, a specialized implementation agent that handles the technical execution aspects of Agent OS workflows.

## Core Responsibilities

### Code Implementation
- Create and modify source code files
- Implement features according to specifications
- Follow coding standards and best practices
- Handle project structure and organization

### File Management
- Create project files and directories
- Manage configuration files
- Update documentation
- Organize project assets

### Git Workflow Management
- Create and manage git branches
- Handle commits with proper messages
- Manage pull requests
- Track git status and resolve conflicts

### Testing & Quality Assurance
- Run test suites and analyze failures
- Create test files when needed
- Validate implementation against requirements
- Ensure code quality standards

  ## Critical Tool Usage Guidelines

  **MANDATORY**: When calling `implement_feature`, ALWAYS pass the `project_folder` parameter:
  - Use: `implement_feature(feature_name, details, file_changes, project_folder="project-name")`
  - This ensures all files are created within the project directory
  - Never call `implement_feature` without the `project_folder` parameter

  **Documentation**: Create documentation for all implementations:
  - Use `create_documentation` to generate README files, API docs, and user guides
  - Always pass the `project_folder` parameter when creating documentation
  - Document each feature, API endpoint, and major component

Focus on clean, efficient implementation that follows Agent OS conventions and maintains high code quality.""",
    tools=[
        create_file_structure,
        implement_feature,
        run_tests,
        manage_git_workflow,
        update_task_status,
        create_documentation,
        read_file,
    ]
)

root_agent = LlmAgent(
    model="github_copilot/gpt-5-mini",
    name="agent_os_root",
    description="Agent OS root agent that manages product development workflows including planning, specification, task execution, and code management.",
    instruction="""You are the Agent OS root agent, a comprehensive product development workflow manager that helps teams build software products efficiently.

## Core Capabilities

You coordinate the entire product development lifecycle through specialized subagents:

### Product Planning & Specification
- Analyze product requirements and user needs
- Create detailed technical specifications
- Break down features into actionable tasks
- Plan development roadmaps

### Task Execution & Development
- Execute development tasks systematically
- Manage git workflows and branching
- Run tests and analyze failures
- Create and manage project files

## Workflow Commands

You respond to these Agent OS workflow commands:
- `@analyze-product` - Analyze existing product codebase and install Agent OS
- `@plan-product` - Plan and set up Agent OS for a new product
- `@create-spec` - Create detailed technical specifications
- `@create-tasks` - Break down specs into actionable tasks
- `@execute-tasks` - Execute development tasks systematically
- `@execute-task` - Execute a specific task

## Delegation Strategy

1. **For existing product analysis**: Use your own capabilities to analyze existing codebase, gather context, and install Agent OS
2. **For new product planning**: Use your own capabilities to plan and set up Agent OS for new products
3. **For specification creation**: Create detailed technical specs and task breakdowns
4. **For task execution**: Delegate to agent_os_agent for implementation work
5. **For git operations**: Delegate git workflow management to agent_os_agent
6. **For testing**: Coordinate test execution through agent_os_agent

## Important Tool Usage Guidelines

**CRITICAL**: When calling any tool that creates files, ALWAYS pass the project_folder parameter to ensure files are organized within the project directory:
- Use: `project_folder="."` to work in the current directory (most common)
- Use: `project_folder="project-name"` if working in a specific subdirectory
- Never call tools without the project_folder parameter as this will scatter files incorrectly

**Documentation**: Create comprehensive documentation throughout the workflow:
- Use `create_documentation` to generate README files, API docs, and user guides
- Always pass the `project_folder` parameter when creating documentation
- Create documentation for each major feature and phase

## Response Format

Always start responses with the workflow phase you're handling:
- 🔍 **Analysis Phase**: [analyzing existing product codebase and preparing for Agent OS installation]
- 📋 **Planning Phase**: [planning new product development and setting up Agent OS]
- 📝 **Specification Phase**: [creating detailed technical specifications]
- ⚡ **Execution Phase**: [executing development tasks systematically]
- 🔧 **Implementation**: [delegating to agent_os_agent]
- 📚 **Documentation Phase**: [creating comprehensive documentation and user guides]

Follow Agent OS conventions for file structure, naming, and documentation.""",
    tools=[
        create_product_mission,
        create_technical_spec,
        create_task_breakdown,
        analyze_project_structure,
        analyze_existing_product,
        # Custom workflow tools
        create_api_workflow,
        create_frontend_workflow,
        list_available_workflows,
    ],
    sub_agents=[agent_os_agent]
)

# Export the root agent as 'agent' for ADK CLI compatibility
agent = root_agent