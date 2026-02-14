# LangChain Knowledge Graph - Architecture & Implementation Details

This document explains how the knowledge graph extraction works under the hood, including performance characteristics, limitations, and potential improvements.

## Table of Contents

- [How It Works](#how-it-works)
- [Performance Characteristics](#performance-characteristics)
- [LLM Triple Extraction](#llm-triple-extraction)
- [Node Deduplication](#node-deduplication)
- [Node Merging](#node-merging)
- [Graph Traversal & Query Strategies](#graph-traversal--query-strategies)
- [Limitations](#limitations)
- [Potential Improvements](#potential-improvements)

## How It Works

### High-Level Flow

```
Document → LLM Extraction → Parse Triples → Add to Graph → Save to GML
```

### Detailed Process

1. **Document Loading**
   - Read text from markdown/text files
   - No preprocessing or chunking

2. **LLM Extraction** (Single API Call)
   - Send entire document to OpenAI GPT-4o-mini
   - Use prompt with few-shot examples
   - LLM generates triples in format: `(subject, predicate, object)<|>(subject, predicate, object)`

3. **Triple Parsing**
   - Split output by delimiter `<|>` (KG_TRIPLE_DELIMITER)
   - Parse each triple into `KnowledgeTriple(subject, predicate, object_)`

4. **Graph Construction**
   - Add nodes if they don't exist (exact string match)
   - Add edges with relationship as attribute
   - NetworkX handles in-memory graph structure

5. **Persistence**
   - Save to GML (Graph Modeling Language) format
   - Can be loaded later for querying

## Performance Characteristics

### Speed Breakdown

| Operation | Time | Notes |
|-----------|------|-------|
| LLM API Call | 2-3s | Per document, depends on size |
| Triple Parsing | 0.01s | String splitting and parsing |
| Graph Operations | 0.001s | In-memory NetworkX operations |
| **Total per doc** | **~2-3s** | Dominated by LLM call |

### Why It's Fast

1. **Single LLM Call Per Document**
   - No iterative refinement
   - No multiple passes
   - Simple prompt → response → parse

2. **Lightweight Processing**
   - NetworkX operations are in-memory
   - String parsing is trivial
   - No complex algorithms

3. **No Database Overhead**
   - Everything in memory
   - Only writes to disk at the end

### Scalability

- **10-20 documents**: Excellent (~30-60 seconds)
- **50-100 documents**: Good (~2-5 minutes)
- **200+ documents**: Consider batching or Neo4j

## LLM Triple Extraction

### Prompt Template

The LLM uses a prompt with few-shot examples:

```python
_KNOWLEDGE_TRIPLE_EXTRACTION_TEMPLATE = """
You are a networked intelligence helping a human track knowledge triples
about all relevant people, things, concepts, etc. and integrating
them with your knowledge stored within your weights
as well as that stored in a knowledge graph.
Extract all of the knowledge triples from the text.
A knowledge triple is a clause that contains a subject, a predicate,
and an object. The subject is the entity being described,
the predicate is the property of the subject that is being
described, and the object is the value of the property.

EXAMPLE
It's a state in the US. It's also the number 1 producer of gold in the US.

Output: (Nevada, is a, state)<|>(Nevada, is in, US)<|>(Nevada, is the number 1 producer of, gold)
END OF EXAMPLE

EXAMPLE
I'm going to the store.

Output: NONE
END OF EXAMPLE

EXAMPLE
Oh huh. I know Descartes likes to drive antique scooters and play the mandolin.
Output: (Descartes, likes to drive, antique scooters)<|>(Descartes, plays, mandolin)
END OF EXAMPLE

EXAMPLE
{text}
Output:
"""
```

### Extraction Process

1. **LLM receives text** with few-shot examples showing the format
2. **LLM generates output** in the specified format
3. **Parser splits by delimiter** `<|>`
4. **Each triple is parsed** into structured format

### Example

**Input:**
```
Python was created by Guido van Rossum. Django is a web framework written in Python.
```

**LLM Output:**
```
(Python, was created by, Guido van Rossum)<|>(Django, is a, web framework)<|>(Django, written in, Python)
```

**Parsed Triples:**
```python
[
    KnowledgeTriple(subject="Python", predicate="was created by", object_="Guido van Rossum"),
    KnowledgeTriple(subject="Django", predicate="is a", object_="web framework"),
    KnowledgeTriple(subject="Django", predicate="written in", object_="Python")
]
```

### What the LLM Does Well

✅ Extracting clear subject-predicate-object relationships
✅ Handling simple declarative sentences
✅ Following the format from examples
✅ Identifying entities and relationships

### What the LLM Struggles With

❌ Complex technical documentation
❌ Implicit relationships
❌ Long explanatory paragraphs
❌ Conceptual descriptions without clear entities

## Node Deduplication

### How It Works

Nodes are deduplicated using **exact string matching**:

```python
def add_triple(self, knowledge_triple: KnowledgeTriple) -> None:
    """Add a triple to the graph."""
    # Creates nodes if they don't exist
    if not self._graph.has_node(knowledge_triple.subject):
        self._graph.add_node(knowledge_triple.subject)
    if not self._graph.has_node(knowledge_triple.object_):
        self._graph.add_node(knowledge_triple.object_)
    # Overwrites existing edges
    self._graph.add_edge(
        knowledge_triple.subject,
        knowledge_triple.object_,
        relation=knowledge_triple.predicate,
    )
```

### Deduplication Strategy

- **Exact string match**: Nodes are deduplicated by exact string matching
- **Case-sensitive**: "Python" ≠ "python" (creates different nodes)
- **NetworkX handles it**: `has_node()` checks existence before adding
- **Automatic**: No manual intervention needed

### Example

```python
# Triple 1: (Python, is a, programming language)
# Triple 2: (Python, was created by, Guido van Rossum)
# Result: Only ONE "Python" node with TWO outgoing edges

# Triple 3: (python, is popular, True)
# Result: SEPARATE "python" node (case-sensitive)
```

### What Gets Deduplicated

✅ Exact same string: "Python" and "Python"
✅ Multiple relationships: Same entity with different predicates

### What Doesn't Get Deduplicated

❌ Case differences: "Python" vs "python"
❌ Whitespace differences: "Python" vs "Python "
❌ Variations: "Python" vs "Python programming language"
❌ Synonyms: "USA" vs "United States"

## Node Merging

### Current Behavior

**The system does NOT merge nodes automatically!**

Nodes are only "merged" if they have **identical strings**. There is no:
- Fuzzy matching
- Entity resolution
- Semantic similarity merging
- Coreference resolution

### Problems This Causes

```python
# These create SEPARATE nodes (not merged):
"Python" vs "python"                    # Case difference
"Python" vs "Python programming language"  # Variation
"Marie Curie" vs "Curie"                # Name variation
"USA" vs "United States"                # Synonym
"Marie Curie" vs "she"                  # Coreference
```

### Why No Merging?

1. **Simple implementation** - Just string matching in NetworkX
2. **No entity resolution** - Would require additional LLM calls or NLP
3. **Performance trade-off** - Entity resolution is expensive
4. **Ambiguity** - Hard to know when to merge (e.g., "Python" the language vs "python" the snake)

### Edge Overwriting

**Important limitation**: Multiple relationships between the same nodes get overwritten:

```python
# Triple 1: (Python, created by, Guido van Rossum)
# Triple 2: (Python, maintained by, Python Software Foundation)
# Result: Only the SECOND relationship is kept!
```

This is because NetworkX's `add_edge()` overwrites existing edges between the same nodes.

## Graph Traversal & Query Strategies

### Overview

The knowledge graph uses **Depth-First Search (DFS)** traversal to explore relationships from a starting entity. This is implemented using NetworkX's `dfs_edges()` function.

### Core Traversal Method

```python
def get_entity_knowledge(self, entity: str, depth: int = 1) -> List[str]:
    """Get information about an entity."""
    import networkx as nx
    
    if not self._graph.has_node(entity):
        return []
    
    results = []
    for src, sink in nx.dfs_edges(self._graph, entity, depth_limit=depth):
        relation = self._graph[src][sink]["relation"]
        results.append(f"{src} {relation} {sink}")
    return results
```

### How DFS Traversal Works

**Depth-First Search (DFS)** explores as far as possible along each branch before backtracking.

#### Example Graph

```
Python --[created by]--> Guido van Rossum
Python --[used by]--> Django
Django --[is a]--> web framework
Django --[written in]--> Python (cycle!)
web framework --[runs on]--> server
```

#### Traversal with depth=1

Starting from "Python":
```
1. Python --[created by]--> Guido van Rossum
2. Python --[used by]--> Django
```

**Result:** Only direct neighbors (1 hop away)

#### Traversal with depth=2

Starting from "Python":
```
1. Python --[created by]--> Guido van Rossum
2. Python --[used by]--> Django
3. Django --[is a]--> web framework
4. Django --[written in]--> Python (stops - already visited)
```

**Result:** Neighbors and their neighbors (2 hops away)

### Traversal Characteristics

#### Direction

- **Outgoing edges only**: Follows edges FROM the starting entity
- **Directed graph**: Respects edge direction
- **No backtracking**: Doesn't follow edges TO the starting entity

**Example:**
```
A --[created]--> B
C --[uses]--> A

Query: get_entity_info("A", depth=1)
Result: Only "A created B" (not "C uses A")
```

#### Depth Limiting

The `depth_limit` parameter controls how many hops to traverse:

- **depth=0**: Only the starting node (no edges)
- **depth=1**: Direct neighbors (1 hop)
- **depth=2**: Neighbors of neighbors (2 hops)
- **depth=N**: Up to N hops away

#### Cycle Handling

DFS automatically handles cycles by tracking visited nodes:

```python
# Graph with cycle:
A --[relates to]--> B
B --[relates to]--> C
C --[relates to]--> A  # Cycle!

# Query: get_entity_info("A", depth=3)
# Result: Visits A, B, C but stops at A (already visited)
```

### Query Strategies

The skill provides several query strategies:

#### 1. Entity-Centric Query

**Get all relationships for a specific entity:**

```bash
uv run langchain-memory query graph.gml --entity "Python"
```

**Implementation:**
```python
def get_entity_info(entity: str, depth: int = 1) -> List[str]:
    """Get information about an entity."""
    return self.graph.get_entity_knowledge(entity, depth=depth)
```

**Use case:** "Tell me everything about Python"

#### 2. Entity Search

**Find entities matching a substring:**

```bash
uv run langchain-memory query graph.gml --search "Python"
```

**Implementation:**
```python
def search_entity(query: str) -> List[str]:
    """Search for entities matching a query."""
    entities = self.get_all_entities()
    query_lower = query.lower()
    return [e for e in entities if query_lower in e.lower()]
```

**Use case:** "Find all entities related to 'machine learning'"

#### 3. Graph Statistics

**Get overview of the entire graph:**

```bash
uv run langchain-memory query graph.gml --stats
```

**Implementation:**
```python
def get_statistics() -> Dict[str, Any]:
    """Get graph statistics."""
    triples = self.graph.get_triples()
    entities = self.get_all_entities()
    
    return {
        "total_nodes": self.graph.get_number_of_nodes(),
        "total_triples": len(triples),
        "total_entities": len(entities),
    }
```

**Use case:** "How big is my knowledge graph?"

### Traversal Performance

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| DFS Traversal | O(V + E) | O(V) |
| Entity Lookup | O(1) | O(1) |
| Entity Search | O(V) | O(V) |
| Get Statistics | O(E) | O(E) |

Where:
- V = number of vertices (nodes)
- E = number of edges (relationships)

### Traversal Examples

#### Example 1: Simple Chain

**Graph:**
```
A --[leads to]--> B --[leads to]--> C --[leads to]--> D
```

**Query:** `get_entity_info("A", depth=1)`
```
Result: ["A leads to B"]
```

**Query:** `get_entity_info("A", depth=2)`
```
Result: ["A leads to B", "B leads to C"]
```

**Query:** `get_entity_info("A", depth=3)`
```
Result: ["A leads to B", "B leads to C", "C leads to D"]
```

#### Example 2: Branching

**Graph:**
```
Python --[created by]--> Guido van Rossum
Python --[used by]--> Django
Python --[used by]--> Flask
Django --[is a]--> web framework
Flask --[is a]--> micro framework
```

**Query:** `get_entity_info("Python", depth=1)`
```
Result: [
    "Python created by Guido van Rossum",
    "Python used by Django",
    "Python used by Flask"
]
```

**Query:** `get_entity_info("Python", depth=2)`
```
Result: [
    "Python created by Guido van Rossum",
    "Python used by Django",
    "Django is a web framework",
    "Python used by Flask",
    "Flask is a micro framework"
]
```

#### Example 3: Disconnected Nodes

**Graph:**
```
A --[relates to]--> B
C --[relates to]--> D  (disconnected from A-B)
```

**Query:** `get_entity_info("A", depth=10)`
```
Result: ["A relates to B"]
# Never reaches C or D (disconnected)
```

### Advanced Query Patterns

#### Multi-Hop Reasoning

To find indirect relationships:

```python
# Find all entities within 3 hops of "Python"
info = query.get_entity_info("Python", depth=3)

# Parse to find specific patterns
for relationship in info:
    if "created by" in relationship:
        print(f"Creator relationship: {relationship}")
```

#### Path Finding

To find paths between entities:

```python
import networkx as nx

# Access internal graph
nx_graph = graph._graph

# Find shortest path
if nx.has_path(nx_graph, "Python", "web framework"):
    path = nx.shortest_path(nx_graph, "Python", "web framework")
    print(f"Path: {' -> '.join(path)}")
```

#### Subgraph Extraction

To extract a subgraph around an entity:

```python
import networkx as nx

# Get all nodes within depth=2
nodes = set()
for src, sink in nx.dfs_edges(nx_graph, "Python", depth_limit=2):
    nodes.add(src)
    nodes.add(sink)

# Create subgraph
subgraph = nx_graph.subgraph(nodes)
```

### Query Limitations

#### 1. Direction-Only Traversal

**Problem:** Only follows outgoing edges

```python
# Graph:
A --[created]--> B
C --[uses]--> A

# Query: get_entity_info("A")
# Result: Only "A created B"
# Missing: "C uses A" (incoming edge)
```

**Workaround:** Query from the other direction or traverse entire graph

#### 2. No Relationship Filtering

**Problem:** Cannot filter by relationship type during traversal

```python
# Cannot do: "Get all 'created by' relationships within 2 hops"
# Must get all relationships and filter manually
```

**Workaround:** Filter results after traversal

#### 3. No Weighted Traversal

**Problem:** All edges are treated equally

```python
# Cannot prioritize certain relationships
# Cannot use edge weights for ranking
```

**Workaround:** Use external ranking after retrieval

#### 4. No Semantic Search

**Problem:** Only exact string matching for entity search

```python
# search_entity("Python") finds "Python"
# But doesn't find "Python programming language" or "python"
```

**Workaround:** Use fuzzy matching or normalize entity names

### Comparison with Other Traversal Strategies

#### Depth-First Search (DFS) - Current

**Pros:**
- ✅ Memory efficient
- ✅ Good for deep exploration
- ✅ Finds paths quickly
- ✅ Simple implementation

**Cons:**
- ❌ May miss nearby nodes
- ❌ Order depends on edge insertion
- ❌ Not optimal for shortest paths

#### Breadth-First Search (BFS) - Alternative

**Pros:**
- ✅ Finds shortest paths
- ✅ Explores nearby nodes first
- ✅ Level-by-level exploration

**Cons:**
- ❌ More memory usage
- ❌ Slower for deep graphs
- ❌ Not implemented in current version

**Implementation:**
```python
def get_entity_info_bfs(entity: str, depth: int = 1) -> List[str]:
    """Get information using BFS."""
    import networkx as nx
    
    results = []
    for src, sink in nx.bfs_edges(self._graph, entity, depth_limit=depth):
        relation = self._graph[src][sink]["relation"]
        results.append(f"{src} {relation} {sink}")
    return results
```

#### Bidirectional Search - Alternative

**Pros:**
- ✅ Explores both directions
- ✅ Finds incoming and outgoing edges
- ✅ More complete view

**Cons:**
- ❌ More complex
- ❌ Slower
- ❌ Not implemented in current version

**Implementation:**
```python
def get_entity_info_bidirectional(entity: str, depth: int = 1) -> List[str]:
    """Get information in both directions."""
    import networkx as nx
    
    results = []
    
    # Outgoing edges (current behavior)
    for src, sink in nx.dfs_edges(self._graph, entity, depth_limit=depth):
        relation = self._graph[src][sink]["relation"]
        results.append(f"{src} --[{relation}]--> {sink}")
    
    # Incoming edges (new)
    for src, sink in nx.dfs_edges(self._graph.reverse(), entity, depth_limit=depth):
        relation = self._graph[sink][src]["relation"]
        results.append(f"{src} --[{relation}]--> {sink}")
    
    return results
```

### Query Optimization Tips

#### 1. Use Appropriate Depth

```python
# For direct relationships only
depth = 1  # Fast, focused

# For exploring neighborhood
depth = 2  # Balanced

# For deep exploration
depth = 3+  # Slow, comprehensive
```

#### 2. Filter Early

```python
# Bad: Get everything then filter
all_info = query.get_entity_info("Python", depth=3)
filtered = [r for r in all_info if "created by" in r]

# Better: Use smaller depth if possible
info = query.get_entity_info("Python", depth=1)
```

#### 3. Cache Results

```python
# Cache frequently queried entities
entity_cache = {}

def get_cached_info(entity: str, depth: int = 1) -> List[str]:
    key = f"{entity}:{depth}"
    if key not in entity_cache:
        entity_cache[key] = query.get_entity_info(entity, depth)
    return entity_cache[key]
```

#### 4. Use Statistics First

```python
# Check graph size before deep queries
stats = query.get_statistics()
if stats["total_nodes"] > 1000:
    # Use smaller depth for large graphs
    depth = 1
else:
    # Can afford deeper traversal
    depth = 3
```

### Future Query Enhancements

Potential improvements to the query system:

1. **Bidirectional traversal** - Follow edges in both directions
2. **Relationship filtering** - Filter by relationship type during traversal
3. **Weighted traversal** - Prioritize certain relationships
4. **Semantic search** - Find similar entities using embeddings
5. **Path finding** - Find paths between two entities
6. **Subgraph extraction** - Extract relevant subgraphs
7. **Aggregation queries** - Count, group, summarize relationships
8. **Cypher-like query language** - More expressive queries

## Limitations

### 1. No Entity Normalization

**Problem:**
```python
"Python" and "python" are different nodes
"Marie Curie" and "marie curie" are different nodes
```

**Impact:** Fragmented graph with duplicate entities

### 2. No Coreference Resolution

**Problem:**
```python
"Marie Curie discovered radium. She won the Nobel Prize."
# Creates nodes: "Marie Curie" and "She" (separate!)
```

**Impact:** Pronouns create separate nodes

### 3. No Semantic Merging

**Problem:**
```python
"USA", "United States", "United States of America" are all different nodes
"Python", "Python programming language" are different nodes
```

**Impact:** Semantically identical entities are fragmented

### 4. Edge Overwriting

**Problem:**
```python
# Only keeps the last relationship between two nodes
(Python, created by, Guido van Rossum)  # Lost!
(Python, maintained by, PSF)            # Kept
```

**Impact:** Loss of information when multiple relationships exist

### 5. Document Format Dependency

**Problem:**
- Works well with simple declarative sentences
- Struggles with technical documentation
- Fails with implicit relationships

**Impact:** Poor extraction quality for complex documents

### 6. No Incremental Updates

**Problem:**
- Must rebuild entire graph to add new documents
- No way to update existing graph

**Impact:** Inefficient for large, evolving knowledge bases

## Potential Improvements

### 1. Add Entity Normalization

**Simple approach:**
```python
def normalize_entity(entity: str) -> str:
    """Normalize entity names."""
    # Lowercase and title case
    entity = entity.strip().lower().title()
    # Remove extra whitespace
    entity = " ".join(entity.split())
    return entity
```

**Benefits:**
- Handles case differences
- Handles whitespace variations

**Limitations:**
- Doesn't handle synonyms
- Doesn't handle name variations

### 2. Add Entity Resolution with LLM

**Approach:**
```python
async def resolve_entities(entity1: str, entity2: str) -> bool:
    """Check if two entities are the same using LLM."""
    prompt = f"Are '{entity1}' and '{entity2}' the same entity? Answer yes or no."
    response = await llm.ainvoke(prompt)
    return response.lower().strip() == "yes"
```

**Benefits:**
- Handles synonyms
- Handles name variations
- Semantic understanding

**Limitations:**
- Expensive (additional LLM calls)
- Slower
- May have false positives

### 3. Support Multiple Relationships

**Approach:**
```python
# Store relationships as a list instead of single value
self._graph.add_edge(
    subject,
    object_,
    relations=[predicate]  # List instead of single value
)

# When adding duplicate edge, append to list
if self._graph.has_edge(subject, object_):
    self._graph[subject][object_]['relations'].append(predicate)
```

**Benefits:**
- Preserves all relationships
- No information loss

### 4. Add Coreference Resolution

**Approach:**
- Use spaCy or similar NLP library
- Resolve pronouns before extraction
- Replace "she", "he", "it" with actual entity names

**Benefits:**
- Better entity linking
- More complete graph

**Limitations:**
- Requires additional NLP processing
- May have errors

### 5. Use Advanced Frameworks

**Consider switching to:**

1. **Microsoft GraphRAG**
   - Community detection
   - Hierarchical graphs
   - Better entity resolution

2. **DataStax LazyGraphRAG**
   - Lazy evaluation
   - Incremental updates
   - Better scalability

3. **Cognee**
   - Full knowledge graph pipeline
   - Entity extraction and linking
   - Graph completion

**Trade-offs:**
- More complex setup
- Heavier dependencies
- Slower but more accurate

### 6. Add Document Preprocessing

**Approach:**
```python
def preprocess_document(text: str) -> str:
    """Preprocess document for better extraction."""
    # Extract key facts
    # Simplify complex sentences
    # Resolve coreferences
    # Normalize entity names
    return processed_text
```

**Benefits:**
- Better extraction quality
- More consistent results

**Limitations:**
- Additional processing time
- May lose nuance

## Comparison with Other Approaches

### Simple Triple Extraction (Current)

**Pros:**
- Fast (2-3s per document)
- Simple implementation
- Easy to understand
- Lightweight dependencies

**Cons:**
- No entity resolution
- No semantic merging
- Poor with complex docs
- Edge overwriting

### GraphRAG (Microsoft)

**Pros:**
- Community detection
- Hierarchical structure
- Better entity resolution
- Incremental updates

**Cons:**
- Complex setup
- Slower
- Heavy dependencies
- Requires more resources

### Cognee

**Pros:**
- Full pipeline
- Entity linking
- Graph completion
- Production-ready

**Cons:**
- Heavy framework
- Slower
- More complex
- Requires setup

### Neo4j + LangChain

**Pros:**
- Scalable
- Persistent storage
- Advanced queries
- Production-ready

**Cons:**
- Requires database
- More complex
- Heavier setup
- Slower for small graphs

## Recommendations

### Use Current Approach When:

- ✅ Documents have clear subject-predicate-object sentences
- ✅ Small to medium document sets (< 100 docs)
- ✅ Speed is important
- ✅ Simple entity names (no variations)
- ✅ Prototyping or experimentation

### Consider Improvements When:

- ⚠️ Documents have entity name variations
- ⚠️ Need to handle pronouns
- ⚠️ Multiple relationships between entities
- ⚠️ Need incremental updates

### Switch to Advanced Framework When:

- ❌ Large document sets (> 200 docs)
- ❌ Complex technical documentation
- ❌ Production deployment
- ❌ Need advanced entity resolution
- ❌ Need community detection
- ❌ Need persistent storage

## References

- [LangChain Documentation](https://python.langchain.com/)
- [NetworkX Documentation](https://networkx.org/)
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [Knowledge Graphs Explained](https://www.ontotext.com/knowledgehub/fundamentals/what-is-a-knowledge-graph/)

---

**Last Updated:** December 2024
**Version:** 1.0.0
