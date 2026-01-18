# OpenSpec Memory Retrieval System

Semantic search over OpenSpec knowledge base using DSPy and ChromaDB.

## Overview

The memory retrieval system indexes OpenSpec memory documents (from `openspec-memories/`) and enables semantic search to find relevant knowledge for implementation tasks.

## Features

- **Automatic Indexing**: Chunks and indexes all markdown files in the memory directory
- **Semantic Search**: Uses vector embeddings for intelligent retrieval
- **Category Filtering**: Filter by DML, Test, or General categories
- **DSPy Integration**: Works seamlessly with DSPy's Retrieve interface

## Installation

```bash
# Install with chromadb support
pip install chromadb

# Or install the package with optional dependencies
pip install -e ".[dev]"
```

## Usage

### CLI Commands

**Index memories:**
```bash
# Index memories from a directory
dspy-memory index openspec-memories/

# Force reindexing
dspy-memory index openspec-memories/ --force

# Use custom persist directory
dspy-memory index openspec-memories/ --persist-dir .my-chromadb
```

**View statistics:**
```bash
dspy-memory stats
```

**Search memories:**
```bash
# Basic search
dspy-memory search "how to implement timer device"

# Filter by category
dspy-memory search "register scope error" --category DML

# Get more results
dspy-memory search "test configuration" --k 5
```

### Python API

**Indexing:**
```python
from dspy_openspec.memory import MemoryIndexer

# Create indexer
indexer = MemoryIndexer(
    memory_dir="openspec-memories",
    persist_directory=".chromadb"
)

# Index all documents
result = indexer.index_memories()
print(f"Indexed {result['files_indexed']} files")

# Get statistics
stats = indexer.get_stats()
print(f"Total chunks: {stats['total_chunks']}")
```

**Retrieval:**
```python
from dspy_openspec.memory import MemoryRetriever

# Create retriever
retriever = MemoryRetriever(
    persist_directory=".chromadb",
    k=3  # Return top 3 results
)

# Retrieve relevant memories
result = retriever.forward(
    task_description="implement watchdog timer",
    error_context="",
    category="DML"  # Optional: filter by category
)

# Access retrieved passages
for passage in result.passages:
    print(passage)
```

**Category-specific retrieval:**
```python
# Retrieve DML-specific memories
dml_memories = retriever.retrieve_for_dml(
    task_description="implement timer countdown",
    error_context="unknown identifier 'this.val'"
)

# Retrieve Test-specific memories
test_memories = retriever.retrieve_for_test(
    task_description="create register access tests",
    error_context="AttributeError: 'NoneType' object has no attribute 'read'"
)
```

## Integration with Apply Module

The memory retriever can be integrated with the apply module to automatically load relevant knowledge:

```python
from dspy_openspec.modules.apply_module import ApplyModule
from dspy_openspec.memory import MemoryRetriever

# Create retriever
retriever = MemoryRetriever()

# Create apply module with memory support
apply_module = ApplyModule(interactive=True)

# In the workflow, retrieve relevant memories
memories = retriever.retrieve_for_dml(
    task_description="implement WDT device with countdown timer",
    error_context=""
)

# Use memories as context for implementation
# (memories are automatically included in the agent's context)
```

## How It Works

1. **Chunking**: Documents are split into overlapping chunks (~1000 chars each)
2. **Embedding**: ChromaDB creates vector embeddings using a default embedding model
3. **Indexing**: Chunks are stored with metadata (filename, category, chunk index)
4. **Retrieval**: Queries are embedded and matched against indexed chunks using cosine similarity
5. **Ranking**: Most relevant chunks are returned based on semantic similarity

## Directory Structure

```
dspy_openspec/memory/
├── __init__.py          # Package exports
├── indexer.py           # MemoryIndexer class
├── retriever.py         # MemoryRetriever and ChromaDBRM classes
├── cli.py               # Command-line interface
└── README.md            # This file
```

## Configuration

### Chunk Size

Default chunk size is 1000 characters with 200 character overlap. Adjust in `indexer.py`:

```python
chunks = self._chunk_document(
    content,
    filename,
    chunk_size=1000,  # Adjust this
    overlap=200       # And this
)
```

### Number of Results

Default is 3 results. Override when retrieving:

```python
retriever = MemoryRetriever(k=5)  # Return top 5 results
```

## Troubleshooting

**ChromaDB not installed:**
```
ImportError: chromadb is required for memory indexing
```
Solution: `pip install chromadb`

**Collection not found:**
```
ValueError: Collection 'openspec_memories' not found
```
Solution: Index memories first with `dspy-memory index openspec-memories/`

**No results returned:**
- Check if memories are indexed: `dspy-memory stats`
- Try broader search queries
- Increase k value: `--k 10`

## Performance

- **Indexing**: ~1-2 seconds for 15 markdown files
- **Retrieval**: ~50-100ms per query
- **Storage**: ~1-5MB for typical memory collection

## Future Enhancements

- [ ] Support for custom embedding models
- [ ] Hybrid search (semantic + keyword)
- [ ] Relevance feedback and learning
- [ ] Integration with DSPy optimization (BootstrapFewShot)
- [ ] Memory usage analytics and recommendations
