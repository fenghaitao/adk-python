#!/bin/bash

# Start MCP Server for Spec-Kit Integration
# This script starts the Crawl4AI RAG server (Simics MCP uses stdio transport)

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
    
    # Give the server time to start
    sleep 3
    
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
        echo -e "${RED}❌ Failed to start $name${NC}"
        return 1
    fi
}

echo ""
echo "Starting Crawl4AI RAG Server..."
echo "   This server provides documentation search and RAG capabilities"

RAG_SERVER_DIR="$SCRIPT_DIR/mcp-crawl4ai-rag"
if [ -d "$RAG_SERVER_DIR" ]; then
    # Check if the server is already running
    if check_port 8051; then
        echo -e "${YELLOW}Crawl4AI RAG server appears to already be running on port 8051${NC}"
    else
        # Check for virtual environment and choose appropriate Python
        RAG_COMMAND=".venv/bin/python src/crawl4ai_mcp.py"
        start_server "Crawl4AI-RAG" 8051 "$RAG_COMMAND" "$RAG_SERVER_DIR"
    fi
else
    echo -e "${RED}❌ Crawl4AI RAG server directory not found: $RAG_SERVER_DIR${NC}"
    echo -e "${YELLOW}Please ensure the mcp-crawl4ai-rag submodule is properly initialized${NC}"
fi

echo ""
echo -e "${BLUE}ℹ️  Note: Simics MCP server uses stdio transport and is managed directly by ADK${NC}"
echo -e "${BLUE}   No separate server process needed for Simics tools${NC}"

echo ""
echo -e "${GREEN}🎉 MCP server startup process completed!${NC}"
echo ""
echo "Server Status:"
echo "  📚 Crawl4AI RAG Server:  http://localhost:8051/sse"
echo "  🔧 Simics MCP Tools:     Available via stdio transport (managed by ADK)"
echo ""
echo "To stop the server, run:"
echo "  ./stop_mcp_servers.sh"
echo ""
echo "To test the integration:"
echo "  python test_integrated_workflow.py"