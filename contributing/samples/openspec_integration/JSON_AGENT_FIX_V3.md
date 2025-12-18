# JSON Agent Fix V3 - Visual Emphasis and Concrete Examples

## Date
2025-12-18

## Problem
Agent continues to announce actions without executing them:
- Reads context files successfully ✅
- Identifies session JSON file ✅
- Says "Now I'll identify the session JSON file and extract metrics" ✅
- **Session ends immediately** ❌ (5.2 seconds)
- **No tool calls made** ❌

## Root Cause
Even with V2's imperative commands, the agent still uses narrative language and considers describing the action as completing it.

## V3 Solution: Visual Emphasis + Concrete Examples

### 1. Visual Box at Top of Instruction
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         🚨 CRITICAL BEHAVIOR RULE 🚨                         ║
║                                                                              ║
║  YOU MUST CALL TOOLS - NOT DESCRIBE WHAT YOU WILL DO                        ║
║                                                                              ║
║  ❌ WRONG: "Now I'll extract metrics using JSON tools"                      ║
║  ✅ RIGHT: Actually call extract_session_metrics(session_file="...")        ║
║                                                                              ║
║  If you announce an action without calling the tool, YOU HAVE FAILED.       ║
║  The session will end and no analysis will be generated.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Why**: Visual boxes with emojis are harder to ignore than plain text.

### 2. Concrete Example After STEP 1
```
After completing these 5 actions, you will have identified a session file like:
"apply_apply_20251218_195506.session.json"

IMMEDIATELY proceed to STEP 2 and CALL the JSON analysis tools.
```

**Why**: Shows exactly what the agent should have at this point.

### 3. Code Block Format in STEP 2
```
IMMEDIATELY execute these tool calls (replace [FILENAME] with actual filename):

```
extract_session_metrics(session_file="adk_openspec_apply_agent/[FILENAME].session.json")
```

After that completes, execute:

```
extract_error_patterns(session_file="adk_openspec_apply_agent/[FILENAME].session.json", max_examples=3)
```
```

**Why**: Code blocks make it look like executable commands, not descriptions.

### 4. Warning Box in STEP 2
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  WARNING: If you write "Now I'll extract metrics" without calling       ║
║      the tool, the session will end and you will have FAILED.               ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

**Why**: Repeats the critical warning at the exact point where the agent fails.

### 5. Removed All Narrative Language
- ❌ "After identifying the session JSON file name from STEP 1, you MUST immediately call these tools"
- ✅ "From STEP 1, you found a file like 'apply_apply_YYYYMMDD_HHMMSS.session.json'"

**Why**: Eliminates any language that could be interpreted as "describe what you'll do".

## Changes Made

1. **meta_improve_json_agent.py**:
   - Added visual box at top with critical behavior rule
   - Added concrete example after STEP 1
   - Reformatted STEP 2 with code blocks
   - Added warning box in STEP 2
   - Removed all narrative language

## Expected Outcome

The agent should:
1. Read context files (already works)
2. See the visual warning boxes
3. See the concrete example showing what it should have
4. See the code block format suggesting executable commands
5. **Actually call the tools** instead of announcing it will

## Testing

Run the JSON agent again:
```bash
cd /home/hfeng1/demo/adk_openspec_project
../adk-python/openspec-scripts/run-meta-improve.sh --agent json
```

## Success Criteria

- Agent calls `extract_session_metrics` tool
- Agent calls `extract_error_patterns` tool
- Session duration > 30 seconds (not 5 seconds)
- Analysis report is generated

## If This Still Fails

Consider:
1. The model may have a fundamental limitation with tool calling
2. The instruction may be too long (causing context issues)
3. May need to add explicit examples of successful tool calls
4. May need to use a different model
5. The text-based agent (proven to work) should be used instead

## Comparison to Text Agent

The text-based agent works because:
- Uses bash commands (simpler, more direct)
- Analyzes .txt files (human-readable)
- Has shorter, clearer instructions
- No JSON parsing complexity

If JSON agent continues to fail after V3, recommend using text agent for production.
