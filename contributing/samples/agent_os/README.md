# Agent OS Integration with ADK

This directory contains the Agent OS integration with Google's Agent Development Kit (ADK) for Python. The integration provides a specialized agent that follows Agent OS workflows for spec-driven development.

## Overview

The Agent OS integration brings structured development workflows to ADK, enabling:

- **Spec-Driven Development**: Follow Agent OS specifications and create comprehensive technical documentation
- **File Operations**: Read, write, and manage project files efficiently
- **Code Quality**: Maintain high coding standards and best practices
- **Project Management**: Track tasks, create roadmaps, and manage project documentation
- **Git Workflow**: Handle version control operations following Agent OS conventions

## Files in this Directory

### Core Integration Files

- **`agent_os_agent.py`** - Main Agent OS Agent class that integrates with ADK
- **`agent_os_tools.py`** - Collection of tools for file operations, searching, and system commands
- **`agent.py`** - Agent configuration file for ADK compatibility

### Example Files

- **`agent_os_agent_example.py`** - Complete working example showing how to use the integration
- **`agent_os_agent_example_safe.py`** - Safe example that tests configuration without LLM calls
- **`claude_code_agent_example.py`** - Alternative example implementation

### Test Files

- **`test_agent_os_integration.py`** - Comprehensive integration tests
- **`test_simple_integration.py`** - Simple integration tests
- **`test_standalone.py`** - Standalone tests for tools without ADK dependencies

### Documentation

- **`README.md`** - This file
- **`AGENT_OS_INTEGRATION.md`** - Detailed integration documentation
- **`INTEGRATION_SUMMARY.md`** - Summary of the integration implementation

## Quick Start

### 1. Install Dependencies

```bash
# Install ADK Python
pip install google-adk

# Install Agent OS (follow their installation instructions)
# https://buildermethods.com/agent-os
```

### 2. Basic Usage

```python
from contributing.samples.agent_os.agent_os_agent import AgentOsAgent
from google.adk.runners import InMemoryRunner

# Create Agent OS Agent with Agent OS integration
agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/path/to/agent-os",
    project_path=".",
    model="github-copilot/gpt-5-mini"
)

# Add Agent OS subagents
agent.add_agent_os_subagents("/path/to/agent-os")

# Use with InMemoryRunner
runner = InMemoryRunner(agent)
response = await runner.run_async("Plan a new product using Agent OS workflows")
```

### 3. Run Tests

```bash
# Run integration tests
python test_agent_os_integration.py

# Run simple tests
python test_simple_integration.py

# Run standalone tests
python test_standalone.py
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

### Basic Example

```python
import asyncio
from contributing.samples.agent_os.agent_os_agent import AgentOsAgent
from google.adk.runners import InMemoryRunner

async def main():
    # Create agent
    agent = AgentOsAgent.create_with_agent_os_config(
        agent_os_path="/path/to/agent-os",
        project_path=".",
        model="github-copilot/gpt-5-mini"
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
from contributing.samples.agent_os.agent_os_tools import create_agent_os_toolset

# Create toolset
toolset = create_agent_os_toolset()

# Use individual tools
read_tool = toolset.tools[0]  # AgentOsReadTool
result = await read_tool.run_async(
    args={"file_path": "README.md"},
    tool_context=tool_context
)
```

## Testing

The integration includes comprehensive tests:

### Integration Tests
```bash
python test_agent_os_integration.py
```

### Simple Tests
```bash
python test_simple_integration.py
```

### Standalone Tests
```bash
python test_standalone.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the ADK source directory is in your Python path
2. **Agent OS Path Not Found**: Ensure the agent_os_path points to a valid Agent OS installation
3. **Tool Execution Errors**: Check file permissions and working directory
4. **Model Errors**: Verify your model configuration and API credentials

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
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
- [Agent OS Documentation](https://buildermethods.com/agent-os) - Official Agent OS documentation
- [ADK Documentation](https://github.com/google/adk-python) - ADK documentation
