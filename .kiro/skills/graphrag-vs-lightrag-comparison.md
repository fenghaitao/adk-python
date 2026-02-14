# GraphRAG vs LightRAG: Knowledge Graph Implementation Comparison

**Date**: February 4, 2026  
**Purpose**: Comparative analysis of two knowledge graph implementations for document retrieval and analysis

---

## Executive Summary

Both **GraphRAG** and **LightRAG** are knowledge graph-based retrieval systems that go beyond simple vector search (like ChromaDB) by extracting entities, relationships, and semantic structures from documents. They differ significantly in their architecture, use cases, and implementation complexity.

### Quick Comparison

| Aspect | GraphRAG | LightRAG |
|--------|----------|----------|
| **Origin** | Microsoft Research | HKU Research (lightrag-hku) |
| **Primary Use Case** | Document analysis & Q&A | Wiki generation & documentation |
| **Implementation** | 718 lines | 832 lines |
| **Dependencies** | 3 direct (simple) | 11 direct (complex) |
| **Query Modes** | 3 modes (local, global, drift) | 5 modes (local, global, mix, hybrid, naive) |
| **Prompts** | 13 files, 864 lines | Built-in to LightRAG library |
| **Storage** | LanceDB (vector store) | nano-vectordb + NetworkX |
| **Async Support** | No (threaded) | Yes (native async/await) |
| **Python Version** | ≥3.10, <3.13 | ≥3.12 |

---

## 1. Architecture & Design Philosophy

### GraphRAG (Microsoft)

**Philosophy**: Structured, enterprise-grade knowledge graph construction with emphasis on community detection and hierarchical understanding.

**Architecture**:
```
Input Documents (Markdown)
    ↓
Chunking (1500 chars, 150 overlap)
    ↓
Entity & Relationship Extraction (LLM)
    ↓
Community Detection (clustering)
    ↓
Community Reports (summaries)
    ↓
LanceDB Storage (vectors + graph)
    ↓
Multi-mode Query (local/global/drift)
```

**Key Components**:
- **13 Production Prompts** (864 lines total):
  - Entity extraction
  - Relationship extraction
  - Community report generation (text & graph)
  - Multiple search system prompts
  - Claim extraction
  - Description summarization
- **LanceDB**: Vector database for efficient retrieval
- **Threaded Async**: Uses `async_mode: threaded` for concurrency
- **Configuration-driven**: Extensive YAML configuration (130+ lines)

### LightRAG (HKU)

**Philosophy**: Lightweight, fast, and flexible knowledge graph with emphasis on practical wiki generation and documentation.

**Architecture**:
```
Code Repository
    ↓
File Scanning (.py, .md, .txt)
    ↓
LightRAG Indexing (entities + relationships)
    ↓
NetworkX Graph + nano-vectordb
    ↓
Multi-mode Query (5 modes)
    ↓
Wiki Generation (hierarchical)
```

**Key Components**:
- **Native Async**: Built with `async/await` from ground up
- **NetworkX**: For graph operations and traversal
- **nano-vectordb**: Lightweight vector storage
- **LlamaIndex Integration**: For LLM abstraction via LiteLLM
- **Wiki Generator**: Automated hierarchical documentation generation
- **Optimized Parallelism**: 48/96/48 concurrent operations

---

## 2. Technical Implementation

### Dependencies

**GraphRAG** (3 direct dependencies):
```python
dependencies = [
    "graphrag @ git+https://github.com/fenghaitao/graphrag.git",
    "pyyaml>=6.0.0",
    "typer>=0.16.0",
]
```
- Uses forked GraphRAG (not PyPI package)
- Minimal external dependencies
- ~50 total packages when installed

**LightRAG** (11 direct dependencies):
```python
dependencies = [
    "lightrag-hku>=1.4.9,<2.0.0",
    "openai>=1.0.0",
    "tiktoken>=0.5.0",
    "numpy>=1.24.0",
    "networkx>=3.0.0",
    "nano-vectordb>=0.0.4",
    "python-dotenv>=1.0.0",
    "llama-index-core>=0.10.0",
    "llama-index-llms-litellm>=0.1.0",
    "llama-index-embeddings-litellm>=0.1.0",
    "litellm @ git+https://github.com/fenghaitao/litellm.git"
]
```
- More complex dependency tree
- Requires Python 3.12+
- Uses forked LiteLLM for GitHub Copilot integration

