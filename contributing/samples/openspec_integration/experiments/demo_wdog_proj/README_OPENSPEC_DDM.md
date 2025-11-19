# OpenSpec DDM Orchestrator - User Guide

This guide explains how to use the `run_openspec_from_ddm.py` script to orchestrate OpenSpec AI agents for implementing Simics DDM device models.

## Overview

The OpenSpec DDM Orchestrator automates the process of:
1. **Parsing** hardware specifications to extract register definitions
2. **Generating** structured tasks for register implementations and tests
3. **Creating** OpenSpec change proposals for each task
4. **Initializing** Git repository for version control
5. **Archiving** completed changes automatically
6. **Committing** each task to Git with descriptive messages
7. **Orchestrating** AI agents to implement the tasks

This allows you to leverage AI agents to handle the repetitive work of implementing device registers and their side effects, while maintaining clean version control and documentation.

## New Features ✨

### 1. Automatic Git Integration
- **Auto-Initialize**: Creates Git repository if it doesn't exist
- **Auto-Commit**: Commits changes after each completed task
- **Smart .gitignore**: Excludes build artifacts automatically
- **Descriptive Messages**: Each commit includes change ID and task title
- **Clean History**: One commit per register implementation

### 2. OpenSpec Archiving
- **Auto-Archive**: Moves completed proposals to `openspec/changes/archive/`
- **Spec Updates**: OpenSpec updates specifications automatically
- **Clean Workspace**: Active vs. completed changes clearly separated
- **Traceability**: Archived changes linked to Git commits

## Prerequisites

1. **OpenSpec Framework** installed and configured
   - Location: `~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv`
   - Activated via: `source ~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate`

2. **ADK Virtual Environment** set up
   - Should be in the adk-openspec directory

3. **Bash Shell** (required for OpenSpec venv activation)

4. **Python 3.8+** for running the orchestrator script

## Quick Start

### Example 1: Basic Usage (This Project)

```bash
# From the project root
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj

# Run the orchestrator
python3 run_openspec_from_ddm.py \
    --project . \
    --dml modules/demo_watchdog/demo_watchdog.dml \
    --spec wdt.md
```

### Example 2: With Custom Model and Port

```bash
python3 run_openspec_from_ddm.py \
    --project . \
    --dml modules/demo_watchdog/demo_watchdog.dml \
    --spec wdt.md \
    --model iflow/qwen3-coder-plus \
    --port 8052
```

### Example 3: Limit Number of Tasks

```bash
# Only generate first 5 tasks (useful for testing)
python3 run_openspec_from_ddm.py \
    --project . \
    --dml modules/demo_watchdog/demo_watchdog.dml \
    --spec wdt.md \
    --max-tasks 5
```

## Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--project` | Yes | - | Path to DDM project root directory |
| `--dml` | Yes | - | Relative path to DML file from project root |
| `--spec` | Yes | - | Path to hardware spec (absolute or relative to project) |
| `--model` | No | `iflow/Qwen3-Coder` | LLM model to use for agents |
| `--port` | No | `8051` | MCP server port |
| `--max-tasks` | No | All tasks | Maximum number of tasks to generate |
| `--openspec-venv` | No | Auto-detected | Path to OpenSpec virtual environment |
| `--output-summary` | No | `openspec_tasks_summary.json` | Output file for task summary |

### Available Models

- `iflow/Qwen3-Coder` (default)
- `iflow/qwen3-coder-plus`
- `github_copilot/claude-sonnet-4`
- `github_copilot/claude-sonnet-4.5`
- `github_copilot/grok-code-fast-1`

## What the Script Does

### Step 1: Parse Hardware Specification

The script parses your hardware specification document (markdown format) to extract:
- Register names and addresses
- Register widths and access types (R/W/RW)
- Reset values
- Field definitions
- Side effects (interrupts, resets, counters, etc.)

**Example Output:**
```
📖 Step 1: Parsing hardware specification...
✅ Found 8 registers
   - WDOGLOAD @ 0x00 (32-bit, RW)
   - WDOGVALUE @ 0x04 (32-bit, R)
   - WDOGCONTROL @ 0x08 (32-bit, RW)
   - WDOGINTCLR @ 0x0C (32-bit, W)
   ...
```

### Step 2: Generate Implementation Tasks

For each register, the script creates two tasks:
1. **Register Implementation Task**: Implement the register in DML with all side effects
2. **Test Implementation Task**: Create Python tests to verify the register behavior

Plus one **Integration Task** that ties everything together.

**Example Output:**
```
📋 Step 2: Generating implementation tasks...
✅ Generated 17 tasks:
   [task-001] Implement WDOGLOAD register logic
   [task-002] Create tests for WDOGLOAD register (depends on: task-001)
   [task-003] Implement WDOGVALUE register logic
   [task-004] Create tests for WDOGVALUE register (depends on: task-003)
   ...
```

### Step 3: Create OpenSpec Change Proposals

For each task (except integration), the script creates an OpenSpec change proposal with:
- `proposal.md`: Detailed description of the change
- `tasks.md`: Checklist of subtasks

