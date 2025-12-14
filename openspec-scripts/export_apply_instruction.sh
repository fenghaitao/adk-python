#!/usr/bin/env bash
set -euo pipefail

# Export the Apply agent's instruction to a file.
#
# Usage:
#   export_apply_instruction.sh APPLY_DIR [OUTPUT_FILE]
#
# Arguments:
#   APPLY_DIR   Directory containing the generated ADK apply agent (with agent.py)
#   OUTPUT_FILE Optional path to write instruction (default: "$APPLY_DIR/apply_agent_instruction.md")
#
# Behavior:
#   - Imports openspec_integration.apply_agent using SAMPLES_DIR extracted
#     from "$APPLY_DIR/agent.py" and writes root_agent.instruction to OUTPUT_FILE
#   - Uses repo-local Python at .venv/bin/python (no fallback parsing path)
#

BLUE="\033[0;34m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo -e "${YELLOW}Usage:${NC} $0 APPLY_DIR [OUTPUT_FILE]"
  exit 1
fi

APPLY_DIR="$1"
OUTPUT_FILE="${2:-}"

if [[ ! -d "$APPLY_DIR" ]]; then
  echo -e "${RED}❌ APPLY_DIR not found: $APPLY_DIR${NC}"
  exit 1
fi

# Determine OUTPUT_FILE default
if [[ -z "${OUTPUT_FILE}" ]]; then
  OUTPUT_FILE="$APPLY_DIR/apply_agent_instruction.md"
fi

# Extract SAMPLES_DIR from the generated agent.py
AGENT_PY="$APPLY_DIR/agent.py"
if [[ ! -f "$AGENT_PY" ]]; then
  echo -e "${RED}❌ agent.py not found in APPLY_DIR: $AGENT_PY${NC}"
  exit 1
fi

# Parse line: sys.path.insert(0, '<SAMPLES_DIR>')
SAMPLES_DIR=$(awk -F"'" '/sys\.path\.insert\(0,/{print $2; exit}' "$AGENT_PY" || true)
if [[ -z "${SAMPLES_DIR}" ]]; then
  echo -e "${RED}❌ Could not extract SAMPLES_DIR from $AGENT_PY${NC}"
  exit 1
fi

# Use repo-local Python from .venv
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY_BIN="$SCRIPT_DIR/../.venv/bin/python"
if [[ ! -x "$PY_BIN" ]]; then
  echo -e "${RED}❌ Python not found at $PY_BIN. Please create the virtualenv and install dependencies.${NC}"
  exit 1
fi

echo -e "${BLUE}📝 Exporting apply agent instruction to: $OUTPUT_FILE${NC}"

OPENSPEC_SAMPLES_DIR="$SAMPLES_DIR" \
APPLY_INSTRUCTION_FILE="$OUTPUT_FILE" \
"$PY_BIN" - <<'PYCODE'
import sys, os
samples_dir = os.environ.get('OPENSPEC_SAMPLES_DIR')
out_path = os.environ.get('APPLY_INSTRUCTION_FILE', 'apply_agent_instruction.md')

if not samples_dir:
    raise RuntimeError('OPENSPEC_SAMPLES_DIR not set')

# Import and export the instruction (no fallback)
sys.path.insert(0, samples_dir)
from openspec_integration.apply_agent import root_agent
instruction = getattr(root_agent, 'instruction', None)
if not instruction:
    raise ValueError("root_agent has no 'instruction' attribute")
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(instruction.strip() + '\n')
print('✓ Apply agent instruction exported')
PYCODE

if [[ -f "$OUTPUT_FILE" ]]; then
  echo -e "${GREEN}✅ Instruction written to: $OUTPUT_FILE${NC}"
else
  echo -e "${RED}❌ No instruction file created.${NC}"
  exit 1
fi
