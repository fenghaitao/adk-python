---
name: cognee-apps
description: Index and search current directory using Cognee knowledge graphs
version: 1.0.0
author: Google LLC
license: Apache-2.0
tags: [cognee, knowledge-graph, code-search, indexing, github-copilot]
dependencies:
  - cognee>=0.1.0
  - litellm>=1.76.0
  - pyyaml>=6.0
  - python-dotenv>=1.0.0
python: ">=3.12"
---

# Cognee Memory - Cognee Knowledge Graph Skill

A self-contained skill for indexing and searching the current directory using Cognee knowledge graphs. Works seamlessly with GitHub Copilot models.

## Overview

**Cognee Memory** is a command-line tool that:
1. **Indexes** any directory (via `--root`) into Cognee knowledge graphs
2. **Searches** indexed content using multiple strategies
3. **Organizes** content with datasets (namespaces for different projects)
4. **Integrates** with GitHub Copilot for free LLM access

Unlike LightRAG-apps which focuses on wiki generation, this skill is optimized for **code search and retrieval**.

## Installation

**Required: One-time setup (30 seconds)**

Before using any commands, create the persistent `.venv`:

```bash
```

This creates a persistent virtual environment for 10x faster execution (~8 seconds vs ~15-20 seconds per command).

## Commands

### 1. Index Directory

Index any directory into a knowledge graph using `--root`:

```bash

# Index current directory
uv run --directory {baseDir} cognee-memory index

# Index specific directory (recommended)
uv run --directory {baseDir} cognee-memory index --root /path/to/project

# Use named dataset to organize projects
uv run --directory {baseDir} cognee-memory index --root ~/project-a --dataset project_a

# Custom LLM model
uv run --directory {baseDir} cognee-memory index --root /path --model github_copilot/gpt-4o-mini
```

**Process:**
1. **Discovers files** matching configured extensions
2. **Filters** by size (50 bytes - 1MB by default)
3. **Adds files** to Cognee dataset
4. **Builds knowledge graph** (cognify step)

**Options:**
- `--root PATH` - Root directory to index (default: current directory)
- `--working-dir PATH` - Storage directory (default: ./cognee_storage)
- `--dataset NAME` - Dataset name (default: main)
- `--model NAME` - LLM model (default: github_copilot/gpt-4o)

**Example output:**
```
================================================================================
INDEXING REPOSITORY
================================================================================

📚 Indexing repository: my-project
   Path: /home/user/my-project
   Dataset: main
   Working directory: ./cognee_storage
   LLM: github_copilot/gpt-4o
   Embedding: github_copilot/text-embedding-3-small
   Rate Limiting: 30/min

🧹 Checking existing data...
   No existing data found

📁 Finding files to index...
   Found 173 files to index

📄 Adding files to Cognee...
   Progress: 10/173 files (8.3 files/sec)
   Progress: 20/173 files (9.1 files/sec)
   ...
   ✅ Files added in 21.3s

🧠 Building knowledge graph...
   (This may take several minutes with rate limiting...)
   ✅ Knowledge graph built in 187.5s

✅ Indexing complete!
   Indexed: 173 files
   Skipped: 0 files
   Errors: 0 files
   Total time: 208.8s
```

**Incremental Indexing:**
If you run `index` again, it will ask if you want to prune existing data or add incrementally.

### 2. Search

Search your indexed knowledge graph:

```bash

# Basic search
uv run --directory {baseDir} cognee-memory search "What is DML?"

# Specify search strategy
uv run --directory {baseDir} cognee-memory search "Find authentication code" --type CHUNKS

# Save results to file
uv run --directory {baseDir} cognee-memory search "Explain architecture" --output results.md

# Search specific dataset
uv run --directory {baseDir} cognee-memory search "query" --dataset my_dataset
```

**Options:**
- `query` - Your search query (required)
- `--working-dir PATH` - Storage directory with indexed data
- `--dataset NAME` - Dataset name (default: main)
- `--type TYPE` - Search strategy: SUMMARIES, CHUNKS, or GRAPH_COMPLETION (default)
- `--output FILE` - Save results to markdown file

