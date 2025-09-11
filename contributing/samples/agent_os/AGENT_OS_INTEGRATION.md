# Agent OS Integration with ADK

This document describes how to use Agent OS workflows with Google's Agent Development Kit (ADK) for Python.

## Overview

The integration provides:
- **Agent OS Agent**: A specialized ADK agent that follows Agent OS workflows
- **Agent OS Tools**: ADK tools that implement Agent OS functionality
- **Subagent Architecture**: Specialized subagents for different aspects of development

## Installation

1. Install ADK Python:
```bash
pip install google-adk
```

2. Install Agent OS:
```bash
# Follow Agent OS installation instructions
# https://buildermethods.com/agent-os
```

## Quick Start

### Basic Usage

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
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(agent)
response = await runner.run_async("Plan a new product using Agent OS workflows")
```

### Advanced Configuration

```python
from contributing.samples.agent_os.agent_os_agent import AgentOsAgent

# Create with custom configuration
agent = AgentOsAgent(
    name="my_coding_agent",
    model="github-copilot/gpt-5-mini",
    instruction="Custom instruction for your specific use case",
    tools=[create_agent_os_toolset()],  # Add Agent OS tools
)

# Add specific subagents
agent.add_agent_os_subagents("/path/to/agent-os")
```

## Available Tools

The integration provides the following tools:

### File Operations
- `read_file`: Read file contents
- `write_file`: Create or update files
- `grep_search`: Search for patterns in files
- `glob_search`: Find files matching patterns

### System Operations
- `bash_command`: Execute shell commands

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

## Subagents

The Agent OS Agent includes specialized subagents:

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
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(agent)
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

The Agent OS Agent uses `github-copilot/gpt-5-mini` as the default model. This can be customized when creating the agent:

```python
# Use default model
agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/path/to/agent-os",
    project_path="."
)

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

### Custom Instructions

You can provide custom instructions while still using Agent OS workflows:

```python
agent = AgentOsAgent(
    instruction="""
    You are a specialized coding agent for web applications.
    Follow Agent OS workflows but focus on React and Node.js development.
    Always ensure accessibility and performance best practices.
    """,
    # ... other parameters
)
```

## Examples

See `examples/agent_os_agent_example.py` for a complete working example.

## Best Practices

1. **Use Agent OS Conventions**: Follow the established file naming and structure conventions
2. **Leverage Subagents**: Use the specialized subagents for their specific purposes
3. **Maintain Context**: The context fetcher helps avoid duplication and keeps responses focused
4. **Follow Git Workflows**: Use the git workflow subagent for proper version control
5. **Document Everything**: Use the file creator to maintain comprehensive documentation

## Troubleshooting

### Common Issues

1. **Agent OS Path Not Found**: Ensure the agent_os_path points to a valid Agent OS installation
2. **Tool Execution Errors**: Check file permissions and working directory
3. **Model Errors**: Verify your model configuration and API credentials
4. **Runner Initialization Errors**: Use `InMemoryRunner` instead of the base `Runner` class for proper initialization
5. **Method Call Errors**: The integration now uses static methods for class method calls to avoid `self` parameter issues

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
