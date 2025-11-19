# Prompt Refinement - Issues Fixed

## Problems Identified in test.log

### 1. Agent NOT Calling MCP Tools ❌
**Issue**: Agent mentioned tools but never actually called them
- Said "Available: perform_rag_query, check_with_dmlc, build_simics_project"
- Never executed: `check_with_dmlc()`, `build_simics_project()`, `run_simics_test()`
- Only called `perform_rag_query()` repeatedly for research

**Root Cause**: Prompt was suggestive ("use perform_rag_query") not directive ("CALL perform_rag_query")

### 2. Wrong Test Filenames ❌
**Issue**: Created files with spaces in names
- Created: `'test_watchdog load.py'` (with spaces from change ID)
- Created: `'s-test_watchdog load.py'` (typo + spaces)
- Should be: `test_wdogload.py` (no spaces)

**Root Cause**: Agent used change ID "implement-watchdog load" as filename

### 3. Over-Implementation ❌
**Issue**: Added features not in specification
- Added `wdog_locked` check (not in spec)
- Added lock protection logic (not requested)
- Should be: Simple write_register() with log + default()

**Root Cause**: Prompt didn't say "ONLY implement what's specified"

### 4. No Exit Criteria ❌
**Issue**: Agent kept running after completing work
- Context grew to 148K tokens
- Kept doing RAG queries after implementation done
- Never typed 'exit' to end session

**Root Cause**: No clear "3 steps then EXIT" instruction

## Solutions Applied

### ✅ Explicit MCP Tool Calls
Changed from:
```
"Use check_with_dmlc to verify"
```

To:
```
Then IMMEDIATELY call:
- check_with_dmlc(project_path="/full/path", module="demo_watchdog")
- build_simics_project(project_path="/full/path", module="demo_watchdog")

CRITICAL: Use ABSOLUTE path, not relative paths!
```

### ✅ Exact Filename Specification
Changed from:
```
"Create test file for WDOGLOAD"
```

To:
```
FILENAME MUST BE: test_wdogload.py (NO SPACES, no 'test_watchdog load.py')
```

### ✅ Simple Implementation Only
Added:
```
THIS EXACT method (SIMPLE, no locks):
method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
    log info, 1: "WDOGLOAD write: 0x%x", value;
    default(value, enabled_bytes, aux);
}

✗ Do NOT add features not in spec (no locks, no extra logic)
```

### ✅ Clear Exit Instructions
Added:
```
MAXIMUM 3 ACTIONS: Edit DML → Create Test → Run Test → EXIT

If tests PASS, respond: "IMPLEMENTATION COMPLETE" and type 'exit'
If tests FAIL, fix and retry ONCE, then exit
```

### ✅ Limited RAG Queries
Added:
```
✗ Do NOT call perform_rag_query multiple times (1-2 max)
✗ Do NOT explore after completing 3 steps
```

## New Prompt Structure

```
STEP 1/3: EDIT DML FILE
- Find register WDOGLOAD
- Add EXACT method (provided)
- CALL check_with_dmlc() - ABSOLUTE path
- CALL build_simics_project() - ABSOLUTE path

STEP 2/3: CREATE TEST FILE
- Filename: test_wdogload.py (NO SPACES)
- Content: (exact code provided)
- DO NOT create multiple files

STEP 3/3: RUN TESTS
- CALL run_simics_test() - ABSOLUTE path
- If PASS → "IMPLEMENTATION COMPLETE" → type 'exit'
- If FAIL → fix once → exit

MAXIMUM 3 ACTIONS: Edit → Test → Run → EXIT
```

## Key Changes

| Old Prompt | New Prompt |
|------------|------------|
| "Use MCP tools..." | "CALL check_with_dmlc(project_path=...)" |
| "Create test file" | "FILENAME MUST BE: test_wdogload.py" |
| "Implement register" | "THIS EXACT method (SIMPLE, no locks)" |
| "When done, exit" | "type 'exit' after IMPLEMENTATION COMPLETE" |
| 4 steps | 3 steps with EXIT |
| Suggested RAG usage | "1-2 max, then stop" |

## Expected Behavior Now

1. Agent edits DML with exact simple method
2. Agent calls check_with_dmlc + build_simics_project
3. Agent creates test_wdogload.py (no spaces)
4. Agent calls run_simics_test
5. Agent responds "IMPLEMENTATION COMPLETE"
6. Agent types 'exit'

Total actions: ~5-6 (edit, call x2, create, call, exit)
Total tokens: <20K (vs 148K before)

## Files Cleaned Up

Removed bad test files:
- `'test_watchdog load.py'` ❌
- `'s-test_watchdog load.py'` ❌

Ready for fresh test with correct filename:
- `test_wdogload.py` ✓

## Next Test

Run with cleaned environment:
```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
export AUTO_YES=1
./test_first_task.sh > test.log 2>&1
```

Expected: Clean 3-step execution with MCP tool calls and proper exit.
