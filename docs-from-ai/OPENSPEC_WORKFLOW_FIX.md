# OpenSpec Workflow Issue - Root Cause Analysis and Fix

## Problem Statement

The ADK OpenSpec agent is not executing tasks following the expected OpenSpec workflow:
- ❌ No change proposals created in `openspec/changes/`
- ❌ No `proposal.md`, `tasks.md`, or spec deltas written
- ❌ No OpenSpec commands executed (`openspec list`, `openspec validate`, `openspec archive`)
- ❌ Agent goes straight to implementation without following the structured workflow

## Root Cause Analysis

### 1. Prompt Does Not Trigger OpenSpec Workflow

**Current Prompt** (`openspec-prompts/1.md`):
```markdown
# DML Device Implementation Task

## MANDATORY STEPS
1. **Read the device spec**: `specs/001-simics-wdt-device/spec.md`
2. **Identify device**: `ls simics-project/modules/<device_name>`
3. **Implement DML device behavior** in: `simics-project/modules/<device_name>/<device_name>.dml`
...
```

**Why This Fails:**
- Uses imperative commands: "Implement", "Read", "Identify"
- Sounds like direct implementation instructions
- **Missing trigger words**: "proposal", "change", "plan", "create proposal"
- Agent interprets this as "skip to implementation" not "create OpenSpec change"

**OpenSpec Trigger Requirements** (from `openspec/AGENTS.md`):
```markdown
Triggers (examples):
- "Help me create a change proposal"
- "Help me plan a change"
- "I want to create a spec proposal"

Loose matching guidance:
- Contains one of: `proposal`, `change`, `spec`
- With one of: `create`, `plan`, `make`, `start`, `help`
```

### 2. Agent Behavior Confirmation

From session logs (`wdt_dbg20_1_openspec.session.json`):

```
👤 [user] 2025-12-02 07:21:08 UTC
   # DML Device Implementation Task
   ## MANDATORY STEPS
   1. **Read the device spec**...

🤖 [openspec_agent] 2025-12-02 07:21:08 UTC
   I'll help you implement the DML device according to the specifications.
   🔧 read_file(file_path=AGENTS.md)
   🔧 read_file(file_path=openspec/project.md)
   🔧 read_file(file_path=specs/001-simics-wdt-device/spec.md)
   ...
   🔧 write_file(file_path=simics-project/modules/test_dev/test_dev.dml, ...)
```

**Agent immediately:**
1. Acknowledged as an implementation task
2. Read supporting documentation
3. Started writing implementation code
4. **Never created OpenSpec change proposal**

### 3. Evidence from Project Structure

```bash
$ ls -la openspec/changes/
total 12
drwxr-s--- 3 yongzhuo ssdv 4096 Dec  1 23:13 .
drwxr-s--- 4 yongzhuo ssdv 4096 Dec  1 23:13 ..
drwxr-s--- 2 yongzhuo ssdv 4096 Dec  1 23:13 archive
```

**Result**: Empty `openspec/changes/` directory - no proposals were ever created.

## Solution

### Fix 1: Rewrite Prompts to Trigger OpenSpec Workflow

We now provide **two versions** of the fixed prompt:

#### Version A: `1.FIXED.md` - Explicit Workflow (All Phases Autonomous)

**Use this for**: Fully autonomous execution from proposal to archiving

**Before** (`openspec-prompts/1.md`):
```markdown
# DML Device Implementation Task

## MANDATORY STEPS
1. **Read the device spec**...
2. **Implement DML device behavior**...
```

