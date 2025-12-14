#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

~/adk-python/openspec-scripts/run_openspec_subagents.sh \
  --workdir adk_openspec_project \
  --port 8056 \
  --apply \
  --change-id implement-wdt-initial \
  --model iflow/qwen3-coder-plus
