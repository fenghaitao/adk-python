# JSON Agent - API Pattern Mismatch (REAL ROOT CAUSE)

## Date
2025-12-18

## Critical Discovery

**The JSON analysis tools use the WRONG ADK API pattern!**

### The Problem

Our JSON tools were implemented using:
```python
class JsonSessionMetricsTool(BaseTool):
    class InputSchema(BaseModel):  # ❌ WRONG
        session_file: str = Field(...)
    
    async def run(self, context, session_file):  # ❌ WRONG
        ...
```

But ADK's BaseTool expects:
```python
class SpecKitReadTool(BaseTool):
    def _get_declaration(self):  # ✅ CORRECT
        return types.FunctionDeclaration(...)
    
    async def run_async(self, *, args, tool_context):  # ✅ CORRECT
        ...
```

### Evidence

1. **Tools not listed to LLM**: User reported the LLM only sees `read_file`, `write_file`, `bash_command`, etc. - NOT our JSON tools
2. **SpecKit tools work**: They use `_get_declaration()` and `run_async()`
3. **Our tools use different pattern**: We use `InputSchema` class and `run()` method
4. **BaseTool source code**: Confirms `_get_declaration()` and `run_async()` are the expected methods

### Why This Happened

We likely copied the pattern from a different tool framework or documentation that uses Pydantic's `InputSchema` pattern. This is a valid pattern in some frameworks, but not in ADK's BaseTool.

### What Needs to Change

All three JSON analysis tools need to be refactored:

1. **JsonSessionMetricsTool**
2. **JsonErrorPatternTool**  
3. **JsonSessionQueryTool**

Each needs:
- Remove `class InputSchema(BaseModel)`
- Add `def _get_declaration(self)` returning `types.FunctionDeclaration`
- Change `async def run(...)` to `async def run_async(self, *, args, tool_context)`
- Extract parameters from `args` dict instead of method parameters

### Estimated Effort

- ~2-3 hours to refactor all three tools
- Need to update standalone test script
- Need to retest after changes
- Risk of introducing new bugs during refactoring

## Recommendation

Given:
1. **Text-based agent works perfectly** (production-ready)
2. **Significant refactoring required** (2-3 hours, risk of bugs)
3. **Uncertain if model will call tools** (even after fix, narrative behavior issue remains)
4. **Limited ROI** (text agent already solves the problem)

**RECOMMEND: Use text-based agent for production, defer JSON agent refactoring**

### If JSON Agent is Required

Follow this refactoring plan:

#### Step 1: Update JsonSessionMetricsTool
```python
def _get_declaration(self):
    from google.genai import types
    return types.FunctionDeclaration(
        name="extract_session_metrics",
        description="...",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "session_file": types.Schema(
                    type=types.Type.STRING,
                    description="Path to session JSON file"
                )
            },
            required=["session_file"]
        )
    )

async def run_async(self, *, args, tool_context):
    session_file = args.get("session_file")
    if not session_file:
        return {"error": "session_file required"}
    # ... rest of implementation
```

#### Step 2: Update JsonErrorPatternTool
Similar pattern with `max_examples` parameter

#### Step 3: Update JsonSessionQueryTool
Similar pattern with `query_type`, `filter_tool`, `limit` parameters

#### Step 4: Update test_json_tools.py
Change how tools are called to match new API

#### Step 5: Test and validate
- Standalone tests pass
- Tools appear in LLM tool list
- Agent can call tools

## Files Affected

- `json_analysis_tools.py` - All three tool classes
- `test_json_tools.py` - Test script
- `json_analysis_tools.py.backup` - Created backup before changes

## Current Status

- ✅ Root cause identified (API pattern mismatch)
- ✅ Backup created
- ⏸️ Refactoring started but incomplete
- ❌ Tools still not working

## Alternative: Use Text Agent

The text-based meta-improve agent:
- ✅ Works correctly (proven in production)
- ✅ Generates complete analysis reports
- ✅ Uses simple bash commands on .txt files
- ✅ No refactoring needed
- ✅ Ready to use now

Command:
```bash
./openspec-scripts/run-meta-improve.sh --agent text
```

## Lessons Learned

1. **Always check the framework's API pattern** before implementing tools
2. **Look at working examples** in the same codebase (SpecKit tools)
3. **Test tool registration early** - don't wait until full implementation
4. **Have a working alternative** - text agent saved us here
5. **Know when to stop** - sometimes the working solution is good enough

## Next Steps

### Option A: Complete JSON Agent (if required)
1. Complete refactoring of all three tools
2. Update tests
3. Validate tools appear in LLM list
4. Test agent behavior
5. May still face narrative behavior issue

### Option B: Use Text Agent (recommended)
1. Document JSON agent as incomplete/experimental
2. Use text agent for all production work
3. Revisit JSON agent if/when needed

## Conclusion

The JSON agent failure was due to using the wrong ADK API pattern (`InputSchema`/`run()` instead of `_get_declaration()`/`run_async()`). While fixable, the text-based agent already provides a working solution, making the JSON agent refactoring a low-priority task.
