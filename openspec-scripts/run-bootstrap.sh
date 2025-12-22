#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}

$ADK_ROOT/run_openspec.sh \
  $WORKDIR \
  --model iflow/qwen3-coder-plus \
  --port 8056
