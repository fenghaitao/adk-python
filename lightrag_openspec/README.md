# LightRAG OpenSpec

**Knowledge graph-based RAG for OpenSpec memories with GitHub Copilot support**

A Python package that provides semantic search and knowledge graph capabilities for OpenSpec documentation using LightRAG and GitHub Copilot's free AI models.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## ✨ Features

- 🧠 **Knowledge Graph RAG** - Understands entity relationships, not just text similarity
- 🆓 **Free with GitHub Copilot** - No additional API costs ($10-19/month subscription)
- 🔍 **4 Search Modes** - naive, local, global, hybrid for different query types
- ⚙️ **Configurable** - Paths, models, all configurable via parameters or env vars
- 🐍 **Python Package** - Proper src/ layout, type hints, installable via pip
- 🧪 **Pytest Tests** - Unit, integration, and auth tests with fixtures
- 📊 **CLI Tools** - `lightrag-index` and `lightrag-query` commands
- 🔗 **ADK Integration** - `LightRAGMemory` class for agent memory

## 📦 Installation

```bash
cd lightrag_openspec
pip install -e .
```

This installs:
- Package with all dependencies
- CLI commands: `lightrag-index`, `lightrag-query`, `lightrag-openspec`
- Forked LiteLLM with GitHub Copilot support

## 🚀 Quick Start

### Index OpenSpec Memories

```bash
# Using CLI
lightrag-index

# With custom paths
lightrag-index --source /path/to/docs --storage /path/to/storage

# Get help
lightrag-index --help
```

### Query Knowledge Base

```bash
# Interactive mode
lightrag-query

# Direct question
lightrag-query "What is DML?"

# With specific mode
lightrag-query "How do I model timers?" --mode hybrid

# Get help
lightrag-query --help
```

### Python API

```python
from lightrag_openspec import OpenSpecIndexer, OpenSpecQuery
from lightrag_openspec.config import LightRAGConfig

# Configure
config = LightRAGConfig(
    working_dir="./my_storage",
    llm_model="github_copilot/gpt-4o-mini"
)

# Index documents
indexer = OpenSpecIndexer(lightrag_config=config)
await indexer.initialize()
await indexer.index_files()
await indexer.finalize()

# Query
query = OpenSpecQuery(config)
await query.initialize()
result = await query.query("What is DML?", mode="hybrid")
await query.finalize()
```

## 📁 Project Structure

```
lightrag_openspec/
├── pyproject.toml              # Package configuration
├── src/lightrag_openspec/      # Python package
│   ├── __init__.py             # Package exports
│   ├── config.py               # Configuration classes
│   ├── indexer.py              # OpenSpecIndexer
│   ├── query.py                # OpenSpecQuery
│   ├── memory.py               # LightRAGMemory (ADK)
│   ├── cli.py                  # CLI commands
│   └── py.typed                # Type hints marker
├── tests/                      # Pytest tests
│   ├── conftest.py             # Fixtures & config
│   ├── fixtures/               # Test data
│   ├── examples/               # Demo scripts
│   ├── test_config.py          # Unit tests
│   ├── test_auth.py            # Auth tests
│   └── test_sample_indexing.py # Integration test
├── lightrag_openspec_storage/  # Knowledge base (1.8MB)
│   ├── 514 nodes (entities)
│   └── 438 edges (relationships)
└── Documentation (8 MD files)

## 📖 Documentation

- **[UNDERSTANDING_LIGHTRAG.md](UNDERSTANDING_LIGHTRAG.md)** - How LightRAG works (499 lines)
- **[LIGHTRAG_CHEATSHEET.md](LIGHTRAG_CHEATSHEET.md)** - Quick reference
- **[LIGHTRAG_GITHUB_COPILOT.md](LIGHTRAG_GITHUB_COPILOT.md)** - GitHub Copilot guide (564 lines)
- **[LIGHTRAG_LITELLM_GUIDE.md](LIGHTRAG_LITELLM_GUIDE.md)** - LiteLLM integration (522 lines)
- **[OPENSPEC_INDEXING_GUIDE.md](OPENSPEC_INDEXING_GUIDE.md)** - Usage guide (283 lines)
- **[tests/README.md](tests/README.md)** - Test documentation

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run fast tests only (no API calls)
pytest tests/ -m "not slow and not requires_api"

# Run with coverage
pytest tests/ --cov=lightrag_openspec --cov-report=html

# Run specific test
pytest tests/test_config.py -v
```

