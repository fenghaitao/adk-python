# Autonomous Workflow Implementation - Short Prompt Support

## Overview

This document describes the changes made to enable **short prompt, full workflow** behavior in the OpenSpec agent. The agent can now respond to simple, high-level requests like:

> "Implement the simics device and python tests as the spec describes"

And autonomously execute the complete OpenSpec workflow without needing a long, detailed prompt.

## Changes Made

### 1. Updated `OpenSpec/openspec/AGENTS.md` (Template File)

**Location**: `/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/OpenSpec/openspec/AGENTS.md`

**Purpose**: This is the template file that gets copied into each OpenSpec project during initialization.

**Changes**:
- ✅ Added new section **"Default Behavior for Short/Vague Task Requests"** at the top
- ✅ Updated **Stage 2** to emphasize autonomous execution and remove "wait for approval" language
- ✅ Updated **Stage 3** to include error handling for archive failures
- ✅ Modified **TL;DR** to mention autonomous workflows

**Key Addition**:
```markdown
## Default Behavior for Short/Vague Task Requests

**CRITICAL**: If the user gives a high-level or vague implementation request without 
explicitly mentioning the OpenSpec workflow, you MUST autonomously follow the complete 
OpenSpec workflow:

1. Assess the current state
2. Create a change proposal
3. Implement the change
4. Archive the change

**DO NOT stop and wait for approval** unless the user explicitly requests a review step.
```

### 2. Updated `contributing/samples/openspec_integration/agent.py`

**Location**: `/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples/openspec_integration/agent.py`

**Purpose**: This is the Python agent implementation that ADK uses.

**Changes**:
- ✅ Added **"CRITICAL: Default Behavior for Short/Vague Task Requests"** section to the system instruction
- ✅ Emphasized **AUTONOMOUS EXECUTION REQUIRED**
- ✅ Explicitly listed examples of short prompts that should trigger the full workflow
- ✅ Added error handling guidance for archive failures

**Key Addition**:
```python
instruction = """
...
## CRITICAL: Default Behavior for Short/Vague Task Requests

**AUTONOMOUS EXECUTION REQUIRED**: If the user gives a high-level or vague 
implementation request without explicitly mentioning the OpenSpec workflow, 
you MUST autonomously follow the complete OpenSpec workflow from proposal 
creation through archiving...
"""
```

## How It Works

### Before (Old Behavior)

**Prompt**:
```
Implement the device as per spec
```

**Agent Response**:
```
I'll implement the device directly...
[Skips OpenSpec workflow]
[No proposal.md, no tasks.md, no archiving]
```

### After (New Behavior)

**Prompt**:
```
Implement the device as per spec
```

**Agent Response**:
```
I'll follow the OpenSpec workflow:
1. Assessing current state...
2. Creating change proposal in openspec/changes/implement-device/
   - Writing proposal.md
   - Writing tasks.md
3. Running openspec validate...
4. Implementing tasks...
5. Running openspec archive --yes...
✓ Complete!
```

## Testing the Changes

### Test Case 1: Short High-Level Prompt

**Command**:
```bash
./test_openspec.sh wdt_test
```

**With prompt**:
```markdown
Implement the simics device and python tests as the spec describes based on 
the current project skeleton.
```

**Expected Behavior**:
1. ✅ Agent reads AGENTS.md and sees default behavior section
2. ✅ Agent creates `openspec/changes/implement-<device>-device/`
3. ✅ Agent writes `proposal.md`, `tasks.md`
4. ✅ Agent runs `openspec validate`
5. ✅ Agent implements all tasks
6. ✅ Agent runs `openspec archive --yes`
7. ✅ Change appears in `openspec/changes/archive/`

### Test Case 2: Verify Archive Error Handling

**Scenario**: Archive fails because target spec doesn't exist

**Expected Behavior**:
1. ✅ Agent detects archive error
2. ✅ Agent creates missing target spec in `openspec/specs/`
3. ✅ Agent retries `openspec archive --yes`
4. ✅ Archive succeeds
5. ✅ Agent does NOT stop and wait for user intervention

### Test Case 3: Explicit Workflow Request (Should Still Work)

**Prompt**:
```markdown
Please create an OpenSpec change proposal for implementing...
[Full detailed prompt]
```

**Expected Behavior**:
1. ✅ Agent still follows the workflow (unchanged from before)
2. ✅ Agent completes all phases autonomously

## Verification Checklist

After running the agent with a short prompt, verify:

