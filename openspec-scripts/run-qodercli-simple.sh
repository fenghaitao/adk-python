#!/bin/bash

# Minimal script to run qodercli and capture session ID
# Usage: ./run-qodercli-simple.sh [PROMPT]
#
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROMPT=${1:-"Hello"}

# Working directory is repo root; store sessions under ./qodercli-simple
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SESSION_DIR="$REPO_ROOT/qodercli-simple"
mkdir -p "$SESSION_DIR"

LOG_PATH="$SESSION_DIR/qodercli-simple_${TIMESTAMP}.log"
echo "Saving run log to: $LOG_PATH"
echo "Prompt: $PROMPT"
echo ""

QODERCLI_BIN="${QODERCLI_CMD:-qodercli}"
export QODERCLI_CMD="$QODERCLI_BIN"

# Use Python helper which properly handles TTY interaction
echo "Running qodercli session..."
echo ""

python3 "$SCRIPT_DIR/qodercli_session_helper.py" "$PROMPT" "/status" "/exit" 2>&1 | tee "$LOG_PATH"

echo ""
echo "Session log saved to: $LOG_PATH"

# Extract session ID from log - look for "Session ID" pattern (from /status command)
# Strip ANSI codes first for easier pattern matching
SESSION_ID=$(sed 's/\x1b\[[0-9;]*m//g' "$LOG_PATH" | grep -oP 'Session ID\s*:\s*\K[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)

if [ -n "$SESSION_ID" ]; then
    echo ""
    echo "✅ Session ID: $SESSION_ID"
    
    # Check if session directory exists
    SESSIONS_DIR="${QODERCLI_SESSIONS_DIR:-$HOME/.qoder/sessions}"
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
