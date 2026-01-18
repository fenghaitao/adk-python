# DSPy OpenSpec

DSPy-based implementation of the OpenSpec workflow for Simics device development.

## Overview

This package provides a DSPy port of the OpenSpec agent system, using instruction markdown files directly as DSPy signatures. This approach enables:

- **Automatic prompt optimization** via DSPy's teleprompt algorithms
- **Consistency** with the ADK-Python implementation (same instructions)
- **Composability** through DSPy's modular architecture
- **Few-shot learning** from successful implementation examples

## Architecture

### Instruction-as-Signature Pattern

The key innovation is using instruction markdown files directly as DSPy signature docstrings:

```python
class ProposalSignature(dspy.Signature):
    __doc__ = Path("proposal_initial_agent_instruction.md").read_text()
    
    task_description: str = dspy.InputField()
    device_hint: str = dspy.InputField(default="")
    
    change_id: str = dspy.OutputField()
    summary: str = dspy.OutputField()
```

This ensures:
- Zero translation loss from instructions to implementation
- Easy updates (edit `.md` file, changes automatically reflected)
- Compatibility with ADK-Python (same instruction source)

### Components

**Signatures** (`dspy-openspec/signatures/`)
- `ProposalSignature`: Loads `proposal_initial_agent_instruction.md`
- `ApplySignature`: Loads `apply_agent_instruction.md`
- `ArchiveSignature`: Loads `archive_agent_instruction.md`

**Modules** (`dspy-openspec/modules/`)
- `ProposalModule`: Generates OpenSpec proposals
- `ApplyModule`: Implements DML devices
- `ArchiveModule`: Archives completed changes

**Tools** (`dspy-openspec/tools/`)
- `OpenSpecTools`: File operations, validation, OpenSpec CLI integration

## Installation

```bash
# Install DSPy
cd dspy
pip install -e .

# Install dspy-openspec with memory support
cd ../dspy-openspec
pip install -e .
pip install chromadb  # For memory retrieval
```

## Memory Integration

DSPy OpenSpec includes a memory retrieval system that provides relevant knowledge from past implementations during the apply phase.

### Quick Start

```bash
# 1. Index memory documents
python -m dspy_openspec.memory.cli index openspec-memories

# 2. Test search
python -m dspy_openspec.memory.cli search "timer implementation" --category DML

# 3. Use with apply agent (memory enabled by default)
python examples/apply_with_memory.py --change-id 001-watchdog-timer
```

### How It Works

The memory system uses ChromaDB and semantic search to retrieve relevant implementation patterns, troubleshooting tips, and best practices:

```python
from dspy_openspec.modules.apply_module import ApplyModule

# Memory enabled by default
apply_module = ApplyModule(
    interactive=True,
    enable_memory=True,  # Default
    memory_k=3           # Retrieve top 3 chunks
)

# The agent can call retrieve_memory during execution:
# retrieve_memory("implement timer countdown logic", category="DML")
```

**Benefits:**
- Avoid repeated mistakes from past sessions
- Follow proven implementation patterns
- Quick access to troubleshooting guidance
- Category filtering (DML, Test, General)

**Documentation:**
- [Quick Start Guide](MEMORY_QUICKSTART.md)
- [Integration Guide](docs/memory_integration.md)
- [Summary](MEMORY_INTEGRATION_SUMMARY.md)

## Usage

### Basic Usage

```python
import dspy
from dspy_openspec import ProposalModule, ApplyModule, ArchiveModule

# Configure DSPy with your model
dspy.settings.configure(lm=dspy.LM("openai/gpt-4"))

# Generate proposal
proposal_agent = ProposalModule()
result = proposal_agent(
    task_description="Implement watchdog timer with interrupt support",
    device_hint="wdt"
)
print(f"Change ID: {result.change_id}")
print(f"Summary: {result.summary}")

# Apply change
apply_agent = ApplyModule()
result = apply_agent(change_id=result.change_id)
print(f"Status: {result.implementation_status}")

# Archive change
archive_agent = ArchiveModule()
result = archive_agent(change_id=result.change_id)
print(f"Archived to: {result.archive_path}")
```

### CLI Usage

```bash
# Generate proposal
python -m dspy_openspec.cli proposal "Implement WDT device" --device wdt --model openai/gpt-4

# Apply change
python -m dspy_openspec.cli apply --id implement-wdt-device --model openai/gpt-4

# Archive change
python -m dspy_openspec.cli archive --id implement-wdt-device --model openai/gpt-4
```

### With iflow Models

```bash
export IFLOW_API_KEY="your-api-key"

python -m dspy_openspec.cli proposal "Implement WDT" \
    --device wdt \
    --model iflow/qwen3-coder-plus
```

## Optimization

DSPy can automatically optimize the modules using training data:

```python
import dspy
from dspy.teleprompt import BootstrapFewShot
from dspy_openspec import ProposalModule

# Load training data (from successful sessions)
train_data = [
    dspy.Example(
        task_description="Implement WDT device",
        device_hint="wdt",
        change_id="implement-wdt-device",
        summary="Implement watchdog timer..."
    ).with_inputs("task_description", "device_hint"),
    # ... more examples
]

# Define quality metric
def proposal_quality(example, pred, trace=None):
    # Check if change_id follows conventions
    # Check if summary is concise
    # Check if validation passes
    return score

# Optimize
optimizer = BootstrapFewShot(metric=proposal_quality)
optimized_proposal = optimizer.compile(
    ProposalModule(),
    trainset=train_data
)

# Use optimized module
result = optimized_proposal(
    task_description="Implement UART device",
    device_hint="uart"
)
```

## Comparison with ADK-Python

| Aspect | ADK-Python | DSPy |
|--------|-----------|------|
| **Instructions** | Markdown templates | Same markdown as signatures |
| **Optimization** | Manual iteration | Automatic via teleprompt |
| **Examples** | Implicit in instructions | Explicit training data |
| **Modularity** | Agent classes | Composable DSPy modules |
| **Session Mgmt** | ADK sessions | DSPy predictions |
| **Tools** | ADK tools | DSPy tools + MCP |

## Benefits

1. **Automatic Optimization**: DSPy can improve prompts based on training data
2. **Composability**: Easier to mix and match modules
3. **Reproducibility**: Declarative signatures are more maintainable
4. **Few-Shot Learning**: Built-in support for learning from examples
5. **Research-Backed**: Uses proven optimization algorithms (MIPRO, BootstrapFewShot)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

Follow ADK style guidelines:
- 2-space indentation
- 80-character line length
- Proper copyright headers
- `from __future__ import annotations`

## License

Copyright 2025 Google LLC. Licensed under Apache 2.0.
