#!/bin/bash

ADK_ROOT="${ADK_ROOT:-$HOME/wp5/ai_agents/adk-openspec}"

# Parse command line arguments with smart defaults
# Usage:
#   ./test_openspec.sh proj_dir                          # 1 arg:  proj_dir
#   ./test_openspec.sh model proj_dir                    # 2 args: model proj_dir
#   ./test_openspec.sh mcp_port model proj_dir           # 3 args: mcp_port model proj_dir

if [ $# -eq 1 ]; then
    # 1 argument: proj_dir
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="$1"
elif [ $# -eq 2 ]; then
    # 2 arguments: model proj_dir
    mcp_server_port=8051
    model="$1"
    proj_dir="$2"
elif [ $# -ge 3 ]; then
    # 3 arguments: mcp_port model proj_dir
    mcp_server_port="$1"
    model="$2"
    proj_dir="$3"
else
    # No arguments: use all defaults
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="wdt_test"
fi

device_name=test_dev

# Set the model for Spec-Kit (Specify agent) to match OpenSpec model
export SPEC_KIT_MODEL="$model"

echo "Parameters:"
echo "  MCP Server Port: $mcp_server_port"
echo "  Model: $model"
echo "  Project Directory: $proj_dir"
echo "  Device Name: $device_name"
echo ""

rm -rf "$proj_dir"

echo "=== Stage 0: Initial Setup ===" | tee "$proj_dir.0.log"
echo "Using model: $model" | tee -a "$proj_dir.0.log"
STAGE0_CMD="$ADK_ROOT/run_openspec.sh $proj_dir --device $device_name --model $model --port $mcp_server_port"
echo "Command: $STAGE0_CMD" | tee -a "$proj_dir.0.log"
start_time=$(date +%s)
$STAGE0_CMD 2>&1 | tee -a "$proj_dir.0.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 0 completed in $elapsed seconds" | tee -a "$proj_dir.0.log"

# Enter the simics-project and make the device target to generate the *-glue.dml file
echo "=== Generating ${device_name}-glue.dml ===" | tee -a "$proj_dir.0.log"
cd "$proj_dir/simics-project" && gmake "$device_name" 2>&1 | tee -a "$proj_dir.0.log"
cd - > /dev/null

# Get the git branch name in the project folder
cd "$proj_dir"
git_branch_name=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "master")
echo "Git branch name: $git_branch_name" | tee -a "$proj_dir.0.log"
cd - > /dev/null
# Copy prompt templates to the project folder
echo "=== Preparing prompt templates ===" | tee -a "$proj_dir.0.log"
mkdir -p "$proj_dir/openspec-prompts"
cp "$ADK_ROOT/openspec-prompts/"*.md "$proj_dir/openspec-prompts/"
# Customize prompts: replace <device_name> placeholder with actual device name
sed -i "s/<device_name>/$device_name/g" "$proj_dir/openspec-prompts/"*.md
# Customize prompts: replace <git_branch_name> placeholder with actual git branch name
sed -i "s/<git_branch_name>/$git_branch_name/g" "$proj_dir/openspec-prompts/"*.md
echo "Prompt templates customized for branch=$git_branch_name, device=$device_name" | tee -a "$proj_dir.0.log"

# exit

echo "=== Stage 1: Implementation (Prompt 1) ===" | tee "$proj_dir.1.log"
STAGE1_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"
echo "Command: $STAGE1_CMD" | tee -a "$proj_dir.1.log"
start_time=$(date +%s)
$STAGE1_CMD 2>&1 | tee -a "$proj_dir.1.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 1 completed in $elapsed seconds" | tee -a "$proj_dir.1.log"

# exit

echo "=== Stage 2: Error Fixing (Prompt 2) ===" | tee "$proj_dir.2.log"
STAGE2_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/2.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"
echo "Command: $STAGE2_CMD" | tee -a "$proj_dir.2.log"
start_time=$(date +%s)
$STAGE2_CMD 2>&1 | tee -a "$proj_dir.2.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 2 completed in $elapsed seconds" | tee -a "$proj_dir.2.log"

# exit

echo "=== Stage 3: Test Implementation (Prompt 3) ===" | tee "$proj_dir.3.log"
STAGE3_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/3.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"
echo "Command: $STAGE3_CMD" | tee -a "$proj_dir.3.log"
# exit
start_time=$(date +%s)
$STAGE3_CMD 2>&1 | tee -a "$proj_dir.3.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 3 completed in $elapsed seconds" | tee -a "$proj_dir.3.log"