- [ ] **Proposal Created**: `openspec/changes/<change-id>/` exists
- [ ] **Proposal Structure**: Contains `proposal.md`, `tasks.md`
- [ ] **Implementation Done**: DML files modified, tests created
- [ ] **Archive Complete**: Change in `openspec/changes/archive/`, NOT in `openspec/changes/`
- [ ] **OpenSpec Commands Used**: Log shows `openspec validate`, `openspec archive`
- [ ] **No Manual Stops**: Agent didn't wait for approval between phases

## Key Principles

### 1. Default to Full Workflow
The agent now defaults to the complete OpenSpec workflow for ANY implementation request, even if the user doesn't mention "proposal" or "OpenSpec".

### 2. Autonomous Execution
The agent completes all three stages (proposal → implement → archive) without stopping for approval unless explicitly requested.

### 3. Error Recovery
If `openspec archive` fails, the agent fixes the issue (e.g., creates missing specs) and retries instead of stopping.

### 4. Short Prompts Work
Users can now give simple, natural language requests like:
- "Implement feature X"
- "Add tests for Y"
- "Create device Z"

And get the full structured workflow automatically.

## Files Modified

1. **OpenSpec/openspec/AGENTS.md** - Template for project AGENTS.md files
2. **contributing/samples/openspec_integration/agent.py** - Agent system instruction

## Migration Notes

### For Existing Projects

**Option 1: Update AGENTS.md manually**
```bash
# Copy the new template section to existing project
cp OpenSpec/openspec/AGENTS.md /path/to/project/openspec/AGENTS.md
```

**Option 2: Re-run openspec init/update**
```bash
cd /path/to/project
openspec update .
```

### For New Projects

New projects initialized after this change will automatically get the updated AGENTS.md template with autonomous workflow behavior.

## Troubleshooting

### Issue: Agent still stops after creating proposal

**Check**:
1. Is the AGENTS.md file updated in the project directory?
   ```bash
   grep "Default Behavior for Short/Vague" openspec/AGENTS.md
   ```
2. Is the agent.py file using the updated system instruction?
   ```bash
   grep "AUTONOMOUS EXECUTION REQUIRED" contributing/samples/openspec_integration/agent.py
   ```

**Fix**: Update the files as described in this document.

### Issue: Archive fails and agent stops

**Check**: Does the error message mention missing specs?

**Expected Behavior**: Agent should automatically create missing specs and retry archive.

**If agent stops**: The error handling logic may need strengthening in agent.py.

## Benefits

### 1. **Simpler Prompts**
Users don't need to write long, detailed prompts explaining the OpenSpec workflow.

### 2. **Consistent Workflow**
Every implementation follows the same structured process (proposal → implement → archive).

### 3. **Better Traceability**
All changes have proposals, tasks, and archived history, even for "simple" requests.

### 4. **Reduced Friction**
No manual intervention needed between workflow phases.

### 5. **Beginner Friendly**
New users can benefit from the OpenSpec workflow without understanding all the details upfront.

## Examples

### Example 1: Hardware Device Implementation

**Before (long prompt needed)**:
```markdown
# Create Change Proposal for DML Device Implementation

I need to create an OpenSpec change proposal for implementing the Simics <device_name> device.

## Expected OpenSpec Workflow
Please follow the complete OpenSpec workflow autonomously from start to finish:
### Phase 1: Create Change Proposal
1. Create a change proposal directory...
[... 50+ lines ...]
```

**After (short prompt works)**:
```markdown
Implement the simics device and python tests as the spec describes.
```

### Example 2: Feature Addition

**Before**:
```markdown
[Long detailed explanation of OpenSpec workflow and phases]
```

**After**:
```markdown
Add user authentication feature with JWT tokens.
```

### Example 3: Test Creation

**Before**:
```markdown
[Detailed workflow instructions]
```

**After**:
```markdown
Create comprehensive unit tests for the API endpoints.
```

## Next Steps

1. ✅ **Test with real projects**: Run `test_openspec.sh` with short prompts
2. ✅ **Verify archive completion**: Ensure changes actually end up in `archive/`
3. ✅ **Monitor error handling**: Watch for archive failures and verify auto-recovery
4. ✅ **Gather feedback**: See if agents consistently follow the workflow
5. ✅ **Iterate**: Strengthen instructions if agents still stop prematurely

## Summary

These changes make the OpenSpec agent **robust to both detailed and simple task descriptions**. The agent now:

- ✅ Understands short, high-level prompts
- ✅ Automatically follows the full OpenSpec workflow
- ✅ Completes all phases autonomously (proposal → implement → archive)
- ✅ Handles errors gracefully and retries
- ✅ Doesn't require explicit workflow instructions in every prompt

**Users can now simply say "implement feature X" and trust the agent to follow the proper spec-driven development process.**

---

**Generated**: 2025-12-02  
**Author**: AI Assistant  
**Status**: Implemented and ready for testing
