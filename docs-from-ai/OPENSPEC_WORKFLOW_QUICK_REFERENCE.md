# OpenSpec Prompts - Quick Reference

## TL;DR - Which Prompt to Use?

```bash
# For autonomous execution (recommended)
# Syntax: ./test_openspec.sh <proj_dir>
# Then manually run with the prompt:
./test_openspec.sh wdt_test
# This will copy prompts to wdt_test/openspec-prompts/
# Then Stage 1 uses: wdt_test/openspec-prompts/1.md

# To use 1.AUTONOMOUS.md, you need to:
# 1. Copy it as 1.md in the source:
cp openspec-prompts/1.AUTONOMOUS.md openspec-prompts/1.md

# OR modify test_openspec.sh Stage 1 to use:
STAGE1_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1.AUTONOMOUS.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"

# Alternative: Use run_openspec.sh directly (not test_openspec.sh)
# Syntax: ./run_openspec.sh <project_name> <prompt_file> [OPTIONS]
./run_openspec.sh my_project openspec-prompts/1.AUTONOMOUS.md --device wdt --model github_copilot/gpt-5-mini

# ❌ DO NOT USE (bypasses OpenSpec workflow)
# Using 1.md (original) will skip the OpenSpec workflow
```

## Problem & Solution Summary

### ❌ Problem: Agent Stops After Proposal

**What happens with bad prompts:**
```
User: [Sends 1.md or poorly written prompt]
Agent: "I've created the proposal. Let me know when ready to implement."
      [STOPS - waiting for approval]
```

**Result:**
- ❌ `openspec/changes/` has proposal but no implementation
- ❌ DML files unchanged
- ❌ No tests written
- ❌ Change not archived

### ✅ Solution: Explicit Autonomous Instructions

**What happens with good prompts (1.FIXED.md or 1.AUTONOMOUS.md):**
```
User: [Sends autonomous prompt]
Agent: "I'll complete all phases autonomously..."
      [Phase 1] Creates proposal
      [Phase 2] Implements all tasks
      [Phase 3] Archives the change
      "Done! Change archived, implementation complete."
```

**Result:**
- ✅ `openspec/changes/archive/` has completed change
- ✅ DML device implemented
- ✅ Tests written and passing
- ✅ OpenSpec commands executed (`validate`, `archive`)

## Prompt Comparison

| Feature | 1.md (Original) | 1.FIXED.md | 1.AUTONOMOUS.md |
|---------|----------------|------------|-----------------|
| **Triggers OpenSpec workflow** | ❌ No | ✅ Yes | ✅ Yes |
| **Creates proposal** | ❌ No | ✅ Yes | ✅ Yes |
| **Implements tasks** | ⚠️ Direct (no proposal) | ✅ Yes | ✅ Yes |
| **Archives change** | ❌ No | ✅ Yes | ✅ Yes |
| **Uses OpenSpec commands** | ❌ No | ✅ Yes | ✅ Yes |
| **Autonomous execution** | ❌ No | ✅ Yes | ✅ Yes (very explicit) |
| **Provides tasks.md template** | ❌ No | ❌ No | ✅ Yes |
| **Shows bash commands** | ❌ No | ⚠️ Mentions | ✅ Explicit |
| **Verification steps** | ❌ No | ❌ No | ✅ Yes |
| **Recommended for** | ❌ Never | ✅ Standard use | ✅ Complex workflows |

## Key Phrases That Make Prompts Autonomous

### ❌ Bad (Makes Agent Stop)

```markdown
Let me know when you've created the proposal and are ready to begin implementation.
```

```markdown
Please create a change proposal. After approval, we'll implement it.
```

```markdown
Step 1: Create proposal
Step 2: Wait for review
Step 3: Implement after approval
```

### ✅ Good (Makes Agent Continue)

```markdown
**Important**: Complete all three phases autonomously. Do NOT stop and wait for approval.
```

```markdown
Execute all phases from proposal creation through archiving without stopping.
```

```markdown
**AUTONOMOUS EXECUTION**: Complete all phases from start to finish.
```

```markdown
Start now and complete all phases.
```

## Testing Your Prompt

### Quick Test Checklist

After running with your prompt, check:

1. **Proposal created?**
   ```bash
   ls openspec/changes/
   # Should show: implement-<device_name>-device/ or similar
   ```

2. **Proposal has structure?**
   ```bash
   ls openspec/changes/implement-*/
   # Should show: proposal.md, tasks.md
   ```

3. **Implementation done?**
   ```bash
   git diff simics-project/modules/<device_name>/<device_name>.dml
   # Should show: actual DML code changes
   ```

4. **Change archived?**
   ```bash
   ls openspec/changes/archive/
   # Should show: YYYY-MM-DD-implement-<device_name>-device/
   ls openspec/changes/
   # Should be: empty or only archive/ directory
   ```