**Example output:**
```
================================================================================
SEARCHING REPOSITORY
================================================================================

🔍 Searching: What is DML?
   Dataset: main
   Search type: GRAPH_COMPLETION

📊 Results:
   Found: 3 results
   Time: 2.34s

================================================================================
SEARCH RESULTS
================================================================================

--- Result 1 ---
DML (Device Modeling Language) is a domain-specific language used in Intel Simics for
modeling hardware devices. It provides constructs for defining registers, memory-mapped
I/O, and device behavior...

--- Result 2 ---
In the context of Simics, DML enables developers to create accurate hardware models that
can be used for software development, testing, and debugging without physical hardware...

--- Result 3 ---
DML includes features such as register banks, connect objects, attributes, and event
handling mechanisms to model complex hardware interactions...
```

## Search Strategies

Cognee provides three search strategies optimized for different use cases.

### Quick Reference

| Strategy | Best For | Speed | Use When |
|----------|----------|-------|----------|
| **GRAPH_COMPLETION** | General questions, explanations | Medium | "How does X work?" |
| **SUMMARIES** | High-level summaries, architecture | Medium | "What are the main components?" |
| **CHUNKS** | Semantic code search | Fast | "Show me authentication code" |
| **CHUNKS_LEXICAL** | Exact code matches | Fastest | "function named login" |
| **CODING_RULES** | Coding patterns, best practices | Fast | "error handling patterns" |

### GRAPH_COMPLETION (Default)

**Best for:** General questions, conceptual understanding, "how does X work?"

Uses the full knowledge graph to provide comprehensive, contextualized answers by traversing relationships between code elements.

**Examples:**
```bash
uv run --directory {baseDir} cognee-memory search "How does the authentication system work?"
uv run --directory {baseDir} cognee-memory search "Explain the data flow from API to database"
uv run --directory {baseDir} cognee-memory search "What are the main components of this system?"
```

**Pros:** Contextual answers, understands relationships  
**Cons:** Slower than CHUNKS, may not show exact code

### SUMMARIES

**Best for:** High-level summaries, architectural questions, patterns

Extracts key summaries and relationships from the knowledge graph, focusing on important concepts and connections.

**Examples:**
```bash
uv run --directory {baseDir} cognee-memory search "What are the key design patterns used?" --type SUMMARIES
uv run --directory {baseDir} cognee-memory search "Summarize the system architecture" --type SUMMARIES
uv run --directory {baseDir} cognee-memory search "What are the main dependencies?" --type SUMMARIES
```

**Pros:** Great for overviews, identifies patterns  
**Cons:** May miss implementation details

### CHUNKS

**Best for:** Finding specific code snippets semantically

Returns relevant code chunks using semantic search (meaning-based).

**Examples:**
```bash
uv run --directory {baseDir} cognee-memory search "Find authentication code" --type CHUNKS
uv run --directory {baseDir} cognee-memory search "Show me error handling" --type CHUNKS
uv run --directory {baseDir} cognee-memory search "database connection logic" --type CHUNKS
```

**Pros:** Fast, semantic understanding, finds related code  
**Cons:** May not find exact names

### CHUNKS_LEXICAL (Code-Specific)

**Best for:** Finding exact code matches by name (functions, classes, variables)

Returns code chunks using lexical search (exact text matching).

**Examples:**
```bash
uv run --directory {baseDir} cognee-memory search "function named authenticate" --type CHUNKS_LEXICAL
uv run --directory {baseDir} cognee-memory search "class UserManager" --type CHUNKS_LEXICAL
uv run --directory {baseDir} cognee-memory search "validate_token" --type CHUNKS_LEXICAL
```

**Pros:** Fastest, finds exact names, no ambiguity  
**Cons:** Must know exact names, no semantic understanding

### CODING_RULES (Code-Specific)

**Best for:** Finding coding patterns, conventions, and best practices

Searches for extracted coding rules and patterns from the codebase.

**Examples:**
```bash
uv run --directory {baseDir} cognee-memory search "What are the error handling patterns?" --type CODING_RULES
uv run --directory {baseDir} cognee-memory search "How should I handle authentication?" --type CODING_RULES
uv run --directory {baseDir} cognee-memory search "logging conventions" --type CODING_RULES
```

**Pros:** Learns from codebase, enforces consistency  
**Cons:** Requires code to have established patterns

### Choosing the Right Strategy

**Simple decision tree:**
- Want to understand how something works? → **GRAPH_COMPLETION**
- Want a high-level overview? → **SUMMARIES**
- Want to find code by meaning? → **CHUNKS**
- Want to find code by exact name? → **CHUNKS_LEXICAL**
- Want to find coding patterns? → **CODING_RULES**

## Configuration

