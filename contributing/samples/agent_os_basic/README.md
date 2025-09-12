# Agent OS Integration with ADK

This directory contains the Agent OS integration with Google's Agent Development Kit (ADK) for Python. The integration provides a specialized agent that follows Agent OS workflows for spec-driven development.

## Overview

The Agent OS integration brings structured development workflows to ADK, enabling:

- **Spec-Driven Development**: Follow Agent OS specifications and create comprehensive technical documentation
- **File Operations**: Read, write, and manage project files efficiently
- **Code Quality**: Maintain high coding standards and best practices
- **Project Management**: Track tasks, create roadmaps, and manage project documentation
- **Git Workflow**: Handle version control operations following Agent OS conventions

## Directory Structure

```
contributing/samples/agent_os_basic/
├── python/                    # Self-contained Python configuration
│   ├── __init__.py           # Package initialization
│   ├── agent.py              # Main agent configuration
│   ├── agent_os_agent.py     # Core agent implementation
│   ├── agent_os_tools.py     # Tools implementation
│   └── README.md             # Python configuration docs
├── yaml_agent/                # YAML agent configurations for adk run
│   ├── root_agent.yaml       # Full AgentOsAgent YAML config
│   └── README.md             # YAML configuration documentation
├── yaml/                      # YAML configuration folder (custom configs)
│   ├── root_agent.yaml       # YAML agent configuration
│   ├── yaml_loader.py        # YAML loader implementation
│   ├── example_usage.py      # YAML usage example
│   ├── test_yaml_integration.py
│   └── README.md             # YAML configuration docs
├── examples/                  # Example scripts
│   ├── agent_os_agent_example.py
│   └── agent_os_agent_example_safe.py
├── test/                      # Test scripts
│   ├── test_simple.py
│   ├── test_python_config.py
│   ├── test_simple_integration.py
│   ├── test_agent_os_integration.py
│   ├── test_standalone.py
│   └── test_tools_simple.py
├── demo_runner.py             # Interactive demo runner
├── AGENT_OS_INTEGRATION.md   # Detailed integration documentation
├── INTEGRATION_SUMMARY.md    # Summary of the integration implementation
└── README.md                 # This file
```

## Quick Start

### Option 1: Interactive Demo (Recommended)

```bash
# Run the interactive demo
cd contributing/samples/agent_os_basic
python demo_runner.py
```

### Option 2: Python Configuration

```bash
# Run with ADK CLI
adk run contributing/samples/agent_os_basic/python

# Or import in code
from contributing.samples.agent_os_basic.python import root_agent
```

### Option 3: YAML Agent Configuration

```bash
# Run with ADK CLI (YAML agent)
adk run contributing/samples/agent_os_basic/yaml_agent

# Or run specific YAML file
adk run contributing/samples/agent_os_basic/yaml_agent/root_agent.yaml
```

### Option 4: Custom YAML Configuration

```bash
# Run with ADK CLI (custom YAML)
adk run contributing/samples/agent_os_basic/yaml

# Or use the YAML loader
from contributing.samples.agent_os_basic.yaml.yaml_loader import load_agent_from_yaml
agent = load_agent_from_yaml("root_agent.yaml")
```

### Option 5: Direct Usage

```python
from contributing.samples.agent_os_basic.python.agent_os_agent import AgentOsAgent
from google.adk.runners import InMemoryRunner

# Create Agent OS Agent with Agent OS integration
agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/path/to/agent-os",
    project_path=".",
    model="iflow/Qwen3-Coder"
)

# Add Agent OS subagents
agent.add_agent_os_subagents("/path/to/agent-os")

# Use with InMemoryRunner
runner = InMemoryRunner(agent)
response = await runner.run_async("Plan a new product using Agent OS workflows")
```

## Installation

### Prerequisites

```bash
# Install ADK Python
pip install google-adk

# Install Agent OS (follow their installation instructions)
# https://buildermethods.com/agent-os
```

## Demo Runner

The `demo_runner.py` provides an interactive way to test all agent configurations:

### Features
- **Live Execution**: Tests both Python and YAML agents with real prompts
- **Comparative Testing**: Shows differences between agent implementations
- **Agent OS Commands**: Supports `@plan-product`, `@create-spec`, `@execute-tasks`, etc.
- **Tool Integration**: Demonstrates Agent OS tools in action
- **Error Handling**: Graceful handling of execution issues

### Usage
```bash
cd contributing/samples/agent_os_basic
python demo_runner.py
```

### Demo Output
The demo will show:
- ✅ Python Agent (AgentOsAgent): Full Agent OS integration with 6 sub-agents and 5 tools
- ✅ YAML Agent (LlmAgent): Standard ADK agent with Agent OS tools
- ✅ Simple YAML Agent: Alternative configuration option

## Testing

### Run Tests

