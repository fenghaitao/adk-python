---
name: langchain-knowledge-graph
description: Build and query knowledge graphs from documents using LangChain. Extract structured relationships with LLM-powered triple extraction, store in NetworkX graphs, and query with entity-centric traversal.
homepage: https://github.com/google/adk-python
metadata: {"clawdbot":{"emoji":"🕸️","requires":{"bins":["uv"],"env":["OPENAI_API_KEY"]}}}
---

# LangChain Knowledge Graph - Document to Knowledge Graph

Build and query knowledge graphs from documents using LangChain's LLM-powered extraction and NetworkX storage.

## Quick Start

### One-Time Setup
```bash
cd {baseDir}
uv sync
export OPENAI_API_KEY='your-api-key-here'
```

### Test Setup
```bash
uv run langchain-memory test
```

### Build and Query
```bash
# Build graph from documents
uv run langchain-memory build docs/ --output knowledge.gml

# Query entity
uv run langchain-memory query knowledge.gml --entity "Python"

# Visualize graph
uv run langchain-memory visualize knowledge.gml --output graph.png
```

## Features

✅ **LLM-powered extraction** - GPT-4o-mini extracts subject-predicate-object triples  
✅ **NetworkX storage** - Efficient graph data structure with persistence  
✅ **Entity-centric queries** - Depth-first traversal for relationship discovery  
✅ **Graph visualization** - Matplotlib rendering with customizable layouts  
✅ **Managed dependencies** - uv with pyproject.toml  
✅ **Multiple formats** - Supports markdown, text, and more

## Commands

### Test Setup
```bash
uv run langchain-memory test
```
Validates dependencies and checks for OPENAI_API_KEY.

### Build Knowledge Graph
```bash
# From directory
uv run langchain-memory build docs/ --output knowledge.gml

# From single file
uv run langchain-memory build article.md --output article.gml

# Custom model
uv run langchain-memory build docs/ --model gpt-4 --output knowledge.gml

# Custom file extensions
uv run langchain-memory build docs/ --extensions .md,.rst,.txt
```

**Options:**
- `--output, -o`: Output graph file (default: knowledge_graph.gml)
- `--model`: OpenAI model (default: gpt-4o-mini)
- `--temperature`: LLM temperature (default: 0.0)
- `--extensions`: File extensions to process (default: .md,.txt)

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

**Options:**
- `--entity, -e`: Entity to query
- `--search, -s`: Search for entities (substring match)
- `--stats`: Show graph statistics
- `--depth, -d`: Traversal depth (default: 1)

### Visualize Graph
```bash
# Basic visualization
uv run langchain-memory visualize knowledge.gml --output graph.png

# Custom size
uv run langchain-memory visualize knowledge.gml --output graph.png --figsize 16,10
```

**Options:**
- `--output, -o`: Output image file (default: knowledge_graph.png)
- `--figsize`: Figure size as width,height (default: 12,8)

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY='your-api-key-here'

# Optional
export OPENAI_MODEL='gpt-4o-mini'  # Default model
```

### Default Settings

- **Model**: gpt-4o-mini (fast and cost-effective)
- **Temperature**: 0.0 (deterministic extraction)
- **File Extensions**: .md, .txt
- **Graph Format**: GML (Graph Modeling Language)
- **Visualization**: Spring layout with matplotlib

## Knowledge Triple Format

The LLM extracts triples in the format:

```
(Subject, Predicate, Object)
```

**Examples:**
- `(Marie Curie, was a, physicist)`
- `(Marie Curie, won, Nobel Prize in Physics)`
- `(Python, created by, Guido van Rossum)`
- `(Django, written in, Python)`

## Graph Structure

**Nodes:** Entities (subjects and objects)
**Edges:** Relationships (predicates as edge attributes)
**Format:** Directed graph where `subject --[predicate]--> object`

**Example:**
```
Marie Curie --[was a]--> physicist
Marie Curie --[won]--> Nobel Prize in Physics
Marie Curie --[discovered]--> Polonium
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Extraction | 2-5s/doc | Depends on document size |
| Building | 10-30s | For 10 documents |
| Query | <100ms | Entity lookup |
| Visualization | 1-2s | For <100 nodes |
| Memory | ~50MB | Typical graph |

**Scalability:**
- 10-20 documents: Excellent
- 50-100 documents: Good
- 200+ documents: Consider batching or Neo4j

## Examples

### Build from Research Papers
```bash
# Extract knowledge from papers
uv run langchain-memory build research_papers/ --output research.gml

# Query specific researcher
uv run langchain-memory query research.gml --entity "Albert Einstein"

# Find related concepts
uv run langchain-memory query research.gml --search "relativity"
```

