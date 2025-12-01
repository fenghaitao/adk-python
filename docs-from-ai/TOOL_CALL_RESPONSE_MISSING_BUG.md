# ADK Bug Report: Missing Tool Response in Message History

## Error Summary

```
litellm.exceptions.BadRequestError: litellm.BadRequestError: Github_copilotException - 
An assistant message with 'tool_calls' must be followed by tool messages responding to 
each 'tool_call_id'. The following tool_call_ids did not have response messages: 
call_Qo7F8nw7c3CERVd7xEEvkHo3
```

## Location
- **Log File**: `/nfs/pdx/home/yongzhuo/wp5/ai_agents/tests/adk-mcp-rag/g5m_openspec/wdt_dbg16.3.log`
- **Stage**: Stage 3 (Test Implementation - Prompt 3)
- **Model**: `github_copilot/gpt-5-mini`
- **Timestamp**: December 1, 2025, 22:21

## Root Cause

This is an **OpenAI API protocol violation**. When the LLM makes a tool call:
1. Assistant sends a message with `tool_calls` field containing tool call ID(s)
2. System executes the tools and MUST include tool responses in the next API request
3. Each tool response MUST reference the original `tool_call_id`

The error indicates that ADK is sending a follow-up request to the LLM that includes the assistant's tool call message, but **missing the corresponding tool response message(s)**.

## Expected Message Sequence

```
Request N:
  messages: [
    {role: "user", content: "Fix the tests"},
    ...
  ]

Response N (from LLM):
  role: "assistant"
  tool_calls: [
    {id: "call_Qo7F8nw7c3CERVd7xEEvkHo3", function: {name: "run_terminal", ...}}
  ]

Request N+1 (CORRECT):
  messages: [
    {role: "user", content: "Fix the tests"},
    ...,
    {role: "assistant", tool_calls: [{id: "call_Qo7F8nw7c3CERVd7xEEvkHo3", ...}]},
    {role: "tool", tool_call_id: "call_Qo7F8nw7c3CERVd7xEEvkHo3", content: "...output..."}  ← REQUIRED!
  ]

Request N+1 (ACTUAL - WRONG):
  messages: [
    {role: "user", content: "Fix the tests"},
    ...,
    {role: "assistant", tool_calls: [{id: "call_Qo7F8nw7c3CERVd7xEEvkHo3", ...}]}
    ← MISSING TOOL RESPONSE!
  ]
```

## Bug Location (Suspected)

Based on the stack trace, the issue is in the message history management:

```
src/google/adk/flows/llm_flows/base_llm_flow.py, line 535, in _run_one_step_async
src/google/adk/flows/llm_flows/base_llm_flow.py, line 859, in _call_llm_async
src/google/adk/models/lite_llm.py, line 855, in generate_content_async
```

**Likely causes:**
1. **Conversation history truncation** - Tool response messages being removed during history trimming
2. **Message filter bug** - Tool responses filtered out when constructing the messages array
3. **Async timing issue** - Tool response not yet added to history when next LLM call is made
4. **Session restoration** - When resuming from saved session, tool responses not properly reconstructed

## Reproduction Context

This occurred during the autonomous test-fixing loop in Stage 3:
- Device: `test_dev`
- Prompt: `openspec-prompts/3.md` (DML Test Fixing Task)
- Session file: `wdt_dbg16_2_openspec.session.json`
- Stage 2 completed successfully (build fixes applied)
- Stage 3 began and failed immediately on first LLM interaction

## Investigation Steps

1. **Check session file** for the last tool call before failure:
   ```bash
   python3 -c "
   import json
   data = json.load(open('wdt_dbg16/adk_openspec_agent/wdt_dbg16_2_openspec.session.json'))
   # Find the tool call with ID call_Qo7F8nw7c3CERVd7xEEvkHo3
   # Verify if tool response exists in events
   "
   ```

2. **Examine message construction** in `base_llm_flow.py`:
   - How are messages assembled before sending to LLM?
   - Is there filtering/truncation logic that might remove tool responses?
   - Are tool responses properly tagged with `role: "tool"` and `tool_call_id`?

3. **Check LiteLLM integration** in `lite_llm.py`:
   - How are tool call events converted to OpenAI message format?
   - Is the tool response → message conversion correct?

4. **Session management**:
   - When loading from session file, are tool responses reconstructed?
   - Is there a race condition between tool execution and message history update?

## Workaround

None available - this is a framework bug that prevents the agent from continuing.

## Impact

- **Severity**: CRITICAL - Blocks autonomous agent operation
- **Frequency**: Unknown - may be intermittent or specific to certain tool calls
- **Scope**: Affects multi-turn conversations with tool use

## Recommended Fix Areas

1. **src/google/adk/flows/llm_flows/base_llm_flow.py**:
   - Add validation before LLM call: Ensure every `tool_calls` in assistant messages has corresponding tool response
   - Add assertion/warning if mismatch detected

2. **Message history management**:
   - Ensure tool responses are NEVER filtered/removed if their tool_call_id is still in history
   - Implement invariant check: `len(tool_calls) == len(tool_responses_for_those_calls)`

3. **Logging enhancement**:
   - Log complete message array before sending to LLM (for debugging)
   - Log tool execution and response addition to history

4. **Session restoration**:
   - Verify tool responses are fully restored when loading session
   - Add integrity check on session load

## Related Files

- `/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/src/google/adk/flows/llm_flows/base_llm_flow.py`
- `/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/src/google/adk/models/lite_llm.py`
- `/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/src/google/adk/cli/cli.py`

## Next Steps

1. Developer to examine message construction logic in `base_llm_flow.py`
2. Add debug logging to trace tool call → tool response → message array
3. Verify session serialization/deserialization preserves tool responses
4. Add validation to catch this error before sending to LLM

---
**Status**: OPEN  
**Priority**: P0 (blocks autonomous operation)  
**Assigned**: ADK Core Team
