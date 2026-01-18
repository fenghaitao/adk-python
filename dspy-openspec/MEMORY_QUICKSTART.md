# Memory System Quick Start

Get started with the OpenSpec memory retrieval system in 3 steps.

## Prerequisites

```bash
# Install ChromaDB
pip install chromadb

# Or install all dspy-openspec dependencies
cd dspy-openspec
pip install -e .
```

## Step 1: Index Your Memories

Index memory documents from the `openspec-memories` directory:

```bash
cd adk-python

# Index memories
python -m dspy_openspec.memory.cli index openspec-memories

# Expected output:
# 📚 Indexing memories from: openspec-memories
# ✅ Successfully indexed memories:
#    Files: 8
#    Chunks: 45
#    Collection: openspec_memories
```

## Step 2: Test Memory Search

Verify the system works by searching for relevant knowledge:

```bash
# Search for DML patterns
python -m dspy_openspec.memory.cli search "timer implementation" --category DML

# Search for test patterns
python -m dspy_openspec.memory.cli search "interrupt signal testing" --category Test

# General search (no category filter)
python -m dspy_openspec.memory.cli search "register side-effects"
```

Example output:
```
🔍 Searching for: timer implementation

✅ Found 3 relevant passages:

--- Passage 1 ---
Timer Implementation Pattern:
Use `after` callback for countdown logic:
```dml
method start_countdown() {
    after(delay_cycles) call timeout_handler;
}
```
...
```

## Step 3: Use with Apply Agent

The apply agent automatically uses memory retrieval when enabled:

```python
#!/usr/bin/env python3
import dspy
from dspy_openspec.modules.apply_module import ApplyModule
from dspy_openspec.config.lm_config import configure_lm

# Configure your language model
configure_lm("openai/gpt-4")

# Initialize apply module (memory enabled by default)
apply_module = ApplyModule(
    interactive=True,
    enable_memory=True,  # This is the default
    memory_k=3           # Retrieve top 3 chunks
)

# Execute apply
result = apply_module(change_id="001-watchdog-timer")

print(f"Status: {result.implementation_status}")
print(f"Completed: {result.completed}")
```

Or use the example script:

```bash
cd adk-python/dspy-openspec

# Run apply with memory
python examples/apply_with_memory.py --change-id 001-watchdog-timer

# Run apply without memory
python examples/apply_with_memory.py --change-id 001-watchdog-timer --no-memory
```

## How It Works

During execution, the agent can call the `retrieve_memory` tool:

```
Thought: I need to implement timer countdown logic. Let me check past implementations.

Action: retrieve_memory
Action Input: {
  "task_description": "implement timer countdown with after callback",
  "category": "DML"
}

Observation: Found 3 relevant memories:
--- Memory 1 ---
Timer Implementation Pattern:
Use `after` callback for countdown logic...
```

The agent automatically retrieves memories when:
- Implementing new features
- Encountering compilation errors
- Fixing test failures
- Following the apply agent instruction guidance

## Memory Categories

| Category | Use For | Example Query |
|----------|---------|---------------|
| **DML** | Device implementation, DML syntax, register patterns | "timer countdown logic", "register write side-effect" |
| **Test** | Python test patterns, Simics test API | "test interrupt signal", "register verification" |
| **General** | Workflow, troubleshooting, best practices | "apply workflow", "debugging approach" |

## Configuration

### Default Configuration

Memory is enabled by default with these settings:

```yaml
# dspy_openspec/config/default.yaml
openspec:
  memory:
    enabled: true
    persist_dir: ".chromadb"
    collection_name: "openspec_memories"
    k: 3
    auto_retrieve: true
```

### Disable Memory

To disable memory retrieval:

```python
apply_module = ApplyModule(
    interactive=True,
    enable_memory=False  # Disable memory
)
```

### Custom Configuration

```python
apply_module = ApplyModule(
    interactive=True,
    enable_memory=True,
    memory_persist_dir="/custom/path/.chromadb",  # Custom ChromaDB location
    memory_k=5  # Retrieve top 5 chunks instead of 3
)
```

## Troubleshooting

### "chromadb not installed"

```bash
pip install chromadb
```

### "Collection not found"

Index your memories first:
```bash
python -m dspy_openspec.memory.cli index openspec-memories
```

### "No relevant passages found"

1. Check if memories are indexed:
   ```bash
   python -m dspy_openspec.memory.cli stats
   ```

2. Try a more specific query:
   ```bash
   # Bad: "timer"
   # Good: "implement timer countdown with interrupt"
   python -m dspy_openspec.memory.cli search "implement timer countdown with interrupt" --category DML
   ```

3. Increase retrieval count:
   ```python
   apply_module = ApplyModule(memory_k=5)
   ```

## Next Steps

- Read the [Memory Integration Guide](docs/memory_integration.md) for detailed documentation
- Add your own memory documents to `openspec-memories/`
- Customize chunking and retrieval in `dspy_openspec/memory/indexer.py`
- Integrate with proposal module (coming soon)

## CLI Reference

```bash
# Index memories
python -m dspy_openspec.memory.cli index <memory_dir> [--persist-dir DIR] [--force]

# Show statistics
python -m dspy_openspec.memory.cli stats [--memory-dir DIR] [--persist-dir DIR]

# Search memories
python -m dspy_openspec.memory.cli search <query> [--category CATEGORY] [--k N] [--persist-dir DIR]
```

## Examples

See `examples/apply_with_memory.py` for a complete working example.
