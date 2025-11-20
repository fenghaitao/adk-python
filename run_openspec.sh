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
#   --ddm_xml FILE      Register definition XML file with absolute path
#   --spec FILE         Hardware specification file with absolute path
#   --device NAME       Simics model device name to generate from DDM XML and spec
#   --save-session      Save session to PROJECT_NAME_openspec.session.json (DEFAULT)
#   --no-save-session   Disable session saving
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
    --ddm_xml FILE    Register definition XML file (will be copied to project directory)
                      Specifies the DDM XML file for hardware register definitions
    --spec FILE       Hardware specification file (will be copied to project directory)
                      Specifies the hardware specification document
    --device NAME     Simics model device name to generate from DDM XML and spec
                      This will be the name of the DML device module to create
    --save-session    Save session to PROJECT_NAME_openspec.session.json (DEFAULT)
                      Allows resuming work later with --resume
    --no-save-session Disable session saving (sessions are saved by default)
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

    # With DDM XML and spec files
    ./run_openspec.sh myproject --ddm_xml /path/to/registers.xml --spec /path/to/spec.md

    # With DDM XML, spec files, and device name
    ./run_openspec.sh myproject --ddm_xml /path/to/registers.xml --spec /path/to/spec.md --device my_device

    # Create project (session saving is automatic by default)
    ./run_openspec.sh myapi "Create REST API"

    # Interactive mode (session saving is automatic)
    ./run_openspec.sh myapi --interactive

    # Disable session saving if needed
    ./run_openspec.sh myapi --no-save-session

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
DDM_XML=""
SPEC_FILE=""
DEVICE_NAME=""
SAVE_SESSION=true
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
        --ddm_xml)
            if [ -z "$2" ]; then
                echo "Error: --ddm_xml requires a file path"
                exit 1
            fi
            DDM_XML="$2"
            shift 2
            ;;
        --spec)
            if [ -z "$2" ]; then
                echo "Error: --spec requires a file path"
                exit 1
            fi
            SPEC_FILE="$2"
            shift 2
            ;;
        --device)
            if [ -z "$2" ]; then
                echo "Error: --device requires a device name"
                exit 1
            fi
            DEVICE_NAME="$2"
            shift 2
            ;;
        --save-session)
            SAVE_SESSION=true
            shift
            ;;
        --no-save-session)
            SAVE_SESSION=false
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

# Set default values for DDM XML, spec file, and device name (relative to script location)
DEFAULT_DDM_XML="$SCRIPT_DIR/wdt.xml"
DEFAULT_SPEC_FILE="$SCRIPT_DIR/wdt.md"
DEFAULT_DEVICE_NAME="wdt"

