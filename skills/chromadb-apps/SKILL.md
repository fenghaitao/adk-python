---
name: chromadb-memory
description: Index and retrieve knowledge from markdown documents using ChromaDB. Category-aware semantic search for DML patterns, test examples, and documentation with fast vector-based retrieval.
homepage: https://github.com/google/adk-python
metadata: {"clawdbot":{"emoji":"💾","requires":{"bins":["uv"]}}}
---

# ChromaDB Memory - Knowledge Indexing & Retrieval

Index and retrieve knowledge from markdown documents using ChromaDB vector storage.

## Quick Start

### Test Setup
```bash
uv run {baseDir}/scripts/chromadb_memory.py test
```

### Index and Search
```bash
# Index memories
uv run {baseDir}/scripts/chromadb_memory.py index openspec-memories

# Search with category filter
uv run {baseDir}/scripts/chromadb_memory.py search "timer implementation" --category DML

# View statistics
uv run {baseDir}/scripts/chromadb_memory.py stats
```

## Features

✅ **Fast semantic search** - Sub-200ms queries with ChromaDB vectors  
✅ **Category-aware retrieval** - Filter by DML, Test, or General  
✅ **Lightweight** - Only ChromaDB + YAML dependencies  
✅ **Self-contained** - PEP 723 inline dependencies  
✅ **Frontmatter parsing** - Automatic metadata extraction  
✅ **Configurable chunking** - Adjust chunk size and overlap

## Commands

### Test Setup
```bash
uv run {baseDir}/scripts/chromadb_memory.py test
```
Validates dependencies and verifies the skill is ready to use.

### Index Documents
```bash
# Index current directory's memories
uv run {baseDir}/scripts/chromadb_memory.py index openspec-memories

# Force reindex
uv run {baseDir}/scripts/chromadb_memory.py index openspec-memories --force

# Custom database location
uv run {baseDir}/scripts/chromadb_memory.py index docs/ --persist-dir ./my_db
```

### Search Memories
```bash
# Basic search
uv run {baseDir}/scripts/chromadb_memory.py search "How to implement timers?"

# Category filter
uv run {baseDir}/scripts/chromadb_memory.py search "register access" --category DML

# More results
uv run {baseDir}/scripts/chromadb_memory.py search "test patterns" --k 5
```

### View Statistics
```bash
uv run {baseDir}/scripts/chromadb_memory.py stats
```

## Configuration

### Default Settings

Uses ChromaDB with sensible defaults:

- **Persist Directory**: `.chromadb`
- **Collection Name**: `openspec_memories`
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters
- **Results (k)**: 3 passages

### Environment Variables (Optional)

```bash
export CHROMA_PERSIST_DIR=".chromadb"
export CHROMA_COLLECTION="openspec_memories"
export RETRIEVAL_K=3
```

## Document Format

Markdown files with optional frontmatter:

```markdown
---
title: DML Timer Implementation
category: DML
tags: [timer, event, scheduling]
---

# Content here
Your documentation...
```

**Category Auto-Detection:**
- Frontmatter `category` field (preferred)
- Filename patterns: `*DML*.md` → DML, `*Test*.md` → Test
- Default: General

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Indexing | ~8s | For 15 files (~50KB) |
| Search | ~200ms | Per query |
| Memory | ~100MB | With ChromaDB |
| Disk | ~50MB | Database size |

**Scalability:**
- 10-20 files: Excellent
- 50-100 files: Good
- 200+ files: Fair (consider LightRAG for large datasets)

## Examples

### Index OpenSpec Memories
```bash
cd /path/to/project
uv run {baseDir}/scripts/chromadb_memory.py index openspec-memories
```

### Search for DML Patterns
```bash
uv run {baseDir}/scripts/chromadb_memory.py search "timer implementation" --category DML
```

### Python API Usage
```python
from dspy_memory import MemoryRetriever

# Search
retriever = MemoryRetriever(k=3)
result = retriever(
    task_description="How to implement watchdog timer?",
    category="DML"
)

# Result is a dict with 'passages' key
for passage in result["passages"]:
    print(passage)
```

### Integration with DSPy
```python
import dspy
from dspy_memory import MemoryRetriever

# Wrap retriever for DSPy compatibility
class DSPyMemoryRetriever(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.retriever = MemoryRetriever(k=k)
    
    def forward(self, query):
        result = self.retriever(query)
        return dspy.Prediction(passages=result["passages"])

# Use in RAG pipeline
class RAGModule(dspy.Module):
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

### Check Setup
```bash
uv run {baseDir}/scripts/chromadb_memory.py test
```

### Common Issues

**Collection already exists**
```bash
# Force reindex
uv run {baseDir}/scripts/chromadb_memory.py index openspec-memories --force
```

**No results found**
```bash
# Check if indexed
uv run {baseDir}/scripts/chromadb_memory.py stats

# Try broader search
uv run {baseDir}/scripts/chromadb_memory.py search "timer" --k 10
```

**Import errors**
```bash
# Reinstall dependencies
uv pip install dspy-ai chromadb pyyaml
```

## File Support

Indexes markdown files (`.md`) with:
- YAML frontmatter (optional)
- Category auto-detection
- Chunking with overlap

## Technical Details

**Built with:**
- [ChromaDB](https://www.trychroma.com/) - Vector storage and semantic search
- [PyYAML](https://pyyaml.org/) - Frontmatter parsing
- Sentence Transformers (via ChromaDB) - Embeddings

**Architecture:**
1. **Indexer** - Parses markdown, extracts metadata, chunks text
2. **ChromaDB** - Stores vectors with metadata, handles embeddings
3. **Retriever** - Semantic search with category filtering

**Dependencies:**
- Only 2 direct dependencies: `chromadb` and `pyyaml`
- ~50 total packages (vs 1000+ with dspy-ai)
- Fast startup: ~16 seconds with `uv run`

## References

See `references/` directory for additional documentation:
- ChromaDB configuration and tuning
- DSPy retrieval patterns (RAG, ReAct, etc.)
- Performance optimization
- Advanced integration examples
