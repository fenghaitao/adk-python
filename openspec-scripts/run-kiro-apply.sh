#!/bin/bash

# Run kiro-cli to apply OpenSpec proposal and analyze the session
# Usage: ./run-kiro-apply.sh [workdir] [change-id] [session-name]

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
SESSION_NAME=${3:-kiro-apply-session_${TIMESTAMP}.json}

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
VIEW_SCRIPT="$REPO_ROOT/view_kiro_session.py"

# Check if workdir exists
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Verify openspec-memories exists (should have been created by run-kiro-propose.sh)
MEMORIES_DIR="$WORKDIR_ABS/openspec-memories"
if [ ! -e "$MEMORIES_DIR" ]; then
  echo "❌ Error: openspec-memories not found: $MEMORIES_DIR"
  echo ""
  echo "The knowledge base is required for the apply agent."
  echo "Please run ./openspec-scripts/run-kiro-propose.sh first to set up the workspace."
  exit 1
fi

# Check if MCP configuration exists in workdir, if not copy from repo
MCP_CONFIG="$WORKDIR_ABS/.kiro/settings/mcp.json"
REPO_MCP_CONFIG="$REPO_ROOT/.kiro/settings/mcp.json"

if [ ! -f "$MCP_CONFIG" ]; then
  if [ -f "$REPO_MCP_CONFIG" ]; then
    echo "⚙️  Copying MCP configuration..."
    mkdir -p "$(dirname "$MCP_CONFIG")"
    cp "$REPO_MCP_CONFIG" "$MCP_CONFIG"
    echo "✅ MCP config created: $MCP_CONFIG"
    echo ""
  else
    echo "❌ Error: MCP config not found in repo: $REPO_MCP_CONFIG"
    echo ""
    echo "The MCP configuration is required for the apply agent (build/test tools)."
    echo "Please ensure .kiro/settings/mcp.json exists in the repository."
    exit 1
  fi
else
  echo "✅ MCP configuration already exists"
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

# Check if change exists
CHANGE_DIR="$WORKDIR_ABS/openspec/changes/$CHANGE_ID"
if [ ! -d "$CHANGE_DIR" ]; then
  echo "❌ Error: Change not found: $CHANGE_DIR"
  echo ""
  echo "Available changes:"
  ls -1 "$WORKDIR_ABS/openspec/changes/" 2>/dev/null || echo "  (none)"
  exit 1
fi

echo "================================"
echo "🚀 Running Kiro CLI Apply"
echo "================================"
echo "Working Directory: $WORKDIR_ABS"
echo "Change ID: $CHANGE_ID"
echo "Power File: $POWER_MD"
echo "Session Name: $SESSION_NAME"
echo ""

# Change to working directory
cd "$WORKDIR_ABS"

# Create kiro-apply directory for session files
KIRO_DIR="$WORKDIR_ABS/kiro-apply"
mkdir -p "$KIRO_DIR"

echo "📁 Session directory: $KIRO_DIR"
echo ""

# Construct the prompt
PROMPT="Read $POWER_MD and apply change $CHANGE_ID by following the instructions in POWER.md"

echo "📝 Prompt:"
echo "$PROMPT"
echo ""

# Run kiro-cli
echo "🤖 Running kiro-cli..."
echo ""

# Run kiro-cli and save session
kiro-cli chat -a "$PROMPT" <<EOF
/chat save kiro-apply/$SESSION_NAME
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
echo "2. Check build status: cd simics-project && make <device-name>"
echo "3. Run tests: cd simics-project && ./bin/test-runner -v modules/<device-name>/test/"
echo "4. Review implementation: Check simics-project/modules/<device-name>/"
echo ""
