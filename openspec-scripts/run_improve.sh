#!/usr/bin/env bash
set -euo pipefail

# Run an improvement agent (apply_improve or meta_improve) on a given OpenSpec project
#
# This script runs improvement agents using ADK to analyze session logs and context
# to generate improvement insights and optional memory files.
#
# Supports two improvement levels:
#   - apply_improve: Analyzes apply agent sessions
#   - meta_improve: Analyzes apply_improve agent sessions (meta-improvement)
#
# Each level supports two agent variants:
#   - text (default): Uses text analysis tools on .session.txt files
#   - json: Uses Python JSON tools on .session.json files
#
# Usage examples:
#   # Run apply_improve agent
#   ./run_improve.sh apply_improve \
#       --workdir adk_openspec_project \
#       --change-id "123-implement-wdt" \
#       --model github_copilot/gpt-5-mini
#
#   # Run meta_improve agent with JSON variant
#   ./run_improve.sh meta_improve \
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

# Check for improvement level argument
if [[ $# -lt 1 ]]; then
  cat <<USAGE
Usage: $0 <improve_level> [OPTIONS]

Improvement Levels:
  apply_improve     Analyze apply agent sessions
  meta_improve      Analyze apply_improve agent sessions (meta-improvement)

Options:
  --workdir DIR     Working directory (required)
  --change-id ID    Change identifier (default: <improve_level>)
  --model MODEL     Model to use (default: iflow/qwen3-coder-plus)
  --agent TYPE      Agent type: text or json (default: text)
                    - text: Uses text analysis tools on .session.txt files (production)
                    - json: Uses Python JSON tools on .session.json files (experimental)
  --save-session    Save session logs (default: true)
  --help, -h        Show this help message

Examples:
  # Run apply_improve with default text agent
  $0 apply_improve --workdir adk_openspec_project

  # Run meta_improve with JSON agent
  $0 meta_improve --workdir adk_openspec_project --agent json

  # Specify model and change ID
  $0 apply_improve --workdir adk_openspec_project --model github_copilot/gpt-5-mini --change-id wdt-123
USAGE
  exit 1
fi

IMPROVE_LEVEL="$1"
shift

# Validate improvement level
case "$IMPROVE_LEVEL" in
  apply_improve|meta_improve)
    ;;
  *)
    echo -e "${RED}❌ Invalid improvement level: $IMPROVE_LEVEL${NC}"
    echo -e "${RED}   Valid options: apply_improve, meta_improve${NC}"
    exit 1
    ;;
esac

# Defaults
MODEL="${OPENSPEC_MODEL:-iflow/qwen3-coder-plus}"
SAVE_SESSION=true
WORKDIR=""
CHANGE_ID="$IMPROVE_LEVEL"
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
Usage: $0 <improve_level> --workdir <openspec_project_dir> [OPTIONS]

Improvement Levels:
  apply_improve     Analyze apply agent sessions
  meta_improve      Analyze apply_improve agent sessions (meta-improvement)

Options:
  --workdir DIR     Working directory (required)
  --change-id ID    Change identifier (default: $IMPROVE_LEVEL)
  --model MODEL     Model to use (default: iflow/qwen3-coder-plus)
  --agent TYPE      Agent type: text or json (default: text)
                    - text: Uses text analysis tools on .session.txt files (production)
                    - json: Uses Python JSON tools on .session.json files (experimental)
  --save-session    Save session logs (default: true)
  --help, -h        Show this help message

Examples:
  # Use default text-based agent
  $0 $IMPROVE_LEVEL --workdir adk_openspec_project

  # Use JSON-based agent (experimental)
  $0 $IMPROVE_LEVEL --workdir adk_openspec_project --agent json

  # Specify model and change ID
  $0 $IMPROVE_LEVEL --workdir adk_openspec_project --model github_copilot/gpt-5-mini --change-id wdt-123
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

