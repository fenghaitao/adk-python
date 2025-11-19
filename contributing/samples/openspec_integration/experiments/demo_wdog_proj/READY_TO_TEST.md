# Ready to Test - Updated Prompt with MCP Support

## What Was Fixed

1. ✅ **Removed IFLOW_API_KEY export** - Uses environment variable
2. ✅ **Added reference documents** - Agent knows where to find files
3. ✅ **Added working directory** - Agent knows current path
4. ✅ **MCP tools enabled** - Port 8051 is exported

## File Ready to Test

### test_first_task.sh

The test script now has:
- WORKING DIRECTORY: $PROJECT_DIR
- REFERENCE DOCUMENTS listing:
  * wdt.md (hardware spec)
  * openspec/changes/implement-watchdog load/proposal.md
  * openspec/changes/implement-watchdog load/tasks.md
- Three-deliverable structure
- MCP_PORT=8051 exported

## Run the Test

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
bash test_first_task.sh
```

## Expected Results

Agent should:
1. Read wdt.md for register specs
2. Read change proposal  
3. Edit modules/demo_watchdog/demo_watchdog.dml
4. Create test file
5. Compile code
6. Respond with "IMPLEMENTATION COMPLETE"

No more:
- ❌ "Simics MCP tools not available"
- ❌ "I need more information"
- ❌ Endless exploration without action
