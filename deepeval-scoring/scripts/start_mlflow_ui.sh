#!/bin/bash

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script to start MLflow UI server

set -e

# Default port
DEFAULT_PORT=5002

# Parse command line arguments
PORT=${1:-$DEFAULT_PORT}

# Validate port is a number
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "❌ Error: Port must be a number"
  echo "Usage: $0 [PORT]"
  echo "Example: $0 5002"
  exit 1
fi

# Check if port is in valid range
if [ "$PORT" -lt 1024 ] || [ "$PORT" -gt 65535 ]; then
  echo "⚠️  Warning: Port $PORT might require special privileges or be invalid"
  echo "Recommended range: 1024-65535"
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

echo "🚀 Starting MLflow UI server..."
echo "📁 Project directory: $PROJECT_DIR"
echo "🌐 Port: $PORT"
echo ""

# Start MLflow UI (use resolved tracking URI from config)
PYTHON_SCRIPT="
import yaml
from pathlib import Path

config_path = Path('$PROJECT_DIR/config/mlflow_config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

tracking_uri = config['mlflow']['tracking_uri']
if '{{ PROJECT_ROOT }}' in tracking_uri:
    project_root = Path('$PROJECT_DIR').parent
    tracking_uri = tracking_uri.replace('{{ PROJECT_ROOT }}', str(project_root))

print(tracking_uri)
"

RESOLVED_URI=$(python -c "$PYTHON_SCRIPT")
echo "🗄️  MLflow tracking URI: $RESOLVED_URI"
echo "📊 MLflow UI will be available at: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start MLflow UI with the resolved tracking URI
mlflow ui --backend-store-uri "$RESOLVED_URI" --port "$PORT"