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

# Bash wrapper for DSPy OpenSpec CLI
#
# Usage:
#   ./run-dspy-openspec.sh [workdir] proposal "Implement WDT device" --device wdt
#   ./run-dspy-openspec.sh [workdir] apply --id implement-wdt-device
#   ./run-dspy-openspec.sh [workdir] archive --id implement-wdt-device

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

# Use venv python if available
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
  PYTHON="$PROJECT_ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

# Default model
MODEL="${OPENSPEC_MODEL:-iflow/qwen3-coder-plus}"

# Colors
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"

# Check if first argument is a directory (workdir)
WORKDIR=""
if [ $# -gt 0 ] && [ -d "$1" ]; then
  WORKDIR="$1"
  shift
  echo -e "${BLUE}📁 Working directory: $WORKDIR${NC}"
else
  # Default to adk_openspec_project
  WORKDIR="adk_openspec_project"
  echo -e "${BLUE}📁 Working directory: $WORKDIR (default)${NC}"
fi

# Check if dspy_openspec is installed
if ! $PYTHON -c "import dspy_openspec" 2>/dev/null; then
  echo -e "${YELLOW}⚠️  dspy_openspec not installed. Installing...${NC}"
  cd "$SCRIPT_DIR/.."
  uv pip install --python "$PYTHON" -e . || {
    echo -e "${RED}❌ Failed to install dspy_openspec${NC}"
    exit 1
  }
fi

# Run CLI
echo -e "${BLUE}🚀 Running DSPy OpenSpec with model: $MODEL${NC}"

# Change to workdir if specified and it exists
if [ -n "$WORKDIR" ] && [ -d "$WORKDIR" ]; then
  cd "$WORKDIR"
elif [ -n "$WORKDIR" ]; then
  echo -e "${YELLOW}⚠️  Workdir $WORKDIR does not exist yet${NC}"
fi

# Add --verbose flag for better debugging
$PYTHON -m dspy_openspec.cli --model "$MODEL" --verbose "$@"