# Validate required directories based on improvement level
case "$IMPROVE_LEVEL" in
  apply_improve)
    REQUIRED_DIR_REL="adk_openspec_apply_agent"
    REQUIRED_DIR="$WORKDIR/$REQUIRED_DIR_REL"
    if [[ ! -d "$REQUIRED_DIR" ]]; then
      echo -e "${RED}❌ $REQUIRED_DIR_REL directory not found in $WORKDIR${NC}"
      echo -e "${RED}   This script requires an apply agent at: $REQUIRED_DIR_REL${NC}"
      exit 1
    else
      # Ensure the apply agent instruction exists (required for analysis prompts)
      INSTRUCTION_FILE="$REQUIRED_DIR/apply_agent_instruction.md"
      if [[ ! -f "$INSTRUCTION_FILE" ]]; then
        echo -e "${YELLOW}ℹ️  Missing $INSTRUCTION_FILE — attempting to export it now${NC}"
        if [[ -x "$SCRIPT_DIR/export_instruction.sh" ]]; then
          bash "$SCRIPT_DIR/export_instruction.sh" "$REQUIRED_DIR" || {
            echo -e "${RED}❌ Failed to export apply agent instruction. Continuing without it.${NC}"
          }
        else
          echo -e "${YELLOW}⚠️  export_instruction.sh not executable or not found at $SCRIPT_DIR${NC}"
        fi
      fi
    fi
    ;;
  meta_improve)
    # Check for apply_improve agent directories (text or json variant)
    REQUIRED_DIR_TEXT="$WORKDIR/adk_openspec_apply_improve_text_agent"
    REQUIRED_DIR_JSON="$WORKDIR/adk_openspec_apply_improve_json_agent"
    
    if [[ ! -d "$REQUIRED_DIR_TEXT" ]] && [[ ! -d "$REQUIRED_DIR_JSON" ]]; then
      echo -e "${RED}❌ No apply_improve agent directory found in $WORKDIR${NC}"
      echo -e "${RED}   This script requires either:${NC}"
      echo -e "${RED}   - adk_openspec_apply_improve_text_agent${NC}"
      echo -e "${RED}   - adk_openspec_apply_improve_json_agent${NC}"
      exit 1
    fi
    
    if [[ -d "$REQUIRED_DIR_TEXT" ]]; then
      echo -e "${BLUE}Found apply_improve_text_agent for analysis${NC}"
    fi
    if [[ -d "$REQUIRED_DIR_JSON" ]]; then
      echo -e "${BLUE}Found apply_improve_json_agent for analysis${NC}"
    fi
    ;;
esac

if [[ ! -d "openspec-memories" ]]; then
  echo -e "${YELLOW}⚠️  openspec-memories directory not found in $WORKDIR${NC}"
  echo -e "${YELLOW}   The agent will work without memory context${NC}"
fi

# Validate agent type and set import path
case "$AGENT_TYPE" in
  text)
    AGENT_IMPORT="openspec_integration.${IMPROVE_LEVEL}_text_agent"
    AGENT_NAME="${IMPROVE_LEVEL}_text_agent (text-based)"
    IMPROVE_DIR="$WORKDIR/adk_openspec_${IMPROVE_LEVEL}_text_agent"
    ;;
  json)
    AGENT_IMPORT="openspec_integration.${IMPROVE_LEVEL}_json_agent"
    AGENT_NAME="${IMPROVE_LEVEL}_json_agent (JSON-based)"
    IMPROVE_DIR="$WORKDIR/adk_openspec_${IMPROVE_LEVEL}_json_agent"
    ;;
  *)
    echo -e "${RED}❌ Invalid agent type: $AGENT_TYPE${NC}"
    echo -e "${RED}   Valid options: text, json${NC}"
    exit 1
    ;;
esac

echo -e "${BLUE}Using agent: $AGENT_NAME${NC}"

