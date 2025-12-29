#!/usr/bin/env bash
set -euo pipefail

# Run only the Score Agent on a given OpenSpec project
#
# This script runs the score agent using ADK and analyzes the
# apply agent session logs and context to generate quality scores
# and metrics.
#
# Usage examples:
#   ./run-score-agent.sh \
#       --workdir adk_openspec_project \
#       --change-id "123-implement-wdt" \
#       --model github_copilot/gpt-5-mini \
#       --save-session
#

# Source helpers and config
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source "$SCRIPT_DIR/common-config.sh"

# Colors
RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; BLUE="\033[0;34m"; NC="\033[0m"

# Derive paths and tooling
SPEC_KIT_DIR="$SCRIPT_DIR/../contributing/samples/spec_kit_integration"
SAMPLES_DIR="$(dirname "$SPEC_KIT_DIR")"
ADK_BIN="$SCRIPT_DIR/../.venv/bin/adk"
if [[ ! -x "$ADK_BIN" ]]; then
  ADK_BIN="adk"
fi

# Simple helper to prepare an ADK agent directory with root_agent
prepare_agent_dir() {
  local target_dir="$1"; local import_path="$2"
  mkdir -p "$target_dir"
  cat > "$target_dir/agent.py" <<EOF
import sys, os
sys.path.insert(0, '$SAMPLES_DIR')
from $import_path import root_agent
EOF
}

# Defaults
MODEL="${OPENSPEC_MODEL:-iflow/qwen3-coder-plus}"
SAVE_SESSION=true
WORKDIR=""
CHANGE_ID="score_agent"
DEVICE_NAME=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --change-id)
      CHANGE_ID="$2"; shift 2;;
    --model)
      MODEL="$2"; shift 2;;
    --workdir)
      WORKDIR="$2"; shift 2;;
    --device-name)
      DEVICE_NAME="$2"; shift 2;;
    --save-session)
      SAVE_SESSION=true; shift;;
    --help|-h)
      cat <<HELP
Usage: $0 --workdir <openspec_project_dir> --device-name <device_name> [OPTIONS]

Options:
  --workdir DIR         Working directory (required)
  --device-name NAME    Device name to evaluate (required)
  --change-id ID        Change identifier (default: score_agent)
  --model MODEL         Model to use (default: iflow/qwen3-coder-plus)
  --save-session        Save session logs (default: true)
  --help, -h            Show this help message

Examples:
  # Evaluate a WDT device implementation
  $0 --workdir /path/to/adk_openspec_project --device-name wdt

  # Specify model and change ID
  $0 --workdir /path/to/project --device-name wdt --model github_copilot/gpt-5-mini --change-id wdt-123
HELP
      exit 0;;
    *)
      echo "Unknown argument: $1"; exit 1;;
  esac
done

if [[ -z "$WORKDIR" ]]; then
  echo -e "${RED}❌ --workdir is required${NC}"
  exit 1
fi

if [[ -z "$DEVICE_NAME" ]]; then
  echo -e "${RED}❌ --device-name is required${NC}"
  exit 1
fi

# Set working directory - create if needed, or validate if exists
if [[ ! -d "$WORKDIR" ]]; then
  echo -e "${YELLOW}Creating working directory: $WORKDIR${NC}"
  mkdir -p "$WORKDIR"
fi

cd "$WORKDIR"
WORKDIR="$(pwd)"

echo -e "${BLUE}Working directory: $WORKDIR${NC}"

# Validate required directories exist
APPLY_DIR_REL="adk_openspec_apply_agent"
APPLY_DIR="$WORKDIR/$APPLY_DIR_REL"
if [[ ! -d "$APPLY_DIR" ]]; then
  echo -e "${RED}❌ $APPLY_DIR_REL directory not found in $WORKDIR${NC}"
  echo -e "${RED}   This script requires an apply agent at: $APPLY_DIR_REL${NC}"
  exit 1
fi

if [[ ! -d "openspec-memories" ]]; then
  echo -e "${YELLOW}⚠️  openspec-memories directory not found in $WORKDIR${NC}"
  echo -e "${YELLOW}   The agent will work without memory context${NC}"
fi

# Set import path for the score agent
AGENT_IMPORT="openspec_integration.score_agent"
AGENT_NAME="score_agent"

echo -e "${BLUE}Using agent: $AGENT_NAME${NC}"

# Prepare score agent directory under workdir
SCORE_DIR="$WORKDIR/adk_openspec_score_agent"
prepare_agent_dir "$SCORE_DIR" "$AGENT_IMPORT"

# Build ADK command
ADK_SCORE_CMD="$ADK_BIN run $SCORE_DIR"
if [[ "$SAVE_SESSION" == true ]]; then
  SCORE_SESSION_ID="score_${CHANGE_ID}_$(date +%Y%m%d_%H%M%S)"
  ADK_SCORE_CMD="$ADK_SCORE_CMD --save_session --session_id $SCORE_SESSION_ID"
  echo -e "${BLUE}Session will be saved as: $SCORE_DIR/${SCORE_SESSION_ID}.session.json${NC}"
fi

SCORE_LOG="$SCORE_DIR/score_agent.log"

echo -e "${BLUE}🧠 Running Score Agent Analysis for ${CHANGE_ID}...${NC}"
echo -e "${BLUE}Device: ${DEVICE_NAME}${NC}"
set +e
printf "/score --workdir=\"$WORKDIR\" --device-name=\"$DEVICE_NAME\"\nexit\n" | OPENSPEC_MODEL="$MODEL" $ADK_SCORE_CMD 2>&1 | tee "$SCORE_LOG"
SCORE_STATUS=${PIPESTATUS[0]}
set -e

echo -e "${BLUE}📝 Score agent log saved: $SCORE_LOG${NC}"

if [[ $SCORE_STATUS -ne 0 ]]; then
  echo -e "${YELLOW}⚠️  Score agent analysis completed with warnings${NC}"
else
  echo -e "${GREEN}✅ Score agent analysis completed successfully${NC}"
  if [[ -f "$WORKDIR/score.md" ]]; then
    echo -e "${GREEN}📋 Score report generated: $WORKDIR/score.md${NC}"
  fi
  if [[ -f "$SCORE_DIR/score_report.md" ]]; then
    echo -e "${GREEN}📋 Score report generated: $SCORE_DIR/score_report.md${NC}"
  fi
  if [[ -f "$SCORE_DIR/metrics.json" ]]; then
    echo -e "${GREEN}📊 Metrics saved: $SCORE_DIR/metrics.json${NC}"
  fi
fi

# Optional: human-readable dump for saved session
if [[ "${SAVE_SESSION}" == true ]] && [[ -f "$SCORE_DIR/${SCORE_SESSION_ID}.session.json" ]]; then
  if [[ -f "$SCRIPT_DIR/../view_session.py" ]]; then
    python3 "$SCRIPT_DIR/../view_session.py" "$SCORE_DIR/${SCORE_SESSION_ID}.session.json" > "$SCORE_DIR/${SCORE_SESSION_ID}.session.txt"
    if [[ -f "$SCORE_DIR/${SCORE_SESSION_ID}.session.txt" ]]; then
      echo -e "${GREEN}Human-readable score session saved: $SCORE_DIR/${SCORE_SESSION_ID}.session.txt${NC}"
    fi
  fi
fi

echo -e "${GREEN}✔ Score Agent run complete.${NC}"
