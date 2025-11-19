#!/bin/bash
# Test script for running the first task only
# This validates the ADK agent integration before running all tasks

set -e
export TMPDIR=~/wtemp2/
export IFLOW_API_KEY=sk-deb002993af4f7984e2eee3c4a86b894

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
MODEL="iflow/Qwen3-Coder"
PORT=8051
OPENSPEC_VENV="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv"
ADK_VENV="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/.venv"
PROJECT_DIR="/nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj"
OPENSPEC_INTEGRATION_DIR="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples/openspec_integration"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Testing ADK Agent with First Task (task-001)              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Model: $MODEL"
echo "Port: $PORT"
echo "Project: $PROJECT_DIR"
echo "ADK venv: $ADK_VENV"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if [ ! -d "$ADK_VENV" ]; then
    echo -e "${RED}❌ Error: ADK virtual environment not found at $ADK_VENV${NC}"
    exit 1
fi
echo -e "${GREEN}✅ ADK venv found${NC}"

if [ ! -d "$OPENSPEC_INTEGRATION_DIR" ]; then
    echo -e "${RED}❌ Error: OpenSpec integration not found at $OPENSPEC_INTEGRATION_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✅ OpenSpec integration found${NC}"

if [ ! -d "$OPENSPEC_VENV" ]; then
    echo -e "${RED}❌ Error: OpenSpec venv not found at $OPENSPEC_VENV${NC}"
    exit 1
fi
echo -e "${GREEN}✅ OpenSpec venv found${NC}"

# Check if change proposal exists
if [ ! -d "openspec/changes/implement-watchdog load" ]; then
    echo -e "${RED}❌ Error: Change proposal 'implement-watchdog load' not found${NC}"
    echo "Please run the orchestrator first to generate change proposals:"
    echo "  python3 run_openspec_from_ddm.py --project . --dml modules/demo_watchdog/demo_watchdog.dml --spec wdt.md"
    exit 1
fi
echo -e "${GREEN}✅ Change proposal exists${NC}"

echo ""

# Create agent directory for ADK if it doesn't exist
mkdir -p adk_openspec_agent

# Function to create agent.py for ADK
create_adk_agent() {
    cat > adk_openspec_agent/agent.py << 'AGENT_EOF'
import sys
sys.path.insert(0, '/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples')

# Import the root_agent from the openspec_integration package using proper package import
# This allows relative imports within openspec_integration to work correctly (e.g., MCP tools)
from openspec_integration.agent import root_agent
AGENT_EOF
}

# Function to archive change and commit to git
archive_and_commit() {
    local change_id=$1
    local task_title=$2
    
    echo ""
    echo -e "${YELLOW}📦 Archiving change: $change_id${NC}"
    
    # Activate OpenSpec venv for archive command
    source "$OPENSPEC_VENV/bin/activate"
    
    # Archive with openspec (this moves proposal to archive and updates specs)
    openspec archive "$change_id" --yes || true
    
    deactivate
    
    echo -e "${YELLOW}💾 Committing changes to Git${NC}"
    
    # Git commit all changes
    cd "$PROJECT_DIR"
    git add .
    git commit -m "✅ Completed: $task_title

Change ID: $change_id
Task completed and archived by OpenSpec orchestrator.
" || echo "No changes to commit"
    
    echo -e "${GREEN}✅ Change archived and committed${NC}"
    echo ""
}

# Export environment variables for ADK agent
export OPENSPEC_MODEL="$MODEL"
export MCP_PORT="$PORT"

# Create the ADK agent
echo -e "${BLUE}📝 Creating ADK agent for OpenSpec integration...${NC}"
create_adk_agent
echo -e "${GREEN}✅ ADK agent created${NC}"
echo ""

# Display agent.py content
echo -e "${BLUE}Agent configuration:${NC}"
cat adk_openspec_agent/agent.py
echo ""

# Task 001: Implement Watchdog Load register logic
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-001: Implement Watchdog Load register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog load"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Show the change proposal summary
echo -e "${YELLOW}Change Proposal Summary:${NC}"
if [ -f "openspec/changes/implement-watchdog load/proposal.md" ]; then
    head -30 "openspec/changes/implement-watchdog load/proposal.md"
    echo ""
fi

# Prepare the prompt for ADK agent
TASK_PROMPT="Implement WDOGLOAD register for change 'implement-watchdog load'.

═══════════════════════════════════════════════════════════
TASK: Implement WDOGLOAD register write_register() method
═══════════════════════════════════════════════════════════
Register: WDOGLOAD at address 0x00
Reset value: 0xFFFFFFFF
Access: Read/Write
Spec: openspec/specs/watchdog_timer/wdt.md

EXECUTE EXACTLY 3 STEPS - NO MORE, NO LESS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1/3: EDIT DML FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION: Edit modules/demo_watchdog/demo_watchdog.dml

Find 'register WDOGLOAD' and add THIS EXACT method (SIMPLE, no locks):

method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
    log info, 1: \"WDOGLOAD write: 0x%x\", value;
    default(value, enabled_bytes, aux);
}

