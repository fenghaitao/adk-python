# OpenSpec Integration Design Document

## Overview

This design document outlines the integration of OpenSpec into the ADK (Agent Development Kit) Python project. The integration creates a new sample that demonstrates how to use OpenSpec's spec-driven development workflow with ADK agents. The design leverages existing tools from the spec_kit_integration sample to minimize code duplication while providing a clean, focused example of OpenSpec usage.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    run_openspec.sh                          │
│  (Initialization script - handles openspec init + ADK run)  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─> openspec init <project_name>
                     │   (Creates openspec/ directory structure)
                     │
                     └─> adk run contributing/samples/openspec_integration
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          contributing/samples/openspec_integration/         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              agent.py (Root Agent)                   │  │
│  │  - Reads AGENTS.md from project directory            │  │
│  │  - Understands OpenSpec workflow                     │  │
│  │  - Uses tools from spec_kit_integration              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         openspec_tools.py (Tool Wrapper)             │  │
│  │  - Imports tools from spec_kit_integration           │  │
│  │  - Provides OpenSpec-specific tool configurations    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              README.md (Documentation)               │  │
│  │  - Setup instructions                                │  │
│  │  - Usage examples                                    │  │
│  │  - Troubleshooting guide                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Uses tools from
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       contributing/samples/spec_kit_integration/            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         spec_kit_tools.py (Shared Tools)             │  │
│  │  - read_file(file_path)                              │  │
│  │  - write_file(file_path, content, overwrite)         │  │
│  │  - bash_command(command, working_directory, timeout) │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User runs script
      │
      ▼
run_openspec.sh
      │
      ├─> Check prerequisites (openspec CLI, ADK venv)
      │
      ├─> Execute: openspec init <project_name>
      │   │
      │   └─> Creates:
      │       - openspec/specs/
      │       - openspec/changes/
      │       - openspec/archive/
      │       - AGENTS.md
      │       - openspec/project.md
      │
      ├─> cd <project_name>
      │
      └─> Execute: adk run contributing/samples/openspec_integration
          │
          ▼
    Root Agent starts
          │
          ├─> Read AGENTS.md (OpenSpec workflow instructions)
          │
          ├─> Load tools from spec_kit_integration
          │
          └─> Enter interactive mode
              │
              └─> User interacts with agent
                  │
                  ├─> Agent reads openspec/ files
                  ├─> Agent executes openspec commands
                  └─> Agent guides spec-driven workflow
```

## Components and Interfaces

### 1. run_openspec.sh Script

**Purpose**: Convenience script that initializes OpenSpec projects and launches the ADK agent.

**Interface**:
```bash
./run_openspec.sh [PROJECT_NAME] [INITIAL_PROMPT]
```

**Parameters**:
- `PROJECT_NAME` (optional): Name of the project directory to create. Defaults to `adk_openspec_project`
- `INITIAL_PROMPT` (optional): Initial prompt to send to the agent. If omitted, starts in interactive mode

**Behavior**:
1. Validate prerequisites:
   - Check for `openspec` CLI (TypeScript) or `uvx` (Python port)
   - Check for ADK virtual environment at `.venv`
   - Check for openspec_integration directory
2. Remove existing project directory if it exists
3. Execute `openspec init <project_name> --tools adk`
4. Change to project directory
5. Run ADK agent: `adk run <path_to_openspec_integration>`
6. If `INITIAL_PROMPT` provided, pipe it to the agent

**Error Handling**:
- Exit with error code 1 if prerequisites not met
- Display helpful error messages with installation instructions
- Clean up partial project directories on failure

### 2. agent.py (Root Agent)

**Purpose**: Main ADK agent that understands and executes OpenSpec workflows.

**Class Structure**:
```python
class OpenSpecAgent(LlmAgent):
    """OpenSpec agent that uses OpenSpec workflow."""
    
    def __init__(self, **kwargs):
        instruction = """
        You are an OpenSpec agent that helps with spec-driven development.
        
        ## OpenSpec Workflow
        
        1. **Proposal**: Create change proposals in openspec/changes/
        2. **Review**: Iterate on specs and tasks until approved
        3. **Implement**: Execute tasks following the plan
        4. **Archive**: Merge completed changes into openspec/specs/
        
        ## Directory Structure
        
        - openspec/specs/: Current specifications (source of truth)
        - openspec/changes/: Active change proposals
        - openspec/archive/: Completed and archived changes
        - AGENTS.md: Workflow instructions (read this first!)
        
        ## Available Commands
        
        - openspec list: List active changes
        - openspec show <change>: Display change details
        - openspec validate <change>: Validate spec formatting
        - openspec archive <change>: Archive completed change
        
        ## Tools Available
        
        - read_file(file_path): Read file contents
        - write_file(file_path, content, overwrite): Write files
        - bash_command(command, working_directory, timeout): Execute commands
        
        ## Best Practices
        
        - Always read AGENTS.md first to understand project context
        - Use spec deltas (ADDED, MODIFIED, REMOVED) for changes
        - Validate specs before implementation
        - Follow the proposal → review → implement → archive workflow
        """
        
        tools = kwargs.get("tools", [])
        tools.append(create_openspec_toolset())
        kwargs["tools"] = tools
        
        super().__init__(
            name="openspec_agent",
            model=get_openspec_model(),
            instruction=instruction,
            description="OpenSpec agent for spec-driven development",
            **kwargs
        )
