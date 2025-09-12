# Python Configuration

This directory contains Python-based configuration files for the Agent OS integration with ADK.

## Files

- **`agent.py`** - Main agent configuration file for ADK compatibility
- **`agent_os_agent.py`** - Core Agent OS agent implementation
- **`agent_os_tools.py`** - Agent OS tools implementation
- **`__init__.py`** - Package initialization file

## Usage

### Basic Usage

The `agent.py` file provides a pre-configured Agent OS agent that can be used directly with ADK:

```python
# Import the pre-configured agent
from contributing.samples.agent_os.python.agent import root_agent

# Use with ADK runner
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(root_agent)

# Run conversations
response = await runner.run_async("Help me plan a new web application")
```

### Configuration

The `agent.py` file contains:

1. **Agent Creation**: Creates an Agent OS agent with default configuration
2. **Agent OS Integration**: Automatically loads Agent OS configuration
3. **Subagents**: Adds all 6 specialized Agent OS subagents
4. **ADK Compatibility**: Exports as `root_agent` for ADK tools compatibility

### Customization

To customize the agent configuration, modify the `agent.py` file:

```python
# Change the model
agent_os_agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/path/to/agent-os",
    project_path=".",
    name="my_custom_agent",
    model="your-custom-model",  # Change model here
)

# Add custom subagents or modify existing ones
# agent_os_agent.add_custom_subagent(...)
```

### Environment Variables

The configuration uses the following paths:
- `agent_os_path`: Path to Agent OS installation (default: "/home/hfeng1/agent-os")
- `project_path`: Current project path (default: ".")

You can override these by modifying the `agent.py` file or using environment variables.

## Integration with ADK

This Python configuration is designed to work seamlessly with ADK:

- **Runner Compatibility**: Works with `InMemoryRunner`, `FastAPIRunner`, etc.
- **Tool Integration**: All Agent OS tools are automatically configured
- **Subagent Support**: All 6 specialized subagents are pre-configured
- **Session Management**: Compatible with ADK session management

## Comparison with YAML Configuration

| Feature | Python (`agent.py`) | YAML (`yaml/root_agent.yaml`) |
|---------|-------------------|------------------------------|
| **Configuration** | Code-based | Declarative |
| **Customization** | Modify Python code | Modify YAML file |
| **Environment Variables** | Manual handling | Built-in support |
| **Validation** | Manual | Automatic |
| **Workflows** | Not included | Predefined workflows |
| **Complexity** | Simple | More features |

Choose the Python configuration for:
- Simple, straightforward setups
- Direct code modification
- Quick prototyping

Choose the YAML configuration for:
- Complex configurations
- Environment variable support
- Workflow management
- Production deployments

## Examples

### Example 1: Basic Usage

```python
from contributing.samples.agent_os.python.agent import root_agent
from google.adk.runners import InMemoryRunner

async def main():
    runner = InMemoryRunner(root_agent)
    response = await runner.run_async("Create a spec for user authentication")
    print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Example 2: Custom Configuration

```python
from contributing.samples.agent_os.agent_os_agent import AgentOsAgent

# Create custom agent
custom_agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/custom/path/to/agent-os",
    project_path="/custom/project/path",
    name="my_custom_agent",
    model="custom-model"
)

# Add subagents
custom_agent.add_agent_os_subagents("/custom/path/to/agent-os")

# Use with runner
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(custom_agent)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the parent directory is in your Python path
2. **Agent OS Path Not Found**: Verify the `agent_os_path` is correct
3. **Model Errors**: Check your model configuration and API credentials

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This Python configuration follows the same license as the Agent OS integration (Apache 2.0).
