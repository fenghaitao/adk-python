#!/bin/bash

# Phased Spec-Kit Runner Script - Saves session for each phase
# Usage: ./run_spec_kit_phased.sh [PROJECT_NAME] [INITIAL_PROMPT]
# Example: ./run_spec_kit_phased.sh myproject "Create a REST API for user management"
# If no project name is provided, defaults to 'adk_spec_kit_project'
# If no prompt is provided, starts interactive mode for each phase
# 
# This script runs each subagent individually and saves separate sessions:
# - PROJECT_NAME_specify.session.json
# - PROJECT_NAME_plan.session.json  
# - PROJECT_NAME_tasks.session.json
# - PROJECT_NAME_implement.session.json

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up paths relative to script location
SPEC_KIT_DIR="$SCRIPT_DIR/spec-kit"
ADK_VENV="$SCRIPT_DIR/.venv"
SPEC_KIT_INTEGRATION_DIR="$SCRIPT_DIR/contributing/samples/spec_kit_integration"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port 8051 is available
check_port_8051() {
    # Convert port 8051 to hex (8051 = 0x1F73)
    if grep -q ":1F73 " /proc/net/tcp 2>/dev/null; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for port 8051 to become available
wait_for_port_8051() {
    local max_attempts=10
    local wait_time=2
    local attempt=1
    
    echo -e "${BLUE}🔍 Waiting for MCP server to start on port 8051...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if check_port_8051; then
            echo -e "${GREEN}✅ MCP server is running on port 8051 (attempt $attempt/$max_attempts)${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Waiting for MCP server... (attempt $attempt/$max_attempts)${NC}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Timeout: MCP server failed to start on port 8051 after ${max_attempts} attempts${NC}"
    return 1
}

# Function to cleanup on script exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Cleaning up MCP servers...${NC}"
    "$SPEC_KIT_INTEGRATION_DIR/stop_mcp_servers.sh"
}

# Set up trap to cleanup on script exit
trap cleanup EXIT

# Check if spec-kit virtual environment exists
if [ ! -d "$SPEC_KIT_DIR/.venv" ]; then
    echo "Error: spec-kit virtual environment not found at $SPEC_KIT_DIR/.venv"
    echo "Please run 'cd $SPEC_KIT_DIR && python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if ADK virtual environment exists
if [ ! -d "$ADK_VENV" ]; then
    echo "Error: ADK virtual environment not found at $ADK_VENV"
    echo "Please run 'python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if spec-kit integration directory exists
if [ ! -d "$SPEC_KIT_INTEGRATION_DIR" ]; then
    echo "Error: Spec-Kit integration directory not found at $SPEC_KIT_INTEGRATION_DIR"
    exit 1
fi

echo "Running Phased Spec-Kit workflow..."
echo "Spec-Kit directory: $SPEC_KIT_DIR"
echo "ADK directory: $SCRIPT_DIR"
echo "Integration directory: $SPEC_KIT_INTEGRATION_DIR"
echo ""

# Add specific IP (simicsbot mcp server: sse) to no_proxy
SIMICSBOT_IP="10.40.133.41"
export no_proxy="${no_proxy},$SIMICSBOT_IP"
export NO_PROXY="${NO_PROXY},$SIMICSBOT_IP"

# Start MCP servers
echo -e "${BLUE}🚀 Starting MCP servers...${NC}"
"$SPEC_KIT_INTEGRATION_DIR/start_mcp_servers.sh"

# Wait for MCP server to be ready
echo ""
if wait_for_port_8051; then
    echo -e "${GREEN}🎉 MCP server is ready!${NC}"
else
    echo -e "${RED}❌ MCP server failed to start properly${NC}"
    echo -e "${RED}Script execution stopped. Please check MCP server configuration.${NC}"
    exit 1
fi
echo ""

# Get project name from first argument, default to 'adk_spec_kit_project' if not provided
PROJECT_NAME="${1:-adk_spec_kit_project}"
# Get initial prompt from second argument (optional)
INITIAL_PROMPT="$2"

echo "Project name: $PROJECT_NAME"
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Initial prompt: $INITIAL_PROMPT"
fi
echo ""

# Initialize spec-kit project
# Remove existing project directory if it exists
if [ -d "$PROJECT_NAME" ]; then
    echo "Removing existing project directory: $PROJECT_NAME"
    rm -rf "$PROJECT_NAME"
fi
"$SPEC_KIT_DIR/.venv/bin/specify" init "$PROJECT_NAME" --ai adk --script sh

