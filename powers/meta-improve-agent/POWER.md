---
name: "meta-improve-agent"
displayName: "Meta Improve Agent"
description: "Analyze apply_agent sessions to identify error patterns and autonomously improve agent instructions and memory documents"
keywords: ["meta-learning", "agent-improvement", "session-analysis", "error-patterns", "autonomous-improvement", "simics", "dml", "compilation-errors"]
author: "ADK Team"
---

# Meta Improve Agent

Documentation and guidance for analyzing apply_agent execution sessions to identify patterns and autonomously improve agent instructions and memory documents.

## Overview

The Meta Improve Agent analyzes session text files from apply_agent executions to make your agent smarter over time. It works by reading session logs, agent instructions, and memory documents directly - **no ADK installation required**.

## What It Does

- **Session Analysis**: Parses apply_agent session text files to extract build attempts, errors, fixes, and outcomes
- **Pattern Recognition**: Groups errors by type and identifies recurring issues
- **Learning Extraction**: Tracks which fixes work consistently and which fail
- **Autonomous Improvement**: Generates specific updates to agent instructions and memory documents
- **Impact Measurement**: Estimates time savings and reduction in build attempts

## Available MCP Servers

**None** - This is a Knowledge Base Power that provides documentation and guidance. No MCP servers required.

## Available Steering Files

None - All documentation is contained in this POWER.md file.

## How to Use

The agent analyzes three types of files:

1. **Session text files** (`adk_openspec_apply_agent/*.session.txt`) - Contains execution logs with all attempts, errors, and fixes
2. **Agent instructions** (`adk_openspec_apply_agent/apply_agent_instruction.md`) - Current agent capabilities and instructions
3. **Memory documents** (`openspec-memories/*.md`) - Existing knowledge base

### Simple Usage

Just ask your AI assistant to analyze a session:

```
Analyze the session file adk_openspec_apply_agent/apply_implement-wdt-initial_20251214_161520.session.txt 
and tell me what improvements should be made to the agent instructions and memory documents.
```

The assistant will:
1. Read the session text file to understand what happened
2. Read the agent instruction file to see current capabilities
3. Read relevant memory documents to identify gaps
4. Provide specific recommendations for improvements

### What Files to Provide

