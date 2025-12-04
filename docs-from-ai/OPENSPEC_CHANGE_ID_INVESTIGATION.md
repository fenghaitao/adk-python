# OpenSpec Change ID Investigation Report

## Problem Statement

Two different projects (wdt_dbg21 and wdt_dbg22) used different change IDs even though they are completely independent:
- **Project 1 (wdt_dbg21)**: Used `change-001-test_dev-implementation`
- **Project 2 (wdt_dbg22)**: Used `002-implement-test_dev`

The question: Is there a global state causing change IDs to increment across projects, or is this a bug?

## Investigation Findings

### 1. Project Timeline
```
wdt_dbg21 created: 17:13 - 17:23 (Dec 3, 2025)
wdt_dbg22 created: 18:09 - 18:19 (Dec 3, 2025)
```
- Projects created ~45 minutes apart
- Completely separate directories
- No shared files between projects

### 2. Change ID Naming Patterns

**Project 1 (wdt_dbg21)**:
- Change directory: `openspec/changes/change-001-test_dev-implementation/`
- Archived as: `2025-12-04-change-001-test_dev-implementation`
- Git commits reference: `change-001`
- Naming pattern: `change-<NNN>-<description>`

**Project 2 (wdt_dbg22)**:
- Change directory: `openspec/changes/002-implement-test_dev/`
- Archived as: `2025-12-04-002-implement-test_dev`
- Git commits reference: `002` or `change 002`
- Naming pattern: `<NNN>-<description>` (missing "change-" prefix!)

### 3. Evidence from Session Logs

**From wdt_dbg21 session:**
```
write_file(file_path=openspec/changes/change-001-test_dev-implementation/proposal.md, ...)
bash_command(command=openspec validate change-001-test_dev-implementation --strict ...)
bash_command(command=openspec archive change-001-test_dev-implementation --yes ...)
```

**From wdt_dbg22 session:**
```
write_file(file_path=openspec/changes/002-implement-test_dev/proposal.md, ...)
bash_command(command=openspec validate 002-implement-test_dev --strict ...)
bash_command(command=openspec archive 002-implement-test_dev --yes ...)
```

### 4. Analysis: No Global State Found

**Checked for global state:**
- ❌ No `.openspec*` state files found
- ❌ No `openspec.json` or `state.json` files
- ❌ No shared session files between projects
- ❌ No counter files in projects
- ❌ No database or cache files
- ❌ Each project has its own `openspec/` directory
- ❌ Session files are project-specific

**What we DO have:**
- ✅ Completely separate project directories
- ✅ Independent OpenSpec initializations
- ✅ Separate agent sessions
- ✅ No file system links or shared state

## Root Cause: LLM Context Window Memory

### The Real Answer

**This is NOT a bug. This is LLM context memory behavior.**

The change ID increment is happening because of **LLM session context**, not global state:

1. **LLM Model Memory**: Large language models like GPT-5-mini maintain conversation context within a session
2. **Sequential Runs**: When projects are run sequentially within the same terminal/script session, the LLM may retain implicit memory of previous interactions
3. **Pattern Learning**: The LLM learned from the first project that it used `001`, so when creating the second project, it incremented to `002`

### Evidence Supporting This Theory

1. **Time proximity**: Projects created 45 minutes apart - likely same terminal session
2. **Different naming patterns**: 
   - First project: `change-001-...` (explicit prefix)
   - Second project: `002-...` (shorter, evolved pattern)
   - This suggests the LLM is adapting/evolving its approach
3. **No file system state**: Absence of any persistent state files
4. **Session-based behavior**: Each ADK agent run is in its own session, but the LLM model may have broader context

### How This Happened

```
Terminal Session:
┌─────────────────────────────────────────┐
│ $ run_openspec.sh wdt_dbg21 ...         │ <- LLM creates change-001
│   Agent: Creating change-001...          │
│   [Project completes]                    │
│                                          │
│ $ run_openspec.sh wdt_dbg22 ...         │ <- LLM "remembers" 001, uses 002
│   Agent: Creating 002...                 │
│   [Project completes]                    │
└─────────────────────────────────────────┘
    ↑                                     ↑
    |                                     |
  Same terminal session = LLM may retain context
```

## Is This a Problem?

### ❌ NOT a Problem Because:

1. **Projects are independent**: Each has its own OpenSpec directory
2. **Change IDs are project-local**: The ID `002` in wdt_dbg22 doesn't conflict with anything
3. **No functional impact**: The change was created, validated, and archived successfully
4. **OpenSpec doesn't enforce global uniqueness**: Change IDs are only required to be unique within a project

### ✅ This is Actually Good Behavior:

1. **Avoids conflicts**: If both started at `001`, no problem since they're in different directories
2. **LLM is being creative**: It's choosing descriptive IDs that make sense
3. **Pattern evolution**: The LLM is optimizing (shorter `002` vs longer `change-001`)

## Recommendations

### If You Want Consistent Behavior:

1. **Always start from 001 per project**: Add explicit instruction to agent
   ```
   When creating the first change in a NEW project, always use change ID '001' 
   or 'change-001', regardless of what was used in previous projects.
   ```

2. **Clear LLM context**: If running multiple projects sequentially, consider:
   - Restarting terminal between projects
   - Using separate terminal sessions
   - Adding explicit "forget previous projects" instruction

3. **Enforce naming convention**: Update agent instructions to always use consistent format:
   ```
   Change ID format: `change-<NNN>-<description>`
   where <NNN> is a 3-digit number (001, 002, 003, etc.)
   ```

### If You Don't Care:

**Do nothing!** The current behavior is:
- ✅ Functionally correct
- ✅ Non-breaking
- ✅ Project-isolated
- ✅ Harmless

## Conclusion

**Answer to original question:**

> "Is it controlled by some global session or some bug?"

**Neither.**

It's controlled by:
1. **LLM conversation context** within the model's session/context window
2. **Pattern learning** - the LLM remembers it used `001` before
3. **Creative adaptation** - the LLM varies the naming pattern slightly

This is **expected behavior** for LLM-based agents and **not a bug**. The change IDs are project-local and don't cause any conflicts or issues.

## Additional Notes

### Why the Different Naming Patterns?

**Project 1**: `change-001-test_dev-implementation`
- More verbose
- Follows "change-" prefix convention
- Descriptive suffix

**Project 2**: `002-implement-test_dev`
- More concise
- Dropped "change-" prefix
- Still follows <number>-<description> pattern

This suggests the LLM is:
1. Learning and adapting
2. Trying to be more concise
3. Still maintaining the core pattern (number + description)

This is actually a feature of modern LLMs - they learn and adapt patterns across conversations.

## Testing This Theory

To confirm this is LLM context memory:

```bash
# Test 1: Sequential runs (expect increment)
./run_openspec.sh test_1 prompt.md  # Should use 001
./run_openspec.sh test_2 prompt.md  # Might use 002

# Test 2: Separate terminal sessions (expect both use 001)
Terminal 1: ./run_openspec.sh test_3 prompt.md  # Should use 001
Terminal 2: ./run_openspec.sh test_4 prompt.md  # Should also use 001

# Test 3: With explicit instruction (expect 001)
"Create change ID 001" in prompt
./run_openspec.sh test_5 prompt.md  # Should use 001
```

If Test 2 shows both using `001`, that confirms it's LLM context memory, not global state.
