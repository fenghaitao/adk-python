#!/bin/bash

# Phased Spec-Kit Runner Script - Saves session for each phase
# Usage: ./run_spec_kit_phased.sh [PROJECT_NAME] [INITIAL_PROMPT] [--model MODEL] [--port PORT] [--skip-plan] [--skip-tasks] [--skip-implement] [--resume PHASE]
# Example: ./run_spec_kit_phased.sh myproject "Create a REST API for user management"
# Example: ./run_spec_kit_phased.sh myproject "Create a REST API" --model iflow/qwen3-coder-plus --skip-plan --skip-tasks
# Example: ./run_spec_kit_phased.sh myproject --resume plan --port 8052
# If no project name is provided, defaults to 'adk_spec_kit_project'
# If no prompt is provided, starts interactive mode for each phase
# 
# Options:
#   --model MODEL    Choose chat model: iflow/qwen3-coder-plus, iflow/qwen3-coder, github_copilot/claude-sonnet-4, github_copilot/claude-sonnet-4.5, github_copilot/grok-code-fast-1
#   --port PORT      MCP server port (default: 8051)
#   --resume PHASE   Resume from a specific phase: plan, tasks, implement (requires existing session files)
#   --skip-plan      Skip the planning phase
#   --skip-tasks     Skip the task breakdown phase  
#   --skip-implement Skip the implementation phase
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

# Function to display help
show_help() {
    cat << 'EOF'
Phased Spec-Kit Runner Script - ADK Development Kit

USAGE:
    ./run_spec_kit_phased.sh [PROJECT_NAME] [INITIAL_PROMPT] [OPTIONS]

DESCRIPTION:
    Runs the Spec-Kit integration in phases, saving session files for each phase.
    Each phase builds upon the previous phase's output.

POSITIONAL ARGUMENTS:
    PROJECT_NAME      Name of the project (default: 'adk_spec_kit_project')
    INITIAL_PROMPT    Initial prompt for the specification phase (optional)

OPTIONS:
    --model MODEL     Choose chat model (default: iflow/qwen3-coder-plus)
                      Available models:
                      - iflow/qwen3-coder-plus
                      - iflow/qwen3-coder
                      - github_copilot/claude-sonnet-4
                      - github_copilot/claude-sonnet-4.5
                      - github_copilot/grok-code-fast-1
    --port PORT       MCP server port (default: 8051)
                      Useful for WSL2 when default port has issues
    --resume PHASE    Resume from a specific phase (plan, tasks, implement)
                      Requires existing session files from previous runs
                      Note: Will run the specified phase and all subsequent phases
    --skip-plan       Skip the planning phase (Phase 2)
                      Note: Also skips TASKS and IMPLEMENT (cascade effect)
    --skip-tasks      Skip the task breakdown phase (Phase 3)  
                      Note: Also skips IMPLEMENT (cascade effect)
    --skip-implement  Skip the implementation phase (Phase 4)
    --help, -h        Show this help message and exit

PHASES:
    1. SPECIFY     - Always runs, creates project specification
    2. PLAN        - Creates implementation plan (skippable)
    3. TASKS       - Generates task breakdown (skippable, depends on PLAN)
    4. IMPLEMENT   - Executes implementation (skippable, depends on TASKS)

PHASE DEPENDENCIES:
    Each phase builds upon the previous phase's output:
    - TASKS phase requires PLAN phase output
    - IMPLEMENT phase requires TASKS phase output
    - Skipping a phase automatically skips all dependent phases

OUTPUT FILES:
    Each phase saves both JSON session files and human-readable dumps:
    - adk_specify_agent/PROJECT_NAME_specify.session.json|.txt
    - adk_plan_agent/PROJECT_NAME_plan.session.json|.txt
    - adk_tasks_agent/PROJECT_NAME_tasks.session.json|.txt
    - adk_implement_agent/PROJECT_NAME_implement.session.json|.txt

EXAMPLES:
    # Run all phases with default project name and model
    ./run_spec_kit_phased.sh

    # Run all phases with custom project and prompt
    ./run_spec_kit_phased.sh myapi "Create a user management REST API"

    # Use specific model
    ./run_spec_kit_phased.sh myapi "Create REST API" --model iflow/qwen3-coder

    # Use custom port (useful for WSL2)
    ./run_spec_kit_phased.sh myapi "Create REST API" --port 8052

    # Use Claude model and skip planning phases
    ./run_spec_kit_phased.sh myapi "Create REST API" --model github_copilot/claude-sonnet-4.5 --skip-plan --skip-tasks

    # Use Grok model with custom port
    ./run_spec_kit_phased.sh myapi "Create REST API" --model github_copilot/grok-code-fast-1 --port 8052

    # Only run specification phase with specific model
    ./run_spec_kit_phased.sh myapi "Create REST API" --model iflow/qwen3-coder-plus --skip-plan --skip-tasks --skip-implement

    # Resume from plan phase (runs plan, tasks, implement)
    ./run_spec_kit_phased.sh myapi --resume plan

    # Resume from tasks phase with specific model (runs tasks, implement)
    ./run_spec_kit_phased.sh myapi --resume tasks --model github_copilot/claude-sonnet-4

    # Resume from implement phase only
    ./run_spec_kit_phased.sh myapi --resume implement

    # Show help
    ./run_spec_kit_phased.sh --help

REQUIREMENTS:
    - ADK virtual environment must be activated or available
    - MCP servers must be configured and available
    - Spec-Kit integration components must be installed

EOF
}