**After** (`openspec-prompts/1.FIXED.md`):
```markdown
# Create Change Proposal for DML Device Implementation

I need to create an OpenSpec change proposal for implementing the Simics <device_name> 
device according to the specifications.

## Expected OpenSpec Workflow

Please follow the complete OpenSpec workflow autonomously from start to finish:

### Phase 1: Create Change Proposal
1. Create a change proposal directory in `openspec/changes/<change-id>/`
2. Write `proposal.md` explaining what needs to be implemented
3. Write `tasks.md` with a detailed implementation checklist
4. Run `openspec validate <change-id>` to check the proposal

### Phase 2: Implement the Change
5. Review the `tasks.md` checklist you created
6. Implement each task sequentially
7. Mark tasks as done in `tasks.md` (change `- [ ]` to `- [x]`)
8. Build and test the implementation

### Phase 3: Archive the Change
9. Run `openspec archive <change-id> --yes` to archive the change
10. Verify archiving and commit the implementation

**Important**: Complete all three phases autonomously. Do NOT stop and wait for 
approval - implement the full workflow from proposal creation through archiving.
```

#### Version B: `1.AUTONOMOUS.md` - Ultra-Explicit Autonomous Execution

**Use this for**: Maximum clarity on autonomous execution with detailed step-by-step instructions

This version:
- ✅ Explicitly states "AUTONOMOUS EXECUTION" at the top
- ✅ Lists concrete bash commands to execute (`openspec validate`, `openspec archive`, etc.)
- ✅ Provides a complete `tasks.md` template
- ✅ Includes verification steps for each phase
- ✅ Explicitly forbids stopping after proposal creation
- ✅ States "Start now and complete all phases" at the end

**Key Differences:**

| Aspect | 1.FIXED.md | 1.AUTONOMOUS.md |
|--------|-----------|-----------------|
| Explicitness | Moderate | Maximum |
| Workflow phases | Listed | Detailed with commands |
| tasks.md template | Not included | Full template provided |
| Bash commands | Mentioned | Explicitly shown |
| Autonomy emphasis | One statement | Multiple warnings |
| Best for | Standard workflows | Complex/long workflows |

### Fix 2: Update Agent Instructions for Better Workflow Adherence

The agent's system instruction in `contributing/samples/openspec_integration/agent.py` is correct, but we can strengthen the workflow adherence by:

1. **Adding explicit workflow reminders** in the prompt
2. **Using stronger trigger words** ("create proposal", "plan change", "OpenSpec workflow")
3. **Making the workflow steps explicit** in the user request

### Fix 3: Two-Phase Approach

For hardware/Simics projects, consider a **two-phase approach**:

**Phase 1: Proposal Creation** (prompt 1):
```markdown
Create an OpenSpec change proposal for implementing the <device_name> device.
Include proposal.md, tasks.md, and validate the proposal.
```

**Phase 2: Implementation** (prompt 2):
```markdown
Implement the tasks from the change proposal in openspec/changes/<change-id>/.
Follow the tasks.md checklist and mark each task complete.
```

This ensures the agent:
- Focuses on proposal creation first (explicit context)
- Switches to implementation only after proposal exists
- Can track progress through tasks.md

## Recommended Changes to `test_openspec.sh`

### Current Stage 1 Command
```bash
STAGE1_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1.md \
  --device $device_name --model $model --skip-specify --skip-simics-setup \
  --port $mcp_server_port"
```

### Recommended Fix - Option A: Split into Two Stages

**Stage 1a: Proposal Creation**
```bash
# Create file: openspec-prompts/1a-proposal.md
cat > "$proj_dir/openspec-prompts/1a-proposal.md" << 'EOF'
Create an OpenSpec change proposal for implementing the <device_name> watchdog timer device.

Please follow the OpenSpec workflow:
1. Create change directory in openspec/changes/
2. Write proposal.md
3. Write tasks.md with implementation checklist
4. Run openspec validate to check the proposal

Include all requirements from specs/<git_branch_name>/spec.md in your task breakdown.
EOF

# Run Stage 1a
STAGE1A_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1a-proposal.md \
  --device $device_name --model $model --skip-specify --skip-simics-setup \
  --port $mcp_server_port"
echo "Command: $STAGE1A_CMD" | tee -a "$proj_dir.1a.log"
$STAGE1A_CMD 2>&1 | tee -a "$proj_dir.1a.log"
```

