#!/bin/bash

# Run the ScoreAgent using GitHub Copilot CLI
#
# This script evaluates the quality of apply_agent implementations using
# the GitHub Copilot CLI with a custom score agent. It analyzes:
# 1. Code Quality (90 points): Build success, test results, DML/test code quality
# 2. Agent Behavior (90 points): Documentation reading, efficiency, time
#
# Usage examples:
#   ./run-copilot-score.sh adk_openspec_project wdt
#   ./run-copilot-score.sh /path/to/project wdt
#

set -e

# Source common configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common-config.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validate arguments
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo "Usage: $0 <workdir> <device_name> [change_id]"
    echo ""
    echo "Arguments:"
    echo "  workdir      Working directory containing the OpenSpec project"
    echo "  device_name  Name of the device to evaluate (e.g., wdt)"
    echo "  change_id    Optional change identifier (default: auto-detect from openspec list)"
    echo ""
    echo "Examples:"
    echo "  $0 adk_openspec_project wdt"
    echo "  $0 /path/to/project wdt 001_add-wdt-registers"
    exit 1
fi

WORKDIR="$1"
DEVICE_NAME="$2"
CHANGE_ID="${3:-}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}OpenSpec Score Agent (Copilot CLI)${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Working directory: $WORKDIR"
echo "Device Name: $DEVICE_NAME"
if [ -n "$CHANGE_ID" ]; then
    echo "Change ID: $CHANGE_ID"
else
    echo "Change ID: (will auto-detect)"
fi
echo ""

# Validate working directory exists
if [ ! -d "$WORKDIR" ]; then
    echo -e "${RED}❌ Error: Working directory not found: $WORKDIR${NC}"
    exit 1
fi

# Change to working directory
cd "$WORKDIR"
WORKDIR="$(pwd)"

echo -e "${BLUE}Step 1: Validating project structure...${NC}"

# Check for required directories
REQUIRED_DIRS=(
    "simics-project/modules/${DEVICE_NAME}"
    "openspec/changes"
)

for DIR in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$DIR" ]; then
        echo -e "${RED}❌ Required directory not found: $DIR${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Project structure validated${NC}"
echo ""

