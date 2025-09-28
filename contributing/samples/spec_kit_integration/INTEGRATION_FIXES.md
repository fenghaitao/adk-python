# ADK Integration Fixes for /specify Command

## Problem
The LLM in `agent.py` was not following the instructions in the `.adk/commands/` folder when `/specify` command was used. Instead, it was creating specifications by itself rather than following the scripted workflow.

## Root Cause
1. **Missing `.adk` folder structure**: The directory was not initialized with the Spec-Kit template files
2. **Weak instruction emphasis**: The agent instructions didn't strongly emphasize reading command files first

## Solutions Applied

### 1. Initialize Spec-Kit Structure
```bash
specify init . --ai adk --force
```

This created:
- `.adk/commands/` - Contains all command instruction files (specify.md, plan.md, tasks.md, etc.)
- `.specify/scripts/` - Contains PowerShell and bash scripts for workflows
- `.specify/templates/` - Contains templates for specifications, plans, and tasks

### 2. Updated Agent Instructions
Modified `agent.py` to include **CRITICAL** emphasis on:
- **ALWAYS read command files first**: `read_file(".adk/commands/{command}.md")`
- **Follow exact instructions**: Don't improvise, follow the command file workflow
- **Use specified tools**: bash_command, read_file, write_file as directed

### 3. Command File Structure
The `/specify` command now follows this workflow (from `.adk/commands/specify.md`):

1. **Run script**: `.specify/scripts/powershell/create-new-feature.ps1 -Json "$ARGUMENTS"`
2. **Parse JSON output**: Extract BRANCH_NAME and SPEC_FILE 
3. **Load template**: Read `.specify/templates/spec-template.md`
4. **Write specification**: Create spec.md following template structure
5. **Report completion**: Branch name, spec file path, readiness for next phase

## Verification

### Manual Test
```powershell
.specify\scripts\powershell\create-new-feature.ps1 -Json "test user authentication system"
```
✅ **Result**: Returns correct JSON with branch and file paths

### Agent Test
Run the test script:
```bash
python test_specify_command.py
```

### Expected Agent Behavior
When receiving `/specify Create a user login system`:

1. ✅ **Reads command file**: `read_file(".adk/commands/specify.md")`
2. ✅ **Runs script**: `bash_command(".specify/scripts/powershell/create-new-feature.ps1 -Json \"Create a user login system\"")`  
3. ✅ **Parses JSON**: Extracts branch and spec file path
4. ✅ **Loads template**: `read_file(".specify/templates/spec-template.md")`
5. ✅ **Writes spec**: `write_file(spec_file_path, completed_specification)`
6. ✅ **Reports results**: Branch name and file path

## Files Modified

- `agent.py` - Updated with stronger command file instructions
- `INTEGRATION_FIXES.md` - This summary document
- `test_specify_command.py` - Test script for verification

## Directory Structure After Setup

```
spec_kit_integration/
├── .adk/
│   └── commands/
│       ├── specify.md      # /specify command instructions
│       ├── plan.md         # /plan command instructions  
│       ├── tasks.md        # /tasks command instructions
│       └── ...
├── .specify/
│   ├── scripts/powershell/
│   │   └── create-new-feature.ps1
│   └── templates/
│       ├── spec-template.md
│       ├── plan-template.md
│       └── ...
├── agent.py               # ADK agent with updated instructions
├── spec_kit_tools.py      # Tools for file/bash operations
└── test_specify_command.py # Test script
```

## Next Steps

1. **Test the integration**: Run `python test_specify_command.py`
2. **Use the agent**: Send `/specify` commands and verify it follows the workflow
3. **Monitor behavior**: Ensure it reads command files before proceeding
4. **Add other commands**: Test `/plan`, `/tasks`, etc. following similar pattern

The agent should now properly read command files from `.adk/commands/` and execute the scripted workflows instead of improvising.