### Code Structure

**GraphRAG** (graphrag_memory.py - 718 lines):
```python
# Main functions (synchronous)
def init()           # Initialize project structure
def index()          # Index documents into graph
def query()          # Query with local/global/drift
def status()         # Show indexing status
def test()           # Run self-test

# Helper utilities
def run_graphrag_command()      # Execute GraphRAG CLI
def create_minimal_prompts()    # Copy prompt templates
def find_root_dir()             # Locate GraphRAG root
```

**LightRAG** (repowiki.py - 832 lines):
```python
# Classes (async-first)
class Config                    # Configuration management
class RepositoryIndexer        # Index code repositories
class WikiGenerator            # Generate hierarchical docs

# Async functions
async def run_index()          # Index repository
async def run_generate()       # Generate wiki
async def run_all()           # Index + generate

# Generator methods (18 async methods)
async def _generate_home()
async def _generate_overview()
async def _generate_getting_started()
async def _generate_core_concepts()
async def _generate_api_reference()
# ... and 13 more
```

---

## 3. Query Capabilities

### GraphRAG: 3 Query Methods

| Method | Use Case | Speed | Detail | Best For |
|--------|----------|-------|--------|----------|
| **Local** | Specific entity questions | Fast | High detail | "How does X work?" |
| **Global** | Broad thematic questions | Slow | Overview | "What are main themes?" |
| **Drift** | Exploratory analysis | Medium | Contextual | "Explain architecture" |

**Example Usage**:
```bash
# Local search - entity-focused, fast
uv run graphrag_memory.py query "How to implement timer?" --method local

# Global search - community-focused, comprehensive
uv run graphrag_memory.py query "What are the main patterns?" --method global

# Drift search - exploratory
uv run graphrag_memory.py query "Explain the architecture" --method drift
```

**Technical Details**:
- Uses **community detection** for hierarchical understanding
- **Entity-centric**: Focuses on extracted entities and relationships
- **Prompt-driven**: Each mode has dedicated system prompts
- **Map-Reduce**: Global search uses map-reduce over communities

### LightRAG: 5 Query Modes

| Mode | Use Case | Speed | Behavior |
|------|----------|-------|----------|
| **Global** | High-level overview | Slow | Searches entire codebase |
| **Local** | Specific details | Fast | Focuses on local context |
| **Mix** | Overview + details | Medium | Combines global & local |
| **Hybrid** | Balanced (default) | Adaptive | Intelligently balances |
| **Naive** | Simple keyword search | Fastest | Basic text matching |

**Example Usage**:
```python
# Programmatic usage in wiki generation
content = await rag.query(
    "What is the overall architecture?",
    mode="hybrid"  # Adaptive, intelligent balancing
)
```

**Technical Details**:
- **Graph traversal**: Uses NetworkX for relationship navigation
- **Adaptive**: Hybrid mode automatically adjusts strategy
- **Built-in to library**: Query logic in lightrag-hku package
- **Wiki-optimized**: Different modes for different doc sections

---

## 4. Use Cases & Strengths

### GraphRAG Strengths

✅ **Best for**:
- Academic research and analysis
- Document Q&A systems
- Complex reasoning over interconnected information
- Enterprise knowledge management
- When you need detailed entity extraction

✅ **Key Advantages**:
1. **Production-ready prompts**: 13 carefully crafted templates
2. **Community detection**: Hierarchical understanding via clustering
3. **Simpler dependencies**: Only 3 direct dependencies
4. **Configurable**: Extensive YAML configuration
5. **Microsoft backing**: Enterprise-grade development
6. **LanceDB**: Efficient vector storage
7. **Multiple entity types**: Flexible entity extraction

❌ **Limitations**:
- No native async (uses threading)
- Slower indexing than LightRAG
- Requires Python <3.13
- More complex setup (prompts, settings.yaml)
- CLI-focused (less programmatic control)