### Default Settings

The skill uses sensible defaults optimized for GitHub Copilot Business:

| Setting | Default Value |
|---------|--------------|
| LLM Model | github_copilot/gpt-4o |
| Embedding Model | github_copilot/text-embedding-3-small |
| Embedding Dimensions | 1536 |
| API Key | oauth2 (GitHub Copilot) |
| Rate Limit (Embeddings) | 30 requests/minute |
| Rate Limit (LLM) | 30 requests/minute |
| Min File Size | 50 bytes |
| Max File Size | 1 MB |
| Dataset Name | main |

### File Extensions

By default, indexes these file types:
- `.py` - Python
- `.md` - Markdown
- `.txt` - Text
- `.dml` - Device Modeling Language
- `.c`, `.h` - C
- `.cpp`, `.hpp` - C++
- `.java` - Java
- `.js`, `.ts` - JavaScript/TypeScript

### Environment Variables

Override defaults with environment variables:

```bash
# Storage settings
export WORKING_DIR=/path/to/storage
export DATASET_NAME=my_dataset

# Model settings
export LLM_MODEL=github_copilot/gpt-4o-mini
export EMBEDDING_MODEL=github_copilot/text-embedding-3-small
export API_KEY=oauth2

# Rate limiting (adjust for your Copilot tier)
export EMBEDDING_RATE_LIMIT_REQUESTS=50
export EMBEDDING_RATE_LIMIT_INTERVAL=60
export LLM_RATE_LIMIT_REQUESTS=50
export LLM_RATE_LIMIT_INTERVAL=60

# File filtering
export MIN_FILE_SIZE=100
```

### Use Cases

### 1. Code Understanding
```bash

# Understand a new codebase
uv run --directory {baseDir} cognee-memory index --root /path/to/new-project
uv run --directory {baseDir} cognee-memory search "What does this project do?"
uv run --directory {baseDir} cognee-memory search "How is data processed?"
```

### 2. Bug Investigation
```bash

# Find relevant code for a bug
uv run --directory {baseDir} cognee-memory search "error handling in API layer" --type CHUNKS
uv run --directory {baseDir} cognee-memory search "Where is validation performed?"
```

### 3. Refactoring Planning
```bash

# Understand dependencies before refactoring
uv run --directory {baseDir} cognee-memory search "What depends on the User class?" --type SUMMARIES
uv run --directory {baseDir} cognee-memory search "How is authentication used across the codebase?"
```

### 4. Documentation
```bash

# Generate documentation summaries
uv run --directory {baseDir} cognee-memory search "List all public APIs" --output api-docs.md
uv run --directory {baseDir} cognee-memory search "Describe the configuration system" --output config-docs.md
```

### 5. Onboarding
```bash

# Help new team members
uv run --directory {baseDir} cognee-memory search "What are the main components?"
uv run --directory {baseDir} cognee-memory search "How do I add a new feature?"
uv run --directory {baseDir} cognee-memory search "What coding conventions are used?"
```

## Workflow Examples

### Complete Repository Analysis

```bash

# 2. Test environment
uv run --directory {baseDir} cognee-memory test

# 3. Index the repository
uv run --directory {baseDir} cognee-memory index

# 4. Ask high-level questions
uv run --directory {baseDir} cognee-memory search "What is the purpose of this project?" --type SUMMARIES

# 5. Dive into specifics
uv run --directory {baseDir} cognee-memory search "How does the main API work?"

# 6. Find implementations
uv run --directory {baseDir} cognee-memory search "show authentication code" --type CHUNKS
```

### Multiple Datasets

```bash

# Index different branches or versions
uv run --directory {baseDir} cognee-memory index --dataset main-branch
uv run --directory {baseDir} cognee-memory index --root ../feature-branch --dataset feature-branch

# Compare by searching each
uv run --directory {baseDir} cognee-memory search "authentication" --dataset main-branch
uv run --directory {baseDir} cognee-memory search "authentication" --dataset feature-branch
```

## Storage and Data Management

### Directory Structure

```
cognee_storage/
├── system/          # Cognee system files and metadata
│   ├── graph.db     # Knowledge graph database
│   └── config.json  # Configuration
└── data/            # Indexed document data
    └── datasets/    # Dataset storage
        └── main/    # Default dataset
```

### Managing Storage

