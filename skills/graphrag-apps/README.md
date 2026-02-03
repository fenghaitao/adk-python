# GraphRAG Memory - Knowledge Graph Retrieval Skill

This skill provides GraphRAG-based knowledge graph construction and retrieval for document analysis using Microsoft's GraphRAG system.

## What This Skill Does

- **Builds knowledge graphs** from markdown documents
- **Multiple query methods** (local, global, drift search)
- **LLM-powered extraction** of entities and relationships
- **Community detection** for hierarchical understanding
- **Works with GitHub Copilot or OpenAI**

## Quick Test

```bash
# Test the skill
cd /path/to/your/project
uv run skills/graphrag-apps/scripts/graphrag_memory.py test

# Initialize project
uv run skills/graphrag-apps/scripts/graphrag_memory.py init

# Index memories
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input openspec-memories

# Query
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "What are the main concepts?"
```

## Files

- `SKILL.md` - Complete documentation for the skill
- `scripts/graphrag_memory.py` - Main script with PEP 723 dependencies
- `QUICKSTART.md` - 5-minute getting started guide
- `references/prompts/` - 13 production-ready prompt templates (864 lines)

## Key Features

✅ Self-contained script with PEP 723 inline dependencies
✅ Knowledge graph construction with entity/relationship extraction
✅ Multiple search methods (local, global, drift)
✅ GitHub Copilot and OpenAI LLM support
✅ Automatic prompt management
✅ Complete CLI with init, index, query, and status commands

## Usage Examples

### Initialize Project

```bash
# Create GraphRAG project structure
uv run skills/graphrag-apps/scripts/graphrag_memory.py init

# Or specify custom root
uv run skills/graphrag-apps/scripts/graphrag_memory.py init --root ./my_graphrag
```

### Index Documents

```bash
# Index from directory
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input openspec-memories

# With verbose output
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input docs/ --verbose
```

### Query Knowledge Graph

```bash
# Local search (detailed, entity-focused)
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "How to implement timer?" --method local

# Global search (high-level, community-focused)
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "What are the main patterns?" --method global

# Drift search (exploratory)
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "Explain the architecture" --method drift
```

### Check Status

```bash
# Show project status
uv run skills/graphrag-apps/scripts/graphrag_memory.py status
```

## How It Works

1. **Initialize**: Sets up project structure with settings.yaml and prompts
2. **Index**: Processes markdown files to extract entities, relationships, and communities
3. **Store**: Creates knowledge graph in LanceDB with embeddings
4. **Query**: Uses LLM to reason over graph structure for answers

## Technical Stack

- [GraphRAG](https://github.com/microsoft/graphrag) - Knowledge graph construction
- [LanceDB](https://lancedb.com/) - Vector storage
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- Only 3 direct dependencies via PEP 723

## Query Methods Comparison

| Method | Best For | Speed | Detail Level |
|--------|----------|-------|--------------|
| **Local** | Specific questions about entities | Fast | High detail |
| **Global** | Broad questions about themes | Slow | High-level overview |
| **Drift** | Exploratory analysis | Medium | Contextual exploration |

## Differences from ChromaDB-apps

GraphRAG provides more sophisticated analysis:

1. **Knowledge Graph** instead of simple vector search
2. **Entity and relationship extraction** using LLM
3. **Community detection** for hierarchical understanding
4. **Multiple query strategies** optimized for different question types
5. **Better for complex reasoning** over interconnected information

## Configuration

Edit `settings.yaml` to configure:
- LLM provider (GitHub Copilot or OpenAI)
- Embedding model
- Chunk sizes
- Community detection parameters
- Query prompts

## See Also

See SKILL.md for complete documentation with all commands and options.
