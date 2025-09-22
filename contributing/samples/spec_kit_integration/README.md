# Spec-Kit Integration with ADK

This is a streamlined integration of Spec-Kit with ADK that uses a single agent and leverages the existing spec-kit command structure with automatic Simics hardware simulation integration.

## Overview

This integration provides a single `SpecKitAgent` that uses tools to execute the existing spec-kit commands with automatic hardware simulation detection and Simics integration:
- `/specify` - Create feature specifications (auto-detects hardware simulation needs)
- `/plan` - Generate implementation plans (includes Simics setup for hardware simulation)
- `/tasks` - Break down plans into actionable tasks (includes Simics MCP tool usage)

## Simics Hardware Simulation

The agent automatically detects projects requiring hardware simulation and integrates Simics simulation environment:
- **Automatic Detection**: Recognizes hardware-related keywords and requirements
- **Real Simics Projects**: Uses create_simics_project MCP tool to create actual Simics projects via ispm
- **Package Management**: Uses install_simics_package MCP tool to install real Simics packages
- **No Manual Setup**: Hardware simulation setup uses proper Simics tooling automatically

## Files

- `agent.py` - SpecKit agent with integrated Simics hardware simulation support
- `spec_kit_tools.py` - Basic tools for file operations and bash commands, plus MCP integration
- `test_integrated_workflow.py` - Test script for the integrated workflow
- `simics-mcp-server/` - Simics MCP server for hardware simulation tools

## Usage

### Basic Usage

```python
from contributing.samples.spec_kit_integration.agent import root_agent
from google.adk.runners import InMemoryRunner

async def main():
    runner = InMemoryRunner(root_agent)
    
    # Software project (normal workflow)
    response = await runner.run_async("/specify Create a user authentication system with email/password login")
    response = await runner.run_async("/plan Use Python FastAPI backend with React frontend")
    response = await runner.run_async("/tasks Break down into TDD tasks")
    
    # Hardware simulation project (automatic Simics integration)
    response = await runner.run_async("/specify Create an ARM processor simulator with memory management")
    response = await runner.run_async("/plan Use Simics for hardware simulation with ARM architecture")
    response = await runner.run_async("/tasks Include Simics environment setup and hardware simulation validation")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Testing

```bash
# Run the integrated workflow test
python test_integrated_workflow.py

# Test individual components
python -c "
import asyncio
from agent import root_agent
from google.adk.runners import InMemoryRunner

async def test():
    runner = InMemoryRunner(root_agent)
    response = await runner.run_async('/specify Create an x86 hardware simulator')
    print(response.model_response.text)

asyncio.run(test())
"
```

## Environment Variables

- `SPEC_KIT_MODEL` - Model to use (default: "iflow/Qwen3-Coder")

## Commands

- `/specify <feature_description>` - Create a feature specification (LLM detects hardware simulation needs)
- `/plan <implementation_details>` - Generate implementation plan (LLM uses Simics MCP tools for hardware simulation)
- `/tasks <context>` - Generate actionable tasks (LLM includes Simics MCP tool calls for hardware simulation)

## Directory Structure

The integration uses the following directory structure:

```
~/.adk/                     # Configuration (read-only)
├── commands/
│   ├── specify.md
│   ├── plan.md
│   └── tasks.md

~/.specify/                 # Templates (used by agent)
├── templates/
│   ├── spec_template.md
│   ├── plan_template.md
│   └── tasks_template.md

project_directory/          # Generated project structure
├── src/
├── tests/
├── docs/
└── simics/                 # For hardware simulation projects
    ├── configs/
    └── scripts/
```

## Automatic Hardware Simulation Detection

The agent automatically detects hardware simulation projects based on keywords:
- **Hardware terms**: processor, CPU, GPU, FPGA, microcontroller, embedded
- **Simulation terms**: simulation, modeling, hardware validation
- **Architecture terms**: x86, ARM, RISC-V, MIPS, SPARC
- **Hardware components**: PCI, USB, memory controller, peripheral
- **Development terms**: firmware, BIOS, bootloader, RTL

When detected, the agent:
1. Suggests appropriate Simics packages based on hardware requirements
2. Uses create_simics_project MCP tool to create real Simics projects with ispm
3. Uses install_simics_package MCP tool to install suggested packages
4. Includes hardware simulation validation tasks in workflow
