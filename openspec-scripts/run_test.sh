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
#   ./run_test.sh proj_dir                          # 1 arg:  proj_dir (stages: 0,1,2,3)
#   ./run_test.sh proj_dir stages                   # 2 args: proj_dir stages
#   ./run_test.sh model proj_dir stages             # 3 args: model proj_dir stages
#   ./run_test.sh mcp_port model proj_dir stages    # 4 args: mcp_port model proj_dir stages
#
# stages format: comma or space separated stage numbers
#   Examples: "0", "1", "0,1", "1,0", "0 1", "0,1,2,3", "4"
#   Stage 0 = bootstrap project
#   Stage 1 = proposal generation (--proposal)
#   Stage 2 = apply changes (--apply)
#   Stage 3 = archive session (--archive)
#   Stage 4 = prompt optimization (DeepEval) + git commit
#
# Environment variables for Stage 4:
#   SKIP_OPTIMIZE=1      - Skip optimization step
#   GOLDENS_PATH         - Path to goldens directory (goldens/item1, goldens/item2, ...)
#   ACTUAL_OUT_PATH      - Path to actual outputs directory (default: optimization_dir/actual_out)
#   ENABLE_MLFLOW=1      - Enable MLflow tracking for collection and optimization
#   ENABLE_PROF=1        - Enable cProfile performance profiling
#   ENABLE_CHKP=1        - Enable checkpoints in COPRO algorithm (waits for user confirmation at key points)
#   SCORING_MODE         - Scoring mode: llm, deterministic, or hybrid (default: llm)
#   AGENT_TYPE           - Agent type for behavior evaluation (e.g., adk-python, kiro-cli, rovodev, copilot-cli)
#   REFERENCE_DIR        - Directory containing golden reference implementation for comparison

