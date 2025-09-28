# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Agent Development Kit (ADK) is Google's open-source, code-first Python toolkit for building, evaluating, and deploying AI agents. While optimized for Gemini and the Google ecosystem, ADK is model-agnostic and deployment-agnostic.

## Development Commands

### Environment Setup
```bash
# Install uv package manager (required)
# See: https://docs.astral.sh/uv/getting-started/installation/

# Create virtual environment (Python 3.11+ recommended)
uv venv --python "python3.11" ".venv"

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies with extras
uv sync --all-extras

# For accurate testing reproduction, use only required test extras
uv sync --extra test --extra eval --extra a2a
```

### Testing
```bash
# Run unit tests
pytest ./tests/unittests

# Run specific test file
pytest ./tests/unittests/test_<module>_<feature>.py

# Run evaluation on agents
adk eval samples_for_testing/hello_world samples_for_testing/hello_world/hello_world_eval_set_001.evalset.json
```

### Code Quality
```bash
# Auto-format code (uses isort + pyink following Google style)
./autoformat.sh

# Build wheel file
uv build

# Test locally built wheel
pip install dist/google_adk-<version>-py3-none-any.whl
```

### Development UI
```bash
# Start development web interface for testing agents
adk web

# Start API server backend
adk api_server

# Run agent from CLI (quick functional checks)
adk run <agent_path>
```

### Deployment
```bash
# Deploy to Google Cloud services
adk deploy
```

## Code Architecture

### Core Abstractions
- **Agent**: Blueprint defining agent identity, instructions, and tools (declarative config)
- **Tool**: Python function providing capabilities (search, API calls, etc.)
- **Runner**: Engine orchestrating the "Reason-Act" loop and LLM interactions
- **Session**: Conversation state for continuous dialogue
- **Memory**: Long-term recall across sessions
- **Artifact Service**: Manages non-textual data like files

### Package Structure
```
src/google/adk/
├── agents/          # Agent definitions and configuration schemas
├── tools/           # Built-in tools (google_search, BigQuery, Spanner, etc.)
├── flows/           # LLM interaction flows and processing
├── runners/         # Execution engines
├── sessions/        # Conversation state management
├── memory/          # Long-term storage
├── models/          # LLM connection and integration
├── evaluation/      # Testing and evaluation framework
├── cli/             # Command-line interface and web UI
├── auth/            # Authentication and credential management
├── artifacts/       # File and data artifact handling
└── utils/           # Shared utilities
```

### Multi-Agent Systems
ADK supports hierarchical multi-agent architectures through `sub_agents`. Agents can coordinate and delegate tasks to specialized sub-agents automatically.

### Canonical Project Structure
ADK projects should follow this structure:
```
my_adk_project/
└── src/
    └── my_app/
        ├── agents/
        │   ├── my_agent/
        │   │   ├── __init__.py   # Must contain: from . import agent
        │   │   └── agent.py      # Must contain: root_agent = Agent(...)
        │   └── another_agent/
        │       ├── __init__.py
        │       └── agent.py
```

## Development Patterns

### Agent Definition
```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="search_assistant",
    model="gemini-2.0-flash",
    instruction="You are a helpful assistant...",
    description="An assistant that can search the web.",
    tools=[google_search]
)
```

### Multi-Agent System
```python
from google.adk.agents import LlmAgent

# Create specialized agents
greeter = LlmAgent(name="greeter", model="gemini-2.0-flash", ...)
task_executor = LlmAgent(name="task_executor", model="gemini-2.0-flash", ...)

# Coordinator with sub-agents
coordinator = LlmAgent(
    name="Coordinator",
    model="gemini-2.0-flash",
    description="I coordinate greetings and tasks.",
    sub_agents=[greeter, task_executor]
)
```

### FastAPI Integration
```python
from google.adk.cli.fast_api import get_fast_api_app

app = get_fast_api_app(agent_dir="./agents")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

## Style Guidelines

### Python Code Style
- **Indentation**: 2 spaces
- **Line Length**: 80 characters max
- **Naming**: `snake_case` for functions/variables, `CamelCase` for classes, `UPPER_SNAKE_CASE` for constants
- **Imports**: Use relative imports in source (`from ..agents.llm_agent import LlmAgent`)
- **Future Annotations**: Always include `from __future__ import annotations` after license header
- **Docstrings**: Required for all public modules, functions, classes, and methods

### Testing Requirements
- **Unit Tests**: In `tests/unittests/`, using pytest framework
- **Integration Tests**: Test agent logic with mocked services
- **Evaluation Tests**: End-to-end quality assessment with live LLMs
- **Manual E2E**: Use `adk web` for UI verification, document with screenshots

## Key Features

### ADK Live (Bidi-streaming)
- Built on Gemini Live API via GenAI SDK
- Access via `runner.run_live(...)`
- Audio converted to text for multi-agent scenarios
- Main logic in `flows/llm_flows/base_llm_flow.py`

### Agent Config
- Build agents without code using configuration files
- Declarative agent definitions

### Rich Tool Ecosystem
- Pre-built tools for Google ecosystem (BigQuery, Spanner, GCS, etc.)
- OpenAPI spec integration
- Custom function support
- MCP (Model Context Protocol) toolset support

### Deployment Options
- Local development with `adk web`
- Cloud Run deployment
- Vertex AI Agent Engine integration
- GKE deployment

## Versioning & API Surface

ADK follows Semantic Versioning 2.0.0. The public API surface includes:
- All public classes, methods, functions in `google.adk` namespace
- Built-in tool names, parameters, and behavior
- Session, Memory, and Evaluation dataset schemas
- FastAPI server JSON request/response format
- CLI commands, arguments, and flags
- Agent file structure conventions

Breaking changes require MAJOR version bump.

## Context Files for AI Development

- `llms.txt`: Summarized context for LLMs with smaller context windows
- `llms-full.txt`: Complete information for LLMs with large context windows
- `AGENTS.md`: Detailed context for AI-assisted development
- `contributing/adk_project_overview_and_architecture.md`: Technical architecture overview