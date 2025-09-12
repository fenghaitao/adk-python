# Agent OS YAML Configuration

This directory contains YAML-based configuration for the Agent OS integration with ADK. The YAML configuration provides a declarative way to define and manage Agent OS agents, their tools, subagents, and workflows.

## Files

- **`root_agent.yaml`** - Main configuration file defining the Agent OS agent
- **`yaml_loader.py`** - Python module for loading and parsing YAML configurations
- **`example_usage.py`** - Example script demonstrating how to use the YAML configuration
- **`README.md`** - This documentation file

## Quick Start

### 1. Basic Usage

```python
from yaml_loader import load_agent_from_yaml

# Load agent from default YAML configuration
agent = load_agent_from_yaml()

# Use with ADK runner
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(agent)
```

### 2. Advanced Usage

```python
from yaml_loader import AgentOsYamlLoader

# Load with custom configuration
loader = AgentOsYamlLoader("custom_config.yaml")

# Validate environment
if loader.validate_environment():
    agent = loader.create_agent()
    
    # Get available workflows
    workflows = loader.get_workflows()
    
    # Get runner configuration
    runner_config = loader.get_runner_config()
```

## Configuration Structure

### Agent Configuration

The main agent configuration is defined under the `agent` key:

```yaml
agent:
  name: "agent_os_agent"
  model: "iflow/Qwen3-Coder"
  description: "A specialized coding agent that follows Agent OS workflows"
  
  agent_os:
    path: "/path/to/agent-os"
    project_path: "."
    auto_load_config: true
    auto_add_subagents: true
  
  instruction: |
    Your agent instruction here...
  
  tools:
    - name: "agent_os_toolset"
      type: "AgentOsToolset"
      enabled: true
  
  subagents:
    enabled: true
    auto_add: true
    # Individual subagent configurations...
```

### Subagents Configuration

Each subagent can be individually configured:

```yaml
subagents:
  context_fetcher:
    name: "context_fetcher"
    model: "iflow/Qwen3-Coder"
    description: "Retrieves information from Agent OS documentation"
    enabled: true
  
  file_creator:
    name: "file_creator"
    model: "iflow/Qwen3-Coder"
    description: "Creates files and directories"
    enabled: true
  
  # ... other subagents
```

### Workflows Configuration

Define reusable workflows:

```yaml
workflows:
  product_planning:
    name: "Product Planning Workflow"
    description: "Plan and design new products"
    steps:
      - "context_analysis"
      - "requirement_gathering"
      - "spec_creation"
      - "task_breakdown"
      - "roadmap_creation"
  
  spec_creation:
    name: "Spec Creation Workflow"
    description: "Create comprehensive specifications"
    steps:
      - "requirement_analysis"
      - "technical_design"
      - "api_specification"
      - "database_schema"
      - "test_planning"
```

### Environment Variables

The configuration supports environment variable substitution:

```yaml
agent:
  agent_os:
    path: "${AGENT_OS_PATH}"  # Uses AGENT_OS_PATH environment variable
    project_path: "${PROJECT_PATH:-.}"  # Uses PROJECT_PATH or defaults to "."
```

### Model Configuration

Configure model parameters:

```yaml
agent:
  model_config:
    temperature: 0.7
    max_tokens: 4096
    top_p: 0.9
    frequency_penalty: 0.0
    presence_penalty: 0.0
```

### Logging Configuration

Configure logging behavior:

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "agent_os.log"
  console: true
```

## Environment Variables

### Required Variables

- `GOOGLE_API_KEY` - For Google Cloud APIs
- `AGENT_OS_PATH` - Path to Agent OS installation

### Optional Variables

- `PROJECT_PATH` - Override project path
- `MODEL_NAME` - Override model name
- `LOG_LEVEL` - Override log level

## Usage Examples

### Example 1: Basic Agent Creation

```python
from yaml_loader import load_agent_from_yaml

# Load agent from YAML
agent = load_agent_from_yaml()

# Use with runner
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(agent)

# Run conversation
response = await runner.run_async("Help me plan a new web application")
```

### Example 2: Custom Configuration

```python
from yaml_loader import AgentOsYamlLoader

# Load custom configuration
loader = AgentOsYamlLoader("my_custom_config.yaml")

# Validate environment
if not loader.validate_environment():
    print("Missing required environment variables")
    exit(1)

# Create agent
agent = loader.create_agent()

# Get workflows
workflows = loader.get_workflows()
for name, config in workflows.items():
    print(f"Workflow: {config['name']}")
```

### Example 3: Workflow Execution

```python
from yaml_loader import load_agent_from_yaml

agent = load_agent_from_yaml()
loader = AgentOsYamlLoader()

# Get available workflows
workflows = loader.get_workflows()

# Execute a specific workflow
workflow = workflows["product_planning"]
print(f"Executing: {workflow['name']}")
print(f"Steps: {' → '.join(workflow['steps'])}")
```

## Testing

Run the example script to test the YAML configuration:

```bash
cd contributing/samples/agent_os/yaml
python example_usage.py
```

This will:
1. Load the YAML configuration
2. Create an Agent OS agent
3. Validate the environment
4. Display available workflows
5. Test basic functionality

## Customization

### Creating Custom Configurations

1. Copy `root_agent.yaml` to create your custom configuration
2. Modify the settings as needed
3. Use the custom configuration:

```python
agent = load_agent_from_yaml("my_custom_config.yaml")
```

### Adding New Workflows

Add new workflows to the `workflows` section:

```yaml
workflows:
  my_custom_workflow:
    name: "My Custom Workflow"
    description: "Description of what this workflow does"
    steps:
      - "step1"
      - "step2"
      - "step3"
```

### Modifying Subagents

Enable/disable or configure individual subagents:

```yaml
subagents:
  context_fetcher:
    enabled: false  # Disable this subagent
  
  file_creator:
    model: "custom-model"  # Use different model
    enabled: true
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Ensure all required environment variables are set
2. **Invalid YAML Syntax**: Check YAML syntax and indentation
3. **File Not Found**: Verify the configuration file path is correct
4. **Import Errors**: Ensure all dependencies are installed

### Debug Mode

Enable debug logging by setting the log level in the configuration:

```yaml
logging:
  level: "DEBUG"
  console: true
```

### Validation

Use the built-in validation:

```python
loader = AgentOsYamlLoader()
if not loader.validate_environment():
    print("Environment validation failed")
```

## Integration with ADK

The YAML configuration integrates seamlessly with ADK:

- **Runners**: Use with `InMemoryRunner`, `FastAPIRunner`, etc.
- **Tools**: All Agent OS tools are automatically configured
- **Subagents**: Specialized subagents are automatically added
- **Workflows**: Predefined workflows are available for common tasks

## Best Practices

1. **Use Environment Variables**: For paths and sensitive configuration
2. **Validate Configuration**: Always validate before creating agents
3. **Modular Configuration**: Split complex configurations into multiple files
4. **Document Workflows**: Provide clear descriptions for custom workflows
5. **Test Thoroughly**: Test configurations in development before production

## License

This YAML configuration follows the same license as the Agent OS integration (Apache 2.0).