**Stage 1b: Implementation**
```bash
# Create file: openspec-prompts/1b-implement.md
cat > "$proj_dir/openspec-prompts/1b-implement.md" << 'EOF'
Implement the tasks from the change proposal in openspec/changes/.

Use openspec list to find the active change, then:
1. Read the proposal.md to understand the goals
2. Read the tasks.md for the implementation checklist
3. Implement each task following the requirements
4. Mark tasks complete as you finish them
5. Follow DML best practices from .specify/memory/DML_Device_Development_Best_Practices.md

Critical constraints:
- ONLY edit simics-project/modules/<device_name>/<device_name>.dml and test/*.py
- Keep ALL import statements intact
- Use event-based timer implementation with SIM_time()
EOF

# Run Stage 1b
STAGE1B_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1b-implement.md \
  --device $device_name --model $model --skip-specify --skip-simics-setup \
  --port $mcp_server_port"
echo "Command: $STAGE1B_CMD" | tee -a "$proj_dir.1b.log"
$STAGE1B_CMD 2>&1 | tee -a "$proj_dir.1b.log"
```

### Recommended Fix - Option B: Enhanced Single Prompt

Replace `openspec-prompts/1.md` with clearer workflow triggers:

```markdown
# OpenSpec Change Proposal: DML Device Implementation

I want to create an OpenSpec change proposal for implementing the <device_name> device.

## What I Need

Please help me create a complete OpenSpec change proposal following the standard workflow.

## Step 1: Create Proposal Structure

Create a new change in `openspec/changes/` with:
1. `proposal.md` - explaining what we're implementing
2. `tasks.md` - detailed implementation checklist
3. Any needed spec deltas

## Step 2: Validate

Run `openspec validate` to check the proposal.

## Step 3: Implement

After the proposal is approved, implement the tasks following this checklist:

### Implementation Requirements
[Move all the detailed requirements here as checklist items in tasks.md]

## Step 4: Complete

Mark all tasks complete and prepare for archiving.

---

**Note**: Please follow the full OpenSpec workflow (proposal → validate → implement → archive).
Start by creating the change proposal structure.
```

## Verification Steps

After applying the fix, verify the agent follows the workflow:

1. **Check for change proposal creation**:
   ```bash
   ls -la openspec/changes/
   # Should show a new directory like "implement-watchdog-device"
   ```

2. **Verify proposal structure**:
   ```bash
   ls -la openspec/changes/<change-id>/
   # Should show: proposal.md, tasks.md, specs/
   ```

3. **Check session logs for OpenSpec commands**:
   ```bash
   grep -i "openspec" wdt_dbg20_1_openspec.session.txt
   # Should show: openspec list, openspec validate, openspec archive
   ```

4. **Verify task tracking**:
   ```bash
   cat openspec/changes/<change-id>/tasks.md
   # Should show tasks marked with [ ] → [x] as they complete
   ```

## Summary

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| No change proposals created | Prompt uses implementation commands, not proposal requests | Rewrite prompts with "create proposal", "OpenSpec workflow" |
| Agent skips OpenSpec workflow | Missing trigger words ("proposal", "plan", "change") | Add explicit workflow triggers and steps |
| Goes straight to coding | Prompt says "Implement" not "Create proposal for implementing" | Frame as proposal creation request, not implementation command |
| No OpenSpec commands run | Agent interprets prompt as direct task | Make workflow explicit: "Follow OpenSpec: proposal → validate → implement → archive" |

## Example Fixed Prompt

See `openspec-prompts/1.FIXED.md` for a complete example that properly triggers the OpenSpec workflow.

## Next Steps

1. ✅ Update `openspec-prompts/1.md` with proposal creation language
2. ✅ Test with a new run to verify change proposals are created
3. ✅ Check that `openspec/changes/` gets populated
4. ✅ Verify OpenSpec commands appear in session logs
5. ✅ Confirm tasks.md is created and tasks are marked complete

---

**Generated**: 2025-12-02  
**Issue**: OpenSpec agent not following workflow  
**Status**: Root cause identified, fix provided
