# Cognee-OpenSpec

Knowledge graph-based memory system for OpenSpec using Cognee's ECL pipeline.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 minutes
- **[MODEL_SETUP.md](MODEL_SETUP.md)** - Detailed model configuration guide
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Complete setup summary

## Overview

This package provides a Cognee-based implementation for building and querying knowledge graphs from OpenSpec memory documents. It transforms markdown documentation into an intelligent, relationship-aware knowledge base that supports complex reasoning and multiple search strategies.

## Features

- **Knowledge Graph Construction**: Automatic entity extraction and relationship detection
- **Multiple Search Strategies**: 8+ retrieval methods (graph completion, chunks, summaries, CoT, temporal)
- **Interactive Visualization**: HTML-based graph explorer
- **Enrichment Pipeline**: Memify for adding domain-specific associations
- **Temporal Support**: Time-aware graph traversal
- **Category Filtering**: DML, Test, and General document categorization

## Installation

```bash
# From adk-python/cognee-openspec directory
uv sync --dev --all-extras --reinstall
```

This installs cognee from the `../cognee` submodule as an editable dependency.

## Model Configuration

Cognee-OpenSpec supports multiple LLM providers through LiteLLM:

- **OpenAI** (default): GPT-4, GPT-3.5, etc.
- **iflow**: Alibaba Cloud's Qwen models (cost-effective)
- **GitHub Copilot**: GPT-4 via your Copilot subscription
- **Local models**: Ollama, LM Studio, etc.

See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed configuration instructions.

### Quick Setup

```bash
# Test your configuration
python test_model_config.py

# Setup iflow
./setup_iflow.sh your-iflow-api-key

# Setup GitHub Copilot
./setup_github_copilot.sh
```

## Quick Start

### 1. Setup

```bash
# Option 1: OpenAI (default)
export LLM_API_KEY="sk-your-openai-api-key"

# Option 2: iflow (Alibaba Cloud)
export LLM_API_KEY="your-iflow-api-key"
export LLM_MODEL="dashscope/qwen3-coder-plus"
export LLM_ENDPOINT="https://apis.iflow.cn/v1/"
export LLM_PROVIDER="custom"

# Option 3: GitHub Copilot
export LLM_MODEL="github_copilot/gpt-4o"
export LLM_PROVIDER="custom"
```

See [MODEL_SETUP.md](MODEL_SETUP.md) for detailed configuration options.

### 2. Index Memories

Build a knowledge graph from your markdown files:

```bash
# Basic indexing
cognee-memory index openspec-memories

# With visualization
cognee-memory index openspec-memories --visualize

# Force reindex
cognee-memory index openspec-memories --force
```

### 3. Search

Query using different strategies:

```bash
# Graph completion (LLM answers with graph context)
cognee-memory search "How do I implement a DML register?"

# Semantic chunks
cognee-memory search "device examples" --search-type CHUNKS

# Document summaries
cognee-memory search "test overview" --search-type SUMMARIES

# Chain-of-thought reasoning
cognee-memory search "What are the steps to test a device?" \
  --search-type GRAPH_COMPLETION_COT
```

### 4. Visualize

Generate an interactive graph visualization:

```bash
cognee-memory visualize
```

Open `openspec_graph.html` in your browser to explore entities and relationships.

## Python API

```python
import asyncio
from cognee_openspec import CogneeMemoryIndexer, CogneeMemoryRetriever

async def main():
  # Index memories
  indexer = CogneeMemoryIndexer(
    memory_dir="openspec-memories",
    dataset_name="openspec_memories"
  )
  result = await indexer.index_memories()
  print(f"Indexed {result['files_indexed']} files")
  
  # Search
  retriever = CogneeMemoryRetriever(
    search_type="GRAPH_COMPLETION",
    top_k=5
  )
  passages = await retriever.search("How do I write a DML device?")
  
  for passage in passages:
    print(passage)
  
  # Visualize
  viz_path = await indexer.visualize_graph("graph.html")
  print(f"Visualization: {viz_path}")

asyncio.run(main())
```

