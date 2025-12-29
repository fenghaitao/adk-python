#!/bin/bash

# Run complete Rovodev workflow: propose then apply
# Usage: ./run-rovodev.sh [workdir] [--multi-spec-deltas]

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
    --multi-spec-deltas   Use multi-spec-deltas mode for complex devices (50+ requirements)
                          Default: simple mode for standard proposals
    --help, -h            Show this help message and exit

BEHAVIOR:
    1. Runs run-rovodev-propose.sh to create a proposal
    2. Captures the change ID from the proposal
    3. Prompts user to continue
    4. Runs run-rovodev-apply.sh with the captured change ID

MODES:
    Simple Mode (default):
        - For devices with <50 requirements
        - Single capability with one spec delta
        
    Multi-Spec-Deltas Mode (--multi-spec-deltas):
        - For complex devices with 50+ requirements
        - Multiple capabilities with separate spec deltas

EXAMPLES:
    # Simple mode (default)
    ./run-rovodev.sh

    # Simple mode with custom workdir
    ./run-rovodev.sh myproject

    # Multi-spec-deltas mode for complex device
    ./run-rovodev.sh myproject --multi-spec-deltas
EOF
}

# Defaults
WORKDIR=""
MULTI_SPEC_DELTAS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    --multi-spec-deltas)
      MULTI_SPEC_DELTAS=true
      shift
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

# Determine mode description
if [ "$MULTI_SPEC_DELTAS" = true ]; then
  MODE_DESC="multi-spec-deltas (complex devices)"
else
  MODE_DESC="simple (standard proposals)"
fi

echo "================================"
echo "🚀 Rovodev Complete Workflow"
echo "================================"
echo ""
echo "Working Directory: $WORKDIR"
echo "Mode: $MODE_DESC"
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
if [ "$MULTI_SPEC_DELTAS" = true ]; then
  PROPOSE_CMD+=(--multi-spec-deltas)
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

# Build apply command - no longer uses --power flag
APPLY_CMD=("$SCRIPT_DIR/run-rovodev-apply.sh" "$WORKDIR" "$CHANGE_ID")

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
