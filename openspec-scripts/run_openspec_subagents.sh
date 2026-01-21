#!/usr/bin/env bash
set -euo pipefail

# Run OpenSpec sub-agents (proposal -> apply -> archive) with Simics MCP server
#
# Usage examples:
#   ./run_openspec_subagents.sh \
#       --proposal "Implement watchdog timer device" \
#       --agent initial \
#       --change-id "123-implement-wdt" \
#       --device wdt \
#       --apply \
#       --archive
#
#   ./run_openspec_subagents.sh --proposal "Add product search" --agent initial --apply
#
#   ./run_openspec_subagents.sh \
#       --proposal openspec-prompts/refine-wdt-interrupt.md \
#       --agent refine \
#       --apply
#
# Options:
#   --proposal TITLE|FILE    Short summary/title for /proposal (string or file path) (required unless --change-id provided)
#   --change-id ID           Explicit change id to use (otherwise /proposal generates one)
#   --agent AGENT_TYPE       Agent type: initial|refine (default: initial)
#   --device NAME            Optional device name hint for id generation
#   --workdir DIR            Working directory for agent directories and logs (default: current directory)
#   --apply                  Run /apply after /proposal using the resolved change id
#   --archive                Run /archive after /apply using the same change id
#   --port PORT              MCP server port (default: 8051)
#   --model MODEL            Override model for sub-agents (default: env OPENSPEC_MODEL or github_copilot/gpt-5-mini)
#   --builtin-mcp yes|no     Start/stop the bundled MCP server (default: yes)
#   --save-session           Save session files (DEFAULT)
#   --no-save-session        Disable session saving
#
# Environment variables:
#   OPENSPEC_MODEL           Default model for agents
#   BUILTIN_MCP_SERVER       yes/no to enable bundled MCP server (overridden by --builtin-mcp)
#
# Notes:
# - Requires `adk run` available in PATH
# - Uses OpenSpec sub-agents in contributing/samples/openspec_integration/
# - Starts Simics MCP server unless disabled

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
AGENT_TYPE="initial"
DEVICE_HINT=""
WORKDIR=""
RUN_APPLY=false
RUN_ARCHIVE=false
MCP_PORT=8051
MODEL="${OPENSPEC_MODEL:-github_copilot/gpt-5-mini}"
BUILTIN_MCP="${BUILTIN_MCP_SERVER:-yes}"
SAVE_SESSION=true

# Colors
RED="\033[0;31m"; GREEN="\033[0;32m"; YELLOW="\033[1;33m"; BLUE="\033[0;34m"; NC="\033[0m"

usage() {
  sed -n '4,/^$/p' "$0" | sed 's/^# \{0,1\}//' | sed '/^$/d'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --proposal) PROPOSAL="$2"; shift 2;;
    --change-id) CHANGE_ID="$2"; shift 2;;
    --agent) AGENT_TYPE="$2"; shift 2;;
    --device) DEVICE_HINT="$2"; shift 2;;
    --workdir) WORKDIR="$2"; shift 2;;
    --apply) RUN_APPLY=true; shift;;
    --archive) RUN_ARCHIVE=true; shift;;
    --port) MCP_PORT="$2"; shift 2;;
    --model) MODEL="$2"; shift 2;;
    --builtin-mcp) BUILTIN_MCP="$2"; shift 2;;
    --save-session) SAVE_SESSION=true; shift;;
    --no-save-session) SAVE_SESSION=false; shift;;
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

# Get absolute path after cd
WORKDIR="$(pwd)"

echo -e "${BLUE}Working directory: $WORKDIR${NC}"

# Symlink openspec-memories folder to workdir if it exists
MEMORIES_SRC="$SCRIPT_DIR/../openspec-memories"
if [[ -d "$MEMORIES_SRC" ]]; then
  echo -e "${BLUE}📂 Symlinking openspec-memories to workdir...${NC}"
  ln -sf "$MEMORIES_SRC" "$WORKDIR/openspec-memories"
  echo -e "${GREEN}✅ openspec-memories symlinked to $WORKDIR/openspec-memories${NC}"
else
  echo -e "${YELLOW}⚠️  openspec-memories folder not found at $MEMORIES_SRC${NC}"
