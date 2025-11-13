#!/bin/bash

# Spec-Kit Runner Script
# Usage: ./run_spec_kit.sh [PROJECT_NAME] [INITIAL_PROMPT] [--port PORT]
# Example: ./run_spec_kit.sh myproject "Create a REST API for user management"
# Example: ./run_spec_kit.sh myproject "Create REST API" --port 8052
# If no project name is provided, defaults to 'adk_spec_kit_project'
# If no prompt is provided, starts interactive mode
# 
# Options:
#   --port PORT      MCP server port (default: 8051)
# 
# NOTE: This script does NOT save sessions because:
# - SequentialAgent does not support session saving (not an LlmAgent)
# - Session saving only works with LlmAgent instances
# 
# For session saving with individual subagents, use:
#   ./run_spec_kit_phased.sh
# 
# The phased script runs each subagent separately and saves individual sessions:
# - specify_agent/PROJECT_NAME_specify.session.json
# - plan_agent/PROJECT_NAME_plan.session.json  
# - tasks_agent/PROJECT_NAME_tasks.session.json
# - implement_agent/PROJECT_NAME_implement.session.json

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
    echo ""
    echo -e "${YELLOW}🛑 Cleaning up MCP servers...${NC}"
    "$SPEC_KIT_INTEGRATION_DIR/simics-mcp-server/stop_mcp_servers.sh"
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

echo "Running Spec-Kit initialization..."
echo "Spec-Kit directory: $SPEC_KIT_DIR"
echo "ADK directory: $SCRIPT_DIR"
echo "Integration directory: $SPEC_KIT_INTEGRATION_DIR"
echo ""

# Parse command line arguments
PROJECT_NAME=""
INITIAL_PROMPT=""
MCP_PORT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            if [ -z "$2" ]; then
                echo "Error: --port requires a value"
                exit 1
            fi
            MCP_PORT="$2"
            shift 2
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

# Set defaults
PROJECT_NAME="${PROJECT_NAME:-adk_spec_kit_project}"
MCP_PORT="${MCP_PORT:-8051}"

# Validate port number
if ! [[ "$MCP_PORT" =~ ^[0-9]+$ ]] || [ "$MCP_PORT" -lt 1024 ] || [ "$MCP_PORT" -gt 65535 ]; then
    echo "Error: Invalid port number '$MCP_PORT'. Must be between 1024 and 65535."
    exit 1
fi

# Export port as environment variable
export MCP_PORT="$MCP_PORT"

# Start MCP servers (start_mcp_servers.sh handles the waiting)
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
else
    echo -e "${RED}❌ Failed to start MCP servers${NC}"
    echo -e "${RED}Script execution stopped. Please check MCP server configuration.${NC}"
    exit 1
fi
echo ""

echo "Project name: $PROJECT_NAME"
echo "MCP Port: $MCP_PORT"
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

echo "Running ADK with Spec-Kit integration..."
echo "Note: This script uses the sequential multi-agent architecture"
echo "For session saving, use: ./run_spec_kit_phased.sh"

# Run ADK with spec-kit integration using sequential agent
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Starting with initial prompt..."
    echo "Using: sequential multi-agent workflow"
    echo "$INITIAL_PROMPT" | "$ADK_VENV/bin/adk" run "$SPEC_KIT_INTEGRATION_DIR"
else
    echo "Starting interactive mode..."
    echo "Using: sequential multi-agent workflow"
    "$ADK_VENV/bin/adk" run "$SPEC_KIT_INTEGRATION_DIR"
fi