### LightRAG Strengths

✅ **Best for**:
- Automated documentation generation
- Code repository analysis
- Wiki creation from codebases
- Fast prototyping
- When you need 5 different query strategies

✅ **Key Advantages**:
1. **Native async**: True async/await throughout
2. **Wiki generation**: Built-in hierarchical doc generator
3. **5 query modes**: Maximum flexibility
4. **Optimized parallelism**: 48/96/48 concurrent operations
5. **NetworkX integration**: Powerful graph operations
6. **Repository-aware**: Auto-detects git metadata
7. **Modern Python**: Takes advantage of 3.12+ features

❌ **Limitations**:
- More dependencies (11 direct)
- Requires Python 3.12+
- Less documentation than GraphRAG
- No built-in prompt customization
- nano-vectordb less mature than LanceDB

---

## 5. Configuration & Setup

### GraphRAG Configuration

**settings.yaml** (130 lines):
```yaml
models:
  default_chat_model:
    type: chat
    model_provider: github_copilot
    model: gpt-4o
    concurrent_requests: 5
    tokens_per_minute: 60000
    requests_per_minute: 30
    
  default_embedding_model:
    type: embedding
    model_provider: github_copilot
    model: text-embedding-3-small

chunks:
  size: 1500
  overlap: 150

extract_graph:
  entity_types: [organization, person, geo, event]
  max_gleanings: 1

cluster_graph:
  max_cluster_size: 10

community_reports:
  max_length: 2000
  max_input_length: 8000

# Plus local_search, global_search, drift_search configs
```

**Project Structure**:
```
my_project/
├── input/              # Markdown files to index
├── output/            # Generated graph data
│   └── lancedb/      # Vector storage
├── cache/            # Processing cache
├── logs/             # Indexing logs
├── prompts/          # 13 prompt templates (864 lines)
└── settings.yaml     # Configuration
```

### LightRAG Configuration

**Config Class** (in-code):
```python
@dataclass
class Config:
    # Paths
    repo_path: Path = Path(".")
    working_dir: Path = Path("./repowiki_storage")
    output_dir: Path = Path("./wiki_docs")
    
    # LLM settings - GitHub Copilot by default
    llm_model_name: str = "github_copilot/gpt-4o"
    embedding_model_name: str = "github_copilot/text-embedding-3-small"
    api_key: str = "oauth2"
    
    # Indexing
    code_extensions: Set[str] = {'.py', '.md', '.txt'}
    min_file_size: int = 50
    
    # Optimized parallelism
    max_parallel_insert: int = 48
    llm_model_max_async: int = 96
    embedding_func_max_async: int = 48
```

**Project Structure**:
```
my_project/
├── repowiki_storage/     # LightRAG working directory
│   └── main/            # Workspace (can have multiple)
│       ├── graph_chunk_entity_relation.graphml
│       ├── vdb_chunks.json
│       └── vdb_entities.json
└── wiki_docs/           # Generated wiki
    ├── Home.md
    ├── Overview.md
    ├── Getting-Started.md
    └── [13-19 more pages]
```

---

## 6. Performance Characteristics

### Indexing Performance

**GraphRAG**:
- **Speed**: Slower (thorough extraction)
- **Concurrency**: 5 concurrent requests (conservative)
- **Rate Limiting**: 30 requests/minute
- **Async Model**: Threaded (not native async)
- **Best for**: Smaller document sets (<1000 files)

**LightRAG**:
- **Speed**: Faster (optimized for code)
- **Concurrency**: 48/96/48 parallel operations
- **Rate Limiting**: Adaptive
- **Async Model**: Native async/await
- **Best for**: Larger repositories (1000+ files)

### Query Performance

**GraphRAG**:
```
Local Search:    Fast (100-500ms)
Global Search:   Slow (5-30s)
Drift Search:    Medium (1-5s)
```

**LightRAG**:
```
Naive Mode:      Fastest (50-200ms)
Local Mode:      Fast (200-800ms)
Hybrid Mode:     Medium (500ms-2s)
Mix Mode:        Medium (1-3s)
Global Mode:     Slow (3-10s)
```

### Memory Usage

