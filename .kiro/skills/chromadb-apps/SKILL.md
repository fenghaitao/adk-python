---
name: chromadb-memory
description: Index and retrieve knowledge from markdown documents using ChromaDB. Category-aware semantic search for DML patterns, test examples, and documentation with fast vector-based retrieval.
homepage: https://github.com/google/adk-python
metadata: {"clawdbot":{"emoji":"💾","requires":{"bins":["uv"]}}}
---

# ChromaDB Memory - Knowledge Indexing & Retrieval

Index and retrieve knowledge from markdown documents using ChromaDB vector storage.

## Quick Start

### Index and Search
```bash
# Index memories
uv run --directory {baseDir} chromadb-memory index openspec-memories

# Search with category filter
uv run --directory {baseDir} chromadb-memory search "timer implementation" --category DML

# View statistics
uv run --directory {baseDir} chromadb-memory stats
```

## Features

✅ **Fast semantic search** - Sub-200ms queries with ChromaDB vectors  
✅ **Category-aware retrieval** - Filter by DML, Test, or General  
✅ **Lightweight** - Only ChromaDB + YAML dependencies  
✅ **Persistent .venv** - 10x faster execution after one-time setup  
✅ **Frontmatter parsing** - Automatic metadata extraction  
✅ **Configurable chunking** - Adjust chunk size and overlap

## Commands

### Index Documents
```bash
# Index current directory's memories
uv run --directory {baseDir} chromadb-memory index openspec-memories

# Force reindex
uv run --directory {baseDir} chromadb-memory index openspec-memories --force

# Custom database location
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir ./my_db
```

### Search Memories
```bash
# Basic search
uv run --directory {baseDir} chromadb-memory search "How to implement timers?"

# Category filter
uv run --directory {baseDir} chromadb-memory search "register access" --category DML

# More results
uv run --directory {baseDir} chromadb-memory search "test patterns" --k 5
```

### View Statistics
```bash
uv run --directory {baseDir} chromadb-memory stats
```

## Configuration

### Default Settings

Uses ChromaDB with sensible defaults:

- **Persist Directory**: `.chromadb` (in current working directory)
- **Collection Name**: `openspec_memories`
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters
- **Results (k)**: 3 passages

### Storage Location Best Practices

The `.chromadb` folder contains your indexed data and should be stored in your **project directory**, not in the skill directory:

**✅ Recommended:**
```bash
# Index from your project directory
cd /path/to/your-project
uv run --directory /path/to/.kiro/skills/chromadb-apps chromadb-memory index docs/

# Creates: /path/to/your-project/.chromadb/
```

**❌ Not recommended:**
```bash
# Don't use --persist-dir to put it in the skill directory
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir {baseDir}/.chromadb
```

**Why?**
- Each project should have its own `.chromadb` folder
- Makes it easy to delete/recreate indexes per project
- Keeps skill directory clean and portable
- Allows multiple projects to have separate indexes

**Custom locations:**
```bash
# Use a shared location for multiple related projects
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir ~/shared-indexes/project-a

# Use project-specific subdirectory
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir ./.indexes/chromadb
```

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
uv run --directory {baseDir} chromadb-memory index openspec-memories
```

### Search for DML Patterns
```bash
uv run --directory {baseDir} chromadb-memory search "timer implementation" --category DML
```

### Multi-Category Search
```bash
# Search across all categories
uv run --directory {baseDir} chromadb-memory search "register patterns"

# Compare DML vs Test results
uv run --directory {baseDir} chromadb-memory search "register" --category DML --k 3
uv run --directory {baseDir} chromadb-memory search "register" --category Test --k 3
```

## Troubleshooting

### Setup Issues

**Problem:** Command not found or import errors

**Solution:**
```bash
uv run --directory {baseDir} chromadb-memory --help
```

### Check Setup
```bash
uv run --directory {baseDir} chromadb-memory stats
```

### Common Issues

**Collection already exists**
```bash
# Force reindex
uv run --directory {baseDir} chromadb-memory index openspec-memories --force
```

**No results found**
```bash
# Check if indexed
uv run --directory {baseDir} chromadb-memory stats

# Try broader search
uv run --directory {baseDir} chromadb-memory search "timer" --k 10
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
- Managed via `pyproject.toml`
- Only 2 direct dependencies: `chromadb` and `pyyaml`
- ~80 total packages (including transitive dependencies)
- Fast startup with persistent `.venv` (~2-3s vs ~15-20s with inline deps)

**Package Structure:**
```
chromadb-apps/
├── pyproject.toml           # Project configuration
├── chromadb_apps/           # Package directory
│   ├── __init__.py
│   └── chromadb_memory.py   # Main script
└── .venv/                   # Created automatically by uv run
```

## References

See `references/` directory for additional documentation:
- ChromaDB configuration and tuning
- Performance optimization tips
