# Memory Integration Guide

This guide explains how the memory retrieval system integrates with the OpenSpec apply agent to provide relevant knowledge from past implementations.

## Overview

The memory system uses ChromaDB and semantic search to retrieve relevant implementation patterns, troubleshooting tips, and best practices during the apply phase. This helps the agent:

- Avoid common mistakes from past sessions
- Follow proven implementation patterns
- Quickly resolve compilation and test errors
- Learn from successful device implementations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ApplyModule                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ReAct Agent (VerboseReAct)                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ File Tools   │  │ Simics Tools │  │ Memory Tool  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ MemoryRetriever  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   ChromaDBRM     │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │    ChromaDB      │
                    │  (Vector Store)  │
                    └──────────────────┘
```

## Setup

### 1. Index Memory Documents

First, index your memory documents into ChromaDB:

```bash
cd adk-python

# Index memories from openspec-memories directory
python -m dspy_openspec.memory.cli index openspec-memories

# Check indexing statistics
python -m dspy_openspec.memory.cli stats
```

### 2. Test Memory Search

Verify the memory system works:

```bash
# Search for DML implementation patterns
python -m dspy_openspec.memory.cli search "timer implementation" --category DML

# Search for test patterns
python -m dspy_openspec.memory.cli search "interrupt signal testing" --category Test

# General search
python -m dspy_openspec.memory.cli search "register side-effects"
```

### 3. Configure Apply Module

The apply module automatically enables memory retrieval by default. Configuration options:

```python
from dspy_openspec.modules.apply_module import ApplyModule

# Enable memory with defaults
apply_module = ApplyModule(
    interactive=True,
    enable_memory=True,        # Enable memory retrieval
    memory_persist_dir=".chromadb",  # ChromaDB location
    memory_k=3                 # Number of chunks to retrieve
)

# Disable memory
apply_module = ApplyModule(
    interactive=True,
    enable_memory=False
)
```

## Usage

### Memory Tool in ReAct Agent

When memory is enabled, the agent has access to a `retrieve_memory` tool:

```python
def retrieve_memory(
    task_description: str,
    error_context: str = "",
    category: Optional[str] = None
) -> str:
    """Retrieve relevant knowledge from past implementations.
    
    Args:
        task_description: What you're trying to implement or solve
        error_context: Any error messages or failures (optional)
        category: Filter by DML, Test, or General (optional)
    
    Returns:
        Relevant knowledge chunks from memory
    """
```

### Example Agent Usage

The agent can call this tool during execution:

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
Use `after` callback for countdown logic:
```dml
method start_countdown() {
    after(delay_cycles) call timeout_handler;
}
```
...
```

### Automatic Retrieval on Errors

The apply agent instruction includes guidance to automatically retrieve memories when encountering errors:

**DML Compilation Errors:**
```
retrieve_memory("DML compilation error: undefined identifier 'wdogint'", category="DML")
```

**Test Failures:**
```
retrieve_memory("test failure: signal not asserted", category="Test")
```

## Memory Categories

The system organizes memories into three categories:

| Category | Description | Example Queries |
|----------|-------------|-----------------|
| **DML** | Device implementation patterns, DML syntax, register side-effects | "timer countdown logic", "register write side-effect", "signal assertion" |
| **Test** | Python test patterns, Simics test API, validation approaches | "test interrupt signal", "register read verification", "test setup patterns" |
| **General** | Workflow guidance, troubleshooting, best practices | "apply workflow", "debugging approach", "quality checks" |

## Configuration

### YAML Configuration

Edit `dspy_openspec/config/default.yaml`:

```yaml
openspec:
  memory:
    enabled: true                    # Enable/disable memory
    persist_dir: ".chromadb"         # ChromaDB location
    collection_name: "openspec_memories"
    k: 3                             # Default retrieval count
    auto_retrieve: true              # Auto-retrieve on errors
```

### Environment Variables

```bash
# Override ChromaDB location
export CHROMADB_PERSIST_DIR="/path/to/.chromadb"

# Override retrieval count
export MEMORY_K=5
```

## Example: Apply with Memory

```python
#!/usr/bin/env python3
import dspy
from dspy_openspec.modules.apply_module import ApplyModule
from dspy_openspec.config.lm_config import configure_lm

# Configure language model
configure_lm("openai/gpt-4")

# Initialize apply module with memory
apply_module = ApplyModule(
    interactive=True,
    enable_memory=True,
    memory_k=3
)

# Execute apply
result = apply_module(change_id="001-watchdog-timer")

print(f"Status: {result.implementation_status}")
print(f"Files: {result.files_modified}")
print(f"Completed: {result.completed}")
```

See `examples/apply_with_memory.py` for a complete example.

## Troubleshooting

### Memory Not Available

If you see: `⚠️ Memory retrieval disabled: chromadb not installed`

Install ChromaDB:
```bash
pip install chromadb
```

### Collection Not Found

If you see: `Collection 'openspec_memories' not found`

Index your memories first:
```bash
python -m dspy_openspec.memory.cli index openspec-memories
```

### Poor Retrieval Quality

If retrieved memories aren't relevant:

1. **Increase k value**: Retrieve more chunks
   ```python
   ApplyModule(memory_k=5)
   ```

2. **Use specific categories**: Filter by DML or Test
   ```python
   retrieve_memory("timer logic", category="DML")
   ```

3. **Improve query**: Be more specific in task_description
   ```python
   # Bad: "timer"
   # Good: "implement timer countdown with interrupt on timeout"
   ```

4. **Re-index with better chunking**: Edit `indexer.py` chunk_size

## Best Practices

### When to Use Memory Retrieval

✅ **DO use memory retrieval for:**
- Implementing new device features
- Resolving compilation errors
- Fixing test failures
- Learning DML patterns
- Understanding register side-effects

❌ **DON'T use memory retrieval for:**
- Reading spec files (use file tools)
- Checking change status (use OpenSpec tools)
- Building projects (use Simics tools)

### Query Writing Tips

**Good queries:**
- "implement watchdog timer countdown with lazy evaluation"
- "DML compilation error: register scope violation"
- "test interrupt signal assertion after register write"

**Poor queries:**
- "timer" (too vague)
- "error" (no context)
- "help" (not specific)

### Memory Document Organization

Structure your memory documents for optimal retrieval:

```markdown
# 01_DML_Timer_Patterns.md

## Timer Countdown Implementation

**Pattern:** Use `after` callback for countdown logic

**Example:**
```dml
method start_countdown() {
    local uint64 delay = this.load_value;
    after(delay) call timeout_handler;
}
```

**Common Mistakes:**
- Don't use Python-style loops in DML
- Remember to cancel pending events on reset
```

## Performance

- **Indexing**: ~1-2 seconds for 10 memory documents
- **Search**: ~50-100ms per query
- **Memory overhead**: ~10-50MB for ChromaDB
- **Disk usage**: ~1-5MB per 100 memory chunks

## Future Enhancements

Planned improvements:

1. **Automatic memory creation**: Extract patterns from successful sessions
2. **Relevance feedback**: Learn from which memories were helpful
3. **Multi-modal retrieval**: Include code snippets, diagrams
4. **Hierarchical memory**: Organize by device type, complexity
5. **Memory versioning**: Track memory document changes over time