if [ $# -eq 1 ]; then
    # 1 argument: proj_dir
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="$1"
    stages="0,1,2,3"
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
    stages="0,1,2,3"
fi

# Set the model for Spec-Kit (Specify agent) to match OpenSpec model
export SPEC_KIT_MODEL="$model"

echo "Parameters:"
echo "  MCP Server Port: $mcp_server_port"
echo "  Model: $model"
echo "  Project Directory: $proj_dir"
echo "  Stages: $stages"
echo ""

# Handle both absolute and relative paths for proj_dir
if [[ "$proj_dir" = /* ]]; then
    # Absolute path - use as is
    proj_dir_abs="$proj_dir"
    # Extract just the directory name for log file naming
    proj_dir_name="$(basename "$proj_dir")"
else
    # Relative path - prepend current working directory
    proj_dir_abs="$(pwd)/$proj_dir"
    proj_dir_name="$proj_dir"
fi
log_dir="$proj_dir_abs"
device_name="wdt"

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
    echo "=== Stage 0: bootstrap ===" | tee "$log_dir/${proj_dir_name}.0.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir_name}.0.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/run_openspec.sh adk_openspec_project --device $device_name --model $model --port $mcp_server_port" "$log_dir/${proj_dir_name}.0.log"
fi

if [[ "${run_stage[1]}" == "1" ]]; then
    echo "=== Stage 1: proposal generation ===" | tee "$log_dir/${proj_dir_name}.1.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir_name}.1.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh --workdir adk_openspec_project --proposal $ADK_ROOT/openspec-prompts/proposal-wdt.md --agent initial --port $mcp_server_port --model $model" "$log_dir/${proj_dir_name}.1.log"
fi

if [[ "${run_stage[2]}" == "1" ]]; then
    echo "=== Stage 2: apply changes ===" | tee "$log_dir/${proj_dir_name}.2.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir_name}.2.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh --workdir adk_openspec_project --agent initial --port $mcp_server_port --apply --model $model" "$log_dir/${proj_dir_name}.2.log"
fi

if [[ "${run_stage[3]}" == "1" ]]; then
    echo "=== Stage 3: archive session ===" | tee "$log_dir/${proj_dir_name}.3.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir_name}.3.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh --workdir adk_openspec_project --agent initial --port $mcp_server_port --archive --model $model" "$log_dir/${proj_dir_name}.3.log"
fi

if [[ "${run_stage[4]}" == "1" ]]; then
    echo "=== Stage 4: prompt optimization ===" | tee "$log_dir/${proj_dir_name}.4.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir_name}.4.log"
    echo "This will collect historical sessions and optimize instructions" | tee -a "$log_dir/${proj_dir_name}.4.log"
    
    # Start timing for stage 4
    stage4_start_time=$(date +%s)
    
    cd "$proj_dir_abs"
    
    # Create optimization directory with absolute path
    OPTIMIZATION_DIR="$proj_dir_abs/adk_openspec_project/.openspec-optimization"
    mkdir -p "$OPTIMIZATION_DIR"
    
    # Check for required dependencies
    echo "Step 1: Checking dependencies..." | tee -a "$log_dir/${proj_dir_name}.4.log"
    if ! python3 -c "import deepeval" 2>/dev/null; then
        echo "❌ Error: deepeval module not found" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "Please install it with: pip install deepeval" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "Skipping stage 4 optimization" | tee -a "$log_dir/${proj_dir_name}.4.log"
        exit 0  # Don't fail the entire pipeline, just skip this stage
    fi
    
    # Step 2: Run optimizer
    echo "Step 2: Running PromptOptimizer..." | tee -a "$log_dir/${proj_dir_name}.4.log"

    # Check if optimization should be skipped
    if [[ "${SKIP_OPTIMIZE:-0}" == "1" ]]; then
        echo "⚠️  Skipping optimization (SKIP_OPTIMIZE=1)" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "✅ Stage 4 session data collection complete!" | tee -a "$log_dir/${proj_dir_name}.4.log"
        cd "$proj_dir_abs"
        exit 0
    fi
    
    # Setup py-spy profiling if enabled
    PYSPY_CMD=""
    PYSPY_OUTPUT=""
    if [[ "${ENABLE_PROF:-0}" == "1" ]]; then
        PYSPY_OUTPUT="$OPTIMIZATION_DIR/profile.json"
        PYSPY_CMD="sudo -E $ADK_ROOT/.venv/bin/py-spy record -o $PYSPY_OUTPUT --"
        echo "📊 py-spy profiling enabled" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "   Profile data will be saved to: $PYSPY_OUTPUT" | tee -a "$log_dir/${proj_dir_name}.4.log"
    fi
    
    # Enable MLflow tracking if requested
    MLFLOW_ARGS=""
    if [[ "${ENABLE_MLFLOW:-0}" == "1" ]]; then
        echo "🔬 MLflow tracking enabled for optimization" | tee -a "$log_dir/${proj_dir_name}.4.log"
        MLFLOW_ARGS="--mlflow"
    fi
    
    # Determine goldens and actual output paths
    # GOLDENS_PATH: Directory containing golden test cases (goldens/item1, goldens/item2, ...)
    # ACTUAL_OUT_PATH: Directory where actual test outputs will be stored
    if [[ -n "${GOLDENS_PATH:-}" ]]; then
        GOLDENS_DIR="$GOLDENS_PATH"
        echo "📁 Using GOLDENS_PATH: $GOLDENS_DIR" | tee -a "$log_dir/${proj_dir_name}.4.log"
    else
        echo "❌ Error: GOLDENS_PATH environment variable not set" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "   Please set GOLDENS_PATH to the directory containing golden test cases" | tee -a "$log_dir/${proj_dir_name}.4.log"
        exit 1
    fi
    
    if [[ -n "${ACTUAL_OUT_PATH:-}" ]]; then
        ACTUAL_OUT_DIR="$ACTUAL_OUT_PATH"
        echo "📁 Using ACTUAL_OUT_PATH: $ACTUAL_OUT_DIR" | tee -a "$log_dir/${proj_dir_name}.4.log"
    else
        # Default to optimization directory
        ACTUAL_OUT_DIR="$OPTIMIZATION_DIR/actual_out"
        echo "📁 Using default ACTUAL_OUT_PATH: $ACTUAL_OUT_DIR" | tee -a "$log_dir/${proj_dir_name}.4.log"
    fi
    
    # Create actual output directory if it doesn't exist
    mkdir -p "$ACTUAL_OUT_DIR"
    
    # Set scoring mode (default: llm)
    SCORING_MODE="${SCORING_MODE:-llm}"
    echo "📊 Scoring mode: $SCORING_MODE" | tee -a "$log_dir/${proj_dir_name}.4.log"
    
    # Set agent type (default: adk-python)
    AGENT_TYPE="${AGENT_TYPE:-adk-python}"
    echo "🤖 Agent type: $AGENT_TYPE" | tee -a "$log_dir/${proj_dir_name}.4.log"
    
    # Set reference directory for golden comparison if specified
    REFERENCE_ARGS=""
    if [[ -n "${REFERENCE_DIR:-}" ]]; then
        if [[ -d "$REFERENCE_DIR" ]]; then
            echo "📚 Reference directory: $REFERENCE_DIR" | tee -a "$log_dir/${proj_dir_name}.4.log"
            REFERENCE_ARGS="--reference $REFERENCE_DIR"
        else
            echo "⚠️  Warning: REFERENCE_DIR not found: $REFERENCE_DIR" | tee -a "$log_dir/${proj_dir_name}.4.log"
        fi
    fi
    
    set +e
    $PYSPY_CMD $ADK_ROOT/.venv/bin/python3 "$ADK_ROOT/deepeval-scoring/optimize_instructions.py" \
        --goldens "$GOLDENS_DIR" \
        --actual-out "$ACTUAL_OUT_DIR" \
        --current-instructions "$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md" \
        --output "$OPTIMIZATION_DIR/optimized_instructions.md" \
        --algorithm copro \
        --iterations 1 \
        --mcp-port "$mcp_server_port" \
        --model "$model" \
        --device "$device_name" \
        --scoring-mode "$SCORING_MODE" \
        --agent "$AGENT_TYPE" \
        --use-custom-scorer \
        $REFERENCE_ARGS \
        $MLFLOW_ARGS 2>&1 | tee -a "$log_dir/${proj_dir_name}.4.log"
    optimize_exit_code=$?
    set -e
    
    # Log py-spy profile file location if profiling was enabled
    if [[ "${ENABLE_PROF:-0}" == "1" ]] && [[ -f "$PYSPY_OUTPUT" ]]; then
        PROFILE_SIZE=$(du -h "$PYSPY_OUTPUT" | cut -f1)
        echo "✅ py-spy profile saved: $PYSPY_OUTPUT ($PROFILE_SIZE)" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "   View with: speedscope $PYSPY_OUTPUT" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "   Or upload to https://www.speedscope.app/" | tee -a "$log_dir/${proj_dir_name}.4.log"
    fi
    
    if [[ $optimize_exit_code -ne 0 ]]; then
        echo "❌ Optimization failed (exit code: $optimize_exit_code)" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "Skipping stage 4 optimization" | tee -a "$log_dir/${proj_dir_name}.4.log"
        exit 0
    fi
    
    # Verify optimized file was created
    if [[ ! -f "$OPTIMIZATION_DIR/optimized_instructions.md" ]]; then
        echo "❌ Optimized instructions file not created" | tee -a "$log_dir/${proj_dir_name}.4.log"
        echo "Skipping stage 4 optimization" | tee -a "$log_dir/${proj_dir_name}.4.log"
        exit 0
    fi
    
    # Step 3: Backup and deploy optimized instructions
    echo "Step 3: Deploying optimized instructions..." | tee -a "$log_dir/${proj_dir_name}.4.log"
    INSTRUCTIONS_FILE="$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md"
    BACKUP_FILE="$INSTRUCTIONS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    cp "$INSTRUCTIONS_FILE" "$BACKUP_FILE"
    cp "$OPTIMIZATION_DIR/optimized_instructions.md" "$INSTRUCTIONS_FILE"
    
    echo "✅ Optimized instructions deployed" | tee -a "$log_dir/${proj_dir_name}.4.log"
    echo "   Backup saved: $BACKUP_FILE" | tee -a "$log_dir/${proj_dir_name}.4.log"
    
    # Step 4: Commit to git repository
    echo "Step 4: Committing optimized instructions to git..." | tee -a "$log_dir/${proj_dir_name}.4.log"
    cd "$ADK_ROOT"
    
    # Verify we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "⚠️  Not in a git repository, skipping commit" | tee -a "$log_dir/${proj_dir_name}.4.log"
        cd "$proj_dir_abs"
        echo "✅ Stage 4 optimization complete (no git commit)" | tee -a "$log_dir/${proj_dir_name}.4.log"
        exit 0
    fi
    
    # Check if there are changes to commit
    if git diff --quiet "$INSTRUCTIONS_FILE"; then
        echo "ℹ️  No changes detected in instructions file, skipping commit" | tee -a "$log_dir/${proj_dir_name}.4.log"
    else
        # Get optimization metrics for commit message
        OPTIMIZATION_DATE=$(date +"%Y-%m-%d %H:%M:%S")
        # Count golden test cases
        GOLDEN_COUNT=$(find "$GOLDENS_DIR" -maxdepth 1 -type d ! -path "$GOLDENS_DIR" 2>/dev/null | wc -l || echo "unknown")
        
        # Stage the optimized instructions file
        git add "$INSTRUCTIONS_FILE" 2>&1 | tee -a "$log_dir/${proj_dir_name}.4.log"
        
        # Create detailed commit message
        set +e
        git commit -m "refactor(openspec): optimize apply agent instructions via DeepEval

- Optimized apply_agent_instruction.md using PromptOptimizer (copro)
- Based on $GOLDEN_COUNT golden test cases from $GOLDENS_DIR
- Optimization date: $OPTIMIZATION_DATE
- Model used: $model
- Algorithm: copro with 3 iterations
- Backup saved: $(basename $BACKUP_FILE)

This optimization aims to improve agent performance based on golden
test cases and automated prompt engineering techniques." 2>&1 | tee -a "$log_dir/${proj_dir_name}.4.log"
        commit_exit_code=$?
        set -e
        
        if [[ $commit_exit_code -eq 0 ]]; then
            COMMIT_HASH=$(git rev-parse --short HEAD)
            echo "✅ Successfully committed optimized instructions: $COMMIT_HASH" | tee -a "$log_dir/${proj_dir_name}.4.log"
        else
            echo "⚠️  Warning: Failed to commit changes (exit code: $commit_exit_code)" | tee -a "$log_dir/${proj_dir_name}.4.log"
            echo "   Optimized instructions were deployed but not committed to git" | tee -a "$log_dir/${proj_dir_name}.4.log"
            # Don't exit with error - optimization was still successful
        fi
    fi
    
    cd "$proj_dir_abs"
    
    # Calculate and log total time for stage 4
    stage4_end_time=$(date +%s)
    stage4_elapsed=$((stage4_end_time - stage4_start_time))
    echo "✅ Stage 4 optimization complete!" | tee -a "$log_dir/${proj_dir_name}.4.log"
    echo "⏱️  Total time for stage 4: $stage4_elapsed seconds" | tee -a "$log_dir/${proj_dir_name}.4.log"
fi
