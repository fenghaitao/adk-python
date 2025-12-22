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

## ⚠️ CRITICAL: Documentation Verification (NEW)

**Don't assume existing documents cover the error!** The most common analysis mistake is assuming a document covers a topic based on its title, without verifying actual content.

**Example of this mistake:**
- Error: `reference to unknown object 'WDOGCONTROL.field'`
- ❌ WRONG: "Agent violated protocol by not reading 07_DML_Register_Access_Scope.md"
- ✅ CORRECT: "Documentation gap - 07_DML_Register_Access_Scope.md covers register values (`.val`) but not field access (`.FIELDNAME`)"

**Always verify:**
1. Read the referenced document
2. Search for keywords related to the error
3. Confirm the document explains what the agent tried to do
4. Classify correctly: Protocol Violation vs Documentation Gap vs Missing Document

See **Step 4.5: Verify Documentation Coverage** in the analysis protocol below for detailed guidance.

## What It Does

- **Session Analysis**: Parses apply_agent session text files to extract build attempts, errors, fixes, and outcomes
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

## Performance Scoring System (100 Points)

Every analysis MUST include a comprehensive performance score that evaluates the apply_agent's execution across 8 dimensions. This scoring system provides objective, quantifiable metrics to track improvement over time.

### Scoring Overview

**Total: 100 Points**
- **Result Quality (50 points)**: Quality of the final output
  - DML Code Quality (15 points)
  - Test Quality (15 points)
  - Documentation Quality (5 points)
  - Functionality Score (15 points)

- **Process Quality (50 points)**: How efficiently the agent worked
  - Efficiency Score (15 points)
  - Methodology Score (15 points)
  - Error Handling Score (10 points)
  - Code Evolution Score (10 points)

### Result Quality Scoring (50 points)

#### 1. DML Code Quality (0-15 points)

Evaluates the quality of the DML device implementation code.

**Components:**
- **Correctness (0-5)**: Does the DML code compile and work?
- **Idioms (0-5)**: Does it follow DML best practices and patterns?
- **Maintainability (0-5)**: Is it clean, readable, well-structured?

**Scoring Guide:**
- 13-15: Excellent - correct, idiomatic, maintainable
- 10-12: Good - correct, mostly idiomatic, readable
- 7-9: Adequate - works but has style/pattern issues
- 4-6: Poor - works but violates best practices
- 0-3: Very poor - doesn't work or major violations

**Example:**
```
DML Code Quality: 8/15
- Correctness: 4/5 (works but had 12 scope errors initially)
- Idioms: 2/5 (used 'bank' keyword incorrectly)
- Maintainability: 2/5 (code structure improved but still has anti-patterns)

Justification: "Code eventually works but violated register access scope 
patterns. Used 'bank' keyword as variable (anti-pattern). Didn't consult 
07_DML_Register_Access_Scope.md before implementing, leading to 12 scope errors."
```

#### 2. Test Quality (0-15 points)

Evaluates the quality of Python test implementations.

**Components:**
- **Coverage (0-8)**: Do tests cover key functionality?
- **Clarity (0-7)**: Are tests clear and maintainable?

**Scoring Guide:**
- 13-15: Excellent - comprehensive coverage, very clear
- 10-12: Good - covers main cases, clear
- 7-9: Adequate - basic coverage, readable
- 4-6: Poor - minimal coverage or unclear
- 0-3: Very poor - tests don't work or missing

**Example:**
```
Test Quality: 10/15
- Coverage: 6/8 (covers main functionality, missing edge cases)
- Clarity: 4/7 (tests are readable but could be better organized)

Justification: "Tests cover core functionality and use correct register 
access patterns. However, missing edge case coverage and tests could be 
better organized with clearer naming."
```

#### 3. Documentation Quality (0-5 points)

Evaluates docstrings and comments in the implementation.

**Components:**
- **Completeness (0-3)**: Are all components documented?
  - DML: Device, banks, registers, methods have docstrings
  - Tests: Test files and functions have docstrings
  - Complex logic has explanatory comments (WHY, not WHAT)
- **Clarity (0-2)**: Is documentation clear and helpful?