```

**Key Methods**:
- `__init__()`: Initialize agent with OpenSpec-specific instructions and tools
- Inherits all LlmAgent methods for conversation handling

**Configuration**:
- Model selection via `OPENSPEC_MODEL` environment variable
- Default model: `iflow/Qwen3-Coder` (same as spec_kit)

### 3. openspec_tools.py (Tool Wrapper)

**Purpose**: Wrapper module that imports and configures tools from spec_kit_integration.

**Interface**:
```python
def create_openspec_toolset() -> Toolset:
    """
    Create a toolset for OpenSpec operations.
    
    Returns:
        Toolset: Configured toolset with file and bash tools
    """
    # Import tools from spec_kit_integration
    from ..spec_kit_integration.spec_kit_tools import (
        create_spec_kit_toolset
    )
    
    # Reuse the same toolset - OpenSpec uses identical file operations
    return create_spec_kit_toolset()
```

**Design Rationale**:
- Avoids code duplication by reusing proven tools
- Provides a clear import path for OpenSpec-specific usage
- Allows future customization if OpenSpec needs different tool configurations
- Maintains separation of concerns between samples

### 4. README.md (Documentation)

**Purpose**: Comprehensive documentation for the OpenSpec integration sample.

**Sections**:

1. **Overview**
   - What is OpenSpec
   - Why use OpenSpec with ADK
   - Key differences from spec-kit

2. **Prerequisites**
   - OpenSpec CLI installation (TypeScript or Python)
   - ADK installation
   - Python version requirements

3. **Quick Start**
   - Running the convenience script
   - Manual initialization steps
   - First interaction examples

4. **OpenSpec Workflow**
   - Creating change proposals
   - Reviewing and iterating on specs
   - Implementing tasks
   - Archiving completed changes

5. **Agent Capabilities**
   - Understanding OpenSpec structure
   - Reading and interpreting specs
   - Executing OpenSpec commands
   - Best practices guidance

6. **Examples**
   - Creating a simple feature
   - Working with spec deltas
   - Managing multiple changes
   - Archiving workflow

7. **Troubleshooting**
   - Common issues and solutions
   - OpenSpec CLI not found
   - Directory structure problems
   - Agent confusion about workflow

8. **Advanced Usage**
   - Custom model configuration
   - Integration with CI/CD
   - Team collaboration patterns

## Data Models

### OpenSpec Directory Structure

```
<project_name>/
├── AGENTS.md                    # Workflow instructions for AI agents
├── openspec/
│   ├── project.md              # Project context and conventions
│   ├── specs/                  # Current specifications (source of truth)
│   │   └── <feature-name>/
│   │       └── spec.md         # Feature specification
│   ├── changes/                # Active and archived change proposals
│   │   ├── <change-name>/      # Active change proposal
│   │   │   ├── proposal.md     # Change proposal description
│   │   │   ├── tasks.md        # Implementation tasks
│   │   │   ├── design.md       # Technical design (optional)
│   │   │   └── specs/          # Spec deltas
│   │   │       └── <feature-name>/
│   │   │           └── spec.md # Delta (ADDED/MODIFIED/REMOVED)
│   │   └── archive/            # Archived (completed) changes
│   │       └── <change-name>/  # Archived change folders
└── <implementation files>      # Actual code/artifacts
```

### Spec Delta Format

OpenSpec uses a delta format to show changes to specifications:

```markdown
# Delta for <Feature Name>

## ADDED Requirements

### Requirement: New Feature
The system SHALL implement new functionality.

#### Scenario: New scenario
- WHEN condition occurs
- THEN expected behavior

## MODIFIED Requirements