**Structure:**
```
openspec/
└── changes/
    ├── implement-wdogload/
    │   ├── proposal.md
    │   └── tasks.md
    ├── implement-wdogvalue/
    │   ├── proposal.md
    │   └── tasks.md
    └── ...
```

### Step 3.5: Initialize Git Repository

The script automatically initializes a Git repository if one doesn't exist:
- Creates `.git/` directory
- Generates `.gitignore` for build artifacts
- Makes initial commit with all project files

**Example Output:**
```
🔧 Step 3.5: Setting up Git repository...
✅ Git repository initialized with initial commit
```

**Generated .gitignore:**
```gitignore
# Build artifacts
*.o
*.so
*.pyc
__pycache__/
.venv/
*.egg-info/

# IDE
.vscode/
.idea/

# Simics specific
linux64/
*.d

# Temporary files
*.log
*.tmp
```

### Step 4: Generate Orchestration Script

Creates `run_all_openspec_tasks.sh` with commands to:
1. Run OpenSpec agents for each task
2. Archive completed changes with `openspec archive`
3. Commit changes to Git after each task

**Key Features:**
- Archiving function included
- Git commit function with descriptive messages
- Clean workflow for each task

### Step 5: Generate Task Summary

Creates `openspec_tasks_summary.json` with complete task details in JSON format for automation.

## Generated Files

After running the script, you'll have:

```
demo_wdog_proj/
├── .git/                              # Git repository
├── .gitignore                         # Generated
├── run_openspec_from_ddm.py          # This orchestrator script
├── run_all_openspec_tasks.sh         # Generated: Run all tasks
├── openspec_tasks_summary.json       # Generated: Task details (JSON)
├── openspec/
│   └── changes/
│       ├── archive/                   # Completed changes move here
│       ├── implement-wdogload/
│       │   ├── proposal.md
│       │   └── tasks.md
│       ├── implement-wdogvalue/
│       │   ├── proposal.md
│       │   └── tasks.md
│       └── ... (more change proposals)
└── modules/
    └── demo_watchdog/
        └── test/
            └── (test files will be created by agents)
```

## Git and OpenSpec Archiving Workflow

### How Archiving Works

When a task is completed, the orchestrator performs two key operations:

#### 1. OpenSpec Archive
```bash
openspec archive <change-id> --message "Completed: task title"
```

**What happens:**
- Proposal moves from `openspec/changes/<change-id>/` to `openspec/changes/archive/<change-id>/`
- OpenSpec updates the project specifications
- Change is marked as deployed/completed
- Keeps workspace clean (active vs. completed changes)

#### 2. Git Commit
```bash
git add .
git commit -m "✅ Completed: task title

Change ID: <change-id>
Task completed and archived by OpenSpec orchestrator."
```

**What happens:**
- All changes (DML code, tests, archived proposals) are committed
- Descriptive commit message with change ID
- Clean Git history showing project progression
- Easy to roll back or review specific implementations

### Typical Workflow

```bash
# 1. Generate tasks and proposals
python3 run_openspec_from_ddm.py --project . --dml ... --spec ...
# Git initialized automatically
# Initial commit created

# 2. Implement first register (using OpenSpec agent)
# Agent implements WDOGLOAD register

# 3. Complete the task
openspec archive implement-watchdog-load --message "Completed WDOGLOAD"
git add .
git commit -m "✅ Completed: implement watchdog load"

# 4. Repeat for each register
# Each gets its own commit

# 5. View progress
git log --oneline
# Shows clean history of all implementations

# 6. Check what's left
ls openspec/changes/         # Active proposals
ls openspec/changes/archive/ # Completed proposals
```

### Git History Example

```
$ git log --oneline
a1b2c3d ✅ Completed: implement watchdog lock
e4f5g6h ✅ Completed: implement watchdog interrupt status
i7j8k9l ✅ Completed: implement watchdog control
m0n1o2p ✅ Completed: implement watchdog value
q3r4s5t ✅ Completed: implement watchdog load
u6v7w8x Initial commit - OpenSpec DDM project setup
```

### Benefits of This Approach

1. **Traceability**: Each register implementation is a separate commit
2. **Rollback**: Easy to revert specific implementations if needed
3. **Review**: Clear what changed for each register
4. **Collaboration**: Team members can see progression
5. **Clean Workspace**: Active vs. completed proposals clearly separated
6. **Spec Updates**: OpenSpec keeps specifications in sync
7. **Audit Trail**: Full history of development process

## How to Use the Generated Output

### Option 1: Run the Orchestration Script (Automated)

```bash
# Review the script first
cat run_all_openspec_tasks.sh

# Edit the script to uncomment the actual OpenSpec commands
# (They are commented out by default for safety)
vim run_all_openspec_tasks.sh

# Run all tasks
bash run_all_openspec_tasks.sh
```

### Option 2: Manual OpenSpec Execution (Recommended)

