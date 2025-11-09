#!/bin/bash

# OpenSpec Runner Script
# Usage: ./run_openspec.sh [PROJECT_NAME] [INITIAL_PROMPT]
# Example: ./run_openspec.sh myproject "Create a REST API for user management"
# If no project name is provided, defaults to 'adk_openspec_project'
# If no prompt is provided, starts interactive mode
#
# This script initializes an OpenSpec project and runs the ADK agent with
# OpenSpec integration. It supports both TypeScript CLI (openspec) and
# Python port (uvx openspec) for initialization.

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set up paths relative to script location
ADK_VENV="$SCRIPT_DIR/.venv"
OPENSPEC_INTEGRATION_DIR="$SCRIPT_DIR/contributing/samples/openspec_integration"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if OpenSpec CLI is available
check_openspec_cli() {
    if command -v openspec &> /dev/null; then
        echo "TypeScript"
        return 0
    elif command -v uvx &> /dev/null; then
        echo "Python"
        return 0
    else
        return 1
    fi
}

# Check if ADK virtual environment exists
if [ ! -d "$ADK_VENV" ]; then
    echo -e "${RED}Error: ADK virtual environment not found at $ADK_VENV${NC}"
    echo "Please run 'python -m venv .venv && source .venv/bin/activate && pip install -e .'"
    exit 1
fi

# Check if openspec_integration directory exists
if [ ! -d "$OPENSPEC_INTEGRATION_DIR" ]; then
    echo -e "${RED}Error: OpenSpec integration directory not found at $OPENSPEC_INTEGRATION_DIR${NC}"
    exit 1
fi

echo "Running OpenSpec initialization..."
echo "ADK directory: $SCRIPT_DIR"
echo "Integration directory: $OPENSPEC_INTEGRATION_DIR"
echo ""

# Check for OpenSpec CLI
echo -e "${BLUE}🔍 Checking for OpenSpec CLI...${NC}"
OPENSPEC_TYPE=$(check_openspec_cli)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ OpenSpec CLI not found${NC}"
    echo ""
    echo "Please install OpenSpec using one of these methods:"
    echo ""
    echo "Option 1: TypeScript CLI (requires Node.js >= 20.19.0)"
    echo "  npm install -g @fission-ai/openspec@latest"
    echo ""
    echo "Option 2: Python port (requires uv)"
    echo "  # Install uv first: https://docs.astral.sh/uv/getting-started/installation/"
    echo "  # Then OpenSpec will be available via: uvx openspec"
    echo ""
    exit 1
fi

if [ "$OPENSPEC_TYPE" = "TypeScript" ]; then
    echo -e "${GREEN}✅ Found OpenSpec TypeScript CLI${NC}"
    OPENSPEC_CMD="openspec"
else
    echo -e "${GREEN}✅ Found OpenSpec Python port (uvx)${NC}"
    OPENSPEC_CMD="uvx openspec"
fi
echo ""

# Get project name from first argument, default to 'adk_openspec_project' if not provided
PROJECT_NAME="${1:-adk_openspec_project}"
# Get initial prompt from second argument (optional)
INITIAL_PROMPT="$2"

echo "Project name: $PROJECT_NAME"
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Initial prompt: $INITIAL_PROMPT"
fi
echo ""

# Initialize OpenSpec project
# Remove existing project directory if it exists
if [ -d "$PROJECT_NAME" ]; then
    echo -e "${YELLOW}⚠️  Removing existing project directory: $PROJECT_NAME${NC}"
    rm -rf "$PROJECT_NAME"
fi

echo -e "${BLUE}🚀 Initializing OpenSpec project...${NC}"
if [ "$OPENSPEC_TYPE" = "TypeScript" ]; then
    $OPENSPEC_CMD init "$PROJECT_NAME" --tools none
else
    uvx openspec init "$PROJECT_NAME" --tools none
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to initialize OpenSpec project${NC}"
    exit 1
fi

echo -e "${GREEN}✅ OpenSpec project initialized successfully${NC}"
echo ""

echo "Entering project directory: $PROJECT_NAME"
cd "$PROJECT_NAME"

echo "Running ADK with OpenSpec integration..."
echo ""

# Run ADK with openspec integration
if [ -n "$INITIAL_PROMPT" ]; then
    echo "Starting with initial prompt..."
    echo "$INITIAL_PROMPT" | "$ADK_VENV/bin/adk" run "$OPENSPEC_INTEGRATION_DIR"
else
    echo "Starting interactive mode..."
    "$ADK_VENV/bin/adk" run "$OPENSPEC_INTEGRATION_DIR"
fi