# Check for help flag first, before any other processing
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        show_help
        exit 0
    fi
done

# Function to check if MCP server is running
check_mcp_server() {
    local port="${1:-8051}"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Server is running
    else
        return 1  # Server is not running
    fi
}

# Track whether MCP servers were started
MCP_SERVERS_STARTED=false

# Function to cleanup on script exit
cleanup() {
    if [ "$MCP_SERVERS_STARTED" = true ]; then
        echo ""
        echo -e "${YELLOW}🛑 Cleaning up MCP servers...${NC}"
        "$SPEC_KIT_INTEGRATION_DIR/simics-mcp-server/stop_mcp_servers.sh"
    fi
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

# Parse command line arguments
PROJECT_NAME=""
INITIAL_PROMPT=""
MODEL=""
MCP_PORT=""
RESUME_PHASE=""
SKIP_PLAN=false
SKIP_TASKS=false
SKIP_IMPLEMENT=false

# Process all arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --model)
            if [ -z "$2" ]; then
                echo "Error: --model requires a value"
                echo "Available models: iflow/qwen3-coder-plus, iflow/qwen3-coder, github_copilot/claude-sonnet-4, github_copilot/claude-sonnet-4.5, github_copilot/grok-code-fast-1"
                exit 1
            fi
            MODEL="$2"
            shift 2
            ;;
        --port)
            if [ -z "$2" ]; then
                echo "Error: --port requires a value"
                exit 1
            fi
            MCP_PORT="$2"
            shift 2
            ;;
        --resume)
            if [ -z "$2" ]; then
                echo "Error: --resume requires a phase value"
                echo "Available phases: plan, tasks, implement"
                exit 1
            fi
            RESUME_PHASE="$2"
            shift 2
            ;;
        --skip-plan)
            SKIP_PLAN=true
            shift
            ;;
        --skip-tasks)
            SKIP_TASKS=true
            shift
            ;;
        --skip-implement)
            SKIP_IMPLEMENT=true
            shift
            ;;
        *)
            if [ -z "$PROJECT_NAME" ]; then
                PROJECT_NAME="$1"
            elif [ -z "$INITIAL_PROMPT" ]; then
                INITIAL_PROMPT="$1"
            fi
            shift
            ;;
    esac
done

# Set defaults if not provided
PROJECT_NAME="${PROJECT_NAME:-adk_spec_kit_project}"
# Construct robust default prompt with absolute paths
DEFAULT_PROMPT="Read the Simics WDT specification from ${SCRIPT_DIR}/simics-wdt-spec.md and the hardware specifications from ${SCRIPT_DIR}/wdt.md to create a comprehensive Simics watchdog timer device implementation."
INITIAL_PROMPT="${INITIAL_PROMPT:-$DEFAULT_PROMPT}"

# Set default model and port
MODEL="${MODEL:-iflow/qwen3-coder-plus}"
MCP_PORT="${MCP_PORT:-8051}"

# Validate port number
if ! [[ "$MCP_PORT" =~ ^[0-9]+$ ]] || [ "$MCP_PORT" -lt 1024 ] || [ "$MCP_PORT" -gt 65535 ]; then
    echo "Error: Invalid port number '$MCP_PORT'. Must be between 1024 and 65535."
    exit 1
fi
VALID_MODELS=("iflow/qwen3-coder-plus" "iflow/qwen3-coder" "github_copilot/claude-sonnet-4" "github_copilot/claude-sonnet-4.5" "github_copilot/grok-code-fast-1")

