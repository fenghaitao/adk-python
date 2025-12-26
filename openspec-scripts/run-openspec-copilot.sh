#!/bin/bash

set -e

# Run OpenSpec workflow with GitHub Copilot agents
# Usage: ./run-openspec-copilot.sh <workdir> <mcp_port> [OPTIONS]
# Example: ./run-openspec-copilot.sh myproject 8051
# Example: ./run-openspec-copilot.sh myproject 8051 --skip-init
# Example: ./run-openspec-copilot.sh myproject 8051 --skip-proposal
# Example: ./run-openspec-copilot.sh myproject 8051 --skip-apply
# Example: ./run-openspec-copilot.sh myproject 8051 --init-only
#
# Options:
#   --skip-init      Skip steps 1, 2, 5, 6, 7, 8 (initialization and setup)
#   --skip-proposal  Skip steps 1, 2, 5, 6, 7, 8, 9 (init + proposal)
#   --skip-apply     Skip steps 1, 2, 5, 6, 7, 8, 10 (init + apply)
#   --init-only      Run only steps 1-8 (initialization only, skip proposal and apply)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up paths
SPEC_KIT_INTEGRATION_DIR="$SCRIPT_DIR/../contributing/samples/spec_kit_integration"
MCP_SERVER_DIR="$SPEC_KIT_INTEGRATION_DIR/simics-mcp-server"

# Validate arguments
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: $0 <workdir> <mcp_port> [OPTIONS]"
    echo "Example: $0 myproject 8051"
    echo "Example: $0 myproject 8051 --skip-init"
    echo ""
    echo "Options:"
    echo "  --skip-init      Skip steps 1, 2, 5, 6, 7, 8 (initialization and setup)"
    echo "  --skip-proposal  Skip steps 1, 2, 5, 6, 7, 8, 9 (init + proposal)"
    echo "  --skip-apply     Skip steps 1, 2, 5, 6, 7, 8, 10 (init + apply)"
    echo "  --init-only      Run only steps 1-8 (initialization only, skip proposal and apply)"
    exit 1
fi

WORKDIR="$1"
MCP_PORT="$2"
DEVICE_NAME="wdt"
BUILTIN_MCP="${BUILTIN_MCP_SERVER:-no}"
SKIP_INIT=false
SKIP_PROPOSAL=false
SKIP_APPLY=false
INIT_ONLY=false

# Parse optional arguments
shift 2
while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-init)
            SKIP_INIT=true
            shift
            ;;
        --skip-proposal)
            SKIP_INIT=true
            SKIP_PROPOSAL=true
            shift
            ;;
        --skip-apply)
            SKIP_INIT=true
            SKIP_APPLY=true
            shift
            ;;
        --init-only)
            INIT_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Validate --init-only parameter
if [ "$INIT_ONLY" = true ]; then
    if [ "$SKIP_INIT" = true ] || [ "$SKIP_PROPOSAL" = true ] || [ "$SKIP_APPLY" = true ]; then
        echo -e "${RED}Error: --init-only cannot be used with --skip-init, --skip-proposal, or --skip-apply${NC}"
        exit 1
    fi
fi

# Track whether MCP servers were started
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

# Function to start MCP servers
start_mcp() {
    if [[ "$BUILTIN_MCP" != "yes" ]]; then
        echo -e "${YELLOW}⚠️  Skipping MCP server startup (BUILTIN_MCP_SERVER=no)${NC}"
        echo "   To enable MCP servers, set: export BUILTIN_MCP_SERVER=yes"
        return 0
    fi
    
    echo ""
    echo -e "${BLUE}🚀 Starting MCP servers on port $MCP_PORT...${NC}"
    if "$MCP_SERVER_DIR/start_mcp_servers.sh" "$MCP_PORT"; then
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
}

# Function to cleanup on script exit
cleanup() {
    if [ "$MCP_SERVERS_STARTED" = true ] && [ "$BUILTIN_MCP" = "yes" ]; then
        echo ""
        echo -e "${YELLOW}🛑 Cleaning up MCP servers...${NC}"
        "$MCP_SERVER_DIR/stop_mcp_servers.sh"
    fi
}

