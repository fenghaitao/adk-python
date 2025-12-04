# OpenSpec Task Tracking Issue - Investigation and Fix

**Date:** December 3, 2024  
**Project:** wdt_dbg24  
**Issue:** Tasks.md file not updated with completion status (all items remain `- [ ]`)

## Problem Statement

When running the OpenSpec workflow, the agent successfully:
- ✅ Created the change proposal (`openspec/changes/test_dev-impl-001/proposal.md`)
- ✅ Created the tasks file (`openspec/changes/test_dev-impl-001/tasks.md`)
- ✅ Implemented DML device code (`simics-project/modules/test_dev/test_dev.dml`)
- ✅ Created test files (`s-wdog-basic.py`, `s-wdog-intclear-reload.py`)
- ✅ Committed the changes to git

However:
- ❌ **Never updated `tasks.md`** to mark completed items as done (`- [ ]` → `- [x]`)
- ❌ **Agent crashed** before completing the workflow
- ❌ **Archive step never executed**

## Root Cause Analysis

### Primary Cause: Context Condensation Bug

**What happened:**
1. Agent consumed 129,911 tokens (exceeding 128K context limit)
2. ADK triggered automatic context condensation
3. Context condensation successfully reduced tokens: 129,911 → 19,544
4. **BUG**: During condensation, tool call history became corrupted
5. LLM API rejected the malformed conversation with error:

```
litellm.exceptions.BadRequestError: Github_copilotException - An assistant message with 
'tool_calls' must be followed by tool messages responding to each 'tool_call_id'. The 
following tool_call_ids did not have response messages: call_YFqzxl9yywb0jfPoIzRCNdH3
```

**Impact:**
- Agent crashed mid-workflow before it could mark tasks as complete
- Archive step never executed
- Workflow left incomplete despite successful implementation

**Evidence from log:**
```
21:30:15 - LiteLLM:INFO: utils.py:3422 - LiteLLM completion() model= gpt-5-mini
🔄 Context condensation triggered. Current tokens: 129911, Max: 128000, Hard limit: 120000
Summarize conversation history using LLM github_copilot/gpt-5-mini...
✅ Context condensed: 129911 → 19544 tokens (hard limit: 120000)
⚠️  Warning: Function responses found but no valid IDs. Skipping rearrangement.
[CRASH with BadRequestError]
```

### Secondary Issue: Instruction Clarity

While the agent.py instructions include:
```python
- Mark tasks complete as you finish them (`- [ ]` → `- [x]`)
```

The instruction is:
- Only mentioned **once** in the workflow
- Not emphasized as **CRITICAL**
- Not specified to happen **FREQUENTLY** during implementation
- Not clear that it should happen **IMMEDIATELY** after each task

## Comparison with Working Projects

### wdt_dbg23 (Also Failed)
- Same issue: tasks never marked complete
- Agent stopped after creating tests and implementation
- Archive failed with: "target spec does not exist" error
- Agent response shows it completed work but asked for user decision instead of autonomous completion

### wdt_dbg21 (Unknown - needs investigation)
Would need to check if this project had the same task tracking issue.

## Implemented Fixes

### Fix 1: Enhanced Task Tracking Instructions in agent.py

**Location:** `contributing/samples/openspec_integration/agent.py` - Step 3

**Before:**
```python
3. **Implement the change**:
   - Follow tasks in `tasks.md` sequentially
   - **FOR SIMICS PROJECTS**: After creating tests, IMMEDIATELY proceed to implement DML code
     - Implement ALL register side-effects (write_register, read_register methods)
     - Implement ALL device behavior (timers, events, state management)
     - Implement ALL signal handling (connect blocks, signal_raise/lower)
     - DO NOT stop after creating tests - tests are just the FIRST step
   - Mark tasks complete as you finish them (`- [ ]` → `- [x]`)
   - Commit incremental progress
   - **Build and test** to verify implementation works
```

**After:**
```python
3. **Implement the change**:
   - Follow tasks in `tasks.md` sequentially
   - **CRITICAL**: Update `tasks.md` FREQUENTLY as you complete each task:
     - IMMEDIATELY after completing a task, edit `tasks.md` to mark it done (`- [ ]` → `- [x]`)
     - Update tasks.md MULTIPLE TIMES during implementation (not just once at the end)
     - Mark preparation tasks done after reading files
     - Mark test tasks done after creating each test file
     - Mark implementation sub-tasks done as you implement each feature
     - Mark validation tasks done after building/testing
   - **FOR SIMICS PROJECTS**: After creating tests, IMMEDIATELY proceed to implement DML code
     - Implement ALL register side-effects (write_register, read_register methods)
     - Implement ALL device behavior (timers, events, state management)
     - Implement ALL signal handling (connect blocks, signal_raise/lower)
     - DO NOT stop after creating tests - tests are just the FIRST step
   - Commit incremental progress
   - **Build and test** to verify implementation works
```

**Key Changes:**
- Moved task marking instruction to **top** of step (higher visibility)
- Added **CRITICAL** marker
- Changed "as you finish them" → "FREQUENTLY as you complete each task"
- Added **IMMEDIATELY** emphasis
- Listed **specific examples** of when to mark tasks:
  - After reading files (preparation)
  - After creating each test file
  - After implementing each feature
  - After building/testing