**Scoring Guide:**
- 5: Excellent - complete docstrings, clear comments, helpful
- 4: Good - most components documented, mostly clear
- 3: Adequate - basic docstrings, minimal comments
- 2: Poor - incomplete docstrings or unclear
- 0-1: Very poor - missing or unhelpful documentation

**Note:** Focus on docstrings and explanatory comments for complex logic. Avoid penalizing for lack of obvious comments (e.g., "increment counter").

#### 4. Functionality Score (0-15 points)

Evaluates whether the implementation meets the specification.

**Components:**
- **Spec Compliance (0-8)**: Implements all required features?
- **Correctness (0-7)**: Works as specified?

**How to Score:**
1. Find the specification in `changes/[change-id]/specs/<capability>/spec.md`
2. Check `changes/[change-id]/tasks.md` for task completion
3. Verify tests pass and device responds correctly

**Scoring Guide:**
- 13-15: Excellent - fully implements spec, works perfectly, all tests pass
- 10-12: Good - implements most features, works well, most tests pass
- 7-9: Adequate - implements core features, mostly works, some tests pass
- 4-6: Poor - missing features or doesn't work well, many test failures
- 0-3: Very poor - incomplete or broken, tests fail

**Example:**
```
Functionality: 11/15
- Spec compliance: 6/8 (timer countdown implemented, all registers present)
- Correctness: 5/7 (basic operations work, but timer behavior has issues)

Justification: "Per spec.md, timer countdown behavior is specified and 
implemented. All required registers present. Per tasks.md, 7 of 8 tasks 
completed. However, timer countdown uses cycle-accurate updates instead 
of lazy evaluation as specified. Tests for timer expiration fail."
```

### Process Quality Scoring (50 points)

#### 5. Efficiency Score (0-15 points)

Evaluates how efficiently the agent completed the task.

**Components:**
- **Build Attempts (0-5)**: Fewer is better
  - 1-2 attempts: 5 points
  - 3-4 attempts: 4 points
  - 5-6 attempts: 3 points
  - 7-8 attempts: 2 points
  - 9+ attempts: 0-1 points

- **Time (0-5)**: Faster is better
  - <30 min: 5 points
  - 30-60 min: 4 points
  - 60-90 min: 3 points
  - 90-120 min: 2 points
  - >120 min: 0-1 points

- **Iterations (0-5)**: Fewer fix cycles is better
  - 1-5 fixes: 5 points
  - 6-10 fixes: 4 points
  - 11-15 fixes: 3 points
  - 16-20 fixes: 2 points
  - 20+ fixes: 0-1 points

**Example:**
```
Efficiency: 5/15
- Build attempts: 2/5 (8 attempts is poor)
- Time: 2/5 (116.5 minutes is poor)
- Iterations: 1/5 (47 errors across iterations is very poor)

Justification: "8 build attempts and 116.5 minutes indicates significant 
inefficiency. 47 total errors suggest agent didn't check best practices 
before implementing. Most errors were preventable with proper protocol adherence."
```

#### 6. Methodology Score (0-15 points)

Evaluates whether the agent followed proper workflows and protocols.

**Components:**
- **Follows Workflow (0-5)**: Does agent follow its instruction steps?
- **Uses Best Practices (0-5)**: Consults and applies best practice docs?
- **Knowledge Protocol (0-5)**: Checks memories before implementing?

**Scoring Guide:**
- 13-15: Excellent - follows all protocols consistently
- 10-12: Good - follows most protocols, occasional skips
- 7-9: Adequate - follows some protocols, misses others
- 4-6: Poor - frequently skips protocols
- 0-3: Very poor - ignores protocols

**Example:**
```
Methodology: 6/15
- Follows workflow: 2/5 (skipped best practice consultation)
- Uses best practices: 2/5 (didn't consult docs before implementing)
- Knowledge protocol: 2/5 (didn't check memories for register patterns)

Justification: "Agent didn't follow knowledge protocol - implemented 
register access without consulting 07_DML_Register_Access_Scope.md. 
This caused 12 preventable errors. Workflow adherence was poor."
```

#### 7. Error Handling Score (0-10 points)

Evaluates how well the agent recovers from errors and learns.

**Components:**
- **Recovery (0-5)**: How well does agent recover from errors?
- **Learning (0-5)**: Does agent avoid repeating same errors?

