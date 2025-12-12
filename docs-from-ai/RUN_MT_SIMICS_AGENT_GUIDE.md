# Simics Agent Runner Guide

## Overview

The `run_mt_simics_agent.sh` script provides a simplified way to run the ADK Simics agent with session saving enabled. This script handles environment setup, MCP server management, and session persistence automatically.

## Prerequisites

### 1. ADK Virtual Environment

The script requires an ADK virtual environment at `.venv` in the project root:

```bash
# If not already created:
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Simics Agent

The `simics_agent` directory must exist in the project root.

### 3. Required Environment Variables

Before running the script, you must set up the following environment variables for LiteLLM API access:

```bash
export LITELLM_BASE_URL=http://model-service.aihub.intel.com
export LITELLM_API_KEY=<your-api-key>
export LITELLM_MODEL=litellm_proxy/"Claude Sonnet 4"
```

**Note:** To obtain your API key (`LITELLM_API_KEY`), please contact the agent owner.

You can add these to your shell configuration file (`~/.bashrc`, `~/.zshrc`, etc.) for persistence:

```bash
# Add to your shell rc file
export LITELLM_BASE_URL=http://model-service.aihub.intel.com
export LITELLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx  # Replace with your actual key
export LITELLM_MODEL=litellm_proxy/"Claude Sonnet 4"
```

### 4. Optional: MCP Server Port

By default, the script uses port 8051 for the MCP server. You can override this:

```bash
export MCP_PORT=8052  # Use a different port if needed
```

## Usage

### Basic Syntax

```bash
./run_mt_simics_agent.sh PROJECT_NAME INITIAL_PROMPT
```

### Arguments

- **PROJECT_NAME** (required): Name of your project. Used in the session name.
  - Format: Alphanumeric characters, underscores, and hyphens only
  - Examples: `wdt_test`, `timer_device`, `uart_model`

- **INITIAL_PROMPT** (required): Initial prompt for the agent
  - Can be a text string: `"Implement watchdog timer device"`
  - Can be a file path: `openspec-prompts/1.md`
  - If a file path is provided, the file contents will be used as the prompt

### Examples

#### Example 1: Run with a text prompt

```bash
./run_mt_simics_agent.sh wdt_test "Implement watchdog timer device with register interface"
```

#### Example 2: Run with a prompt from file

```bash
./run_mt_simics_agent.sh timer_device openspec-prompts/implementation.md
```

#### Example 3: Show help

```bash
./run_mt_simics_agent.sh --help
```

## Session Management

### Session Files

The script automatically saves session data with the following naming convention:

```
<PROJECT_NAME>_simics_agent.session.json
```

For example, if you run:
```bash
./run_mt_simics_agent.sh wdt_test "Implement WDT"
```

The session will be saved as:
```
wdt_test_simics_agent.session.json
```

### Session Location

Session files are saved in the current working directory where you run the script.

### Resuming Sessions

To resume a previous session, you can use the ADK session management features. The session ID follows the pattern: `<PROJECT_NAME>_simics_agent`

## MCP Server Management

The script automatically manages MCP (Model Context Protocol) servers:

1. **Checks** if MCP server is running on the configured port (default: 8051)
2. **Starts** MCP servers if not running
3. **Cleans up** MCP servers on exit (if started by this script)

This is handled automatically - no manual intervention required.

## Workflow

When you run the script, it performs the following steps:

1. ✅ Validates environment (ADK venv, simics_agent directory)
2. ✅ Validates arguments (project name, prompt)
3. ✅ Reads prompt from file (if file path provided)
4. ✅ Checks/starts MCP server
5. ✅ Runs ADK agent with session saving
6. ✅ Cleans up MCP servers on exit

## Complete Setup Example

```bash
# 1. Set up environment variables (one-time setup)
export LITELLM_BASE_URL=http://model-service.aihub.intel.com
export LITELLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx  # Get from agent owner
export LITELLM_MODEL=litellm_proxy/"Claude Sonnet 4"

# 2. Navigate to project directory
cd /path/to/adk-openspec

# 3. Ensure ADK virtual environment exists
source .venv/bin/activate

# 4. Run the agent
./run_mt_simics_agent.sh my_project "Implement my device"

# Session saved as: my_project_simics_agent.session.json
```

## Troubleshooting

### Error: ADK virtual environment not found

```bash
# Solution: Create and set up the virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Error: Simics agent not found

```bash
# Solution: Ensure simics_agent directory exists
ls -la simics_agent/
```

### Warning: MCP server failed to start

The script will continue running but with reduced functionality. Check:
- Port availability: `lsof -i :8051`
- MCP server scripts exist: `ls contributing/samples/spec_kit_integration/simics-mcp-server/`

### Error: LITELLM_API_KEY not set

```bash
# Solution: Export the required environment variables
export LITELLM_BASE_URL=http://model-service.aihub.intel.com
export LITELLM_API_KEY=<your-key>  # Contact agent owner for key
export LITELLM_MODEL=litellm_proxy/"Claude Sonnet 4"
```

## Advanced Configuration

### Custom MCP Port

```bash
export MCP_PORT=8052
./run_mt_simics_agent.sh my_project "My prompt"
```

### Using Different Models

Modify the `LITELLM_MODEL` environment variable:

```bash
export LITELLM_MODEL=litellm_proxy/"GPT-4"
./run_mt_simics_agent.sh my_project "My prompt"
```

## Contact

For API key access or other issues, please contact the agent owner.

## Related Documentation

- ADK Documentation: See main README.md
- OpenSpec Guide: See AGENTS.md
- Simics Integration: See contributing/samples/spec_kit_integration/
