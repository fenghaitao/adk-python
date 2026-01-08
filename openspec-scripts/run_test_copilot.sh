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
#   Examples: "0", "1", "0,1", "1,0", "0 1"
#   Stage 0 = bootstrap project
#   Stage 1 = proposal initialization

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
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run-openspec-copilot.sh . $mcp_server_port --init-only" "$log_dir/${proj_dir}.0.log"
fi

if [[ "${run_stage[1]}" == "1" ]]; then
    echo "=== Stage 1: proposal initialization ===" | tee "$log_dir/${proj_dir}.1.log"
    echo "Using model: $model" | tee -a "$log_dir/${proj_dir}.1.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run-copilot-proposal.sh . $mcp_server_port" "$log_dir/${proj_dir}.1.log"
fi

if [[ "${run_stage[2]}" == "1" ]]; then
    echo "=== Stage 2: appy the changes ===" | tee "$log_dir/${proj_dir}.2.log"
    echo "Using model: claude-sonnet-4.5" | tee -a "$log_dir/${proj_dir}.2.log"
    cd "$proj_dir_abs"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run-copilot-apply.sh . $mcp_server_port" "$log_dir/${proj_dir}.2.log"
fi
