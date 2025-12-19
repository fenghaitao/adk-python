#!/usr/bin/env bash
set -euo pipefail

# Export an agent's instruction to a file.
#
# Usage:
#   export_instruction.sh AGENT_DIR [OUTPUT_FILE]
#
# Arguments:
#   AGENT_DIR   Directory containing the generated ADK agent (with agent.py)
#   OUTPUT_FILE Optional path to write instruction (default: "$AGENT_DIR/{agent_name}_instruction.md")
#               where {agent_name} is AGENT_DIR basename with "adk_openspec_" prefix removed
#
# Behavior:
#   - Imports openspec_integration.{module_name} using SAMPLES_DIR extracted
#     from "$AGENT_DIR/agent.py" and writes root_agent.instruction to OUTPUT_FILE
#   - Uses repo-local Python at .venv/bin/python
#

BLUE="\033[0;34m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo -e "${YELLOW}Usage:${NC} $0 AGENT_DIR [OUTPUT_FILE]"
  exit 1
fi

AGENT_DIR="$1"
OUTPUT_FILE="${2:-}"

if [[ ! -d "$AGENT_DIR" ]]; then
  echo -e "${RED}❌ AGENT_DIR not found: $AGENT_DIR${NC}"
  exit 1
fi

# Extract agent name from directory basename, removing "adk_openspec_" prefix
AGENT_DIR_BASENAME=$(basename "$AGENT_DIR")
AGENT_NAME="${AGENT_DIR_BASENAME#adk_openspec_}"

# Determine OUTPUT_FILE default
if [[ -z "${OUTPUT_FILE}" ]]; then
  OUTPUT_FILE="$AGENT_DIR/${AGENT_NAME}_instruction.md"
fi

# Extract SAMPLES_DIR from the generated agent.py
AGENT_PY="$AGENT_DIR/agent.py"
if [[ ! -f "$AGENT_PY" ]]; then
  echo -e "${RED}❌ agent.py not found in AGENT_DIR: $AGENT_PY${NC}"
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

echo -e "${BLUE}📝 Exporting ${AGENT_NAME} agent instruction to: $OUTPUT_FILE${NC}"

OPENSPEC_SAMPLES_DIR="$SAMPLES_DIR" \
AGENT_MODULE_NAME="$AGENT_NAME" \
AGENT_INSTRUCTION_FILE="$OUTPUT_FILE" \
"$PY_BIN" - <<'PYCODE'
import sys, os
samples_dir = os.environ.get('OPENSPEC_SAMPLES_DIR')
module_name = os.environ.get('AGENT_MODULE_NAME')
out_path = os.environ.get('AGENT_INSTRUCTION_FILE')

if not samples_dir:
    raise RuntimeError('OPENSPEC_SAMPLES_DIR not set')
if not module_name:
    raise RuntimeError('AGENT_MODULE_NAME not set')
if not out_path:
    raise RuntimeError('AGENT_INSTRUCTION_FILE not set')

# Import and export the instruction
sys.path.insert(0, samples_dir)
module_path = f'openspec_integration.{module_name}'
try:
    module = __import__(module_path, fromlist=['root_agent'])
    root_agent = getattr(module, 'root_agent', None)
    if not root_agent:
        raise ValueError(f"Module {module_path} has no 'root_agent' attribute")
    instruction = getattr(root_agent, 'instruction', None)
    if not instruction:
        raise ValueError(f"root_agent has no 'instruction' attribute")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(instruction.strip() + '\n')
    print(f'✓ {module_name} agent instruction exported')
except ImportError as e:
    raise ImportError(f"Failed to import {module_path}: {e}")
PYCODE

if [[ -f "$OUTPUT_FILE" ]]; then
  echo -e "${GREEN}✅ Instruction written to: $OUTPUT_FILE${NC}"
else
  echo -e "${RED}❌ No instruction file created.${NC}"
  exit 1
fi
