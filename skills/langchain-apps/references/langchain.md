# LangChain Configuration Reference

This document provides configuration guidance for the LangChain Knowledge Graph skill.

## Environment Variables

### Required

```bash
# OpenAI API Key (required for LLM-based extraction)
export OPENAI_API_KEY='your-api-key-here'
```

### Optional

```bash
# Default model to use
export OPENAI_MODEL='gpt-4o-mini'

# API base URL (for custom endpoints)
export OPENAI_API_BASE='https://api.openai.com/v1'

# Organization ID (if using organization)
export OPENAI_ORG_ID='org-xxxxx'
```

## Model Selection

### Recommended Models

**For Production:**
- `gpt-4o-mini` - Fast, cost-effective, good quality (default)
- `gpt-4o` - Higher quality, more expensive
- `gpt-4-turbo` - Balance of speed and quality

**For Development/Testing:**
- `gpt-3.5-turbo` - Fastest, cheapest, lower quality

### Model Comparison

| Model | Speed | Cost | Quality | Best For |
|-------|-------|------|---------|----------|
| gpt-4o-mini | Fast | Low | Good | Production, high volume |
| gpt-4o | Medium | High | Excellent | Complex documents |
| gpt-4-turbo | Fast | Medium | Very Good | Balance |
| gpt-3.5-turbo | Very Fast | Very Low | Fair | Testing |

### Usage

```bash
# Use specific model
uv run scripts/langchain_knowledge_graph.py build docs/ --model gpt-4o --output knowledge.gml

# Use environment variable
export OPENAI_MODEL='gpt-4o'
uv run scripts/langchain_knowledge_graph.py build docs/ --output knowledge.gml
```

## Temperature Settings

Temperature controls randomness in extraction:

- `0.0` - Deterministic, consistent (default, recommended)
- `0.1-0.3` - Slightly creative, good for varied text
- `0.5+` - More creative, may hallucinate

```bash
# Deterministic extraction
uv run scripts/langchain_knowledge_graph.py build docs/ --temperature 0.0

# Slightly creative
uv run scripts/langchain_knowledge_graph.py build docs/ --temperature 0.2
```

## Graph Storage

### GML Format

The skill uses GML (Graph Modeling Language) for persistence:

**Advantages:**
- Human-readable text format
- Preserves graph structure and attributes
- Compatible with NetworkX and other tools
- Version control friendly

**Example GML:**
```gml
graph [
  directed 1
  node [
    id 0
    label "Python"
  ]
  node [
    id 1
    label "Guido van Rossum"
  ]
  edge [
    source 0
    target 1
    relation "created by"
  ]
]
```

### Alternative Formats

For integration with other tools:

```python
# Load graph
from langchain_community.graphs import NetworkxEntityGraph
graph = NetworkxEntityGraph.from_gml("knowledge.gml")

# Export to other formats
import networkx as nx
nx_graph = graph._graph

# GraphML
nx.write_graphml(nx_graph, "knowledge.graphml")

# JSON
import json
data = nx.node_link_data(nx_graph)
with open("knowledge.json", "w") as f:
    json.dump(data, f)

# Pickle (for Python only)
import pickle
with open("knowledge.pkl", "wb") as f:
    pickle.dump(graph, f)
```

## Performance Tuning

### Extraction Speed

**Factors affecting speed:**
1. Document size
2. Model selection
3. API rate limits
4. Network latency

**Optimization tips:**
```bash
# Use faster model
--model gpt-4o-mini

# Process smaller batches
# Split large directories into batches

# Use parallel processing (custom script)
# Process multiple documents concurrently
```

### Memory Usage

**Typical memory usage:**
- Small graphs (<100 nodes): ~10-20MB
- Medium graphs (100-1000 nodes): ~50-100MB
- Large graphs (1000+ nodes): ~200MB+

**For large graphs:**
- Consider using Neo4j instead of NetworkX
- Process documents in batches
- Use graph databases for production

## Document Processing

### Supported Formats

**Default:**
- `.md` - Markdown
- `.txt` - Plain text

**Custom extensions:**
```bash
uv run scripts/langchain_knowledge_graph.py build docs/ --extensions .md,.rst,.txt,.adoc
```

### Document Preprocessing

**Best practices:**

1. **Clean text:**
   - Remove excessive whitespace
   - Fix encoding issues
   - Remove special characters

2. **Structure:**
   - Use clear headings
   - Break into paragraphs
   - Use explicit relationships

3. **Content:**
   - Write in subject-verb-object format
   - Avoid ambiguous pronouns
   - Include entity names explicitly

**Example preprocessing script:**
```python
import re
from pathlib import Path

def preprocess_document(text: str) -> str:
    """Preprocess document for better extraction."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n')
    
    return text.strip()

# Use it
doc = Path("document.md").read_text()
clean_doc = preprocess_document(doc)
Path("document_clean.md").write_text(clean_doc)
```

## Query Optimization

### Depth Traversal

Depth controls how far to traverse relationships:

```bash
# Depth 1: Direct relationships only
uv run scripts/langchain_knowledge_graph.py query knowledge.gml --entity "Python" --depth 1

# Depth 2: Relationships of relationships
uv run scripts/langchain_knowledge_graph.py query knowledge.gml --entity "Python" --depth 2

# Depth 3+: Deeper traversal (may be slow)
uv run scripts/langchain_knowledge_graph.py query knowledge.gml --entity "Python" --depth 3
```

**Performance:**
- Depth 1: <10ms
- Depth 2: <50ms
- Depth 3: <200ms
- Depth 4+: May be slow for large graphs

