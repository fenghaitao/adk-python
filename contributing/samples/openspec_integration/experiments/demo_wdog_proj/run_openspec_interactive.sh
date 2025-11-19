#!/bin/bash
# Helper script to run OpenSpec agents for the watchdog implementation
# Features:
# - Interactive menu
# - Automatic archiving after task completion
# - Git commits after each task

set -e

# Configuration
PROJECT_DIR="/nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj"
OPENSPEC_SCRIPT="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/run_openspec.sh"
PROJECT_NAME="demo_wdog_openspec"
MODEL="${1:-iflow/Qwen3-Coder}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to initialize Git if needed
init_git_if_needed() {
    cd "$PROJECT_DIR"
    if [ ! -d ".git" ]; then
        echo -e "${YELLOW}📦 Initializing Git repository...${NC}"
        git init
        
        # Create .gitignore if it doesn't exist
        if [ ! -f ".gitignore" ]; then
            cat > .gitignore << 'EOF'
# Build artifacts
*.o
*.so
*.pyc
__pycache__/
.venv/
*.egg-info/

# IDE
.vscode/
.idea/

# Simics specific
linux64/
*.d

# Temporary files
*.log
*.tmp
EOF
        fi
        
        git add .
        git commit -m "Initial commit - OpenSpec DDM project setup"
        echo -e "${GREEN}✅ Git repository initialized${NC}"
    else
        echo -e "${GREEN}✅ Git repository already exists${NC}"
    fi
}

# Function to archive change and commit
archive_and_commit() {
    local change_id=$1
    local task_title=$2
    
    cd "$PROJECT_DIR"
    
    echo ""
    echo -e "${YELLOW}📦 Archiving change: $change_id${NC}"
    
    # Activate OpenSpec venv for archive command
    source ~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate
    
    # Archive the change
    openspec archive "$change_id" --yes || echo "Archive failed or not needed"
    
    echo -e "${YELLOW}💾 Committing changes to Git${NC}"
    
    # Commit all changes
    git add .
    git commit -m "✅ Completed: $task_title

Change ID: $change_id
Task completed and archived by OpenSpec.
" || echo "No changes to commit"
    
    echo -e "${GREEN}✅ Change archived and committed to Git${NC}"
    echo ""
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   OpenSpec Agent Runner for Watchdog Implementation        ║${NC}"
echo -e "${BLUE}║   with Auto-Archive & Git Integration                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Project directory not found: $PROJECT_DIR${NC}"
    echo "Please update the PROJECT_DIR variable in this script"
    exit 1
fi

# Check if OpenSpec script exists
if [ ! -f "$OPENSPEC_SCRIPT" ]; then
    echo -e "${YELLOW}⚠️  OpenSpec script not found: $OPENSPEC_SCRIPT${NC}"
    echo "Please update the OPENSPEC_SCRIPT variable in this script"
    exit 1
fi

# Initialize Git if needed
init_git_if_needed

# Navigate to project
cd "$PROJECT_DIR"

echo "📍 Working directory: $(pwd)"
echo "🤖 Model: $MODEL"
echo "📝 Project: $PROJECT_NAME"
echo ""

# Count change proposals
PROPOSAL_COUNT=$(ls -d openspec/changes/implement-* 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Found $PROPOSAL_COUNT change proposals${NC}"
echo ""

# Show available proposals
echo "Available change proposals:"
ls -1 openspec/changes/ | grep "^implement-" | sed 's/^/  - /'
echo ""

# Prompt for action
echo -e "${YELLOW}Choose an option:${NC}"
echo "1) Start fresh implementation (all registers)"
echo "2) Resume from saved session"
echo "3) Implement specific register"
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 Starting fresh OpenSpec session...${NC}"
        echo ""
        
        PROMPT="I need you to implement the watchdog device model registers.

Context:
- Project: Simics DDM watchdog device
- DML file: modules/demo_watchdog/demo_watchdog.dml
- Spec: wdt.md (Chinese hardware specification)
- Change proposals: openspec/changes/

Tasks:
1. Review all change proposals in openspec/changes/
2. Start with implement-watchdog-load
3. Implement each register following DML 1.4 best practices
4. Create Python tests for each register
5. Validate implementations match the hardware spec

Important:
- After completing EACH register, tell me so I can archive it and commit to Git
- The workflow for each register is:
  a) Implement the register in DML
  b) Create tests
  c) Validate it works
  d) Tell me it's complete
  e) I'll run: archive_and_commit <change-id> <title>

