#!/bin/bash

# Stop MCP Server for Spec-Kit Integration

echo "🛑 Stopping MCP server for Spec-Kit integration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to stop a server by PID file
stop_server_by_pid() {
    local name=$1
    local pid_file="${SCRIPT_DIR}/${name,,}_mcp_server.pid"
    
    if [ -f "$pid_file" ]; then
        local pid_content=$(cat "$pid_file")
        echo -e "${YELLOW}Found PID file for $name: $pid_content${NC}"
        
        # Parse PIDs - could be single PID or "shell_pid,python_pid" 
        local shell_pid=""
        local python_pid=""
        
        if [[ "$pid_content" == *","* ]]; then
            # Format: "shell_pid,python_pid"
            shell_pid=$(echo "$pid_content" | cut -d',' -f1)
            python_pid=$(echo "$pid_content" | cut -d',' -f2)
            echo -e "${YELLOW}Found Shell PID: $shell_pid, Python PID: $python_pid${NC}"
        else
            # Format: single PID (could be shell or python)
            shell_pid="$pid_content"
            echo -e "${YELLOW}Found single PID: $shell_pid${NC}"
        fi
        
        # Try to stop Python process first (if available), then shell process
        local stopped=false
        
        if [ -n "$python_pid" ] && kill -0 "$python_pid" 2>/dev/null; then
            echo -e "${YELLOW}Stopping Python process (PID: $python_pid)...${NC}"
            kill "$python_pid" 2>/dev/null || true
            
            # Check if Python process stopped
            for i in {1..3}; do
                sleep 1
                if ! kill -0 "$python_pid" 2>/dev/null; then
                    echo -e "${GREEN}✅ Python process stopped${NC}"
                    stopped=true
                    break
                fi
            done
            
            # Force kill Python if needed
            if [ "$stopped" = false ] && kill -0 "$python_pid" 2>/dev/null; then
                echo -e "${YELLOW}Force killing Python process...${NC}"
                kill -9 "$python_pid" 2>/dev/null || true
                sleep 1
                if ! kill -0 "$python_pid" 2>/dev/null; then
                    stopped=true
                fi
            fi
        fi
        
        # If Python didn't stop or no Python PID, try shell process
        if [ "$stopped" = false ] && [ -n "$shell_pid" ] && kill -0 "$shell_pid" 2>/dev/null; then
            echo -e "${YELLOW}Stopping shell process (PID: $shell_pid)...${NC}"
            kill "$shell_pid" 2>/dev/null || true
            
            # Wait longer and check multiple times
            for i in {1..5}; do
                sleep 1
                if ! kill -0 "$shell_pid" 2>/dev/null; then
                    echo -e "${GREEN}✅ Shell process stopped gracefully${NC}"
                    stopped=true
                    break
                fi
                echo -e "${YELLOW}Waiting for shell process to stop... ($i/5)${NC}"
            done
            
            # Force kill shell if still running
            if [ "$stopped" = false ] && kill -0 "$shell_pid" 2>/dev/null; then
                echo -e "${YELLOW}Force killing shell process...${NC}"
                kill -9 "$shell_pid" 2>/dev/null || true
                sleep 2
                
                if ! kill -0 "$shell_pid" 2>/dev/null; then
                    echo -e "${GREEN}✅ Shell process force stopped${NC}"
                    stopped=true
                fi
            fi
        fi
        
        # Final status
        if [ "$stopped" = true ]; then
            echo -e "${GREEN}✅ $name stopped successfully${NC}"
        else
            echo -e "${RED}❌ Failed to stop $name${NC}"
            return 1
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}No PID file found for $name${NC}"
    fi
}

# Function to stop servers by port
stop_server_by_port() {
    local name=$1
    local port=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}Found processes on port $port: $pids${NC}"
        echo -e "${YELLOW}Stopping $name on port $port...${NC}"
        
        # Kill each PID individually with better error handling
        echo "$pids" | while read -r pid; do
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}Killing process $pid...${NC}"
                kill "$pid" 2>/dev/null || true
            fi
        done
        
        # Wait and check if processes are gone
        for i in {1..5}; do
            sleep 1
            local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
            if [ -z "$remaining_pids" ]; then
                echo -e "${GREEN}✅ $name stopped (port $port freed)${NC}"
                return 0
            fi
            echo -e "${YELLOW}Waiting for port $port to be freed... ($i/5)${NC}"
        done
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            echo -e "${YELLOW}Force killing remaining processes on port $port...${NC}"
            echo "$remaining_pids" | while read -r pid; do
                if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                    echo -e "${YELLOW}Force killing process $pid...${NC}"
                    kill -9 "$pid" 2>/dev/null || true
                fi
            done
            sleep 2
            
            # Final check
            local final_pids=$(lsof -ti:$port 2>/dev/null || true)
            if [ -z "$final_pids" ]; then
                echo -e "${GREEN}✅ $name force stopped (port $port freed)${NC}"
            else
                echo -e "${RED}❌ Failed to free port $port, remaining PIDs: $final_pids${NC}"
                return 1
            fi
        fi
    else
        echo -e "${YELLOW}$name was not running on port $port${NC}"
    fi
}

echo ""
echo "Stopping Crawl4AI RAG Server..."
stop_server_by_pid "Crawl4AI-RAG"
stop_server_by_port "Crawl4AI RAG Server" 8051

echo ""
echo -e "${GREEN}🎉 MCP server stopped!${NC}"
echo -e "${YELLOW}Note: Simics MCP tools use stdio transport (no server process to stop)${NC}"