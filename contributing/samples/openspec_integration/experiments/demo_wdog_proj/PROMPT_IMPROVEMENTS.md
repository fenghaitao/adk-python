# Agent Prompt Improvements

## Problem Analysis from test.log

The agent was running but not completing the task effectively because:

1. **Too Vague**: The original prompt said "implement this task" without clear step-by-step instructions
2. **No Clear Actions**: Agent spent time exploring files rather than taking action
3. **Missing Context**: No concrete code examples showing WHAT to implement
4. **Unclear Success Criteria**: Agent didn't know when it was done

## Original Prompt Issues

```
You are working on a Simics Device Modeling Language (DML) project.

Task: Implement Watchdog Load register logic

Description:
Implement the Watchdog Load register in the DML device model.

**Implementation Requirements:**
1. Review the OpenSpec change proposal: ...
2. Read the current DML implementation: ...
3. Add register field in the DML bank structure
...
```

### Problems:
- ❌ Too passive - "review", "read" without "DO this specific thing"
- ❌ No concrete code examples
- ❌ Unclear what "implement" means specifically
- ❌ Agent explored endlessly without taking action

## Improved Prompt Strategy

### Key Improvements:

1. **Directive Language**
   - OLD: "Please implement this task"
   - NEW: "IMPORTANT: You are an implementation agent. Follow these steps EXACTLY in order."

2. **Step-by-Step Instructions**
   - Clear numbered steps: STEP 1, STEP 2, etc.
   - Each step has specific, actionable instructions
   - Steps build on each other logically

3. **Concrete Code Examples**
   - NEW: Includes actual DML code template to follow
   - Shows exact syntax expected
   - Removes ambiguity about what to write

4. **Clear Success Criteria**
   - NEW: "When done, respond with: 'IMPLEMENTATION COMPLETE - [description]'"
   - Agent knows exactly what constitutes completion

5. **Critical Rules Section**
   - NEW: Explicit DO and DO NOT instructions
   - Prevents common failure modes (endless exploration)
   - Forces action-taking behavior

## New Prompt Structure

```
IMPORTANT: You are an implementation agent. Follow these steps EXACTLY in order.

**YOUR MISSION**: [Clear, specific goal]

**STEP 1 - READ THE CHANGE PROPOSAL**
[Specific files to read and what to look for]

**STEP 2 - READ THE CURRENT CODE**
[Where to look and what to notice]

**STEP 3 - IMPLEMENT THE CHANGES**
[Concrete code example with exact syntax]

**STEP 4 - VERIFY YOUR WORK**
[Checklist of what to verify]

**STEP 5 - COMPLETE THE TASK**
[Exact completion message to send]

**CRITICAL RULES:**
- DO NOT just explore files endlessly
- DO implement the actual code
- DO edit the files using tools
...

Start with STEP 1 now!
```

## Results Expected

With the improved prompt, the agent should:

✅ Follow a clear, linear workflow
✅ Take concrete actions (file edits) instead of just exploring
✅ Have a concrete code template to follow
✅ Know when the task is complete
✅ Complete tasks faster with fewer LLM calls

## Implementation

### Files Updated:

1. **test_first_task.sh** - Improved prompt for manual testing
   - Includes specific DML code template for WDOGLOAD register
   - Clear 5-step process
   - Directive language throughout

2. **run_openspec_from_ddm.py** - Improved prompt template for orchestration
   - Parameterized template that works for all tasks
   - Adapts to register implementation vs test tasks
   - Maintains directive, actionable language

## Testing

To test the improved prompt:

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
bash test_first_task.sh
```

Expected behavior:
1. Agent reads change proposal
2. Agent reads current DML code
3. Agent EDITS the DML file to add WDOGLOAD register
4. Agent responds with "IMPLEMENTATION COMPLETE"
5. Task completes in < 10 LLM calls instead of endless exploration

## Key Principle

**"Show, Don't Tell"** - Instead of asking the agent to figure out what to do, show them exactly what code to write with concrete examples. This dramatically improves success rate.