### Search Optimization

```bash
# Case-insensitive substring search
uv run scripts/langchain_knowledge_graph.py query knowledge.gml --search "python"

# Exact match (use entity query)
uv run scripts/langchain_knowledge_graph.py query knowledge.gml --entity "Python"
```

## Visualization

### Layout Algorithms

The skill uses spring layout by default. For custom layouts:

```python
import matplotlib.pyplot as plt
import networkx as nx
from langchain_community.graphs import NetworkxEntityGraph

graph = NetworkxEntityGraph.from_gml("knowledge.gml")
nx_graph = graph._graph

# Different layouts
layouts = {
    'spring': nx.spring_layout(nx_graph),
    'circular': nx.circular_layout(nx_graph),
    'kamada_kawai': nx.kamada_kawai_layout(nx_graph),
    'shell': nx.shell_layout(nx_graph),
}

# Use preferred layout
pos = layouts['kamada_kawai']
nx.draw(nx_graph, pos, with_labels=True)
plt.savefig("graph_custom.png")
```

### Styling

```python
# Custom colors and sizes
nx.draw_networkx_nodes(
    nx_graph, pos,
    node_color='lightgreen',
    node_size=2000,
    alpha=0.8
)

nx.draw_networkx_edges(
    nx_graph, pos,
    edge_color='blue',
    arrows=True,
    arrowsize=15,
    width=1.5
)
```

## Error Handling

### Common Errors

**1. API Key Not Set**
```
ValueError: OPENAI_API_KEY environment variable not set
```
**Solution:**
```bash
export OPENAI_API_KEY='your-key-here'
```

**2. Rate Limit Exceeded**
```
openai.error.RateLimitError: Rate limit exceeded
```
**Solution:**
- Wait and retry
- Use slower model
- Implement exponential backoff

**3. No Triples Extracted**
```
⚠ Extracted 0 triples
```
**Solution:**
- Check document format
- Use more explicit text
- Increase temperature slightly

**4. Graph File Not Found**
```
FileNotFoundError: knowledge.gml
```
**Solution:**
```bash
# Rebuild graph
uv run scripts/langchain_knowledge_graph.py build docs/ --output knowledge.gml
```

## Integration Patterns

### With ADK Agents

```python
# In your agent.py
import subprocess
from typing import List, Dict

class KnowledgeGraphTool:
    """Tool for querying knowledge graph."""
    
    def __init__(self, graph_path: str = "knowledge.gml"):
        self.graph_path = graph_path
    
    def query_entity(self, entity: str, depth: int = 1) -> str:
        """Query entity information."""
        result = subprocess.run(
            [
                "uv", "run",
                "skills/langchain-apps/scripts/langchain_knowledge_graph.py",
                "query", self.graph_path,
                "--entity", entity,
                "--depth", str(depth)
            ],
            capture_output=True,
            text=True
        )
        return result.stdout
    
    def search_entities(self, query: str) -> str:
        """Search for entities."""
        result = subprocess.run(
            [
                "uv", "run",
                "skills/langchain-apps/scripts/langchain_knowledge_graph.py",
                "query", self.graph_path,
                "--search", query
            ],
            capture_output=True,
            text=True
        )
        return result.stdout

# Use in agent
kg_tool = KnowledgeGraphTool()
info = kg_tool.query_entity("Python", depth=2)
```

### With Python Scripts

```python
# Direct Python API usage
from langchain_community.graphs import NetworkxEntityGraph
from langchain_community.graphs.index_creator import GraphIndexCreator
from langchain_openai import ChatOpenAI

# Build graph
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
creator = GraphIndexCreator(llm=llm)

text = "Your document text here..."
graph = creator.from_text(text)

# Query
info = graph.get_entity_knowledge("Entity Name", depth=2)
for relationship in info:
    print(relationship)

# Save
graph.write_to_gml("knowledge.gml")
```

## Best Practices

### 1. Document Preparation
- Use clear, explicit language
- Include entity names in full
- Avoid ambiguous references
- Structure with headings

### 2. Model Selection
- Use gpt-4o-mini for production
- Use gpt-4o for complex documents
- Keep temperature at 0.0 for consistency

### 3. Graph Management
- Save graphs with descriptive names
- Version control GML files
- Backup before rebuilding
- Use statistics to monitor growth

### 4. Query Patterns
- Start with depth 1
- Use search for discovery
- Use entity queries for details
- Check statistics regularly

### 5. Performance
- Process documents in batches
- Use faster models when possible
- Monitor API usage and costs
- Cache results when appropriate

## Troubleshooting

### Debug Mode

Add verbose output:

```python
# In the script, add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validate Extraction

```bash
# Build and immediately query
uv run scripts/langchain_knowledge_graph.py build sample.md --output test.gml
uv run scripts/langchain_knowledge_graph.py query test.gml --stats
```

### Check Graph Structure

```python
from langchain_community.graphs import NetworkxEntityGraph
import networkx as nx

graph = NetworkxEntityGraph.from_gml("knowledge.gml")
nx_graph = graph._graph

# Check connectivity
print(f"Connected: {nx.is_connected(nx_graph.to_undirected())}")

# Check for isolated nodes
isolated = list(nx.isolates(nx_graph))
print(f"Isolated nodes: {isolated}")

# Check degree distribution
degrees = dict(nx_graph.degree())
print(f"Average degree: {sum(degrees.values()) / len(degrees)}")
```

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [NetworkX Documentation](https://networkx.org/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Knowledge Graphs Guide](https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/)