fi

# Prepare sub-agent directories (ADK expects a package with root_agent)
PROPOSAL_INITIAL_DIR="$WORKDIR/adk_openspec_proposal_initial_agent"
PROPOSAL_REFINE_DIR="$WORKDIR/adk_openspec_proposal_refine_agent"
APPLY_DIR="$WORKDIR/adk_openspec_apply_agent"
ARCHIVE_DIR="$WORKDIR/adk_openspec_archive_agent"

prepare_agent_dir() {
  local target_dir="$1"; local import_path="$2"
  mkdir -p "$target_dir"
  
  # Extract the last component (agent name) from import path
  # E.g., "openspec_integration.apply_agent" -> "apply_agent"
  local agent_name="${import_path##*.}"
  
  # Symlink {agent_name}_instruction.md from source to target directory
  INSTRUCTION_SRC="$SCRIPT_DIR/../contributing/samples/openspec_integration/${agent_name}_instruction.md"
  if [[ -f "$INSTRUCTION_SRC" ]]; then
    ln -sf "$INSTRUCTION_SRC" "$target_dir/$(basename "$INSTRUCTION_SRC")"
    echo -e "${GREEN}✅ Symlinked instruction file to $target_dir${NC}"
  else
    echo -e "${YELLOW}⚠️  Instruction file not found at $INSTRUCTION_SRC${NC}"
  fi

  cat > "$target_dir/agent.py" <<EOF
import sys, os
sys.path.insert(0, '$SAMPLES_DIR')
from $import_path import root_agent
EOF
}

# Validate agent type
case "$AGENT_TYPE" in
  initial|refine) ;;
  *) echo -e "${RED}Invalid agent type: $AGENT_TYPE. Must be 'initial' or 'refine'.${NC}"; exit 1;;
esac

# Resolve change id via /proposal if provided
if [[ -n "$PROPOSAL" ]] && [[ -z "$CHANGE_ID" ]]; then
  echo -e "${BLUE}🧩 Running /proposal with ${AGENT_TYPE} agent to generate change id...${NC}"
  
  # Choose the appropriate agent based on type
  if [[ "$AGENT_TYPE" == "initial" ]]; then
    PROPOSAL_DIR="$PROPOSAL_INITIAL_DIR"
    prepare_agent_dir "$PROPOSAL_DIR" "openspec_integration.proposal_initial_agent"
  else
    PROPOSAL_DIR="$PROPOSAL_REFINE_DIR"
    prepare_agent_dir "$PROPOSAL_DIR" "openspec_integration.proposal_refine_agent"
  fi
  # If proposal is a readable file, read its content
  if [[ -f "$PROPOSAL" ]]; then
    echo -e "${BLUE}Reading proposal from file: $PROPOSAL${NC}"
    PROPOSAL_TEXT=$(cat "$PROPOSAL")
  else
    PROPOSAL_TEXT="$PROPOSAL"
  fi
  
  # Convert newlines to literal \n so entire prompt is sent as single line
  # The LLM will still interpret \n as line breaks in the prompt
  SINGLE_LINE_PROPOSAL=$(echo "$PROPOSAL_TEXT" | awk '{printf "%s\\n", $0}' | sed 's/\\n$//')
  
  PROPOSAL_CMD="/proposal ${SINGLE_LINE_PROPOSAL}"
  if [[ -n "$DEVICE_HINT" ]]; then
    PROPOSAL_CMD+=" --device ${DEVICE_HINT}"
  fi
  
  # Build ADK command with session options
  ADK_PROPOSAL_CMD="$ADK_BIN run $PROPOSAL_DIR"
  if [[ "$SAVE_SESSION" == true ]]; then
    SESSION_ID="proposal_${CHANGE_ID:-$(date +%Y%m%d_%H%M%S)}"
    ADK_PROPOSAL_CMD="$ADK_PROPOSAL_CMD --save_session --session_id $SESSION_ID"
    echo -e "${BLUE}Session will be saved as: $PROPOSAL_DIR/${SESSION_ID}.session.json${NC}"
  fi
  
  # Save proposal output to log file while displaying it
  PROPOSAL_LOG="$PROPOSAL_DIR/proposal.log"
  
  set +e
  printf "%s\nexit\n" "$PROPOSAL_CMD" | OPENSPEC_MODEL="$MODEL" $ADK_PROPOSAL_CMD 2>&1 | tee "$PROPOSAL_LOG"
  STATUS=${PIPESTATUS[0]}
  set -e
  
  echo -e "${BLUE}📝 Proposal log saved: $PROPOSAL_LOG${NC}"
  
  if [[ $STATUS -ne 0 ]]; then
    echo -e "${RED}❌ /proposal failed. Check log: $PROPOSAL_LOG${NC}"; exit 1
  fi
  
  # Extract change_id from agent JSON responses in the log file
  CHANGE_ID=$(grep -o '"change_id"[[:space:]]*:[[:space:]]*"[^"]\+"' "$PROPOSAL_LOG" | sed -n 's/.*"change_id"[[:space:]]*:[[:space:]]*"\([^"]\+\)".*/\1/p' | head -n1)
  if [[ -z "$CHANGE_ID" ]]; then
    echo -e "${RED}❌ Could not extract change_id from /proposal output. Check log: $PROPOSAL_LOG${NC}"; exit 1
  fi
  echo -e "${GREEN}✅ Resolved change id: ${CHANGE_ID}${NC}"
  
  # Generate human-readable session dump if session was saved
  if [[ "$SAVE_SESSION" == true ]] && [[ -f "$PROPOSAL_DIR/${SESSION_ID}.session.json" ]]; then
    echo -e "${GREEN}Proposal session saved: $PROPOSAL_DIR/${SESSION_ID}.session.json${NC}"
    if [[ -f "$SCRIPT_DIR/../view_session.py" ]]; then
      echo "📄 Generating human-readable proposal session dump..."
      python3 "$SCRIPT_DIR/../view_session.py" "$PROPOSAL_DIR/${SESSION_ID}.session.json" > "$PROPOSAL_DIR/${SESSION_ID}.session.txt"
      if [[ -f "$PROPOSAL_DIR/${SESSION_ID}.session.txt" ]]; then
        echo -e "${GREEN}Human-readable proposal session saved: $PROPOSAL_DIR/${SESSION_ID}.session.txt${NC}"
      fi
    fi
  fi
