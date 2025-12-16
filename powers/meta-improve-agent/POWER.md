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

The Meta Improve Agent analyzes session JSON files from apply_agent executions to make your agent smarter over time. It works by reading session logs, agent instructions, and memory documents directly - **no ADK installation required**.

## What It Does

- **Session Analysis**: Parses apply_agent session JSON files to extract build attempts, errors, fixes, and outcomes
- **Pattern Recognition**: Groups errors by type and identifies recurring issues
- **Learning Extraction**: Tracks which fixes work consistently and which fail
- **Autonomous Improvement**: Generates specific updates to agent instructions and memory documents
- **Impact Measurement**: Estimates time savings and reduction in build attempts

## Available MCP Servers

**None** - This is a Knowledge Base Power that provides documentation and guidance. No MCP servers required.

## Available Steering Files

- **getting-started.md** - Step-by-step guide for analyzing sessions and applying improvements

## How to Use

The agent analyzes three types of files:

1. **Session JSON files** (`adk_openspec_apply_agent/*.session.json`) - Contains execution logs with all attempts, errors, and fixes
2. **Agent instructions** (`adk_openspec_apply_agent/apply_agent_instruction.md`) - Current agent capabilities and instructions
3. **Memory documents** (`openspec-memories/*.md`) - Existing knowledge base

### Simple Usage

Just ask your AI assistant to analyze a session:

```
Analyze the session file adk_openspec_apply_agent/apply_implement-wdt-initial_20251214_161520.session.json 
and tell me what improvements should be made to the agent instructions and memory documents.
```

The assistant will:
1. Read the session JSON file to understand what happened
2. Read the agent instruction file to see current capabilities
3. Read relevant memory documents to identify gaps
4. Provide specific recommendations for improvements

### What Files to Provide

