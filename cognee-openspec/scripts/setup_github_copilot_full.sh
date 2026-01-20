#!/bin/bash
# Setup script for GitHub Copilot (both LLM and embeddings)

set -e

echo "🔧 Setting up GitHub Copilot for Cognee-OpenSpec"
echo "   LLM: github_copilot/gpt-4o"
echo "   Embeddings: github_copilot/text-embedding-3-small"
echo ""

# Configure GitHub Copilot for both LLM and embeddings
export LLM_MODEL="github_copilot/gpt-4o"
export LLM_PROVIDER="custom"
export EMBEDDING_MODEL="github_copilot/text-embedding-3-small"
export EMBEDDING_DIMENSIONS=1536

# Suppress warnings
export ENABLE_BACKEND_ACCESS_CONTROL=false
export LOG_LEVEL=ERROR

echo "✅ Configuration complete!"
echo ""
echo "Environment variables set:"
echo "  LLM_MODEL: $LLM_MODEL"
echo "  LLM_PROVIDER: $LLM_PROVIDER"
echo "  EMBEDDING_MODEL: $EMBEDDING_MODEL"
echo "  EMBEDDING_DIMENSIONS: $EMBEDDING_DIMENSIONS"
echo ""
echo "🚀 You can now run:"
echo "  ../.venv/bin/cognee-memory index ../openspec-memories --visualize"
echo "  ../.venv/bin/cognee-memory search 'What is DML?'"
echo ""
echo "💡 Note: GitHub Copilot uses OAuth authentication"
echo "   Make sure you have an active Copilot subscription"