Please implement the registers one by one, starting with the most critical ones (those with side effects).
Let me know when you're ready to start."
        
        echo "$PROMPT" | $OPENSPEC_SCRIPT "$PROJECT_NAME" --model "$MODEL" --save-session
        
        # After session, ask user which changes to archive
        echo ""
        echo -e "${YELLOW}Which changes did you complete? (for archiving and Git commit)${NC}"
        echo "Enter change IDs separated by spaces, or 'none':"
        ls -1 openspec/changes/ | grep "^implement-" | nl
        read -p "Change IDs: " completed_changes
        
        if [ "$completed_changes" != "none" ]; then
            for change_id in $completed_changes; do
                # If it's a number, convert to change-id
                if [[ "$change_id" =~ ^[0-9]+$ ]]; then
                    change_id=$(ls -1 openspec/changes/ | grep "^implement-" | sed -n "${change_id}p")
                fi
                
                if [ -n "$change_id" ]; then
                    archive_and_commit "$change_id" "$(echo $change_id | sed 's/-/ /g')"
                fi
            done
        fi
        ;;
        
    2)
        echo ""
        echo -e "${GREEN}🔄 Resuming from saved session...${NC}"
        echo ""
        
        # Check if session exists
        if [ -f "adk_openspec_agent/${PROJECT_NAME}_openspec.session.json" ]; then
            $OPENSPEC_SCRIPT "$PROJECT_NAME" --resume --model "$MODEL"
        else
            echo -e "${YELLOW}⚠️  No saved session found${NC}"
            echo "Session file: adk_openspec_agent/${PROJECT_NAME}_openspec.session.json"
            echo ""
            echo "Please run option 1 first to create a session"
        fi
        ;;
        
    3)
        echo ""
        echo "Available registers:"
        ls -1 openspec/changes/ | grep "^implement-" | nl
        echo ""
        read -p "Enter number of register to implement: " reg_num
        
        REGISTER=$(ls -1 openspec/changes/ | grep "^implement-" | sed -n "${reg_num}p")
        
        if [ -z "$REGISTER" ]; then
            echo -e "${YELLOW}⚠️  Invalid selection${NC}"
            exit 1
        fi
        
        echo ""
        echo -e "${GREEN}🎯 Implementing: $REGISTER${NC}"
        echo ""
        
        PROMPT="I need you to implement the $REGISTER register.

Please:
1. Read the proposal in openspec/changes/$REGISTER/
2. Review the hardware spec in wdt.md
3. Implement the register in modules/demo_watchdog/demo_watchdog.dml
4. Create tests in modules/demo_watchdog/test/
5. Validate the implementation

Focus only on this register. Let me know when it's complete so I can archive it and commit to Git."
        
        echo "$PROMPT" | $OPENSPEC_SCRIPT "$PROJECT_NAME" --model "$MODEL" --save-session
        
        # Ask if the task was completed
        echo ""
        read -p "Was the task completed successfully? (y/n): " completed
        if [ "$completed" = "y" ] || [ "$completed" = "Y" ]; then
            archive_and_commit "$REGISTER" "$(echo $REGISTER | sed 's/-/ /g')"
        fi
        ;;
        
    4)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo -e "${YELLOW}⚠️  Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Session Complete                                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Git commit log:"
git log --oneline -5
echo ""
echo "Next steps:"
echo "1. Review the implementations: git log -p"
echo "2. Run tests: cd $PROJECT_DIR && make test"
echo "3. Validate: openspec validate --all"
echo "4. Check archived changes: ls openspec/changes/archive/"
echo "5. Resume work: $0"
echo ""
