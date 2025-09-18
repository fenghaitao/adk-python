# Spec-Kit Integration with ADK

This is a streamlined integration of Spec-Kit with ADK that uses a single agent and leverages the existing spec-kit command structure.

## Overview

This integration provides a single `SpecKitAgent` that uses tools to execute the existing spec-kit commands:
- `/specify` - Create feature specifications
- `/plan` - Generate implementation plans  
- `/tasks` - Break down plans into actionable tasks

## Files

- `agent.py` - Single SpecKit agent that uses command tools
- `spec_kit_tools.py` - Tools that execute spec-kit commands
- `demo.py` - Simple demo script

## Usage

### Basic Usage

```python
from contributing.samples.spec_kit_integration.agent import root_agent
from google.adk.runners import InMemoryRunner

async def main():
    runner = InMemoryRunner(root_agent)
    
    # Create a specification
    response = await runner.run_async("/specify Create a user authentication system with email/password login")
    
    # Generate implementation plan
    response = await runner.run_async("/plan Use Python FastAPI backend with React frontend")
    
    # Create tasks
    response = await runner.run_async("/tasks Break down into TDD tasks")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Demo

```bash
python demo.py
```

## Environment Variables

- `SPEC_KIT_MODEL` - Model to use (default: "iflow/Qwen3-Coder")

## Commands

- `/specify <feature_description>` - Create a feature specification
- `/plan <implementation_details>` - Generate implementation plan
- `/tasks <context>` - Generate actionable tasks