```bash
# Check storage size
du -sh cognee_storage/

# Reset everything (start fresh)
rm -rf cognee_storage/

# Reset specific dataset
rm -rf cognee_storage/data/datasets/main/

# Backup indexed data
tar -czf cognee-backup.tar.gz cognee_storage/
```

### Incremental Updates

To add new files to existing index:
```bash
# Add new files (will ask about pruning)
uv run --directory {baseDir} cognee-memory index
# Answer "no" to pruning to keep existing data
```

## Troubleshooting

### Search Hangs or Times Out

**Problem:** Search command hangs indefinitely

**Cause:** Kuzu database lock from a previous crashed or hung process

**Solution:**
```bash
# Kill any existing cognee processes
pkill -f cognee

# Or find and kill specific process
ps aux | grep cognee
kill -9 <PID>

# Then retry search
uv run --directory {baseDir} cognee-memory search "query" --dataset your_dataset
```

**Prevention:**
- Use different `--working-dir` for concurrent access
- Use separate `--dataset` names for different projects
- Always use Ctrl+C to cleanly stop processes

### Database Lock Error

**Problem:** `RuntimeError: IO exception: Could not set lock on file`

**Cause:** Another process is using the Kuzu database

**Solution:**
```bash
# Check what's locking the database
lsof ~/path/to/cognee_storage/system/databases/cognee_graph_kuzu

# Kill the locking process
kill -9 <PID>
```

### Rate Limiting

**Problem:** Slow indexing due to rate limits

**Solution:**
```bash
# Increase rate limits if you have higher tier
export EMBEDDING_RATE_LIMIT_REQUESTS=100
export LLM_RATE_LIMIT_REQUESTS=100
```

### No Search Results

**Problem:** Search returns no results

**Solutions:**
1. Verify indexing completed successfully
2. Try different search type (--type CHUNKS)
3. Rephrase your query
4. Check dataset name matches

### Storage Issues

**Problem:** Permission denied or disk full

**Solution:**
```bash
# Use custom location with more space
uv run cognee-memory index --working-dir /mnt/large-disk/cognee
```

## Integration with Other Skills

### With pptx-creator
```bash

# Index codebase
uv run --directory {baseDir} cognee-memory index

# Extract summaries
uv run --directory {baseDir} cognee-memory search "system architecture" --output summaries.md

# Create presentation (use pptx-creator skill)
# ... convert summaries.md to presentation
```

### With lightrag-apps
```bash
# Use both for different purposes:
# - cognee-apps: Code search and Q&A
# - lightrag-apps: Wiki generation

uv run --directory {baseDir} cognee-memory index
uv run --directory lightrag-apps lightrag-apps/scripts/repowiki.py all
```

## Technical Details

### Dependencies (PEP 723)

Managed automatically via inline script metadata:
- `cognee>=0.1.0` - Knowledge graph framework
- `litellm>=1.76.0` - LLM provider abstraction
- `pyyaml>=6.0` - Configuration handling
- `python-dotenv>=1.0.0` - Environment variable support

### Architecture

```
cognee_memory.py
├── Config: Configuration management
├── RepositoryIndexer: File discovery and indexing
├── RepositorySearch: Search interface
└── CLI: Command-line interface
```

### Performance

- **Indexing speed:** ~10 files/second (depends on rate limits)
- **Search speed:** 1-3 seconds per query
- **Storage:** ~1-2MB per 100 files indexed
- **Memory:** ~500MB during indexing, ~100MB during search

## Comparison: Cognee vs LightRAG

| Feature | cognee-apps | lightrag-apps |
|---------|-------------|---------------|
| Primary use | Code search/Q&A | Wiki generation |
| Search strategies | 3 types (SUMMARIES, CHUNKS, GRAPH_COMPLETION) | 5 modes (global, local, mix, hybrid, naive) |
| Output | Search results | Hierarchical wiki pages |
| Incremental updates | Yes | No |
| Graph structure | Cognee knowledge graph | LightRAG knowledge graph |
| Best for | Interactive exploration | Documentation generation |

## See Also

- **[Cognee-OpenSpec](../../cognee-openspec/)** - Original implementation and advanced features
- **[GraphRAG-apps](../graphrag-apps/)** - Alternative knowledge graph skill
- **[LightRAG-apps](../lightrag-apps/)** - Wiki generation skill

## License

Apache-2.0 License - Copyright 2025 Google LLC

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review cognee-openspec documentation in `../../cognee-openspec/`
3. Check related skills: graphrag-apps, lightrag-apps
