#!/bin/bash

set -e

# Run OpenSpec Apply workflow with GitHub Copilot agents
# Usage: ./run-openspec-copilot-apply.sh <workdir> <mcp_port>
# Example: ./run-openspec-copilot-apply.sh myproject 8051

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
    echo "Usage: $0 <workdir> <mcp_port>"
    echo "Example: $0 myproject 8051"
    exit 1
fi

WORKDIR="$1"
MCP_PORT="$2"
DEVICE_NAME="wdt"
BUILTIN_MCP="${BUILTIN_MCP_SERVER:-no}"

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
echo -e "${BLUE}OpenSpec Copilot Apply Workflow${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Working directory: $WORKDIR"
echo "MCP Port: $MCP_PORT"
echo "Device Name: $DEVICE_NAME"
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

# Change to working directory
cd "$WORKDIR"

mkdir -p log

# Step 3: Create .github directory and setup agent file
echo -e "${BLUE}Step 3: Setting up GitHub Copilot agent...${NC}"
mkdir -p .github/agents

# Create openspec_apply.agent.md
cat > .github/agents/openspec_apply.agent.md << 'EOF'
---
name: OpenSpec-Apply
description: Execute OpenSpec Apply phase - implement Simics device DML code and tests from approved proposals
---

EOF
cat "$SCRIPT_DIR/../contributing/samples/openspec_integration/apply_agent_instruction.md" >> .github/agents/openspec_apply.agent.md

echo -e "${GREEN}✅ Copilot agent file created in .github/agents/${NC}"
echo ""

# Step 3.5: Configure Copilot MCP server settings
echo -e "${BLUE}Step 3.5: Configuring Copilot MCP server settings...${NC}"
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

# Step 8: List OpenSpec changes and extract capability names
echo -e "${BLUE}Step 8: Listing OpenSpec changes...${NC}"
OPENSPEC_LIST_OUTPUT=$(openspec list 2>&1)
echo "$OPENSPEC_LIST_OUTPUT"
echo ""

# Step 9: Apply each capability
echo -e "${BLUE}Step 9: Preparing to run OpenSpec Apply agent for each capability...${NC}"

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
    echo -e "${YELLOW}   Please create proposals first${NC}"
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
            if copilot --allow-all-tools --agent openspec_apply --log-dir log --log-level debug -p "$APPLY_PROMPT"; then
                echo -e "${GREEN}✅ Apply completed for $CAPABILITY_NAME${NC}"
            else
                echo -e "${YELLOW}⚠️  Apply completed with warnings for $CAPABILITY_NAME${NC}"
            fi
            echo ""
            
            CAPABILITY_INDEX=$((CAPABILITY_INDEX + 1))
        fi
    done <<< "$CAPABILITY_NAMES"
fi

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}OpenSpec Copilot Apply workflow completed!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Summary:"
echo "  • Copilot agent configured"
if [ -n "$CAPABILITY_NAMES" ]; then
    echo "  • Apply agent executed for $CAPABILITY_COUNT capability(ies)"
else
    echo "  • No capabilities found to apply"
fi
echo ""
echo "Next steps:"
if [ -z "$CAPABILITY_NAMES" ]; then
    echo "  1. Create proposals in the changes/ directory"
    echo "  2. Then run this script again to apply changes"
else
    echo "  1. Review the implementation in simics-project/"
    echo "  2. Build and test: cd simics-project && make"
    echo "  3. Run tests: cd simics-project && make test"
fi
echo ""