Test categories:
- **Unit tests** (`test_config.py`) - Fast, no API
- **Auth tests** (`test_auth.py`) - Requires GitHub Copilot
- **Integration tests** (`test_sample_indexing.py`) - Slow, full workflow

## 📊 Current Knowledge Base

**Status:** ✅ Indexed and ready

- **Nodes:** 514 entities (DML, Simics, Timers, UART, I2C, etc.)
- **Edges:** 438 relationships (connections between concepts)
- **Storage:** 1.8MB in `lightrag_openspec_storage/`
- **Source:** OpenSpec memories markdown files

## 💡 Key Features

- ✅ **Knowledge Graph RAG** - Understands entity relationships
- ✅ **4 Search Modes** - naive, local, global, hybrid
- ✅ **GitHub Copilot** - Free with subscription ($10-19/month)
- ✅ **No GitHub CLI needed** - OAuth2 handled automatically
- ✅ **Multi-hop reasoning** - Traverse relationships for context

## 📖 Learning Path

1. **Start with visuals:**
   ```bash
   ../.venv/bin/python tmp_rovodev_visualize_lightrag.py
   ```

2. **Read the guide:**
   ```bash
   cat UNDERSTANDING_LIGHTRAG.md
   ```

3. **Quick reference:**
   ```bash
   cat LIGHTRAG_CHEATSHEET.md
   ```

4. **Try queries:**
   ```bash
   ../.venv/bin/python query_openspec_memories.py
   ```

## 🔧 Advanced Usage

### Re-index After Updates

```bash
# Add new files to ../openspec-memories/
# Then re-run:
../.venv/bin/python index_openspec_with_copilot.py
```

### Start Fresh

```bash
# Delete storage and re-index
rm -rf lightrag_openspec_storage/
../.venv/bin/python index_openspec_with_copilot.py
```

### Custom Queries

```python
import asyncio
from lightrag import LightRAG, QueryParam

async def custom_query():
    rag = LightRAG(working_dir="./lightrag_openspec_storage", ...)
    await rag.initialize_storages()
    
    result = await rag.aquery(
        "Your question?",
        param=QueryParam(
            mode="hybrid",
            top_k=50,
            max_token_for_text_unit=4000,
        )
    )
    
    print(result)
    await rag.finalize_storages()

asyncio.run(custom_query())
```

## 📚 Available Models

### Chat Models
- `github_copilot/gpt-4o` - Best quality
- `github_copilot/gpt-4o-mini` - Fast (default)
- `github_copilot/o1-preview` - Advanced reasoning
- `github_copilot/o1-mini` - Reasoning, fast

### Embedding Models
- `github_copilot/text-embedding-3-small` - 1536 dim (default)
- `github_copilot/text-embedding-3-large` - 3072 dim

## 💰 Cost

**FREE with GitHub Copilot subscription!**
- No additional API costs
- Unlimited usage within rate limits (~30 req/min)
- Subscription: $10-19/month

## 🔗 Integration

### With ADK Agents

See `lightrag_adk_example.py` for complete example:

```python
class LightRAGMemory:
    async def add_memory(self, content):
        await self.rag.ainsert(content)
    
    async def query_memory(self, query):
        return await self.rag.aquery(query, mode="hybrid")
```

## 📝 Notes

- **LightRAG submodule:** Located at `../lightrag/`
- **Source docs:** Located at `../openspec-memories/`
- **Python environment:** Use `../.venv/bin/python`

## 🆘 Troubleshooting

### Scripts not finding lightrag

Scripts use `sys.path.insert(0, '../lightrag')` to find the submodule.

### Authentication errors

