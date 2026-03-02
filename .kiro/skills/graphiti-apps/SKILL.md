---
name: graphiti-apps
description: Build and query knowledge graphs from documents using Graphiti and Neo4j. Extract entities, relationships, and communities with LLM-powered graph construction. Supports group-scoped entity isolation, semantic search, and multi-domain ingestion.
homepage: https://github.com/google/adk-python
metadata: {"clawdbot":{"emoji":"🕸️","requires":{"bins":["uv","neo4j"]}}}
---

# Graphiti Memory - Knowledge Graph Indexing & Retrieval

Index documents and query a Neo4j knowledge graph using [Graphiti](https://github.com/getzep/graphiti) for LLM-powered entity and relationship extraction.

## Quick Start

### One-Time Setup (Required)
```bash
# Create persistent .venv with all dependencies
uv sync --directory {baseDir}
```

This pre-builds the venv so every subsequent `uv run` skips dependency
resolution and starts fast (~2s vs ~20s+ without it).

### Test Setup
```bash
uv run --directory {baseDir} graphiti-memory test
```

### Ingest and Query
```bash
# Ingest a directory of markdown files
uv run --directory {baseDir} graphiti-memory ingest-directory ./docs --pattern "*.md"

# Query the graph
uv run --directory {baseDir} graphiti-memory query "What are the main components?"

# View statistics
uv run --directory {baseDir} graphiti-memory stats
```

## Prerequisites

- Neo4j running locally (or Docker / Aura cloud)
- LLM access: GitHub Copilot, OpenAI, or Ollama
- `uv` package manager

### Start Neo4j with Docker
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

## Configuration

Create a `.env` file in your project directory:

```bash
# LLM (GitHub Copilot default)
LLM_CHOICE=github_copilot/gpt-4o
EMBEDDING_MODEL_CHOICE=github_copilot/text-embedding-3-small

# OpenAI alternative
# LLM_CHOICE=gpt-4o-mini
# LLM_API_KEY=sk-...
# EMBEDDING_MODEL_CHOICE=text-embedding-3-small
# EMBEDDING_API_KEY=sk-...

# Neo4j (local profile default)
NEO4J_PROFILE=local
NEO4J_URI_LOCAL=bolt://localhost:7687
NEO4J_USERNAME_LOCAL=neo4j
NEO4J_PASSWORD_LOCAL=password

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
CONFIDENCE_THRESHOLD=0.5
MAX_CONCURRENT_CHUNKS=2
```

### Neo4j Profiles

Set `NEO4J_PROFILE` to switch between environments:

| Profile | Variables |
|---------|-----------|
| `local` (default) | `NEO4J_URI_LOCAL`, `NEO4J_USERNAME_LOCAL`, `NEO4J_PASSWORD_LOCAL` |
| `docker` | `NEO4J_URI_DOCKER`, `NEO4J_USERNAME_DOCKER`, `NEO4J_PASSWORD_DOCKER` |
| `cloud` | `NEO4J_URI_CLOUD`, `NEO4J_USERNAME_CLOUD`, `NEO4J_PASSWORD_CLOUD` |

## Commands

### Test Setup
```bash
uv run --directory {baseDir} graphiti-memory test
```
Checks dependencies and Neo4j connectivity.

### Ingest Text
```bash
uv run --directory {baseDir} graphiti-memory ingest-text "Your content here" \
  --document-id my_doc \
  --group-id doc_markdown
```

### Ingest File
```bash
uv run --directory {baseDir} graphiti-memory ingest-file README.md
uv run --directory {baseDir} graphiti-memory ingest-file code.py --group-id code_python
```

Group ID is auto-detected from file extension if not specified.

### Ingest Directory
```bash
# Ingest all markdown files recursively
uv run --directory {baseDir} graphiti-memory ingest-directory ./docs --pattern "*.md"

# Ingest Python files, non-recursive
uv run --directory {baseDir} graphiti-memory ingest-directory ./src \
  --pattern "*.py" \
  --no-recursive \
  --group-id code_python
```

### Query
```bash
# Natural language query
uv run --directory {baseDir} graphiti-memory query "What are the main components?"

# Limit results
uv run --directory {baseDir} graphiti-memory query "authentication flow" --max-results 5

# Scope to a group
uv run --directory {baseDir} graphiti-memory query "register access" --group-id code_python

# JSON output
uv run --directory {baseDir} graphiti-memory query "dependencies" --format json
```

### Statistics
```bash
uv run --directory {baseDir} graphiti-memory stats
```
Shows entity count, relationship count, episode count, and breakdown by group.

### Configuration Info
```bash
uv run --directory {baseDir} graphiti-memory info
```

### Clear Graph
```bash
# Clear everything (requires --confirm)
uv run --directory {baseDir} graphiti-memory clear-graph --confirm

# Clear a specific group only
uv run --directory {baseDir} graphiti-memory clear-graph --confirm --group-id doc_markdown
```

## Group IDs

Content is categorised by group for logical isolation. Graphiti uses groups for community detection within boundaries.

| Group ID | Content Type |
|----------|-------------|
| `doc_markdown` | Markdown documentation |
| `doc_text` | Plain text files |
| `doc_rst` | reStructuredText |
| `code_python` | Python source files |
| `code_c` | C/C++ source files |
| `config_json` | JSON configuration |
| `config_yaml` | YAML configuration |
| `generic` | Fallback / unclassified |

Group IDs use underscores (not colons) — Graphiti validation requirement.

## Python API

```python
import asyncio
from graphiti_core import Graphiti
from datetime import datetime, timezone

async def example():
    graphiti = Graphiti(
        "bolt://localhost:7687",
        "neo4j",
        "password",
    )
    await graphiti.build_indices_and_constraints()

    # Ingest an episode
    await graphiti.add_episode(
        name="my_doc_chunk_0",
        episode_body="AI agents can use tools to interact with external systems.",
        source_description="document:my_doc",
        reference_time=datetime.now(timezone.utc),
        group_id="doc_markdown",
    )

    # Search
    results = await graphiti.search(
        query="What can AI agents do?",
        num_results=5,
    )
    for r in results:
        print(r.fact)

    await graphiti.close()

asyncio.run(example())
```

## Features

- LLM-powered entity and relationship extraction via Graphiti
- Group-scoped entity isolation (multi-domain graphs)
- Semantic search using embeddings
- GitHub Copilot support via LiteLLM (no OpenAI key required)
- Neo4j profile switching (local / docker / cloud)
- Auto-detected group IDs from file extensions
- Exponential back-off retry on rate limits
- Neo4j-compatible JSON flattening for complex LLM responses

## Architecture

```
graphiti-apps/
├── pyproject.toml
├── SKILL.md
└── graphiti_apps/
    ├── __init__.py
    ├── graphiti_memory.py   # CLI entry point (Typer)
    └── litellm_clients.py   # Custom LiteLLM → Graphiti bridge
```

**How it works:**

1. Text is split into overlapping chunks (configurable size/overlap)
2. Each chunk is added to Graphiti as an "episode"
3. Graphiti calls the LLM to extract entities and relationships
4. Entities and relationships are stored in Neo4j
5. Queries use Graphiti's semantic search (embeddings + graph traversal)

## Troubleshooting

### Neo4j not connecting
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Verify credentials
uv run --directory {baseDir} graphiti-memory test
```

### Rate limit errors
Graphiti retries automatically with exponential back-off. To reduce pressure:
```bash
# Lower concurrency in .env
MAX_CONCURRENT_CHUNKS=1
```

### Dependencies missing
```bash
rm -rf {baseDir}/.venv
uv sync --directory {baseDir}
```

### Empty query results
```bash
# Check something is indexed
uv run --directory {baseDir} graphiti-memory stats

# Try broader terms
uv run --directory {baseDir} graphiti-memory query "main concepts" --max-results 20
```

## Performance

| Operation | Approximate time |
|-----------|-----------------|
| Ingest 1 chunk | 2–5s (LLM call) |
| Ingest 10-file directory | 1–5 min |
| Query | 1–3s |

LLM response time dominates. Use `MAX_CONCURRENT_CHUNKS=1` if hitting rate limits.

## References

- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
