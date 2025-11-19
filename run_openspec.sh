#!/bin/bash

# OpenSpec Runner Script with Session Support
# Usage: ./run_openspec.sh [PROJECT_NAME] [INITIAL_PROMPT] [OPTIONS]
# Example: ./run_openspec.sh myproject "Create a REST API for user management"
# Example: ./run_openspec.sh myproject --model iflow/qwen3-coder-plus --save-session
# Example: ./run_openspec.sh myproject --resume --port 8052
# If no project name is provided, defaults to 'adk_openspec_project'
# If no prompt is provided, starts interactive mode
#
# Options:
#   --model MODEL       Choose chat model (default: iflow/qwen3-coder-plus)
#   --port PORT         MCP server port (default: 8051)
#   --save-session      Save session to PROJECT_NAME_openspec.session.json
#   --resume            Resume from existing session file
#   --help, -h          Show help message
#
# This script initializes an OpenSpec project and runs the ADK agent with
# OpenSpec integration. It supports both TypeScript CLI (openspec) and
# Python port for initialization.
#
# Session files are saved in: adk_openspec_agent/PROJECT_NAME_openspec.session.json
# Human-readable dumps: adk_openspec_agent/PROJECT_NAME_openspec.session.txt

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up paths relative to script location
ADK_VENV="$SCRIPT_DIR/.venv"
OPENSPEC_INTEGRATION_DIR="$SCRIPT_DIR/contributing/samples/openspec_integration"
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
OpenSpec Runner Script with Session Support

USAGE:
    ./run_openspec.sh [PROJECT_NAME] [INITIAL_PROMPT] [OPTIONS]

DESCRIPTION:
    Initializes an OpenSpec project and runs the ADK agent with OpenSpec
    integration. Supports session saving and resuming for continuous work.

POSITIONAL ARGUMENTS:
    PROJECT_NAME      Name of the project (default: 'adk_openspec_project')
    INITIAL_PROMPT    Initial prompt for the agent (optional)
                      Default: "Please read this project first, then read openspec/project.md
                      and help me fill it out with details about my project, tech stack,
                      and conventions"

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
    --save-session    Save session to PROJECT_NAME_openspec.session.json
                      Allows resuming work later with --resume
    --resume          Resume from existing session file
                      Requires PROJECT_NAME_openspec.session.json to exist
    --interactive     Skip default prompt and start in pure interactive mode
    --force-python    Force use of Python port instead of TypeScript CLI
    --help, -h        Show this help message and exit

OUTPUT FILES:
    When --save-session is used:
    - adk_openspec_agent/PROJECT_NAME_openspec.session.json (raw session data)
    - adk_openspec_agent/PROJECT_NAME_openspec.session.txt (human-readable dump)

EXAMPLES:
    # Basic usage with default project name (uses default prompt)
    ./run_openspec.sh

    # Pure interactive mode without default prompt
    ./run_openspec.sh myapi --interactive

    # Create project with custom prompt
    ./run_openspec.sh myapi "Create a user authentication feature"

    # Save session for later resuming
    ./run_openspec.sh myapi "Create REST API" --save-session

    # Interactive mode with session saving
    ./run_openspec.sh myapi --interactive --save-session

    # Use specific model and save session
    ./run_openspec.sh myapi --model iflow/qwen3-coder-plus --save-session

    # Use custom port (useful for WSL2)
    ./run_openspec.sh myapi --port 8052

    # Resume from saved session
    ./run_openspec.sh myapi --resume

    # Resume with different model and custom port
    ./run_openspec.sh myapi --resume --model github_copilot/claude-sonnet-4 --port 8052

    # Show help
    ./run_openspec.sh --help

REQUIREMENTS:
    - OpenSpec CLI (TypeScript) or uvx (Python port)
    - ADK virtual environment
    - Python 3.11+

EOF
}

# Check for help flag first
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        show_help
        exit 0
    fi
done

# Function to check if OpenSpec CLI is available
check_openspec_cli() {
    # Check if we have the Python port available locally
    if [ -f "$SCRIPT_DIR/OpenSpec/python_port/.venv/bin/openspec" ]; then
        PYTHON_AVAILABLE=true
    else
        PYTHON_AVAILABLE=false
    fi
    
    # If force-python flag is set, only check for Python version
    if [ "$FORCE_PYTHON" = true ]; then
        if [ "$PYTHON_AVAILABLE" = true ]; then
            echo "Python"
            return 0
        else
            return 1
        fi
    fi
    
    # Default behavior - prefer TypeScript (via npm), then fallback to Python port
    if command -v openspec &> /dev/null; then
        echo "TypeScript"
        return 0
    elif [ "$PYTHON_AVAILABLE" = true ]; then
        echo "Python"
        return 0
    else
        return 1
    fi
}

