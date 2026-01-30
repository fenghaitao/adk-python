# Understanding LightRAG: A Comprehensive Guide

## What is LightRAG?

LightRAG (Light Retrieval-Augmented Generation) is a **knowledge graph-based RAG system** that goes beyond traditional vector-similarity RAG by understanding relationships between entities in your documents.

### Traditional RAG vs LightRAG

**Traditional RAG:**
```
Document → Split into chunks → Generate embeddings → Store in vector DB
Query → Generate embedding → Find similar chunks → Pass to LLM
```

**LightRAG:**
```
Document → Split into chunks → Extract entities & relationships → Build knowledge graph
Query → Traverse graph + vector similarity → Get connected context → Pass to LLM
```

## Core Concepts

### 1. Knowledge Graph Construction

When you insert a document, LightRAG:

1. **Chunks the document** into manageable pieces (default: 1200 tokens)
2. **Extracts entities** using LLM (people, places, organizations, concepts, etc.)
3. **Identifies relationships** between entities (e.g., "John works_at Google")
4. **Builds a graph** where:
   - **Nodes** = Entities (with descriptions)
   - **Edges** = Relationships (with descriptions)
5. **Creates embeddings** for entities, relationships, and chunks

### 2. Four Search Modes

LightRAG offers different retrieval strategies:

#### **Naive Mode** 🔹
- Simple vector similarity search (like traditional RAG)
- Finds chunks with embeddings similar to the query
- **Fast but limited** - doesn't use graph structure
- Use for: Simple factual lookups

#### **Local Mode** 🔶
- Finds entities matching the query
- Retrieves **immediate neighbors** in the graph
- Gets chunks associated with these entities
- Use for: Questions about specific entities and their direct relationships

#### **Global Mode** 🔷
- Uses the **entire graph structure**
- Considers global patterns and communities
- Generates summaries of entity clusters
- Use for: High-level questions, themes, patterns across documents

#### **Hybrid Mode** ⭐ (Recommended)
- **Combines local + global** approaches
- Best of both worlds
- Use for: Most queries, especially complex ones

### 3. Storage Architecture

LightRAG uses multiple storage backends:

```
┌─────────────────────────────────────────────────────────────┐
│                      LightRAG Storage                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │   Key-Value      │  │   Vector Store   │                │
│  │   Storage        │  │                  │                │
│  │  (JSON/Redis)    │  │  (NanoDB/Milvus) │                │
│  ├──────────────────┤  ├──────────────────┤                │
│  │ • Full docs      │  │ • Entity vectors │                │
│  │ • Text chunks    │  │ • Relation vecs  │                │
│  │ • Entities       │  │ • Chunk vectors  │                │
│  │ • Relations      │  │                  │                │
│  │ • LLM cache      │  └──────────────────┘                │
│  └──────────────────┘                                        │
│                                                               │
│  ┌──────────────────────────────────────────────┐           │
│  │         Graph Storage                         │           │
│  │      (NetworkX/Neo4j/MongoDB)                │           │
│  ├──────────────────────────────────────────────┤           │
│  │  • Entity nodes with properties              │           │
│  │  • Relationship edges with types             │           │
│  │  • Graph traversal and queries               │           │
│  └──────────────────────────────────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## How LightRAG Works: Step-by-Step

### Insertion Process

```python
rag.insert("Your document text here...")
```

**What happens:**

1. **Text Chunking**
   ```
   Document (10,000 tokens)
        ↓
   [Chunk 1: 1200 tokens]
   [Chunk 2: 1200 tokens]
   [Chunk 3: 1200 tokens]
   ...
   (with 100 token overlap between chunks)
   ```

2. **Entity Extraction** (using LLM)
   ```
   Chunk 1: "John Smith works at Google in Mountain View..."
        ↓
   Entities:
   - John Smith (PERSON) - "Software engineer at Google"
   - Google (ORGANIZATION) - "Technology company"
   - Mountain View (LOCATION) - "City in California"
   
   Relations:
   - John Smith --[works_at]--> Google
   - Google --[located_in]--> Mountain View
   ```

3. **Graph Building**
   ```
   (John Smith) --[works_at]--> (Google) --[located_in]--> (Mountain View)
   ```

4. **Embedding Generation**
   - Entity embeddings: "John Smith: Software engineer at Google"
   - Relation embeddings: "John Smith works at Google"
   - Chunk embeddings: Original text chunks

5. **Storage**
   - Graph: Nodes and edges
   - Vector DB: All embeddings
   - KV Store: Original text, metadata

### Query Process

```python
result = rag.query("What does John Smith do?", mode="hybrid")
```

**What happens:**

1. **Query Understanding**
   - Generate embedding for query
   - Identify potential entities: "John Smith"

2. **Local Retrieval** (from local mode)
   - Find "John Smith" node in graph
   - Get immediate neighbors: Google, Mountain View
   - Get relationships: works_at, located_in
   - Retrieve associated chunks

3. **Global Retrieval** (from global mode)
   - Analyze graph communities
   - Find related entity clusters
   - Generate high-level summaries

4. **Context Assembly**
   ```
   Context = {
     Entities: [John Smith, Google, Mountain View],
     Relations: [works_at, located_in],
     Chunks: [relevant text chunks],
     Global Summary: [community insights]
   }
   ```

5. **LLM Generation**
   ```
   System: "Use this context to answer..."
   Context: [assembled from step 4]
   Query: "What does John Smith do?"
        ↓
   LLM generates answer using graph context
   ```

## Key Components

### 1. LightRAG Class

The main class that orchestrates everything:

```python
from lightrag import LightRAG

