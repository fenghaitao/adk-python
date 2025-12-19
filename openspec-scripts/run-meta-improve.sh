#!/usr/bin/env bash
set -euo pipefail

# Wrapper script for running meta_improve agent
# This is a convenience wrapper around run_improve.sh

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Forward all arguments to run_improve.sh with meta_improve level
exec "$SCRIPT_DIR/run_improve.sh" meta_improve "$@"
