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

# Script to run the ADK evaluation agent
# Usage: ./run_evaluator.sh [interactive|pipe]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADK_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Set up proxy if needed
export https_proxy=${https_proxy:-http://localhost:7890}
export http_proxy=${http_proxy:-http://localhost:7890}

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ADK Evaluation Agent ===${NC}"
echo -e "${GREEN}Using model: github_copilot/gpt-4.1${NC}"
echo -e "${GREEN}Proxy: $https_proxy${NC}"
echo ""

# Check if we're in pipe mode or interactive mode
MODE="${1:-interactive}"

if [ "$MODE" = "pipe" ]; then
  # Pipe mode - read from stdin
  echo -e "${YELLOW}Reading evaluation request from stdin...${NC}"
  cd "$SCRIPT_DIR"
  "$ADK_ROOT/.venv/bin/python" -m google.adk.cli run .
elif [ "$MODE" = "interactive" ]; then
  # Interactive mode
  echo -e "${YELLOW}Starting interactive evaluation session...${NC}"
  echo -e "${YELLOW}Type 'exit' to quit${NC}"
  echo ""
  echo -e "${BLUE}Example input:${NC}"
  echo "Input: What's the capital of France?"
  echo "Output: The capital of France is Paris."
  echo ""
  cd "$SCRIPT_DIR"
  "$ADK_ROOT/.venv/bin/python" -m google.adk.cli run .
else
  echo "Usage: $0 [interactive|pipe]"
  echo ""
  echo "Modes:"
  echo "  interactive - Start interactive session (default)"
  echo "  pipe        - Read from stdin"
  echo ""
  echo "Examples:"
  echo "  $0                    # Interactive mode"
  echo "  $0 interactive        # Interactive mode"
  echo "  echo 'Input: ...' | $0 pipe  # Pipe mode"
  exit 1
fi
