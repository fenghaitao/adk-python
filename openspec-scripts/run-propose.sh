#!/bin/bash

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Run OpenSpec proposal using run_openspec.sh
~/adk-python/run_openspec.sh \
  adk_openspec_project \
  ~/adk-python/openspec-prompts/propose-wdt-register-interface.md \
  --model iflow/qwen3-coder-plus \
  --port 8051 \
  --skip-specify \
  --skip-simics-setup \
  --save-session
