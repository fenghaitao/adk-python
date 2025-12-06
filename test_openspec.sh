#!/bin/bash

ADK_ROOT="${ADK_ROOT:-$HOME/wp5/ai_agents/adk-openspec}"

# Parse command line arguments with smart defaults
# Usage:
#   ./test_openspec.sh proj_dir                                    # 1 arg:  proj_dir (runs stage 0,1)
#   ./test_openspec.sh proj_dir stage                              # 2 args: proj_dir stage
#   ./test_openspec.sh model proj_dir stage                        # 3 args: model proj_dir stage
#   ./test_openspec.sh mcp_port model proj_dir stage               # 4 args: mcp_port model proj_dir stage
#
# Stage parameter examples:
#   1       - Run stage 1 only
#   2       - Run stage 2 only
#   0,1     - Run stages 0 and 1 in sequence
#   1,2,3   - Run stages 1, 2, and 3 in sequence
#   0,1,2,3 - Run all stages in sequence

if [ $# -eq 1 ]; then
    # 1 argument: proj_dir
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="$1"
    stages="0,1"
elif [ $# -eq 2 ]; then
    # 2 arguments: proj_dir stage
    mcp_server_port=8051
    model="github_copilot/gpt-5-mini"
    proj_dir="$1"
    stages="$2"
elif [ $# -eq 3 ]; then
    # 3 arguments: model proj_dir stage
    mcp_server_port=8051
    model="$1"
    proj_dir="$2"
    stages="$3"
elif [ $# -ge 4 ]; then
    # 4 arguments: mcp_port model proj_dir stage
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

device_name=test_dev

# Set the model for Spec-Kit (Specify agent) to match OpenSpec model
export SPEC_KIT_MODEL="$model"

echo "Parameters:"
echo "  MCP Server Port: $mcp_server_port"
echo "  Model: $model"
echo "  Project Directory: $proj_dir"
echo "  Device Name: $device_name"
echo "  Stages to Run: $stages"
echo ""

# Function: Stage 0 - Initial Setup
run_stage0() {
    local proj_dir="$1"
    local device_name="$2"
    local model="$3"
    local mcp_server_port="$4"
    
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
    local git_branch_name=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "master")
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
}

# Function: Stage 1 - Implementation (Prompt 1)
run_stage1() {
    local proj_dir="$1"
    local device_name="$2"
    local model="$3"
    local mcp_server_port="$4"
    
    echo "=== Stage 1: Implementation (Prompt 1) ===" | tee "$proj_dir.1.log"
    STAGE1_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/1.SIMPLE.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"
    echo "Command: $STAGE1_CMD" | tee -a "$proj_dir.1.log"
    start_time=$(date +%s)
    $STAGE1_CMD 2>&1 | tee -a "$proj_dir.1.log"
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "Stage 1 completed in $elapsed seconds" | tee -a "$proj_dir.1.log"
}

# Function: Stage 2 - Error Fixing (Prompt 2)
run_stage2() {
    local proj_dir="$1"
    local device_name="$2"
    local model="$3"
    local mcp_server_port="$4"
    
    echo "=== Stage 2: Error Fixing (Prompt 2) ===" | tee "$proj_dir.2.log"
    STAGE2_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/2.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"
    echo "Command: $STAGE2_CMD" | tee -a "$proj_dir.2.log"
    start_time=$(date +%s)
    $STAGE2_CMD 2>&1 | tee -a "$proj_dir.2.log"
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "Stage 2 completed in $elapsed seconds" | tee -a "$proj_dir.2.log"
}

# Function: Stage 3 - Test Implementation (Prompt 3)
run_stage3() {
    local proj_dir="$1"
    local device_name="$2"
    local model="$3"
    local mcp_server_port="$4"
    
    echo "=== Stage 3: Test Implementation (Prompt 3) ===" | tee "$proj_dir.3.log"
    STAGE3_CMD="$ADK_ROOT/run_openspec.sh $proj_dir $proj_dir/openspec-prompts/3.md --device $device_name --model $model --skip-specify --skip-simics-setup --port $mcp_server_port"
    echo "Command: $STAGE3_CMD" | tee -a "$proj_dir.3.log"
    start_time=$(date +%s)
    $STAGE3_CMD 2>&1 | tee -a "$proj_dir.3.log"
    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "Stage 3 completed in $elapsed seconds" | tee -a "$proj_dir.3.log"
}

# Parse and execute stages
IFS=',' read -ra STAGE_ARRAY <<< "$stages"
for stage in "${STAGE_ARRAY[@]}"; do
    # Trim whitespace
    stage=$(echo "$stage" | xargs)
    
    case "$stage" in
        0)
            echo ""
            echo "▶ Running Stage 0..."
            run_stage0 "$proj_dir" "$device_name" "$model" "$mcp_server_port"
            ;;
        1)
            echo ""
            echo "▶ Running Stage 1..."
            run_stage1 "$proj_dir" "$device_name" "$model" "$mcp_server_port"
            ;;
        2)
            echo ""
            echo "▶ Running Stage 2..."
            run_stage2 "$proj_dir" "$device_name" "$model" "$mcp_server_port"
            ;;
        3)
            echo ""
            echo "▶ Running Stage 3..."
            run_stage3 "$proj_dir" "$device_name" "$model" "$mcp_server_port"
            ;;
        *)
            echo "⚠️  Unknown stage: $stage (valid stages: 0, 1, 2, 3)"
            ;;
    esac
done

echo ""
echo "✅ All requested stages completed!"