fi

# If CHANGE_ID is still not set, try to find the most recent proposal log
if [[ -z "$CHANGE_ID" ]]; then
  echo -e "${BLUE}🔍 No change_id or proposal provided, searching for most recent proposal...${NC}"
  
  # Determine which proposal directory to check based on agent type
  if [[ "$AGENT_TYPE" == "initial" ]]; then
    SEARCH_PROPOSAL_DIR="$PROPOSAL_INITIAL_DIR"
  else
    SEARCH_PROPOSAL_DIR="$PROPOSAL_REFINE_DIR"
  fi
  
  # Look for the most recent proposal.log file
  if [[ -f "$SEARCH_PROPOSAL_DIR/proposal.log" ]]; then
    PROPOSAL_LOG="$SEARCH_PROPOSAL_DIR/proposal.log"
    echo -e "${BLUE}📝 Found proposal log: $PROPOSAL_LOG${NC}"
    
    # Extract change_id from the log file
    CHANGE_ID=$(grep -o '"change_id"[[:space:]]*:[[:space:]]*"[^"]\+"' "$PROPOSAL_LOG" | sed -n 's/.*"change_id"[[:space:]]*:[[:space:]]*"\([^"]\+\)".*/\1/p' | head -n1)
    
    if [[ -n "$CHANGE_ID" ]]; then
      echo -e "${GREEN}✅ Resolved change id from previous proposal: ${CHANGE_ID}${NC}"
    else
      echo -e "${YELLOW}⚠️  Could not extract change_id from proposal log${NC}"
    fi
  else
    echo -e "${YELLOW}⚠️  No previous proposal log found at $SEARCH_PROPOSAL_DIR/proposal.log${NC}"
  fi
fi