**Scoring Guide:**
- 9-10: Excellent - recovers quickly, learns from errors
- 7-8: Good - recovers well, mostly avoids repeats
- 5-6: Adequate - eventually recovers, some repeats
- 3-4: Poor - struggles to recover, repeats errors
- 0-2: Very poor - can't recover or repeats constantly

#### 8. Code Evolution Score (0-10 points)

Evaluates how code quality changes across iterations.

**Components:**
- **Improvement Trajectory (0-5)**: Does code get better over iterations?
- **Refinement (0-5)**: Does agent refine vs. rewrite randomly?

**What This Measures:**
Does the agent make thoughtful, incremental improvements, or does it thrash around making random changes?

**How to Score:**
1. Track code changes across builds (build 1 → 2 → 3, etc.)
2. Check if code quality increases over time
3. Verify agent makes targeted fixes vs. random rewrites

**Scoring Guide:**
- 9-10: Excellent - clear improvement, thoughtful refinement, learns from errors
- 7-8: Good - generally improves, mostly refines, some learning
- 5-6: Adequate - some improvement, mix of refinement and rewrites
- 3-4: Poor - little improvement, frequent random rewrites
- 0-2: Very poor - no improvement or gets worse, constant thrashing

**Red Flags (score 0-3):**
- Same error appears in builds 1, 3, 5 (not learning)
- Code structure completely different in each build (thrashing)
- Later builds have more errors than earlier builds (regression)

**Examples:**
- **Good (9/10)**: Build 1 has scope error → Build 2 fixes scope → Build 3 adds missing logic
- **Poor (3/10)**: Build 1 has scope error → Build 2 rewrites entire method → Build 3 rewrites again differently → Build 4 back to Build 1 approach

### Calculating the Overall Score

1. Score each dimension individually using the guides above
2. Calculate **Result Quality Total** = sum of scores 1-4 (max 50)
3. Calculate **Process Quality Total** = sum of scores 5-8 (max 50)
4. Calculate **Overall Score** = Result Quality + Process Quality (max 100)
5. Calculate **Overall Score out of 10** = Overall Score / 10.0

### Complete Scoring Example

```
📊 Performance Score: 56/100 (5.6/10)

RESULT QUALITY: 32/50
├─ DML Code Quality: 8/15
│  ├─ Correctness: 4/5 (works but had 12 scope errors initially)
│  ├─ Idioms: 2/5 (used 'bank' keyword incorrectly)
│  └─ Maintainability: 2/5 (code structure improved but still has anti-patterns)
│
├─ Test Quality: 10/15
│  ├─ Coverage: 6/8 (covers main functionality, missing edge cases)
│  └─ Clarity: 4/7 (tests readable but could be better organized)
│
├─ Documentation: 3/5
│  ├─ Completeness: 2/3 (basic docstrings, missing some details)
│  └─ Clarity: 1/2 (clear but could be more detailed)
│
└─ Functionality: 11/15
   ├─ Spec compliance: 6/8 (timer countdown implemented, all registers present)
   └─ Correctness: 5/7 (basic operations work, timer behavior has issues)

PROCESS QUALITY: 24/50
├─ Efficiency: 5/15
│  ├─ Build attempts: 2/5 (8 attempts is poor)
│  ├─ Time: 2/5 (116.5 minutes is poor)
│  └─ Iterations: 1/5 (47 errors is very poor)
│
├─ Methodology: 6/15
│  ├─ Follows workflow: 2/5 (skipped best practice consultation)
│  ├─ Uses best practices: 2/5 (didn't consult docs before implementing)
│  └─ Knowledge protocol: 2/5 (didn't check memories for register patterns)
│
├─ Error Handling: 6/10
│  ├─ Recovery: 3/5 (eventually recovered but took many attempts)
│  └─ Learning: 3/5 (repeated some error patterns)
│
└─ Code Evolution: 7/10
   ├─ Improvement: 4/5 (code improved over iterations)
   └─ Refinement: 3/5 (some refinement, some rewrites)

KEY JUSTIFICATIONS:
• DML Code: "Code eventually works but violated register access scope patterns. 
  Used 'bank' keyword as variable (anti-pattern). Didn't consult 
  07_DML_Register_Access_Scope.md before implementing, leading to 12 scope errors."

• Test Quality: "Tests cover core functionality and use correct register access 
  patterns. However, missing edge case coverage and tests could be better 
  organized with clearer naming."

• Efficiency: "8 build attempts and 116.5 minutes indicates significant 
  inefficiency. 47 total errors suggest agent didn't check best practices 
  before implementing. Most errors were preventable with proper protocol adherence."

• Methodology: "Agent didn't follow knowledge protocol - implemented register 
  access without consulting 07_DML_Register_Access_Scope.md. This caused 12 
  preventable errors. Workflow adherence was poor."

EXPECTED IMPROVEMENT AFTER RECOMMENDATIONS: 56/100 → 75-80/100 (19-24 point gain)
```

