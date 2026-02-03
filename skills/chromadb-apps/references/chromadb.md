# ChromaDB Configuration Guide

ChromaDB is an open-source embedding database designed for AI applications. This guide covers configuration options for the DSPy Memory skill.

## Basic Configuration

### Default Settings

The skill uses these defaults:

```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    persist_directory=".chromadb",
    anonymized_telemetry=False,
))
```

### Custom Persistence Directory

```bash
# Via CLI
uv run dspy_memory.py index openspec-memories --persist-dir ./my_db

# Via Python
from dspy_memory import MemoryIndexer

indexer = MemoryIndexer(
    memory_dir="docs",
    persist_directory="./custom_db"
)
```

## Collection Settings

### Distance Metrics

ChromaDB supports multiple distance metrics for similarity search:

- **cosine** (default): Cosine similarity (range: -1 to 1)
- **l2**: Euclidean distance
- **ip**: Inner product

```python
collection = client.create_collection(
    name="openspec_memories",
    metadata={"hnsw:space": "cosine"}  # or "l2" or "ip"
)
```

### HNSW Index Parameters

HNSW (Hierarchical Navigable Small World) is the index algorithm used by ChromaDB:

```python
collection = client.create_collection(
    name="openspec_memories",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:construction_ef": 200,  # Higher = better quality, slower
        "hnsw:M": 16,                  # Higher = more connections
    }
)
```

**Parameters:**
- `hnsw:construction_ef`: Controls build quality (default: 100)
- `hnsw:M`: Max connections per node (default: 16)
- `hnsw:search_ef`: Query time quality (default: 10)

## Embedding Models

### Default Model

ChromaDB uses `all-MiniLM-L6-v2` by default:
- Size: 22M parameters
- Speed: ~3000 docs/sec
- Dimension: 384

### Custom Embedding Function

```python
from chromadb.utils import embedding_functions

# OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-ada-002"
)

# Sentence transformers
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-mpnet-base-v2"
)

# Use with collection
collection = client.create_collection(
    name="openspec_memories",
    embedding_function=openai_ef
)
```

### Popular Models

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|---------|
| all-MiniLM-L6-v2 | 384 | Fast | Good |
| all-mpnet-base-v2 | 768 | Medium | Better |
| text-embedding-ada-002 | 1536 | Medium | Best |

## Performance Tuning

### Batch Size

```python
# Index in batches for large datasets
batch_size = 100
for i in range(0, len(documents), batch_size):
    batch = documents[i:i+batch_size]
    collection.add(
        documents=batch,
        ids=[f"doc_{j}" for j in range(i, i+len(batch))]
    )
```

### Query Performance

```python
# Adjust search_ef for speed vs quality tradeoff
results = collection.query(
    query_texts=["your query"],
    n_results=10,
    # Lower = faster, higher = more accurate
)
```

### Memory Usage

ChromaDB loads the index into memory. For large datasets:

```bash
# Monitor memory usage
docker stats  # if using Docker

# Optimize by reducing batch size
# or using a smaller embedding model
```

## Storage Structure

### Directory Layout

```
.chromadb/
├── chroma.sqlite3          # Metadata database
└── [collection_id]/
    ├── index/              # HNSW index files
    ├── data_level0.bin    # Vector data
    └── length.bin         # Document lengths
```

### Backup and Restore

```bash
# Backup
tar -czf chromadb-backup.tar.gz .chromadb/

# Restore
tar -xzf chromadb-backup.tar.gz

# Or copy directory
cp -r .chromadb .chromadb.backup
```

## Advanced Features

### Filtering with Where Clause

```python
# Filter by metadata
results = collection.query(
    query_texts=["timer implementation"],
    n_results=5,
    where={"category": "DML"}
)

# Multiple conditions
results = collection.query(
    query_texts=["test patterns"],
    where={
        "$and": [
            {"category": "Test"},
            {"difficulty": "beginner"}
        ]
    }
)
```

### Available Operators

- `$eq`: Equal to
- `$ne`: Not equal to
- `$gt`: Greater than
- `$gte`: Greater than or equal
- `$lt`: Less than
- `$lte`: Less than or equal
- `$in`: In array
- `$nin`: Not in array
- `$and`: Logical AND
- `$or`: Logical OR

### Metadata Filtering Examples

```python
# Category filter
where={"category": "DML"}

# Multiple categories
where={"category": {"$in": ["DML", "Test"]}}

# Difficulty range
where={"difficulty": {"$in": ["beginner", "intermediate"]}}

# Complex query
where={
    "$and": [
        {"category": "DML"},
        {"difficulty": {"$ne": "advanced"}}
    ]
}
```

## Client Modes

### Persistent Client (Default)

```python
# Data persists to disk
client = chromadb.Client(Settings(
    persist_directory=".chromadb"
))
```

### In-Memory Client

```python
# Data only in RAM (faster, no persistence)
client = chromadb.Client()
```

### HTTP Client

```python
# Connect to remote ChromaDB server
client = chromadb.HttpClient(
    host="localhost",
    port=8000
)
```

## Production Deployment

### Docker Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - ./chromadb_data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=False
```

```bash
# Start server
docker-compose up -d

# Connect from Python
client = chromadb.HttpClient(host="localhost", port=8000)
```

### Environment Variables

```bash
# ChromaDB settings
export CHROMA_HOST="localhost"
export CHROMA_PORT="8000"
export CHROMA_PERSIST_DIR=".chromadb"

# Embedding settings
export EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Performance
export CHROMA_BATCH_SIZE=100
export CHROMA_MAX_WORKERS=4
```

## Troubleshooting

### Issue: "Collection already exists"

```python
# Delete and recreate
client.delete_collection("openspec_memories")
collection = client.create_collection("openspec_memories")

# Or use force reindex
indexer.index_memories(force_reindex=True)
```

### Issue: Slow queries

```python
# Reduce search space with filters
results = collection.query(
    query_texts=["query"],
    n_results=3,  # Request fewer results
    where={"category": "DML"}  # Use filters
)

# Adjust HNSW parameters
collection = client.create_collection(
    name="openspec_memories",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:search_ef": 10  # Lower = faster
    }
)
```

### Issue: High memory usage

```bash
# Use smaller embedding model
# all-MiniLM-L6-v2 (384 dims) vs all-mpnet-base-v2 (768 dims)

# Or reduce document count
# Index only necessary documents

# Monitor usage
import psutil
print(f"Memory: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
```

### Issue: Database corruption

```bash
# Remove and reindex
rm -rf .chromadb
uv run dspy_memory.py index openspec-memories
```

## Best Practices

### 1. Collection Naming

```python
# Use descriptive names
collection_name = "openspec_dml_memories_v1"

# Include version for schema changes
collection_name = f"memories_{version}"
```

### 2. Metadata Design

```python
# Store searchable fields
metadata = {
    "file": "path/to/file.md",
    "category": "DML",
    "difficulty": "intermediate",
    "tags": ["timer", "event"],
    "date": "2025-02-03"
}
```

### 3. ID Conventions

```python
# Use consistent ID patterns
doc_id = f"{filename}_{chunk_index}"
doc_id = f"{category}_{timestamp}_{index}"
```

### 4. Regular Maintenance

```python
# Periodic cleanup
def cleanup_old_documents():
    results = collection.get(where={"date": {"$lt": "2024-01-01"}})
    collection.delete(ids=results["ids"])

# Reindex on schema changes
def update_schema():
    old_collection = client.get_collection("old_name")
    new_collection = client.create_collection("new_name")
    # Migrate data...
```

## Reference Links

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)
- [Sentence Transformers](https://www.sbert.net/)
- [Embedding Models Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