# Prepare improve agent directory under workdir
prepare_agent_dir "$IMPROVE_DIR" "$AGENT_IMPORT"

# Export instruction for the improve agent if it doesn't exist
IMPROVE_INSTRUCTION_FILE="$IMPROVE_DIR/${IMPROVE_LEVEL}_${AGENT_TYPE}_agent_instruction.md"
if [[ ! -f "$IMPROVE_INSTRUCTION_FILE" ]]; then
  echo -e "${YELLOW}ℹ️  Missing $IMPROVE_INSTRUCTION_FILE — attempting to export it now${NC}"
  if [[ -x "$SCRIPT_DIR/export_instruction.sh" ]]; then
    bash "$SCRIPT_DIR/export_instruction.sh" "$IMPROVE_DIR" || {
      echo -e "${RED}❌ Failed to export ${IMPROVE_LEVEL} agent instruction. Continuing without it.${NC}"
    }
  else
    echo -e "${YELLOW}⚠️  export_instruction.sh not executable or not found at $SCRIPT_DIR${NC}"
  fi
fi

# Build ADK command
ADK_CMD="$ADK_BIN run $IMPROVE_DIR"
if [[ "$SAVE_SESSION" == true ]]; then
  SESSION_ID="${IMPROVE_LEVEL}_${CHANGE_ID}_$(date +%Y%m%d_%H%M%S)"
  ADK_CMD="$ADK_CMD --save_session --session_id $SESSION_ID"
  echo -e "${BLUE}Session will be saved as: $IMPROVE_DIR/${SESSION_ID}.session.json${NC}"
fi

LOG_FILE="$IMPROVE_DIR/${IMPROVE_LEVEL}.log"

echo -e "${BLUE}🧠 Running ${IMPROVE_LEVEL} Analysis for ${CHANGE_ID}...${NC}"
set +e
printf "/analyze --generate-improvements\nexit\n" | OPENSPEC_MODEL="$MODEL" $ADK_CMD 2>&1 | tee "$LOG_FILE"
STATUS=${PIPESTATUS[0]}
set -e

echo -e "${BLUE}📝 ${IMPROVE_LEVEL} log saved: $LOG_FILE${NC}"

if [[ $STATUS -ne 0 ]]; then
  echo -e "${YELLOW}⚠️  ${IMPROVE_LEVEL} analysis completed with warnings${NC}"
else
  echo -e "${GREEN}✅ ${IMPROVE_LEVEL} analysis completed successfully${NC}"
  if [[ -f "$IMPROVE_DIR/improvement_report.md" ]]; then
    echo -e "${GREEN}📋 Improvement report generated: $IMPROVE_DIR/improvement_report.md${NC}"
  fi
  if [[ -d "$IMPROVE_DIR/generated_memories" ]]; then
    MEMORY_COUNT=$(find "$IMPROVE_DIR/generated_memories" -name "*.md" -type f | wc -l)
    echo -e "${GREEN}📚 Generated $MEMORY_COUNT memory improvement files${NC}"
  fi
fi

# Optional: human-readable dump for saved session
if [[ "${SAVE_SESSION}" == true ]] && [[ -f "$IMPROVE_DIR/${SESSION_ID}.session.json" ]]; then
  if [[ -f "$SCRIPT_DIR/../view_session.py" ]]; then
    python3 "$SCRIPT_DIR/../view_session.py" "$IMPROVE_DIR/${SESSION_ID}.session.json" > "$IMPROVE_DIR/${SESSION_ID}.session.txt"
    if [[ -f "$IMPROVE_DIR/${SESSION_ID}.session.txt" ]]; then
      echo -e "${GREEN}Human-readable ${IMPROVE_LEVEL} session saved: $IMPROVE_DIR/${SESSION_ID}.session.txt${NC}"
    fi
  fi
fi

echo -e "${GREEN}✔ ${IMPROVE_LEVEL} run complete.${NC}"
