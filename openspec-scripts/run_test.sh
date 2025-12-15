#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Function to execute a command with logging and timing
# Usage: run_cmd_with_timing "command string" "log_file"
run_cmd_with_timing() {
    local cmd="$1"
    local log_file="$2"

    echo "Command: $cmd" | tee -a "$log_file"
    start_time=$(date +%s)
    eval "$cmd 2>&1" | tee -a "$log_file"
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "Completed in $elapsed seconds" | tee -a "$log_file"
}

# Parse command line arguments with smart defaults
# Usage:
#   ./run-bootstrap.sh proj_dir                          # 1 arg:  proj_dir (stages: 0,1)
#   ./run-bootstrap.sh proj_dir stages                   # 2 args: proj_dir stages
#   ./run-bootstrap.sh model proj_dir stages             # 3 args: model proj_dir stages
#   ./run-bootstrap.sh mcp_port model proj_dir stages    # 4 args: mcp_port model proj_dir stages
# stages examples: "0" (only stage 0), "1" (only stage 1), "0,1" (both stages)

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

rm -rf "$proj_dir"
mkdir -p "$proj_dir"
cd "$proj_dir" || exit 1

# Execute stages based on input
if [[ "$stages" == *"0"* ]]; then
    echo "=== Stage 0: bootstrap ===" | tee "$proj_dir.0.log"
    echo "Using model: $model" | tee -a "$proj_dir.0.log"
    run_cmd_with_timing "$ADK_ROOT/run_openspec.sh adk_openspec_project --model $model --port $mcp_server_port" "$proj_dir.0.log"
fi

if [[ "$stages" == *"1"* ]]; then
    echo "=== Stage 1: proposal initialization ===" | tee "$proj_dir.1.log"
    echo "Using model: $model" | tee -a "$proj_dir.1.log"
    run_cmd_with_timing "$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh --workdir adk_openspec_project --proposal $ADK_ROOT/openspec-prompts/proposal-wdt.md --agent initial --port $mcp_server_port --apply --archive --model $model" "$proj_dir.1.log"
fi
