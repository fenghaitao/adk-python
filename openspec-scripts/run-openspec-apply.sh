#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}
CHANGE_ID=${2:-implement-wdt-initial}
MODE=${3:-standard}  # standard or optimize

# Colors
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
NC="\033[0m"

case "$MODE" in
    "optimize")
        echo -e "${BLUE}🧠 Running DeepEval PromptOptimizer mode${NC}"
        echo -e "${YELLOW}This will collect historical sessions and optimize instructions${NC}"
        
        # Create optimization directory
        OPTIMIZATION_DIR="$WORKDIR/.openspec-optimization"
        mkdir -p "$OPTIMIZATION_DIR"
        
        # Step 1: Collect historical session data
        echo -e "${BLUE}📊 Step 1: Collecting historical session data...${NC}"
        python3 "$ADK_ROOT/deepeval-scoring/collect_session_data.py" \
            --workdir "$WORKDIR" \
            --output "$OPTIMIZATION_DIR/historical_sessions.json" \
            --min-score 0.5 \
            --model iflow/qwen3-coder-plus
        
        if [[ $? -ne 0 ]]; then
            echo -e "${YELLOW}⚠️  Failed to collect session data${NC}"
            echo -e "${YELLOW}   Make sure you have at least 10 historical sessions${NC}"
            exit 1
        fi
        
        # Step 2: Run optimizer
        echo -e "${BLUE}🔧 Step 2: Running PromptOptimizer...${NC}"
        python3 "$ADK_ROOT/deepeval-scoring/optimize_instructions.py" \
            --historical-data "$OPTIMIZATION_DIR/historical_sessions.json" \
            --current-instructions "$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md" \
            --output "$OPTIMIZATION_DIR/optimized_instructions.md" \
            --algorithm miprov2 \
            --iterations 5 \
            --model iflow/qwen3-coder-plus
        
        if [[ $? -ne 0 ]]; then
            echo -e "${YELLOW}⚠️  Optimization failed${NC}"
            exit 1
        fi
        
        # Step 3: Backup and deploy optimized instructions
        echo -e "${BLUE}💾 Step 3: Deploying optimized instructions...${NC}"
        INSTRUCTIONS_FILE="$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md"
        cp "$INSTRUCTIONS_FILE" "$INSTRUCTIONS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$OPTIMIZATION_DIR/optimized_instructions.md" "$INSTRUCTIONS_FILE"
        
        echo -e "${GREEN}✅ Optimization complete!${NC}"
        echo -e "${GREEN}   Optimized instructions deployed${NC}"
        echo -e "${GREEN}   Backup saved: $INSTRUCTIONS_FILE.backup.*${NC}"
        echo ""
        echo -e "${BLUE}💡 Next steps:${NC}"
        echo -e "   1. Test with: ./run-openspec-apply.sh $WORKDIR <new-change-id> standard"
        echo -e "   2. Score result: cd deepeval-scoring && python score.py --workdir $WORKDIR --device <device>"
        echo -e "   3. Compare with historical average to measure improvement"
        ;;
        
    "standard"|*)
        # Standard mode: just run the agent
        $ADK_ROOT/openspec-scripts/run_openspec_subagents.sh \
          --workdir $WORKDIR \
          --port 8056 \
          --apply \
          --change-id $CHANGE_ID \
          --model iflow/qwen3-coder-plus
        ;;
esac
