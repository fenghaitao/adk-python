#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}

$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh \
  --workdir $WORKDIR \
  --proposal $ADK_ROOT/openspec-prompts/proposal-wdt.md \
  --agent initial \
  --port 8056 \
  --apply \
  --model iflow/qwen3-coder-plus
