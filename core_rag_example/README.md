# Core RAG Components Example

This example demonstrates how to use ADK Python's core RAG components including:

1. **VertexAiRagRetrieval** - For document retrieval using Vertex AI RAG
2. **VertexAiRagMemoryService** - For RAG-powered memory storage
3. **VertexAiSearchTool** - For search functionality
4. **FilesRetrieval** - For local file-based retrieval

## Setup

1. Install ADK with extensions:
```bash
pip install "google-adk[extensions]"
```

2. Set up environment variables:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export RAG_CORPUS="projects/your-project/locations/us-central1/ragCorpora/your-corpus-id"
export VERTEX_AI_SEARCH_DATASTORE="projects/your-project/locations/global/collections/default_collection/dataStores/your-datastore"
```

3. Run the examples:
```bash
# Basic RAG agent
python basic_rag_agent.py

# Memory-powered RAG agent
python memory_rag_agent.py

# Multi-tool RAG agent
python multi_tool_rag_agent.py

# Local files RAG agent
python files_rag_agent.py
```

## Examples Overview

- `basic_rag_agent.py` - Simple RAG with Vertex AI retrieval
- `memory_rag_agent.py` - RAG with persistent memory using Vertex AI RAG Memory Service
- `multi_tool_rag_agent.py` - Combines multiple RAG tools (search + retrieval)
- `files_rag_agent.py` - Local file-based RAG without cloud dependencies
- `sample_documents/` - Sample documents for testing