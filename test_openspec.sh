#!/bin/bash

ADK_ROOT="${ADK_ROOT:-$HOME/wp5/ai_agents/adk-openspec}"

proj_dir=$1
device_name=wdog
mcp_server_port=$2

if [ -z "$mcp_server_port" ]; then
    mcp_server_port=8051
fi

rm -rf "$proj_dir"

echo "=== Stage 0: Initial Setup ===" | tee "$proj_dir.0.log"
start_time=$(date +%s)
"$ADK_ROOT/run_openspec.sh" "$proj_dir" \
--device "$device_name" \
--port "$mcp_server_port" 2>&1 | tee -a "$proj_dir.0.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 0 completed in $elapsed seconds" | tee -a "$proj_dir.0.log"

# enter the simics-project and make the device target to generate the *-glue.dml file
echo "=== Generating ${device_name}-glue.dml ===" | tee -a "$proj_dir.0.log"
cd "$proj_dir/simics-project" && gmake "$device_name" 2>&1 | tee -a "$proj_dir.0.log"
cd - > /dev/null

# Copy prompt templates to the project folder
echo "=== Preparing prompt templates ===" | tee -a "$proj_dir.0.log"
mkdir -p "$proj_dir/openspec-prompts"
cp "$ADK_ROOT/openspec-prompts/"*.md "$proj_dir/openspec-prompts/"
# Customize prompts: replace <device_name> placeholder with actual device name
sed -i "s/<device_name>/$device_name/g" "$proj_dir/openspec-prompts/"*.md
echo "✓ Prompt templates customized for device: $device_name" | tee -a "$proj_dir.0.log"

echo "=== Stage 1: Implementation (Prompt 1) ===" | tee "$proj_dir.1.log"
start_time=$(date +%s)
"$ADK_ROOT/run_openspec.sh" "$proj_dir" \
"$proj_dir/openspec-prompts/1.md" \
--device "$device_name" \
--skip-specify \
--skip-simics-setup \
--port "$mcp_server_port" 2>&1 | tee -a "$proj_dir.1.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 1 completed in $elapsed seconds" | tee -a "$proj_dir.1.log"

# exit

echo "=== Stage 2: Error Fixing (Prompt 2) ===" | tee "$proj_dir.2.log"
start_time=$(date +%s)
"$ADK_ROOT/run_openspec.sh" "$proj_dir" \
"$proj_dir/openspec-prompts/2.md" \
--device "$device_name" \
--skip-specify \
--skip-simics-setup \
--port "$mcp_server_port" 2>&1 | tee -a "$proj_dir.2.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 2 completed in $elapsed seconds" | tee -a "$proj_dir.2.log"

exit

echo "=== Stage 3: Test Implementation (Prompt 3) ===" | tee "$proj_dir.3.log"
start_time=$(date +%s)
"$ADK_ROOT/run_openspec.sh" "$proj_dir" \
"$proj_dir/openspec-prompts/3.md" \
--device "$device_name" \
--skip-specify \
--skip-simics-setup \
--port "$mcp_server_port" 2>&1 | tee -a "$proj_dir.3.log"
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Stage 3 completed in $elapsed seconds" | tee -a "$proj_dir.3.log"