# Final check: if CHANGE_ID is still not set, show error
if [[ -z "$CHANGE_ID" ]]; then
  echo -e "${RED}❌ Failed to resolve change_id${NC}"
  echo -e "${RED}   Please provide either:${NC}"
  echo -e "${RED}   - --change-id <id> to use a specific change_id${NC}"
  echo -e "${RED}   - --proposal <text|file> to generate a new change_id${NC}"
  echo -e "${RED}   - Or ensure a previous proposal log exists with a change_id${NC}"
  exit 1
else
  # If CHANGE_ID was provided directly or resolved, log it
  if [[ -n "$PROPOSAL" ]]; then
    : # Already logged during proposal execution
  else
    echo -e "${GREEN}✅ Using change id: ${CHANGE_ID}${NC}"
  fi
fi

# Run /apply if requested
if [[ "$RUN_APPLY" == true ]]; then
  echo -e "${BLUE}🔧 Running /apply for ${CHANGE_ID}...${NC}"
  prepare_agent_dir "$APPLY_DIR" "openspec_integration.apply_agent"

  # Build ADK command with session options
  ADK_APPLY_CMD="$ADK_BIN run $APPLY_DIR"
  if [[ "$SAVE_SESSION" == true ]]; then
    APPLY_SESSION_ID="apply_${CHANGE_ID}_$(date +%Y%m%d_%H%M%S)"
    ADK_APPLY_CMD="$ADK_APPLY_CMD --save_session --session_id $APPLY_SESSION_ID"
    echo -e "${BLUE}Session will be saved as: $APPLY_DIR/${APPLY_SESSION_ID}.session.json${NC}"
  fi
  
  # Save apply output to log file while displaying it
  APPLY_LOG="$APPLY_DIR/apply.log"
  
  set +e
  printf "/apply --id %s\nexit\n" "$CHANGE_ID" | OPENSPEC_MODEL="$MODEL" $ADK_APPLY_CMD 2>&1 | tee "$APPLY_LOG"
  APPLY_STATUS=${PIPESTATUS[0]}
  set -e
  
  echo -e "${BLUE}📝 Apply log saved: $APPLY_LOG${NC}"
  
  if [[ $APPLY_STATUS -ne 0 ]]; then
    echo -e "${YELLOW}⚠️  /apply completed with warnings${NC}"
  else
    echo -e "${GREEN}✅ /apply completed successfully${NC}"
  fi
  
  # Generate human-readable session dump if session was saved
  if [[ "$SAVE_SESSION" == true ]] && [[ -f "$APPLY_DIR/${APPLY_SESSION_ID}.session.json" ]]; then
    echo -e "${GREEN}Apply session saved: $APPLY_DIR/${APPLY_SESSION_ID}.session.json${NC}"
    if [[ -f "$SCRIPT_DIR/../view_session.py" ]]; then
      echo "📄 Generating human-readable apply session dump..."
      python3 "$SCRIPT_DIR/../view_session.py" "$APPLY_DIR/${APPLY_SESSION_ID}.session.json" > "$APPLY_DIR/${APPLY_SESSION_ID}.session.txt"
      if [[ -f "$APPLY_DIR/${APPLY_SESSION_ID}.session.txt" ]]; then
        echo -e "${GREEN}Human-readable apply session saved: $APPLY_DIR/${APPLY_SESSION_ID}.session.txt${NC}"
      fi
    fi
  fi
fi

