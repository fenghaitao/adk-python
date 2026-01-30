# LightRAG Tests

This folder contains test and demo scripts for LightRAG with GitHub Copilot.

## Test Scripts

### Authentication Test
**`tmp_test_copilot_auth.py`**
- Tests GitHub Copilot authentication
- Verifies LLM (gpt-4o-mini) is working
- Verifies embeddings (text-embedding-3-small) are working
- Quick test (~10 seconds)

**Usage:**
```bash
../../.venv/bin/python tmp_test_copilot_auth.py
```

**Expected output:**
```
✅ LLM Response: Hello from GitHub Copilot!
✅ Embedding dimension: 1536
🎉 GitHub Copilot is working!
```

### Query Test
**`tmp_quick_query_test.py`**
- Tests querying the indexed knowledge base
- Runs 3 sample queries
- Uses hybrid search mode
- Takes ~30-60 seconds

**Usage:**
```bash
../../.venv/bin/python tmp_quick_query_test.py
```

**Sample queries:**
- "What is DML?"
- "How do I model timers in Simics?"
- "What are best practices for testing?"

## Demo Scripts

### Full LightRAG Demo
**`tmp_lightrag_github_copilot.py`**
- Complete LightRAG demonstration
- Inserts sample documents
- Tests all 4 search modes
- Shows entity extraction and querying

**Usage:**
```bash
../../.venv/bin/python tmp_lightrag_github_copilot.py
```

**What it demonstrates:**
- Document insertion
- Entity extraction
- Knowledge graph building
- Query with different modes

### OpenAI Demo
**`tmp_rovodev_lightrag_openai.py`**
- LightRAG demo using OpenAI instead of GitHub Copilot
- Requires OPENAI_API_KEY environment variable
- Similar to GitHub Copilot demo but with OpenAI models

**Usage:**
```bash
export OPENAI_API_KEY='sk-your-key'
../../.venv/bin/python tmp_rovodev_lightrag_openai.py
```

### Visual Learning Tool
**`tmp_rovodev_visualize_lightrag.py`**
- Interactive ASCII visualizations
- Shows how LightRAG works step-by-step
- Explains chunking, entity extraction, knowledge graph
- Demonstrates all search modes

**Usage:**
```bash
../../.venv/bin/python tmp_rovodev_visualize_lightrag.py
```

**What you'll see:**
- Document chunking process
- Entity and relationship extraction
- Knowledge graph construction
- Storage architecture
- Query modes comparison
- Complete query flow

## Running All Tests

### Quick Health Check
```bash
# 1. Test authentication
../../.venv/bin/python tmp_test_copilot_auth.py

# 2. Test queries (requires indexed knowledge base)
../../.venv/bin/python tmp_quick_query_test.py
```

### Full Demo Suite
```bash
# 1. Authentication test
../../.venv/bin/python tmp_test_copilot_auth.py

# 2. Visual learning
../../.venv/bin/python tmp_rovodev_visualize_lightrag.py

# 3. Full demo
../../.venv/bin/python tmp_lightrag_github_copilot.py

# 4. Query test
../../.venv/bin/python tmp_quick_query_test.py
```

## Prerequisites

### For All Tests
- Python environment: `../../.venv/bin/python`
- LightRAG submodule: `../../lightrag/`
- Dependencies installed (via setup script)

### For Query Tests
- Knowledge base must be indexed first
- Run: `../../.venv/bin/python ../index_openspec_with_copilot.py`
- Storage location: `../lightrag_openspec_storage/`

### For GitHub Copilot Tests
- GitHub Copilot subscription
- OAuth2 authentication (automatic via LiteLLM)
- No GitHub CLI needed

### For OpenAI Tests
- OpenAI API key
- Set: `export OPENAI_API_KEY='sk-your-key'`

## File Descriptions

| File | Purpose | Duration | Prerequisites |
|------|---------|----------|---------------|
| `tmp_test_copilot_auth.py` | Auth test | ~10s | GitHub Copilot |
| `tmp_quick_query_test.py` | Query test | ~30-60s | Indexed KB |
| `tmp_lightrag_github_copilot.py` | Full demo | ~2-3min | GitHub Copilot |
| `tmp_rovodev_lightrag_openai.py` | OpenAI demo | ~2-3min | OpenAI API key |
| `tmp_rovodev_visualize_lightrag.py` | Visual guide | ~1min | None |
| `test_sample_indexing.py` | Sample book test | ~2-3min | GitHub Copilot |

## Sample Data

**`sample_book.txt`** - "A Tale of Two AI Systems"
- Small document (3.9K) about ADK and LightRAG
- Used by `test_sample_indexing.py` for demonstrations
- Good for quick testing without large document sets

## Troubleshooting

### Authentication Fails
```bash
# Test GitHub Copilot access
../../.venv/bin/python tmp_test_copilot_auth.py

# If fails, verify dependencies
cd .. && ./setup_lightrag_copilot_simple.sh
```

### Knowledge Base Not Found
```bash
# Index OpenSpec memories first
cd ..
../../.venv/bin/python index_openspec_with_copilot.py
```

### Import Errors
```bash
# Verify LightRAG submodule
ls -la ../../lightrag/

# If missing, initialize submodule
cd ../..
git submodule update --init --recursive
```

### Path Issues
All scripts use relative paths:
- `sys.path.insert(0, '../../lightrag')`
- `WORKING_DIR = "../lightrag_openspec_storage"`
- Run from tests directory or use `../../.venv/bin/python tests/script.py`

## Expected Results

### tmp_test_copilot_auth.py
```
🧪 Testing GitHub Copilot Authentication

1️⃣ Testing LLM (github_copilot/gpt-4o-mini)...
✅ LLM Response: Hello from GitHub Copilot!

2️⃣ Testing Embeddings (github_copilot/text-embedding-3-small)...
✅ Embedding dimension: 1536

════════════════════════════════════════════════════════════════
🎉 GitHub Copilot is working!
````

### tmp_quick_query_test.py
```
🔍 Testing OpenSpec Knowledge Base Queries
✅ Knowledge base loaded

[1/3] ❓ Query: What is DML?
💡 Answer:
DML (Device Modeling Language) is a specialized language...

[2/3] ❓ Query: How do I model timers in Simics?
💡 Answer:
Timer modeling in Simics uses event objects and after statements...

[3/3] ❓ Query: What are best practices for testing?
💡 Answer:
[Results based on indexed content]
```

## Notes

- Test files are prefixed with `tmp_` for easy identification
- Scripts are executable (`chmod +x`)
- All use GitHub Copilot by default (free with subscription)
- OpenAI variant provided for comparison

---

**Quick Start:** `../../.venv/bin/python tmp_test_copilot_auth.py`
