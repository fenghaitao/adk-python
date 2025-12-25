#!/bin/bash

# Run kiro-cli to create OpenSpec proposal with custom prompt
# Usage: ./run-kiro-propose-custom.sh [workdir] [prompt-file] [change-id]

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Use provided workdir or default to adk_openspec_project
WORKDIR=${1:-adk_openspec_project}

# Prompt file (required)
PROMPT_FILE=${2:-""}

# Change ID for the proposal (optional - will be auto-detected after creation)
CHANGE_ID=${3:-""}

if [ -z "$PROMPT_FILE" ]; then
  echo "❌ Error: Prompt file is required"
  echo "Usage: $0 [workdir] [prompt-file] [change-id]"
  echo ""
  echo "Examples:"
  echo "  $0 /path/to/workdir /path/to/prompt.txt"
  echo "  $0 /path/to/workdir /path/to/prompt.txt my-change-id"
  exit 1
fi

# Generate timestamp for session name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -n "$CHANGE_ID" ]; then
  SESSION_NAME="${CHANGE_ID}-session_${TIMESTAMP}.json"
else
  SESSION_NAME="proposal-session_${TIMESTAMP}.json"
fi

# Resolve absolute paths
if [[ "$WORKDIR" = /* ]]; then
  WORKDIR_ABS="$WORKDIR"
else
  WORKDIR_ABS=$(realpath "$WORKDIR")
fi

POWER_MD="$REPO_ROOT/powers/openspec-propose/POWER.md"
VIEW_SCRIPT="$REPO_ROOT/view_kiro_session.py"

# Check if workdir exists
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Check if openspec-memories exists in workdir, if not create symlink
MEMORIES_DIR="$WORKDIR_ABS/openspec-memories"
REPO_MEMORIES="$REPO_ROOT/openspec-memories"

if [ ! -e "$MEMORIES_DIR" ]; then
  if [ -d "$REPO_MEMORIES" ]; then
    echo "📚 Creating symlink to openspec-memories..."
    ln -s "$REPO_MEMORIES" "$MEMORIES_DIR"
    echo "✅ Symlink created: $MEMORIES_DIR -> $REPO_MEMORIES"
    echo ""
  fi
elif [ -L "$MEMORIES_DIR" ]; then
  echo "✅ openspec-memories symlink already exists"
  echo ""
elif [ -d "$MEMORIES_DIR" ]; then
  echo "✅ openspec-memories directory already exists"
  echo ""
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
echo "Prompt File: $PROMPT_FILE"
if [ -n "$CHANGE_ID" ]; then
  echo "Expected Change ID: $CHANGE_ID"
fi
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
if [ -n "$PROMPT_FILE" ] && [ -f "$PROMPT_FILE" ]; then
  echo "📄 Using custom prompt from: $PROMPT_FILE"
  PROMPT=$(cat "$PROMPT_FILE")
else
  echo "❌ Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

echo ""
echo "📝 Prompt:"
echo "$PROMPT"
echo ""

# Run kiro-cli
echo "🤖 Running kiro-cli..."
echo ""

# Run kiro-cli and save session
kiro-cli chat -a "$PROMPT" <<EOF
/chat save kiro-propose/$SESSION_NAME
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

# Auto-detect the created change-id from openspec/changes directory
if [ -z "$CHANGE_ID" ]; then
  LATEST_CHANGE=$(ls -t "$WORKDIR_ABS/openspec/changes/" 2>/dev/null | head -1)
  if [ -n "$LATEST_CHANGE" ]; then
    CHANGE_ID="$LATEST_CHANGE"
    echo "📋 Auto-detected Change ID: $CHANGE_ID"
  fi
else
  # Verify the expected change-id was created
  if [ -d "$WORKDIR_ABS/openspec/changes/$CHANGE_ID" ]; then
    echo "📋 Created Change ID: $CHANGE_ID"
  else
    echo "⚠️  Warning: Expected change directory not found at openspec/changes/$CHANGE_ID/"
    # Try to find what was actually created
    LATEST_CHANGE=$(ls -t "$WORKDIR_ABS/openspec/changes/" 2>/dev/null | head -1)
    if [ -n "$LATEST_CHANGE" ]; then
      echo "📋 Found Change ID: $LATEST_CHANGE"
      CHANGE_ID="$LATEST_CHANGE"
    fi
  fi
fi

if [ -n "$CHANGE_ID" ] && [ -d "$WORKDIR_ABS/openspec/changes/$CHANGE_ID" ]; then
  echo "📂 Location: openspec/changes/$CHANGE_ID/"
  echo ""
  echo "Next steps:"
  echo "1. Review the session: cat $ANALYSIS_FILE"
  echo "2. Check the proposal: ls -la openspec/changes/$CHANGE_ID/"
  echo "3. Validate quality: openspec validate $CHANGE_ID --strict"
  echo "4. Apply the change: ./openspec-scripts/run-kiro-apply.sh $WORKDIR $CHANGE_ID"
else
  echo "⚠️  Warning: Could not locate created change directory"
  echo "Check the session analysis for details: $ANALYSIS_FILE"
  echo ""
  echo "Next steps:"
  echo "1. Review the session: cat $ANALYSIS_FILE"
  echo "2. Check the proposal: ls -la openspec/changes/"
fi

echo ""
