# LangChain Knowledge Graph - Document to Knowledge Graph Skill

This skill provides knowledge graph construction and querying from documents using LangChain and NetworkX.

## What This Skill Does

- **Extracts knowledge triples** from documents using LLM
- **Builds knowledge graphs** with NetworkX storage
- **Entity-centric queries** with depth traversal
- **Graph visualization** with matplotlib
- **Persistent storage** in GML format
- **Lightweight** - Only LangChain and NetworkX dependencies

## Quick Start

```bash
# One-time setup
cd adk-python/skills/langchain-apps
uv sync

# Test the skill
uv run langchain-memory test

# Build graph from documents
uv run langchain-memory build docs/ --output my_graph.gml

# Query the graph
uv run langchain-memory query my_graph.gml --entity "Python"

# Visualize the graph
uv run langchain-memory visualize my_graph.gml --output graph.png
```

## Files

- `SKILL.md` - Complete documentation for the skill
- `QUICKSTART.md` - Quick start guide
- `pyproject.toml` - Project dependencies and configuration
- `langchain_apps/langchain_memory.py` - Main script
- `references/langchain.md` - LangChain configuration guide

## Key Features

✅ Managed dependencies with uv and pyproject.toml
✅ LLM-based knowledge extraction (GPT-4o-mini)
✅ NetworkX graph storage with persistence
✅ Entity-centric queries with configurable depth
✅ Graph visualization with matplotlib
✅ Support for markdown and text documents
✅ Complete CLI with build, query, and visualize commands

## Usage Examples

### Build Knowledge Graph

```bash
# From a directory
uv run langchain-memory build docs/ --output knowledge.gml

# From a single file
uv run langchain-memory build article.md --output article_graph.gml

# Custom model
uv run langchain-memory build docs/ --model gpt-4 --output knowledge.gml
```

### Query Knowledge Graph

```bash
# Query specific entity
uv run langchain-memory query knowledge.gml --entity "Marie Curie"

# Search for entities
uv run langchain-memory query knowledge.gml --search "Python"

# Show statistics
uv run langchain-memory query knowledge.gml --stats

# Deep traversal
uv run langchain-memory query knowledge.gml --entity "Python" --depth 2
```

### Visualize Graph

```bash
# Basic visualization
uv run langchain-memory visualize knowledge.gml --output graph.png

# Custom size
uv run langchain-memory visualize knowledge.gml --output graph.png --figsize 16,10
```

## How It Works

1. **Extract**: LLM analyzes text and extracts subject-predicate-object triples
2. **Build**: Triples are added to NetworkX directed graph
3. **Store**: Graph is persisted in GML format
4. **Query**: Entity-centric queries with depth-first traversal
5. **Visualize**: Graph layout and rendering with matplotlib

## Technical Stack

- [LangChain](https://python.langchain.com/) - LLM orchestration and knowledge extraction
- [LangChain Community](https://python.langchain.com/docs/integrations/graphs/) - Graph integrations
- [NetworkX](https://networkx.org/) - Graph data structure and algorithms
- [Matplotlib](https://matplotlib.org/) - Graph visualization
- [OpenAI](https://openai.com/) - GPT models for extraction

## Differences from Other Skills

### vs chromadb-apps
- **chromadb-apps**: Vector search, semantic similarity
- **langchain-apps**: Structured relationships, graph traversal

### vs cognee-apps
- **cognee-apps**: Full knowledge graph with entity extraction and graph completion
- **langchain-apps**: Lightweight triple extraction with NetworkX storage

## Prerequisites

- Python 3.10+
- OpenAI API key
- `uv` package manager

## Environment Setup

```bash
# Required: OpenAI API key
export OPENAI_API_KEY='your-api-key-here'

# Optional: Custom model
export OPENAI_MODEL='gpt-4o-mini'
```

## Performance

- **Extraction**: ~2-5 seconds per document (depends on size)
- **Query**: <100ms for entity lookups
- **Visualization**: ~1-2 seconds for graphs with <100 nodes
- **Memory**: ~50MB for typical graphs

## Use Cases

### Documentation Understanding
```bash
# Build graph from technical docs
uv run langchain-memory build technical_docs/ --output tech_graph.gml

# Query relationships
uv run langchain-memory query tech_graph.gml --entity "API"
```

### Research Paper Analysis
```bash
# Extract knowledge from papers
uv run langchain-memory build papers/ --output research_graph.gml

# Find related concepts
uv run langchain-memory query research_graph.gml --search "machine learning"
```

### Knowledge Base Construction
```bash
# Build company knowledge graph
uv run langchain-memory build company_docs/ --output company_kg.gml

# Visualize relationships
uv run langchain-memory visualize company_kg.gml --output company_graph.png
```

## See Also

See SKILL.md for complete documentation with all commands and options.
See QUICKSTART.md for a step-by-step tutorial.
