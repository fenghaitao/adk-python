#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

$ADK_ROOT/openspec-scripts/run_openspec_subagents.sh \
  --workdir adk_openspec_project \
  --proposal $ADK_ROOT/openspec-prompts/refine-wdt-interrupt.md \
  --agent refine \
  --port 8056 \
  --apply \
  --archive \
  --model iflow/qwen3-coder-plus