## What You Get (Required Output Format)

Every analysis MUST include these sections:

### 1. Performance Score (Required - NEW)
```
📊 Performance Score: X/100 (Y/10)

RESULT QUALITY: X/50
├─ DML Code Quality: X/15 (Correctness X/5, Idioms X/5, Maintainability X/5)
├─ Test Quality: X/15 (Coverage X/8, Clarity X/7)
├─ Documentation: X/5 (Completeness X/3, Clarity X/2)
└─ Functionality: X/15 (Spec compliance X/8, Correctness X/7)

PROCESS QUALITY: X/50
├─ Efficiency: X/15 (Build attempts X/5, Time X/5, Iterations X/5)
├─ Methodology: X/15 (Workflow X/5, Best practices X/5, Knowledge protocol X/5)
├─ Error Handling: X/10 (Recovery X/5, Learning X/5)
└─ Code Evolution: X/10 (Improvement X/5, Refinement X/5)

KEY JUSTIFICATIONS:
• [2-3 sentence justification for each major dimension]

EXPECTED IMPROVEMENT: X/100 → Y/100 (Z point gain)
```

### 2. Session Summary (Required)
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

### 5. Before/After Metrics (Required)
```
📉 Expected Results After Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Performance Score | X/100 | Y/100 | +Z points |
| Build attempts | X | Y | Z% reduction |
| Time to completion | X min | Y min | Z% faster |
| [Error type] errors | X | Y | Z% reduction |
```