rag = LightRAG(
    working_dir="./storage",           # Where to store data
    llm_model_func=your_llm_func,      # LLM for extraction & generation
    embedding_func=your_embed_func,    # Embedding model
    llm_model_name="gpt-4o-mini",     # Model name
    
    # Chunking parameters
    chunk_token_size=1200,             # Max tokens per chunk
    chunk_overlap_token_size=100,      # Overlap between chunks
    
    # Retrieval parameters
    top_k=60,                          # Entities/relations to retrieve
    max_entity_tokens=8000,            # Max entity tokens in context
    max_relation_tokens=8000,          # Max relation tokens in context
)
```

### 2. Storage Backends

LightRAG is flexible with storage:

**Key-Value Storage:**
- `JsonKVStorage` (default) - Local JSON files
- `RedisKVStorage` - Redis for distributed systems

**Vector Storage:**
- `NanoVectorDBStorage` (default) - Local lightweight vector DB
- `MilvusStorage` - Scalable vector database
- `QdrantStorage` - Alternative vector DB

**Graph Storage:**
- `NetworkXStorage` (default) - In-memory Python graph
- `Neo4jStorage` - Production graph database
- `MongoDBStorage` - Document-based graph storage

### 3. Query Parameters

Fine-tune your queries:

```python
from lightrag import QueryParam

result = rag.query(
    "Your question?",
    param=QueryParam(
        mode="hybrid",                 # Search mode
        only_need_context=False,       # Return just context, no LLM answer
        top_k=10,                      # Override default top_k
        max_token_for_text_unit=4000,  # Max chunk tokens
        max_token_for_local_context=4000,  # Max local context
        max_token_for_global_context=4000, # Max global context
    )
)
```

## Practical Example

### Scenario: Company Knowledge Base

```python
import sys
sys.path.insert(0, 'lightrag')

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

# Initialize
rag = LightRAG(
    working_dir="./company_kb",
    llm_model_func=gpt_4o_mini_complete,
    embedding_func=openai_embed,
)
await rag.initialize_storages()

# Insert company documents
docs = [
    "Alice Johnson is the CEO of TechCorp. She founded the company in 2015.",
    "TechCorp develops AI software. Their main product is SmartAssist.",
    "Bob Williams leads the engineering team at TechCorp. He reports to Alice.",
    "SmartAssist uses machine learning for customer support automation.",
]

for doc in docs:
    await rag.ainsert(doc)

# Query examples
queries = [
    "Who is the CEO of TechCorp?",           # Naive/Local: Direct entity lookup
    "What does TechCorp do?",                # Local: Company + products
    "What is the company structure?",        # Global: High-level overview
    "How does SmartAssist work?",            # Hybrid: Product + tech details
]

for query in queries:
    result = await rag.aquery(query, param=QueryParam(mode="hybrid"))
    print(f"Q: {query}")
    print(f"A: {result}\n")
```

### Expected Knowledge Graph

```
    (Alice Johnson)
         |
         | founded
         ↓
     (TechCorp) ----develops----> (SmartAssist)
         ↑                             |
         | works_at                    | uses
         |                             ↓
    (Bob Williams)              (Machine Learning)
         |
         | leads
         ↓
  (Engineering Team)
```

## Advanced Features

### 1. Custom Entity Types

```python
rag = LightRAG(
    addon_params={
        "entity_types": ["person", "company", "product", "technology"],
        "language": "English",
    }
)
```

### 2. Document Tracking

```python
# Insert with IDs and file paths
await rag.ainsert(
    text,
    ids="doc_001",
    file_paths="/path/to/file.pdf"
)

