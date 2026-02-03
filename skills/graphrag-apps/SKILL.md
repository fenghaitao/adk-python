---
name: graphrag-memory
description: Build and query knowledge graphs from markdown documents using Microsoft GraphRAG. Extract entities, relationships, and communities with LLM-powered graph construction for sophisticated retrieval-augmented generation.
homepage: https://github.com/google/adk-python
metadata: {"clawdbot":{"emoji":"🕸️","requires":{"bins":["uv"]}}}
---

# GraphRAG Memory - Knowledge Graph RAG

Build and query knowledge graphs from markdown documents using Microsoft's GraphRAG system.

## Quick Start

### Test Setup
```bash
uv run {baseDir}/scripts/graphrag_memory.py test
```

### Initialize and Query
```bash
# Initialize project
uv run {baseDir}/scripts/graphrag_memory.py init

# Index documents
uv run {baseDir}/scripts/graphrag_memory.py index --input openspec-memories

# Query with local search
uv run {baseDir}/scripts/graphrag_memory.py query "How to implement timer?" --method local

# Query with global search
uv run {baseDir}/scripts/graphrag_memory.py query "What are the main concepts?" --method global

# Check status
uv run {baseDir}/scripts/graphrag_memory.py status
```

## Features

✅ **Knowledge graph construction** - Extract entities and relationships using LLM  
✅ **Multiple query methods** - Local, global, and drift search strategies  
✅ **Community detection** - Hierarchical understanding of document structure  
✅ **GitHub Copilot support** - Use your existing Copilot subscription  
✅ **OpenAI compatible** - Works with OpenAI API  
✅ **Self-contained** - PEP 723 inline dependencies  
✅ **Caching built-in** - Save LLM costs by caching responses

## Commands

### Test Setup
```bash
uv run {baseDir}/scripts/graphrag_memory.py test
```
Validates dependencies and verifies the skill is ready to use.

### Initialize Project
```bash
# Initialize in current directory
uv run {baseDir}/scripts/graphrag_memory.py init

# Initialize in custom directory
uv run {baseDir}/scripts/graphrag_memory.py init --root ./my_graphrag

# Force reinitialize
uv run {baseDir}/scripts/graphrag_memory.py init --force
```

Creates project structure:
- `settings.yaml` - Configuration file
- `prompts/` - LLM prompt templates
- `input/` - Document directory
- `output/` - Knowledge graph storage
- `cache/` - LLM response cache

### Index Documents
```bash
# Index from directory
uv run {baseDir}/scripts/graphrag_memory.py index --input openspec-memories

# Index with verbose output
uv run {baseDir}/scripts/graphrag_memory.py index --input docs/ --verbose

# Index with custom root
uv run {baseDir}/scripts/graphrag_memory.py index --root ./my_kb --input docs/
```

**Indexing Process:**
1. Chunks documents into manageable pieces
2. Extracts entities (people, places, concepts) using LLM
3. Extracts relationships between entities
4. Builds knowledge graph
5. Creates embeddings for vector search
6. Detects communities for hierarchical queries

### Query Knowledge Graph
```bash
# Local search - detailed, entity-focused
uv run {baseDir}/scripts/graphrag_memory.py query "How to implement timer?" --method local

# Global search - high-level, community-focused
uv run {baseDir}/scripts/graphrag_memory.py query "What are the main patterns?" --method global

# Drift search - exploratory
uv run {baseDir}/scripts/graphrag_memory.py query "Explain the architecture" --method drift

# With custom root
uv run {baseDir}/scripts/graphrag_memory.py query "..." --root ./my_kb
```

### Check Status
```bash
# Show project status
uv run {baseDir}/scripts/graphrag_memory.py status

# With custom root
uv run {baseDir}/scripts/graphrag_memory.py status --root ./my_kb
```

## Configuration

### Default Settings

The `settings.yaml` file contains all configuration:

```yaml
### LLM settings ###
models:
  default_chat_model:
    type: chat
    model_provider: github_copilot  # or openai
    model: gpt-4o
    concurrent_requests: 5
    requests_per_minute: 30
    
  default_embedding_model:
    type: embedding
    model_provider: github_copilot
    model: text-embedding-3-small

### Input settings ###
input:
  storage:
    type: file
    base_dir: "input"
  file_type: text
  file_pattern: ".*\\.md"

chunks:
  size: 1500
  overlap: 150

### Output settings ###
output:
  type: file
  base_dir: "output"
  
cache:
  type: file
  base_dir: "cache"

vector_store:
  default_vector_store:
    type: lancedb
    db_uri: output/lancedb
```

### GitHub Copilot Configuration

Default configuration uses GitHub Copilot (OAuth2 authentication):

```yaml
models:
  default_chat_model:
    model_provider: github_copilot
    api_key: copilot  # Placeholder - auto-authenticated
    model: gpt-4o
```

No API key needed if you have GitHub Copilot access!

### OpenAI Configuration

To use OpenAI, edit `settings.yaml`:

```yaml
models:
  default_chat_model:
    model_provider: openai
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o
    
  default_embedding_model:
    model_provider: openai
    api_key: ${OPENAI_API_KEY}
    model: text-embedding-3-small
```

Set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

## Query Methods

### Local Search

**Best for:** Specific questions about entities and their relationships

**How it works:**
- Finds relevant entities in the query
- Retrieves connected entities and relationships
- Uses vector similarity for relevant text chunks
- Provides detailed, cited answers

**Example questions:**
- "How does the timer implementation work in DML?"
- "What are the register access patterns for interrupts?"
- "Explain the relationship between events and methods"

```bash
uv run {baseDir}/scripts/graphrag_memory.py query \
  "How to implement timer in DML?" \
  --method local
```

