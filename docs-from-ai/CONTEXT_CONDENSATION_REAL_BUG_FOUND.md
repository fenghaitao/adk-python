# Finding the Real Bug - Where Do None-ID Function Responses Come From?

## Summary

Option 3 was logically flawed (throwing away summaries we just created). Let's find the REAL source of the bug.

## The Production Error

```
⚠️  Warning: Function responses found but no valid IDs. Skipping rearrangement.

litellm.exceptions.BadRequestError: An assistant message with 'tool_calls' must be 
followed by tool messages responding to each 'tool_call_id'. The following tool_call_ids 
did not have response messages: call_YFqzxl9yywb0jfPoIzRCNdH3
```

## Where This Warning Comes From

```python
def _rearrange_events_for_latest_function_response(events):
  function_responses = events[-1].get_function_responses()
  
  function_responses_ids = set()
  for function_response in function_responses:
    if function_response.id is not None:
      function_responses_ids.add(function_response.id)
  
  if not function_responses_ids:
    print("⚠️  Warning: Function responses found but no valid IDs. Skipping rearrangement.")
    return events  # ← Returns malformed events!
```

**This means:** The last event has function_response objects, but ALL of them have `id=None`.

## How Can function_response.id Be None?

Let's trace where function responses are created:

### 1. Normal Tool Execution

When a tool runs, ADK creates a function response with a valid ID:

```python
# In tool execution code
function_response = types.FunctionResponse(
    name=tool_name,
    response=tool_result,
    id=function_call_id  # ← Should have valid ID
)
```

### 2. Event Restoration from Session

When restoring from saved session:

```python
# session.json contains:
{
  "events": [
    {
      "content": {
        "parts": [
          {
            "function_response": {
              "name": "tool_name",
              "response": {...},
              "id": "call_ABC"  # ← Should be preserved
            }
          }
        ]
      }
    }
  ]
}
```

But if session serialization/deserialization loses the ID...

### 3. Manual Event Creation

If code manually creates events without IDs:

```python
# BAD:
event = Event(
    content=types.Content(
        role='function',
        parts=[types.Part(
            function_response=types.FunctionResponse(
                name='tool',
                response={},
                # id=None  ← MISSING!
            )
        )]
    )
)
```

### 4. Event Conversion or Copying

If events are copied/converted and IDs are lost:

```python
# During condensation, when creating truncated events:
new_part = types.Part.from_function_response(
    name=func_resp.name,
    response=new_response
    # id not passed! ← BUG!
)
```

## Found It! Check Condensation Code

Looking at condensation Step 1 (truncating tool outputs):

```python
# STEP 1: Truncate large tool outputs
for event in events:
  if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
    new_parts = []
    for part in event.content.parts:
      if hasattr(part, 'function_response') and part.function_response:
        func_resp = part.function_response
        if hasattr(func_resp, 'response') and func_resp.response:
          try:
            result_str = json.dumps(func_resp.response, indent=0)
            if len(result_str) > _CONTEXT_MAX_TOOL_OUTPUT_TOKENS * 4:
              truncated_result = _truncate_tool_output(result_str, _CONTEXT_MAX_TOOL_OUTPUT_TOKENS)
              new_response = {"output": truncated_result}
              new_part = types.Part.from_function_response(
                  name=func_resp.name,
                  response=new_response
                  # ← BUG: Missing id=func_resp.id!
              )
              new_parts.append(new_part)
              continue
```

**FOUND THE BUG!**

When creating a new truncated function response, we pass:
- `name=func_resp.name` ✅
- `response=new_response` ✅
- **Missing: `id=func_resp.id`** ❌

## The Fix

```python
# STEP 1: Truncate large tool outputs
if len(result_str) > _CONTEXT_MAX_TOOL_OUTPUT_TOKENS * 4:
  truncated_result = _truncate_tool_output(result_str, _CONTEXT_MAX_TOOL_OUTPUT_TOKENS)
  new_response = {"output": truncated_result}
  new_part = types.Part.from_function_response(
      name=func_resp.name,
      response=new_response,
      id=func_resp.id  # ← FIX: Preserve the ID!
  )
```

## Why This Bug Occurs

1. Agent makes many tool calls with large outputs
2. Context exceeds 128K tokens
3. Condensation triggered
4. STEP 1 truncates large tool outputs
5. **BUG**: Creates new function_response parts WITHOUT IDs
6. These events go through rearrangement
7. Rearrangement finds responses with `id=None`
8. Warning printed, returns malformed events
9. LLM API rejects them: "tool_call_id did not have response messages"

## Timeline in Production

```
21:30:15 - Context condensation triggered. Current tokens: 129911
  ↓
STEP 1: Truncate tool outputs
  ↓
Create new function_response parts (BUG: missing IDs!)
  ↓
STEP 2-7: Normal processing
  ↓
✅ Context condensed: 129911 → 19544 tokens
  ↓
Return condensed events with None-ID responses
  ↓
_get_contents() called
  ↓
_rearrange_events_for_latest_function_response()
  ↓
⚠️  Warning: Function responses found but no valid IDs. Skipping rearrangement.
  ↓
Return events as-is (with None-ID responses)
  ↓
Convert to LLM API format
  ↓
❌ litellm.exceptions.BadRequestError: tool_call_id did not have response messages
```

## The Real Fix

**Single line change in contents.py, STEP 1:**

```python
new_part = types.Part.from_function_response(
    name=func_resp.name,
    response=new_response,
    id=func_resp.id  # ← ADD THIS LINE
)
```

That's it! No need for Option 3 filtering. Just preserve the ID when truncating.

## Why Option 2 Is Still Good

Option 2 (skipping summary events in rearrangement) is still a good defensive practice:
- Summary events should never be rearranged anyway
- Prevents edge cases where summary might be last event
- Belt-and-suspenders approach

But it's not the fix for this bug. The fix is preserving IDs during truncation.

## Conclusion

**Root Cause:** Tool output truncation in Step 1 creates new function_response parts without preserving the original ID.

**Fix:** Add `id=func_resp.id` when creating truncated function response.

**Option 3 Status:** REJECTED - wasteful and illogical, not needed.

**Option 2 Status:** KEEP - defensive practice, doesn't hurt.