```bash
# 1. Activate OpenSpec environment
source ~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate

# 2. Review change proposals
ls -la openspec/changes/
cat openspec/changes/implement-wdogload/proposal.md

# 3. Work on a specific change
cd openspec/changes/implement-wdogload

# 4. Use OpenSpec CLI to implement
openspec apply implement-wdogload

# 5. Validate the change
openspec validate implement-wdogload --strict

# 6. Repeat for other changes
```

### Option 3: Interactive OpenSpec Session

```bash
# Use the example script from adk-openspec
/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/run_openspec.sh \
    demo_wdog_proj \
    "Please implement all the watchdog registers according to the proposals in openspec/changes/" \
    --model iflow/Qwen3-Coder \
    --save-session
```

## Customizing the Hardware Spec Parser

The script includes a `HardwareSpecParser` class that extracts register information from markdown files. If your specification format is different, you can customize:

### Current Assumptions

- Registers are identified by headers like: `## RegisterName register [0xAddress]`
- Properties are in Chinese or English (e.g., "位宽：32位" or "Width: 32")
- Tables use markdown format with columns: Bit, Name, R/W, Reset, Description
- Side effects are detected by keywords: interrupt, reset, reload, clear, trigger, enable, disable, counter, timer

### Customization Points

Edit the `HardwareSpecParser` class methods:

```python
# In run_openspec_from_ddm.py

class HardwareSpecParser:
    def parse_registers(self):
        # Customize the regex pattern for your spec format
        register_pattern = r'your_custom_pattern'
        
    def _extract_width(self, content):
        # Customize width extraction
        
    def _extract_access_type(self, content):
        # Customize access type extraction
        
    # ... etc.
```

## Task Structure

Each task contains:

```json
{
  "task_id": "task-001",
  "title": "Implement WDOGLOAD register logic",
  "description": "Detailed description with register specs and requirements",
  "register": {
    "name": "WDOGLOAD",
    "address": "0x00",
    "width": 32,
    "access": "RW",
    "reset_value": "0xFFFFFFFF",
    "description": "...",
    "fields": [...],
    "side_effects": [...]
  },
  "task_type": "register_impl",
  "dependencies": [],
  "files_to_modify": ["modules/demo_watchdog/demo_watchdog.dml"],
  "priority": 1
}
```

## Workflow Integration

### Typical Development Flow

1. **Run the orchestrator** to generate tasks and proposals
2. **Review the task summary** to understand what will be implemented
3. **Prioritize tasks** based on dependencies and importance
4. **Use OpenSpec agents** to implement high-priority tasks first
5. **Validate implementations** using `openspec validate`
6. **Run tests** to verify register behavior
7. **Iterate** on any failing tests or incorrect implementations

### Integration with Existing Workflows

- **CI/CD**: Use the JSON summary file to integrate with build systems
- **Issue Tracking**: Generate GitHub/JIRA issues from tasks
- **Code Review**: Review generated OpenSpec proposals before implementation
- **Documentation**: Use proposals as implementation documentation

## Troubleshooting

### Issue: No registers found

**Cause**: Specification format doesn't match expected pattern

**Solution**: 
- Check the register header format in your spec
- Customize the `register_pattern` in `HardwareSpecParser.parse_registers()`
- Add debug print statements to see what's being parsed

### Issue: OpenSpec venv not found

**Cause**: OpenSpec installation path is different

**Solution**:
```bash
python3 run_openspec_from_ddm.py \
    --openspec-venv /your/custom/path/.venv \
    ...
```

### Issue: Tasks not specific enough

**Cause**: Hardware spec lacks detailed side effect descriptions

**Solution**:
- Enhance your hardware spec with more details
- Manually edit the generated `proposal.md` files
- Add custom side effects in the task descriptions

## Advanced Usage

### Using with Multiple Device Models

```bash
# Process multiple devices in sequence
for device in watchdog timer uart spi; do
    python3 run_openspec_from_ddm.py \
        --project . \
        --dml modules/${device}/${device}.dml \
        --spec specs/${device}.md \
        --output-summary ${device}_tasks.json
done
```

### Programmatic Access

```python
# Use as a library
from run_openspec_from_ddm import HardwareSpecParser, TaskGenerator

# Parse your spec
parser = HardwareSpecParser("path/to/spec.md")
registers = parser.parse_registers()

# Generate tasks
task_gen = TaskGenerator("/project/path", "device.dml", "spec.md")
tasks = task_gen.generate_tasks(registers)

# Process tasks programmatically
for task in tasks:
    # Your custom logic here
    pass
```

## Best Practices

1. **Review Generated Proposals**: Always review the generated change proposals before implementing
2. **Start Small**: Use `--max-tasks 3` to test the workflow with a few tasks first
3. **Validate Frequently**: Run `openspec validate` after each implementation
4. **Test Incrementally**: Implement and test one register at a time
5. **Document Deviations**: If you deviate from the spec, document it in the proposal
6. **Version Control**: Commit proposals and implementations separately for better tracking

## Support and Feedback

For issues or questions:
1. Check the task summary JSON for detailed task information
2. Review the OpenSpec documentation
3. Examine the generated proposals for clarity
4. Modify the script to fit your specific needs

## License

This script is provided as-is for use with Simics DDM projects and OpenSpec framework integration.
