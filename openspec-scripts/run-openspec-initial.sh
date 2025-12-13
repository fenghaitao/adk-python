#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

~/adk-python/openspec-scripts/run_openspec_subagents.sh \
  --workdir adk_openspec_project \
  --proposal ~/adk-python/openspec-prompts/proposal-wdt.md \
  --agent initial \
  --port 8056 \
  --apply \
  --archive \
  --model iflow/qwen3-coder-plus