**GraphRAG**:
- **Storage**: LanceDB (efficient vector storage)
- **Memory**: Moderate (loads communities as needed)
- **Disk**: ~100-500MB per 1000 documents

**LightRAG**:
- **Storage**: JSON files + GraphML
- **Memory**: Higher (loads full graph into NetworkX)
- **Disk**: ~50-200MB per 1000 files

---

## 7. LLM Integration

### Both Support GitHub Copilot

**GraphRAG**:
```yaml
model_provider: github_copilot
api_key: copilot  # OAuth2 via LiteLLM
model: gpt-4o
```

**LightRAG**:
```python
llm_model_name: "github_copilot/gpt-4o"
api_key: "oauth2"
# Uses forked litellm for authentication
```

### Model Requirements

**GraphRAG**:
- Chat model: Must support JSON mode
- Embedding model: Any compatible embedding model
- Token limits: Configurable (default 60k/min)

**LightRAG**:
- Chat model: 128K context window (gpt-4o)
- Embedding model: text-embedding-3-small
- Token limits: Managed by LiteLLM

---

## 8. Real-World Usage Patterns

### GraphRAG Workflow

```bash
# 1. Initialize project
uv run graphrag_memory.py init --root ./my_analysis

# 2. Add markdown documents to input/
cp -r my_docs/* ./my_analysis/input/

# 3. Index documents (creates knowledge graph)
uv run graphrag_memory.py index --verbose

# 4. Query for specific information
uv run graphrag_memory.py query "How does authentication work?" --method local

# 5. Query for broad themes
uv run graphrag_memory.py query "What are the security patterns?" --method global

# 6. Check status
uv run graphrag_memory.py status
```

**Typical Timeline**:
- Init: <1 second
- Index 100 docs: 5-15 minutes
- Query: 0.5-30 seconds depending on method

### LightRAG Workflow

```bash
# 1. Navigate to repository
cd /path/to/my_repo

# 2. Test setup
uv run repowiki.py test

# 3. Index + Generate wiki (all-in-one)
uv run repowiki.py all --extended

# Or step by step:
# 3a. Index repository
uv run repowiki.py index

# 3b. Generate wiki
uv run repowiki.py generate --extended
```

**Typical Timeline**:
- Test: <1 second
- Index 1000 files: 10-20 minutes
- Generate base wiki (13 pages): 5-10 minutes
- Generate extended wiki (19 pages): 15-25 minutes

---

## 9. Prompt Engineering

### GraphRAG: Extensive Prompt Templates

**13 Production Prompts** (864 lines total):

1. **extract_graph.txt**: Entity & relationship extraction
2. **extract_claims.txt**: Claim extraction from text
3. **summarize_descriptions.txt**: Entity description summarization
4. **community_report_graph.txt**: Community analysis from graph
5. **community_report_text.txt**: Community analysis from text
6. **local_search_system_prompt.txt**: Local search instructions
7. **global_search_knowledge_system_prompt.txt**: Global knowledge prompts
8. **global_search_map_system_prompt.txt**: Map phase of global search
9. **global_search_reduce_system_prompt.txt**: Reduce phase of global search
10. **drift_search_system_prompt.txt**: Drift search instructions
11. **drift_reduce_prompt.txt**: Drift search reduction
12. **basic_search_system_prompt.txt**: Basic search mode
13. **question_gen_system_prompt.txt**: Question generation

**Customization**: Easy to modify prompts in `prompts/` directory

### LightRAG: Built-in Prompts

**Prompts**: Embedded in lightrag-hku library (not easily customizable)

**Query Generation**: Automatic based on mode selection

**Wiki Prompts**: Hardcoded in WikiGenerator class:
```python
# Examples from code
query = f"Provide a comprehensive overview of the {repo_name} project"
query = f"List and describe the main classes in {repo_name}"
query = f"Explain the development workflow for {repo_name}"
```

**Trade-off**: Less flexibility, but simpler to use

---

## 10. Comparison with Vector-Only Approach (ChromaDB)

### How Knowledge Graphs Differ from Vector Search

