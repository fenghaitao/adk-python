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
"$SPEC_KIT_DIR/.venv/bin/specify" init "$PROJECT_NAME" --ai adk --script sh

echo ""
echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

echo ""
echo "==========================================="
echo "PHASE 1: SPECIFY - Creating specification"
echo "==========================================="

# Create specify agent directory
mkdir -p "specify_agent"
cat > "specify_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from specify_agent import specify_agent as root_agent
EOF

if [ -n "$INITIAL_PROMPT" ]; then
    echo "Running SpecifyAgent with feature description..."
    echo "Command: $INITIAL_PROMPT"
    echo "Session will be saved as: specify_agent/${PROJECT_NAME}_specify.session.json"
    (echo "$INITIAL_PROMPT"; echo "exit") | "$ADK_VENV/bin/adk" run "specify_agent" --save_session --session_id "${PROJECT_NAME}_specify"
else
    echo "Running SpecifyAgent in interactive mode..."
    echo "Session will be saved as: specify_agent/${PROJECT_NAME}_specify.session.json"
    echo "Please provide the feature description for /specify command"
    "$ADK_VENV/bin/adk" run "specify_agent" --save_session --session_id "${PROJECT_NAME}_specify"
fi

# Check if session file was created
if [ -f "specify_agent/${PROJECT_NAME}_specify.session.json" ]; then
    echo "✅ Session saved: specify_agent/${PROJECT_NAME}_specify.session.json"
else
    echo "❌ Session file not found in specify_agent/"
fi

echo ""
echo "==========================================="
echo "PHASE 2: PLAN - Creating implementation plan"
echo "==========================================="

# Create plan agent directory
mkdir -p "plan_agent"
cat > "plan_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from plan_agent import plan_agent as root_agent
EOF

echo "Running PlanAgent with /plan command..."
echo "Session will be saved as: plan_agent/${PROJECT_NAME}_plan.session.json"
(echo "/plan"; echo "exit") | "$ADK_VENV/bin/adk" run "plan_agent" --save_session --session_id "${PROJECT_NAME}_plan"

# Check if session file was created
if [ -f "plan_agent/${PROJECT_NAME}_plan.session.json" ]; then
    echo "✅ Session saved: plan_agent/${PROJECT_NAME}_plan.session.json"
else
    echo "❌ Session file not found in plan_agent/"
fi

echo ""
echo "==========================================="
echo "PHASE 3: TASKS - Generating task breakdown"
echo "==========================================="

# Create tasks agent directory
mkdir -p "tasks_agent"
cat > "tasks_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from tasks_agent import tasks_agent as root_agent
EOF

echo "Running TasksAgent with /tasks command..."
echo "Session will be saved as: tasks_agent/${PROJECT_NAME}_tasks.session.json"
(echo "/tasks"; echo "exit") | "$ADK_VENV/bin/adk" run "tasks_agent" --save_session --session_id "${PROJECT_NAME}_tasks"

# Check if session file was created
if [ -f "tasks_agent/${PROJECT_NAME}_tasks.session.json" ]; then
    echo "✅ Session saved: tasks_agent/${PROJECT_NAME}_tasks.session.json"
else
    echo "❌ Session file not found in tasks_agent/"
fi

echo ""
echo "==========================================="
echo "PHASE 4: IMPLEMENT - Executing implementation"
echo "==========================================="

# Create implement agent directory
mkdir -p "implement_agent"
cat > "implement_agent/agent.py" << EOF
import sys
import os
sys.path.insert(0, '$SPEC_KIT_INTEGRATION_DIR')
from implement_agent import implement_agent as root_agent
EOF

echo "Running ImplementAgent with /implement command..."
echo "Session will be saved as: implement_agent/${PROJECT_NAME}_implement.session.json"
(echo "/implement"; echo "exit") | "$ADK_VENV/bin/adk" run "implement_agent" --save_session --session_id "${PROJECT_NAME}_implement"

# Check if session file was created
if [ -f "implement_agent/${PROJECT_NAME}_implement.session.json" ]; then
    echo "✅ Session saved: implement_agent/${PROJECT_NAME}_implement.session.json"
else
    echo "❌ Session file not found in implement_agent/"
fi

echo ""
echo "==========================================="
echo "WORKFLOW COMPLETE"
echo "==========================================="
echo "Checking for session files..."

SESSIONS_FOUND=0
for phase in "specify" "plan" "tasks" "implement"; do
    SESSION_FILE="${phase}_agent/${PROJECT_NAME}_${phase}.session.json"
    if [ -f "$SESSION_FILE" ]; then
        echo "✅ Found: $SESSION_FILE"
        ls -la "$SESSION_FILE"
        ((SESSIONS_FOUND++))
    else
        echo "❌ Missing: $SESSION_FILE"
    fi
done

echo ""
echo "Summary: $SESSIONS_FOUND/4 session files created"
echo "Location: $(pwd)"
echo ""
echo "Agent directories created:"
echo "  specify_agent/    - SpecifyAgent with session logs"
echo "  plan_agent/       - PlanAgent with session logs"
echo "  tasks_agent/      - TasksAgent with session logs"
echo "  implement_agent/  - ImplementAgent with session logs"
echo ""
echo "To resume a specific phase:"
echo "  $ADK_VENV/bin/adk run specify_agent --resume ${PROJECT_NAME}_specify.session.json"
echo "  $ADK_VENV/bin/adk run plan_agent --resume ${PROJECT_NAME}_plan.session.json"
echo "  $ADK_VENV/bin/adk run tasks_agent --resume ${PROJECT_NAME}_tasks.session.json"
echo "  $ADK_VENV/bin/adk run implement_agent --resume ${PROJECT_NAME}_implement.session.json"