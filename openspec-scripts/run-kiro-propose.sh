#!/bin/bash

# Run kiro-cli to create OpenSpec proposal and analyze the session
# Usage: ./run-kiro-propose.sh [workdir] [session-name]

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}

# Generate timestamp for session name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_NAME=${2:-kiro-proposal-session_${TIMESTAMP}.json}

# Resolve absolute paths
# If workdir is relative, resolve from current directory; if absolute, use as-is
if [[ "$WORKDIR" = /* ]]; then
  # Absolute path provided
  WORKDIR_ABS="$WORKDIR"
else
  # Relative path - resolve from current directory
  WORKDIR_ABS=$(realpath "$WORKDIR")
fi

POWER_MD="$REPO_ROOT/powers/openspec-propose/POWER.md"
VIEW_SCRIPT="$REPO_ROOT/view_kiro_session.py"

# Check if workdir exists
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Check if POWER.md exists
if [ ! -f "$POWER_MD" ]; then
  echo "❌ Error: POWER.md not found: $POWER_MD"
  exit 1
fi

# Check if view script exists
if [ ! -f "$VIEW_SCRIPT" ]; then
  echo "❌ Error: view_kiro_session.py not found: $VIEW_SCRIPT"
  exit 1
fi

echo "================================"
echo "🚀 Running Kiro CLI Proposal"
echo "================================"
echo "Working Directory: $WORKDIR_ABS"
echo "Power File: $POWER_MD"
echo "Session Name: $SESSION_NAME"
echo ""

# Change to working directory
cd "$WORKDIR_ABS"

# Create kiro-propose directory for session files
KIRO_DIR="$WORKDIR_ABS/kiro-propose"
mkdir -p "$KIRO_DIR"

echo "📁 Session directory: $KIRO_DIR"
echo ""

# Construct the prompt
PROMPT="Read $POWER_MD and propose to model a simple watchdog timer for Simics platform simulation by following the instructions in POWER.md"

echo "📝 Prompt:"
echo "$PROMPT"
echo ""

# Run kiro-cli
echo "🤖 Running kiro-cli..."
echo ""

# Run kiro-cli and save session
kiro-cli chat -a "$PROMPT" <<EOF
/save kiro-propose/$SESSION_NAME
/quit
EOF

# Check if session file was created
SESSION_FILE="$KIRO_DIR/$SESSION_NAME"
if [ ! -f "$SESSION_FILE" ]; then
  echo "❌ Error: Session file not created: $SESSION_FILE"
  exit 1
fi

echo ""
echo "✅ Session saved: $SESSION_FILE"
echo ""

# Analyze the session
echo "================================"
echo "📊 Analyzing Session"
echo "================================"
echo ""

# Strip .json extension and add .txt for the analysis file
SESSION_BASE="${SESSION_FILE%.json}"
ANALYSIS_FILE="${SESSION_BASE}.txt"

python3 "$VIEW_SCRIPT" "$SESSION_FILE" > "$ANALYSIS_FILE"

echo "✅ Analysis saved: $ANALYSIS_FILE"
echo ""

# Display summary
echo "================================"
echo "📋 Session Summary"
echo "================================"
echo ""

# Extract key metrics from the analysis
if [ -f "$ANALYSIS_FILE" ]; then
  # Show conversation turns
  grep "Conversation Turns:" "$ANALYSIS_FILE" || true
  
  # Show timing summary
  grep -A 3 "SESSION TIMING SUMMARY" "$ANALYSIS_FILE" | tail -3 || true
  
  # Show file modifications
  echo ""
  grep -A 10 "FILE MODIFICATIONS" "$ANALYSIS_FILE" | head -15 || true
  
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
echo "2. Check the proposal: ls -la openspec/changes/"
echo "3. Validate quality: Check requirement coverage in spec delta"
echo ""
