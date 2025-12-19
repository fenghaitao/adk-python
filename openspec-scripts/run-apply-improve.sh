#!/usr/bin/env bash
set -euo pipefail

# Run only the Apply-Improvement Agent on a given OpenSpec project
#
# This script runs the apply improvement agent using ADK and analyzes the
# apply agent session logs and context to generate improvement insights
# and optional memory files.
#
# Supports two agent variants:
#   - apply_improve_text_agent (default): Uses text analysis tools on .session.txt files
#   - apply_improve_json_agent: Uses Python JSON tools on .session.json files
#
# Usage examples:
#   ./run_meta_improve.sh \
#       --workdir adk_openspec_project \
#       --change-id "123-implement-wdt" \
#       --model github_copilot/gpt-5-mini \
#       --save-session
#
#   # Use JSON-based agent
#   ./run_meta_improve.sh \
#       --workdir adk_openspec_project \
#       --agent json
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
CHANGE_ID="apply_improve"
AGENT_TYPE="text"  # Options: "text" (default) or "json"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --change-id)
      CHANGE_ID="$2"; shift 2;;
    --model)
      MODEL="$2"; shift 2;;
    --workdir)
      WORKDIR="$2"; shift 2;;
    --agent)
      AGENT_TYPE="$2"; shift 2;;
    --save-session)
      SAVE_SESSION=true; shift;;
    --help|-h)
      cat <<HELP
Usage: $0 --workdir <openspec_project_dir> [OPTIONS]

Options:
  --workdir DIR         Working directory (required)
  --change-id ID        Change identifier (default: apply_improve)
  --model MODEL         Model to use (default: iflow/qwen3-coder-plus)
  --agent TYPE          Agent type: text or json (default: text)
                        - text: Uses text analysis tools on .session.txt files (production)
                        - json: Uses Python JSON tools on .session.json files (experimental)
  --save-session        Save session logs (default: true)
  --help, -h            Show this help message

Examples:
  # Use default text-based agent
  $0 --workdir adk_openspec_project

  # Use JSON-based agent (experimental)
  $0 --workdir adk_openspec_project --agent json

  # Specify model and change ID
  $0 --workdir adk_openspec_project --model github_copilot/gpt-5-mini --change-id wdt-123
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
else
  # Ensure the apply agent instruction exists (required for analysis prompts)
  APPLY_INSTRUCTION_FILE="$APPLY_DIR/apply_agent_instruction.md"
  if [[ ! -f "$APPLY_INSTRUCTION_FILE" ]]; then
    echo -e "${YELLOW}ℹ️  Missing $APPLY_INSTRUCTION_FILE — attempting to export it now${NC}"
    if [[ -x "$SCRIPT_DIR/export_instruction.sh" ]]; then
      bash "$SCRIPT_DIR/export_instruction.sh" "$APPLY_DIR" || {
        echo -e "${RED}❌ Failed to export apply agent instruction. Continuing without it.${NC}"
      }
    else
      echo -e "${YELLOW}⚠️  export_instruction.sh not executable or not found at $SCRIPT_DIR${NC}"
    fi
  fi
fi

if [[ ! -d "openspec-memories" ]]; then
  echo -e "${YELLOW}⚠️  openspec-memories directory not found in $WORKDIR${NC}"
  echo -e "${YELLOW}   The agent will work without memory context${NC}"
fi

# Validate agent type and set import path
case "$AGENT_TYPE" in
  text)
    AGENT_IMPORT="openspec_integration.apply_improve_text_agent"
    AGENT_NAME="apply_improve_text_agent (text-based)"
    ;;
  json)
    AGENT_IMPORT="openspec_integration.apply_improve_json_agent"
    AGENT_NAME="apply_improve_json_agent (JSON-based)"
    ;;
  *)
    echo -e "${RED}❌ Invalid agent type: $AGENT_TYPE${NC}"
    echo -e "${RED}   Valid options: text, json${NC}"
    exit 1
    ;;
esac

echo -e "${BLUE}Using agent: $AGENT_NAME${NC}"

# Prepare apply improve agent directory under workdir
APPLY_IMPROVE_DIR="$WORKDIR/adk_openspec_apply_improvement_agent"
prepare_agent_dir "$APPLY_IMPROVE_DIR" "$AGENT_IMPORT"

# Build ADK command
ADK_IMPROVE_CMD="$ADK_BIN run $APPLY_IMPROVE_DIR"
if [[ "$SAVE_SESSION" == true ]]; then
  IMPROVE_SESSION_ID="apply_improve_${CHANGE_ID}_$(date +%Y%m%d_%H%M%S)"
  ADK_IMPROVE_CMD="$ADK_IMPROVE_CMD --save_session --session_id $IMPROVE_SESSION_ID"
  echo -e "${BLUE}Session will be saved as: $APPLY_IMPROVE_DIR/${IMPROVE_SESSION_ID}.session.json${NC}"
fi

IMPROVE_LOG="$APPLY_IMPROVE_DIR/apply_improvement.log"

echo -e "${BLUE}🧠 Running Apply-Improvement Analysis for ${CHANGE_ID}...${NC}"
set +e
printf "/analyze --generate-improvements\nexit\n" | OPENSPEC_MODEL="$MODEL" $ADK_IMPROVE_CMD 2>&1 | tee "$IMPROVE_LOG"
IMPROVE_STATUS=${PIPESTATUS[0]}
set -e

echo -e "${BLUE}📝 Apply-improvement log saved: $IMPROVE_LOG${NC}"

if [[ $IMPROVE_STATUS -ne 0 ]]; then
  echo -e "${YELLOW}⚠️  Apply-improvement analysis completed with warnings${NC}"
else
  echo -e "${GREEN}✅ Apply-improvement analysis completed successfully${NC}"
  if [[ -f "$APPLY_IMPROVE_DIR/improvement_report.md" ]]; then
    echo -e "${GREEN}📋 Improvement report generated: $APPLY_IMPROVE_DIR/improvement_report.md${NC}"
  fi
  if [[ -d "$APPLY_IMPROVE_DIR/generated_memories" ]]; then
    MEMORY_COUNT=$(find "$APPLY_IMPROVE_DIR/generated_memories" -name "*.md" -type f | wc -l)
    echo -e "${GREEN}📚 Generated $MEMORY_COUNT memory improvement files${NC}"
  fi
fi

# Optional: human-readable dump for saved session
if [[ "${SAVE_SESSION}" == true ]] && [[ -f "$APPLY_IMPROVE_DIR/${IMPROVE_SESSION_ID}.session.json" ]]; then
  if [[ -f "$SCRIPT_DIR/../view_session.py" ]]; then
    python3 "$SCRIPT_DIR/../view_session.py" "$APPLY_IMPROVE_DIR/${IMPROVE_SESSION_ID}.session.json" > "$APPLY_IMPROVE_DIR/${IMPROVE_SESSION_ID}.session.txt"
    if [[ -f "$APPLY_IMPROVE_DIR/${IMPROVE_SESSION_ID}.session.txt" ]]; then
      echo -e "${GREEN}Human-readable apply-improvement session saved: $APPLY_IMPROVE_DIR/${IMPROVE_SESSION_ID}.session.txt${NC}"
    fi
  fi
fi

echo -e "${GREEN}✔ Apply-Improvement run complete.${NC}"
