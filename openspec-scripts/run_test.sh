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
#   SKIP_COLLECT=1       - Skip session data collection, use existing historical_sessions.json
#   SKIP_OPTIMIZE=1      - Skip optimization step, only collect session data
#   FORCE_OPTIMIZE=1     - Force optimization even with insufficient sessions
#   FORCE_RECOLLECT=1    - Force recollection from EXTRA_WORKDIRS (ignore cache)
#   MIN_SESSIONS=N       - Set minimum session threshold (default: 5)
#   MAX_CONCURRENT=N     - Set max concurrent API calls (default: 1)
#   THROTTLE_SECONDS=N   - Set throttle delay between batches (default: 30.0)
#   EXTRA_WORKDIRS       - Space-separated additional workdirs to collect sessions from
#                          Example: EXTRA_WORKDIRS="/path/to/proj1 /path/to/proj2"
#                          Sessions are cached per workdir and reused across runs
#   ENABLE_MLFLOW=1      - Enable MLflow tracking for collection and optimization
#   SCORING_MODE         - Scoring mode: llm, deterministic, or hybrid (default: hybrid)
#   AGENT_TYPE           - Agent type for behavior evaluation (e.g., kiro-cli, rovodev, copilot-cli)
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
    
    # Step 1: Collect historical session data
    if [[ "${SKIP_COLLECT:-0}" == "1" ]]; then
        echo "Step 1: Skipping session data collection (SKIP_COLLECT=1)" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Using existing historical_sessions.json if available" | tee -a "$log_dir/${proj_dir}.2.log"
        
        # Verify existing file
        if [[ ! -f "$OPTIMIZATION_DIR/historical_sessions.json" ]]; then
            echo "❌ Error: historical_sessions.json not found and SKIP_COLLECT=1" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Either run without SKIP_COLLECT=1 or provide an existing historical_sessions.json" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
            exit 0
        fi
        echo "✅ Found existing historical_sessions.json" | tee -a "$log_dir/${proj_dir}.2.log"
    else
        echo "Step 1: Collecting historical session data..." | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Working directory: $(pwd)" | tee -a "$log_dir/${proj_dir}.2.log"
        echo "Output path: $OPTIMIZATION_DIR/historical_sessions.json" | tee -a "$log_dir/${proj_dir}.2.log"
        
        # Create cache directory for extra workdirs
        CACHE_DIR="$OPTIMIZATION_DIR/.cache"
        mkdir -p "$CACHE_DIR"
        
        # Process EXTRA_WORKDIRS with caching
        EXTRA_SESSION_FILES=""
        if [[ -n "${EXTRA_WORKDIRS:-}" ]]; then
            echo "📁 Processing additional workdirs with caching..." | tee -a "$log_dir/${proj_dir}.2.log"
            
            for extra_dir in $EXTRA_WORKDIRS; do
                # Generate cache filename based on directory path
                cache_name=$(echo "$extra_dir" | sed 's/[^a-zA-Z0-9]/_/g')
                cache_file="$CACHE_DIR/extra_sessions_${cache_name}.json"
                
                # Check if cache exists and is recent (use FORCE_RECOLLECT=1 to override)
                if [[ -f "$cache_file" ]] && [[ "${FORCE_RECOLLECT:-0}" != "1" ]]; then
                    echo "   ♻️  Using cached data from: $extra_dir" | tee -a "$log_dir/${proj_dir}.2.log"
                    echo "      Cache file: $(basename $cache_file)" | tee -a "$log_dir/${proj_dir}.2.log"
                    EXTRA_SESSION_FILES="$EXTRA_SESSION_FILES $cache_file"
                else
                    if [[ "${FORCE_RECOLLECT:-0}" == "1" ]]; then
                        echo "   🔄 Force recollecting from: $extra_dir" | tee -a "$log_dir/${proj_dir}.2.log"
                    else
                        echo "   📥 Collecting from: $extra_dir" | tee -a "$log_dir/${proj_dir}.2.log"
                    fi
                    
                    # Build MLflow args
                    MLFLOW_ARGS=""
                    if [[ "${ENABLE_MLFLOW:-0}" == "1" ]]; then
                        MLFLOW_ARGS="--mlflow"
                    fi
                    
                    # Set scoring mode (default: hybrid)
                    SCORING_MODE="${SCORING_MODE:-hybrid}"
                    
                    # Build optional arguments for agent and reference
                    AGENT_ARGS=""
                    if [[ -n "${AGENT_TYPE:-adk-python}" ]]; then
                        AGENT_ARGS="--agent $AGENT_TYPE"
                    fi
                    
                    REFERENCE_ARGS=""
                    if [[ -n "${REFERENCE_DIR:-$ADK_ROOT/experiments/golden_reference}" ]]; then
                        REFERENCE_ARGS="--reference-dir $REFERENCE_DIR"
                    fi
                    
                    # Collect sessions from this extra workdir
                    set +e
                    python3 "$ADK_ROOT/deepeval-scoring/collect_session_data.py" \
                        --workdir "$extra_dir" \
                        --output "$cache_file" \
                        --min-score 0.5 \
                        --model "$model" \
                        --scoring-mode "$SCORING_MODE" \
                        $AGENT_ARGS \
                        $REFERENCE_ARGS \
                        $MLFLOW_ARGS 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
                    extra_collect_exit=$?
                    set -e
                    
                    if [[ $extra_collect_exit -eq 0 ]] && [[ -f "$cache_file" ]]; then
                        echo "      ✅ Cached to: $(basename $cache_file)" | tee -a "$log_dir/${proj_dir}.2.log"
                        EXTRA_SESSION_FILES="$EXTRA_SESSION_FILES $cache_file"
                    else
                        echo "      ⚠️  Failed to collect from $extra_dir, skipping" | tee -a "$log_dir/${proj_dir}.2.log"
                    fi
                fi
            done
        fi
        
        # Collect from current project directory
        echo "📥 Collecting from current project: $proj_dir_abs/adk_openspec_project" | tee -a "$log_dir/${proj_dir}.2.log"
        CURRENT_SESSION_FILE="$CACHE_DIR/current_sessions.json"
        
        # Enable MLflow tracking if requested
        MLFLOW_ARGS=""
        if [[ "${ENABLE_MLFLOW:-0}" == "1" ]]; then
            echo "🔬 MLflow tracking enabled" | tee -a "$log_dir/${proj_dir}.2.log"
            MLFLOW_ARGS="--mlflow"
        fi
        
        # Set scoring mode (default: hybrid)
        SCORING_MODE="${SCORING_MODE:-hybrid}"
        echo "🎯 Scoring mode: $SCORING_MODE" | tee -a "$log_dir/${proj_dir}.2.log"
        
        # Build optional arguments for agent and reference
        AGENT_ARGS=""
        if [[ -n "${AGENT_TYPE:-adk-python}" ]]; then
            echo "🤖 Agent type: $AGENT_TYPE" | tee -a "$log_dir/${proj_dir}.2.log"
            AGENT_ARGS="--agent $AGENT_TYPE"
        fi
        
        REFERENCE_ARGS=""
        if [[ -n "${REFERENCE_DIR:-$ADK_ROOT/experiments/golden_reference}" ]]; then
            echo "📚 Reference directory: $REFERENCE_DIR" | tee -a "$log_dir/${proj_dir}.2.log"
            REFERENCE_ARGS="--reference-dir $REFERENCE_DIR"
        fi
        
        # Collect current project sessions
        set +e
        python3 "$ADK_ROOT/deepeval-scoring/collect_session_data.py" \
            --workdir "$proj_dir_abs/adk_openspec_project" \
            --output "$CURRENT_SESSION_FILE" \
            --min-score 0.5 \
            --model "$model" \
            --scoring-mode "$SCORING_MODE" \
            $AGENT_ARGS \
            $REFERENCE_ARGS \
            $MLFLOW_ARGS 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
        collect_exit_code=$?
        set -e
        
        if [[ $collect_exit_code -ne 0 ]]; then
            echo "❌ Failed to collect session data (exit code: $collect_exit_code)" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Common issues:" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "  - DMLParser constructor error: Update deepeval-scoring/collect_session_data.py" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "  - Missing DML files: Make sure stage 1 completed successfully" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "  - Insufficient historical sessions: Need at least 10 sessions" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
            exit 0  # Don't fail the entire pipeline
        fi
        
        # Merge current sessions with extra workdir sessions (if any)
        if [[ -n "$EXTRA_SESSION_FILES" ]]; then
            echo "🔀 Merging session data from multiple sources..." | tee -a "$log_dir/${proj_dir}.2.log"
            echo "   Current: $(basename $CURRENT_SESSION_FILE)" | tee -a "$log_dir/${proj_dir}.2.log"
            
            # Count sessions in each file
            current_count=$(grep -c '"device_name"' "$CURRENT_SESSION_FILE" 2>/dev/null || echo "0")
            echo "   - Current project: $current_count sessions" | tee -a "$log_dir/${proj_dir}.2.log"
            
            for extra_file in $EXTRA_SESSION_FILES; do
                extra_count=$(grep -c '"device_name"' "$extra_file" 2>/dev/null || echo "0")
                echo "   - $(basename $extra_file): $extra_count sessions" | tee -a "$log_dir/${proj_dir}.2.log"
            done
            
            # Use Python to merge JSON arrays
            python3 -c "
