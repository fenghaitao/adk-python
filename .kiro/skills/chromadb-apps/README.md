# ChromaDB Memory - Knowledge Retrieval Skill

This skill provides memory indexing and retrieval for OpenSpec workflows using ChromaDB vector storage.

## What This Skill Does

- **Indexes markdown documents** into ChromaDB vector database
- **Category-aware retrieval** (DML, Test, General)
- **Semantic search** using embeddings
- **Works with any markdown documentation**
- **Lightweight** - Only ChromaDB and YAML dependencies

## Quick Test

```bash
# Test the skill
cd /path/to/your/project
uv run skills/chromadb-apps/scripts/chromadb_memory.py test

# Index memories
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories

# Search memories
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "How to implement timer in DML?"
```

## Files

- `SKILL.md` - Complete documentation for the skill
- `scripts/chromadb_memory.py` - Main script with PEP 723 dependencies
- `references/chromadb.md` - ChromaDB configuration guide

## Key Features

✅ Self-contained script with PEP 723 dependencies
✅ ChromaDB vector storage with persistence
✅ Category-based filtering (DML/Test/General)
✅ Semantic search with configurable k results
✅ Self-contained with PEP 723 inline dependencies
✅ Complete CLI with index, search, and stats commands

## Usage Examples

### Index Memory Documents

```bash
# Index from directory
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories

# Force reindexing
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories --force

# Custom ChromaDB location
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories --persist-dir ./my_db
```

### Search Memories

```bash
# Basic search
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "timer implementation"

# Category-filtered search
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "test patterns" --category Test

# More results
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "DML registers" --k 5
```

### View Statistics

```bash
# Show index stats
uv run skills/chromadb-apps/scripts/chromadb_memory.py stats
```

## How It Works

1. **Index**: Parses markdown files, extracts metadata, chunks content
2. **Store**: ChromaDB creates embeddings and stores vectors
3. **Search**: Semantic search with optional category filtering
4. **Retrieve**: Returns most relevant passages

## Technical Stack

- ChromaDB for vector storage and semantic search
- PyYAML for frontmatter parsing
- Sentence transformers (via ChromaDB) for embeddings
- Only 2 direct dependencies (~50 total packages)

## Differences from lightrag-apps

This skill is simpler and more focused:

1. **Vector search only** (no knowledge graphs)
2. **ChromaDB** instead of NetworkX graphs
3. **Direct retrieval** instead of multi-mode queries
4. **Faster indexing** for smaller document sets
5. **Category-aware** for domain-specific retrieval

## See Also

See SKILL.md for complete documentation with all commands and options.
