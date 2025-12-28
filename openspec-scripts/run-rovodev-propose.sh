#!/bin/bash

# Run acli rovodev to create a proposal and capture session
# Usage: ./run-rovodev-propose.sh [workdir] [--power <POWER_MD>]
#
# Options:
#   --power <POWER_MD>  Path to a POWER.md (or similar) to seed the assistant prompt
#   --help, -h          Show this help message

set -e

show_help() {
  cat << 'EOF'
Run acli rovodev to create a proposal and save the session

USAGE:
    ./run-rovodev-propose.sh [WORKDIR] [OPTIONS]

POSITIONAL ARGUMENTS:
    WORKDIR         Working directory (default: adk_openspec_project)

OPTIONS:
    --power <POWER_MD>   Use the given POWER file to seed the assistant prompt
    --help, -h           Show this help message and exit

BEHAVIOR:
    - Runs acli rovodev with --yolo flag
    - Sends proposal creation prompt
    - Captures session ID using /status command
    - Saves session log and session ID
EOF
}

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Defaults
WORKDIR=""
POWER_MD=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --power)
      POWER_MD="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      if [ -z "$WORKDIR" ]; then
        WORKDIR="$1"
      fi
      shift
      ;;
  esac
done

# Set default workdir
WORKDIR=${WORKDIR:-adk_openspec_project}

# Set default POWER_MD if not provided
if [ -z "$POWER_MD" ]; then
  DEFAULT_POWER_MD="$REPO_ROOT/powers/openspec-propose/POWER.md"
  if [ -f "$DEFAULT_POWER_MD" ]; then
    POWER_MD="$DEFAULT_POWER_MD"
    echo "Using default POWER.md: $POWER_MD"
  fi
fi

# Resolve WORKDIR to absolute
if [[ "$WORKDIR" = /* ]]; then
  WORKDIR_ABS="$WORKDIR"
else
  WORKDIR_ABS=$(realpath "$WORKDIR" 2>/dev/null || echo "$REPO_ROOT/$WORKDIR")
fi

# Check workdir
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Build prompt
PROMPT=""
if [ -n "$POWER_MD" ]; then
  if [ ! -f "$POWER_MD" ]; then
    echo "❌ Error: POWER file not found: $POWER_MD"
    exit 1
  fi
  PROMPT="Read $POWER_MD and propose to model a simple watchdog timer for Simics platform simulation by following the instructions in POWER.md"
else
  PROMPT="Create a proposal based on the current repository context."
fi

# Prepare output dir
cd "$WORKDIR_ABS"
ROVO_DIR="$WORKDIR_ABS/rovodev-propose"
mkdir -p "$ROVO_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_PATH="$ROVO_DIR/rovodev-propose_${TIMESTAMP}.log"

echo "================================"
echo "🚀 Running acli rovodev Proposal"
echo "================================"
echo "Working Directory: $WORKDIR_ABS"
[ -n "$POWER_MD" ] && echo "Power File: $POWER_MD"
echo "Log: $LOG_PATH"
echo ""

# Set acli command
ACLI_CMD_BIN="${ACLI_CMD:-$HOME/acli}"
export ACLI_CMD="$ACLI_CMD_BIN"

# Run acli rovodev with session helper
echo "Running acli rovodev session..."
# For propose, use longer timeout and send /status after agent completes
python3 "$SCRIPT_DIR/rovodev_session_helper.py" "$PROMPT" "/status" "/exit" 2>&1 | tee "$LOG_PATH"

echo ""
echo "Session log saved to: $LOG_PATH"

# Extract session ID from log
SESSION_ID=$(grep -oP 'Session ID:\s*\K[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' "$LOG_PATH" | head -1)

if [ -n "$SESSION_ID" ]; then
    echo ""
    echo "✅ Session ID: $SESSION_ID"
    
    # Check if session directory exists
    SESSIONS_DIR="${ROVODEV_SESSIONS_DIR:-$HOME/.rovodev/sessions}"
    if [ -d "$SESSIONS_DIR/$SESSION_ID" ]; then
        echo "   Session dir: $SESSIONS_DIR/$SESSION_ID"
    fi
    
    # Save session ID to a file
    echo "$SESSION_ID" > "$ROVO_DIR/last_session_id.txt"
    echo "   Session ID saved to: $ROVO_DIR/last_session_id.txt"
else
    echo "⚠️  Could not extract session ID from log"
    echo "   Showing last 30 lines of log:"
    tail -30 "$LOG_PATH"
fi

# Optional: Try to extract a change id by scanning the workdir structure
CHANGE_BASE="${WORKDIR_ABS}/openspec/changes"
LATEST_CHANGE=""
if [ -d "$CHANGE_BASE" ]; then
  LATEST_CHANGE=$(ls -1 "$CHANGE_BASE" 2>/dev/null | grep -v "^archive$" | tail -1 || true)
fi

echo ""
echo "================================"
echo "📋 Next Steps"
echo "================================"
echo "1) Review the session log saved above."
if [ -n "$LATEST_CHANGE" ]; then
  echo "2) Potential change detected: $LATEST_CHANGE"
fi

echo ""
# Output change id on the last line for orchestration (if detected)
[ -n "$LATEST_CHANGE" ] && echo "$LATEST_CHANGE"