# Check document status
status = await rag.doc_status.get_by_id("doc_001")
```

### 3. Incremental Updates

```python
# Add more documents - graph grows incrementally
await rag.ainsert(new_document)

# Existing entities are merged
# New relationships are added
```

### 4. Graph Visualization

```python
# Get knowledge graph for an entity
kg = await rag.get_knowledge_graph(
    node_label="TechCorp",
    max_depth=2,
    max_nodes=50
)

# Export for visualization
print(kg.nodes)  # List of entity nodes
print(kg.edges)  # List of relationships
```

## Performance Considerations

### Token Usage

LightRAG makes multiple LLM calls:
- **Entity extraction** (1-3 calls per chunk)
- **Relationship extraction** (1-3 calls per chunk)
- **Query generation** (1 call per query)

**Cost optimization:**
- Use `gpt-4o-mini` for extraction (cheaper)
- Enable caching: `enable_llm_cache=True`
- Tune `entity_extract_max_gleaning` (default: 1)

### Processing Speed

For a 10-page document:
- Chunking: < 1 second
- Entity extraction: 10-30 seconds (depends on LLM speed)
- Embedding generation: 2-5 seconds
- Total: ~15-40 seconds

**Speed optimization:**
- Increase `llm_model_max_async` for parallel LLM calls
- Increase `embedding_func_max_async` for parallel embeddings
- Use faster LLM models

### Storage Size

For 100 documents (1MB text):
- Vector DB: ~50-100MB (embeddings)
- Graph: ~10-20MB (entities + relations)
- KV Storage: ~5-10MB (text + metadata)
- Total: ~65-130MB

## Common Patterns

### Pattern 1: Document Analysis

```python
# Insert all documents
for doc in documents:
    await rag.ainsert(doc)

# Ask analytical questions
await rag.aquery("What are the main themes?", mode="global")
await rag.aquery("What are the key entities?", mode="global")
```

### Pattern 2: Multi-Document QA

```python
# Each document represents a different source
await rag.ainsert(doc1, ids="source1")
await rag.ainsert(doc2, ids="source2")

# Query across sources
await rag.aquery("Compare the approaches in source1 vs source2", mode="hybrid")
```

### Pattern 3: Knowledge Base

```python
# Build comprehensive knowledge base
await rag.ainsert(company_docs)
await rag.ainsert(product_docs)
await rag.ainsert(support_docs)

# Query for support
await rag.aquery("How do I configure the API?", mode="hybrid")
```

## Comparison with Other Systems

| Feature | Traditional RAG | LightRAG | GraphRAG (Microsoft) |
|---------|----------------|----------|----------------------|
| **Retrieval** | Vector similarity | Vector + Graph | Graph-based |
| **Relationships** | ❌ None | ✅ Explicit | ✅ Explicit |
| **Search Modes** | 1 (similarity) | 4 (naive/local/global/hybrid) | 2-3 modes |
| **Setup Complexity** | Low | Medium | High |
| **Query Speed** | Fast | Medium | Slower |
| **Context Quality** | Good | Better | Best |
| **Cost** | Low | Medium | Higher |

## When to Use LightRAG

### ✅ Good Use Cases:
- Multi-document question answering
- Knowledge base with complex relationships
- Research paper analysis
- Company documentation
- Legal document analysis
- Scientific literature review

### ❌ Less Ideal:
- Simple keyword search (use traditional search)
- Real-time chat (high latency for insertion)
- Frequently changing documents (rebuild cost)
- Very large corpora (>10,000 documents without optimization)

## Tips & Best Practices

1. **Start with Hybrid Mode** - It works well for most queries

2. **Use Descriptive Text** - Better descriptions = better graph

3. **Enable Caching** - Saves costs on repeated queries
   ```python
   enable_llm_cache=True
   ```

4. **Monitor Token Usage** - Track costs during development

5. **Tune Chunk Size** - Larger chunks = fewer LLM calls but less granular

6. **Test Different Modes** - Some queries work better with specific modes

7. **Use Async Methods** - `ainsert()` and `aquery()` for better performance

8. **Persist Storage** - Keep `working_dir` for incremental updates

## Next Steps

1. **Try the examples**: `./run_lightrag_examples.sh`
2. **Read the code**: Explore `lightrag/lightrag/lightrag.py`
3. **Experiment**: Test with your own documents
4. **Integrate**: Use with ADK agents (see `lightrag_adk_example.py`)
5. **Scale up**: Try Neo4j or Milvus for production

---

**Questions?** Check:
- Official docs: `lightrag/README.md`
- Examples: `lightrag/examples/`
- Integration guide: `lightrag_integration.md`
