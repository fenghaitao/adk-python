#!/bin/bash

# Run complete Rovodev workflow: propose then apply
# Usage: ./run-rovodev.sh [workdir] [--power-propose <POWER_MD>] [--power-apply <POWER_MD>]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
  cat << 'EOF'
Run complete Rovodev workflow: propose then apply

USAGE:
    ./run-rovodev.sh [WORKDIR] [OPTIONS]

POSITIONAL ARGUMENTS:
    WORKDIR         Working directory (default: adk_openspec_project)

OPTIONS:
    --power-propose <POWER_MD>  Use the given POWER file for propose step
    --power-apply <POWER_MD>    Use the given POWER file for apply step
    --help, -h                  Show this help message and exit

BEHAVIOR:
    1. Runs run-rovodev-propose.sh to create a proposal
    2. Captures the change ID from the proposal
    3. Prompts user to continue
    4. Runs run-rovodev-apply.sh with the captured change ID
EOF
}

# Defaults
WORKDIR=""
POWER_PROPOSE=""
POWER_APPLY=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    --power-propose)
      POWER_PROPOSE="$2"
      shift 2
      ;;
    --power-apply)
      POWER_APPLY="$2"
      shift 2
      ;;
    *)
      if [ -z "$WORKDIR" ]; then
        WORKDIR="$1"
        shift
      else
        echo "❌ Error: Unknown argument: $1"
        show_help
        exit 1
      fi
      ;;
  esac
done

# Set default workdir
WORKDIR=${WORKDIR:-adk_openspec_project}

echo "================================"
echo "🚀 Rovodev Complete Workflow"
echo "================================"
echo ""
echo "This will run:"
echo "  1. run-rovodev-propose.sh - Create proposal"
echo "  2. run-rovodev-apply.sh   - Apply the proposal"
echo ""

# Step 1: Run propose and capture the change ID
echo "================================"
echo "STEP 1: PROPOSE"
echo "================================"
echo ""

# Build propose command
PROPOSE_CMD=("$SCRIPT_DIR/run-rovodev-propose.sh" "$WORKDIR")
if [ -n "$POWER_PROPOSE" ]; then
  PROPOSE_CMD+=(--power "$POWER_PROPOSE")
fi

# Run propose and capture last line (change ID)
CHANGE_ID=$("${PROPOSE_CMD[@]}" | tee /dev/tty | tail -1)

if [ -z "$CHANGE_ID" ]; then
  echo ""
  echo "⚠️  Warning: No change ID returned from propose step"
  echo "You may need to manually specify the change ID for apply step"
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

if [ -z "$CHANGE_ID" ]; then
  echo "❌ Error: No change ID available for apply step"
  echo "Please run propose step again or manually run:"
  echo "  $SCRIPT_DIR/run-rovodev-apply.sh $WORKDIR <change-id>"
  exit 1
fi

# Build apply command
APPLY_CMD=("$SCRIPT_DIR/run-rovodev-apply.sh" "$WORKDIR" "$CHANGE_ID")
if [ -n "$POWER_APPLY" ]; then
  APPLY_CMD+=(--power "$POWER_APPLY")
fi

# Run apply
"${APPLY_CMD[@]}"

echo ""
echo "================================"
echo "🎉 Workflow Complete!"
echo "================================"
echo ""
echo "Change ID: $CHANGE_ID"
echo "Working Directory: $WORKDIR"
echo ""