# Validate model choice
if [[ ! " ${VALID_MODELS[@]} " =~ " ${MODEL} " ]]; then
    echo "Error: Invalid model '$MODEL'"
    echo "Available models: ${VALID_MODELS[@]}"
    exit 1
fi

# Export the model as environment variable for spec_kit integration
export SPEC_KIT_MODEL="$MODEL"

# Validate and handle resume phase
if [ -n "$RESUME_PHASE" ]; then
    VALID_RESUME_PHASES=("plan" "tasks" "implement")
    if [[ ! " ${VALID_RESUME_PHASES[@]} " =~ " ${RESUME_PHASE} " ]]; then
        echo "Error: Invalid resume phase '$RESUME_PHASE'"
        echo "Available phases: ${VALID_RESUME_PHASES[@]}"
        exit 1
    fi
    
    # Set skip flags based on resume phase
    case "$RESUME_PHASE" in
        "plan")
            SKIP_PLAN=false
            SKIP_TASKS=false
            SKIP_IMPLEMENT=false
            ;;
        "tasks")
            SKIP_PLAN=true
            SKIP_TASKS=false
            SKIP_IMPLEMENT=false
            ;;
        "implement")
            SKIP_PLAN=true
            SKIP_TASKS=true
            SKIP_IMPLEMENT=false
            ;;
    esac
    
    echo "🔄 Resume mode: Starting from $RESUME_PHASE phase"
fi

# Apply cascade logic for phase dependencies (only in normal mode, not resume mode)
if [ -z "$RESUME_PHASE" ]; then
    if [ "$SKIP_PLAN" = true ]; then
        echo "⚠️  PLAN phase skipped - cascading to skip TASKS and IMPLEMENT phases"
        SKIP_TASKS=true
        SKIP_IMPLEMENT=true
    elif [ "$SKIP_TASKS" = true ]; then
        echo "⚠️  TASKS phase skipped - cascading to skip IMPLEMENT phase"
        SKIP_IMPLEMENT=true
    fi
fi

echo "Project name: $PROJECT_NAME"
echo "Model: $MODEL"
echo "MCP Port: $MCP_PORT"
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Initial prompt: $INITIAL_PROMPT"
fi

# Start MCP servers after all argument validation is complete
echo ""
echo -e "${BLUE}🚀 Starting MCP servers on port $MCP_PORT...${NC}"
if "$SPEC_KIT_INTEGRATION_DIR/simics-mcp-server/start_mcp_servers.sh" "$MCP_PORT"; then
    echo -e "${GREEN}🎉 MCP servers started successfully!${NC}"
    
    # Quick verification
    if check_mcp_server "$MCP_PORT"; then
        echo -e "${GREEN}✅ MCP server confirmed running on port $MCP_PORT${NC}"
    else
        echo -e "${RED}❌ MCP server not responding on port $MCP_PORT${NC}"
        exit 1
    fi

    MCP_SERVERS_STARTED=true
else
    echo -e "${RED}❌ Failed to start MCP servers${NC}"
    echo -e "${RED}Script execution stopped. Please check MCP server configuration.${NC}"
    exit 1
fi

# Show phase configuration
echo ""
echo "Phase configuration:"
echo "  SPECIFY phase: ✅ Always runs"
if [ "$SKIP_PLAN" = true ]; then
    echo "  PLAN phase: ⏭️  SKIPPED"
else
    echo "  PLAN phase: ✅ Will run"
fi
if [ "$SKIP_TASKS" = true ]; then
    if [ "$SKIP_PLAN" = true ]; then
        echo "  TASKS phase: ⏭️  SKIPPED (cascaded from --skip-plan)"
    else
        echo "  TASKS phase: ⏭️  SKIPPED"
    fi
else
    echo "  TASKS phase: ✅ Will run"
fi
if [ "$SKIP_IMPLEMENT" = true ]; then
    if [ "$SKIP_PLAN" = true ]; then
        echo "  IMPLEMENT phase: ⏭️  SKIPPED (cascaded from --skip-plan)"
    elif [ "$SKIP_TASKS" = true ]; then
        echo "  IMPLEMENT phase: ⏭️  SKIPPED (cascaded from --skip-tasks)"
    else
        echo "  IMPLEMENT phase: ⏭️  SKIPPED"
    fi
else
    echo "  IMPLEMENT phase: ✅ Will run"
fi
echo ""

# Initialize spec-kit project or enter existing project
if [ -n "$RESUME_PHASE" ]; then
    # Resume mode - check if project directory exists
    if [ ! -d "$PROJECT_NAME" ]; then
        echo "Error: Project directory '$PROJECT_NAME' not found for resume"
        echo "Cannot resume without existing project directory"
        exit 1
    fi
    echo "🔄 Resume mode: Using existing project directory: $PROJECT_NAME"
