#!/usr/bin/env bash
set -euo pipefail

# Wrapper script for running apply_improve agent
# This is a convenience wrapper around run_improve.sh

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Forward all arguments to run_improve.sh with apply_improve level
exec "$SCRIPT_DIR/run_improve.sh" apply_improve "$@"
