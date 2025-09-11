# Installation Guide

This guide will help you set up the Google ADK (Agent Development Kit) with Agent OS integration using `uv` for fast and reliable dependency management.

## Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/google/adk-python.git
cd adk-python
```

### 2. Create Virtual Environment with uv

```bash
uv venv
```

### 3. Activate Virtual Environment

```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
uv pip install -e .
```

This will install the ADK package in editable mode along with all required dependencies including:
- Google GenAI SDK
- LiteLLM for multi-provider LLM support
- FastAPI for web services
- And many more...

### 5. Run Agent OS Sample

```bash
adk run ./contributing/samples/agent_os
```

This will start an interactive CLI with the Agent OS Agent that includes:
- Agent OS workflows and tools
- Spec-driven development capabilities
- Product planning and documentation features
- Code generation with Agent OS standards

## Alternative Installation Methods

### Using pip (if uv is not available)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Development Installation

For development with additional tools:

```bash
uv pip install -e ".[dev,test]"
```

## Available Samples

The `contributing/samples/` directory contains several examples:

- `agent_os/` - Agent OS integration with full workflow support
- `core_basic_config/` - Basic agent configuration
- `multi_agent_basic_config/` - Multi-agent setup
- `workflow_agent_seq/` - Sequential workflow agents

## Troubleshooting

### Common Issues

1. **Permission Errors**: Make sure you have write permissions in the project directory
2. **Python Version**: Ensure you're using Python 3.9 or higher
3. **uv Not Found**: Install uv using `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Getting Help

- Check the [documentation](https://google.github.io/adk-docs/)
- Review the [examples](contributing/samples/)
- Open an issue on [GitHub](https://github.com/google/adk-python/issues)

## Next Steps

After installation, you can:

1. **Explore Examples**: Try different sample configurations
2. **Create Your Own Agent**: Use the Agent OS workflows for your projects
3. **Integrate with Services**: Connect to various LLM providers via LiteLLM
4. **Deploy**: Use the deployment tools for production environments

Happy coding! 🚀