**ChromaDB** (baseline):
- Simple vector embeddings
- Semantic similarity search
- No entity extraction
- No relationship modeling
- Fast but shallow understanding

**GraphRAG & LightRAG** (knowledge graphs):
- Extract entities (people, places, concepts, classes, functions)
- Model relationships (uses, inherits, calls, mentions)
- Community detection (clusters of related entities)
- Multi-hop reasoning (traverse relationships)
- Slower but deeper understanding

### When to Use Each

| Use Case | ChromaDB | GraphRAG | LightRAG |
|----------|----------|----------|----------|
| Simple Q&A | ✅ Best | ⚠️ Overkill | ⚠️ Overkill |
| Document analysis | ⚠️ Limited | ✅ Best | ✅ Good |
| Code documentation | ❌ Poor | ✅ Good | ✅ Best |
| Entity extraction | ❌ No | ✅ Yes | ✅ Yes |
| Relationship analysis | ❌ No | ✅ Yes | ✅ Yes |
| Fast prototyping | ✅ Best | ⚠️ Slow | ✅ Good |
| Production systems | ✅ Good | ✅ Best | ⚠️ Newer |

---

## 11. Limitations & Challenges

### GraphRAG Challenges

1. **Setup Complexity**: Requires proper directory structure and settings.yaml
2. **Slow Global Search**: Can take 30+ seconds for large graphs
3. **Python Version**: Restricted to <3.13
4. **No Native Async**: Uses threading instead of async/await
5. **Prompt Management**: 13 files to maintain
6. **Token Costs**: Extensive LLM usage for extraction
7. **Learning Curve**: Complex configuration options

### LightRAG Challenges

1. **Dependency Hell**: 11 direct dependencies can conflict
2. **Python 3.12+ Required**: Limits compatibility
3. **Less Mature**: Newer project, less battle-tested
4. **Memory Usage**: Loads full graph into memory
5. **Limited Customization**: Prompts are built-in
6. **Documentation**: Less comprehensive than GraphRAG
7. **Forked Dependencies**: Uses forked litellm (maintenance risk)

---

## 12. Decision Matrix

### Choose GraphRAG if you need:

✅ **Research & Analysis**
- Academic paper analysis
- Legal document review
- Medical literature analysis
- Patent research

✅ **Enterprise Features**
- Production-ready prompts
- Extensive configuration
- Microsoft backing
- Mature ecosystem

✅ **Custom Entity Types**
- Domain-specific entities
- Custom relationship types
- Flexible extraction

✅ **Simpler Dependencies**
- Fewer packages to manage
- Stable dependency tree

### Choose LightRAG if you need:

✅ **Code Documentation**
- Automated wiki generation
- Repository analysis
- API documentation
- Architecture documentation

✅ **Performance**
- Fast indexing
- High concurrency (48/96/48)
- Native async/await
- Efficient for large codebases

✅ **Flexibility**
- 5 different query modes
- Mix and match strategies
- Hybrid intelligent mode

✅ **Modern Python**
- Python 3.12+ features
- Async-first architecture
- Type hints throughout

---

## 13. Integration & Ecosystem

### GraphRAG Integrations

**Works well with**:
- **LanceDB**: Primary vector store
- **GitHub Copilot**: LLM provider
- **OpenAI**: Alternative LLM
- **Typer**: CLI framework
- **Rich**: Terminal output

**Export formats**:
- GraphML (optional)
- Parquet files
- JSON embeddings

### LightRAG Integrations

**Works well with**:
- **NetworkX**: Graph operations
- **LlamaIndex**: LLM abstraction
- **GitHub Copilot**: Default LLM
- **nano-vectordb**: Vector storage
- **Other skills**: pptx-creator, excel, github-pr

**Export formats**:
- Markdown wiki (13-19 pages)
- GraphML
- JSON vector databases

---

## 14. Cost Considerations

### Token Usage Estimates (per 1000 documents)

**GraphRAG**:
- **Indexing**: High (5-10M tokens)
  - Entity extraction: ~3M tokens
  - Relationship extraction: ~2M tokens
  - Community reports: ~2M tokens
  - Embeddings: ~1M tokens
