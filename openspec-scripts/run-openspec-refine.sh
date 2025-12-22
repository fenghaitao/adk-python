#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}

$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh \
  --workdir $WORKDIR \
  --proposal $ADK_ROOT/openspec-prompts/refine-wdt-interrupt.md \
  --agent refine \
  --port 8056 \
  --apply \
  --archive \
  --model iflow/qwen3-coder-plus