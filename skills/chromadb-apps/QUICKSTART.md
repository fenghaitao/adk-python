# ChromaDB Memory - Quick Start Guide

Get started with ChromaDB Memory in 5 minutes!

## Prerequisites

- Python 3.10+
- `uv` package manager (or `pip`)

## Installation

No installation needed! The script uses PEP 723 inline dependencies.

```bash
# Just run with uv
uv run skills/chromadb-apps/scripts/chromadb_memory.py --help
```

## Quick Start (3 Steps)

### Step 1: Verify Installation

```bash
cd /path/to/your/project
uv run skills/chromadb-apps/scripts/chromadb_memory.py test
```

**Expected output:**
```
🧪 Testing ChromaDB Memory Skill...
✅ DSPy import: OK
✅ ChromaDB import: OK
✅ YAML import: OK
✅ All dependencies available!
```

### Step 2: Index Your Memories

```bash
# Index OpenSpec memories (example)
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories
```

**Expected output:**
```
📚 Indexing memories from: openspec-memories
✅ Successfully indexed memories:
   Files: 15
   Chunks: 142
   Collection: openspec_memories
```

**Note:** First run will download dependencies (~30 seconds)

### Step 3: Search

```bash
# Search for relevant information
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "How to implement timer?"
```

**Expected output:**
```
🔍 Searching for: How to implement timer?

✅ Found 3 relevant passages:

--- Passage 1 ---
# DML Timer Implementation
Timers in DML use the `after` keyword...
```

## Common Commands

### Index with Options

```bash
# Force reindex
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories --force

# Custom database location
uv run skills/chromadb-apps/scripts/chromadb_memory.py index docs/ --persist-dir ./my_db
```

### Search with Filters

```bash
# Category filter
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "register access" --category DML

# More results
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "test patterns" --k 5

# Combine filters
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "timer" --category DML --k 10
```

### View Statistics

```bash
# Show what's indexed
uv run skills/chromadb-apps/scripts/chromadb_memory.py stats
```

**Output:**
```
📊 Memory Index Statistics:
   Total chunks: 142
   Unique files: 15
   Categories:
     - DML: 78 chunks
     - Test: 45 chunks
     - General: 19 chunks
```

## Python API Usage

### Basic Retrieval

```python
from chromadb_memory import MemoryRetriever

# Search
retriever = MemoryRetriever(k=3)
result = retriever(
    task_description="How to implement watchdog timer?",
    category="DML"
)

# Print results
for passage in result["passages"]:
    print(passage)
```

### DSPy Integration

If you want to use this with DSPy pipelines, wrap it in a DSPy module:

```python
import dspy
from chromadb_memory import MemoryRetriever

class DSPyMemoryRetriever(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.retriever = MemoryRetriever(k=k)
    
    def forward(self, query):
        result = self.retriever(query)
        return dspy.Prediction(passages=result["passages"])

# Use in RAG
class RAGAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retriever = DSPyMemoryRetriever(k=3)
        self.generate = dspy.ChainOfThought("context, query -> answer")
    
    def forward(self, query):
        retrieval = self.retriever(query)
        context = "\n\n".join(retrieval.passages)
        return self.generate(context=context, query=query)
```

## Troubleshooting

### Dependencies downloading slowly?

First run downloads DSPy, ChromaDB, and dependencies (~100MB). Subsequent runs are instant.

```bash
# Pre-install if needed
pip install dspy-ai chromadb pyyaml
```

### "Collection already exists" error?

Use `--force` to reindex:

```bash
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories --force
```

### No results found?

1. Check if indexed: `uv run skills/chromadb-apps/scripts/chromadb_memory.py stats`
2. Try different search terms
3. Remove category filter: don't use `--category`

### Database location?

Default: `.chromadb/` in current directory

Custom location:
```bash
uv run skills/chromadb-apps/scripts/chromadb_memory.py index docs/ --persist-dir ~/my_db
```

## Document Format

Your markdown files can have optional frontmatter:

```markdown
---
title: DML Timer Implementation
category: DML
tags: [timer, event, scheduling]
---

# Content here

Your documentation...
```

**Auto-detection:**
- Filenames with "DML" → DML category
- Filenames with "Test" → Test category
- Others → General category

## Next Steps

1. **Read full docs**: `skills/chromadb-apps/SKILL.md`
2. **See examples**: `skills/chromadb-apps/examples/basic_usage.py`
3. **ChromaDB config**: `skills/chromadb-apps/references/chromadb.md`
4. **DSPy patterns**: `skills/chromadb-apps/references/dspy-retrieval.md`

## Use Cases

### OpenSpec Workflow
```bash
# Index DML/Test best practices
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories

# Query during development
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "DML register implementation" --category DML
```

### Documentation Search
```bash
# Index your docs
uv run skills/chromadb-apps/scripts/chromadb_memory.py index docs/

# Search
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "API authentication"
```

### AI Agent Context
```python
# Use in your agent for RAG
retriever = MemoryRetriever(k=5)
context = retriever("user query").passages
# Feed to LLM...
```

## Performance

- **Indexing**: ~8 seconds for 15 files (50KB)
- **Search**: ~200ms per query
- **Memory**: ~100MB with ChromaDB
- **Disk**: ~50MB database

## Getting Help

- Full documentation: `SKILL.md`
- Examples: `examples/basic_usage.py`
- Configuration: `references/chromadb.md`
- Patterns: `references/dspy-retrieval.md`

## Summary

```bash
# 1. Test
uv run skills/chromadb-apps/scripts/chromadb_memory.py test

# 2. Index
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories

# 3. Search
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "your query"

# 4. View stats
uv run skills/chromadb-apps/scripts/chromadb_memory.py stats
```

That's it! You're ready to use ChromaDB Memory. 🚀
