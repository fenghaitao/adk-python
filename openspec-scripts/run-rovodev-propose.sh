#!/bin/bash

# Run acli rovodev to create OpenSpec proposal and analyze the session
# Usage: ./run-rovodev-propose.sh [workdir] [session-name] [--multi-spec-deltas]
#
# Options:
#   --multi-spec-deltas   Use multi-spec-deltas mode for complex devices (50+ requirements)
#                         Default: simple mode for standard proposals
#   --help, -h            Show this help message

set -e

# Function to display help
show_help() {
    cat << 'EOF'
Run acli rovodev to create OpenSpec proposal and analyze the session

USAGE:
    ./run-rovodev-propose.sh [WORKDIR] [SESSION_NAME] [OPTIONS]

POSITIONAL ARGUMENTS:
    WORKDIR         Working directory (default: adk_openspec_project)
    SESSION_NAME    Session filename (default: rovodev-proposal-session_TIMESTAMP.log)

OPTIONS:
    --multi-spec-deltas   Use multi-spec-deltas mode for complex devices (50+ requirements)
                          - Uses powers/openspec-propose-multiple-spec-deltas/POWER.md
                          - Includes guidance for decomposing into multiple spec deltas
                          - Creates separate spec delta directories per capability
                          Default: simple mode for standard proposals
    --help, -h            Show this help message and exit

MODES:
    Simple Mode (default):
        - For devices with <50 requirements
        - Single capability with one spec delta
        - Uses powers/openspec-propose/POWER.md
        
    Multi-Spec-Deltas Mode (--multi-spec-deltas):
        - For complex devices with 50+ requirements
        - Multiple capabilities with separate spec deltas
        - Uses powers/openspec-propose-multiple-spec-deltas/POWER.md
        - Includes design.md for capability interactions

EXAMPLES:
    # Simple mode (default)
    ./run-rovodev-propose.sh

    # Simple mode with custom workdir
    ./run-rovodev-propose.sh myproject

    # Multi-spec-deltas mode for complex device
    ./run-rovodev-propose.sh myproject --multi-spec-deltas

    # Multi-spec-deltas mode with custom session name
    ./run-rovodev-propose.sh myproject my-session.log --multi-spec-deltas

    # Show help
    ./run-rovodev-propose.sh --help

OUTPUT:
    - Session file: workdir/rovodev-propose/SESSION_NAME
    - Session ID file: workdir/rovodev-propose/last_session_id.txt
    - Proposal: workdir/openspec/changes/CHANGE_ID/

EOF
}

# Check for help flag first
for arg in "$@"; do
    if [[ "$arg" == "--help" || "$arg" == "-h" ]]; then
        show_help
        exit 0
    fi
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
WORKDIR=""
SESSION_NAME=""
MULTI_SPEC_DELTAS=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --multi-spec-deltas)
      MULTI_SPEC_DELTAS=true
      shift
      ;;
    *)
      if [ -z "$WORKDIR" ]; then
        WORKDIR="$1"
      elif [ -z "$SESSION_NAME" ]; then
        SESSION_NAME="$1"
      fi
      shift
      ;;
  esac
done

# Use defaults if not provided
WORKDIR=${WORKDIR:-adk_openspec_project}

# Generate timestamp for session name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_NAME=${SESSION_NAME:-rovodev-proposal-session_${TIMESTAMP}.log}

