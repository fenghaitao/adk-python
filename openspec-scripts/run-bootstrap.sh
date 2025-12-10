#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"
~/adk-python/run_openspec.sh \
  adk_openspec_project \
  --model iflow/qwen3-coder-plus \
  --port 8056