Then IMMEDIATELY call:
- check_with_dmlc(project_path=\"$PROJECT_DIR\", module=\"demo_watchdog\")
- build_simics_project(project_path=\"$PROJECT_DIR\", module=\"demo_watchdog\")

CRITICAL: Use ABSOLUTE path $PROJECT_DIR, not relative paths!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 2/3: CREATE TEST FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION: Create modules/demo_watchdog/test/test_wdogload.py

FILENAME MUST BE: test_wdogload.py (NO SPACES, no 'test_watchdog load.py')

Content:
import simics

def test_wdogload_write():
    obj = simics.SIM_get_object('demo_watchdog')
    obj.iface.bank_instrumentation_subscribe.write(obj, 0x00, 0x12345678, 4)
    val = obj.iface.bank_instrumentation_subscribe.read(obj, 0x00, 4)
    assert val == 0x12345678
    print(\"✓ WDOGLOAD write test PASSED\")

def test_wdogload_reset():
    obj = simics.SIM_get_object('demo_watchdog')
    val = obj.iface.bank_instrumentation_subscribe.read(obj, 0x00, 4)
    assert val == 0xFFFFFFFF
    print(\"✓ WDOGLOAD reset test PASSED\")

if __name__ == '__main__':
    test_wdogload_reset()
    test_wdogload_write()
    print(\"ALL TESTS PASSED\")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 3/3: RUN TESTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACTION: Call run_simics_test with ABSOLUTE path:

run_simics_test(project_path=\"$PROJECT_DIR\", suite=\"modules/demo_watchdog/test\")

If tests PASS, respond: \"IMPLEMENTATION COMPLETE\" and type 'exit'
If tests FAIL, fix and retry ONCE, then exit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ ONLY edit WDOGLOAD register - ignore all other registers
✓ CALL MCP tools (check_with_dmlc, build_simics_project, run_simics_test)
✓ Use ABSOLUTE paths: $PROJECT_DIR
✓ Test filename: test_wdogload.py (NO SPACES)
✗ Do NOT add features not in spec (no locks, no extra logic)
✗ Do NOT create multiple test files
✗ Do NOT call perform_rag_query multiple times (1-2 max)
✗ Do NOT explore after completing 3 steps

MAXIMUM 3 ACTIONS: Edit DML → Create Test → Run Test → EXIT
START NOW!"

# Save prompt to file for reference
echo "$TASK_PROMPT" > /tmp/test_task_001_prompt.txt
echo -e "${BLUE}Prompt saved to: /tmp/test_task_001_prompt.txt${NC}"
echo ""

# Show the prompt
echo -e "${YELLOW}════════════════════════════════════════${NC}"
echo -e "${YELLOW}Task Prompt (first 500 chars):${NC}"
echo "$TASK_PROMPT" | head -c 500
echo "..."
echo ""
echo -e "${YELLOW}════════════════════════════════════════${NC}"
echo ""

# Ask user if they want to proceed (unless AUTO_YES is set)
if [[ -z "$AUTO_YES" ]]; then
    read -p "$(echo -e ${GREEN}Proceed with running ADK agent? [Y/n]: ${NC})" -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        echo -e "${YELLOW}Test cancelled. You can run manually with:${NC}"
        echo "  cd $PROJECT_DIR"
        echo "  echo \"\$TASK_PROMPT\" | $ADK_VENV/bin/adk run adk_openspec_agent --save_session --session_id task_task-001_openspec"
        exit 0
    fi
else
    echo -e "${GREEN}Auto-proceeding (AUTO_YES=1)${NC}"
fi

# Run the ADK agent for this task
echo ""
echo -e "${YELLOW}🤖 Running ADK agent for task task-001...${NC}"
echo -e "${BLUE}Command: echo \"\$TASK_PROMPT\" | adk run adk_openspec_agent --save_session --session_id task_task-001_openspec${NC}"
echo ""

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-001_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

# Check exit status
ADK_EXIT_CODE=$?

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $ADK_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Task task-001 completed successfully${NC}"
    echo ""
    
    # Ask if user wants to archive (unless AUTO_YES is set)
    if [[ -z "$AUTO_YES" ]]; then
        read -p "$(echo -e ${GREEN}Archive and commit the changes? [Y/n]: ${NC})" -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            archive_and_commit "implement-watchdog load" "Implement Watchdog Load register logic"
        else
            echo -e "${YELLOW}Skipped archiving. You can archive manually with:${NC}"
            echo "  source $OPENSPEC_VENV/bin/activate"
        echo "  openspec archive 'implement-watchdog load' --yes"
    fi
else
    echo -e "${RED}❌ Task task-001 failed with exit code: $ADK_EXIT_CODE${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test Complete${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Session file: adk_openspec_agent/task_task-001_openspec.session.json"
echo "Prompt file: /tmp/test_task_001_prompt.txt"
echo ""
echo "To check the session:"
echo "  cat adk_openspec_agent/task_task-001_openspec.session.json | jq"
echo ""
echo "To review changes:"
echo "  git diff"
echo "  git log -1"
echo ""