# Resolve absolute paths
# If workdir is relative, resolve from current directory; if absolute, use as-is
if [[ "$WORKDIR" = /* ]]; then
  # Absolute path provided
  WORKDIR_ABS="$WORKDIR"
else
  # Relative path - resolve from current directory
  WORKDIR_ABS=$(realpath "$WORKDIR")
fi

# Select power file based on mode
if [ "$MULTI_SPEC_DELTAS" = true ]; then
  POWER_MD="$REPO_ROOT/powers/openspec-propose-multiple-spec-deltas/POWER.md"
  MODE_DESC="multi-spec-deltas (complex devices)"
else
  POWER_MD="$REPO_ROOT/powers/openspec-propose/POWER.md"
  MODE_DESC="simple (standard proposals)"
fi

# Check if workdir exists
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Check if openspec-memories exists in workdir, if not copy it
MEMORIES_DIR="$WORKDIR_ABS/openspec-memories"
REPO_MEMORIES="$REPO_ROOT/openspec-memories"

if [ ! -e "$MEMORIES_DIR" ]; then
  if [ -d "$REPO_MEMORIES" ]; then
    echo "📚 Copying openspec-memories to working directory..."
    cp -r "$REPO_MEMORIES" "$MEMORIES_DIR"
    echo "✅ openspec-memories copied: $REPO_MEMORIES -> $MEMORIES_DIR"
    echo ""
  else
    echo "❌ Error: openspec-memories not found in repo: $REPO_MEMORIES"
    echo ""
    echo "The knowledge base is required for the propose agent."
    echo "Please ensure openspec-memories/ exists in the repository."
    exit 1
  fi
elif [ -d "$MEMORIES_DIR" ]; then
  echo "✅ openspec-memories directory already exists"
  echo ""
fi

# Check if POWER.md exists
if [ ! -f "$POWER_MD" ]; then
  echo "❌ Error: POWER.md not found: $POWER_MD"
  exit 1
fi

# Prepare output dir
cd "$WORKDIR_ABS"
ROVO_DIR="$WORKDIR_ABS/rovodev-propose"
mkdir -p "$ROVO_DIR"

echo "================================"
echo "🚀 Running acli rovodev Proposal"
echo "================================"
echo "Working Directory: $WORKDIR_ABS"
echo "Mode: $MODE_DESC"
echo "Power File: $POWER_MD"
echo "Session Name: $SESSION_NAME"
echo ""

# Change to working directory
cd "$WORKDIR_ABS"

# Create rovodev-propose directory for session files
echo "📁 Session directory: $ROVO_DIR"
echo ""

# Construct the prompt based on mode
if [ "$MULTI_SPEC_DELTAS" = true ]; then
  # Complex prompt for multi-spec-deltas devices
  PROMPT="Read $POWER_MD and propose to model a complex watchdog timer device for Simics platform simulation by following the instructions in POWER.md. This is a complex device with 50+ requirements that should be decomposed into multiple capabilities with separate spec deltas."
else
  # Simple prompt for standard proposals (from main branch)
  PROMPT="Read $POWER_MD and propose to model a simple watchdog timer for Simics platform simulation by following the instructions in POWER.md"
fi

echo "📝 Prompt:"
echo "$PROMPT"
echo ""

# Set acli command
ACLI_CMD_BIN="${ACLI_CMD:-$HOME/acli}"
export ACLI_CMD="$ACLI_CMD_BIN"

LOG_PATH="$ROVO_DIR/$SESSION_NAME"

echo "🤖 Running acli rovodev..."
echo ""

# Run acli rovodev with session helper
python3 "$SCRIPT_DIR/rovodev_session_helper.py" "$PROMPT" "/status" "/exit" 2>&1 | tee "$LOG_PATH"

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

VIEW_ROVODEV_SCRIPT="$SCRIPT_DIR/view_rovodev_session.py"

# Check if view script exists
if [ ! -f "$VIEW_ROVODEV_SCRIPT" ]; then
  echo "❌ Error: view_rovodev_session.py not found: $VIEW_ROVODEV_SCRIPT"
  exit 1
fi

python3 "$VIEW_ROVODEV_SCRIPT" "$LOG_PATH"

echo "✅ Analysis saved: $ANALYSIS_FILE"
echo ""

# Extract session ID from log
SESSION_ID=$(grep -oP 'Session ID:\s*\K[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' "$LOG_PATH" | head -1)

if [ -n "$SESSION_ID" ]; then
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
fi

echo ""
echo "================================"
echo "📋 Session Summary"
echo "================================"
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

# Optional: Try to extract a change id by scanning the workdir structure
CHANGE_BASE="${WORKDIR_ABS}/openspec/changes"
LATEST_CHANGE=""
if [ -d "$CHANGE_BASE" ]; then
  LATEST_CHANGE=$(ls -1 "$CHANGE_BASE" 2>/dev/null | grep -v "^archive$" | tail -1 || true)
fi

echo ""
echo "Next steps:"
echo "1. Review the session: cat $ANALYSIS_FILE"
if [ -n "$LATEST_CHANGE" ]; then
  echo "2. Check the proposal: ls -la openspec/changes/$LATEST_CHANGE/"
  echo "3. Validate quality: openspec validate $LATEST_CHANGE --strict"
  echo "4. Apply the change: ./openspec-scripts/run-rovodev-apply.sh $WORKDIR $LATEST_CHANGE"
else
  echo "2. Check the proposal: ls -la openspec/changes/"
  echo "3. Validate quality: Check requirement coverage in spec delta"
fi
echo ""
# Output change id on the last line for orchestration (if detected)
[ -n "$LATEST_CHANGE" ] && echo "$LATEST_CHANGE"