Point the assistant to:
- **Session file**: `adk_openspec_apply_agent/*.session.txt` (the execution log)
- **Instruction file**: `adk_openspec_apply_agent/apply_agent_instruction.md` (agent's current instructions)
- **Memory directory**: `openspec-memories/` (existing knowledge base)

### Example Prompts

**Post-Implementation Review:**
```
Analyze the latest session.txt in adk_openspec_apply_agent/ and tell me what could be improved
```

**Pattern Discovery:**
```
Look at the session.txt file and identify the top 3 most common error patterns
```

**Documentation Gap Analysis:**
```
Review the session.txt and tell me what memory documents are missing or need updates
```

**Comparative Analysis:**
```
Compare these two session.txt files and tell me if the agent is improving over time
```

## What You Get (Required Output Format)

Every analysis MUST include these sections:

### 1. Session Summary (Required)
```
📊 Session Summary
- Duration: X.X minutes (HH:MM:SS → HH:MM:SS UTC)
- Build attempts: X (Y failed, Z successful)
- Test runs: X (Y passed, Z failed)
- Final status: Build ✅/❌ | Tests ✅/❌
- Total events: X
```

### 2. Top Error Patterns (Required - Extract Actual Errors)
```
🔴 Top Error Pattern: "error type" (X occurrences)

Affected identifiers/files:
- identifier1 (Xx)
- identifier2 (Xx)

Root cause: [Explain WHY this happened]

Time wasted: ~X minutes on [what activity]
```

**CRITICAL**: Count ACTUAL errors, not error lines. Use grep to extract specific identifiers.

**Example**: If you see one build failure with "unknown identifier: 'WDOGLOAD', 'WDOGPERIPHID0', 'WDOGPERIPHID1'..." that's 3+ errors, not 1 error.

### 3. What Went Well / What Caused Problems (Required)
```
✅ What Went Well
- [Specific thing agent did correctly]
- [Another success]

❌ What Caused Problems
1. [Error pattern name] (X errors)
   - Pattern: [What the agent did wrong]
   - Impact: [Time wasted, builds failed]
   - Knowledge gap: [What the agent should have known]
```

### 4. Proposed Improvements (Required - Must Be Specific)
```
🎯 Proposed Improvements

1. Add to [specific file path]:
   ```
   [EXACT TEXT TO ADD]
   ```
   Expected Impact: [Quantified improvement]

2. Create [specific file path]:
   [Content outline with examples]
   Expected Impact: [Quantified improvement]
```

**CRITICAL**: Provide EXACT text, not generic advice like "improve error handling".

### 4. Before/After Metrics (Required)
```
📉 Expected Results After Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Build attempts | X | Y | Z% reduction |
| Time to completion | X min | Y min | Z% faster |
| [Error type] errors | X | Y | Z% reduction |
```

**Example Output Format:**
```
📊 Session Summary
- Duration: 8.4 minutes
- Build attempts: 6 (1 failed, 5 successful)
- Top error: "unknown identifier" (12 occurrences)

💡 Root Cause
Agent referenced registers directly (WDOGLOAD) instead of 
using bank.register pattern (bank.WDOGLOAD)

🎯 Proposed Improvement
Add to agent instructions:
"Register Access: Use bank.REGISTER at device level,
 REGISTER at bank level, this at register level"

📉 Expected Impact
- Errors: 12 → 0 (100% reduction)
- Time: 8.4 min → 4-5 min (40-50% faster)
```

## Real-World Example Analysis

Here's an actual analysis from a WDT device implementation session:

```
Session: apply_implement-wdt-initial_20251214_235424.session.txt
Task: Implement Simics Watchdog Timer device

Summary:
- Duration: 8.4 minutes (07:54:30 → 08:02:55 UTC)
- Build attempts: 6 (counted via `grep -c "TOOL_CALL.*build_simics_project"`)
- First build failed, then 5 successful
- Test runs: 6 (all tests failed - implementation incomplete)
- Final status: Build ✅ | Tests ❌

Top Error Pattern: "unknown identifier" (12 occurrences in first build)
- WDOGLOAD, WDOGPERIPHID0-7, WDOGPCELLID0-3
- Root cause: Agent referenced registers directly instead of using bank.register pattern
- Time wasted: ~4 minutes on compilation errors

What Went Well:
✓ Followed protocol (read AGENTS.md first)
✓ Loaded memory indices correctly
✓ Iterative build-test cycle
✓ Recovered from errors successfully

What Caused Problems:
✗ Missing knowledge: DML 1.4 register access scope rules
✗ Impact: 12 compilation errors, 4 minutes wasted
✗ Pattern: Agent didn't know to use bank.REGISTER vs REGISTER vs this

Proposed Improvements:

1. Add to apply_agent_instruction.md:
   "Register Access Patterns (DML 1.4):
    - Device level: bank.REGISTER.val
    - Bank level: REGISTER.val
    - Register level: this.val
    Before implementing, identify scope and use correct pattern."
   
   Expected Impact: Prevent 100% of register access errors, save 3-4 min

2. Create openspec-memories/07_DML_Register_Access_Patterns.md:
   - Scope-based access rules
   - Common error patterns and fixes
   - Examples for each scope level
   
   Expected Impact: Reduce errors from 12 → 0, save 4 minutes

3. Add pre-build validation:
   "Before first build, search for bare register names in device-level code"
   
   Expected Impact: Catch 80-90% of errors before building

Results After Improvements:
- Build attempts: 6 → 1 (83% reduction)
- Time to first build: 4 min → 1 min (75% reduction)
- Register errors: 12 → 0 (100% reduction)
- Total time: 8.4 min → 4-5 min (40-50% reduction)
```

## Use Cases

### 1. Post-Implementation Review (Most Common)

After completing a task with apply_agent:

```
Analyze /tmp/project/adk_openspec_apply_agent/apply_implement-wdt_*.session.txt

Extract:
- Duration and build attempt count
- Top 3 error patterns with frequency
- What knowledge was missing from agent instructions
- Specific improvements to make

Provide concrete text to add to apply_agent_instruction.md
```

**When to use**: After every significant implementation session

### 2. Error Pattern Discovery

Find recurring issues across multiple sessions:

```
Analyze all .session.txt files in adk_openspec_apply_agent/ from this week.

Identify:
- Which errors appear in multiple sessions
- Which errors take the most time to resolve
- Common root causes

Focus on patterns that occur 3+ times across sessions.
```

**When to use**: Weekly or after 5-10 sessions to identify systemic issues

### 3. Comparative Analysis (Measure Improvement)

Compare sessions before/after improvements:

```
Compare these two sessions:
- BEFORE: apply_implement-wdt_20251214.session.txt (before improvements)
- AFTER: apply_implement-wdt_20251215.session.txt (after improvements)

Metrics to compare:
- Build attempts to success
- Time to completion
- Error frequency
- Types of errors

Did the improvements work? What's still problematic?
```

**When to use**: After applying improvements to validate they work

### 4. Documentation Gap Analysis

Find missing or incomplete memory documents:

```
Review session apply_implement-wdt_*.session.txt

For each error pattern:
- Check if openspec-memories/ has relevant documentation
- Identify gaps where agent should have known the answer
- Recommend new memory documents to create

List specific document titles and content outlines.
```

**When to use**: When agent repeatedly struggles with same issue type

### 5. Quick Health Check

Fast analysis for immediate feedback:

```
Quick analysis of latest session:
- Did it succeed? How many attempts?
- What was the #1 error?
- One-sentence recommendation

Keep it under 5 lines.
```

**When to use**: After each session for quick feedback loop

## How It Works

The analysis process follows these steps:

1. **Read Context Files**: Uses file reading tools to access session text files, instructions, and memory docs
2. **Parse Session Data**: Extracts events, timestamps, build attempts, errors, and fixes from text logs
3. **Identify Patterns**: Groups similar errors and tracks fix success rates
4. **Analyze Gaps**: Compares errors against existing memory to find knowledge gaps
5. **Generate Recommendations**: Proposes specific improvements with expected impact

## Step-by-Step Analysis Protocol

Follow these steps for consistent, thorough analysis:

### Step 1: Extract Basic Metrics
```bash
# Session duration
grep "👤 \[user\]" session.txt | head -1  # Start time
tail -100 session.txt | grep "🤖" | tail -1  # End time

# Count attempts - IMPORTANT: Count TOOL_CALL, not just function name
grep -c "TOOL_CALL.*build_simics_project" session.txt  # Actual build invocations
grep -c "TOOL_CALL.*run_simics_test" session.txt      # Actual test invocations

# DON'T do this (counts all mentions, not just invocations):
# grep -c "build_simics_project" session.txt  # ❌ WRONG - counts results too

# Check final status
tail -50 session.txt | grep -E "success|failed|completed"
```

### Step 2: Extract ALL Error Patterns (CRITICAL)
```bash
# Find compilation errors - look for the actual error messages
grep -i "error\|failed" session.txt | head -50

# Count specific error types - extract actual identifiers
grep "unknown identifier" session.txt | grep -o "WDOG[A-Z0-9]*" | sort | uniq -c | sort -rn
grep "unknown identifier" session.txt | grep -o "'[A-Z][A-Z0-9_]*'" | sort | uniq -c | sort -rn
```

**CRITICAL**: Don't just count error lines - extract the ACTUAL error messages and identifiers.
One line may contain multiple errors (e.g., 12 "unknown identifier" errors in one build output).

**Common mistake**: Seeing "1 line with errors" and reporting "1 error" when there are actually 12+ errors in that line.

### Step 3: Identify Root Causes
For each error pattern:
- What was the agent trying to do?
- Why did it fail? (syntax, scope, missing knowledge)
- How did the agent fix it?
- How long did it take to fix?

### Step 4: Check Knowledge Gaps
- Read agent instruction file to see what guidance exists
- Check memory documents for relevant information
- Identify what the agent SHOULD have known but didn't

### Step 5: Generate Specific Improvements
For each significant error pattern (3+ occurrences):
- Exact text to add to agent instructions
- New memory document to create (with outline)
- Pre-build validation check to add
- Quantified expected impact

### Step 6: Calculate Before/After Metrics
- Build attempts: X → Y (Z% reduction)
- Time to success: X min → Y min (Z% reduction)
- Error frequency: X → Y (Z% reduction)
- Success rate: X% → Y% (Z% improvement)

### Working with Session Files

Session text files (`.session.txt`) are human-readable logs that are easy to parse:

**Advantages:**
- Plain text format, easy to grep and search
- Contains all execution information
- Can use standard text tools (grep, sed, awk)
- Typically 100KB-300KB in size

**Example analysis approach:**
```bash
# Count build attempts - IMPORTANT: Count TOOL_CALL only
grep -c "TOOL_CALL.*build_simics_project" session.txt  # Actual invocations

# Extract error patterns
grep "error: unknown identifier" session.txt | sort | uniq -c

# Get timing information
grep "👤 \[user\]" session.txt  # Start time
tail -100 session.txt | grep "🤖" | tail -1  # End time
```

**Prompt example:**
```
Analyze the session.txt file and extract:
1. Start and end timestamps to calculate duration
2. Count of build_simics_project calls (use TOOL_CALL lines only)
3. All "error:" patterns with frequency
4. Test results (pass/fail counts)
Then provide improvement recommendations.
```

### Example Prompt

```
Analyze /tmp/project/adk_openspec_apply_agent/apply_*.session.txt:
- Extract start/end times and calculate duration
- Count build attempts using TOOL_CALL lines
- Find all error patterns with grep
- Identify the top 3 most frequent errors
- Recommend specific improvements
```

## No Installation Required

This is a **documentation-only power** that guides you in analyzing session files. Your AI assistant can:
- Read session text files directly
- Parse and analyze the execution logs
- Compare against instruction and memory files
- Generate improvement recommendations

No ADK installation or Python dependencies needed - just point your assistant to the files!

## Integration with Your Workflow

### Continuous Improvement Cycle

```
1. Implement → Run apply_agent (creates session.txt file)
2. Analyze → Ask AI to analyze the session.txt
3. Improve → Apply proposed changes to instructions/memory docs
4. Test → Run apply_agent on new task
5. Measure → Compare sessions to quantify improvement
6. Repeat → Keep iterating
```

### Regular Analysis

After each apply_agent execution:

1. Locate the session.txt file in `adk_openspec_apply_agent/`
2. Ask your AI assistant: "Analyze this session and recommend improvements"
3. Review the recommendations
4. Update instruction and memory files as suggested
5. Test with a new task to measure improvement

## Practical Analysis Workflow

Based on real usage, here's the most effective workflow:

### Step 1: Locate Session Files
```bash
# Find session files
ls -lh /path/to/project/adk_openspec_apply_agent/*.session.txt

# Check file sizes
wc -l *.session.txt   # Text files (typically 2000-5000 lines)
```

### Step 2: Quick Analysis with Text Tools
```bash
# Get session duration
grep "👤 \[user\]" session.txt  # Start time
tail -100 session.txt | grep "🤖" | tail -1  # End time

# Count attempts - CRITICAL: Use TOOL_CALL to count actual invocations
grep -c "TOOL_CALL.*build_simics_project" session.txt  # Actual build attempts
grep -c "TOOL_CALL.*run_simics_test" session.txt      # Actual test attempts

# Common mistake: Don't count all mentions
# grep -c "build_simics_project" session.txt  # ❌ WRONG - includes TOOL_RESULT lines

# Find error patterns
grep "error:" session.txt | grep -o "error: [^\\]*" | sort | uniq -c | sort -rn
```

### Step 3: Ask AI for Deep Analysis

**Prompt template:**
```
Analyze this apply_agent session and provide improvement recommendations:

Session file: /path/to/session.txt

Please extract:
1. Duration (start to end time)
2. Build attempts and success rate
3. Top 3 most frequent error patterns with examples
4. What the agent did well vs what caused problems
5. Specific improvements to agent instructions
6. New memory documents to create
7. Expected impact (time savings, error reduction)

Focus on patterns that occurred multiple times, not one-off issues.
```

### Step 4: Review and Apply Improvements

1. Read the AI's recommendations
2. Verify the error patterns are accurate
3. Update agent instruction file
4. Create or update memory documents
5. Test with a new session to measure improvement

### Step 5: Measure Impact

Compare before/after metrics:
- Build attempts to success
- Time to completion
- Error frequency
- Success rate

## Tips for Best Results

1. **Use session.txt files**: Easy to analyze with standard text tools
2. **Focus on Patterns**: Look for recurring issues (3+ occurrences), not one-off errors
3. **Review Before Applying**: Always verify recommendations match your context
4. **Iterate Regularly**: Run analysis after every 2-3 sessions to catch patterns early
5. **Measure Impact**: Track metrics before/after to validate improvements work
6. **Start Simple**: Begin with the top 1-2 most frequent errors, not everything at once

## Expected Impact

After using meta_improve_agent to improve your apply_agent:

- **Build attempts**: 8 → 2-3 (62-75% reduction)
- **Time to success**: 10.4 min → 3-4 min (65-70% reduction)
- **Error reduction**: 90-100% fewer repeated errors
- **Success rate**: 12.5% → 60-70% (55% improvement)

## Common Analysis Pitfalls

### Pitfall 0: Miscounting Build Attempts (MOST COMMON)
**Symptom**: Analysis reports 27 build attempts when there were actually only 9

**Problem**: Searching for function name counts ALL occurrences, including:
- `[TOOL_CALL] build_simics_project(...)` - the actual invocation
- `[TOOL_RESULT] build_simics_project -> {...}` - the result (appears twice in logs)
- Other mentions in text

**Solution**: Count TOOL_CALL lines only:
```bash
# ✅ CORRECT - counts actual invocations
grep -c "TOOL_CALL.*build_simics_project" session.txt

# ❌ WRONG - counts invocations + results + mentions
grep -c "build_simics_project" session.txt
```

**Example**:
- One build attempt creates 3 lines: 1 TOOL_CALL + 2 TOOL_RESULT lines
- 9 actual builds = 27 total mentions
- Always use `TOOL_CALL` to get the correct count

### Pitfall 1: Missing Compilation Errors
**Symptom**: Analysis says "no errors found" but build failed

**Solution**: Compilation errors are embedded in TOOL_RESULT lines. Search for:
- `"error":` in the session file
- `build_simics_project → {'content': [{'type': 'text', 'text': '{"success": false`
- Extract the actual error messages from the result payload

### Pitfall 2: Undercounting Errors
**Symptom**: Report says "1 error" but there were actually 12

**Solution**: One build failure line may contain multiple errors. Use:
```bash
# Extract all error identifiers, not just count lines
grep "unknown identifier" session.txt | grep -o "'[A-Z][A-Z0-9_]*'" | sort | uniq -c
```

**Example**: This line contains 13 errors, not 1:
```
error: unknown identifier: 'WDOGLOAD'
error: unknown identifier: 'WDOGPERIPHID0'
error: unknown identifier: 'WDOGPERIPHID1'
...
```

### Pitfall 3: Surface-Level Analysis
**Symptom**: Analysis just says "tests failed" without explaining why

**Solution**: 
- Read test log files if referenced
- Look for specific test failure patterns
- Identify what functionality is missing
- Check if it's a setup issue vs implementation issue

### Pitfall 4: Generic Recommendations
**Symptom**: Recommendations like "improve error handling" without specifics

**Solution**: Provide EXACT text to add:
```markdown
❌ BAD: "Add better register access documentation"

✅ GOOD: "Add to agent instructions:
'DML Register Access: Use bank.REGISTER at device level, 
REGISTER at bank level, this at register level'"
```

### Pitfall 5: Ignoring Time Impact
**Symptom**: Listing errors without calculating time wasted

**Solution**: For each error pattern, estimate:
- Time spent on failed builds
- Time spent debugging
- Time spent on rework
- Total impact in minutes

## Analysis Quality Checklist

Before submitting analysis, verify:

- [ ] **Counted build attempts correctly using TOOL_CALL**
  - [ ] Used `grep -c "TOOL_CALL.*build_simics_project"` not `grep -c "build_simics_project"`
  - [ ] Verified count makes sense (typically 2-15 builds, not 20+)
- [ ] Extracted actual error messages (not just counted error lines)
- [ ] Counted unique error occurrences correctly
- [ ] Identified root cause for each major error pattern
- [ ] Provided EXACT text for instruction updates (not generic advice)
- [ ] Calculated quantified before/after metrics
- [ ] Focused on patterns (3+ occurrences), not one-off issues
- [ ] Checked agent instructions and memory docs for gaps
- [ ] Provided specific file paths for all recommendations

## Troubleshooting

### Issue: Session file too large to read

**Symptom**: File reading errors, truncated output, or timeout

**Solution**: Use grep and text tools to extract specific sections:
```bash
# Extract just the error lines
grep "error:" session.txt > errors.txt

# Extract just build attempts
grep "TOOL_CALL.*build_simics_project" session.txt
```

### Issue: Can't calculate duration from timestamps

**Symptom**: Negative duration or incorrect time calculation

**Solution**: Look for user start time and final agent response:
```bash
grep "👤 \[user\]" session.txt  # Start
tail -100 session.txt | grep "🤖 \[" | tail -1  # End
```

### Issue: Too many errors to analyze

**Symptom**: Hundreds of errors, overwhelming output

**Solution**: Focus on unique error patterns:
```bash
# Get unique error types with counts
grep "error:" session.txt | sort | uniq -c | sort -rn | head -10
```

### Issue: Analysis is too generic

**Symptom**: Recommendations don't match your specific context

**Solution**: Provide more context in your prompt:
```
Analyze this session for a Simics DML device implementation.
Focus on DML compilation errors and register access patterns.
The agent has access to memory documents in openspec-memories/.
```

### Issue: Can't find session files

**Symptom**: No .session.txt files

**Solution**: Check the agent's output directory:
```bash
# Common locations
ls -la adk_openspec_apply_agent/*.session.txt
ls -la /tmp/*/adk_openspec_apply_agent/*.session.txt
```

## See Also

- ADK Documentation: https://github.com/google/adk-python
- OpenSpec Integration Sample: `contributing/samples/openspec_integration/`
- Real Analysis Example: See "Real-World Example Analysis" section above