- Emphasized **MULTIPLE TIMES** during implementation

### Fix 2: Context Condensation Bug (Requires ADK Framework Fix)

**Location:** ADK framework code (outside this repository)

**Issue:**
The context condensation logic in ADK's `base_llm_flow.py` or related code improperly handles tool calls when summarizing conversation history. When condensing messages, it must ensure:
- Every assistant message with `tool_calls` is followed by corresponding tool responses
- Tool call IDs and their responses remain paired
- If a tool call is removed during condensation, its response must also be removed
- If a tool response is removed, its corresponding tool call must also be removed

**Workaround until fixed:**
- Reduce context usage by making prompts more concise
- Implement checkpointing to save state before context condensation
- Add try-catch around context condensation to gracefully handle failures

## Verification Steps

To verify the fix works in future runs:

1. **Check tasks.md updates during execution:**
   ```bash
   # Watch tasks.md in real-time during agent execution
   watch -n 2 cat openspec/changes/*/tasks.md
   ```

2. **Check git history for tasks.md changes:**
   ```bash
   cd <project_directory>
   git log --oneline --all -- openspec/changes/*/tasks.md
   ```

3. **Verify tasks marked complete:**
   ```bash
   # Count unchecked tasks (should decrease over time)
   grep -c "^- \[ \]" openspec/changes/*/tasks.md
   
   # Count checked tasks (should increase over time)
   grep -c "^- \[x\]" openspec/changes/*/tasks.md
   ```

4. **Check for completion:**
   ```bash
   # All tasks should be marked done before archive
   grep "^- \[ \]" openspec/changes/*/tasks.md
   # Should return empty if all done
   ```

## Expected Behavior After Fix

With the enhanced instructions, the agent should:

1. **During Preparation:**
   - Read constitution.md → Update tasks.md to mark "Read project constitution" as `[x]`
   - Read spec files → Update tasks.md to mark spec review tasks as `[x]`

2. **During Test Creation:**
   - Create s-wdog-basic.py → Update tasks.md to mark that test task as `[x]`
   - Create s-wdog-intclear-reload.py → Update tasks.md to mark that test task as `[x]`

3. **During Implementation:**
   - Implement timer event → Update tasks.md to mark that sub-task as `[x]`
   - Implement WDOGLOAD → Update tasks.md to mark that task as `[x]`
   - Implement WDOGVALUE → Update tasks.md to mark that task as `[x]`
   - ... (continue for each implementation task)

4. **During Validation:**
   - Build device → Update tasks.md to mark build task as `[x]`
   - Run tests → Update tasks.md to mark test task as `[x]`

5. **Before Archive:**
   - All tasks should be marked `[x]`
   - Archive step should succeed

## Related Files

- **Agent Instructions:** `contributing/samples/openspec_integration/agent.py`
- **Failed Project:** `/nfs/pdx/home/yongzhuo/wp5/ai_agents/tests/adk-mcp-rag/g5m_openspec/wdt_dbg24/`
- **Log Files:** 
  - `wdt_dbg24.1.log` (shows context condensation crash)
  - `adk_openspec_agent/wdt_dbg24_openspec.session.txt`
- **Tasks File:** `wdt_dbg24/openspec/changes/test_dev-impl-001/tasks.md`

## Recommendations

### Immediate Actions
1. ✅ **DONE**: Enhanced task tracking instructions in agent.py
2. ⏸️ **TODO**: File bug report with ADK team about context condensation
3. ⏸️ **TODO**: Test with a new project to verify the enhanced instructions work

### Future Improvements
1. Add automatic task tracking validation:
   - Before archive, verify all tasks are marked `[x]`
   - Warn if tasks remain unchecked
   
2. Add task tracking to common mistakes section:
   ```python
   - ❌ Never updating tasks.md → ✅ Update tasks.md after EACH task completion
   - ❌ Waiting until end to mark all tasks → ✅ Mark tasks IMMEDIATELY and INCREMENTALLY
   ```

3. Add task tracking checkpoint:
   - After major phases (tests, implementation, validation), automatically commit tasks.md
   - This preserves progress even if agent crashes

4. Implement graceful context overflow handling:
   - Save state before context condensation
   - If condensation fails, restore state and retry with different strategy
   - Never crash mid-workflow due to context issues

## Testing Plan

1. **Run new test with enhanced instructions:**
   ```bash
   ./run_openspec.sh wdt_dbg25 --device test_dev --model github_copilot/gpt-5-mini
   ```

2. **Monitor during execution:**
   - Watch for tasks.md updates in git commits
   - Check if tasks are marked incrementally
   - Verify no context condensation crashes

3. **Verify completion:**
   - Check all tasks marked `[x]` in final tasks.md
   - Verify archive step succeeded
   - Confirm implementation is complete

## Status

- **Investigation:** ✅ Complete
- **Root Cause Identified:** ✅ Yes (context condensation bug + instruction clarity)
- **Fix Implemented:** ✅ Partial (enhanced instructions in agent.py)
- **ADK Bug Report:** ⏸️ Pending
- **Verification:** ⏸️ Pending (needs test run)

---

**Last Updated:** December 3, 2024  
**Author:** AI Assistant Analysis
