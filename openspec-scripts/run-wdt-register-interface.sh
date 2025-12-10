#!/bin/bash

# Run complete WDT register interface workflow (propose + implement + archive)
# This script uses the unified autonomous prompt that completes all phases

# Source common configuration
source "$(dirname "$0")/common-config.sh"

# Run OpenSpec with unified autonomous prompt
~/adk-python/run_openspec.sh \
  adk_openspec_project \
  ~/adk-python/openspec-prompts/wdt-register-interface.auto.md \
  --model iflow/qwen3-coder-plus \
  --port 8056 \
  --skip-specify \
  --skip-simics-setup \
  --save-session

echo ""
echo "=========================================="
echo "WDT Register Interface Workflow Complete"
echo "=========================================="
echo ""
echo "The agent should have completed all phases:"
echo "  ✅ Phase 1: Created change proposal"
echo "  ✅ Phase 2: Implemented DML code and tests"
echo "  ✅ Phase 3: Archived the change"
echo "  ✅ Phase 4: Provided final status report"
echo ""
echo "Check the output above for the final status."
echo ""
