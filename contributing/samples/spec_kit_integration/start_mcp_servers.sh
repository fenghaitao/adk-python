#!/bin/bash

# Start MCP Server for Spec-Kit Integration
# This script starts the Simics MCP server with SSE transport

set -e

echo "🚀 Starting MCP server for Spec-Kit integration..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start a server in the background
start_server() {
    local name=$1
    local port=$2
    local command=$3
    local working_dir=$4

    echo -e "${BLUE}Starting $name on port $port...${NC}"

    if check_port $port; then
        echo -e "${YELLOW}Warning: Port $port is already in use. $name may already be running.${NC}"
        return 0
    fi

    cd "$working_dir"
    echo -e "${BLUE}Working directory: $working_dir${NC}"
    echo -e "${BLUE}Command: $command${NC}"

    # Start the server in the background
    eval "$command" &
    local shell_pid=$!

    # Wait for server to start with retry logic
    local max_attempts=15
    local wait_time=2
    local attempt=1
    
    echo -e "${BLUE}🔍 Waiting for $name to start on port $port...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            echo -e "${GREEN}✅ $name is listening on port $port (attempt $attempt/$max_attempts)${NC}"
            break
        fi
        
        echo -e "${YELLOW}⏳ Waiting for $name... (attempt $attempt/$max_attempts)${NC}"
        sleep $wait_time
        attempt=$((attempt + 1))
    done

    # Final verification that server started
    if check_port $port; then
        # Find the actual Python process PID (child of shell)
        local python_pid=""
        if kill -0 $shell_pid 2>/dev/null; then
            # Look for Python subprocess
            python_pid=$(pgrep -P $shell_pid 2>/dev/null | head -1)

            if [ -n "$python_pid" ] && kill -0 $python_pid 2>/dev/null; then
                echo -e "${GREEN}✅ $name started successfully (Shell PID: $shell_pid, Python PID: $python_pid)${NC}"
                echo "$shell_pid,$python_pid" > "${SCRIPT_DIR}/${name,,}_mcp_server.pid"
                return 0
            else
                # Fallback: use shell PID if no subprocess found
                echo -e "${YELLOW}⚠️  Using shell PID $shell_pid (no Python subprocess detected)${NC}"
                echo "$shell_pid" > "${SCRIPT_DIR}/${name,,}_mcp_server.pid"
                return 0
            fi
        else
            echo -e "${RED}❌ Failed to start $name (shell process died)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Failed to start $name (port not listening after $((max_attempts * wait_time)) seconds)${NC}"
        return 1
    fi
}

echo ""
echo "Starting Simics MCP Server..."
echo "   This server provides Simics device modeling tools and documentation access"

SIMICS_SERVER_DIR="$SCRIPT_DIR/simics-mcp-server"
if [ -d "$SIMICS_SERVER_DIR" ]; then
    # Check if the server is already running
    if check_port 8051; then
        echo -e "${YELLOW}Simics MCP server appears to already be running on port 8051${NC}"
        echo -e "${YELLOW}Use ./stop_mcp_servers.sh to stop it first if you want to restart${NC}"
    else
        # Start Simics MCP server with SSE transport
        SIMICS_COMMAND="$SIMICS_SERVER_DIR/.venv/bin/python run_server_sse.py --port 8051"
        if start_server "Simics-MCP" 8051 "$SIMICS_COMMAND" "$SIMICS_SERVER_DIR"; then
            # Wait a bit more and verify server is responding
            sleep 2
            if check_port 8051; then
                echo -e "${GREEN}✅ Simics MCP Server is running and listening on port 8051${NC}"
            else
                echo -e "${RED}❌ Simics MCP Server started but not responding on port 8051${NC}"
            fi
        else
            echo -e "${RED}❌ Failed to start Simics MCP Server${NC}"
            exit 1
        fi
    fi
else
    echo -e "${RED}❌ Simics MCP server directory not found: $SIMICS_SERVER_DIR${NC}"
    echo -e "${YELLOW}Please ensure the simics-mcp-server submodule is properly initialized${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 MCP server startup completed!${NC}"
echo ""
echo "Server Status:"
echo "  ✓ Simics MCP Server:    http://localhost:8051/sse"
echo ""
echo "To stop the server, run:"
echo "  ./stop_mcp_servers.sh"
echo ""
echo "To test the integration:"
echo "  python test_integrated_workflow.py"
