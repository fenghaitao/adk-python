#!/bin/bash
# Generated OpenSpec Orchestration Script with ADK Agent
# This script runs ADK agents for each task with:
# - ADK agent execution per task
# - Automatic archiving after completion
# - Git commits after each task

set -e

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

echo -e "${BLUE}🚀 Starting OpenSpec DDM Orchestration with ADK Agents${NC}"
echo "Model: $MODEL"
echo "Port: $PORT"
echo "Project: $PROJECT_DIR"
echo "ADK venv: $ADK_VENV"
echo ""

# Check ADK venv exists
if [ ! -d "$ADK_VENV" ]; then
    echo -e "${RED}❌ Error: ADK virtual environment not found at $ADK_VENV${NC}"
    exit 1
fi

# Check OpenSpec integration exists
if [ ! -d "$OPENSPEC_INTEGRATION_DIR" ]; then
    echo -e "${RED}❌ Error: OpenSpec integration not found at $OPENSPEC_INTEGRATION_DIR${NC}"
    exit 1
fi

# Create agent directory for ADK if it doesn't exist
mkdir -p adk_openspec_agent

# Function to create agent.py for ADK
create_adk_agent() {
    cat > adk_openspec_agent/agent.py << 'AGENT_EOF'
import sys
sys.path.insert(0, '/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples/openspec_integration')
sys.path.insert(0, '/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples')

# Import the root_agent from the openspec_integration package
import importlib.util
spec = importlib.util.spec_from_file_location(
    "openspec_agent_module",
    "/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples/openspec_integration/agent.py"
)
openspec_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openspec_agent_module)
root_agent = openspec_agent_module.root_agent
AGENT_EOF
}

