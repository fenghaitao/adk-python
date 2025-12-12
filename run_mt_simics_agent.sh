#!/bin/bash

# Simics Agent Runner Script with Session Support
# Usage: ./run_mt_simics_agent.sh PROJECT_NAME INITIAL_PROMPT
# Example: ./run_mt_simics_agent.sh wdt_test "Implement watchdog timer device"
#
# This script runs the Simics agent with session saving enabled.
# Session name format: PROJECT_NAME_simics_agent

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up ADK virtual environment path
ADK_VENV="$SCRIPT_DIR/.venv"

# Set up Simics agent path
SIMICS_AGENT="$SCRIPT_DIR/simics_agent"

# Set up MCP server paths
SPEC_KIT_INTEGRATION_DIR="$SCRIPT_DIR/contributing/samples/spec_kit_integration"
MCP_SERVER_SCRIPT="$SPEC_KIT_INTEGRATION_DIR/simics-mcp-server/start_mcp_servers.sh"
MCP_STOP_SCRIPT="$SPEC_KIT_INTEGRATION_DIR/simics-mcp-server/stop_mcp_servers.sh"
MCP_PORT="${MCP_PORT:-8051}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track whether MCP servers were started by this script
MCP_SERVERS_STARTED=false

# Function to check if MCP server is running
check_mcp_server() {
    local port="${1:-8051}"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Server is running
    else
        return 1  # Server is not running
    fi
}

# Function to cleanup on script exit
cleanup() {
    if [ "$MCP_SERVERS_STARTED" = true ]; then
        echo ""
        echo -e "${YELLOW}🛑 Cleaning up MCP servers...${NC}"
        if [ -f "$MCP_STOP_SCRIPT" ]; then
            "$MCP_STOP_SCRIPT"
        fi
    fi
}

# Set up trap to cleanup on script exit
trap cleanup EXIT

# Function to display help
show_help() {
    cat << 'EOF'
Simics Agent Runner Script with Session Support

USAGE:
    ./run_mt_simics_agent.sh PROJECT_NAME INITIAL_PROMPT

DESCRIPTION:
    Runs the ADK Simics agent with session saving enabled.
    Session files are saved with the project name included.

POSITIONAL ARGUMENTS:
    PROJECT_NAME      Name of the project (REQUIRED)
                      This will be included in the session name
                      Example: wdt_test, timer_device, uart_model
    
    INITIAL_PROMPT    Initial prompt for the agent (REQUIRED)
                      Can be a text string or a file path
                      If the value is a readable file, its contents will be used
                      Example: "Implement watchdog timer device"
                      Example: openspec-prompts/1.md

OPTIONS:
    --help, -h        Show this help message and exit

OUTPUT FILES:
    Session files are saved in the current directory:
    - PROJECT_NAME_simics_agent.session.json (raw session data)
    
    Session name format: PROJECT_NAME_simics_agent
    Example: wdt_test_simics_agent

EXAMPLES:
    # Run with project name and prompt string
    ./run_mt_simics_agent.sh wdt_test "Implement watchdog timer"

    # Run with project name and prompt from file
    ./run_mt_simics_agent.sh wdt_test openspec-prompts/1.md

    # Show help
    ./run_mt_simics_agent.sh --help

REQUIREMENTS:
    - ADK virtual environment at $SCRIPT_DIR/.venv
    - Simics agent at ./simics_agent

EOF
}

# Check for help flag first
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        show_help
        exit 0
    fi
done

# Check if ADK virtual environment exists
if [ ! -d "$ADK_VENV" ]; then
    echo -e "${RED}Error: ADK virtual environment not found at $ADK_VENV${NC}"
    echo "Please run 'python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if Simics agent exists
if [ ! -d "$SIMICS_AGENT" ]; then
    echo -e "${RED}Error: Simics agent not found at $SIMICS_AGENT${NC}"
    echo "Please ensure the simics_agent directory exists"
    exit 1
fi

# Parse command line arguments
PROJECT_NAME="$1"
INITIAL_PROMPT="$2"

# Validate required arguments
if [ -z "$PROJECT_NAME" ]; then
    echo -e "${RED}Error: PROJECT_NAME is required${NC}"
    echo ""
    show_help
    exit 1
fi

if [ -z "$INITIAL_PROMPT" ]; then
    echo -e "${RED}Error: INITIAL_PROMPT is required${NC}"
    echo ""
    show_help
    exit 1
fi

# If INITIAL_PROMPT is a file path, read its contents
if [ -f "$INITIAL_PROMPT" ]; then
    echo -e "${BLUE}Reading prompt from file: $INITIAL_PROMPT${NC}"
    INITIAL_PROMPT="$(cat "$INITIAL_PROMPT")"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to read prompt file${NC}"
        exit 1
    fi
fi

# Validate PROJECT_NAME format
if ! [[ "$PROJECT_NAME" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo -e "${RED}Error: Invalid project name '$PROJECT_NAME'. Only alphanumeric, underscore, and hyphen characters allowed.${NC}"
    exit 1
fi

# Create session name with project name
SESSION_NAME="${PROJECT_NAME}_simics_agent"

echo -e "${GREEN}=== Simics Agent Runner ===${NC}"
echo -e "${BLUE}Project Name: $PROJECT_NAME${NC}"
echo -e "${BLUE}Session Name: $SESSION_NAME${NC}"
echo -e "${BLUE}Initial Prompt: ${INITIAL_PROMPT:0:80}...${NC}"
echo ""

# Check if MCP server is running
echo -e "${BLUE}Checking MCP server status on port $MCP_PORT...${NC}"
if check_mcp_server "$MCP_PORT"; then
    echo -e "${GREEN}✅ MCP server is already running on port $MCP_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  MCP server not running on port $MCP_PORT${NC}"
    
    if [ -f "$MCP_SERVER_SCRIPT" ]; then
        echo -e "${BLUE}Starting MCP servers...${NC}"
        if "$MCP_SERVER_SCRIPT"; then
            MCP_SERVERS_STARTED=true
            echo -e "${GREEN}✅ MCP servers started successfully${NC}"
            # Give servers a moment to fully start
            sleep 2
        else
            echo -e "${RED}❌ Failed to start MCP servers${NC}"
            echo -e "${YELLOW}Continuing anyway - agent may not have full functionality${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  MCP server start script not found at: $MCP_SERVER_SCRIPT${NC}"
        echo -e "${YELLOW}Continuing anyway - agent may not have full functionality${NC}"
    fi
fi
echo ""

# Run the ADK command
echo -e "${GREEN}Running: $ADK_VENV/bin/adk run $SIMICS_AGENT --save_session --session_id $SESSION_NAME${NC}"
echo ""

$ADK_VENV/bin/adk run "$SIMICS_AGENT" --save_session --session_id "$SESSION_NAME" <<EOF
$INITIAL_PROMPT
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Agent completed successfully${NC}"
    echo -e "${BLUE}Session saved as: ${SESSION_NAME}.session.json${NC}"
else
    echo ""
    echo -e "${RED}❌ Agent failed${NC}"
    exit 1
fi