- **Query**:
  - Local: Low (~5k tokens)
  - Global: High (~50k tokens)
  - Drift: Medium (~20k tokens)

**LightRAG**:
- **Indexing**: Medium (3-6M tokens)
  - Entity/relationship extraction: ~4M tokens
  - Embeddings: ~1M tokens
- **Query**:
  - Naive: Very low (~1k tokens)
  - Local: Low (~3k tokens)
  - Hybrid: Medium (~10k tokens)
  - Global: High (~30k tokens)
- **Wiki Generation**: Very high (~2M tokens for 19 pages)

**Cost with GitHub Copilot**:
- Free with license (no per-token charges)
- Subject to rate limits
- GraphRAG: 30 requests/min
- LightRAG: Higher concurrency possible

---

## 15. Future Outlook

### GraphRAG Roadmap

**Likely developments**:
- Improved async support
- Faster global search
- More embedding model options
- Enhanced community detection
- Better visualization tools
- Python 3.13+ support

**Community**: Large, backed by Microsoft

### LightRAG Roadmap

**Likely developments**:
- Stable 2.0 release
- More query modes
- Better prompt customization
- Enhanced wiki templates
- Visualization tools
- Broader LLM support

**Community**: Growing, active HKU research project

---

## 16. Conclusion & Recommendations

### Summary Table

| Criteria | GraphRAG | LightRAG | Winner |
|----------|----------|----------|--------|
| **Documentation** | Excellent | Good | GraphRAG |
| **Setup Ease** | Medium | Easy | LightRAG |
| **Indexing Speed** | Slow | Fast | LightRAG |
| **Query Flexibility** | 3 modes | 5 modes | LightRAG |
| **Async Support** | No (threaded) | Yes (native) | LightRAG |
| **Dependencies** | Simple (3) | Complex (11) | GraphRAG |
| **Prompt Control** | Full (864 lines) | Limited | GraphRAG |
| **Wiki Generation** | No | Yes | LightRAG |
| **Python Support** | 3.10-3.12 | 3.12+ | GraphRAG |
| **Maturity** | High | Medium | GraphRAG |
| **Use Case Fit** | General analysis | Code docs | Tie |

### Final Recommendations

**Use GraphRAG for**:
1. Research and academic analysis
2. General document Q&A systems
3. When you need custom prompts
4. Enterprise deployments
5. Maximum configurability
6. When dependencies matter

**Use LightRAG for**:
1. Code repository documentation
2. Automated wiki generation
3. Fast prototyping
4. Large codebases
5. When you need 5 query modes
6. Modern Python projects (3.12+)

**Use ChromaDB for**:
1. Simple vector search
2. No entity extraction needed
3. Fast, lightweight solution
4. When knowledge graphs are overkill

### Hybrid Approach

Consider using **both**:
- **GraphRAG** for document analysis and Q&A
- **LightRAG** for wiki generation and documentation
- **ChromaDB** for fast semantic search
- Each serves different needs in the knowledge management pipeline

---

## Appendix: Quick Reference

### GraphRAG Commands

```bash
# Initialize
uv run graphrag_memory.py init [--root DIR]

# Index documents
uv run graphrag_memory.py index --input DIR [--verbose]

# Query
uv run graphrag_memory.py query "QUESTION" [--method local|global|drift]

# Status
uv run graphrag_memory.py status [--root DIR]

# Test
uv run graphrag_memory.py test
```

### LightRAG Commands

```bash
# Test setup
uv run repowiki.py test

# Index repository
uv run repowiki.py index [--repo PATH] [--working-dir DIR]

# Generate wiki
uv run repowiki.py generate [--extended] [--output-dir DIR]

# All-in-one
uv run repowiki.py all [--extended]
```

### Key Files

**GraphRAG**:
- `scripts/graphrag_memory.py` (718 lines)
- `references/settings.yaml` (130 lines)
- `references/prompts/*.txt` (13 files, 864 lines)

**LightRAG**:
- `scripts/repowiki.py` (832 lines)
- `references/query-modes.md`
- `references/configuration.md`

---

**Document Version**: 1.0  
**Last Updated**: February 4, 2026  
**Authors**: Comparative analysis based on workspace implementations