## Search Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|
| `GRAPH_COMPLETION` | Natural language questions | "How do I...?" |
| `CHUNKS` | Finding specific examples | "show me code for..." |
| `SUMMARIES` | Getting overviews | "what is...?" |
| `GRAPH_COMPLETION_COT` | Complex reasoning | "what are the steps to...?" |
| `TEMPORAL` | Time-aware queries | "recent changes to..." |

## Architecture

```
OpenSpec Memories (Markdown)
         ↓
    Cognee ECL Pipeline
    ├── Extract: Ingest documents
    ├── Cognify: Build knowledge graph
    │   ├── Entity extraction
    │   ├── Relationship detection
    │   └── Semantic embeddings
    └── Load: Store in graph + vector DB
         ↓
    Memify Enrichment
    ├── Domain-specific associations
    ├── Coding rules extraction
    └── Custom enrichments
         ↓
    Knowledge Graph
    ├── Nodes: Entities (concepts, functions, etc.)
    ├── Edges: Relationships (implements, uses, etc.)
    └── Embeddings: Vector representations
         ↓
    Multi-Strategy Retrieval
    ├── Graph traversal + LLM reasoning
    ├── Vector similarity search
    └── Hybrid approaches
```

## CLI Commands

```bash
# Index
cognee-memory index <directory> [--force] [--temporal] [--visualize]

# Search
cognee-memory search <query> [--search-type TYPE] [--category CAT] [--k N]

# Visualize
cognee-memory visualize [--output PATH]

# Stats
cognee-memory stats
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=cognee_openspec --cov-report=html
```

### Running Examples

```bash
# Set API key
export LLM_API_KEY="your-key"

# Run example
python examples/memory_example.py
```

### Code Style

Follow ADK style guidelines:
- 2-space indentation
- 80-character line length
- Proper copyright headers
- `from __future__ import annotations`

Format code:
```bash
black cognee_openspec/ tests/ examples/
pylint cognee_openspec/
```

## Project Structure

```
cognee-openspec/
├── cognee_openspec/
│   ├── __init__.py
│   └── memory/
│       ├── __init__.py
│       ├── indexer.py      # Knowledge graph builder
│       ├── retriever.py    # Multi-strategy search
│       └── cli.py          # Command-line interface
├── tests/
│   └── test_memory.py      # Unit tests
├── examples/
│   └── memory_example.py   # Demonstration script
├── pyproject.toml          # Package configuration
└── README.md               # This file
```

## Advanced Usage

### Custom Enrichment

Add domain-specific enrichments using memify:

```python
import cognee
from cognee.modules.pipelines.tasks.task import Task

# Define custom extraction
async def extract_dml_patterns(subgraphs):
  for subgraph in subgraphs:
    for node in subgraph.nodes.values():
      if "register" in node.attributes.get("text", "").lower():
        yield node.attributes["text"]

# Define custom enrichment
async def add_dml_best_practices(data: str):
  # Your custom logic
  pass

# Run memify
await cognee.memify(
  dataset="openspec_memories",
  extraction_tasks=[Task(extract_dml_patterns)],
  enrichment_tasks=[Task(add_dml_best_practices)]
)
```

### Temporal Analysis

Enable temporal features:

```bash
cognee-memory index openspec-memories --temporal
cognee-memory search "recent DML changes" --search-type TEMPORAL
```

## Troubleshooting

### LLM API Key Not Set
```bash
export LLM_API_KEY="your-openai-api-key"
```

### Import Errors
```bash
cd adk-python/cognee-openspec
uv sync --dev --all-extras --reinstall
```

### Empty Search Results
- Verify indexing: `cognee-memory stats`
- Try different search type: `--search-type CHUNKS`
- Increase results: `--k 10`

## References

- [Cognee Fork (fenghaitao)](https://github.com/fenghaitao/cognee)
- [Cognee Documentation](https://docs.cognee.ai/)
- [Cognee Original](https://github.com/topoteretes/cognee)
- [ADK Python](https://github.com/google/adk-python)

## License

Copyright 2025 Google LLC. Licensed under Apache 2.0.