**Example Output Format:**
```
📊 Performance Score: 56/100 (5.6/10)

RESULT QUALITY: 32/50
├─ DML Code Quality: 8/15
├─ Test Quality: 10/15
├─ Documentation: 3/5
└─ Functionality: 11/15

PROCESS QUALITY: 24/50
├─ Efficiency: 5/15
├─ Methodology: 6/15
├─ Error Handling: 6/10
└─ Code Evolution: 7/10

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

📊 Performance Score: 56/100 (5.6/10)

RESULT QUALITY: 32/50
├─ DML Code Quality: 8/15
│  └─ Justification: "Code eventually works but violated register access scope 
│     patterns. Used 'bank' keyword as variable (anti-pattern). Didn't consult 
│     07_DML_Register_Access_Scope.md before implementing, leading to 12 scope errors."
├─ Test Quality: 10/15
│  └─ Justification: "Tests cover core functionality and use correct register 
│     access patterns. However, missing edge case coverage."
├─ Documentation: 3/5
└─ Functionality: 11/15

PROCESS QUALITY: 24/50
├─ Efficiency: 5/15
│  └─ Justification: "8 build attempts and 116.5 minutes indicates significant 
│     inefficiency. 47 total errors suggest agent didn't check best practices."
├─ Methodology: 6/15
│  └─ Justification: "Agent didn't follow knowledge protocol - implemented 
│     register access without consulting 07_DML_Register_Access_Scope.md."
├─ Error Handling: 6/10
└─ Code Evolution: 7/10

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
- Performance Score: 56/100 → 75-80/100 (19-24 point improvement)
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

### Step 4.5: Verify Documentation Coverage (CRITICAL - NEW)

**Don't assume existing documents cover the error!** You must verify that referenced documents actually contain the needed information.

#### Documentation Gap Analysis Process

For each error pattern, follow this verification workflow:

1. **Identify what the agent was trying to do**
   - Example: "Agent tried to access register fields using `.field` syntax"

2. **Check agent instructions for guidance**
   - Example: Instructions say "read `07_DML_Register_Access_Scope.md`"

3. **Read the referenced document(s)**
   - **CRITICAL**: Don't assume the document covers the issue - actually read it!
   - Example: Read `07_DML_Register_Access_Scope.md` to see what it covers

4. **Verify coverage of the specific error pattern**
   - Does the document explain how to do what the agent tried?
   - Example: Document covers register VALUE access (`.val`) but NOT field access (`.FIELDNAME`)

5. **Classify the root cause**:
   - **Protocol Violation**: Document exists and covers the issue, but agent didn't read it
   - **Documentation Gap**: Document exists but doesn't cover the specific issue
   - **Missing Document**: No document exists for this topic

#### Example: Field Access Error Analysis

**Error Pattern:**
```
error: reference to unknown object 'WatchdogRegisters.WDOGCONTROL.field'
```

**Step-by-step verification:**

1. **What agent tried:** Access register fields using `.field` syntax
2. **Instruction guidance:** "Read `07_DML_Register_Access_Scope.md` for ANY DML implementation"
3. **Read the document:** Check what `07_DML_Register_Access_Scope.md` actually covers
4. **Verify coverage:**
   ```bash
   # Search for field-related content
   grep -i "field" openspec-memories/07_DML_Register_Access_Scope.md
   # Result: Document only mentions "field" in context of bank/register hierarchy
   # Does NOT explain how to access fields within registers
   ```
5. **Classification:** **Documentation Gap** - Document covers register access but not field access

**Correct diagnosis:**
- ❌ WRONG: "Agent violated protocol by not reading 07_DML_Register_Access_Scope.md"
- ✅ CORRECT: "Document gap - 07_DML_Register_Access_Scope.md doesn't cover field access patterns"

**Correct recommendation:**
- ❌ WRONG: "Strengthen instruction to read existing document"
- ✅ CORRECT: "Create new document `08_DML_Register_Field_Access.md` covering field access patterns"

#### Verification Commands

Use these commands to verify documentation coverage:

```bash
# Search for specific concepts in a document
grep -i "field" openspec-memories/07_DML_Register_Access_Scope.md
grep -i "\.INTEN\|\.RESEN" openspec-memories/*.md

# Check if document covers the error pattern
grep -i "unknown object" openspec-memories/05_DML_Troubleshooting.md

# List all documents that might be relevant
ls openspec-memories/ | grep -i "register\|field\|access"

# Search across all memory documents
grep -r "field access" openspec-memories/
```

#### Common Verification Mistakes

**Mistake 1: Assuming document title = complete coverage**
- Document titled "Register Access" might only cover register values, not fields
- Always read the document to verify actual coverage

**Mistake 2: Confusing similar concepts**
- "Register access" (accessing whole register value) ≠ "Field access" (accessing bits within register)
- "Register scope" (device/bank/register level) ≠ "Field syntax" (how to reference fields)

**Mistake 3: Not distinguishing protocol violation vs documentation gap**
- Protocol violation: Agent should have read existing doc but didn't
- Documentation gap: Agent read the doc but it didn't cover the issue
- These require DIFFERENT solutions!

#### Decision Tree for Root Cause

```
Error Pattern Found
    ↓
Does agent instruction reference a document?
    ↓ YES                           ↓ NO
Read the document              → Missing Document
    ↓                              (Create new doc)
Does it cover this error?
    ↓ YES              ↓ NO
Protocol Violation   Documentation Gap
(Strengthen         (Expand existing doc
 instruction)        or create new doc)
```

#### Impact on Recommendations

Your recommendations must match the root cause:

| Root Cause | Recommendation Type | Example |
|------------|-------------------|---------|
| **Protocol Violation** | Strengthen instruction emphasis | "Add checklist to ensure agent reads doc before implementing" |
| **Documentation Gap** | Expand or create documentation | "Add field access section to existing doc" or "Create new doc for field access" |
| **Missing Document** | Create new documentation | "Create `08_DML_Register_Field_Access.md`" |

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

- **Performance Score**: 56/100 → 75-80/100 (19-24 point improvement)
- **Build attempts**: 8 → 2-3 (62-75% reduction)
- **Time to success**: 10.4 min → 3-4 min (65-70% reduction)
- **Success rate**: 12.5% → 60-70% (55% improvement)

### Score Improvement Breakdown

**Result Quality (32/50 → 42/50):**
- DML Code Quality: 8/15 → 13/15 (better idioms, fewer violations)
- Test Quality: 10/15 → 13/15 (better coverage)
- Documentation: 3/5 → 4/5 (more complete)
- Functionality: 11/15 → 12/15 (fewer spec gaps)

**Process Quality (24/50 → 35/50):**
- Efficiency: 5/15 → 12/15 (fewer builds, faster completion)
- Methodology: 6/15 → 13/15 (better protocol adherence)
- Error Handling: 6/10 → 7/10 (better recovery)
- Code Evolution: 7/10 → 8/10 (more refinement, less thrashing)

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

### Pitfall 6: Assuming Documentation Coverage (NEW - CRITICAL)
**Symptom**: Analysis says "agent should have read document X" but document X doesn't actually cover the error

**Problem**: Assuming a document covers a topic based on its title, without verifying actual content

**Example:**
- Error: `reference to unknown object 'WDOGCONTROL.field'`
- Analysis says: "Agent violated protocol by not reading 07_DML_Register_Access_Scope.md"
- Reality: That document covers register VALUE access (`.val`) but NOT field access (`.FIELDNAME`)
- Correct diagnosis: Documentation gap, not protocol violation

**Solution**: Always verify documentation coverage:
```bash
# Read the referenced document
cat openspec-memories/07_DML_Register_Access_Scope.md

# Search for relevant keywords
grep -i "field" openspec-memories/07_DML_Register_Access_Scope.md
grep -i "\.INTEN\|\.RESEN" openspec-memories/*.md

# Verify the document explains what the agent tried to do
```

**Impact of this mistake:**
- Wrong root cause diagnosis (protocol violation vs documentation gap)
- Wrong recommendation (strengthen instruction vs create new doc)
- Wasted effort (agent will still fail because doc doesn't help)

**Correct approach:**
1. Identify what agent tried to do: "Access register fields"
2. Check instruction guidance: "Read 07_DML_Register_Access_Scope.md"
3. **Read the document**: Verify it covers field access
4. **Verify coverage**: Document covers `.val` but not `.FIELDNAME`
5. **Correct diagnosis**: Documentation gap - need new section or document
6. **Correct recommendation**: Create `08_DML_Register_Field_Access.md`

## Analysis Quality Checklist

Before submitting analysis, verify:

- [ ] **Counted build attempts correctly using TOOL_CALL**
  - [ ] Used `grep -c "TOOL_CALL.*build_simics_project"` not `grep -c "build_simics_project"`
  - [ ] Verified count makes sense (typically 2-15 builds, not 20+)
- [ ] **Calculated comprehensive performance score (100 points)**
  - [ ] Scored all 8 dimensions with justifications
  - [ ] Calculated Result Quality Total (max 50)
  - [ ] Calculated Process Quality Total (max 50)
  - [ ] Provided overall score out of 100 and out of 10
- [ ] Extracted actual error messages (not just counted error lines)
- [ ] Counted unique error occurrences correctly
- [ ] Identified root cause for each major error pattern
- [ ] **Verified documentation coverage (CRITICAL - NEW)**
  - [ ] Read referenced memory documents to verify they cover the error pattern
  - [ ] Distinguished between protocol violation vs documentation gap
  - [ ] Used grep/search to confirm document content matches error needs
  - [ ] Classified root cause correctly: Protocol Violation / Documentation Gap / Missing Document
- [ ] Provided EXACT text for instruction updates (not generic advice)
- [ ] Calculated quantified before/after metrics including score improvement
- [ ] Focused on patterns (3+ occurrences), not one-off issues
- [ ] Checked agent instructions and memory docs for gaps
- [ ] Provided specific file paths for all recommendations
- [ ] **Matched recommendations to root cause type**
  - [ ] Protocol Violation → Strengthen instructions
  - [ ] Documentation Gap → Expand existing doc or create new section
  - [ ] Missing Document → Create new document with full content outline

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

- Getting Started Guide: See `steering/getting-started.md`
- ADK Documentation: https://github.com/google/adk-python
- OpenSpec Integration Sample: `contributing/samples/openspec_integration/`
- Real Analysis Example: See "Real-World Example Analysis" section above
