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

# Setup script for iflow model configuration

set -e

echo "🔧 Setting up iflow model for Cognee-OpenSpec"
echo ""

# Check if API key is provided
if [ -z "$1" ]; then
  echo "Usage: ./setup_iflow.sh <your-iflow-api-key>"
  echo ""
  echo "Example:"
  echo "  ./setup_iflow.sh sk-abc123..."
  echo ""
  echo "Get your API key from: https://iflow.cn"
  exit 1
fi

API_KEY="$1"
MODEL="${2:-dashscope/qwen3-coder-plus}"

echo "📝 Configuring environment variables..."
export LLM_API_KEY="$API_KEY"
export LLM_MODEL="$MODEL"
export LLM_ENDPOINT="https://apis.iflow.cn/v1/"
export LLM_PROVIDER="custom"

# Note: iflow embeddings have tokenizer compatibility issues
# Using OpenAI embeddings is recommended (set OPENAI_API_KEY separately)
# If you have OpenAI API key, uncomment below:
# export EMBEDDING_API_KEY="$OPENAI_API_KEY"
# export EMBEDDING_MODEL="openai/text-embedding-3-small"
# export EMBEDDING_DIMENSIONS=1536

# Suppress warnings
export ENABLE_BACKEND_ACCESS_CONTROL=false
export LOG_LEVEL=ERROR

echo "✅ Configuration complete!"
echo ""
echo "Environment variables set:"
echo "  LLM_API_KEY: ${LLM_API_KEY:0:10}..."
echo "  LLM_MODEL: $LLM_MODEL"
echo "  LLM_ENDPOINT: $LLM_ENDPOINT"
echo "  LLM_PROVIDER: $LLM_PROVIDER"
echo ""
echo "🚀 You can now run:"
echo "  cognee-memory index openspec-memories --visualize"
echo "  cognee-memory search 'What is DML?'"
echo ""
echo "💡 To persist these settings, add them to ../cognee/.env"
