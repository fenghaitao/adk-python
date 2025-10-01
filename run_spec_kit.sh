#!/bin/bash

# Spec-Kit Runner Script
# Usage: ./run_spec_kit.sh [PROJECT_NAME] [INITIAL_PROMPT]
# Example: ./run_spec_kit.sh myproject "Create a REST API for user management"
# If no project name is provided, defaults to 'adk_spec_kit_project'
# If no prompt is provided, starts interactive mode
# 
# NOTE: This script does NOT save sessions because:
# - SequentialAgent does not support session saving (not an LlmAgent)
# - Session saving only works with LlmAgent instances
# 
# For session saving with individual subagents, use:
#   ./run_spec_kit_phased.sh
# 
# The phased script runs each subagent separately and saves individual sessions:
# - specify_agent/PROJECT_NAME_specify.session.json
# - plan_agent/PROJECT_NAME_plan.session.json  
# - tasks_agent/PROJECT_NAME_tasks.session.json
# - implement_agent/PROJECT_NAME_implement.session.json

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up paths relative to script location
SPEC_KIT_DIR="$SCRIPT_DIR/spec-kit"
ADK_VENV="$SCRIPT_DIR/.venv"
SPEC_KIT_INTEGRATION_DIR="$SCRIPT_DIR/contributing/samples/spec_kit_integration"

# Check if spec-kit virtual environment exists
if [ ! -d "$SPEC_KIT_DIR/.venv" ]; then
    echo "Error: spec-kit virtual environment not found at $SPEC_KIT_DIR/.venv"
    echo "Please run 'cd $SPEC_KIT_DIR && python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if ADK virtual environment exists
if [ ! -d "$ADK_VENV" ]; then
    echo "Error: ADK virtual environment not found at $ADK_VENV"
    echo "Please run 'python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if spec-kit integration directory exists
if [ ! -d "$SPEC_KIT_INTEGRATION_DIR" ]; then
    echo "Error: Spec-Kit integration directory not found at $SPEC_KIT_INTEGRATION_DIR"
    exit 1
fi

echo "Running Spec-Kit initialization..."
echo "Spec-Kit directory: $SPEC_KIT_DIR"
echo "ADK directory: $SCRIPT_DIR"
echo "Integration directory: $SPEC_KIT_INTEGRATION_DIR"
echo ""

# Get project name from first argument, default to 'adk_spec_kit_project' if not provided
PROJECT_NAME="${1:-adk_spec_kit_project}"
# Get initial prompt from second argument (optional)
INITIAL_PROMPT="$2"

echo "Project name: $PROJECT_NAME"
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Initial prompt: $INITIAL_PROMPT"
fi
echo ""

# Initialize spec-kit project
# Remove existing project directory if it exists
if [ -d "$PROJECT_NAME" ]; then
    echo "Removing existing project directory: $PROJECT_NAME"
    rm -rf "$PROJECT_NAME"
fi
"$SPEC_KIT_DIR/.venv/bin/specify" init "$PROJECT_NAME" --ai adk --script sh

echo ""
echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

echo "Running ADK with Spec-Kit integration..."
echo "Note: This script uses the sequential multi-agent architecture"
echo "For session saving, use: ./run_spec_kit_phased.sh"

# Run ADK with spec-kit integration using sequential agent
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Starting with initial prompt..."
    echo "Using: sequential multi-agent workflow"
    echo "$INITIAL_PROMPT" | "$ADK_VENV/bin/adk" run "$SPEC_KIT_INTEGRATION_DIR"
else
    echo "Starting interactive mode..."
    echo "Using: sequential multi-agent workflow"
    "$ADK_VENV/bin/adk" run "$SPEC_KIT_INTEGRATION_DIR"
fi
