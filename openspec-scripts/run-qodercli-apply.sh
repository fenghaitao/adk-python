#!/bin/bash

# Run qodercli to apply OpenSpec proposal and analyze the session
# Usage: ./run-qodercli-apply.sh [workdir] [change-id] [session-name]

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}

# Change ID is required
CHANGE_ID=${2}

if [ -z "$CHANGE_ID" ]; then
  echo "❌ Error: Change ID is required"
  echo "Usage: $0 [workdir] <change-id> [session-name]"
  echo ""
  echo "Example: $0 adk_openspec_project 001-implement-wdt"
  exit 1
fi

# Generate timestamp for session name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_NAME=${3:-qodercli-apply-session_${TIMESTAMP}.log}

# Resolve absolute paths
# If workdir is relative, resolve from current directory; if absolute, use as-is
if [[ "$WORKDIR" = /* ]]; then
  # Absolute path provided
  WORKDIR_ABS="$WORKDIR"
else
  # Relative path - resolve from current directory
  WORKDIR_ABS=$(realpath "$WORKDIR")
fi

POWER_MD="$REPO_ROOT/powers/openspec-apply/POWER.md"

# Check if workdir exists
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Verify openspec-memories exists (should have been created by run-qodercli-propose.sh)
MEMORIES_DIR="$WORKDIR_ABS/openspec-memories"
if [ ! -e "$MEMORIES_DIR" ]; then
  echo "❌ Error: openspec-memories not found: $MEMORIES_DIR"
  echo ""
  echo "The knowledge base is required for the apply agent."
  echo "Please run ./openspec-scripts/run-qodercli-propose.sh first to set up the workspace."
  exit 1
fi

# Check if POWER.md exists
if [ ! -f "$POWER_MD" ]; then
  echo "❌ Error: POWER.md not found: $POWER_MD"
  exit 1
fi

# Check if change exists
CHANGE_DIR="$WORKDIR_ABS/openspec/changes/$CHANGE_ID"
if [ ! -d "$CHANGE_DIR" ]; then
  echo "❌ Error: Change not found: $CHANGE_DIR"
  echo ""
  echo "Available changes:"
  ls -1 "$WORKDIR_ABS/openspec/changes/" 2>/dev/null || echo "  (none)"
  exit 1
fi

# Setup directories in workdir
cd "$WORKDIR_ABS"
QODER_DIR="$WORKDIR_ABS/qodercli-apply"
mkdir -p "$QODER_DIR"

echo "================================"
echo "🚀 Running qodercli Apply"
echo "================================"
echo "Working Directory: $WORKDIR_ABS"
echo "Change ID: $CHANGE_ID"
echo "Power File: $POWER_MD"
echo "Session Name: $SESSION_NAME"
echo ""

# Change to working directory
cd "$WORKDIR_ABS"

# Create qodercli-apply directory for session files
echo "📁 Session directory: $QODER_DIR"
echo ""

# Build prompt
PROMPT="Read $POWER_MD and apply change $CHANGE_ID by following the instructions in POWER.md"

echo "📝 Prompt:"
echo "$PROMPT"
echo ""

# Set qodercli command
QODERCLI_BIN="${QODERCLI_CMD:-qodercli}"
export QODERCLI_CMD="$QODERCLI_BIN"

LOG_PATH="$QODER_DIR/$SESSION_NAME"

echo "🤖 Running qodercli..."
echo ""

# Run qodercli with session helper
python3 "$SCRIPT_DIR/qodercli_session_helper.py" "$PROMPT" "/status" "/exit" 2>&1 | tee "$LOG_PATH"

# Check if session file was created
if [ ! -f "$LOG_PATH" ]; then
  echo "❌ Error: Session file not created: $LOG_PATH"
  exit 1
fi

echo ""
echo "✅ Session saved: $LOG_PATH"
echo ""

# Analyze the session
echo "================================"
echo "📊 Analyzing Session"
echo "================================"
echo ""

# Strip .log extension and add .txt for the analysis file
SESSION_BASE="${LOG_PATH%.log}"
ANALYSIS_FILE="${SESSION_BASE}.txt"

VIEW_QODERCLI_SCRIPT="$SCRIPT_DIR/view_qodercli_session.py"

# Check if view script exists
if [ ! -f "$VIEW_QODERCLI_SCRIPT" ]; then
  echo "❌ Error: view_qodercli_session.py not found: $VIEW_QODERCLI_SCRIPT"
  exit 1
fi

python3 "$VIEW_QODERCLI_SCRIPT" "$LOG_PATH"

echo "✅ Analysis saved: $ANALYSIS_FILE"
echo ""

# Extract session ID from log
SESSION_ID=$(sed 's/\x1b\[[0-9;]*m//g' "$LOG_PATH" | grep -oP 'Session ID\s*:\s*\K[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' | head -1)

if [ -n "$SESSION_ID" ]; then
    echo "✅ Session ID: $SESSION_ID"
    
    # Check if session directory exists
    SESSIONS_DIR="${QODERCLI_SESSIONS_DIR:-$HOME/.qoder/sessions}"
    if [ -d "$SESSIONS_DIR/$SESSION_ID" ]; then
        echo "   Session dir: $SESSIONS_DIR/$SESSION_ID"
    fi
    
    # Save session ID to a file
    echo "$SESSION_ID" > "$QODER_DIR/last_session_id.txt"
    echo "   Session ID saved to: $QODER_DIR/last_session_id.txt"
else
    echo "⚠️  Could not extract session ID from log"
fi

echo ""
# Display summary
echo "================================"
echo "📋 Session Summary"
echo "================================"
echo ""

# Extract key metrics from the analysis
if [ -f "$ANALYSIS_FILE" ]; then
  # Show conversation summary
  grep "Total Messages:" "$ANALYSIS_FILE" || true
  grep "User Messages:" "$ANALYSIS_FILE" || true
  grep "Assistant Messages:" "$ANALYSIS_FILE" || true
  
  # Show token usage
  grep "Total Tokens:" "$ANALYSIS_FILE" || true
  
  echo ""
  echo "📄 Full analysis available at: $ANALYSIS_FILE"
fi

echo ""
echo "================================"
echo "✅ Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Review the session: cat $ANALYSIS_FILE"
echo "2. Check build status: cd simics-project && make <device-name>"
echo "3. Run tests: cd simics-project && ./bin/test-runner -v modules/<device-name>/test/"
echo "4. Review implementation: Check simics-project/modules/<device-name>/"
echo ""
