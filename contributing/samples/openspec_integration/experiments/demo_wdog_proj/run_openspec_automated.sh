#!/bin/bash
# Automated OpenSpec Runner for Watchdog Implementation
# This script runs OpenSpec for each register implementation automatically

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
MODEL="iflow/Qwen3-Coder"
PORT=8051
OPENSPEC_RUNNER="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/run_openspec.sh"
PROJECT_NAME="demo_wdog_openspec"

# Change to project directory
cd "$PROJECT_DIR"

# Function to initialize Git if needed
init_git_if_needed() {
    if [ ! -d ".git" ]; then
        echo -e "${YELLOW}📦 Initializing Git repository...${NC}"
        git init
        cat > .gitignore << 'GITIGNORE'
# Build artifacts
*.o
*.so
*.pyc
__pycache__/
*.swp
*.swo
*~

# Simics generated
*.log
*.trace
checkpoints/

# IDE
.vscode/
.idea/

# Python
.venv/
venv/
*.egg-info/

# Session files
*.session.json
*.session.txt
GITIGNORE
        git add .
        git commit -m "Initial commit - OpenSpec DDM project setup"
        echo -e "${GREEN}✅ Git repository initialized${NC}"
    fi
}

# Function to archive change and commit to git
archive_and_commit() {
    local change_id=$1
    local task_title=$2
    
    echo -e "${YELLOW}📦 Archiving change: $change_id${NC}"
    
    # Archive with openspec
    source /nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate
    openspec archive "$change_id" --yes 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Archive command not fully complete (this is normal)${NC}"
    }
    
    echo -e "${YELLOW}💾 Committing changes to Git${NC}"
    
    # Git commit all changes
    git add .
    git commit -m "✅ Completed: $task_title

Change ID: $change_id
Task completed and archived by OpenSpec orchestrator.
" 2>/dev/null || echo -e "${YELLOW}No new changes to commit${NC}"
    
    echo -e "${GREEN}✅ Change processed${NC}"
    echo ""
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Automated Watchdog Implementation via OpenSpec           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Initialize Git
init_git_if_needed

echo -e "${BLUE}📍 Working directory: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}🤖 Model: ${MODEL}${NC}"
echo -e "${BLUE}📝 Project: ${PROJECT_NAME}${NC}"
echo ""

# List all change proposals
CHANGES=$(ls -1 openspec/changes/ 2>/dev/null | grep -E '^implement-' | sort)
CHANGE_COUNT=$(echo "$CHANGES" | wc -l)

echo -e "${GREEN}✅ Found ${CHANGE_COUNT} change proposals${NC}"
echo ""

# Array of registers in order of implementation
REGISTERS=(
    "implement-watchdog load"
    "implement-watchdog value"
    "implement-watchdog control"
    "implement-watchdog interrupt clear"
    "implement-watchdog raw interrupt status"
    "implement-watchdog interrupt status"
    "implement-watchdog lock"
    "implement-watchdog integration test control"
    "implement-watchdog integration test output set"
)

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Starting Implementation${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

for ((i=0; i<${#REGISTERS[@]}; i++)); do
    CHANGE_ID="${REGISTERS[$i]}"
    TASK_NUM=$((i+1))
    TOTAL=${#REGISTERS[@]}
    
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}║ Task ${TASK_NUM}/${TOTAL}: ${CHANGE_ID}${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Check if change proposal exists
    if [ ! -d "openspec/changes/${CHANGE_ID}" ]; then
        echo -e "${RED}❌ Change proposal not found: ${CHANGE_ID}${NC}"
        echo -e "${YELLOW}   Skipping...${NC}"
        echo ""
        continue
    fi
    
    # Create a focused prompt for this register
    REGISTER_NAME=$(echo "$CHANGE_ID" | sed 's/implement-watchdog //' | tr '-' ' ' | sed 's/\b\(.\)/\u\1/g')
    
    PROMPT="I need you to implement the Watchdog ${REGISTER_NAME} register based on the OpenSpec change proposal.

Please:
1. Review the change proposal in openspec/changes/${CHANGE_ID}/
2. Read the tasks in openspec/changes/${CHANGE_ID}/tasks.md
3. Implement all the required changes in the DML file
4. Create comprehensive tests
5. Validate the implementation

Focus ONLY on this specific register. When you're done with ALL tasks in the checklist, respond with 'IMPLEMENTATION COMPLETE'.

Start now."
    
    echo -e "${BLUE}🤖 Running OpenSpec agent for: ${CHANGE_ID}${NC}"
    echo ""
    
    # Run OpenSpec with the specific prompt
    # Use --save-session to track progress
    SESSION_FILE="${PROJECT_NAME}_${CHANGE_ID// /_}.session"
    
    echo "$PROMPT" | "$OPENSPEC_RUNNER" "$PROJECT_NAME" \
        --model "$MODEL" \
        --port "$PORT" \
        --save-session \
        2>&1 | tee "/tmp/openspec_${CHANGE_ID// /_}.log" || {
        echo -e "${YELLOW}⚠️  OpenSpec session ended${NC}"
    }
    
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  Review the implementation above${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Ask user for confirmation before archiving
    read -p "$(echo -e ${GREEN}Was the implementation successful? Archive and continue? [Y/n]: ${NC})" -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        archive_and_commit "$CHANGE_ID" "Implement ${REGISTER_NAME} register"
        echo -e "${GREEN}✅ Task ${TASK_NUM}/${TOTAL} completed${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping archive. You can manually archive later with:${NC}"
        echo -e "${YELLOW}   openspec archive '${CHANGE_ID}'${NC}"
    fi
    
    echo ""
    echo ""
    
    # Small delay between tasks
    sleep 2
done

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}║  🎉 All Tasks Processed!${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review all implementations: git log --oneline"
echo "2. Run tests: cd $PROJECT_DIR && make test"
echo "3. Build the module: make"
echo "4. Test in Simics"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