# Function to archive change and commit to git
archive_and_commit() {
    local change_id=$1
    local task_title=$2
    
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


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-001: Implement Watchdog Load register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog load"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog load/proposal.md  
- Task Details: openspec/changes/implement-watchdog load/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Load register logic
TYPE: register_impl
CHANGE ID: implement-watchdog load
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog load/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Load register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog load/proposal.md
- Task Details: openspec/changes/implement-watchdog load/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-001...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-001_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-001 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog load" "Implement Watchdog Load register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-002: Create tests for Watchdog Load register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog load"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog load/proposal.md  
- Task Details: openspec/changes/implement-watchdog load/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Load register
TYPE: test_impl
CHANGE ID: implement-watchdog load
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog load/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Load register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog load/proposal.md
- Task Details: openspec/changes/implement-watchdog load/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-002...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-002_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-002 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog load" "Create tests for Watchdog Load register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-003: Implement Watchdog Value register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog value"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog value/proposal.md  
- Task Details: openspec/changes/implement-watchdog value/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Value register logic
TYPE: register_impl
CHANGE ID: implement-watchdog value
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog value/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Value register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog value/proposal.md
- Task Details: openspec/changes/implement-watchdog value/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-003...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-003_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-003 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog value" "Implement Watchdog Value register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-004: Create tests for Watchdog Value register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog value"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog value/proposal.md  
- Task Details: openspec/changes/implement-watchdog value/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Value register
TYPE: test_impl
CHANGE ID: implement-watchdog value
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog value/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Value register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog value/proposal.md
- Task Details: openspec/changes/implement-watchdog value/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-004...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-004_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-004 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog value" "Create tests for Watchdog Value register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-005: Implement Watchdog Control register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog control"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog control/proposal.md  
- Task Details: openspec/changes/implement-watchdog control/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Control register logic
TYPE: register_impl
CHANGE ID: implement-watchdog control
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog control/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Control register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog control/proposal.md
- Task Details: openspec/changes/implement-watchdog control/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-005...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-005_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-005 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog control" "Implement Watchdog Control register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-006: Create tests for Watchdog Control register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog control"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog control/proposal.md  
- Task Details: openspec/changes/implement-watchdog control/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Control register
TYPE: test_impl
CHANGE ID: implement-watchdog control
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog control/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Control register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog control/proposal.md
- Task Details: openspec/changes/implement-watchdog control/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-006...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-006_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-006 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog control" "Create tests for Watchdog Control register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-007: Implement Watchdog Interrupt Clear register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog interrupt clear"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog interrupt clear/proposal.md  
- Task Details: openspec/changes/implement-watchdog interrupt clear/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Interrupt Clear register logic
TYPE: register_impl
CHANGE ID: implement-watchdog interrupt clear
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog interrupt clear/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Interrupt Clear register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog interrupt clear/proposal.md
- Task Details: openspec/changes/implement-watchdog interrupt clear/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-007...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-007_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-007 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog interrupt clear" "Implement Watchdog Interrupt Clear register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-008: Create tests for Watchdog Interrupt Clear register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog interrupt clear"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog interrupt clear/proposal.md  
- Task Details: openspec/changes/implement-watchdog interrupt clear/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Interrupt Clear register
TYPE: test_impl
CHANGE ID: implement-watchdog interrupt clear
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog interrupt clear/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Interrupt Clear register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog interrupt clear/proposal.md
- Task Details: openspec/changes/implement-watchdog interrupt clear/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-008...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-008_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-008 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog interrupt clear" "Create tests for Watchdog Interrupt Clear register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-009: Implement Watchdog Raw Interrupt Status register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog raw interrupt status"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog raw interrupt status/proposal.md  
- Task Details: openspec/changes/implement-watchdog raw interrupt status/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Raw Interrupt Status register logic
TYPE: register_impl
CHANGE ID: implement-watchdog raw interrupt status
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog raw interrupt status/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Raw Interrupt Status register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog raw interrupt status/proposal.md
- Task Details: openspec/changes/implement-watchdog raw interrupt status/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-009...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-009_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-009 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog raw interrupt status" "Implement Watchdog Raw Interrupt Status register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-010: Create tests for Watchdog Raw Interrupt Status register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog raw interrupt status"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog raw interrupt status/proposal.md  
- Task Details: openspec/changes/implement-watchdog raw interrupt status/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Raw Interrupt Status register
TYPE: test_impl
CHANGE ID: implement-watchdog raw interrupt status
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog raw interrupt status/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Raw Interrupt Status register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog raw interrupt status/proposal.md
- Task Details: openspec/changes/implement-watchdog raw interrupt status/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-010...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-010_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-010 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog raw interrupt status" "Create tests for Watchdog Raw Interrupt Status register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-011: Implement Watchdog Interrupt Status register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog interrupt status"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog interrupt status/proposal.md  
- Task Details: openspec/changes/implement-watchdog interrupt status/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Interrupt Status register logic
TYPE: register_impl
CHANGE ID: implement-watchdog interrupt status
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog interrupt status/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Interrupt Status register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog interrupt status/proposal.md
- Task Details: openspec/changes/implement-watchdog interrupt status/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-011...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-011_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-011 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog interrupt status" "Implement Watchdog Interrupt Status register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-012: Create tests for Watchdog Interrupt Status register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog interrupt status"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog interrupt status/proposal.md  
- Task Details: openspec/changes/implement-watchdog interrupt status/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Interrupt Status register
TYPE: test_impl
CHANGE ID: implement-watchdog interrupt status
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog interrupt status/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Interrupt Status register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog interrupt status/proposal.md
- Task Details: openspec/changes/implement-watchdog interrupt status/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-012...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-012_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-012 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog interrupt status" "Create tests for Watchdog Interrupt Status register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-013: Implement Watchdog Lock register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog lock"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog lock/proposal.md  
- Task Details: openspec/changes/implement-watchdog lock/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Lock register logic
TYPE: register_impl
CHANGE ID: implement-watchdog lock
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog lock/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Lock register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog lock/proposal.md
- Task Details: openspec/changes/implement-watchdog lock/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-013...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-013_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-013 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog lock" "Implement Watchdog Lock register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-014: Create tests for Watchdog Lock register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog lock"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog lock/proposal.md  
- Task Details: openspec/changes/implement-watchdog lock/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Lock register
TYPE: test_impl
CHANGE ID: implement-watchdog lock
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog lock/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Lock register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog lock/proposal.md
- Task Details: openspec/changes/implement-watchdog lock/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-014...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-014_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-014 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog lock" "Create tests for Watchdog Lock register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-015: Implement Watchdog Integration Test Control register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog integration test control"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog integration test control/proposal.md  
- Task Details: openspec/changes/implement-watchdog integration test control/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Integration Test Control register logic
TYPE: register_impl
CHANGE ID: implement-watchdog integration test control
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog integration test control/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Integration Test Control register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog integration test control/proposal.md
- Task Details: openspec/changes/implement-watchdog integration test control/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-015...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-015_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-015 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog integration test control" "Implement Watchdog Integration Test Control register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-016: Create tests for Watchdog Integration Test Control register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog integration test control"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog integration test control/proposal.md  
- Task Details: openspec/changes/implement-watchdog integration test control/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Integration Test Control register
TYPE: test_impl
CHANGE ID: implement-watchdog integration test control
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog integration test control/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Integration Test Control register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog integration test control/proposal.md
- Task Details: openspec/changes/implement-watchdog integration test control/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-016...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-016_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-016 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog integration test control" "Create tests for Watchdog Integration Test Control register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-017: Implement Watchdog Integration Test Output Set register logic${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog integration test output set"
echo "Type: register_impl"
echo "Priority: 1"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog integration test output set/proposal.md  
- Task Details: openspec/changes/implement-watchdog integration test output set/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Implement Watchdog Integration Test Output Set register logic
TYPE: register_impl
CHANGE ID: implement-watchdog integration test output set
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog integration test output set/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Implement Watchdog Integration Test Output Set register logic

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog integration test output set/proposal.md
- Task Details: openspec/changes/implement-watchdog integration test output set/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-017...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-017_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-017 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog integration test output set" "Implement Watchdog Integration Test Output Set register logic"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 Task task-018: Create tests for Watchdog Integration Test Output Set register${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "Change ID: implement-watchdog integration test output set"
echo "Type: test_impl"
echo "Priority: 2"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Change Proposal: openspec/changes/implement-watchdog integration test output set/proposal.md  
- Task Details: openspec/changes/implement-watchdog integration test output set/tasks.md
- DML File: modules/demo_watchdog/demo_watchdog.dml

═══════════════════════════════════════════════════════════
TASK: Create tests for Watchdog Integration Test Output Set register
TYPE: test_impl
CHANGE ID: implement-watchdog integration test output set
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/implement-watchdog integration test output set/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: modules/demo_watchdog/demo_watchdog.dml
WHERE: In the bank section where registers are defined  
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: \">>> REGNAME write_register() CALLED with value=0x%x\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \">>> REGNAME updated, value=0x%x\", this.val;
    }

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: \">>> REGNAME read_register() CALLED\";
        return this.val;
    }

✓ DELIVERABLE 1 COMPLETE WHEN: modules/demo_watchdog/demo_watchdog.dml contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\"✓ Test PASSED\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\"\\n✓✓✓ ALL TESTS PASSED ✓✓✓\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - Create tests for Watchdog Integration Test Output Set register

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading modules/demo_watchdog/demo_watchdog.dml to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- DML Implementation: modules/demo_watchdog/demo_watchdog.dml  
- Change Proposal: openspec/changes/implement-watchdog integration test output set/proposal.md
- Task Details: openspec/changes/implement-watchdog integration test output set/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${YELLOW}🤖 Running ADK agent for task task-018...${NC}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_task-018_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${GREEN}✅ Task task-018 completed${NC}"
echo ""

# Archive and commit
archive_and_commit "implement-watchdog integration test output set" "Create tests for Watchdog Integration Test Output Set register"


echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 All 19 tasks completed!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "1. Review the Git commit history: git log --oneline"
echo "2. Check the DML implementation: modules/demo_watchdog/demo_watchdog.dml"
echo "3. Build and test the module: make -C modules/demo_watchdog"
echo "4. Run integration tests if available"
echo ""