# Check if ADK virtual environment exists
if [ ! -d "$ADK_VENV" ]; then
    echo -e "${RED}Error: ADK virtual environment not found at $ADK_VENV${NC}"
    echo "Please run 'python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if openspec_integration directory exists
if [ ! -d "$OPENSPEC_INTEGRATION_DIR" ]; then
    echo -e "${RED}Error: OpenSpec integration directory not found at $OPENSPEC_INTEGRATION_DIR${NC}"
    exit 1
fi

echo "Running OpenSpec initialization..."
echo "ADK directory: $SCRIPT_DIR"
echo "Integration directory: $OPENSPEC_INTEGRATION_DIR"
echo ""

# Parse command line arguments
PROJECT_NAME=""
INITIAL_PROMPT=""
MODEL=""
MCP_PORT=""
SAVE_SESSION=false
RESUME_SESSION=false
NO_PROMPT=false
FORCE_PYTHON=false

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
                echo "Available models: iflow/qwen3-coder-plus, iflow/qwen3-coder, github_copilot/claude-sonnet-4, etc."
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
        --save-session)
            SAVE_SESSION=true
            shift
            ;;
        --resume)
            RESUME_SESSION=true
            shift
            ;;
        --interactive)
            NO_PROMPT=true
            shift
            ;;
        --force-python)
            FORCE_PYTHON=true
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

# Set defaults
PROJECT_NAME="${PROJECT_NAME:-adk_openspec_project}"
MODEL="${MODEL:-iflow/qwen3-coder-plus}"
MCP_PORT="${MCP_PORT:-8051}"

# Validate port number
if ! [[ "$MCP_PORT" =~ ^[0-9]+$ ]] || [ "$MCP_PORT" -lt 1024 ] || [ "$MCP_PORT" -gt 65535 ]; then
    echo "Error: Invalid port number '$MCP_PORT'. Must be between 1024 and 65535."
    exit 1
fi

# Set default prompt if not provided and not in resume mode and not explicitly skipped
if [ -z "$INITIAL_PROMPT" ] && [ "$RESUME_SESSION" = false ] && [ "$NO_PROMPT" = false ]; then
    INITIAL_PROMPT="Please read this project first, then read openspec/project.md and help me fill it out with details about my project, tech stack, and conventions"
fi

# Export model and port as environment variables
export OPENSPEC_MODEL="$MODEL"
export MCP_PORT="$MCP_PORT"

echo "Project name: $PROJECT_NAME"
echo "Model: $MODEL"
echo "MCP Port: $MCP_PORT"
if [ "$SAVE_SESSION" = true ]; then
    echo "Session saving: ENABLED"
fi
if [ "$RESUME_SESSION" = true ]; then
    echo "Resume mode: ENABLED"
fi
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Initial prompt: $INITIAL_PROMPT"
fi
echo ""

# Check for OpenSpec CLI
echo -e "${BLUE}🔍 Checking for OpenSpec CLI...${NC}"
OPENSPEC_TYPE=$(check_openspec_cli)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ OpenSpec CLI not found${NC}"
    echo ""
    echo "Please install OpenSpec using one of these methods:"
    echo ""
    echo "Option 1: TypeScript CLI (requires Node.js >= 20.19.0)"
    echo "  npm install -g @fission-ai/openspec@latest"
    echo ""
    echo "Option 2: Python port (requires uv)"
    echo "  # Install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    echo "  # Then OpenSpec will be available via: openspec"
    echo ""
    exit 1
fi

if [ "$OPENSPEC_TYPE" = "TypeScript" ]; then
    echo -e "${GREEN}✅ Using OpenSpec TypeScript (npm)${NC}"
    OPENSPEC_CMD="openspec"
else
    echo -e "${GREEN}✅ Using OpenSpec Python port${NC}"
    OPENSPEC_CMD="$SCRIPT_DIR/OpenSpec/python_port/.venv/bin/openspec"
fi
echo ""

