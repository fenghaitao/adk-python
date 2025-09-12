# Agent OS Basic - YAML Configuration

This directory now provides two ways to run the Agent OS integration with ADK:

## 1. Python Configuration (Original)

The `python/` directory contains the original Python-based configuration:

```bash
# Run with ADK CLI
adk run contributing/samples/agent_os_basic/python

# Or import in code
from contributing.samples.agent_os_basic.python import root_agent
```

## 2. YAML Configuration (New)

Two YAML configurations are available for `adk run`:

### Option A: Full AgentOsAgent (root_agent.yaml)

Uses the custom `AgentOsAgent` class with full Agent OS integration:

```bash
adk run contributing/samples/agent_os_basic/yaml_agent/root_agent.yaml
```

**Features:**
- Full Agent OS workflow support
- Automatic subagent loading
- Agent OS-specific configuration
- All Agent OS tools included

### Option B: Simple LlmAgent (root_agent_simple.yaml)

Uses standard `LlmAgent` with Agent OS tools:

```bash
adk run contributing/samples/agent_os_basic/yaml_agent/root_agent_simple.yaml
```

**Features:**
- Standard ADK agent with Agent OS tools
- Simpler configuration
- Better compatibility with ADK CLI
- Core Agent OS functionality

## Configuration Details

### Agent OS Settings

Both YAML configurations support these Agent OS settings:

```yaml
agent_os_path: "/home/hfeng1/agent-os"  # Path to Agent OS installation
project_path: "."                       # Current project path
```

### Model Configuration

```yaml
model: iflow/Qwen3-Coder
model_config:
  temperature: 0.7
  max_tokens: 4096
  top_p: 0.9
```

### Available Tools

Both configurations include these Agent OS tools:
- `read_file` - Read file contents
- `write_file` - Create or update files
- `grep_search` - Search for patterns in files
- `glob_search` - Find files matching patterns
- `bash_command` - Execute shell commands

## Usage Examples

### Basic Usage

```bash
# Using the full Agent OS agent
adk run contributing/samples/agent_os_basic/yaml_agent/root_agent.yaml

# Using the simple configuration
adk run contributing/samples/agent_os_basic/yaml_agent/root_agent_simple.yaml

# Using Python configuration
adk run contributing/samples/agent_os_basic/python
```

### Programmatic Usage

```python
from google.adk.agents.config_agent_utils import from_config

# Load from YAML
agent = from_config('contributing/samples/agent_os_basic/yaml_agent/root_agent.yaml')

# Or use the simple version
agent = from_config('contributing/samples/agent_os_basic/yaml_agent/root_agent_simple.yaml')
```

## Directory Structure

```
agent_os_basic/
├── python/                    # Original Python configuration
│   ├── agent.py
│   ├── agent_os_agent.py
│   └── agent_os_tools.py
├── yaml/                      # YAML configuration folder (custom configs)
│   ├── root_agent.yaml
│   └── yaml_loader.py
├── yaml_agent/                # YAML agent configurations for adk run
│   ├── root_agent.yaml        # Full AgentOsAgent YAML config
│   ├── root_agent_simple.yaml # Simple LlmAgent YAML config
│   └── README.md              # YAML configuration documentation
├── examples/                  # Example scripts
├── test/                      # Test files
└── README.md                  # Main documentation
```

## Recommendations

- **For full Agent OS features**: Use `yaml_agent/root_agent.yaml`
- **For better ADK compatibility**: Use `yaml_agent/root_agent_simple.yaml`
- **For custom development**: Use the `python/` directory
- **For testing**: Use the `yaml/` directory with custom configurations

## Troubleshooting

If you encounter issues:

1. **Import errors**: Make sure the ADK source is in your Python path
2. **Agent OS path**: Update the `agent_os_path` in the YAML files
3. **Model errors**: Check that the model name is correct and accessible
4. **Tool errors**: Verify that Agent OS is properly installed

## Next Steps

1. Choose the configuration that best fits your needs
2. Update the `agent_os_path` to point to your Agent OS installation
3. Test with `adk run` to ensure everything works
4. Customize the configuration as needed for your project
