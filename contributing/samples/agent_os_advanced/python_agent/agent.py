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

## Users

### Primary Customers

{target_users}

## Key Features

### Core Features

{chr(10).join(f"- **{feature}**" for feature in key_features)}

## The Problem

### Need for {product_name}

[Problem description to be filled based on user research]

**Our Solution:** {description}

## Differentiators

### Comprehensive Functionality

[Differentiators to be defined based on competitive analysis]
"""
    
    # Create .agent-os directory structure if it doesn't exist
    agent_os_dir = Path(".agent-os/product")
    agent_os_dir.mkdir(parents=True, exist_ok=True)
    
    # Write mission file
    mission_file = agent_os_dir / "mission.md"
    with open(mission_file, "w") as f:
        f.write(mission_content)
    
    return f"✅ Created product mission at {mission_file}"


def create_technical_spec(
    spec_name: str,
    feature_description: str,
    technical_approach: str,
    acceptance_criteria: List[str],
    tool_context: ToolContext
) -> str:
    """Create a technical specification following Agent OS structure.
    
    Args:
        spec_name: Name of the specification
        feature_description: Description of the feature
        technical_approach: Technical implementation approach
        acceptance_criteria: List of acceptance criteria
        
    Returns:
        Status message about spec creation
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    spec_folder = f".agent-os/specs/{date_str}-{spec_name.lower().replace(' ', '-')}"
    
    spec_content = f"""# {spec_name}

## Overview

{feature_description}

## Technical Approach

{technical_approach}

## Acceptance Criteria

{chr(10).join(f"- {criteria}" for criteria in acceptance_criteria)}

## Implementation Details

[To be filled during implementation]

## Testing Strategy

[To be defined based on requirements]
"""
    
    spec_lite_content = f"""# {spec_name} - Specification Summary

## Feature Summary

{feature_description}

## Key Requirements

{chr(10).join(f"- {criteria}" for criteria in acceptance_criteria)}
"""
    
    # Create spec directory structure
    spec_dir = Path(spec_folder)
    spec_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sub-specs directory
    sub_specs_dir = spec_dir / "sub-specs"
    sub_specs_dir.mkdir(exist_ok=True)
    
    # Write specification files
    with open(spec_dir / "spec.md", "w") as f:
        f.write(spec_content)
    
    with open(spec_dir / "spec-lite.md", "w") as f:
        f.write(spec_lite_content)
    
    # Create technical spec
    tech_spec_content = f"""# Technical Specification - {spec_name}

## Architecture

{technical_approach}

## Implementation Plan

[Detailed implementation steps to be defined]

## Dependencies

[External dependencies and requirements]
"""
    
    with open(sub_specs_dir / "technical-spec.md", "w") as f:
        f.write(tech_spec_content)
    
    return f"✅ Created technical specification at {spec_folder}"


