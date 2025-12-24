#!/bin/bash

# Run complete Kiro workflow: propose then apply OpenSpec change
# Usage: ./run-kiro.sh [workdir] [propose-session-name] [apply-session-name]

set -e

# Get script directory to find the other scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================"
echo "🚀 Kiro Complete Workflow"
echo "================================"
echo ""
echo "This will run:"
echo "  1. run-kiro-propose.sh - Create OpenSpec proposal"
echo "  2. run-kiro-apply.sh   - Apply the proposal"
echo ""

# Step 1: Run propose and capture the change ID
echo "================================"
echo "STEP 1: PROPOSE"
echo "================================"
echo ""

# Run propose, show output, and capture the last line (change ID)
CHANGE_ID=$("$SCRIPT_DIR/run-kiro-propose.sh" "$@" | tee /dev/tty | tail -1)

if [ -z "$CHANGE_ID" ]; then
  echo "❌ Error: No change ID returned from propose step"
  exit 1
fi

echo ""
echo "📋 Created Change ID: $CHANGE_ID"
echo ""

# Prompt user to continue
echo "================================"
echo "⏸️  Ready for Apply Step"
echo "================================"
echo ""
echo "Press Enter to continue with apply, or Ctrl+C to stop..."
read -r

# Step 2: Run apply with the change ID
echo ""
echo "================================"
echo "STEP 2: APPLY"
echo "================================"
echo ""

"$SCRIPT_DIR/run-kiro-apply.sh" "${1:-adk_openspec_project}" "$CHANGE_ID" "${3}"

echo ""
echo "================================"
echo "🎉 Workflow Complete!"
echo "================================"
echo ""
echo "Change ID: $CHANGE_ID"
echo ""