echo ""
echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

echo ""
echo "==========================================="
echo "PHASE 1: SPECIFY - Creating specification"
echo "==========================================="

# Create specify agent directory
mkdir -p "adk_specify_agent"
cat > "adk_specify_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from specify_agent import specify_agent as root_agent
EOF

if [ -n "$INITIAL_PROMPT" ]; then
    echo "Running SpecifyAgent with feature description..."
    echo "Command: $INITIAL_PROMPT"
    echo "Session will be saved as: adk_specify_agent/${PROJECT_NAME}_specify.session.json"
    (echo "$INITIAL_PROMPT"; echo "exit") | "$ADK_VENV/bin/adk" run "adk_specify_agent" --save_session --session_id "${PROJECT_NAME}_specify"
else
    echo "Running SpecifyAgent in interactive mode..."
    echo "Session will be saved as: adk_specify_agent/${PROJECT_NAME}_specify.session.json"
    echo "Please provide the feature description for /specify command"
    "$ADK_VENV/bin/adk" run "adk_specify_agent" --save_session --session_id "${PROJECT_NAME}_specify"
fi

# Check if session file was created
if [ -f "adk_specify_agent/${PROJECT_NAME}_specify.session.json" ]; then
    echo "✅ Session saved: adk_specify_agent/${PROJECT_NAME}_specify.session.json"
    
    # Generate human-readable session dump
    echo "📄 Generating human-readable session dump..."
    python3 "$SCRIPT_DIR/view_session.py" "adk_specify_agent/${PROJECT_NAME}_specify.session.json" > "adk_specify_agent/${PROJECT_NAME}_specify.session.txt"
    if [ -f "adk_specify_agent/${PROJECT_NAME}_specify.session.txt" ]; then
        echo "✅ Human-readable session saved: adk_specify_agent/${PROJECT_NAME}_specify.session.txt"
    else
        echo "❌ Failed to generate human-readable session dump"
    fi
else
    echo "❌ Session file not found in adk_specify_agent/"
fi

echo ""
echo "==========================================="
echo "PHASE 2: PLAN - Creating implementation plan"
echo "==========================================="

# Create plan agent directory
mkdir -p "adk_plan_agent"
cat > "adk_plan_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from plan_agent import plan_agent as root_agent
EOF

echo "Running PlanAgent with /plan command..."
echo "Session will be saved as: adk_plan_agent/${PROJECT_NAME}_plan.session.json"
(echo "/plan"; echo "exit") | "$ADK_VENV/bin/adk" run "adk_plan_agent" --save_session --session_id "${PROJECT_NAME}_plan"

# Check if session file was created
if [ -f "adk_plan_agent/${PROJECT_NAME}_plan.session.json" ]; then
    echo "✅ Session saved: adk_plan_agent/${PROJECT_NAME}_plan.session.json"
    
    # Generate human-readable session dump
    echo "📄 Generating human-readable session dump..."
    python3 "$SCRIPT_DIR/view_session.py" "adk_plan_agent/${PROJECT_NAME}_plan.session.json" > "adk_plan_agent/${PROJECT_NAME}_plan.session.txt"
    if [ -f "adk_plan_agent/${PROJECT_NAME}_plan.session.txt" ]; then
        echo "✅ Human-readable session saved: adk_plan_agent/${PROJECT_NAME}_plan.session.txt"
    else
        echo "❌ Failed to generate human-readable session dump"
    fi
else
    echo "❌ Session file not found in adk_plan_agent/"
fi

echo ""
echo "==========================================="
echo "PHASE 3: TASKS - Generating task breakdown"
echo "==========================================="

# Create tasks agent directory
mkdir -p "adk_tasks_agent"
cat > "adk_tasks_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from tasks_agent import tasks_agent as root_agent
EOF

echo "Running TasksAgent with /tasks command..."
echo "Session will be saved as: adk_tasks_agent/${PROJECT_NAME}_tasks.session.json"
(echo "/tasks"; echo "exit") | "$ADK_VENV/bin/adk" run "adk_tasks_agent" --save_session --session_id "${PROJECT_NAME}_tasks"