import json
import sys

# Read current sessions
with open('$CURRENT_SESSION_FILE', 'r') as f:
    all_sessions = json.load(f)

# Merge extra sessions
extra_files = '$EXTRA_SESSION_FILES'.split()
for extra_file in extra_files:
    if extra_file.strip():
        try:
            with open(extra_file.strip(), 'r') as f:
                extra_sessions = json.load(f)
                all_sessions.extend(extra_sessions)
        except Exception as e:
            print(f'Warning: Failed to read {extra_file}: {e}', file=sys.stderr)

# Write merged sessions
with open('$OPTIMIZATION_DIR/historical_sessions.json', 'w') as f:
    json.dump(all_sessions, f, indent=2)

print(f'✅ Merged {len(all_sessions)} total sessions')
" 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
            
        else
            # No extra workdirs, just copy current sessions
            cp "$CURRENT_SESSION_FILE" "$OPTIMIZATION_DIR/historical_sessions.json"
        fi
        
        # Verify output file was created
        if [[ ! -f "$OPTIMIZATION_DIR/historical_sessions.json" ]]; then
            echo "❌ Historical sessions file not created" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
            exit 0
        fi
    fi
    
    # Check if we have enough sessions
    # Count objects by counting "device_name" field (each session object has one)
    session_count=$(grep -c '"device_name"' "$OPTIMIZATION_DIR/historical_sessions.json" 2>/dev/null || echo "0")
    session_count=$(echo "$session_count" | tr -d '\n\r ')
    echo "Found $session_count historical sessions" | tee -a "$log_dir/${proj_dir}.2.log"
    
    # Check minimum session count (default: 5, override with FORCE_OPTIMIZE=1 or MIN_SESSIONS=N)
    MIN_SESSIONS="${MIN_SESSIONS:-5}"
    if [[ "$session_count" -lt "$MIN_SESSIONS" ]]; then
        if [[ "${FORCE_OPTIMIZE:-0}" == "1" ]]; then
            echo "⚠️  Warning: Only $session_count sessions found (recommended: 10+)" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "⚡ FORCE_OPTIMIZE=1 - Proceeding with optimization anyway" | tee -a "$log_dir/${proj_dir}.2.log"
        else
            echo "⚠️  Warning: Only $session_count sessions found (recommended: 10+)" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Optimization may not be effective with limited data" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "Skipping stage 2 optimization" | tee -a "$log_dir/${proj_dir}.2.log"
            echo "💡 Tip: Use FORCE_OPTIMIZE=1 to bypass this check or MIN_SESSIONS=N to set a different threshold" | tee -a "$log_dir/${proj_dir}.2.log"
            exit 0
        fi
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
    
    set +e
    python3 "$ADK_ROOT/deepeval-scoring/optimize_instructions.py" \
        --historical-data "$OPTIMIZATION_DIR/historical_sessions.json" \
        --current-instructions "$ADK_ROOT/contributing/samples/openspec_integration/apply_agent_instruction.md" \
        --output "$OPTIMIZATION_DIR/optimized_instructions.md" \
        --algorithm copro \
        --iterations 5 \
        --max-concurrent "$MAX_CONCURRENT" \
        --throttle-seconds "$THROTTLE_SECONDS" \
        --model "github_copilot/gpt-4o" \
        --no-async \
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
        HISTORICAL_SESSIONS=$(grep -c '"device_name"' "$OPTIMIZATION_DIR/historical_sessions.json" 2>/dev/null || echo "unknown")
        
        # Stage the optimized instructions file
        git add "$INSTRUCTIONS_FILE" 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
        
        # Create detailed commit message
        set +e
        git commit -m "refactor(openspec): optimize apply agent instructions via DeepEval

- Optimized apply_agent_instruction.md using PromptOptimizer (copro)
- Based on $HISTORICAL_SESSIONS historical sessions (min score: 0.5)
- Optimization date: $OPTIMIZATION_DATE
- Model used: $model
- Algorithm: copro with 5 iterations
- Backup saved: $(basename $BACKUP_FILE)

This optimization aims to improve agent performance based on historical
session data and automated prompt engineering techniques." 2>&1 | tee -a "$log_dir/${proj_dir}.2.log"
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
