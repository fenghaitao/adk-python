#!/usr/bin/env bash
set -euo pipefail

# Run OpenSpec sub-agents (proposal -> apply -> archive) with Simics MCP server
#
# Usage examples:
#   ./run_openspec_subagents.sh \
#       --proposal "Implement watchdog timer device" \
#       --change-id "123-implement-wdt" \
#       --device wdt \
#       --apply \
#       --archive
#
#   ./run_openspec_subagents.sh --proposal "Add product search" --apply
#
# Options:
#   --proposal TITLE|FILE    Short summary/title for /proposal (string or file path) (required unless --change-id provided)
#   --change-id ID           Explicit change id to use (otherwise /proposal generates one)
#   --device NAME            Optional device name hint for id generation
#   --workdir DIR            Working directory for agent directories and logs (default: current directory)
#   --apply                  Run /apply after /proposal using the resolved change id
#   --archive                Run /archive after /apply using the same change id
#   --port PORT              MCP server port (default: 8051)
#   --model MODEL            Override model for sub-agents (default: env OPENSPEC_MODEL or github_copilot/gpt-5-mini)
#   --builtin-mcp yes|no     Start/stop the bundled MCP server (default: yes)
#
# Environment variables:
#   OPENSPEC_MODEL           Default model for agents
#   BUILTIN_MCP_SERVER       yes/no to enable bundled MCP server (overridden by --builtin-mcp)
#
# Notes:
# - Requires `adk run` available in PATH
# - Uses OpenSpec sub-agents in contributing/samples/openspec_integration/
# - Starts Simics MCP server unless disabled

source "$(dirname "$0")/common-config.sh"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SPEC_KIT_DIR="$SCRIPT_DIR/../contributing/samples/spec_kit_integration"
SAMPLES_DIR="$(dirname "$SPEC_KIT_DIR")"
MCP_SERVER_DIR="$SPEC_KIT_DIR/simics-mcp-server"
ADK_BIN="$SCRIPT_DIR/../.venv/bin/adk"
if [[ ! -x "$ADK_BIN" ]]; then
  ADK_BIN="adk"
fi

PROPOSAL=""
CHANGE_ID=""
DEVICE_HINT=""
WORKDIR=""
RUN_APPLY=false
RUN_ARCHIVE=false
MCP_PORT=8051
MODEL="${OPENSPEC_MODEL:-github_copilot/gpt-5-mini}"
BUILTIN_MCP="${BUILTIN_MCP_SERVER:-yes}"

# Colors
RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; BLUE="\033[0;34m"; NC="\033[0m"

usage() {
  sed -n '4,/^$/p' "$0" | sed 's/^# \{0,1\}//' | sed '/^$/d'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proposal) PROPOSAL="$2"; shift 2;;
    --change-id) CHANGE_ID="$2"; shift 2;;
    --device) DEVICE_HINT="$2"; shift 2;;
    --workdir) WORKDIR="$2"; shift 2;;
    --apply) RUN_APPLY=true; shift;;
    --archive) RUN_ARCHIVE=true; shift;;
    --port) MCP_PORT="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --builtin-mcp) BUILTIN_MCP="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo -e "${RED}Unknown arg: $1${NC}"; usage; exit 1;;
  esac
done

start_mcp() {
  if [[ "$BUILTIN_MCP" != "yes" ]]; then
    echo -e "${YELLOW}⚠️  Skipping MCP server startup (BUILTIN_MCP_SERVER=no)${NC}"
    echo "   To enable MCP servers, run with: --builtin-mcp yes"
    return 0
  fi
  echo -e "${BLUE}🚀 Starting MCP servers on port $MCP_PORT...${NC}"
  if "$MCP_SERVER_DIR/start_mcp_servers.sh" "$MCP_PORT"; then
    echo -e "${GREEN}🎉 MCP servers started successfully!${NC}"
  else
    echo -e "${RED}❌ Failed to start MCP servers${NC}"; exit 1
  fi
}

stop_mcp() {
  if [[ "$BUILTIN_MCP" != "yes" ]]; then
    return 0
  fi
  echo -e "${YELLOW}🛑 Cleaning up MCP servers...${NC}"
  "$MCP_SERVER_DIR/stop_mcp_servers.sh"
}

trap stop_mcp EXIT

# Export environment for sub-agents
export MCP_PORT="$MCP_PORT"
export OPENSPEC_MODEL="$MODEL"

# Start MCP server
start_mcp

# Set working directory (default to current directory)
WORKDIR="${WORKDIR:-$(pwd)}"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo -e "${BLUE}Working directory: $WORKDIR${NC}"

# Prepare sub-agent directories (ADK expects a package with root_agent)
PROPOSAL_DIR="$WORKDIR/adk_openspec_proposal_agent"
APPLY_DIR="$WORKDIR/adk_openspec_apply_agent"
ARCHIVE_DIR="$WORKDIR/adk_openspec_archive_agent"