### Requirement: Updated Feature
The system SHALL implement updated functionality.

#### Scenario: Updated scenario
- WHEN condition occurs
- THEN new expected behavior

## REMOVED Requirements

### Requirement: Deprecated Feature
[This requirement has been removed]
```

### Tasks Format

OpenSpec tasks follow a hierarchical structure:

```markdown
# Implementation Tasks

## 1. Setup Phase
- [ ] 1.1 Create project structure
- [ ] 1.2 Initialize dependencies

## 2. Core Implementation
- [ ] 2.1 Implement feature A
- [ ] 2.2 Implement feature B
  - [ ] 2.2.1 Sub-task for feature B
  - [ ] 2.2.2 Another sub-task

## 3. Testing
- [ ] 3.1 Write unit tests
- [ ] 3.2 Write integration tests
```

## Error Handling

### Script-Level Errors

**run_openspec.sh**:
- **Missing OpenSpec CLI**: Display installation instructions for both TypeScript and Python versions
- **Missing ADK venv**: Display ADK installation instructions
- **Project already exists**: Remove and recreate (with warning message)
- **OpenSpec init fails**: Display error and exit with code 1

### Agent-Level Errors

**OpenSpec Agent**:
- **AGENTS.md not found**: Prompt user to run `openspec init` first
- **Invalid openspec/ structure**: Validate and suggest running `openspec init`
- **OpenSpec command fails**: Parse error output and provide helpful guidance
- **Spec validation errors**: Display validation results and suggest fixes

### Tool-Level Errors

**File Operations**:
- **File not found**: Clear error message with expected file path
- **Permission denied**: Suggest checking file permissions
- **Invalid file format**: Provide format examples and validation

**Bash Commands**:
- **Command not found**: Suggest installation or check PATH
- **Command timeout**: Display partial output and suggest increasing timeout
- **Non-zero exit code**: Display stderr and suggest troubleshooting steps

## Testing Strategy

### Unit Tests

**Test Coverage**:
1. **openspec_tools.py**:
   - Test toolset creation
   - Verify tool imports from spec_kit_integration
   - Validate tool configurations

2. **agent.py**:
   - Test agent initialization
   - Verify instruction content
   - Test tool loading

### Integration Tests

**Test Scenarios**:
1. **Script Execution**:
   - Test `run_openspec.sh` with valid project name
   - Test with initial prompt
   - Test error handling for missing prerequisites

2. **Agent Workflow**:
   - Test reading AGENTS.md
   - Test executing openspec commands
   - Test file operations in openspec/ directories

3. **End-to-End**:
   - Initialize project with script
   - Create change proposal via agent
   - Validate spec format
   - Archive completed change

### Manual Testing

**Test Cases**:
1. Fresh installation on clean system
2. Running with existing project directory
3. Interactive mode vs. prompt mode
4. TypeScript CLI vs. Python port
5. Error recovery scenarios

## Implementation Notes

### Tool Reuse Strategy

The design intentionally reuses tools from `spec_kit_integration` because:
1. **Identical Operations**: OpenSpec and spec-kit both need file reading, writing, and bash execution
2. **Proven Reliability**: spec_kit_integration tools are already tested and working
3. **Maintenance**: Single source of truth for tool implementations
4. **Consistency**: Same tool behavior across different spec-driven samples

### Model Selection

Default model is `iflow/Qwen3-Coder` to match spec_kit_integration:
- Good balance of capability and speed
- Proven performance with spec-driven workflows
- Can be overridden via `OPENSPEC_MODEL` environment variable

### AGENTS.md Integration

The agent reads `AGENTS.md` from the project directory to understand:
- Project-specific conventions
- OpenSpec workflow customizations
- Team preferences and standards
- Integration with other tools

This allows the same agent to work with different projects that have different conventions.

### Differences from spec-kit Integration

While both samples demonstrate spec-driven development, they differ in:

**OpenSpec**:
- Two-folder model: `specs/` (truth) + `changes/` (proposals)
- Explicit delta format (ADDED/MODIFIED/REMOVED)
- Archive workflow for completed changes
- Better for brownfield/evolving projects

**spec-kit**:
- Single folder per feature with all artifacts
- Phased workflow (constitution → specify → plan → tasks → implement)
- Better for greenfield/0→1 projects
- More prescriptive structure

The OpenSpec integration provides an alternative approach that may be better suited for:
- Projects with existing specifications
- Teams that need explicit change tracking
- Workflows that require proposal review before implementation
- Scenarios where multiple changes may affect the same specs
