#!/bin/bash

# Minimal script to run adal and capture session ID
# Usage: ./run-adal-simple.sh [PROMPT]
#
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
PROMPT=${1:-"Hello"}

# Working directory is repo root; store sessions under ./adal-simple
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SESSION_DIR="$REPO_ROOT/adal-simple"
mkdir -p "$SESSION_DIR"

LOG_PATH="$SESSION_DIR/adal-simple_${TIMESTAMP}.log"
echo "Saving run log to: $LOG_PATH"
echo "Prompt: $PROMPT"
echo ""

ADAL_BIN="${ADAL_CMD:-adal}"
export ADAL_CMD="$ADAL_BIN"

# Use Python helper which properly handles TTY interaction
echo "Running adal session..."
echo ""

python3 "$SCRIPT_DIR/adal_session_helper.py" "$PROMPT" "/exit" 2>&1 | tee "$LOG_PATH"

echo ""
echo "Session log saved to: $LOG_PATH"

# Extract session ID from log - look for session ID in /stats output
# Strip ANSI codes first for easier pattern matching
SESSION_ID=$(sed 's/\x1b\[[0-9;]*m//g' "$LOG_PATH" | grep -oP '(?:Session ID|conversation_id)[:\s]*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})' | grep -oP '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)

if [ -n "$SESSION_ID" ]; then
    echo ""
    echo "✅ Session ID: $SESSION_ID"
    
    # Check if session directory exists
    SESSIONS_DIR="${ADAL_SESSIONS_DIR:-$HOME/.adal/sessions}"
    
    # Check if session file exists
    if [ -f "$SESSIONS_DIR/conversation_$SESSION_ID.jsonl" ]; then
        echo "   Session file: $SESSIONS_DIR/conversation_$SESSION_ID.jsonl"
    fi
    
    # Save session ID to a file
    echo "$SESSION_ID" > "$SESSION_DIR/last_session_id.txt"
    echo "   Session ID saved to: $SESSION_DIR/last_session_id.txt"
else
    echo "⚠️  Could not extract session ID from log"
    echo "   Trying fallback: newest metadata file"
    
    # Fallback: Extract from newest metadata file
    SESSIONS_DIR="${ADAL_SESSIONS_DIR:-$HOME/.adal/sessions}"
    METADATA_FILE=$(ls -t "$SESSIONS_DIR"/*_metadata.json 2>/dev/null | head -1)
    
    if [ -n "$METADATA_FILE" ] && [ -f "$METADATA_FILE" ]; then
        SESSION_ID=$(grep -oP '"conversation_id":\s*"\K[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' "$METADATA_FILE" 2>/dev/null)
        
        if [ -n "$SESSION_ID" ]; then
            echo "   ✅ Session ID (from metadata): $SESSION_ID"
            echo "$SESSION_ID" > "$SESSION_DIR/last_session_id.txt"
        fi
    fi
fi