```bash
# Interactive demo (recommended)
cd contributing/samples/agent_os_basic
python demo_runner.py

# Test Python configuration
cd contributing/samples/agent_os_basic/test
python test_simple.py
python test_tools_simple.py

# Test YAML configuration
cd contributing/samples/agent_os_basic/yaml
python test_yaml_integration.py

# Test examples
cd contributing/samples/agent_os_basic/examples
python agent_os_agent_example_safe.py
```

## Available Tools

The integration provides the following tools:

### File Operations
- **`read_file`**: Read file contents
- **`write_file`**: Create or update files with overwrite protection
- **`grep_search`**: Search for patterns in files using grep
- **`glob_search`**: Find files matching glob patterns

### System Operations
- **`bash_command`**: Execute shell commands with timeout support

## Specialized Subagents

The Agent OS Agent includes six specialized subagents:

### Context Fetcher
- Retrieves information from Agent OS documentation
- Avoids duplication by checking existing context
- Uses smart extraction for targeted searches

### File Creator
- Creates files and directories following Agent OS conventions
- Applies standard templates based on file type
- Handles batch file creation operations

### Project Manager
- Tracks task completion and project progress
- Updates roadmap and task documentation
- Manages project tracking files

### Git Workflow
- Handles git operations following Agent OS conventions
- Manages branch naming and commit messages
- Creates pull requests with proper descriptions

### Test Runner
- Runs tests and analyzes failures for the current task
- Provides detailed failure analysis without making fixes
- Returns control to main agent after analysis

### Date Checker
- Determines and outputs today's date in YYYY-MM-DD format
- Uses file system timestamps for accurate date determination
- Checks context first to avoid duplication

## Agent OS Workflows

The integration supports all major Agent OS workflows:

### Product Planning
```python
response = await runner.run_async("Plan a new task management application with user authentication and project tracking features")
```

### Spec Creation
```python
response = await runner.run_async("Create a spec for user authentication feature with email/password login and password reset")
```

### Task Execution
```python
response = await runner.run_async("Execute the tasks for the user authentication feature")
```

### Code Analysis
```python
response = await runner.run_async("Analyze the current codebase and suggest improvements")
```

## Configuration

### Model Configuration

The Agent OS Agent uses `github-copilot/gpt-5-mini` as the default model. This can be customized:

```python
# Use custom model
agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/path/to/agent-os",
    project_path=".",
    model="your-custom-model"
)
```

### Agent OS Configuration

The agent automatically loads Agent OS configuration from:
- `{agent_os_path}/config.yml`
- `{agent_os_path}/instructions/`
- `{agent_os_path}/standards/`

## Examples

### Python Configuration Example

```python
# Using the pre-configured agent
from contributing.samples.agent_os.python import root_agent
from google.adk.runners import InMemoryRunner

# Create runner with pre-configured agent
runner = InMemoryRunner(root_agent)

# Run conversation
response = await runner.run_async("Help me plan a new web application")
print(response)
```

### YAML Configuration Example

```python
# Using YAML configuration
from contributing.samples.agent_os.yaml.yaml_loader import load_agent_from_yaml
from google.adk.runners import InMemoryRunner

# Load agent from YAML
agent = load_agent_from_yaml("root_agent.yaml")

# Create runner
runner = InMemoryRunner(agent)

# Run conversation
response = await runner.run_async("Create a spec for user authentication")
print(response)
```

### Direct Usage Example

```python
import asyncio
from contributing.samples.agent_os.python.agent_os_agent import AgentOsAgent
from google.adk.runners import InMemoryRunner

async def main():
    # Create agent
    agent = AgentOsAgent.create_with_agent_os_config(
        agent_os_path="/path/to/agent-os",
        project_path=".",
        model="iflow/Qwen3-Coder"
    )
    
    # Add subagents
    agent.add_agent_os_subagents("/path/to/agent-os")
    
    # Create runner
    runner = InMemoryRunner(agent)
    
    # Run conversation
    response = await runner.run_async("Help me plan a new web application")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Tool Usage Example

```python
from contributing.samples.agent_os.python.agent_os_tools import create_agent_os_toolset

# Create toolset
toolset = create_agent_os_toolset()

# Use individual tools
read_tool = toolset.tools[0]  # AgentOsReadTool
result = await read_tool.run_async(
    args={"file_path": "README.md"},
    tool_context=tool_context
)
```

## Configuration Options

### Python Configuration (`python/`)

The Python configuration provides a self-contained setup:

- **`agent.py`** - Pre-configured agent ready to use
- **`agent_os_agent.py`** - Core agent implementation
- **`agent_os_tools.py`** - Tools implementation
- **`__init__.py`** - Package initialization

**Usage:**
```bash
# Run with ADK CLI
adk run contributing/samples/agent_os_basic/python