prepare_agent_dir() {
  local target_dir="$1"; local import_path="$2"
  mkdir -p "$target_dir"
  cat > "$target_dir/agent.py" <<EOF
import sys, os
sys.path.insert(0, '$SAMPLES_DIR')
from $import_path import root_agent
EOF
}

# Resolve change id via /proposal if not provided
if [[ -z "$CHANGE_ID" ]]; then
  if [[ -z "$PROPOSAL" ]]; then
    echo -e "${RED}Either --change-id or --proposal must be provided.${NC}"; exit 1
  fi
  echo -e "${BLUE}🧩 Running /proposal to generate change id...${NC}"
  prepare_agent_dir "$PROPOSAL_DIR" "openspec_integration.proposal_agent"
  # If proposal is a readable file, read its content
  if [[ -f "$PROPOSAL" ]]; then
    echo -e "${BLUE}Reading proposal from file: $PROPOSAL${NC}"
    PROPOSAL_TEXT=$(cat "$PROPOSAL")
  else
    PROPOSAL_TEXT="$PROPOSAL"
  fi
  PROPOSAL_CMD="/proposal ${PROPOSAL_TEXT}"
  if [[ -n "$DEVICE_HINT" ]]; then
    PROPOSAL_CMD+=" --device ${DEVICE_HINT}"
  fi
  set +e
  PROPOSAL_OUTPUT=$(printf "%s\nexit\n" "$PROPOSAL_CMD" | OPENSPEC_MODEL="$MODEL" "$ADK_BIN" run "$PROPOSAL_DIR" 2>&1)
  STATUS=$?
  set -e
  
  # Save proposal output to log file
  PROPOSAL_LOG="$PROPOSAL_DIR/proposal.log"
  echo "$PROPOSAL_OUTPUT" > "$PROPOSAL_LOG"
  echo -e "${BLUE}📝 Proposal log saved: $PROPOSAL_LOG${NC}"
  
  if [[ $STATUS -ne 0 ]]; then
    echo -e "${RED}❌ /proposal failed. Output:${NC}"; echo "$PROPOSAL_OUTPUT"; exit 1
  fi
  # Extract change_id from agent JSON responses in the output
  CHANGE_ID=$(echo "$PROPOSAL_OUTPUT" | grep -o '"change_id"[[:space:]]*:[[:space:]]*"[^"]\+"' | sed -n 's/.*"change_id"[[:space:]]*:[[:space:]]*"\([^"]\+\)".*/\1/p' | head -n1)
  if [[ -z "$CHANGE_ID" ]]; then
    echo -e "${RED}❌ Could not extract change_id from /proposal output.${NC}"; echo "$PROPOSAL_OUTPUT"; exit 1
  fi
  echo -e "${GREEN}✅ Resolved change id: ${CHANGE_ID}${NC}"
fi

# Run /apply if requested
if [[ "$RUN_APPLY" == true ]]; then
  echo -e "${BLUE}🔧 Running /apply for ${CHANGE_ID}...${NC}"
  prepare_agent_dir "$APPLY_DIR" "openspec_integration.apply_agent"
  
  set +e
  APPLY_OUTPUT=$(printf "/apply --id %s\nexit\n" "$CHANGE_ID" | OPENSPEC_MODEL="$MODEL" "$ADK_BIN" run "$APPLY_DIR" 2>&1)
  APPLY_STATUS=$?
  set -e
  
  # Save apply output to log file
  APPLY_LOG="$APPLY_DIR/apply.log"
  echo "$APPLY_OUTPUT" > "$APPLY_LOG"
  echo -e "${BLUE}📝 Apply log saved: $APPLY_LOG${NC}"
  
  if [[ $APPLY_STATUS -ne 0 ]]; then
    echo -e "${YELLOW}⚠️  /apply completed with warnings${NC}"
  else
    echo -e "${GREEN}✅ /apply completed successfully${NC}"
  fi
fi

# Run /archive if requested
if [[ "$RUN_ARCHIVE" == true ]]; then
  echo -e "${BLUE}📦 Running /archive for ${CHANGE_ID}...${NC}"
  prepare_agent_dir "$ARCHIVE_DIR" "openspec_integration.archive_agent"
  
  set +e
  ARCHIVE_OUTPUT=$(printf "/archive --id %s\nexit\n" "$CHANGE_ID" | OPENSPEC_MODEL="$MODEL" "$ADK_BIN" run "$ARCHIVE_DIR" 2>&1)
  ARCHIVE_STATUS=$?
  set -e
  
  # Save archive output to log file
  ARCHIVE_LOG="$ARCHIVE_DIR/archive.log"
  echo "$ARCHIVE_OUTPUT" > "$ARCHIVE_LOG"
  echo -e "${BLUE}📝 Archive log saved: $ARCHIVE_LOG${NC}"
  
  if [[ $ARCHIVE_STATUS -ne 0 ]]; then
    echo -e "${YELLOW}⚠️  /archive completed with warnings${NC}"
  else
    echo -e "${GREEN}✅ /archive completed successfully${NC}"
  fi
fi

echo -e "${GREEN}✔ Done.${NC}"
