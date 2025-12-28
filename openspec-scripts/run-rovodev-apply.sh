#!/bin/bash

# Run acli rovodev to apply a change and capture session ID
# Usage: ./run-rovodev-apply.sh <change-id> [--power <POWER_MD>]

set -e

# Help
show_help() {
  cat << 'EOF'
Run acli rovodev to apply a change and capture session ID

USAGE:
    ./run-rovodev-apply.sh <CHANGE_ID> [OPTIONS]

POSITIONAL ARGUMENTS:
    CHANGE_ID       Change identifier to apply (required)

OPTIONS:
    --power <POWER_MD>  Use the given POWER file (default: powers/openspec-apply/POWER.md)
    --help, -h          Show this help message and exit
EOF
}

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Defaults
CHANGE_ID=""
POWER_MD="$REPO_ROOT/powers/openspec-apply/POWER.md"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      show_help
      exit 0
      ;;
    --power)
      POWER_MD="$2"
      shift 2
      ;;
    *)
      if [ -z "$CHANGE_ID" ]; then
        CHANGE_ID="$1"
        shift
      else
        echo "❌ Error: Unknown argument: $1"
        show_help
        exit 1
      fi
      ;;
  esac
done

if [ -z "$CHANGE_ID" ]; then
  echo "❌ Error: CHANGE_ID is required"
  show_help
  exit 1
fi

# Verify POWER.md exists
if [ ! -f "$POWER_MD" ]; then
  echo "❌ Error: POWER file not found: $POWER_MD"
  exit 1
fi

# Setup directories
ROVO_DIR="$REPO_ROOT/rovodev-apply"
mkdir -p "$ROVO_DIR"
LOG_FILE="$ROVO_DIR/rovodev-apply_${TIMESTAMP}.log"
SESSION_ID_FILE="$ROVO_DIR/last_session_id.txt"

# Build prompt
PROMPT="Read $POWER_MD and apply change $CHANGE_ID by following the instructions in POWER.md"

echo "================================"
echo "🚀 Running acli rovodev Apply"
echo "================================"
echo "Change ID: $CHANGE_ID"
echo "Power File: $POWER_MD"
echo "Log File: $LOG_FILE"
echo ""

# Set acli command
ACLI_CMD_BIN="${ACLI_CMD:-$HOME/acli}"
export ACLI_CMD="$ACLI_CMD_BIN"

# Run acli rovodev with session helper
echo "Running acli rovodev session..."
python3 "$SCRIPT_DIR/rovodev_session_helper.py" "$PROMPT" "/status" "/exit" 2>&1 | tee "$LOG_FILE"

echo ""
echo "Session log saved to: $LOG_FILE"

# Extract session ID from log
SESSION_ID=$(grep -oP 'Session ID:\s*\K[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' "$LOG_FILE" | head -1)

if [ -n "$SESSION_ID" ]; then
    echo ""
    echo "✅ Session ID: $SESSION_ID"
    
    # Check if session directory exists
    SESSIONS_DIR="${ROVODEV_SESSIONS_DIR:-$HOME/.rovodev/sessions}"
    if [ -d "$SESSIONS_DIR/$SESSION_ID" ]; then
        echo "   Session dir: $SESSIONS_DIR/$SESSION_ID"
    fi
    
    # Save session ID to a file
    echo "$SESSION_ID" > "$SESSION_ID_FILE"
    echo "   Session ID saved to: $SESSION_ID_FILE"
else
    echo "⚠️  Could not extract session ID from log"
    echo "   Showing last 30 lines of log:"
    tail -30 "$LOG_FILE"
fi
echo ""
echo "================================"
echo "📋 Next Steps"
echo "================================"
echo "1) Review the session log and repository changes"
echo "2) Build, test, and validate results as appropriate"