# Set up trap to cleanup on script exit
trap cleanup EXIT

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}OpenSpec Copilot Workflow${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Working directory: $WORKDIR"
echo "MCP Port: $MCP_PORT"
echo "Device Name: $DEVICE_NAME"
if [ "$SKIP_INIT" = true ]; then
    echo "Skip Mode: Initialization (steps 1, 2, 5, 6, 7, 8)"
fi
if [ "$SKIP_PROPOSAL" = true ]; then
    echo "Skip Mode: Proposal agent (step 9)"
fi
if [ "$SKIP_APPLY" = true ]; then
    echo "Skip Mode: Apply agent (step 10)"
fi
if [ "$INIT_ONLY" = true ]; then
    echo "Init Only Mode: Running steps 1-8 only"
fi
echo ""

# Validate port number
if ! [[ "$MCP_PORT" =~ ^[0-9]+$ ]] || [ "$MCP_PORT" -lt 1024 ] || [ "$MCP_PORT" -gt 65535 ]; then
    echo -e "${RED}Error: Invalid port number '$MCP_PORT'. Must be between 1024 and 65535.${NC}"
    exit 1
fi

# Export MCP_PORT for agents
export MCP_PORT="$MCP_PORT"

# Start MCP servers
start_mcp

# Step 1: Initialize Spec-Kit project
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 1: Initializing Spec-Kit project...${NC}"
    SPEC_KIT_VENV="$SCRIPT_DIR/../spec-kit/.venv"

    if [ ! -d "$SPEC_KIT_VENV" ]; then
        echo -e "${RED}Error: Spec-Kit virtual environment not found at $SPEC_KIT_VENV${NC}"
        echo "Please run: cd $SCRIPT_DIR/../spec-kit && python -m venv .venv && source .venv/bin/activate && pip install -e ."
        exit 1
    fi

    "$SPEC_KIT_VENV/bin/specify" init "$WORKDIR" --ai copilot --script sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to initialize Spec-Kit project${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Spec-Kit project initialized${NC}"
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 1: Spec-Kit initialization${NC}"
    echo ""
fi

# Step 2: Initialize OpenSpec project
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 2: Initializing OpenSpec project...${NC}"
    cd "$WORKDIR"
    openspec init . --tools none
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to initialize OpenSpec project${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ OpenSpec project initialized${NC}"
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 2: OpenSpec initialization${NC}"
    cd "$WORKDIR"
    echo ""
fi

# Step 3: Create .github directory and setup agent files
mkdir -p log
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 3: Setting up GitHub Copilot agents...${NC}"
    mkdir -p .github/agents
    
    # Create openspec_proposal.agent.md
    cat > .github/agents/openspec_proposal.agent.md << 'EOF'
---
name: OpenSpec-Proposal-Initial
description: Create OpenSpec proposals for Simics device INITIAL implementations.
---

EOF
    cat "$SCRIPT_DIR/../contributing/samples/openspec_integration/proposal_initial_agent_instruction.md" >> .github/agents/openspec_proposal.agent.md
    
    # Create openspec_apply.agent.md
    cat > .github/agents/openspec_apply.agent.md << 'EOF'
---
name: OpenSpec-Apply
description: Execute OpenSpec Apply phase - implement Simics device DML code and tests from approved proposals
---

EOF
    cat "$SCRIPT_DIR/../contributing/samples/openspec_integration/apply_agent_instruction.md" >> .github/agents/openspec_apply.agent.md
    
    # Copy simics_project_setup.agent.md
    cp "$SCRIPT_DIR/../openspec-copilot/agents/simics_project_setup.agent.md" .github/agents/
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to copy simics_project_setup.agent.md${NC}"
        exit 1
    fi
    
    # Copy specify.agent.md
    cp "$SCRIPT_DIR/../openspec-copilot/agents/specify.agent.md" .github/agents/
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to copy specify.agent.md${NC}"
        exit 1
    fi
   
    echo -e "${GREEN}✅ Copilot agent files created in .github/agents/${NC}"
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 3: GitHub Copilot agents setup${NC}"
    echo ""
fi

# Step 4: Configure Copilot MCP server settings
echo -e "${BLUE}Step 4: Configuring Copilot MCP server settings...${NC}"
MCP_CONFIG_FILE="$HOME/.copilot/mcp-config.json"

# Create config directory if it doesn't exist
mkdir -p "$HOME/.copilot"

# Check if config file exists
if [ -f "$MCP_CONFIG_FILE" ]; then
    # Read existing config and check for simics-mcp-server
    if grep -q '"simics-mcp-server"' "$MCP_CONFIG_FILE"; then
        # Extract current port from URL within mcpServers section
        CURRENT_PORT=$(sed -n '/"mcpServers":/,/^  }/{/"simics-mcp-server":/,/^    }/{/"url":/s/.*localhost:\([0-9]*\).*/\1/p}}' "$MCP_CONFIG_FILE")
        
        if [ "$CURRENT_PORT" = "$MCP_PORT" ]; then
            echo -e "${GREEN}✅ MCP server config already exists with correct port${NC}"
        else
            echo -e "${YELLOW}Updating MCP server port from $CURRENT_PORT to $MCP_PORT${NC}"
            # Replace the port in the URL
            sed -i "s|localhost:${CURRENT_PORT}/sse|localhost:${MCP_PORT}/sse|g" "$MCP_CONFIG_FILE"
            echo -e "${GREEN}✅ MCP server config updated${NC}"
        fi
    else
        # Add simics-mcp-server config
        echo -e "${YELLOW}Adding simics-mcp-server config${NC}"
        
        # Check if mcpServers section exists
        if grep -q '"mcpServers"' "$MCP_CONFIG_FILE"; then
            # mcpServers exists, add simics-mcp-server inside it
            # Find the closing brace of mcpServers and insert before it
            sed -i '/"mcpServers":/,/^  }/ {
                /^  }/ i\    ,\
    "simics-mcp-server": {\
      "url": "http://localhost:'"${MCP_PORT}"'/sse",\
      "type": "sse"\
    }
            }' "$MCP_CONFIG_FILE"
        else
            # No mcpServers section, add it
            if [ -s "$MCP_CONFIG_FILE" ]; then
                # File has content, add mcpServers section
                sed -i '$ d' "$MCP_CONFIG_FILE"
                cat >> "$MCP_CONFIG_FILE" << EOF
  ,
  "mcpServers": {
    "simics-mcp-server": {
      "url": "http://localhost:${MCP_PORT}/sse",
      "type": "sse"
    }
  }
}
EOF
            else
                # File is empty, create new config with mcpServers
                cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "simics-mcp-server": {
      "url": "http://localhost:${MCP_PORT}/sse",
      "type": "sse"
    }
  }
}
EOF
            fi
        fi
        echo -e "${GREEN}✅ MCP server config added${NC}"
    fi
