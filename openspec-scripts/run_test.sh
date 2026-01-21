#!/bin/bash

set -e

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Function to execute a command with logging and timing
# Usage: run_cmd_with_timing "command string" "log_file"
run_cmd_with_timing() {
    local cmd="$1"
    local log_file="$2"

    echo "Command: $cmd" | tee -a "$log_file"
    start_time=$(date +%s)
    
    # Execute command and capture exit code
    if eval "$cmd 2>&1" | tee -a "$log_file"; then
        end_time=$(date +%s)
        elapsed=$((end_time - start_time))
        echo "Completed in $elapsed seconds" | tee -a "$log_file"
    else
        exit_code=$?
        end_time=$(date +%s)
        elapsed=$((end_time - start_time))
        echo "Failed after $elapsed seconds with exit code $exit_code" | tee -a "$log_file"
        exit 1
    fi
}

# Parse command line arguments with smart defaults
# Usage:
#   ./run_test.sh proj_dir                          # 1 arg:  proj_dir (stages: 0,1)
#   ./run_test.sh proj_dir stages                   # 2 args: proj_dir stages
#   ./run_test.sh model proj_dir stages             # 3 args: model proj_dir stages
#   ./run_test.sh mcp_port model proj_dir stages    # 4 args: mcp_port model proj_dir stages
#
# stages format: comma or space separated stage numbers
#   Examples: "0", "1", "0,1", "1,0", "0 1", "0,1,2", "2"
#   Stage 0 = bootstrap project
#   Stage 1 = proposal initialization
#   Stage 2 = prompt optimization (DeepEval) + git commit
#
# Environment variables for Stage 2:
#   SKIP_COLLECT=1       - Skip session data collection (deprecated, use SKIP_OPTIMIZE instead)
#   SKIP_OPTIMIZE=1      - Skip optimization step
#   FORCE_OPTIMIZE=1     - Force optimization even with insufficient sessions
#   FORCE_RECOLLECT=1    - Force recollection (deprecated with new directory-based approach)
#   MIN_SESSIONS=N       - Set minimum session threshold (default: 5)
#   MAX_CONCURRENT=N     - Set max concurrent API calls (default: 1)
#   THROTTLE_SECONDS=N   - Set throttle delay between batches (default: 30.0)
#   EXTRA_WORKDIRS       - Path to directory containing multiple project folders for optimization
#                          Example: EXTRA_WORKDIRS="/path/to/data"
#                          The directory should contain folders like wdt_dbg132, wdt_dbg134, etc.
#                          Each folder must have an adk_openspec_project subdirectory
#                          If not set, uses parent directory of current project
#   ENABLE_MLFLOW=1      - Enable MLflow tracking for collection and optimization
#   SCORING_MODE         - Scoring mode: llm, deterministic, or hybrid (default: llm)
#   AGENT_TYPE           - Agent type for behavior evaluation (e.g., adk-python, kiro-cli, rovodev, copilot-cli)
#   REFERENCE_DIR        - Directory containing golden reference implementation for comparison

