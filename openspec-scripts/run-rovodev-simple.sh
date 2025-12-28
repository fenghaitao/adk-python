#!/bin/bash

# Minimal script to run acli rovodev and capture session ID
# Usage: ./run-rovodev-simple.sh [PROMPT]
#
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROMPT=${1:-"Hello"}

# Working directory is repo root; store sessions under ./rovodev-simple
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SESSION_DIR="$REPO_ROOT/rovodev-simple"
mkdir -p "$SESSION_DIR"

LOG_PATH="$SESSION_DIR/rovodev-simple_${TIMESTAMP}.log"
echo "Saving run log to: $LOG_PATH"
echo "Prompt: $PROMPT"
echo ""

ACLI_CMD_BIN="${ACLI_CMD:-$HOME/acli}"
export ACLI_CMD="$ACLI_CMD_BIN"

# Use Python helper which properly handles TTY interaction
echo "Running acli rovodev session..."
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
    echo "$SESSION_ID" > "$SESSION_DIR/last_session_id.txt"
    echo "   Session ID saved to: $SESSION_DIR/last_session_id.txt"
else
    echo "⚠️  Could not extract session ID from log"
    echo "   Showing last 30 lines of log:"
    tail -30 "$LOG_PATH"
fi
