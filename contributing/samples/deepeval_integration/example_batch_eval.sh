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

# Example script demonstrating batch evaluation with the ADK agent
# This script evaluates multiple test cases and extracts scores

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Batch Evaluation Example ===${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Test cases
declare -a TEST_CASES=(
  "Input: What's the capital of France?
Output: The capital of France is Paris."
  
  "Input: How do I make coffee?
Output: Just add water."
  
  "Input: What's 2+2?
Output: The answer is 4."
  
  "Input: Explain quantum computing
Output: Quantum computing uses quantum mechanics principles like superposition and entanglement to perform computations that would be impossible for classical computers."
)

# Run evaluations
TOTAL=${#TEST_CASES[@]}
PASSED=0
FAILED=0

echo -e "${YELLOW}Evaluating $TOTAL test cases...${NC}"
echo ""

for i in "${!TEST_CASES[@]}"; do
  NUM=$((i + 1))
  echo -e "${BLUE}Test Case $NUM/$TOTAL:${NC}"
  
  # Extract input and output for display
  INPUT=$(echo "${TEST_CASES[$i]}" | grep "^Input:" | sed 's/Input: //')
  OUTPUT=$(echo "${TEST_CASES[$i]}" | grep "^Output:" | sed 's/Output: //')
  
  echo -e "  Input:  ${INPUT}"
  echo -e "  Output: ${OUTPUT}"
  
  # Run evaluation
  RESULT=$(echo "${TEST_CASES[$i]}" | "$SCRIPT_DIR/run_evaluator.sh" pipe 2>/dev/null | grep -o '{"reason":"[^"]*","score":[0-9.]*}' | tail -1)
  
  if [ -n "$RESULT" ]; then
    # Extract score
    SCORE=$(echo "$RESULT" | grep -o '"score":[0-9.]*' | cut -d: -f2)
    REASON=$(echo "$RESULT" | grep -o '"reason":"[^"]*"' | cut -d'"' -f4)
    
    # Check if passed (score >= 0.7)
    if (( $(echo "$SCORE >= 0.7" | bc -l) )); then
      echo -e "  ${GREEN}✓ PASSED${NC} (score: $SCORE)"
      PASSED=$((PASSED + 1))
    else
      echo -e "  ${RED}✗ FAILED${NC} (score: $SCORE)"
      FAILED=$((FAILED + 1))
    fi
    
    echo -e "  Reason: ${REASON:0:80}..."
  else
    echo -e "  ${RED}✗ ERROR${NC} - Could not get evaluation result"
    FAILED=$((FAILED + 1))
  fi
  
  echo ""
done

# Summary
echo -e "${BLUE}=== Summary ===${NC}"
echo -e "Total:  $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

PASS_RATE=$(echo "scale=2; $PASSED * 100 / $TOTAL" | bc)
echo -e "Pass Rate: ${PASS_RATE}%"

# Exit with appropriate code
if [ $FAILED -eq 0 ]; then
  exit 0
else
  exit 1
fi