# Run /archive if requested
if [[ "$RUN_ARCHIVE" == true ]]; then
  echo -e "${BLUE}📦 Running /archive for ${CHANGE_ID}...${NC}"
  prepare_agent_dir "$ARCHIVE_DIR" "openspec_integration.archive_agent"
  
  # Build ADK command with session options
  ADK_ARCHIVE_CMD="$ADK_BIN run $ARCHIVE_DIR"
  if [[ "$SAVE_SESSION" == true ]]; then
    ARCHIVE_SESSION_ID="archive_${CHANGE_ID}_$(date +%Y%m%d_%H%M%S)"
    ADK_ARCHIVE_CMD="$ADK_ARCHIVE_CMD --save_session --session_id $ARCHIVE_SESSION_ID"
    echo -e "${BLUE}Session will be saved as: $ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.json${NC}"
  fi
  
  # Save archive output to log file while displaying it
  ARCHIVE_LOG="$ARCHIVE_DIR/archive.log"
  
  set +e
  printf "/archive --id %s\nexit\n" "$CHANGE_ID" | OPENSPEC_MODEL="$MODEL" $ADK_ARCHIVE_CMD 2>&1 | tee "$ARCHIVE_LOG"
  ARCHIVE_STATUS=${PIPESTATUS[0]}
  set -e
  
  echo -e "${BLUE}📝 Archive log saved: $ARCHIVE_LOG${NC}"
  
  if [[ $ARCHIVE_STATUS -ne 0 ]]; then
    echo -e "${YELLOW}⚠️  /archive completed with warnings${NC}"
  else
    echo -e "${GREEN}✅ /archive completed successfully${NC}"
  fi
  
  # Generate human-readable session dump if session was saved
  if [[ "$SAVE_SESSION" == true ]] && [[ -f "$ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.json" ]]; then
    echo -e "${GREEN}Archive session saved: $ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.json${NC}"
    if [[ -f "$SCRIPT_DIR/../view_session.py" ]]; then
      echo "📄 Generating human-readable archive session dump..."
      python3 "$SCRIPT_DIR/../view_session.py" "$ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.json" > "$ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.txt"
      if [[ -f "$ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.txt" ]]; then
        echo -e "${GREEN}Human-readable archive session saved: $ARCHIVE_DIR/${ARCHIVE_SESSION_ID}.session.txt${NC}"
      fi
    fi
  fi
fi

# Auto-commit changes if any were generated by apply agent
if [[ "$RUN_APPLY" == true ]] && [[ $APPLY_STATUS -eq 0 ]]; then
  echo -e "${BLUE}🔍 Checking for changes to commit...${NC}"
  
  # Check if we're in a git repository
  if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Not in a git repository, skipping auto-commit${NC}"
  else
    # Stage all changes in simics-project if it exists
    if [[ -d "simics-project" ]]; then
      git add simics-project/ 2>/dev/null || true
    fi
    
    # Check if there are staged changes
    if git diff --cached --quiet 2>/dev/null; then
      echo -e "${YELLOW}⚠️  No changes to commit${NC}"
    else
      # Prepare commit message with available context
      # PROPOSAL_TEXT may not be set if --change-id was provided directly
      if [[ -n "${PROPOSAL_TEXT:-}" ]]; then
        PROPOSAL_SUMMARY="$PROPOSAL_TEXT"
      elif [[ -n "${PROPOSAL:-}" ]]; then
        # If PROPOSAL is a file path, read it; otherwise use it directly
        if [[ -f "$PROPOSAL" ]]; then
          PROPOSAL_SUMMARY=$(cat "$PROPOSAL")
        else
          PROPOSAL_SUMMARY="$PROPOSAL"
        fi
      else
        PROPOSAL_SUMMARY="Changes for ${CHANGE_ID}"
      fi
      # Truncate proposal to first line or 80 chars for summary
      PROPOSAL_SUMMARY=$(echo "$PROPOSAL_SUMMARY" | head -n1 | cut -c1-80)
      
      COMMIT_MSG="feat(openspec): implement change: ${CHANGE_ID}

Changes:
- Applied OpenSpec agent changes for: ${PROPOSAL_SUMMARY}
- Change ID: ${CHANGE_ID}
- Agent type: ${AGENT_TYPE}
$(if [[ -n "$DEVICE_HINT" ]]; then echo "- Device: ${DEVICE_HINT}"; fi)

Rationale and Impact:
AI-driven implementation using OpenSpec ${AGENT_TYPE} proposal agent and apply agent.
All changes generated and validated by the agent pipeline (proposal → apply → archive)."
      
      if git commit -m "$COMMIT_MSG" 2>/dev/null; then
        echo -e "${GREEN}✅ OpenSpec agent changes committed to git${NC}"
        # Show the commit details
        COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null)
        echo -e "${GREEN}   Commit: $COMMIT_HASH${NC}"
        echo ""
        git --no-pager log -1 --stat 2>/dev/null || true
      else
        echo -e "${YELLOW}⚠️  Git commit failed (might need manual intervention)${NC}"
      fi
    fi
  fi
fi

echo -e "${GREEN}✔ Done.${NC}"