# Validate DEVICE_NAME if provided
if [ -n "$DEVICE_NAME" ] && ! [[ "$DEVICE_NAME" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo -e "${RED}Error: Invalid device name '$DEVICE_NAME'. Only alphanumeric, underscore, and hyphen characters allowed.${NC}"
    exit 1
fi

# Use defaults if not specified and files exist
if [ -z "$DDM_XML" ] && [ -f "$DEFAULT_DDM_XML" ]; then
    DDM_XML="$DEFAULT_DDM_XML"
    echo -e "${BLUE}Using default DDM XML: $DDM_XML${NC}"
fi

if [ -z "$SPEC_FILE" ] && [ -f "$DEFAULT_SPEC_FILE" ]; then
    SPEC_FILE="$DEFAULT_SPEC_FILE"
    echo -e "${BLUE}Using default spec file: $SPEC_FILE${NC}"
fi

if [ -z "$DEVICE_NAME" ]; then
    DEVICE_NAME="$DEFAULT_DEVICE_NAME"
    echo -e "${BLUE}Using default device name: $DEVICE_NAME${NC}"
fi

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

# Export DDM_XML and SPEC_FILE if provided
if [ -n "$DDM_XML" ]; then
    export DDM_XML="$DDM_XML"
fi
if [ -n "$SPEC_FILE" ]; then
    export SPEC_FILE="$SPEC_FILE"
fi
if [ -n "$DEVICE_NAME" ]; then
    export DEVICE_NAME="$DEVICE_NAME"
fi

echo "Project name: $PROJECT_NAME"
echo "Model: $MODEL"
echo "MCP Port: $MCP_PORT"
if [ -n "$DDM_XML" ]; then
    echo "DDM XML: $DDM_XML"
fi
if [ -n "$SPEC_FILE" ]; then
    echo "Spec File: $SPEC_FILE"
fi
if [ -n "$DEVICE_NAME" ]; then
    echo "Device Name: $DEVICE_NAME"
fi
if [ "$SAVE_SESSION" = true ]; then
    echo "Session saving: ENABLED"
fi
if [ "$RESUME_SESSION" = true ]; then
    echo "Resume mode: ENABLED"
fi
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
echo ""

# Check for OpenSpec CLI
echo -e "${BLUE}Checking for OpenSpec CLI...${NC}"
OPENSPEC_TYPE=$(check_openspec_cli)
if [ $? -ne 0 ]; then
    echo -e "${RED}OpenSpec CLI not found${NC}"
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
    echo -e "${GREEN}Using OpenSpec TypeScript (npm)${NC}"
    OPENSPEC_CMD="openspec"
else
    echo -e "${GREEN}Using OpenSpec Python port${NC}"
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
    echo -e "${BLUE}Resume mode: Using existing project directory: $PROJECT_NAME${NC}"
    
    # Check if session file exists
    if [ ! -f "$PROJECT_NAME/adk_openspec_agent/${PROJECT_NAME}_openspec.session.json" ]; then
        echo -e "${RED}Error: Session file not found: $PROJECT_NAME/adk_openspec_agent/${PROJECT_NAME}_openspec.session.json${NC}"
        echo "Cannot resume without existing session file"
        exit 1
    fi
    echo -e "${GREEN}Found existing session file${NC}"
else
    # Normal mode - initialize new project
    # Remove existing project directory if it exists
    if [ -d "$PROJECT_NAME" ]; then
        echo -e "${YELLOW}Removing existing project directory: $PROJECT_NAME${NC}"
        rm -rf "$PROJECT_NAME"
    fi

    echo -e "${BLUE}Initializing OpenSpec project...${NC}"
    $OPENSPEC_CMD init "$PROJECT_NAME" --tools none

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to initialize OpenSpec project${NC}"
        exit 1
    fi

    echo -e "${GREEN}OpenSpec project initialized successfully${NC}"
fi

echo ""
echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

# Handle DDM_XML and SPEC_FILE - copy to project if not already there

if [ -n "$DDM_XML" ]; then
    # Check if DDM_XML file exists
    if [ ! -f "$DDM_XML" ]; then
        echo -e "${RED}Error: DDM XML file not found: $DDM_XML${NC}"
        exit 1
    fi
    
    DDM_XML_BASENAME=$(basename "$DDM_XML")
    
    # Check if file is already in project directory
    if [ -f "$DDM_XML_BASENAME" ]; then
        echo -e "${GREEN}DDM XML already in project: $DDM_XML_BASENAME${NC}"
    else
        echo -e "${BLUE}Copying DDM XML to project: $DDM_XML_BASENAME${NC}"
        cp "$DDM_XML" "$DDM_XML_BASENAME"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to copy DDM XML file${NC}"
            exit 1
        fi
        echo -e "${GREEN}DDM XML copied successfully${NC}"
    fi
    
    # Update DDM_XML to point to the project-relative path
    export DDM_XML="$DDM_XML_BASENAME"
fi

if [ -n "$SPEC_FILE" ]; then
    # Check if SPEC_FILE exists
    if [ ! -f "$SPEC_FILE" ]; then
        echo -e "${RED}Error: Spec file not found: $SPEC_FILE${NC}"
        exit 1
    fi
    
    SPEC_FILE_BASENAME=$(basename "$SPEC_FILE")
    
    # Check if file is already in project directory
    if [ -f "$SPEC_FILE_BASENAME" ]; then
        echo -e "${GREEN}Spec file already in project: $SPEC_FILE_BASENAME${NC}"
    else
        echo -e "${BLUE}Copying Spec file to project: $SPEC_FILE_BASENAME${NC}"
        cp "$SPEC_FILE" "$SPEC_FILE_BASENAME"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to copy Spec file${NC}"
            exit 1
        fi
        echo -e "${GREEN}Spec file copied successfully${NC}"
    fi
    
    # Update SPEC_FILE to point to the project-relative path
    export SPEC_FILE="$SPEC_FILE_BASENAME"
fi

# Define Simics agent directory for potential use
SIMICS_AGENT_DIR="$SCRIPT_DIR/contributing/samples/simics_integration"

# Create Simics agent configuration if DDM_XML, SPEC_FILE, or DEVICE_NAME is provided
if [ -n "$DDM_XML" ] || [ -n "$SPEC_FILE" ] || [ -n "$DEVICE_NAME" ]; then
    echo -e "${BLUE}🔧 Configuring Simics integration for hardware development...${NC}"
    
    if [ -d "$SIMICS_AGENT_DIR" ]; then
        echo -e "${GREEN}✅ Simics integration agent found${NC}"
        echo "   The agent will help you set up Simics projects and DML device skeletons."
        echo "   You can ask it to:"
        echo "   • 'Create a new Simics project for my device'"
        echo "   • 'Add a DML skeleton for the $DEVICE_NAME device'"
        echo "   • 'Help me implement hardware registers from DDM XML'"
        echo ""
    else
        echo -e "${YELLOW}⚠️  Simics integration agent not found at $SIMICS_AGENT_DIR${NC}"
        echo "   Continuing with standard OpenSpec agent..."
    fi
fi

# TODO: call the ddm script to generatre the DDM skeleton

# TODO: change the agent prompt to "generate registers side effects for ddm device"

# Create agent directory for session management
mkdir -p "adk_openspec_agent"

# Always use the standard OpenSpec agent for the main interactive session
echo -e "${BLUE}📋 Using OpenSpec integration agent for main interactive session${NC}"
cat > "adk_openspec_agent/agent.py" << EOF
import sys
import os

# Add parent directory to path for spec_kit_integration imports
sys.path.insert(0, os.path.dirname('$SPEC_KIT_INTEGRATION_DIR'))

# Import the OpenSpec agent directly
sys.path.insert(0, '$OPENSPEC_INTEGRATION_DIR')
from agent import root_agent
EOF

# Run Simics setup agent first if hardware development is detected
if [ -n "$DDM_XML" ] || [ -n "$SPEC_FILE" ] || [ -n "$DEVICE_NAME" ]; then
    if [ -d "$SIMICS_AGENT_DIR" ]; then
        echo -e "${BLUE}🔧 Running Simics project setup first...${NC}"
        
        # Create temporary Simics setup agent
        mkdir -p "adk_simics_setup_agent"
        cat > "adk_simics_setup_agent/agent.py" << EOF
import sys
import os

# Add parent directory to path for simics_integration imports
sys.path.insert(0, os.path.dirname('$SIMICS_AGENT_DIR'))

# Import the Simics integration agent
sys.path.insert(0, '$SIMICS_AGENT_DIR')
from agent import root_agent
EOF

        # Get absolute path for simics-project in current directory
        SIMICS_PROJECT_PATH="$(pwd)/simics-project"
        
        # Prepare initial setup prompt for Simics
        SIMICS_SETUP_PROMPT="Execute these MCP tool calls immediately: create_simics_project(project_path=\"$SIMICS_PROJECT_PATH\") then add_dml_device_skeleton(project_path=\"$SIMICS_PROJECT_PATH\", device_name=\"$DEVICE_NAME\"). After completion, provide a brief 3-sentence confirmation stating: project created at $SIMICS_PROJECT_PATH, device skeleton created for $DEVICE_NAME, and project ready for DML development. Be concise."

        echo ""
        echo -e "${BLUE}📋 Setting up Simics project structure for device: $DEVICE_NAME${NC}"
        echo "   This will create the simics-project/ directory and DML device skeleton..."
        echo "   Working directory: $(pwd)"
        echo "   Simics agent path: $SIMICS_AGENT_DIR"
        echo ""
        
        # Check if the Simics agent file exists
        if [ ! -f "$SIMICS_AGENT_DIR/agent.py" ]; then
            echo -e "${RED}❌ Simics agent.py not found at $SIMICS_AGENT_DIR/agent.py${NC}"
            echo "   Skipping Simics setup..."
        else
            echo -e "${GREEN}✅ Simics agent.py found${NC}"
            echo "   Running Simics setup..."
            echo ""
            
            # Build Simics setup command with session options
            SIMICS_SETUP_CMD="$ADK_VENV/bin/adk run adk_simics_setup_agent"
            
            if [ "$SAVE_SESSION" = true ]; then
                SIMICS_SETUP_CMD="$SIMICS_SETUP_CMD --save_session --session_id ${PROJECT_NAME}_simics_setup"
                echo "   Simics setup session will be saved as: adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.json"
            fi
            
            # Run Simics setup with the setup prompt and exit command
            # Use printf to send the entire prompt as a single message, then exit
            echo -e "${BLUE}Executing Simics setup agent...${NC}"
            if printf "%s\nexit\n" "$SIMICS_SETUP_PROMPT" | $SIMICS_SETUP_CMD 2>&1; then
                echo ""
                echo -e "${GREEN}✅ Simics setup agent completed${NC}"
                
                # Generate human-readable session dump if session was saved
                if [ "$SAVE_SESSION" = true ] && [ -f "adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.json" ]; then
                    echo -e "${GREEN}Simics setup session saved: adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.json${NC}"
                    
                    # Generate human-readable session dump
                    if [ -f "$SCRIPT_DIR/view_session.py" ]; then
                        echo "📄 Generating human-readable Simics setup session dump..."
                        python3 "$SCRIPT_DIR/view_session.py" "adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.json" > "adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.txt"
                        if [ -f "adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.txt" ]; then
                            echo -e "${GREEN}Human-readable Simics setup session saved: adk_simics_setup_agent/${PROJECT_NAME}_simics_setup.session.txt${NC}"
                        fi
                    fi
                fi
            else
                echo ""
                echo -e "${YELLOW}⚠️  Simics setup agent completed with warnings${NC}"
            fi
            
            # Check if the simics-project directory was actually created
            if [ -d "simics-project" ]; then
                echo -e "${GREEN}✅ simics-project/ directory created successfully${NC}"
                echo "   Contents: $(ls -la simics-project/ 2>/dev/null || echo 'Directory empty or inaccessible')"
            else
                echo -e "${RED}❌ simics-project/ directory was not created${NC}"
                echo "   This may indicate an issue with the MCP tools or agent execution"
            fi
        fi
        
        # Keep the Simics setup agent for potential reuse or debugging
        
        echo ""
        echo -e "${BLUE}🎯 Now launching main agent for interactive development...${NC}"
        echo ""
    fi
fi

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
    echo -e "${GREEN}Session saved: adk_openspec_agent/${PROJECT_NAME}_openspec.session.json${NC}"
    
    # Generate human-readable session dump
    if [ -f "$SCRIPT_DIR/view_session.py" ]; then
        echo "📄 Generating human-readable session dump..."
        python3 "$SCRIPT_DIR/view_session.py" "adk_openspec_agent/${PROJECT_NAME}_openspec.session.json" > "adk_openspec_agent/${PROJECT_NAME}_openspec.session.txt"
        if [ -f "adk_openspec_agent/${PROJECT_NAME}_openspec.session.txt" ]; then
            echo -e "${GREEN}Human-readable session saved: adk_openspec_agent/${PROJECT_NAME}_openspec.session.txt${NC}"
        else
            echo -e "${YELLOW}Failed to generate human-readable session dump${NC}"
        fi
    fi
    
    echo ""
    echo "To resume this session later:"
    echo "  ./run_openspec.sh $PROJECT_NAME --resume"
    echo ""
    echo "To resume with a different model:"
    echo "  ./run_openspec.sh $PROJECT_NAME --resume --model $MODEL"
fi
