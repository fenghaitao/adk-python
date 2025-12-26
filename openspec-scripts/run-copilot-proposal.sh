#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

workdir=${1:-adk_openspec_project}
mcp_port=${2:-8056}
$ADK_ROOT/openspec-scripts/run-openspec-copilot.sh $workdir $mcp_port --skip-proposal