else
    # Create new config file
    echo -e "${YELLOW}Creating new MCP config file${NC}"
    cat > "$MCP_CONFIG_FILE" << EOF
{
  "mcpServers": {
    "simics-mcp-server": {
      "url": "http://localhost:${MCP_PORT}/sse",
      "type": "sse"
    }
  }
}
EOF
    echo -e "${GREEN}✅ MCP server config created${NC}"
fi
echo ""

# Step 5: Copy specification files
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 5: Copying specification files...${NC}"
    cp "$SCRIPT_DIR/../simics-wdt-spec.md" .
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to copy simics-wdt-spec.md${NC}"
        exit 1
    fi

    cp "$SCRIPT_DIR/../wdt.md" .
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to copy wdt.md${NC}"
        exit 1
    fi

    cp -r "$SCRIPT_DIR/../openspec-memories" .
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to copy openspec-memories folder${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Specification files copied${NC}"
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 5: Copying specification files${NC}"
    echo ""
fi

# Step 6: Run Specify agent
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 6: Running Specify agent (IP-XACT generation)...${NC}"
    SPECIFY_PROMPT="/specify Read the Simics WDT specification from ./simics-wdt-spec.md and the hardware specifications from ./wdt.md to create a comprehensive Simics ${DEVICE_NAME} device implementation."

    echo "   Prompt: $SPECIFY_PROMPT"
    copilot --allow-all-tools --agent specify --log-dir ./log --log-level debug -p "$SPECIFY_PROMPT"
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Specify agent completed with warnings${NC}"
    else
        echo -e "${GREEN}✅ Specify agent completed${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 6: Specify agent${NC}"
    echo ""
fi

# Step 7: Fill project.md
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 7: Filling openspec/project.md...${NC}"
    PROJECT_PROMPT="Read current project to fill \`openspec/project.md\`"

    echo "   Prompt: $PROJECT_PROMPT"
    if copilot --allow-all-tools -p "$PROJECT_PROMPT"; then
        echo -e "${GREEN}✅ Project.md filled successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Project.md filling completed with warnings${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 7: Fill project.md${NC}"
    echo ""
fi

# Step 8: Run Simics Project Setup agent
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Step 8: Setting up Simics project...${NC}"
    SIMICS_SETUP_PROMPT="setup simics-project for device wdt"

    echo "   Prompt: $SIMICS_SETUP_PROMPT"
    if copilot --allow-all-tools --agent simics_project_setup -p "$SIMICS_SETUP_PROMPT"; then
        echo -e "${GREEN}✅ Simics project setup completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Simics project setup completed with warnings${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 8: Simics project setup${NC}"
    echo ""
fi

# Commit changes after project initialization
if [ "$SKIP_INIT" = false ]; then
    echo -e "${BLUE}Committing project initialization changes...${NC}"
    git add .
    git commit -m "Project Initialization done"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Changes committed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Git commit completed with warnings (possibly no changes to commit)${NC}"
    fi
    echo ""
fi

# Step 9: Run OpenSpec Proposal agent
if [ "$SKIP_PROPOSAL" = false ] && [ "$INIT_ONLY" = false ]; then
    echo -e "${BLUE}Step 9: Running OpenSpec Proposal agent...${NC}"
    PROPOSAL_PROMPT="/proposal proposal capabilities to implement simics watchdog timer device and tests based on spec.md in specs/"

    echo "   Prompt: $PROPOSAL_PROMPT"
    copilot --allow-all-tools --agent openspec_proposal --log-dir ./log --log-level debug -p "$PROPOSAL_PROMPT"
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Proposal agent completed with warnings${NC}"
    else
        echo -e "${GREEN}✅ Proposal agent completed${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⏭️  Skipping Step 9: Proposal agent${NC}"
    echo ""
fi

# Step 10: List OpenSpec changes and apply each capability
if [ "$SKIP_APPLY" = false ] && [ "$INIT_ONLY" = false ]; then
    echo -e "${BLUE}Step 10: Listing OpenSpec changes and applying capabilities...${NC}"
    OPENSPEC_LIST_OUTPUT=$(openspec list 2>&1)
    echo "$OPENSPEC_LIST_OUTPUT"
    echo ""

    echo -e "${BLUE}Preparing to run OpenSpec Apply agent for each capability...${NC}"

    # Parse capability names from openspec list output
    # Look for pattern: "capability-name" followed by task count
    # Example: "implement-watchdog-timer 0/39 tasks" or "001_add-wdt-registers 0/28 tasks"
    CAPABILITY_NAMES=$(echo "$OPENSPEC_LIST_OUTPUT" | grep -oE '([0-9]{3}_)?[a-zA-Z0-9_-]+\s+[0-9]+/[0-9]+\s+tasks' | grep -oE '^([0-9]{3}_)?[a-zA-Z0-9_-]+' | sort -u)

    # Debug: Show what was parsed
    if [ -n "$CAPABILITY_NAMES" ]; then
        echo -e "${BLUE}Parsed capability names:${NC}"
        echo "$CAPABILITY_NAMES"
        echo ""
    fi

    if [ -z "$CAPABILITY_NAMES" ]; then
        echo -e "${YELLOW}⚠️  No capabilities found in openspec list output${NC}"
        echo -e "${YELLOW}   This is expected when --skip-proposal is used${NC}"
        echo -e "${YELLOW}   Skipping apply step${NC}"
        echo ""
    else
        # Count capabilities
        CAPABILITY_COUNT=$(echo "$CAPABILITY_NAMES" | wc -l)
        echo -e "${GREEN}✅ Found $CAPABILITY_COUNT capability(ies) to apply${NC}"
        echo ""
        
        CAPABILITY_INDEX=1
        
        while IFS= read -r CAPABILITY_NAME; do
            if [ -n "$CAPABILITY_NAME" ]; then
                echo -e "${BLUE}[$CAPABILITY_INDEX/$CAPABILITY_COUNT] Applying capability: $CAPABILITY_NAME${NC}"
                APPLY_PROMPT="/apply --id $CAPABILITY_NAME"
                
                echo "   Prompt: $APPLY_PROMPT"
                if copilot --allow-all-tools --agent openspec_apply --log-dir ./log --log-level debug -p "$APPLY_PROMPT"; then
                    echo -e "${GREEN}✅ Apply completed for $CAPABILITY_NAME${NC}"
                else
                    echo -e "${YELLOW}⚠️  Apply completed with warnings for $CAPABILITY_NAME${NC}"
                fi
                echo ""
                
                CAPABILITY_INDEX=$((CAPABILITY_INDEX + 1))
            fi
        done <<< "$CAPABILITY_NAMES"
    fi
else
    echo -e "${YELLOW}⏭️  Skipping Step 10: Apply capabilities${NC}"
    echo ""
fi

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}OpenSpec Copilot workflow completed!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Summary:"
if [ "$SKIP_INIT" = false ]; then
    echo "  • Spec-Kit project initialized"
    echo "  • OpenSpec project initialized"
    echo "  • Specification files copied"
    echo "  • Specify agent executed (IP-XACT generation)"
    echo "  • Project.md filled"
    echo "  • Simics project setup completed"
fi
if [ "$SKIP_PROPOSAL" = false ]; then
    echo "  • Proposal agent executed"
fi
echo "  • Copilot agents configured"
if [ "$SKIP_APPLY" = false ] && [ "$INIT_ONLY" = false ]; then
    if [ -n "$CAPABILITY_NAMES" ]; then
        echo "  • Apply agent executed for $CAPABILITY_COUNT capability(ies)"
    else
        echo "  • No capabilities found to apply"
    fi
fi
echo ""
echo "Next steps:"
if [ "$SKIP_APPLY" = true ] || [ "$INIT_ONLY" = true ] || [ -z "$CAPABILITY_NAMES" ]; then
    echo "  1. Create a proposal: copilot --allow-all-tools --agent openspec_proposal -p '/proposal ...'"
    echo "  2. Then run this script again with --skip-proposal to apply changes"
else
    echo "  1. Review the implementation in simics-project/"
    echo "  2. Build and test: cd simics-project && make"
    echo "  3. Run tests: cd simics-project && make test"
fi
echo ""