# Auto-detect change ID if not provided
if [ -z "$CHANGE_ID" ]; then
    echo -e "${BLUE}Step 2: Auto-detecting change ID...${NC}"
    
    # Get the most recent change directory
    LATEST_CHANGE=$(ls -1dt openspec/changes/*/ 2>/dev/null | head -1)
    
    if [ -n "$LATEST_CHANGE" ]; then
        CHANGE_ID=$(basename "$LATEST_CHANGE")
        echo -e "${GREEN}✅ Detected change ID: $CHANGE_ID${NC}"
    else
        echo -e "${YELLOW}⚠️  No changes found in openspec/changes/${NC}"
        echo -e "${YELLOW}   Will proceed with basic evaluation${NC}"
        CHANGE_ID="evaluation"
    fi
    echo ""
else
    echo -e "${BLUE}Step 2: Using provided change ID: $CHANGE_ID${NC}"
    echo ""
fi

# Check for apply agent session files
APPLY_AGENT_DIR="adk_openspec_apply_agent"
APPLY_AGENT_SESSION_FOUND=false

# First, check if adk_openspec_apply_agent directory exists with session files
if [ -d "$APPLY_AGENT_DIR" ]; then
    SESSION_COUNT=$(ls -1 "$APPLY_AGENT_DIR"/*.session.txt 2>/dev/null | wc -l)
    if [ "$SESSION_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $SESSION_COUNT session file(s) in $APPLY_AGENT_DIR${NC}"
        APPLY_AGENT_SESSION_FOUND=true
        echo ""
    fi
fi

# If not found, check for log/session-*.log files and extract apply agent session
if [ "$APPLY_AGENT_SESSION_FOUND" = false ]; then
    echo -e "${BLUE}Checking for apply agent logs in log/session-*.log files...${NC}"
    
    if [ -d "log" ]; then
        # Find apply agent log file by checking for the pattern
        APPLY_AGENT_LOG=""
        for LOG_FILE in log/session-*.log; do
            if [ -f "$LOG_FILE" ]; then
                # Check if this log contains the apply agent pattern
                # Use a simple pattern that works with JSON across newlines
                if grep -q '"/apply --id' "$LOG_FILE" 2>/dev/null; then
                    APPLY_AGENT_LOG="$LOG_FILE"
                    echo -e "${GREEN}✅ Found apply agent log: $LOG_FILE${NC}"
                    break
                fi
            fi
        done
        
        # If found, extract the session file
        if [ -n "$APPLY_AGENT_LOG" ]; then
            # Create the apply agent directory
            mkdir -p "$APPLY_AGENT_DIR"
            
            # Use view_copilot_session.py to extract the session
            VIEW_SESSION_SCRIPT="$SCRIPT_DIR/../openspec-copilot/view_copilot_session.py"
            OUTPUT_SESSION="$APPLY_AGENT_DIR/apply_agent.session.txt"
            
            if [ -f "$VIEW_SESSION_SCRIPT" ]; then
                echo -e "${BLUE}Extracting apply agent session...${NC}"
                python3 "$VIEW_SESSION_SCRIPT" "$APPLY_AGENT_LOG" -o "$OUTPUT_SESSION" 2>/dev/null
                
                if [ -f "$OUTPUT_SESSION" ]; then
                    echo -e "${GREEN}✅ Extracted session to: $OUTPUT_SESSION${NC}"
                    APPLY_AGENT_SESSION_FOUND=true
                else
                    echo -e "${YELLOW}⚠️  Failed to extract session from $APPLY_AGENT_LOG${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Session extraction script not found: $VIEW_SESSION_SCRIPT${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️  No apply agent logs found in log/ directory${NC}"
        fi
    fi
fi

# Report final status
if [ "$APPLY_AGENT_SESSION_FOUND" = false ]; then
    echo -e "${YELLOW}⚠️  No apply agent session files available${NC}"
    echo -e "${YELLOW}   Agent behavior scoring will not be available${NC}"
    echo -e "${YELLOW}   Only code quality will be evaluated${NC}"
fi
echo ""

# Step 3: Setup score agent file
echo -e "${BLUE}Step 3: Setting up score agent...${NC}"
mkdir -p .github/agents

# Create openspec_score.agent.md
cat > .github/agents/openspec_score.agent.md << 'EOF'
---
name: OpenSpec-Score
description: Evaluate apply_agent implementation quality - analyzes code quality and agent behavior
---

EOF

# Append the score agent instruction
SCORE_INSTRUCTION="$SCRIPT_DIR/../contributing/samples/openspec_integration/score_agent_instruction.md"
if [ -f "$SCORE_INSTRUCTION" ]; then
    cat "$SCORE_INSTRUCTION" >> .github/agents/openspec_score.agent.md
    echo -e "${GREEN}✅ Score agent configuration created${NC}"
else
    echo -e "${RED}❌ Score agent instruction not found: $SCORE_INSTRUCTION${NC}"
    exit 1
fi
echo ""

# Step 4: Run score agent with Copilot CLI
echo -e "${BLUE}Step 4: Running score agent evaluation...${NC}"
echo -e "${BLUE}This may take several minutes depending on project size${NC}"
echo ""

# Build the scoring prompt
SCORE_PROMPT="/score Please evaluate the apply_agent implementation for device '$DEVICE_NAME' in working directory '$WORKDIR'. Follow all steps in your instructions carefully."

echo "   Prompt: $SCORE_PROMPT"
echo ""

# Create log directory if it doesn't exist
mkdir -p log

# Run copilot with the score agent
SCORE_LOG="log/score_agent_$(date +%Y%m%d_%H%M%S).log"

set +e
copilot --allow-all-tools --agent openspec_score --log-dir ./log --log-level debug -p "$SCORE_PROMPT" 2>&1 | tee "$SCORE_LOG"
SCORE_EXIT_CODE=$?
set -e

echo ""

# Step 5: Check results
echo -e "${BLUE}Step 5: Checking evaluation results...${NC}"

if [ -f "score.md" ]; then
    echo -e "${GREEN}✅ Score report generated: $WORKDIR/score.md${NC}"
    echo ""
    
    # Extract and display key metrics
    if grep -q "Overall Score:" score.md; then
        echo -e "${BLUE}=== Evaluation Summary ===${NC}"
        grep "Overall Score:" score.md || true
        grep "Code Quality Score:" score.md || true
        grep "Agent Behavior Score:" score.md || true
        grep "Grade:" score.md | head -1 || true
        echo ""
    fi
    
    # Display key strengths and weaknesses
    if grep -q "Key Strengths:" score.md; then
        echo -e "${GREEN}Key Strengths:${NC}"
        sed -n '/^### Strengths/,/^###/{/^###/!p;}' score.md | head -10 || true
        echo ""
    fi
    
    if grep -q "Weaknesses" score.md; then
        echo -e "${YELLOW}Areas for Improvement:${NC}"
        sed -n '/^### Weaknesses/,/^###/{/^###/!p;}' score.md | head -10 || true
        echo ""
    fi
else
    echo -e "${YELLOW}⚠️  Score report not found at $WORKDIR/score.md${NC}"
    echo -e "${YELLOW}   Check the log for details: $SCORE_LOG${NC}"
fi

# Check if score agent completed successfully
if [ $SCORE_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Score agent completed successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Score agent completed with warnings (exit code: $SCORE_EXIT_CODE)${NC}"
fi

echo ""
echo -e "${BLUE}Score agent log saved: $SCORE_LOG${NC}"
echo ""

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Score Agent Evaluation Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Summary:"
echo "  • Evaluated device: $DEVICE_NAME"
echo "  • Change ID: $CHANGE_ID"
if [ -f "score.md" ]; then
    echo "  • Full report: $WORKDIR/score.md"
fi
echo "  • Execution log: $SCORE_LOG"
echo ""
echo "Next steps:"
echo "  1. Review the full score report: cat score.md"
echo "  2. Address any identified weaknesses"
echo "  3. Re-run apply agent if needed to improve score"
echo "  4. Iterate until quality targets are met"
echo ""

# Display final score if available
if [ -f "score.md" ] && grep -q "Overall Score:" score.md; then
    OVERALL_SCORE=$(grep "Overall Score:" score.md | head -1)
    echo -e "${BLUE}Final Result:${NC}"
    echo "  $OVERALL_SCORE"
    echo ""
fi