Test with:
```bash
../.venv/bin/python tmp_test_copilot_auth.py
```

### Storage not found

Run indexing first:
```bash
../.venv/bin/python index_openspec_with_copilot.py
```

## 📖 Documentation Index

1. **Getting Started:** This README
2. **Understanding Concepts:** UNDERSTANDING_LIGHTRAG.md
3. **Quick Reference:** LIGHTRAG_CHEATSHEET.md
4. **GitHub Copilot:** LIGHTRAG_GITHUB_COPILOT.md
5. **OpenSpec Usage:** OPENSPEC_INDEXING_GUIDE.md
6. **Complete Summary:** LIGHTRAG_SUMMARY.md
7. **LiteLLM Guide:** LIGHTRAG_LITELLM_GUIDE.md

---

**Last Updated:** 2026-01-29  
**Status:** ✅ Fully functional  
**Knowledge Base:** 62 entities, 47 relationships, 1.8MB

## 🔧 Configuration

### Environment Variables

```bash
# LightRAG configuration
export LIGHTRAG_WORKING_DIR="/path/to/storage"
export LIGHTRAG_LLM_MODEL="github_copilot/gpt-4o-mini"
export LIGHTRAG_EMBEDDING_MODEL="github_copilot/text-embedding-3-small"

# OpenSpec configuration
export OPENSPEC_MEMORIES_DIR="/path/to/memories"
```

### Python API Configuration

```python
from lightrag_openspec.config import LightRAGConfig, OpenSpecConfig

# Custom configuration
config = LightRAGConfig(
    working_dir="./custom_storage",
    llm_model="github_copilot/gpt-4o",
    embedding_model="github_copilot/text-embedding-3-large",
    embedding_dim=3072,
)

# From environment variables
config = LightRAGConfig.from_env()
```

## 💡 Usage Examples

### CLI Examples

```bash
# Index with defaults (auto-detect paths)
lightrag-index

# Index with custom paths
lightrag-index --source ~/docs --storage ~/storage

# Query interactively
lightrag-query

# Query with question
lightrag-query "What is DML?"

# Query with specific mode
lightrag-query "Best practices for testing?" --mode global
```

### Python API Examples

```python
# Simple query
from lightrag_openspec import OpenSpecQuery

query = OpenSpecQuery()
await query.initialize()
result = await query.query("What is DML?")
print(result)
await query.finalize()

# Get entities
entities = await query.get_entities()
print(f"Total entities: {len(entities)}")

# Get knowledge graph for entity
kg = await query.get_knowledge_graph("DML", max_depth=2)
print(f"Nodes: {kg.nodes}")
print(f"Edges: {kg.edges}")
```

### ADK Agent Integration

```python
from lightrag_openspec import LightRAGMemory

# Create memory for ADK agent
memory = LightRAGMemory(working_dir="./agent_memory")
await memory.initialize()

# Add memories
await memory.add_memory("Agent learned: DML is for device modeling")

# Query memory
context = await memory.query_memory("What did I learn about DML?")

# Get all entities
entities = await memory.get_entities()

await memory.finalize()
```

## 🎯 Search Modes

| Mode | Best For | Speed | Quality | Use Case |
|------|----------|-------|---------|----------|
| **naive** | Simple facts | ⚡⚡⚡ | ⭐⭐ | "What is X?" |
| **local** | Entity queries | ⚡⚡ | ⭐⭐⭐ | "What does X do?" |
| **global** | Themes/patterns | ⚡ | ⭐⭐⭐⭐ | "What are main themes?" |
| **hybrid** | Complex queries | ⚡⚡ | ⭐⭐⭐⭐⭐ | Most queries (recommended) |

## 🤝 Contributing

See [tests/README.md](tests/README.md) for development setup and testing guidelines.

## 📄 License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **LightRAG**: https://github.com/fenghaitao/lightrag
- **LiteLLM (Forked)**: https://github.com/fenghaitao/litellm
- **ADK**: https://github.com/google/adk-python

---

**Built with ❤️ for OpenSpec documentation and ADK integration**
