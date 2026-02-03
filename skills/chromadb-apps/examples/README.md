# ChromaDB Memory Examples

This directory contains example code demonstrating various usage patterns for the ChromaDB Memory skill.

## Files

### basic_usage.py

Demonstrates fundamental operations:
- Indexing markdown documents
- Searching with category filters
- RAG (Retrieval-Augmented Generation) pattern
- Custom chunking strategies
- Statistics and monitoring

**Note:** These are code examples for reference. Use the CLI for actual operations:

```bash
# Instead of running the examples, use:
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "your query"
```

## Common Patterns

### 1. Simple Search

```python
from chromadb_memory import MemoryRetriever
import dspy

dspy.settings.configure(lm=dspy.LM("openai/gpt-4"))
retriever = MemoryRetriever(k=3)

result = retriever(task_description="How to implement timer?")
for passage in result.passages:
    print(passage)
```

### 2. Category-Filtered Search

```python
# Search only in DML category
dml_result = retriever(
    task_description="register access patterns",
    category="DML"
)

# Search only in Test category  
test_result = retriever(
    task_description="test examples",
    category="Test"
)
```

### 3. RAG Module

```python
class RAGModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retriever = MemoryRetriever(k=3)
        self.generate = dspy.ChainOfThought("context, query -> answer")
    
    def forward(self, query):
        retrieval = self.retriever(query)
        context = "\n\n".join(retrieval.passages)
        return self.generate(context=context, query=query)

dspy.settings.configure(lm=dspy.LM("openai/gpt-4"))
rag = RAGModule()
result = rag("How to implement watchdog timer?")
print(result.answer)
```

### 4. ReAct with Memory

```python
class ReActAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retriever = MemoryRetriever(k=3)
        
        def search_memory(query: str) -> str:
            result = self.retriever(query)
            return "\n\n".join(result.passages)
        
        self.agent = dspy.ReAct(
            "task -> result",
            tools=[search_memory]
        )
    
    def forward(self, task):
        return self.agent(task=task)
```

### 5. Multi-Category Search

```python
def search_all_categories(query, k=3):
    """Search across all categories and combine results."""
    retriever = MemoryRetriever(k=k)
    
    categories = ["DML", "Test", "General"]
    all_passages = []
    
    for category in categories:
        result = retriever(task_description=query, category=category)
        all_passages.extend(result.passages)
    
    return all_passages[:k]
```

### 6. Indexed Statistics

```python
from chromadb_memory import MemoryIndexer

indexer = MemoryIndexer(
    memory_dir="openspec-memories",
    persist_directory=".chromadb"
)

stats = indexer.get_stats()
print(f"Total: {stats['total_chunks']} chunks")
print(f"Files: {stats['unique_files']}")
for category, count in stats['categories'].items():
    print(f"  {category}: {count} chunks")
```

## Running Examples

These examples show code patterns. To actually use the skill:

```bash
# CLI is recommended for most operations
uv run skills/chromadb-apps/scripts/chromadb_memory.py --help

# Index
uv run skills/chromadb-apps/scripts/chromadb_memory.py index openspec-memories

# Search
uv run skills/chromadb-apps/scripts/chromadb_memory.py search "timer" --category DML

# Stats
uv run skills/chromadb-apps/scripts/chromadb_memory.py stats
```

## See Also

- **Quick Start**: `../QUICKSTART.md` - Get started in 5 minutes
- **Full Documentation**: `../SKILL.md` - Complete reference
- **ChromaDB Config**: `../references/chromadb.md` - Database configuration
- **DSPy Patterns**: `../references/dspy-retrieval.md` - Advanced patterns