Point the assistant to:
- **Session file**: `adk_openspec_apply_agent/*.session.json` (the execution log)
- **Instruction file**: `adk_openspec_apply_agent/apply_agent_instruction.md` (agent's current instructions)
- **Memory directory**: `openspec-memories/` (existing knowledge base)

### Example Prompts

**Post-Implementation Review:**
```
Analyze the latest session JSON in adk_openspec_apply_agent/ and tell me what could be improved
```

**Pattern Discovery:**
```
Look at the session file and identify the top 3 most common error patterns
```

**Documentation Gap Analysis:**
```
Review the session and tell me what memory documents are missing or need updates
```

**Comparative Analysis:**
```
Compare these two session files and tell me if the agent is improving over time
```

## What You Get

The analysis provides comprehensive, actionable insights:

### 1. Session Summary
- **Duration**: Start to end time with total minutes
- **Attempts**: Build attempts, test runs, success/failure counts
- **Final Status**: Whether build and tests succeeded
- **Event Count**: Total events in the session

### 2. Error Pattern Analysis
- **Top Errors**: Most frequent errors with occurrence counts
- **Root Cause**: Why each error happened
- **Examples**: Actual error messages from the session
- **Impact**: Time wasted on each error type

### 3. What Went Well / What Caused Problems
- **Successes**: What the agent did correctly
- **Failures**: Where the agent struggled
- **Knowledge Gaps**: What information was missing
- **Recovery Patterns**: How the agent fixed issues

### 4. Proposed Improvements (Specific & Actionable)
- **Instruction Updates**: Exact text to add to agent instructions
- **Memory Documents**: New docs to create with content outlines
- **Validation Checks**: Pre-build checks to add
- **Expected Impact**: Quantified improvements (time savings, error reduction %)

### 5. Before/After Metrics
- Build attempts: X → Y (Z% reduction)
- Time to success: X min → Y min (Z% reduction)
- Error frequency: X → Y (Z% reduction)
- Success rate: X% → Y% (Z% improvement)

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
Session: apply_implement-wdt-initial_20251214_235424.session.json (318KB)
Task: Implement Simics Watchdog Timer device

Summary:
- Duration: 8.4 minutes (07:54:30 → 08:02:55 UTC)
- Build attempts: 6 (first failed, then 5 successful)
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
- AFTER: apply_implement-uart_20251215.session.txt (after improvements)

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

1. **Read Context Files**: Uses file reading tools to access session JSON, instructions, and memory docs
2. **Parse Session Data**: Extracts events, timestamps, build attempts, errors, and fixes from JSON
3. **Identify Patterns**: Groups similar errors and tracks fix success rates
4. **Analyze Gaps**: Compares errors against existing memory to find knowledge gaps
5. **Generate Recommendations**: Proposes specific improvements with expected impact

### Handling Large Session Files

Session JSON files can be very large (100KB-300KB+). You have two options:

#### Option 1: Analyze the .session.txt File (Recommended)

Most sessions also generate a human-readable `.session.txt` file that's easier to parse:

**Advantages:**
- Plain text format, easier to grep and search
- Contains the same information as JSON
- Can use standard text tools (grep, sed, awk)
- No JSON parsing issues with large files

**Example analysis approach:**
```bash
# Count build attempts
grep -c "build_simics_project" session.txt

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
2. Count of build_simics_project calls
3. All "error:" patterns with frequency
4. Test results (pass/fail counts)
Then provide improvement recommendations.
```

#### Option 2: Chunked JSON Reading

If you need to analyze the JSON directly:

1. **Use chunked reading**: Read the file in chunks using `read_file_range` or similar tools
   - Start with offset=0, length=65536 (64KB chunks)
   - Continue reading subsequent chunks if needed
   - Example: "Read the session JSON file in 64KB chunks starting from offset 0"

2. **Focus on key sections**: You don't need to read the entire file
   - Start with the first chunk to understand structure
   - Look for error patterns in events
   - Sample middle and end sections if needed

3. **Incremental analysis**: Build understanding progressively
   - Parse events as you read each chunk
   - Track error counts and patterns
   - Summarize findings after each chunk

### Example Prompts

**For .txt files (easier):**
```
Analyze /tmp/project/adk_openspec_apply_agent/apply_*.session.txt:
- Extract start/end times and calculate duration
- Count build attempts and test runs
- Find all error patterns with grep
- Identify the top 3 most frequent errors
- Recommend specific improvements
```

**For .json files (when needed):**
```
Read the session file adk_openspec_apply_agent/*.session.json in 64KB chunks.
For each chunk, extract error events and build attempts. 
After reading all chunks, summarize the top 3 error patterns and recommend improvements.
```

## No Installation Required

This is a **documentation-only power** that guides you in analyzing session files. Your AI assistant can:
- Read JSON session files directly (in chunks if large)
- Parse and analyze the data structure incrementally
- Compare against instruction and memory files
- Generate improvement recommendations

No ADK installation or Python dependencies needed - just point your assistant to the files!

## Integration with Your Workflow

### Continuous Improvement Cycle

```
1. Implement → Run apply_agent (creates session JSON file)
2. Analyze → Ask AI to analyze the session JSON
3. Improve → Apply proposed changes to instructions/memory docs
4. Test → Run apply_agent on new task
5. Measure → Compare sessions to quantify improvement
6. Repeat → Keep iterating
```

### Regular Analysis

After each apply_agent execution:

1. Locate the session JSON file in `adk_openspec_apply_agent/`
2. Ask your AI assistant: "Analyze this session and recommend improvements"
3. Review the recommendations
4. Update instruction and memory files as suggested
5. Test with a new task to measure improvement

## Practical Analysis Workflow

Based on real usage, here's the most effective workflow:

### Step 1: Locate Session Files
```bash
# Find session files
ls -lh /path/to/project/adk_openspec_apply_agent/*.session.*

# Check file sizes
wc -c *.session.json  # JSON files (100-300KB typical)
wc -l *.session.txt   # Text files (easier to analyze)
```

### Step 2: Quick Analysis with Text Tools
```bash
# Get session duration
grep "👤 \[user\]" session.txt  # Start time
tail -100 session.txt | grep "🤖" | tail -1  # End time

# Count attempts
grep -c "build_simics_project" session.txt
grep -c "run_simics_test" session.txt

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

1. **Use .txt files when possible**: Easier to analyze than JSON, same information
2. **Focus on Patterns**: Look for recurring issues (3+ occurrences), not one-off errors
3. **Review Before Applying**: Always verify recommendations match your context
4. **Iterate Regularly**: Run analysis after every 2-3 sessions to catch patterns early
5. **Measure Impact**: Track metrics before/after to validate improvements work
6. **Start Simple**: Begin with the top 1-2 most frequent errors, not everything at once

## Expected Impact

After using meta_improve_agent to improve your apply_agent:

- **Build attempts**: 8 → 2-3 (62-75% reduction)
- **Time to success**: 10.4 min → 3-4 min (65-70% reduction)
- **Success rate**: 12.5% → 60-70% (55% improvement)

## Troubleshooting

### Issue: JSON file too large to parse

**Symptom**: JSON parsing errors, truncated output, or timeout

**Solution**: Use the `.session.txt` file instead:
```
Analyze the .session.txt file instead of .json - it contains 
the same information in a more readable format
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

**Symptom**: No .session.json or .session.txt files

**Solution**: Check the agent's output directory:
```bash
# Common locations
ls -la adk_openspec_apply_agent/*.session.*
ls -la /tmp/*/adk_openspec_apply_agent/*.session.*
```

## See Also

- Getting Started Guide: See `steering/getting-started.md`
- ADK Documentation: https://github.com/google/adk-python
- OpenSpec Integration Sample: `contributing/samples/openspec_integration/`
- Real Analysis Example: See "Real-World Example Analysis" section above