### Global Search

**Best for:** Broad questions about themes and high-level concepts

**How it works:**
- Analyzes community summaries (hierarchical clusters)
- Uses map-reduce pattern across communities
- Provides high-level overview with supporting details

**Example questions:**
- "What are the main architectural patterns?"
- "Summarize the testing methodology"
- "What are the core concepts in the documentation?"

```bash
uv run {baseDir}/scripts/graphrag_memory.py query \
  "What are the main concepts in DML?" \
  --method global
```

### Drift Search

**Best for:** Exploratory analysis and contextual discovery

**How it works:**
- Combines local and global approaches
- Explores related concepts through graph traversal
- Good for open-ended investigation

**Example questions:**
- "Explain the relationship between DML and testing"
- "How do the different components interact?"
- "Explore the implementation patterns"

```bash
uv run {baseDir}/scripts/graphrag_memory.py query \
  "Explain the DML modeling approach" \
  --method drift
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Initialization | ~10s | One-time setup |
| Indexing (small) | ~5-10 min | 10-20 files, ~100KB |
| Indexing (medium) | ~15-30 min | 50-100 files, ~500KB |
| Indexing (large) | ~1-2 hours | 200+ files, ~2MB |
| Local query | ~5-10s | Per query |
| Global query | ~15-30s | Per query |

**Factors affecting speed:**
- LLM response time (major factor)
- Number of documents
- Document complexity
- Concurrent request limits
- Caching (dramatically speeds up re-indexing)

## Examples

### Initialize New Project

```bash
cd /path/to/project
uv run {baseDir}/scripts/graphrag_memory.py init
```

### Index OpenSpec Memories

```bash
uv run {baseDir}/scripts/graphrag_memory.py index --input openspec-memories
```

### Search for Specific Information

```bash
# Detailed answer about timers
uv run {baseDir}/scripts/graphrag_memory.py query \
  "What are the best practices for implementing timers?" \
  --method local

# Overview of testing approaches
uv run {baseDir}/scripts/graphrag_memory.py query \
  "Summarize the testing methodology" \
  --method global
```

### Check What's Indexed

```bash
uv run {baseDir}/scripts/graphrag_memory.py status
```

## Troubleshooting

### Check Setup
```bash
uv run {baseDir}/scripts/graphrag_memory.py test
```

### Common Issues

**Project not found**
```bash
# Initialize first
uv run {baseDir}/scripts/graphrag_memory.py init

# Or specify root
uv run {baseDir}/scripts/graphrag_memory.py query "..." --root ./my_project
```

**No indexed data**
```bash
# Run indexing first
uv run {baseDir}/scripts/graphrag_memory.py index --input openspec-memories

# Check status
uv run {baseDir}/scripts/graphrag_memory.py status
```

**Indexing fails**
```bash
# Check LLM configuration in settings.yaml
# Verify API keys are set
# Try with verbose flag
uv run {baseDir}/scripts/graphrag_memory.py index --input docs/ --verbose
```

**LLM rate limits**

Edit `settings.yaml`:
```yaml
models:
  default_chat_model:
    concurrent_requests: 3  # Lower from 5
    requests_per_minute: 20  # Lower from 30
```

**Dependencies not found**
```bash
# The script auto-installs dependencies via uv run
# If issues persist, ensure uv is up to date:
pip install --upgrade uv
```

## Cost Considerations

⚠️ **GraphRAG uses LLMs extensively - costs can add up!**

**Estimated costs using GPT-4o:**
- Small (10-20 files): $5-10
- Medium (50-100 files): $20-50
- Large (200+ files): $100+

**Cost-saving strategies:**
1. **Use caching** (enabled by default) - avoids re-processing
2. **Start small** - test with 5-10 files first
3. **Use cheaper models** - gpt-3.5-turbo for testing
4. **Use GitHub Copilot** - included in subscription
5. **Reduce concurrent requests** - slower but cheaper
6. **Disable claims extraction** (already disabled by default)

## Technical Details

**Built with:**
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag) - Knowledge graph construction
- [LanceDB](https://lancedb.com/) - Vector database
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal UI

**Architecture:**
1. **Chunking** - Splits documents into overlapping chunks
2. **Entity Extraction** - LLM identifies entities and relationships
3. **Graph Construction** - Builds knowledge graph from entities
4. **Community Detection** - Hierarchical clustering using Leiden algorithm
5. **Embedding** - Creates vectors for semantic search
6. **Query** - Combines graph and vector search for answers

**Dependencies:**
- 3 direct dependencies via PEP 723
- ~100 total packages (including GraphRAG dependencies)
- ~200MB download on first run

## Comparison with ChromaDB-apps

| Feature | GraphRAG | ChromaDB |
|---------|----------|----------|
| **Approach** | Knowledge graph | Vector search |
| **Complexity** | High | Low |
| **Setup time** | 5-60 min | 1-5 min |
| **Query methods** | 3 (local/global/drift) | 1 (semantic) |
| **Best for** | Complex reasoning | Fast retrieval |
| **Cost** | $$$ (LLM-heavy) | $ (embeddings only) |
| **Relationship understanding** | Excellent | Limited |
| **Speed** | Slower | Faster |

**When to use GraphRAG:**
- Complex domain with interconnected concepts
- Need to understand relationships
- Have budget for LLM processing
- Want hierarchical/community understanding

**When to use ChromaDB:**
- Simple retrieval needs
- Fast iteration required
- Limited budget
- Straightforward Q&A

## References

- [GraphRAG Documentation](https://microsoft.github.io/graphrag/)
- [GraphRAG Research Paper](https://arxiv.org/pdf/2404.16130)
- [Microsoft Research Blog](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/)
