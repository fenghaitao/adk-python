# Core RAG Components Example

This example demonstrates how to use ADK Python's core RAG components including:

1. **FilesRetrieval** - For local file-based retrieval
2. **GoogleSearchTool** - For web search functionality

## Setup

1. Install ADK with extensions:
```bash
pip install "google-adk[extensions]"
```

2. Set up environment variables (optional for Google Search):
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
# Google Search API credentials (optional - for enhanced web search)
```

3. Run the example:
```bash
# Local files RAG agent with web search
python files_rag_agent.py

# Or run all examples interactively
python run_all_examples.py
```

## Examples Overview

- `files_rag_agent.py` - Local file-based RAG combined with web search capabilities
- `run_all_examples.py` - Interactive runner for the example
- `sample_documents/` - Sample documents for testing (created automatically)