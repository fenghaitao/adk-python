#!/bin/bash

# Run kiro-cli to create OpenSpec proposal and analyze the session
# Usage: ./run-kiro-propose.sh [workdir] [session-name] [--multi-spec-deltas]
#
# Options:
#   --multi-spec-deltas   Use multi-spec-deltas mode for complex devices (50+ requirements)
#                         Default: simple mode for standard proposals
#   --help, -h            Show this help message

set -e

# Function to display help
show_help() {
    cat << 'EOF'
Run Kiro CLI to create OpenSpec proposal and analyze the session

USAGE:
    ./run-kiro-propose.sh [WORKDIR] [SESSION_NAME] [OPTIONS]

POSITIONAL ARGUMENTS:
    WORKDIR         Working directory (default: adk_openspec_project)
    SESSION_NAME    Session filename (default: kiro-proposal-session_TIMESTAMP.json)

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
    ./run-kiro-propose.sh

    # Simple mode with custom workdir
    ./run-kiro-propose.sh myproject

    # Multi-spec-deltas mode for complex device
    ./run-kiro-propose.sh myproject --multi-spec-deltas

    # Multi-spec-deltas mode with custom session name
    ./run-kiro-propose.sh myproject my-session.json --multi-spec-deltas

    # Show help
    ./run-kiro-propose.sh --help

OUTPUT:
    - Session file: workdir/kiro-propose/SESSION_NAME
    - Analysis file: workdir/kiro-propose/SESSION_NAME.txt
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
SESSION_NAME=${SESSION_NAME:-kiro-proposal-session_${TIMESTAMP}.json}

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
  else
    echo "❌ Error: openspec-memories not found in repo: $REPO_MEMORIES"
    echo ""
    echo "The knowledge base is required for the propose agent."
    echo "Please ensure openspec-memories/ exists in the repository."
    exit 1
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
echo "Mode: $MODE_DESC"
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

# Extract change-id from the analysis or openspec/changes directory
LATEST_CHANGE=$(ls -t "$WORKDIR_ABS/openspec/changes/" 2>/dev/null | head -1)

if [ -n "$LATEST_CHANGE" ]; then
  echo "📋 Created Change ID: $LATEST_CHANGE"
  echo ""
fi

echo "Next steps:"
echo "1. Review the session: cat $ANALYSIS_FILE"
if [ -n "$LATEST_CHANGE" ]; then
  echo "2. Check the proposal: ls -la openspec/changes/$LATEST_CHANGE/"
  echo "3. Validate quality: openspec validate $LATEST_CHANGE --strict"
  echo "4. Apply the change: ./openspec-scripts/run-kiro-apply.sh $WORKDIR $LATEST_CHANGE"
else
  echo "2. Check the proposal: ls -la openspec/changes/"
  echo "3. Validate quality: Check requirement coverage in spec delta"
fi
echo ""

# Return the change ID for use by calling scripts
# Write to stdout on the last line so it can be captured
if [ -n "$LATEST_CHANGE" ]; then
  echo "$LATEST_CHANGE"
fi
