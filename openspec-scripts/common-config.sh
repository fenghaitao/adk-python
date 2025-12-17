#!/bin/bash

# Context management for ADK agents
export CONTEXT_ENABLE_CONDENSATION="true"
export CONTEXT_MAX_TOKENS="512000"
export CONTEXT_KEEP_SYSTEM_MESSAGES="2"
export CONTEXT_KEEP_RECENT_TURNS="3"
export CONTEXT_SUMMARIZATION_MODEL="iflow/qwen3-coder-plus"
export CONTEXT_SUMMARY_PROMPT_TYPE="vscode"
export ADK_ROOT=$(realpath "$(dirname "$(dirname "${BASH_SOURCE[0]}")")")
export BUILTIN_MCP_SERVER=no
export TMPDIR=~/tmp
echo "ADK_ROOT is set to $ADK_ROOT"