# Import in code
from contributing.samples.agent_os_basic.python import root_agent
```

### YAML Agent Configuration (`yaml_agent/`)

The YAML agent configuration provides ADK CLI compatible setup:

- **`root_agent.yaml`** - Full AgentOsAgent YAML config
- **`README.md`** - YAML configuration documentation

**Usage:**
```bash
# Run with ADK CLI
adk run contributing/samples/agent_os_basic/yaml_agent

# Or run specific YAML file
adk run contributing/samples/agent_os_basic/yaml_agent/root_agent.yaml
```

### Custom YAML Configuration (`yaml/`)

The custom YAML configuration provides declarative setup:

- **`root_agent.yaml`** - Agent configuration in YAML format
- **`yaml_loader.py`** - YAML loader implementation
- **`example_usage.py`** - Usage examples

**Usage:**
```bash
# Run with ADK CLI
adk run contributing/samples/agent_os_basic/yaml

# Load from YAML
from contributing.samples.agent_os_basic.yaml.yaml_loader import load_agent_from_yaml
agent = load_agent_from_yaml("root_agent.yaml")
```

## Testing

The integration includes comprehensive tests in the `test/` directory:

### Python Configuration Tests
```bash
cd contributing/samples/agent_os_basic/test
python test_simple.py              # Basic agent test
python test_tools_simple.py        # Tools test
python test_python_config.py       # Full configuration test
```

### Integration Tests
```bash
cd contributing/samples/agent_os_basic/test
python test_agent_os_integration.py    # Full integration test
python test_simple_integration.py      # Simple integration test
python test_standalone.py              # Standalone tools test
```

### YAML Configuration Tests
```bash
cd contributing/samples/agent_os_basic/yaml
python test_yaml_integration.py    # YAML configuration test
```

### Example Tests
```bash
cd contributing/samples/agent_os_basic/examples
python agent_os_agent_example_safe.py  # Safe example test
```

## Troubleshooting

### Common Issues

1. **Import Errors**: 
   - For Python configuration: Ensure the `python/` directory is in your Python path
   - For YAML configuration: Ensure the `yaml/` directory is in your Python path
   - For direct usage: Ensure the ADK source directory is in your Python path

2. **Agent OS Path Not Found**: Ensure the agent_os_path points to a valid Agent OS installation

3. **Tool Execution Errors**: Check file permissions and working directory

4. **Model Errors**: Verify your model configuration and API credentials

5. **ADK CLI Issues**: 
   - Ensure you're running from the correct directory
   - Check that the agent configuration files exist
   - Verify ADK is properly installed

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Folder Structure Issues

If you encounter import errors, check the folder structure:

```bash
# Verify the structure
ls -la contributing/samples/agent_os_basic/
ls -la contributing/samples/agent_os_basic/python/
ls -la contributing/samples/agent_os_basic/yaml/
ls -la contributing/samples/agent_os_basic/test/
ls -la contributing/samples/agent_os_basic/examples/
```

## Contributing

To contribute to the Agent OS integration:

1. Follow the existing code patterns
2. Add tests for new functionality
3. Update documentation
4. Ensure compatibility with both ADK and Agent OS

## License

This integration follows the same license as ADK (Apache 2.0) and Agent OS.

## Related Documentation

- [AGENT_OS_INTEGRATION.md](AGENT_OS_INTEGRATION.md) - Detailed integration documentation
- [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - Summary of the integration implementation
- [python/README.md](python/README.md) - Python configuration documentation
- [yaml/README.md](yaml/README.md) - YAML configuration documentation
- [yaml_agent/README.md](yaml_agent/README.md) - YAML agent configuration documentation
- [Agent OS Documentation](https://buildermethods.com/agent-os) - Official Agent OS documentation
- [ADK Documentation](https://github.com/google/adk-python) - ADK documentation

## Migration Guide

If you're migrating from the old structure to the new organized structure:

### From Direct Imports
```python
# Old way
from google.adk.agents import AgentOsAgent
from google.adk.tools import create_agent_os_toolset

# New way
from contributing.samples.agent_os_basic.python.agent_os_agent import AgentOsAgent
from contributing.samples.agent_os_basic.python.agent_os_tools import create_agent_os_toolset
```

### From Agent Configuration
```python
# Old way
from contributing.samples.agent_os.agent import root_agent

# New way
from contributing.samples.agent_os_basic.python import root_agent
```

### From YAML Configuration
```python
# New YAML way
from contributing.samples.agent_os_basic.yaml.yaml_loader import load_agent_from_yaml
agent = load_agent_from_yaml("root_agent.yaml")
```

### New Demo Runner
```bash
# New interactive demo
cd contributing/samples/agent_os_basic
python demo_runner.py
```

### New YAML Agent Support
```bash
# New YAML agent for ADK CLI
adk run contributing/samples/agent_os_basic/yaml_agent
```
