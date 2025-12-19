#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}
CHANGE_ID=${2:-implement-wdt-initial}

$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh \
  --workdir $WORKDIR \
  --port 8056 \
  --apply \
  --change-id $CHANGE_ID \
  --model iflow/qwen3-coder-plus