# Initialize OpenSpec project or enter existing project
if [ "$RESUME_SESSION" = true ]; then
    # Resume mode - check if project directory exists
    if [ ! -d "$PROJECT_NAME" ]; then
        echo -e "${RED}Error: Project directory '$PROJECT_NAME' not found for resume${NC}"
        echo "Cannot resume without existing project directory"
        exit 1
    fi
    echo -e "${BLUE}🔄 Resume mode: Using existing project directory: $PROJECT_NAME${NC}"
    
    # Check if session file exists
    if [ ! -f "$PROJECT_NAME/adk_openspec_agent/${PROJECT_NAME}_openspec.session.json" ]; then
        echo -e "${RED}Error: Session file not found: $PROJECT_NAME/adk_openspec_agent/${PROJECT_NAME}_openspec.session.json${NC}"
        echo "Cannot resume without existing session file"
        exit 1
    fi
    echo -e "${GREEN}✅ Found existing session file${NC}"
else
    # Normal mode - initialize new project
    # Remove existing project directory if it exists
    if [ -d "$PROJECT_NAME" ]; then
        echo -e "${YELLOW}⚠️  Removing existing project directory: $PROJECT_NAME${NC}"
        rm -rf "$PROJECT_NAME"
    fi

    echo -e "${BLUE}🚀 Initializing OpenSpec project...${NC}"
    $OPENSPEC_CMD init "$PROJECT_NAME" --tools none

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to initialize OpenSpec project${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ OpenSpec project initialized successfully${NC}"
fi

echo ""
echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

# Create agent directory for session management
mkdir -p "adk_openspec_agent"
cat > "adk_openspec_agent/agent.py" << EOF
import sys
import os

# Add parent directory to path for spec_kit_integration imports
sys.path.insert(0, os.path.dirname('$SPEC_KIT_INTEGRATION_DIR'))

# Import the OpenSpec agent directly
sys.path.insert(0, '$OPENSPEC_INTEGRATION_DIR')
from agent import root_agent
EOF

echo "Running ADK with OpenSpec integration..."
echo ""

# Build ADK command with session options
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"

if [ "$SAVE_SESSION" = true ]; then
    ADK_CMD="$ADK_CMD --save_session --session_id ${PROJECT_NAME}_openspec"
    echo "Session will be saved as: adk_openspec_agent/${PROJECT_NAME}_openspec.session.json"
fi

if [ "$RESUME_SESSION" = true ]; then
    ADK_CMD="$ADK_CMD --resume adk_openspec_agent/${PROJECT_NAME}_openspec.session.json"
    echo "Resuming from: adk_openspec_agent/${PROJECT_NAME}_openspec.session.json"
fi

echo ""

# Run ADK with openspec integration
if [ -n "$INITIAL_PROMPT" ] && [ "$RESUME_SESSION" = false ]; then
    echo "Starting with initial prompt..."
    echo "$INITIAL_PROMPT" | $ADK_CMD
else
    echo "Starting interactive mode..."
    $ADK_CMD
fi

# Generate human-readable session dump if session was saved
if [ "$SAVE_SESSION" = true ] && [ -f "adk_openspec_agent/${PROJECT_NAME}_openspec.session.json" ]; then
    echo ""
    echo -e "${GREEN}✅ Session saved: adk_openspec_agent/${PROJECT_NAME}_openspec.session.json${NC}"
    
    # Generate human-readable session dump
    if [ -f "$SCRIPT_DIR/view_session.py" ]; then
        echo "📄 Generating human-readable session dump..."
        python3 "$SCRIPT_DIR/view_session.py" "adk_openspec_agent/${PROJECT_NAME}_openspec.session.json" > "adk_openspec_agent/${PROJECT_NAME}_openspec.session.txt"
        if [ -f "adk_openspec_agent/${PROJECT_NAME}_openspec.session.txt" ]; then
            echo -e "${GREEN}✅ Human-readable session saved: adk_openspec_agent/${PROJECT_NAME}_openspec.session.txt${NC}"
        else
            echo -e "${YELLOW}⚠️  Failed to generate human-readable session dump${NC}"
        fi
    fi
    
    echo ""
    echo "To resume this session later:"
    echo "  ./run_openspec.sh $PROJECT_NAME --resume"
    echo ""
    echo "To resume with a different model:"
    echo "  ./run_openspec.sh $PROJECT_NAME --resume --model $MODEL"
fi
