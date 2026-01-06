#!/usr/bin/env bash

set -e

JSON_MODE=false
ARGS=()
for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        --help|-h) echo "Usage: $0 [--json] <device_name>"; exit 0 ;;
        *) ARGS+=("$arg") ;;
    esac
done

DEVICE_NAME="${ARGS[0]}"
if [ -z "$DEVICE_NAME" ]; then
    echo "Usage: $0 [--json] <device_name>" >&2
    exit 1
fi

# Function to find the repository root by searching for existing project markers
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.specify" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Resolve repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel)
    HAS_GIT=true
else
    REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
    if [ -z "$REPO_ROOT" ]; then
        # If no repository root found, use current directory
        REPO_ROOT="$(pwd)"
    fi
    HAS_GIT=false
fi

cd "$REPO_ROOT"

# Check if it is a git repo, if not create a git repo with "git init"
if [ "$HAS_GIT" = false ]; then
    git init
    >&2 echo "[device-init] Initialized new git repository at $REPO_ROOT"
    HAS_GIT=true
fi

# Create a git branch named "implement-[device-name]"
BRANCH_NAME="implement-${DEVICE_NAME}"

if [ "$HAS_GIT" = true ]; then
    git checkout -b "$BRANCH_NAME"
    >&2 echo "[device-init] Created and switched to branch: $BRANCH_NAME"
fi

# Create openspec directory and copy project.md
OPENSPEC_DIR="$REPO_ROOT/openspec"
mkdir -p "$OPENSPEC_DIR"

if [ -f "$REPO_ROOT/project.md" ]; then
    cp "$REPO_ROOT/project.md" "$OPENSPEC_DIR/project.md"
    >&2 echo "[device-init] Copied project.md to $OPENSPEC_DIR/project.md"
else
    >&2 echo "[device-init] Warning: project.md not found at $REPO_ROOT/project.md"
fi

# Return branch-name
if $JSON_MODE; then
    printf '{"BRANCH_NAME":"%s","DEVICE_NAME":"%s","REPO_ROOT":"%s"}\n' "$BRANCH_NAME" "$DEVICE_NAME" "$REPO_ROOT"
else
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "DEVICE_NAME: $DEVICE_NAME"
    echo "REPO_ROOT: $REPO_ROOT"
fi