### Build from Technical Documentation
```bash
# Build from API docs
uv run langchain-memory build api_docs/ --output api_graph.gml

# Query API relationships
uv run langchain-memory query api_graph.gml --entity "REST API" --depth 2

# Visualize architecture
uv run langchain-memory visualize api_graph.gml --output api_architecture.png
```

### Build from Company Knowledge Base
```bash
# Index company docs
uv run langchain-memory build company_docs/ --output company_kg.gml

# Show statistics
uv run langchain-memory query company_kg.gml --stats

# Search for products
uv run langchain-memory query company_kg.gml --search "product"
```

## Troubleshooting

### Check Setup
```bash
uv run langchain-memory test
```

### Common Issues

**OPENAI_API_KEY not set**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**No triples extracted**
- Check document has clear subject-predicate-object relationships
- Try more explicit text: "X is a Y" rather than implicit relationships
- Increase temperature slightly: `--temperature 0.1`

**Graph file not found**
```bash
# Check file exists
ls -la knowledge.gml

# Rebuild if needed
uv run langchain-memory build docs/ --output knowledge.gml
```

**Entity not found**
```bash
# Search for similar entities
uv run langchain-memory query knowledge.gml --search "partial_name"

# Show all entities
uv run langchain-memory query knowledge.gml --stats
```

**Visualization fails**
```bash
# Ensure matplotlib is installed (auto-installed with uv sync)
# If issues persist, check graph size:
uv run langchain-memory query knowledge.gml --stats
```

## Document Format

Supports any text-based format:

**Markdown:**
```markdown
# Marie Curie

Marie Curie was a physicist and chemist. She won the Nobel Prize in Physics in 1903.
```

**Plain Text:**
```
Python is a programming language created by Guido van Rossum.
Django is a web framework written in Python.
```

**Best Practices:**
- Use clear subject-verb-object sentences
- Avoid ambiguous pronouns
- Include explicit relationships
- Break complex sentences into simpler ones

## Technical Details

**Built with:**
- [LangChain](https://python.langchain.com/) - LLM orchestration
- [LangChain Community](https://python.langchain.com/docs/integrations/graphs/) - Graph integrations
- [NetworkX](https://networkx.org/) - Graph data structure
- [Matplotlib](https://matplotlib.org/) - Visualization
- [OpenAI](https://openai.com/) - GPT models

**Architecture:**
1. **Extractor** - LLM analyzes text and extracts triples
2. **Builder** - Constructs NetworkX directed graph
3. **Storage** - Persists graph in GML format
4. **Query** - Entity-centric queries with DFS traversal
5. **Visualizer** - Spring layout rendering

**Dependencies:**
- 5 direct dependencies (langchain, langchain-community, langchain-openai, networkx, matplotlib)
- ~30 total packages
- Managed with uv and pyproject.toml

## Advanced Usage

### Python API

```python
from langchain_knowledge_graph import KnowledgeGraphBuilder, KnowledgeGraphQuery

# Build graph
builder = KnowledgeGraphBuilder(model="gpt-4o-mini")
graph = builder.build_from_directory("docs/")

# Save
graph.write_to_gml("knowledge.gml")

# Query
query = KnowledgeGraphQuery(graph)
info = query.get_entity_info("Python", depth=2)
for relationship in info:
    print(relationship)
```

### Integration with ADK Agents

```python
# In your agent.py
import subprocess
from pathlib import Path

def query_knowledge_graph(entity: str) -> str:
    """Query knowledge graph for entity information."""
    skill_dir = Path("skills/langchain-apps")
    result = subprocess.run(
        ["uv", "run", "langchain-memory", "query", "knowledge.gml", "--entity", entity],
        capture_output=True,
        text=True,
        cwd=skill_dir
    )
    return result.stdout
```

## Comparison with Other Skills

### vs chromadb-apps
- **chromadb-apps**: Vector search, semantic similarity
- **langchain-apps**: Structured relationships, graph traversal

### vs graphrag-apps
- **graphrag-apps**: Large-scale RAG with graph structure
- **langchain-apps**: Lightweight knowledge extraction

### vs lightrag-apps
- **lightrag-apps**: Multi-mode retrieval (local/global/hybrid)
- **langchain-apps**: Simple triple extraction and storage

## Use Cases

1. **Research Analysis** - Extract relationships from papers
2. **Documentation Understanding** - Build concept maps from docs
3. **Knowledge Base Construction** - Create company knowledge graphs
4. **Relationship Discovery** - Find connections between entities
5. **Concept Mapping** - Visualize domain knowledge

## References

See `references/` directory for additional documentation:
- LangChain configuration and tuning
- NetworkX graph operations
- OpenAI API best practices

## See Also

- [LangChain Documentation](https://python.langchain.com/)
- [NetworkX Documentation](https://networkx.org/)
- [Knowledge Graphs Explained](https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/)
