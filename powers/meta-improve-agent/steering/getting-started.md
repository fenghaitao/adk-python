# Getting Started with Meta Improve Agent

This guide will help you get started analyzing apply_agent sessions to identify patterns and improve your agent's performance.

## What is Meta Improve Agent?

Meta Improve Agent is a guided analysis approach that helps you examine session logs from apply_agent executions to identify patterns, extract learnings, and generate concrete improvements to your agent's instructions and documentation.

## Prerequisites

1. **Session JSON files**: Run apply_agent to generate `.session.json` files in `adk_openspec_apply_agent/`
2. **Agent instructions**: Located at `adk_openspec_apply_agent/apply_agent_instruction.md`
3. **Memory documents**: Located in `openspec-memories/` directory

**No installation required** - your AI assistant can read and analyze these files directly!

## Quick Start

### Step 1: Ensure You Have Session Files

The analysis works with session JSON files from apply_agent executions. These files are typically located in:

```
adk_openspec_apply_agent/apply_implement-wdt-initial_20251214_161520.session.json
```

If you don't have any session files yet, run apply_agent first to generate them.

### Step 2: Ask for Analysis

Simply ask your AI assistant to analyze the session:

```
Analyze the session file adk_openspec_apply_agent/apply_implement-wdt-initial_20251214_161520.session.json
and tell me what improvements should be made to the agent instructions and memory documents.
```

The assistant will:
1. Read and parse the session JSON file (in chunks if large)
2. Extract all build attempts, errors, and fixes
3. Read the agent instruction file to understand current capabilities
4. Read relevant memory documents to identify gaps
5. Identify error patterns and propose specific improvements

### Important: Handling Large Session Files

Session JSON files can be 100KB+ in size. For large files:

**Recommended approach:**
```
Read the session file in 64KB chunks and analyze error patterns. 
Start with offset 0, length 65536, then continue with subsequent chunks if needed.
```

**Why chunked reading?**
- Avoids overwhelming the context window
- Allows incremental analysis
- More efficient for large files

**What to look for in each chunk:**
- Events with "error" or "failure" indicators
- Build attempt patterns
- Tool call sequences
- Timestamps to calculate durations

### Step 3: Review the Analysis

The assistant provides structured output with:

- **Session Summary**: How long it took, how many attempts, success rate
- **Top Error Patterns**: Most frequent errors with examples and root causes
- **Knowledge Gaps**: What the agent should have known but didn't
- **Proposed Improvements**: Specific changes to make
- **Expected Impact**: Estimated time savings and error reduction

### Step 4: Apply Improvements

Based on the analysis, you can:

1. **Update Agent Instructions**: Add error prevention strategies to `apply_agent_instruction.md`
2. **Create Memory Documents**: Fill documentation gaps in `openspec-memories/`
3. **Update Existing Docs**: Add troubleshooting sections and examples
4. **Add Validation Checks**: Prevent common errors before building

## Common Use Cases

### Use Case 1: Post-Implementation Review

After completing a complex implementation:

```
Read the latest session JSON file in adk_openspec_apply_agent/ in chunks 
and tell me what could be improved
```

### Use Case 2: Pattern Discovery

Looking for recurring issues across multiple sessions:

```
Analyze all session JSON files in adk_openspec_apply_agent/ and identify 
the top 5 most common error patterns
```

### Use Case 3: Documentation Gap Analysis

Finding missing or incomplete documentation:

```
Review the session file (read in chunks) and identify what memory documents 
in openspec-memories/ are missing or need updates
```

### Use Case 4: Time Optimization

Finding the biggest time sinks:

```
Analyze the session JSON and tell me which errors took the most time to resolve. 
Calculate time between error events and successful fixes.
```

## Practical Example: Chunked Reading

Here's a complete example of how to analyze a large session file:

**Step 1: Check file size**
```
How large is the session file demo/adk_openspec_project/adk_openspec_agent/*.session.json?
```

**Step 2: Read first chunk**
```
Read the first 64KB (offset=0, length=65536) of the session JSON file 
and show me the structure and first few events
```

**Step 3: Scan for errors**
```
Continue reading the file in 64KB chunks and extract all events that contain 
errors, failures, or build attempts. Track the event types and timestamps.
```

**Step 4: Analyze patterns**
```
Based on the events you've extracted, identify:
1. Most common error types
2. Average time between error and fix
3. Which fixes worked vs failed
4. What knowledge was missing
```

**Step 5: Generate recommendations**
```
Based on the error patterns, recommend:
1. Updates to agent instructions
2. New memory documents to create
3. Validation checks to add
```

## Understanding the Output

### Error Pattern Example

```
Error Pattern: "unknown identifier: 'bank'"
- Type: scope_error
- Frequency: 12 occurrences
- Time spent: 3.2 minutes
- Successful fix: Use BankName.RegisterName pattern
- Failed attempts: bank.RegisterName, regs.bank.RegisterName
- Root cause: Wrong scope/context for register access
```

### Improvement Proposal Example

```
Proposed Improvement:
1. Add to apply_agent.py instructions:
   "Before implementing register access, check context:
    - Device level: Use BankName.RegisterName
    - Bank level: Use RegisterName directly
    - Register level: Use this"

2. Create memory document: 07_DML_Common_Compilation_Errors.md
   - Section for scope errors
   - Examples of correct patterns
   - Common mistakes to avoid

3. Add validation step:
   "Search code for 'bank.' or 'regs.' before building"

Expected Impact:
- Reduce build attempts from 8 to 2-3
- Save 5-7 minutes per session
- Prevent 80% of scope errors
```

## Advanced Usage

### Batch Analysis

Analyze multiple sessions at once:

```
Analyze all .session.txt files in the sessions/ directory and create a comprehensive improvement plan
```

### Comparative Analysis

Compare sessions over time:

```
Compare this week's sessions to last week's and tell me if we're improving
```

### Targeted Analysis

Focus on specific error types:

```
Analyze the session and focus only on compilation errors, ignore other issues
```

## Tips for Best Results

1. **Provide Complete Sessions**: Make sure session files include the entire execution from start to finish

2. **Be Specific**: If you want to focus on particular aspects, mention them explicitly

3. **Review Before Applying**: Always review proposed improvements before implementing them

4. **Measure Impact**: After applying improvements, run new sessions and compare results

5. **Iterate**: Run analysis regularly to continuously improve your agent

## Troubleshooting

### Issue: Agent can't find session file

**Solution**: Provide the full path to the session file:
```
Analyze /full/path/to/session.txt
```

### Issue: Analysis is too generic

**Solution**: Ask for more specific analysis:
```
Analyze the session and provide detailed examples for each error pattern
```

### Issue: Too much output

**Solution**: Ask for a summary:
```
Analyze the session and give me just the top 3 most important improvements
```

## Next Steps

After getting comfortable with basic analysis:

1. Set up automated analysis after each apply_agent run
2. Create a feedback loop: analyze → improve → test → measure
3. Build a library of common error patterns and fixes
4. Share learnings across your team

## Example Workflow

Here's a complete workflow for continuous improvement:

```bash
# 1. Run apply_agent on a task
adk run apply_agent "Implement WDT device"

# 2. Analyze the session
adk run meta_improve_agent "Analyze the latest session file"

# 3. Review and apply improvements
# (manually edit agent instructions or memory docs)

# 4. Test improvements
adk run apply_agent "Implement another similar device"

# 5. Compare results
adk run meta_improve_agent "Compare the last two sessions"
```

## Getting Help

If you need help:
- Check the POWER.md for detailed documentation
- Review example sessions in the samples directory
- Ask the agent for clarification: "Explain what you mean by scope error"
