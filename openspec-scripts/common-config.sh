#!/bin/bash

# Context management for ADK agents
export CONTEXT_ENABLE_CONDENSATION="true"
export CONTEXT_MAX_TOKENS="128000"
export CONTEXT_KEEP_SYSTEM_MESSAGES="2"
export CONTEXT_KEEP_RECENT_TURNS="3"
export CONTEXT_SUMMARIZATION_MODEL="github_copilot/gpt-5-mini"
export CONTEXT_SUMMARY_PROMPT_TYPE="vscode"
export ADK_ROOT=~/adk-python
export BUILTIN_MCP_SERVER=no
export IFLOW_API_KEY="sk-fddb7adb2d7eb413b4da655e16be70f7"
