# Cached FilesRetrieval for ADK

This directory contains an enhanced version of FilesRetrieval that caches embeddings to disk for significantly better performance on repeated use.

## 🚀 Quick Start

### Basic Usage

```python
from cached_files_retrieval import CachedFilesRetrieval

# Create cached retrieval tool
tool = CachedFilesRetrieval(
    name="my_docs_search",
    description="Search through my documents",
    input_dir="./my_documents"
)
```

### With Agent

```python
from cached_files_retrieval import create_cached_rag_agent

# Create agent with cached retrieval
agent, retrieval_tool = create_cached_rag_agent("./my_documents")

# Use the agent
response = agent.run("What is machine learning?")
```

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `cached_files_retrieval.py` | Main implementation of CachedFilesRetrieval |
| `cached_rag_agent.py` | Drop-in replacement for `files_rag_agent.py` with caching |
| `demo_cached_retrieval.py` | Performance demonstration and examples |
| `README_CACHED.md` | This documentation |

## 🎯 Key Benefits

### Performance Comparison

| Operation | Original FilesRetrieval | CachedFilesRetrieval |
|-----------|------------------------|---------------------|
| First run | ~10-30 seconds | ~10-30 seconds |
| Subsequent runs | ~10-30 seconds | ~1-3 seconds |
| **Speedup** | - | **5-10x faster** |

### Features

✅ **Persistent Cache**: Embeddings saved to disk  
✅ **Automatic Invalidation**: Detects file changes  
✅ **Fast Startup**: Skip re-computing embeddings  
✅ **Drop-in Replacement**: Works with existing code  
✅ **Configurable**: Custom cache location  
✅ **Metadata Tracking**: File hash verification  

## 🛠️ Configuration Options

### Basic Configuration

```python
CachedFilesRetrieval(
    name="search_docs",
    description="Search documents",
    input_dir="./documents",           # Required: documents directory
    cache_dir="./custom_cache",        # Optional: custom cache location
    force_rebuild=False                # Optional: force cache rebuild
)
```

### Cache Directory Structure

```
documents/
├── doc1.txt
├── doc2.txt
└── .embeddings_cache/              # Default cache location
    ├── docstore.json               # Document store
    ├── index_store.json           # Index metadata
    ├── vector_store.json          # Vector embeddings
    └── cache_metadata.json        # File tracking info
```

## 📊 Performance Analysis

### Demo Script

Run the performance demo to see the benefits:

```bash
python demo_cached_retrieval.py
```

Sample output:
```
🔄 TEST 1: First creation (building cache)
⏱️  First creation time: 15.32 seconds

🔄 TEST 2: Second creation (using cache)  
⏱️  Second creation time: 2.14 seconds
🚀 Speedup: 7.2x faster!
```

### Production Usage

```bash
# Run cached RAG agent (demo mode)
python cached_rag_agent.py

# Run in interactive mode
python cached_rag_agent.py --interactive
```

## 🔧 Cache Management

### Check Cache Status

```python
cache_info = retrieval_tool.get_cache_info()
print(f"Cache size: {cache_info['cache_size_mb']} MB")
print(f"Documents: {cache_info['documents_count']}")
print(f"Cache valid: {cache_info['cache_valid']}")
```

### Manual Cache Control

```python
# Force rebuild cache
retrieval_tool.invalidate_cache()

# Create with force rebuild
tool = CachedFilesRetrieval(
    name="search_docs",
    description="Search documents", 
    input_dir="./documents",
    force_rebuild=True  # Ignores existing cache
)
```

### Clean Up Cache

```bash
# Remove specific cache
rm -rf ./documents/.embeddings_cache

# Remove all ADK caches
find . -name ".embeddings_cache" -type d -exec rm -rf {} +
```

## 🔍 How It Works

### Cache Validation Process

1. **File Discovery**: Scan input directory for documents
2. **Metadata Generation**: Calculate file hashes and timestamps  
3. **Cache Check**: Compare current files with cached metadata
4. **Decision**: 
   - If files unchanged → Load from cache
   - If files changed → Rebuild cache
   - If no cache → Build new cache

### File Change Detection

The system detects changes using multiple signals:
- File modification time (mtime)
- File size
- Content hash (MD5)

### Supported File Types

- `.txt` - Plain text files
- `.md` - Markdown files  
- `.pdf` - PDF documents (requires additional setup)
- `.docx` - Word documents (requires additional setup)

## 🚧 Troubleshooting

### Common Issues

**"No module named 'llama_index.embeddings.huggingface'"**
```bash
pip install llama-index-embeddings-huggingface
```

**"Could not load OpenAI embedding model"**
```python
# Option 1: Set OpenAI key
os.environ['OPENAI_API_KEY'] = 'your-key-here'

# Option 2: Use local embeddings
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```

**Cache not invalidating after file changes**
```python
# Force rebuild
tool = CachedFilesRetrieval(..., force_rebuild=True)

# Or manually invalidate
tool.invalidate_cache()
```

### Performance Optimization

**For Large Document Collections:**
- Use SSD storage for cache directory
- Consider splitting into multiple smaller indices
- Monitor cache size and clean up periodically

**For Production:**
- Set up proper local embedding models
- Use persistent cache storage
- Implement cache warming strategies

## 🔄 Migration Guide

### From Original FilesRetrieval

**Before:**
```python
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval

tool = FilesRetrieval(
    name="search_docs",
    description="Search documents",
    input_dir="./documents"
)
```

**After:**
```python
from cached_files_retrieval import CachedFilesRetrieval

tool = CachedFilesRetrieval(
    name="search_docs", 
    description="Search documents",
    input_dir="./documents"
    # cache_dir="./custom_cache"  # Optional
)
```

### Updating Existing Agents

Replace the tool creation in your agent setup:

```python
# Old
files_tool = FilesRetrieval(...)

# New  
files_tool = CachedFilesRetrieval(...)

# Agent creation remains the same
agent = Agent(
    model="gemini-2.0-flash-001",
    tools=[files_tool, other_tools...],
    # ... other config
)
```

## 📈 Best Practices

### Development

- Use small document sets for testing
- Enable force_rebuild during development
- Monitor cache sizes and clean up regularly

### Production

- Set up dedicated cache directories
- Implement cache backup strategies
- Monitor file change patterns
- Use proper embedding models (not dummy keys)

### Performance Tuning

```python
# For frequently changing documents
CachedFilesRetrieval(
    input_dir="./dynamic_docs",
    cache_dir="/fast_ssd/cache"  # Use fast storage
)

# For static document collections  
CachedFilesRetrieval(
    input_dir="./static_docs",
    cache_dir="./persistent_cache",
    force_rebuild=False  # Maximize cache usage
)
```

## 🤝 Contributing

The cached retrieval implementation follows ADK patterns and can be extended:

- Add support for more file types
- Implement distributed caching
- Add cache compression
- Implement cache sharing between instances

---

## 📚 Related Documentation

- [ADK FilesRetrieval Documentation](../src/google/adk/tools/retrieval/)
- [LlamaIndex Vector Stores](https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores.html)
- [ADK RAG Examples](../contributing/samples/)

For questions or issues, please check the main ADK documentation or create an issue in the repository.