if [ $# -eq 1 ]; then
    # 1 argument: proj_dir
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="$1"
    stages="0,1"
elif [ $# -eq 2 ]; then
    # 2 arguments: proj_dir stages
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="$1"
    stages="$2"
elif [ $# -eq 3 ]; then
    # 3 arguments: model proj_dir stages
    mcp_server_port=8051
    model="$1"
    proj_dir="$2"
    stages="$3"
elif [ $# -ge 4 ]; then
    # 4 arguments: mcp_port model proj_dir stages
    mcp_server_port="$1"
    model="$2"
    proj_dir="$3"
    stages="$4"
else
    # No arguments: use all defaults
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="wdt_test"
    stages="0,1"
fi

# Set the model for Spec-Kit (Specify agent) to match OpenSpec model
export SPEC_KIT_MODEL="$model"

echo "Parameters:"
echo "  MCP Server Port: $mcp_server_port"
echo "  Model: $model"
echo "  Project Directory: $proj_dir"
echo "  Stages: $stages"
echo ""

# Use current working directory + project directory name
proj_dir_abs="$(pwd)/$proj_dir"
log_dir="$proj_dir_abs"

# Create project directory if it doesn't exist
if [ ! -d "$proj_dir_abs" ]; then
    echo "Creating directory: $proj_dir_abs"
    mkdir -p "$proj_dir_abs"
else
    echo "Using existing directory: $proj_dir_abs"
fi
echo ""

# Parse stages into array for robust checking
# Handles: "0", "1", "0,1", "1,0", "0 1", etc.
IFS=',' read -ra STAGE_ARRAY <<< "$stages"
declare -A run_stage
for stage in "${STAGE_ARRAY[@]}"; do
    # Trim whitespace and store
    stage_clean=$(echo "$stage" | tr -d ' ')
    run_stage[$stage_clean]=1
done

# Execute stages based on parsed input
if [[ "${run_stage[0]}" == "1" ]]; then
    echo "=== Stage 0: bootstrap ===" | tee "$log_dir/${proj_dir}.0.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir}.0.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/run_openspec.sh adk_openspec_project --model $model --port $mcp_server_port" "$log_dir/${proj_dir}.0.log"
fi

if [[ "${run_stage[1]}" == "1" ]]; then
    echo "=== Stage 1: proposal initialization ===" | tee "$log_dir/${proj_dir}.1.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir}.1.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh --workdir adk_openspec_project --proposal $ADK_ROOT/openspec-prompts/proposal-wdt.md --agent initial --port $mcp_server_port --apply --archive --model $model" "$log_dir/${proj_dir}.1.log"
fi

if [[ "${run_stage[2]}" == "1" ]]; then
    echo "=== Stage 2: prompt optimization ===" | tee "$log_dir/${proj_dir}.2.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir}.2.log"
    echo "This will collect historical sessions and optimize instructions" | tee -a "$log_dir/${proj_dir}.2.log"
    
    cd "$proj_dir_abs"
    
    # Create optimization directory with absolute path
    OPTIMIZATION_DIR="$proj_dir_abs/adk_openspec_project/.openspec-optimization"
    mkdir -p "$OPTIMIZATION_DIR"
    
    # Check for required dependencies
    echo "Checking dependencies..." | tee -a "$log_dir/${proj_dir}.2.log"
    if ! python3 -c "import deepeval" 2>/dev/null; then
        echo "❌ Error: deepeval module not found" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Please install it with: pip install deepeval" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
        exit 0  # Don't fail the entire pipeline, just skip this stage
    fi
    
    # Step 2: Run optimizer
    echo "Step 2: Running PromptOptimizer..." | tee -a "$log_dir/${proj_dir}.2.log"
    
    # Check if optimization should be skipped
    if [[ "${SKIP_OPTIMIZE:-0}" == "1" ]]; then
        echo "⚠️  Skipping optimization (SKIP_OPTIMIZE=1)" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "✅ Stage 2 session data collection complete!" | tee -a "$log_dir/${proj_dir}.2.log"
        cd "$proj_dir_abs"
        exit 0
    fi
    
    # Rate limiting configuration (can be overridden with environment variables)
    MAX_CONCURRENT="${MAX_CONCURRENT:-1}"
    THROTTLE_SECONDS="${THROTTLE_SECONDS:-30.0}"
    
    echo "⏱️  Rate limiting: max_concurrent=$MAX_CONCURRENT, throttle=${THROTTLE_SECONDS}s" | tee -a "$log_dir/${proj_dir}.2.log"
    
    # Enable MLflow tracking if requested
    MLFLOW_ARGS=""
    if [[ "${ENABLE_MLFLOW:-0}" == "1" ]]; then
        echo "🔬 MLflow tracking enabled for optimization" | tee -a "$log_dir/${proj_dir}.2.log"
        MLFLOW_ARGS="--mlflow"
    fi
    
    # Determine historical data path
    # If EXTRA_WORKDIRS is set, use it as the data path containing multiple projects
    # Otherwise use current working directory (parent of current project)
    if [[ -n "${EXTRA_WORKDIRS:-}" ]]; then
        # Use EXTRA_WORKDIRS as the directory containing all project folders
        HISTORICAL_DATA_PATH="$EXTRA_WORKDIRS"
        echo "📁 Using EXTRA_WORKDIRS for multi-project optimization: $HISTORICAL_DATA_PATH" | tee -a "$log_dir/${proj_dir}.2.log"
    else
        # Single project mode - use parent directory which should contain multiple test runs
        HISTORICAL_DATA_PATH="$(dirname "$(pwd)")"
        echo "📁 Using parent directory for optimization: $HISTORICAL_DATA_PATH" | tee -a "$log_dir/${proj_dir}.2.log"
    fi
    
    # Set scoring mode (default: llm)
    SCORING_MODE="${SCORING_MODE:-llm}"
    echo "📊 Scoring mode: $SCORING_MODE" | tee -a "$log_dir/${proj_dir}.2.log"
    
    # Set agent type (default: adk-python)
    AGENT_TYPE="${AGENT_TYPE:-adk-python}"
    echo "🤖 Agent type: $AGENT_TYPE" | tee -a "$log_dir/${proj_dir}.2.log"
    
    # Set reference directory for golden comparison if specified
    REFERENCE_ARGS=""
    if [[ -n "${REFERENCE_DIR:-}" ]]; then
        if [[ -d "$REFERENCE_DIR" ]]; then
            echo "📚 Reference directory: $REFERENCE_DIR" | tee -a "$log_dir/${proj_dir}.2.log"
            REFERENCE_ARGS="--reference-dir $REFERENCE_DIR"
        else
            echo "⚠️  Warning: REFERENCE_DIR not found: $REFERENCE_DIR" | tee -a "$log_dir/${proj_dir}.2.log"
        fi
    fi
    
    set +e
    python3 "$ADK_ROOT/deepeval-scoring/optimize_instructions.py" \
        --historical-data "$HISTORICAL_DATA_PATH" \
        --current-instructions "$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md" \
        --output "$OPTIMIZATION_DIR/optimized_instructions.md" \
        --algorithm copro \
        --iterations 5 \
        --max-concurrent "$MAX_CONCURRENT" \
        --throttle-seconds "$THROTTLE_SECONDS" \
        --model "$model" \
        --scoring-mode "$SCORING_MODE" \
        --agent "$AGENT_TYPE" \
        --no-async \
        --use-custom-scorer \
        $REFERENCE_ARGS \
        $MLFLOW_ARGS 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
    optimize_exit_code=$?
    set -e
    
    if [[ $optimize_exit_code -ne 0 ]]; then
        echo "❌ Optimization failed (exit code: $optimize_exit_code)" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
        exit 0
    fi
    
    # Verify optimized file was created
    if [[ ! -f "$OPTIMIZATION_DIR/optimized_instructions.md" ]]; then
        echo "❌ Optimized instructions file not created" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
        exit 0
    fi
    
    # Step 3: Backup and deploy optimized instructions
    echo "Step 3: Deploying optimized instructions..." | tee -a "$log_dir/${proj_dir}.2.log"
    INSTRUCTIONS_FILE="$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md"
    BACKUP_FILE="$INSTRUCTIONS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    cp "$INSTRUCTIONS_FILE" "$BACKUP_FILE"
    cp "$OPTIMIZATION_DIR/optimized_instructions.md" "$INSTRUCTIONS_FILE"
    
    echo "✅ Optimized instructions deployed" | tee -a "$log_dir/${proj_dir}.2.log"
    echo "   Backup saved: $BACKUP_FILE" | tee -a "$log_dir/${proj_dir}.2.log"
    
    # Step 4: Commit to git repository
    echo "Step 4: Committing optimized instructions to git..." | tee -a "$log_dir/${proj_dir}.2.log"
    cd "$ADK_ROOT"
    
    # Verify we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "⚠️  Not in a git repository, skipping commit" | tee -a "$log_dir/${proj_dir}.2.log"
        cd "$proj_dir_abs"
        echo "✅ Stage 2 optimization complete (no git commit)" | tee -a "$log_dir/${proj_dir}.2.log"
        exit 0
    fi
    
    # Check if there are changes to commit
    if git diff --quiet "$INSTRUCTIONS_FILE"; then
        echo "ℹ️  No changes detected in instructions file, skipping commit" | tee -a "$log_dir/${proj_dir}.2.log"
    else
        # Get optimization metrics for commit message
        OPTIMIZATION_DATE=$(date +"%Y-%m-%d %H:%M:%S")
        # Count project folders in HISTORICAL_DATA_PATH
        HISTORICAL_SESSIONS=$(find "$HISTORICAL_DATA_PATH" -maxdepth 2 -type d -name "adk_openspec_project" 2>/dev/null | wc -l || echo "unknown")
        
        # Stage the optimized instructions file
        git add "$INSTRUCTIONS_FILE" 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
        
        # Create detailed commit message
        set +e
        git commit -m "refactor(openspec): optimize apply agent instructions via DeepEval

- Optimized apply_agent_instruction.md using PromptOptimizer (copro)
- Based on $HISTORICAL_SESSIONS historical project folders from $HISTORICAL_DATA_PATH
- Optimization date: $OPTIMIZATION_DATE
- Model used: $model
- Algorithm: copro with 5 iterations
- Backup saved: $(basename $BACKUP_FILE)

This optimization aims to improve agent performance based on historical
project data and automated prompt engineering techniques." 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
        commit_exit_code=$?
        set -e
        
        if [[ $commit_exit_code -eq 0 ]]; then
            COMMIT_HASH=$(git rev-parse --short HEAD)
            echo "✅ Successfully committed optimized instructions: $COMMIT_HASH" | tee -a "$log_dir/${proj_dir}.2.log"
        else
            echo "⚠️  Warning: Failed to commit changes (exit code: $commit_exit_code)" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "   Optimized instructions were deployed but not committed to git" | tee -a "$log_dir/${proj_dir}.2.log"
            # Don't exit with error - optimization was still successful
        fi
    fi
    
    cd "$proj_dir_abs"
    echo "✅ Stage 2 optimization complete!" | tee -a "$log_dir/${proj_dir}.2.log"
fi
