# Memory System Architecture

## Overview

The memory system provides semantic search over past implementation knowledge to help the apply agent produce better quality code with fewer iterations.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Request                             │
│                  "Apply change 001-watchdog-timer"               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ApplyModule                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              ReAct Agent (VerboseReAct)                    │ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │ │
│  │  │  File Tools  │  │ Simics Tools │  │  Memory Tool    │ │ │
│  │  │              │  │              │  │                 │ │ │
│  │  │ • read_file  │  │ • build      │  │ • retrieve_     │ │ │
│  │  │ • write_file │  │ • test       │  │   memory()      │ │ │
│  │  │ • list_dir   │  │ • validate   │  │                 │ │ │
│  │  └──────────────┘  └──────────────┘  └────────┬────────┘ │ │
│  └────────────────────────────────────────────────┼──────────┘ │
└───────────────────────────────────────────────────┼────────────┘
                                                    │
                                                    ▼
                                    ┌───────────────────────────┐
                                    │   MemoryRetriever         │
                                    │                           │
                                    │  • forward()              │
                                    │  • retrieve_for_dml()     │
                                    │  • retrieve_for_test()    │
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │     ChromaDBRM            │
                                    │  (DSPy Retrieve)          │
                                    │                           │
                                    │  • Semantic search        │
                                    │  • Category filtering     │
                                    │  • Top-k retrieval        │
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │       ChromaDB            │
                                    │    (Vector Store)         │
                                    │                           │
                                    │  Collection:              │
                                    │  "openspec_memories"      │
                                    │                           │
                                    │  Documents: 45 chunks     │
                                    │  Categories: DML/Test/Gen │
                                    └───────────────────────────┘
```

## Data Flow

### 1. Indexing Phase (One-Time Setup)

```
Memory Documents                    Indexer                     ChromaDB
(openspec-memories/)                                           (.chromadb/)
                                                              
01_DML_Patterns.md     ──┐                                   
02_Test_Patterns.md    ──┼──> MemoryIndexer ──> Chunks ──> Collection
03_Troubleshooting.md  ──┘    • Parse markdown              • Embeddings
...                           • Extract sections            • Metadata
                              • Categorize                  • Indexed
                              • Create chunks
```

**Process:**
1. Read markdown files from `openspec-memories/`
2. Parse into sections (headers + content)
3. Detect category from filename (DML/Test/General)
4. Create chunks with metadata
5. Generate embeddings
6. Store in ChromaDB collection

### 2. Retrieval Phase (During Apply)

```
Agent Query                    Retriever                    Results
                                                           
"implement timer       ──> MemoryRetriever ──> ChromaDB ──> Top-3 Chunks
countdown logic"           • Build query                   • Ranked by
category: DML              • Filter category                 relevance
                           • Semantic search               • With metadata
                           • Rank results
```

**Process:**
1. Agent calls `retrieve_memory(task_description, category)`
2. MemoryRetriever builds query from task + error context
3. ChromaDBRM performs semantic search
4. Filter by category if specified
5. Return top-k most relevant chunks
6. Format results for agent consumption

### 3. Apply Phase (Full Workflow)

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Read Spec                                               │
│   Agent: read_file("openspec/changes/001/specs/timer/spec.md") │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Retrieve Implementation Patterns                        │
│   Agent: retrieve_memory("implement timer countdown", "DML")    │
│   Result: "Use `after` callback for countdown logic..."         │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Implement DML Code                                      │
│   Agent: write_file("simics-project/modules/wdt/wdt.dml", ...) │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Build and Check Errors                                  │
│   Agent: build_simics_project(...)                              │
│   Error: "undefined identifier 'wdogint'"                       │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Retrieve Troubleshooting                                │
│   Agent: retrieve_memory("undefined identifier", "DML")         │
│   Result: "Check register scope - use this.bank.regs.name"      │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Fix and Rebuild                                         │
│   Agent: write_file(...) # Apply fix                            │
│   Agent: build_simics_project(...)                              │
│   Result: Build successful ✅                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### MemoryIndexer

**Purpose**: Index memory documents into ChromaDB

**Key Methods:**
- `index_memories()` - Index all documents
- `get_stats()` - Get indexing statistics
- `_parse_markdown()` - Parse markdown into sections
- `_detect_category()` - Detect DML/Test/General
- `_create_chunks()` - Create searchable chunks

**Configuration:**
```python
indexer = MemoryIndexer(
    memory_dir="openspec-memories",
    persist_directory=".chromadb",
    collection_name="openspec_memories",
    chunk_size=1000,
    chunk_overlap=200
)
```

### MemoryRetriever

**Purpose**: Retrieve relevant memory chunks

**Key Methods:**
- `forward()` - Main retrieval method
- `retrieve_for_dml()` - DML-specific retrieval
- `retrieve_for_test()` - Test-specific retrieval

**Configuration:**
```python
retriever = MemoryRetriever(
    collection_name="openspec_memories",
    persist_directory=".chromadb",
    k=3  # Number of chunks to retrieve
)
```

### ChromaDBRM

**Purpose**: DSPy Retrieve interface for ChromaDB

**Key Features:**
- Semantic search using embeddings
- Category filtering via metadata
- Top-k retrieval
- Integration with DSPy modules

### ApplyModule

**Purpose**: Apply OpenSpec changes with memory support

**Key Features:**
- Optional memory integration
- `retrieve_memory` tool for agent
- Configurable retrieval count
- Graceful fallback

**Configuration:**
```python
apply_module = ApplyModule(
    interactive=True,
    enable_memory=True,
    memory_persist_dir=".chromadb",
    memory_k=3
)
```

## Memory Categories

### DML Category

**Purpose**: Device implementation patterns

**Content:**
- DML syntax and patterns
- Register side-effects
- Timer/interrupt implementations
- Scope and access patterns
- Common compilation errors

**Example Query:**
```python
retrieve_memory(
    "implement timer countdown with after callback",
    category="DML"
)
```

### Test Category

**Purpose**: Python test patterns

**Content:**
- Simics test API usage
- Signal testing patterns
- Register verification
- Test setup/teardown
- Common test failures

**Example Query:**
```python
retrieve_memory(
    "test interrupt signal assertion",
    category="Test"
)
```

### General Category

**Purpose**: Workflow and troubleshooting

**Content:**
- Apply workflow guidance
- Debugging approaches
- Quality checks
- Best practices
- Common pitfalls

**Example Query:**
```python
retrieve_memory(
    "apply workflow steps",
    category="General"
)
```

## Configuration

### YAML Configuration

```yaml
# dspy_openspec/config/default.yaml
openspec:
  memory:
    enabled: true                    # Enable/disable
    persist_dir: ".chromadb"         # Storage location
    collection_name: "openspec_memories"
    k: 3                             # Retrieval count
    auto_retrieve: true              # Auto on errors