else
    # Normal mode - initialize new project
    # Remove existing project directory if it exists
    if [ -d "$PROJECT_NAME" ]; then
        echo "Removing existing project directory: $PROJECT_NAME"
        rm -rf "$PROJECT_NAME"
    fi
    "$SPEC_KIT_DIR/.venv/bin/specify" init "$PROJECT_NAME" --ai adk --script sh
fi

echo ""
echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

if [ -z "$RESUME_PHASE" ]; then
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
else
    echo ""
    echo "==========================================="
    echo "PHASE 1: SPECIFY - ⏭️  SKIPPED (resume mode)"
    echo "==========================================="
    
    # Verify that required session files exist for resume
    if [ ! -f "adk_specify_agent/${PROJECT_NAME}_specify.session.json" ]; then
        echo "❌ Error: Required session file not found: adk_specify_agent/${PROJECT_NAME}_specify.session.json"
        echo "Cannot resume without existing specify session"
        exit 1
    fi
    echo "✅ Found existing specify session: adk_specify_agent/${PROJECT_NAME}_specify.session.json"
fi

if [ "$SKIP_PLAN" = false ]; then
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
else
    echo ""
    echo "==========================================="
    echo "PHASE 2: PLAN - ⏭️  SKIPPED"
    echo "==========================================="
fi

if [ "$SKIP_TASKS" = false ]; then
    echo ""
    echo "==========================================="
    echo "PHASE 3: TASKS - Generating task breakdown"
    echo "==========================================="
    
    # When resuming from tasks, verify required session files exist
    if [ "$RESUME_PHASE" = "tasks" ]; then
        if [ ! -f "adk_plan_agent/${PROJECT_NAME}_plan.session.json" ]; then
            echo "❌ Error: Required session file not found: adk_plan_agent/${PROJECT_NAME}_plan.session.json"
            echo "Cannot resume tasks phase without existing plan session"
            exit 1
        fi
        echo "✅ Found required plan session for tasks resume"
    fi

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
else
    echo ""
    echo "==========================================="
    echo "PHASE 3: TASKS - ⏭️  SKIPPED"
    echo "==========================================="
fi

if [ "$SKIP_IMPLEMENT" = false ]; then
    echo ""
    echo "==========================================="
    echo "PHASE 4: IMPLEMENT - Executing implementation"
    echo "==========================================="
    
    # When resuming from implement, verify required session files exist
    if [ "$RESUME_PHASE" = "implement" ]; then
        if [ ! -f "adk_tasks_agent/${PROJECT_NAME}_tasks.session.json" ]; then
            echo "❌ Error: Required session file not found: adk_tasks_agent/${PROJECT_NAME}_tasks.session.json"
            echo "Cannot resume implement phase without existing tasks session"
            exit 1
        fi
        echo "✅ Found required tasks session for implement resume"
    fi

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
else
    echo ""
    echo "==========================================="
    echo "PHASE 4: IMPLEMENT - ⏭️  SKIPPED"
    echo "==========================================="
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
echo "To resume from a specific phase using the --resume option:"
echo "  ./run_spec_kit_phased.sh ${PROJECT_NAME} --resume plan    # Resume from plan phase (runs plan → tasks → implement)"
echo "  ./run_spec_kit_phased.sh ${PROJECT_NAME} --resume tasks   # Resume from tasks phase (runs tasks → implement)"
echo "  ./run_spec_kit_phased.sh ${PROJECT_NAME} --resume implement # Resume from implement phase only"
echo ""
echo "To resume with a specific model:"
echo "  ./run_spec_kit_phased.sh ${PROJECT_NAME} --resume plan --model $MODEL"
echo ""
echo "To manually resume individual agent sessions (advanced):"
echo "  SPEC_KIT_MODEL=$MODEL $ADK_VENV/bin/adk run adk_specify_agent --resume ${PROJECT_NAME}_specify.session.json"
echo "  SPEC_KIT_MODEL=$MODEL $ADK_VENV/bin/adk run adk_plan_agent --resume ${PROJECT_NAME}_plan.session.json"
echo "  SPEC_KIT_MODEL=$MODEL $ADK_VENV/bin/adk run adk_tasks_agent --resume ${PROJECT_NAME}_tasks.session.json"
echo "  SPEC_KIT_MODEL=$MODEL $ADK_VENV/bin/adk run adk_implement_agent --resume ${PROJECT_NAME}_implement.session.json"