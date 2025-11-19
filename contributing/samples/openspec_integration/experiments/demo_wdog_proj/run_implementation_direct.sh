#!/bin/bash
# Direct OpenSpec Implementation Runner
# This runs the ADK agent directly for each change proposal

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_DIR="/nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj"
ADK_DIR="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec"
OPENSPEC_VENV="/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv"
MODEL="iflow/Qwen3-Coder"
PORT="8051"

cd "$PROJECT_DIR"

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}  Watchdog Register Implementation${NC}"
echo -e "${BLUE}  Using OpenSpec + ADK Agent${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Register list
REGISTERS=(
    "load:WDOGLOAD"
    "value:WDOGVALUE"
    "control:WDOGCONTROL"
    "interrupt clear:WDOGINTCLR"
    "raw interrupt status:WDOGRIS"
    "interrupt status:WDOGMIS"
    "lock:WDOGLOCK"
    "integration test control:WDOGITCR"
    "integration test output set:WDOGITOP"
)

TOTAL=${#REGISTERS[@]}

for ((i=0; i<TOTAL; i++)); do
    IFS=':' read -r REG_NAME REG_SHORT <<< "${REGISTERS[$i]}"
    TASK_NUM=$((i+1))
    CHANGE_ID="implement-watchdog ${REG_NAME}"
    
    echo -e "${GREEN}╔════════════════════════════════════════${NC}"
    echo -e "${GREEN}║ Register ${TASK_NUM}/${TOTAL}: ${REG_SHORT}${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════${NC}"
    echo ""
    
    # Check if change proposal exists
    if [ ! -d "openspec/changes/${CHANGE_ID}" ]; then
        echo -e "${YELLOW}⚠️  Change proposal not found, skipping...${NC}"
        continue
    fi
    
    echo -e "${BLUE}📝 Change: ${CHANGE_ID}${NC}"
    echo -e "${BLUE}📂 Proposal: openspec/changes/${CHANGE_ID}/${NC}"
    echo ""
    
    # Show the proposal summary
    if [ -f "openspec/changes/${CHANGE_ID}/proposal.md" ]; then
        echo -e "${BLUE}Proposal Summary:${NC}"
        head -20 "openspec/changes/${CHANGE_ID}/proposal.md" | grep -E "^#|^-|^Register" | head -10
        echo ""
    fi
    
    # Show the tasks
    if [ -f "openspec/changes/${CHANGE_ID}/tasks.md" ]; then
        echo -e "${BLUE}Tasks to Complete:${NC}"
        grep -E "^- \[.\]" "openspec/changes/${CHANGE_ID}/tasks.md" | head -10
        echo ""
    fi
    
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  Ready to implement ${REG_SHORT}${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo ""
    echo "This will:"
    echo "  1. Review: openspec/changes/${CHANGE_ID}/proposal.md"
    echo "  2. Review: openspec/changes/${CHANGE_ID}/tasks.md"
    echo "  3. Modify: modules/demo_watchdog/demo_watchdog.dml"
    echo "  4. Create tests"
    echo "  5. Validate implementation"
    echo ""
    read -p "$(echo -e ${GREEN}Proceed with ${REG_SHORT} implementation? [Y/n]: ${NC})" -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        echo -e "${YELLOW}Skipping ${REG_SHORT}...${NC}"
        echo ""
        continue
    fi
    
    # Create implementation prompt
    PROMPT="I'm implementing the ${REG_SHORT} register for a Simics DDM watchdog device.

Please help me complete this implementation:

1. First, review the change proposal:
   - Read: openspec/changes/${CHANGE_ID}/proposal.md
   - Read: openspec/changes/${CHANGE_ID}/tasks.md

2. Then review the current implementation:
   - Read: modules/demo_watchdog/demo_watchdog.dml
   - Read: wdt.md (hardware specification)

3. Implement the ${REG_SHORT} register:
   - Add register definition in DML
   - Implement read/write methods
   - Add proper field handling
   - Handle side effects

4. Create comprehensive tests:
   - Test read/write operations
   - Test field behavior
   - Test side effects
   - Test reset values

5. Validate:
   - Check all tasks in tasks.md are complete
   - Ensure code follows DML 1.4 best practices
   - Add logging where appropriate

When you've completed ALL tasks for ${REG_SHORT}, respond with 'REGISTER IMPLEMENTATION COMPLETE'.

Let's start!"
    
    echo -e "${BLUE}🤖 Launching ADK agent with OpenSpec MCP server...${NC}"
    echo ""
    
    # Save prompt to file for reference
    PROMPT_FILE="/tmp/openspec_prompt_${REG_SHORT}.txt"
    echo "$PROMPT" > "$PROMPT_FILE"
    
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  Manual Implementation Required${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo ""
    echo "The OpenSpec project is already initialized."
    echo "To implement this register, you have two options:"
    echo ""
    echo "Option 1: Use your AI editor (Cursor, VSCode with Copilot, etc.)"
    echo "  1. Open: modules/demo_watchdog/demo_watchdog.dml"
    echo "  2. Review: openspec/changes/${CHANGE_ID}/proposal.md"
    echo "  3. Review: openspec/changes/${CHANGE_ID}/tasks.md"
    echo "  4. Implement the register based on the proposal"
    echo ""
    echo "Option 2: Use OpenSpec with manual AI agent"
    echo "  1. Start your AI tool (Cursor AI, Claude Desktop, etc.)"
    echo "  2. Give it this prompt:"
    echo "     \"Review openspec/changes/${CHANGE_ID}/ and implement\""
    echo "     \"the ${REG_SHORT} register in modules/demo_watchdog/demo_watchdog.dml\""
    echo ""
    echo "Prompt saved to: $PROMPT_FILE"
    echo "You can also read it with: cat $PROMPT_FILE"
    echo ""
    
    # Wait for user to complete implementation
    read -p "$(echo -e ${GREEN}Press Enter when you have completed the ${REG_SHORT} implementation...${NC})"
    
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  ${REG_SHORT} Implementation Complete${NC}"
    echo -e "${YELLOW}════════════════════════════════════════${NC}"
    echo ""
    
    # Ask if should archive
    read -p "$(echo -e ${GREEN}Archive this change? [Y/n]: ${NC})" -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo -e "${BLUE}📦 Archiving ${CHANGE_ID}...${NC}"
        source "$OPENSPEC_VENV/bin/activate"
        openspec archive "${CHANGE_ID}" --yes || {
            echo -e "${YELLOW}⚠️  Archive may have warnings (normal)${NC}"
        }
        
        echo -e "${BLUE}💾 Committing to Git...${NC}"
        git add .
        git commit -m "✅ Implemented ${REG_SHORT} register

Change: ${CHANGE_ID}
Completed register implementation with tests.
" || echo "No changes to commit"
        
        echo -e "${GREEN}✅ ${REG_SHORT} archived and committed${NC}"
    fi
    
    echo ""
    echo ""
    sleep 2
done

echo ""
echo -e "${GREEN}╔════════════════════════════════════════${NC}"
echo -e "${GREEN}║  🎉 All Registers Processed!${NC}"
echo -e "${GREEN}╚════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo "  1. Review changes: git log --oneline"
echo "  2. Run tests: make test"
echo "  3. Build module: make"
echo "  4. Test in Simics"
echo ""
