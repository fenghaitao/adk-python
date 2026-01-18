#!/bin/bash
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Run complete DSPy OpenSpec workflow: propose then apply
# Usage: ./run-dspy-propose-apply.sh [workdir] [proposal-text] [device-hint]
#
# Arguments:
#   workdir        Working directory (default: adk_openspec_project)
#   proposal-text  Proposal description (default: "Propose to model a simple watchdog timer for Simics platform simulation")
#   device-hint    Device name hint (optional)
#
# Examples:
#   ./run-dspy-propose-apply.sh                                    # Use all defaults
#   ./run-dspy-propose-apply.sh "Implement WDT device" wdt         # Custom proposal
#   ./run-dspy-propose-apply.sh myproject "Implement I2C" i2c      # Custom workdir and proposal

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
BLUE="\033[0;34m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo "================================"
echo "🚀 DSPy OpenSpec Complete Workflow"
echo "================================"
echo ""
echo "This will run:"
echo "  1. Proposal - Create OpenSpec proposal"
echo "  2. Apply    - Apply the proposal"
echo ""

# Parse arguments
WORKDIR=""
PROPOSAL_TEXT=""
DEVICE_HINT=""

# Check if first argument is a directory (workdir)
if [ $# -gt 0 ] && [ -d "$1" ]; then
  WORKDIR="$1"
  shift
else
  # Default to adk_openspec_project
  WORKDIR="adk_openspec_project"
fi

# Get proposal text (optional - has default)
if [ $# -gt 0 ]; then
  PROPOSAL_TEXT="$1"
  shift
else
  # Default prompt similar to run-kiro-propose.sh
  PROPOSAL_TEXT="Propose to model a simple watchdog timer for Simics platform simulation"
  echo -e "${YELLOW}ℹ️  Using default proposal: $PROPOSAL_TEXT${NC}"
  echo ""
fi

# Get device hint (optional)
if [ $# -gt 0 ]; then
  DEVICE_HINT="$1"
  shift
else
  # Default device hint when using default proposal
  if [ "$PROPOSAL_TEXT" = "Propose to model a simple watchdog timer for Simics platform simulation" ]; then
    DEVICE_HINT="wdt"
    echo -e "${YELLOW}ℹ️  Using default device hint: $DEVICE_HINT${NC}"
    echo ""
  fi
fi

# Step 1: Run propose and capture the change ID
echo "================================"
echo "STEP 1: PROPOSE"
echo "================================"
echo ""

# Build propose command
PROPOSE_CMD="$SCRIPT_DIR/run-dspy-openspec.sh"
if [ -n "$WORKDIR" ]; then
  PROPOSE_CMD="$PROPOSE_CMD $WORKDIR"
fi
PROPOSE_CMD="$PROPOSE_CMD proposal \"$PROPOSAL_TEXT\""
if [ -n "$DEVICE_HINT" ]; then
  PROPOSE_CMD="$PROPOSE_CMD --device $DEVICE_HINT"
fi

# Run propose and capture output
echo -e "${BLUE}Running: $PROPOSE_CMD${NC}"
echo ""

PROPOSE_OUTPUT=$(eval "$PROPOSE_CMD" 2>&1 | tee /dev/tty)

# Extract change ID from output (look for "Change ID: xxx")
CHANGE_ID=$(echo "$PROPOSE_OUTPUT" | grep "Change ID:" | tail -1 | sed 's/.*Change ID: //' | tr -d ' ')

if [ -z "$CHANGE_ID" ]; then
  echo ""
  echo "❌ Error: No change ID returned from propose step"
  exit 1
fi

echo ""
echo -e "${GREEN}📋 Created Change ID: $CHANGE_ID${NC}"
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

# Build apply command
APPLY_CMD="$SCRIPT_DIR/run-dspy-openspec.sh"
if [ -n "$WORKDIR" ]; then
  APPLY_CMD="$APPLY_CMD $WORKDIR"
fi
APPLY_CMD="$APPLY_CMD apply --id $CHANGE_ID"

echo -e "${BLUE}Running: $APPLY_CMD${NC}"
echo ""

eval "$APPLY_CMD"

echo ""
echo "================================"
echo "🎉 Workflow Complete!"
echo "================================"
echo ""
echo "Change ID: $CHANGE_ID"
echo ""
echo "Next steps:"
echo "1. Check the implementation in simics-project/modules/"
echo "2. Build: cd simics-project && make"
echo "3. Run tests: cd simics-project && ./bin/test-runner -v"
echo ""
