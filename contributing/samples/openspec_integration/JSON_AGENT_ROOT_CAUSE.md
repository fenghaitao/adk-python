# JSON Agent Root Cause Analysis

## Date
2025-12-18

## Critical Discovery

**The JSON analysis tools are NOT being registered with the LLM!**

### Evidence

Checked the latest session file: `meta_improve_meta_improve_20251218_214441.session.json`

**Tools available to the agent:**
- `list_directory` ✅
- `read_file` ✅

**Tools MISSING:**
- `extract_session_metrics` ❌
- `extract_error_patterns` ❌
- `query_session_data` ❌

### Why the Agent Can't Call the Tools

The agent announces "Now I'll extract metrics using JSON tools" but immediately ends because:
1. The LLM doesn't see `extract_session_metrics` in its available tools
2. The LLM can't call a tool that doesn't exist
3. The session ends because there's nothing more the agent can do

### Code Analysis

In `meta_improve_json_agent.py` lines 405-413:

```python
# Tools
tools = kwargs.get("tools", [])
tools.append(create_openspec_toolset())

# Add JSON analysis tools
tools.extend([
  JsonSessionMetricsTool(),
  JsonErrorPatternTool(),
  JsonSessionQueryTool(),
])

kwargs["tools"] = tools
```

The code LOOKS correct - it's adding the JSON analysis tools to the tools list.

### Hypothesis: Tool Registration Failure

Possible causes:
1. **Import Error**: The JSON analysis tools may be failing to import
2. **Tool Initialization Error**: The tools may be throwing exceptions during `__init__`
3. **ADK Tool Registration**: ADK may be silently failing to register these tools
4. **Agent Discovery**: The agent.py file may not be loading the correct agent

### Next Steps

1. Check if there are any import errors when loading the agent
2. Check if the tools are being instantiated correctly
3. Compare with the text agent to see how bash_command tool is registered
4. Add logging/debugging to see where tool registration fails
5. Check the agent.py file to ensure it's loading meta_improve_json_agent correctly

### Comparison: Text Agent vs JSON Agent

**Text Agent** (working):
- Uses `bash_command` tool from openspec_toolset
- Tool is part of create_openspec_toolset()
- Successfully registered and callable

**JSON Agent** (not working):
- Uses custom JSON analysis tools
- Tools are instantiated separately
- **NOT being registered** with the LLM

### Immediate Action Required

Check the agent.py file in the meta improvement agent directory to see which agent is actually being loaded.


## Solution

### Root Cause
ADK requires tools to be provided as **Toolsets** (BaseToolset), not as individual tool instances.

### The Fix

**Before (broken)**:
```python
tools.extend([
  JsonSessionMetricsTool(),
  JsonErrorPatternTool(),
  JsonSessionQueryTool(),
])
```

**After (working)**:
```python
# Created JsonAnalysisToolset class in json_analysis_tools.py
class JsonAnalysisToolset(BaseToolset):
  def __init__(self):
    super().__init__()
    self.name = "json_analysis_toolset"
    self._tools = [
      JsonSessionMetricsTool(),
      JsonErrorPatternTool(),
      JsonSessionQueryTool(),
    ]

  async def get_tools(self, readonly_context=None) -> list:
    return self._tools

# In meta_improve_json_agent.py
tools.append(create_json_analysis_toolset())
```

### Changes Made

1. **json_analysis_tools.py**:
   - Added `from google.adk.tools.base_toolset import BaseToolset`
   - Created `JsonAnalysisToolset` class extending `BaseToolset`
   - Created `create_json_analysis_toolset()` factory function

2. **meta_improve_json_agent.py**:
   - Changed import from individual tool classes to `create_json_analysis_toolset`
   - Changed `tools.extend([...])` to `tools.append(create_json_analysis_toolset())`

### Why This Works

ADK's agent initialization expects tools to be provided as Toolset objects, not raw tool instances. The Toolset pattern:
- Provides a consistent interface via `get_tools()` method
- Allows ADK to properly register and manage tools
- Matches the pattern used by `create_openspec_toolset()`

### Testing

After this fix, the JSON agent should have all tools available:
- `list_directory` ✅
- `read_file` ✅
- `write_file` ✅
- `bash_command` ✅
- `replace_string_in_file` ✅
- `extract_session_metrics` ✅ (NEW)
- `extract_error_patterns` ✅ (NEW)
- `query_session_data` ✅ (NEW)