5. **OpenSpec commands in logs?**
   ```bash
   grep -i "openspec" *.log
   # Should show: openspec validate, openspec archive
   ```

### Expected Agent Behavior

**Phase 1: Proposal Creation (2-5 minutes)**
```
Agent: Creating change proposal...
      Writing openspec/changes/implement-wdt-device/proposal.md
      Writing openspec/changes/implement-wdt-device/tasks.md
      Running: openspec validate implement-wdt-device
      ✓ Validation passed
```

**Phase 2: Implementation (10-30 minutes)**
```
Agent: Implementing tasks from tasks.md...
      Task 1.1 ✓ Read specifications
      Task 2.1 ✓ Implement register handlers
      Task 2.2 ✓ Implement side effects
      Task 3.1 ✓ Write unit tests
      Running: gmake wdt
      ✓ Build successful
```

**Phase 3: Archive (1-2 minutes)**
```
Agent: Archiving change...
      Running: openspec archive implement-wdt-device --yes
      ✓ Change moved to openspec/changes/archive/2025-12-02-implement-wdt-device/
      ✓ All tasks complete
```

## Common Issues

### Issue: Agent stops after creating proposal

**Symptom:**
```
Agent: "I've created the proposal in openspec/changes/implement-wdt-device/. 
        Let me know when you're ready to proceed with implementation."
[Session ends]
```

**Fix:** Use `1.AUTONOMOUS.md` instead of `1.FIXED.md` or add stronger autonomy instructions:
```markdown
**CRITICAL**: Do NOT stop after creating the proposal. 
Immediately proceed to Phase 2 implementation without waiting.
```

### Issue: Agent creates proposal but doesn't use OpenSpec commands

**Symptom:**
```
# Agent creates files manually instead of using OpenSpec CLI
Agent: Writing openspec/changes/my-change/proposal.md...
       [Direct file writes, no openspec commands]
```

**Fix:** Explicitly mention OpenSpec commands in the prompt:
```markdown
3. Run validation: `openspec validate <change-id>`
...
9. Run archive: `openspec archive <change-id> --yes`
```

### Issue: Agent implements but doesn't archive

**Symptom:**
```
# Change stays in openspec/changes/ instead of archive/
ls openspec/changes/
implement-wdt-device/  # Should be in archive/
```

**Fix:** Add explicit archive verification:
```markdown
### Phase 3: Archive the Change
1. Run: `openspec archive implement-<device_name>-device --yes`
2. Verify: `ls openspec/changes/archive/` shows the archived change
3. Verify: `ls openspec/changes/` is empty (except archive directory)
```

## Migration Guide

### From Old Prompts to New

If you have existing prompts that don't work:

**Step 1:** Identify the problem
```bash
# Check if proposal was created but not implemented
ls openspec/changes/  # Has directories?
ls openspec/changes/archive/  # Empty?
# Problem: Agent stopped after proposal
```

**Step 2:** Add autonomous execution phrase
```markdown
# Add this at the top of your prompt:
**AUTONOMOUS EXECUTION**: Complete all phases from proposal through archiving.

# Or add at the end:
**Important**: Do NOT stop after proposal creation. Complete all three phases.
```

**Step 3:** Structure phases explicitly
```markdown
## Complete Workflow (Execute All Phases)

### Phase 1: Create Change Proposal
[steps...]

### Phase 2: Implement the Change  
[steps...]

### Phase 3: Archive the Change
[steps...]
```

**Step 4:** Add verification
```markdown
**When you're done**, you should have:
- ✅ Empty openspec/changes/ directory
- ✅ Populated openspec/changes/archive/YYYY-MM-DD-<change>/
- ✅ Working implementation
```

## Summary

**Recommended approach:**

**Option 1: Modify test_openspec.sh to use the better prompt**
```bash
# Edit test_openspec.sh line 80 to use 1.AUTONOMOUS.md:
STAGE1_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1.AUTONOMOUS.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"

# Then run normally:
./test_openspec.sh wdt_test
```

**Option 2: Use run_openspec.sh directly**
```bash
# This gives you direct control over the prompt file:
./run_openspec.sh my_project openspec-prompts/1.AUTONOMOUS.md --device wdt --model github_copilot/gpt-5-mini
```

**Option 3: Replace 1.md with 1.AUTONOMOUS.md**
```bash
# Make the autonomous version the default:
cp openspec-prompts/1.AUTONOMOUS.md openspec-prompts/1.md

# Then run test_openspec.sh normally:
./test_openspec.sh wdt_test
```

**Key principles:**
1. ✅ Explicitly state "autonomous execution"
2. ✅ List all three phases
3. ✅ Forbid stopping after proposal
4. ✅ Show concrete OpenSpec commands
5. ✅ Include verification steps

---

**Need help?** See `OPENSPEC_WORKFLOW_FIX.md` for detailed analysis and `README.md` for template variables.