def create_task_breakdown(
    spec_folder: str,
    tasks: List[Dict[str, str]],
    tool_context: ToolContext
) -> str:
    """Create a task breakdown file for a specification.
    
    Args:
        spec_folder: Path to the specification folder
        tasks: List of tasks with 'name' and 'description' keys
        
    Returns:
        Status message about task creation
    """
    tasks_content = f"""# Tasks for {spec_folder}

## Task Breakdown

"""
    
    for i, task in enumerate(tasks, 1):
        tasks_content += f"""### Task {i}: {task['name']}

**Description:** {task['description']}

**Status:** [ ] Not Started

**Acceptance Criteria:**
- Implementation complete
- Tests passing
- Documentation updated

---

"""
    
    # Write tasks file
    tasks_file = Path(spec_folder) / "tasks.md"
    with open(tasks_file, "w") as f:
        f.write(tasks_content)
    
    return f"✅ Created task breakdown at {tasks_file}"


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
    file_path: str,
    implementation_code: str,
    tool_context: ToolContext
) -> str:
    """Implement a feature by creating or updating a file.
    
    Args:
        feature_name: Name of the feature being implemented
        file_path: Path to the file to create/update
        implementation_code: Code to write to the file
        
    Returns:
        Status message about implementation
    """
    file = Path(file_path)
    file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file, "w") as f:
        f.write(implementation_code)
    
    return f"🔨 Implemented {feature_name} in {file_path}"


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
    tasks_file: str,
    task_number: int,
    status: str,
    tool_context: ToolContext
) -> str:
    """Update the status of a task in a tasks.md file.
    
    Args:
        tasks_file: Path to the tasks.md file
        task_number: Number of the task to update
        status: New status (completed, in_progress, not_started)
        
    Returns:
        Status message about the update
    """
    file_path = Path(tasks_file)
    if not file_path.exists():
        return f"❌ Tasks file not found: {tasks_file}"
    
    with open(file_path, "r") as f:
        content = f.read()
    
    # Update task status based on the status parameter
    status_markers = {
        "completed": "[x]",
        "in_progress": "[-]", 
        "not_started": "[ ]"
    }
    
    marker = status_markers.get(status, "[ ]")
    
    # Simple replacement - in a real implementation, you'd want more sophisticated parsing
    lines = content.split("\n")
    updated_lines = []
    
    for line in lines:
        if f"Task {task_number}:" in line:
            # Update the next status line
            updated_lines.append(line)
            continue
        elif "**Status:**" in line and len(updated_lines) > 0 and f"Task {task_number}:" in updated_lines[-1]:
            updated_lines.append(f"**Status:** {marker} {status.replace('_', ' ').title()}")
            continue
        updated_lines.append(line)
    
    with open(file_path, "w") as f:
        f.write("\n".join(updated_lines))
    
    return f"✅ Updated Task {task_number} status to: {status}"


def create_documentation(
    doc_type: str,
    file_path: str,
    content: str,
    tool_context: ToolContext
) -> str:
    """Create documentation files.
    
    Args:
        doc_type: Type of documentation (readme, api, user_guide)
        file_path: Path where to create the documentation
        content: Content of the documentation
        
    Returns:
        Status message about documentation creation
    """
    file = Path(file_path)
    file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add appropriate headers based on doc type
    if doc_type == "readme":
        full_content = f"# {file.stem.replace('_', ' ').title()}\n\n{content}"
    elif doc_type == "api":
        full_content = f"# API Documentation\n\n{content}"
    elif doc_type == "user_guide":
        full_content = f"# User Guide\n\n{content}"
    else:
        full_content = content
    
    with open(file, "w") as f:
        f.write(full_content)
    
    return f"📝 Created {doc_type} documentation at {file_path}"


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
claude_code_agent = LlmAgent(
    model="github_copilot/gpt-5-mini",
    name="claude_code_agent",
    description="Claude Code subagent specialized in code implementation, file management, git operations, and testing for Agent OS workflows.",
    instruction="""You are the Claude Code agent, a specialized implementation agent that handles the technical execution aspects of Agent OS workflows.

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

Focus on clean, efficient implementation that follows Agent OS conventions and maintains high code quality.""",
    tools=[
        create_file_structure,
        implement_feature,
        run_tests,
        manage_git_workflow,
        update_task_status,
        create_documentation,
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
- `@plan-product` - Analyze and plan product development
- `@create-spec` - Create detailed technical specifications
- `@create-tasks` - Break down specs into actionable tasks
- `@execute-tasks` - Execute development tasks systematically
- `@execute-task` - Execute a specific task

## Delegation Strategy

1. **For product planning**: Use your own capabilities to analyze requirements and create plans
2. **For specification creation**: Create detailed technical specs and task breakdowns
3. **For task execution**: Delegate to claude_code_agent for implementation work
4. **For git operations**: Delegate git workflow management to claude_code_agent
5. **For testing**: Coordinate test execution through claude_code_agent

Always start responses with the workflow phase you're handling and follow Agent OS conventions.""",
    tools=[
        create_product_mission,
        create_technical_spec,
        create_task_breakdown,
        analyze_project_structure,
        # Custom workflow tools
        create_api_workflow,
        create_frontend_workflow,
        list_available_workflows,
    ],
    sub_agents=[claude_code_agent]
)

# Export the root agent as 'agent' for ADK CLI compatibility
agent = root_agent