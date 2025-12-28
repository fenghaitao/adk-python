#!/bin/bash

# Run complete Rovodev workflow: propose then apply, similar to run-kiro.sh
# Usage: ./run-rovodev.sh [workdir] [propose-session-name] [apply-session-name]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================"
echo "🚀 Rovodev Complete Workflow"
echo "================================"
echo ""
echo "This will run:"
echo "  1. run-rovodev-propose.sh - Create proposal"
echo "  2. run-rovodev-apply.sh   - Apply the proposal"
echo ""

# Step 1: Run propose and capture the change ID (if any is emitted)
echo "================================"
echo "STEP 1: PROPOSE"
echo "================================"
echo ""

CHANGE_ID=$("$SCRIPT_DIR/run-rovodev-propose.sh" "$@" | tee /dev/tty | tail -1)

if [ -z "$CHANGE_ID" ]; then
  echo "⚠️  Warning: No change ID returned from propose step"
else
  echo ""
  echo "📋 Proposed Change ID: $CHANGE_ID"
fi

echo ""
echo "================================"
echo "⏸️  Ready for Apply Step"
echo "================================"
echo ""
echo "Press Enter to continue with apply, or Ctrl+C to stop..."
read -r

echo ""
echo "================================"
echo "STEP 2: APPLY"
echo "================================"
echo ""

# Prefer captured CHANGE_ID, but allow user-provided third arg to override
APPLY_CHANGE_ID="$CHANGE_ID"
[ -n "${2}" ] && APPLY_CHANGE_ID="${2}"

if [ -z "$APPLY_CHANGE_ID" ]; then
  echo "❌ Error: No change ID available for apply step. Provide one explicitly."
  echo "Usage: $0 [workdir] [propose-session-name] [apply-session-name]"
  exit 1
fi

"$SCRIPT_DIR/run-rovodev-apply.sh" "${1:-adk_openspec_project}" "$APPLY_CHANGE_ID" "${3}"

echo ""
echo "================================"
echo "🎉 Workflow Complete!"
echo "================================"
echo ""
echo "Change ID: ${APPLY_CHANGE_ID}"
echo ""