```

### Environment Variables

```bash
export CHROMADB_PERSIST_DIR="/custom/path/.chromadb"
export MEMORY_K=5
```

### Programmatic Configuration

```python
apply_module = ApplyModule(
    enable_memory=True,
    memory_persist_dir="/custom/path/.chromadb",
    memory_k=5
)
```

## Performance Characteristics

### Indexing

- **Time**: ~1-2 seconds for 10 documents
- **Disk**: ~1-5MB per 100 chunks
- **Memory**: ~10-20MB during indexing

### Retrieval

- **Latency**: ~50-100ms per query
- **Memory**: ~10-50MB for ChromaDB
- **Accuracy**: High (semantic search)

### Scaling

- **Documents**: Tested up to 100 documents
- **Chunks**: Tested up to 1000 chunks
- **Concurrent**: Single-threaded (ChromaDB limitation)

## Error Handling

### ChromaDB Not Installed

```python
if not MEMORY_AVAILABLE:
    print("⚠️ Memory retrieval disabled: chromadb not installed")
    # Falls back to no memory
```

### Collection Not Found

```python
try:
    collection = client.get_collection(name)
except Exception:
    raise ValueError("Collection not found. Please index first.")
```

### No Results Found

```python
if not results['documents']:
    return []  # Empty list, agent continues
```

## Security Considerations

### Data Privacy

- Memory documents stored locally
- No external API calls for embeddings (uses local model)
- ChromaDB data encrypted at rest (optional)

### Access Control

- File system permissions control access
- No network exposure by default
- Can be configured for multi-user scenarios

## Monitoring and Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Retrieval Quality

```bash
# Test search with different queries
python -m dspy_openspec.memory.cli search "timer" --k 5
python -m dspy_openspec.memory.cli search "implement timer countdown" --k 5
```

### Monitor Agent Usage

```python
# VerboseReAct shows all tool calls
apply_module = ApplyModule(interactive=True)
# Watch for retrieve_memory calls in output
```

## Best Practices

### Memory Document Structure

```markdown
# 01_DML_Timer_Patterns.md

## Timer Countdown Implementation

**Pattern**: Use `after` callback

**Example**:
```dml
method start_countdown() {
    after(delay_cycles) call timeout_handler;
}
```

**Common Mistakes**:
- Don't use Python-style loops
- Remember to cancel on reset
```

### Query Writing

**Good queries:**
- "implement watchdog timer countdown with lazy evaluation"
- "DML compilation error: register scope violation"
- "test interrupt signal assertion after register write"

**Poor queries:**
- "timer" (too vague)
- "error" (no context)
- "help" (not specific)

### Category Selection

- Use "DML" for device implementation questions
- Use "Test" for test writing questions
- Use "General" for workflow questions
- Omit category for broad searches

## Future Architecture

### Planned Enhancements

```
┌─────────────────────────────────────────────────────────────────┐
│                    Enhanced Memory System                        │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │   Automatic    │  │   Relevance    │  │   Multi-modal   │  │
│  │    Memory      │  │    Feedback    │  │    Retrieval    │  │
│  │   Creation     │  │    Learning    │  │                 │  │
│  └────────────────┘  └────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐  │
│  │  Hierarchical  │  │     Memory     │  │  Cross-Project  │  │
│  │  Organization  │  │   Versioning   │  │     Sharing     │  │
│  └────────────────┘  └────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Summary

The memory system provides:

✅ **Semantic search** over implementation knowledge
✅ **Category filtering** for targeted retrieval
✅ **Agent integration** via `retrieve_memory` tool
✅ **Automatic error recovery** with troubleshooting guidance
✅ **Configurable** and **extensible** architecture
✅ **Production-ready** with proper error handling

This enables the apply agent to learn from past implementations and produce higher quality code with fewer iterations.
