# GraphRAG Memory Skill

Build and query knowledge graphs from markdown documents using Microsoft GraphRAG.

## What is GraphRAG?

GraphRAG extracts entities, relationships, and communities from documents using LLMs to build a knowledge graph. This enables sophisticated retrieval-augmented generation with:

- **Entity extraction** - Identifies people, places, concepts
- **Relationship mapping** - Understands connections between entities
- **Community detection** - Hierarchical clustering for high-level understanding
- **Multiple query methods** - Local (detailed), global (overview), drift (exploratory)

## Quick Links

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [SKILL.md](SKILL.md) - Complete documentation
- [GraphRAG Documentation](https://microsoft.github.io/graphrag/)
- [GraphRAG Research Paper](https://arxiv.org/pdf/2404.16130)

## Installation

```bash
# Initialize project
uv run --directory .kiro/skills/graphrag-apps graphrag-memory init

# Index documents
uv run --directory .kiro/skills/graphrag-apps graphrag-memory index --input docs/

# Query
uv run --directory .kiro/skills/graphrag-apps graphrag-memory query "your question" --method local
```

## When to Use GraphRAG

**Use GraphRAG when:**
- You need to understand relationships between concepts
- Documents have interconnected information
- You want hierarchical/community understanding
- You have budget for LLM processing

**Use ChromaDB when:**
- You need fast, simple retrieval
- Budget is limited
- Straightforward Q&A is sufficient

## Features

✅ Knowledge graph construction with LLM  
✅ Multiple query methods (local/global/drift)  
✅ Community detection for hierarchical understanding  
✅ GitHub Copilot support (no API key needed)  
✅ OpenAI compatible  
✅ Persistent .venv for fast execution  
✅ Built-in caching to save LLM costs

## Cost Warning

⚠️ GraphRAG uses LLMs extensively. Start with 5-10 files to test before indexing large document sets.

## Migration from PEP 723

This skill was migrated from PEP 723 inline dependencies to `pyproject.toml` for:
- Persistent virtual environment (faster execution)
- Better dependency management
- Consistent with other skills

Old usage: `uv run scripts/graphrag_memory.py`  
New usage: `uv run --directory .kiro/skills/graphrag-apps graphrag-memory`

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [SKILL.md](SKILL.md) - Complete documentation with all features
- [pyproject.toml](pyproject.toml) - Package configuration

## Support

For issues or questions:
1. Check [SKILL.md](SKILL.md) troubleshooting section
2. Review [GraphRAG documentation](https://microsoft.github.io/graphrag/)
3. Open an issue in the repository
