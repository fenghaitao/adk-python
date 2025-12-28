#!/bin/bash

# Run rovodev CLI to apply a change and (optionally) analyze the session
# Usage: ./run-rovodev-apply.sh [workdir] <change-id> [session-name] [--power <POWER_MD>]

set -e

# Help
show_help() {
  cat << 'EOF'
Run rovodev CLI to apply a change and save the session

USAGE:
    ./run-rovodev-apply.sh [WORKDIR] <CHANGE_ID> [SESSION_NAME] [OPTIONS]

POSITIONAL ARGUMENTS:
    WORKDIR         Working directory (default: adk_openspec_project)
    CHANGE_ID       Change identifier to apply (required)
    SESSION_NAME    Session filename (default: rovodev-apply-session_TIMESTAMP.json)

OPTIONS:
    --power <POWER_MD>  Use the given POWER file to seed the assistant prompt
    --help, -h          Show this help message and exit
EOF
}

# Get script directory and repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Defaults and args
WORKDIR=${1:-adk_openspec_project}
CHANGE_ID=${2:-}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_NAME=${3:-rovodev-apply-session_${TIMESTAMP}.json}

# Parse options
POWER_MD=""
if [[ "$*" == *"--help"* ]] || [[ "$*" == *"-h"* ]]; then
  show_help; exit 0
fi
# Walk remaining args for options (skip first three positional if present)
shift $(( $# > 0 ? 0 : 0 ))
for arg in "$@"; do
  case "$arg" in
    --power)
      POWER_MD="$2"; shift 2;;
    -h|--help)
      show_help; exit 0;;
  esac
done

if [ -z "$CHANGE_ID" ]; then
  echo "❌ Error: CHANGE_ID is required"
  echo "Usage: $0 [workdir] <change-id> [session-name] [--power <POWER_MD>]"
  exit 1
fi

# Resolve WORKDIR to absolute
if [[ "$WORKDIR" = /* ]]; then
  WORKDIR_ABS="$WORKDIR"
else
  WORKDIR_ABS=$(realpath "$WORKDIR")
fi

# Rovodev CLI
ROVODEV_CLI=${ROVODEV_CLI:-"rovodev-cli"}

# Optional viewer
VIEW_SCRIPT_CANDIDATE="$REPO_ROOT/view_kiro_session.py"

# Verify workdir
if [ ! -d "$WORKDIR_ABS" ]; then
  echo "❌ Error: Working directory not found: $WORKDIR_ABS"
  exit 1
fi

# Build prompt
if [ -n "$POWER_MD" ]; then
  if [ ! -f "$POWER_MD" ]; then
    echo "❌ Error: POWER file not found: $POWER_MD"; exit 1
  fi
  PROMPT="Read $POWER_MD and apply change $CHANGE_ID by following the instructions."
else
  PROMPT="Apply change $CHANGE_ID to the repository by following standard procedures."
fi

cd "$WORKDIR_ABS"
ROVO_DIR="$WORKDIR_ABS/rovodev-apply"
mkdir -p "$ROVO_DIR"
SESSION_FILE="$ROVO_DIR/$SESSION_NAME"

echo "================================"
echo "🚀 Running Rovodev CLI Apply"
echo "================================"
echo "Working Directory: $WORKDIR_ABS"
echo "Change ID: $CHANGE_ID"
[ -n "$POWER_MD" ] && echo "Power File: $POWER_MD"
echo "Session Name: $SESSION_NAME"

# Run rovodev-cli and save session
"$ROVODEV_CLI" chat -a "$PROMPT" <<EOF
/chat save rovodev-apply/$SESSION_NAME
/quit
EOF

if [ ! -f "$SESSION_FILE" ]; then
  echo "❌ Error: Session file not created: $SESSION_FILE"; exit 1
fi

echo ""
echo "✅ Session saved: $SESSION_FILE"
echo ""

# Optional analysis
if [ -f "$VIEW_SCRIPT_CANDIDATE" ]; then
  SESSION_BASE="${SESSION_FILE%.json}"
  ANALYSIS_FILE="${SESSION_BASE}.txt"
  if python3 "$VIEW_SCRIPT_CANDIDATE" "$SESSION_FILE" > "$ANALYSIS_FILE" 2>/dev/null; then
    echo "📊 Analysis saved: $ANALYSIS_FILE"
  fi
fi

echo "================================"
echo "✅ Complete!"
echo "================================"
echo "Next steps:"
echo "1) Review the session analysis and repository changes."
echo "2) Build, test, and validate results as appropriate."