# Check if session file was created
if [ -f "adk_tasks_agent/${PROJECT_NAME}_tasks.session.json" ]; then
    echo "✅ Session saved: adk_tasks_agent/${PROJECT_NAME}_tasks.session.json"
    
    # Generate human-readable session dump
    echo "📄 Generating human-readable session dump..."
    python3 "$SCRIPT_DIR/view_session.py" "adk_tasks_agent/${PROJECT_NAME}_tasks.session.json" > "adk_tasks_agent/${PROJECT_NAME}_tasks.session.txt"
    if [ -f "adk_tasks_agent/${PROJECT_NAME}_tasks.session.txt" ]; then
        echo "✅ Human-readable session saved: adk_tasks_agent/${PROJECT_NAME}_tasks.session.txt"
    else
        echo "❌ Failed to generate human-readable session dump"
    fi
else
    echo "❌ Session file not found in adk_tasks_agent/"
fi

echo ""
echo "==========================================="
echo "PHASE 4: IMPLEMENT - Executing implementation"
echo "==========================================="

# Create implement agent directory
mkdir -p "adk_implement_agent"
cat > "adk_implement_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from implement_agent import implement_agent as root_agent
EOF

echo "Running ImplementAgent with /implement command..."
echo "Session will be saved as: adk_implement_agent/${PROJECT_NAME}_implement.session.json"
(echo "/implement"; echo "exit") | "$ADK_VENV/bin/adk" run "adk_implement_agent" --save_session --session_id "${PROJECT_NAME}_implement"

# Check if session file was created
if [ -f "adk_implement_agent/${PROJECT_NAME}_implement.session.json" ]; then
    echo "✅ Session saved: adk_implement_agent/${PROJECT_NAME}_implement.session.json"
    
    # Generate human-readable session dump
    echo "📄 Generating human-readable session dump..."
    python3 "$SCRIPT_DIR/view_session.py" "adk_implement_agent/${PROJECT_NAME}_implement.session.json" > "adk_implement_agent/${PROJECT_NAME}_implement.session.txt"
    if [ -f "adk_implement_agent/${PROJECT_NAME}_implement.session.txt" ]; then
        echo "✅ Human-readable session saved: adk_implement_agent/${PROJECT_NAME}_implement.session.txt"
    else
        echo "❌ Failed to generate human-readable session dump"
    fi
else
    echo "❌ Session file not found in adk_implement_agent/"
fi

echo ""
echo "==========================================="
echo "WORKFLOW COMPLETE"
echo "==========================================="
echo "Checking for session files..."

SESSIONS_FOUND=0
READABLE_SESSIONS_FOUND=0
for phase in "specify" "plan" "tasks" "implement"; do
    SESSION_FILE="adk_${phase}_agent/${PROJECT_NAME}_${phase}.session.json"
    READABLE_FILE="adk_${phase}_agent/${PROJECT_NAME}_${phase}.session.txt"
    
    if [ -f "$SESSION_FILE" ]; then
        echo "✅ Found: $SESSION_FILE"
        ls -la "$SESSION_FILE"
        ((SESSIONS_FOUND++))
    else
        echo "❌ Missing: $SESSION_FILE"
    fi
    
    if [ -f "$READABLE_FILE" ]; then
        echo "✅ Found: $READABLE_FILE"
        ls -la "$READABLE_FILE"
        ((READABLE_SESSIONS_FOUND++))
    else
        echo "❌ Missing: $READABLE_FILE"
    fi
done

echo ""
echo "Summary: $SESSIONS_FOUND/4 session files created"
echo "Summary: $READABLE_SESSIONS_FOUND/4 human-readable session files created"
echo "Location: $(pwd)"
echo ""
echo "Agent directories created:"
echo "  adk_specify_agent/    - SpecifyAgent with session logs (.json + .txt)"
echo "  adk_plan_agent/       - PlanAgent with session logs (.json + .txt)"
echo "  adk_tasks_agent/      - TasksAgent with session logs (.json + .txt)"
echo "  adk_implement_agent/  - ImplementAgent with session logs (.json + .txt)"
echo ""
echo "Session files generated:"
echo "  *.session.json        - Raw JSON session data for resuming"
echo "  *.session.txt         - Human-readable session dumps for review"
echo ""
echo "To resume a specific phase:"
echo "  $ADK_VENV/bin/adk run adk_specify_agent --resume ${PROJECT_NAME}_specify.session.json"
echo "  $ADK_VENV/bin/adk run adk_plan_agent --resume ${PROJECT_NAME}_plan.session.json"
echo "  $ADK_VENV/bin/adk run adk_tasks_agent --resume ${PROJECT_NAME}_tasks.session.json"
echo "  $ADK_VENV/bin/adk run adk_implement_agent --resume ${PROJECT_NAME}_implement.session.json"