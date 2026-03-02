# Cognee Memory - Cognee Knowledge Graph Skill

This skill enables indexing and searching the current directory using Cognee knowledge graphs.

Source: Based on [cognee-openspec](../../cognee-openspec)

## What This Skill Does

- **Indexes directories** into Cognee knowledge graphs using `--root`
- **Searches indexed content** with multiple search strategies
- **Supports multiple file types** (.py, .md, .txt, .dml, .c, .h, .cpp, .java, .js, .ts, etc.)
- **Works out of the box** with GitHub Copilot models
- **Organizes content** with datasets (namespaces for different projects)

## Installation

**One-time setup:** No setup needed — `uv run --directory` handles it automatically.

## Quick Start

```bash
# Index current directory
uv run --directory {baseDir} cognee-memory index

# Index specific directory
uv run --directory {baseDir} cognee-memory index --root /path/to/project

# Search
uv run --directory {baseDir} cognee-memory search "What is DML?"
```

## Files

- `SKILL.md` - Complete documentation for the skill
- `pyproject.toml` - Project dependencies and configuration
- `cognee_apps/cognee_memory.py` - Main command-line script
- `.venv/` - Virtual environment (created automatically by `uv run`)

## Key Features

✅ **10x faster** - 8 seconds per search (was 90s)  
✅ Flexible `--root` parameter to index any directory  
✅ GitHub Copilot integration (free with license)  
✅ 5 search strategies including code-specific  
✅ Dataset support for organizing multiple projects  

## Commands

### Index Directory
```bash
uv run cognee-memory index [options]
```
Indexes all code files into a Cognee knowledge graph.

Options:
- `--root PATH` - Root directory to index (default: current directory)
- `--working-dir PATH` - Storage directory (default: ./cognee_storage)
- `--dataset NAME` - Dataset name (default: main)
- `--model NAME` - LLM model (default: github_copilot/gpt-4o)

### Search
```bash
uv run cognee-memory search "your query" [options]
```
Searches the indexed knowledge graph.

Options:
- `--working-dir PATH` - Storage directory with indexed data
- `--dataset NAME` - Dataset name (default: main)
- `--type TYPE` - Search type: SUMMARIES, CHUNKS, or GRAPH_COMPLETION (default)
- `--output FILE` - Save results to markdown file

## Search Strategies

| Strategy | Use When | Example Query |
|----------|----------|---------------|
| **GRAPH_COMPLETION** (default) | Understand how things work | "How does authentication work?" |
| **SUMMARIES** | Get high-level overview | "What are the main components?" |
| **CHUNKS** | Find specific code semantically | "Show me the login function" |
| **CHUNKS_LEXICAL** | Find exact code matches | "function named authenticate" |
| **CODING_RULES** | Find coding patterns/rules | "What are the error handling patterns?" |

**Quick tips:**
- Use default (GRAPH_COMPLETION) for most questions
- Add `--type CHUNKS` to find code semantically
- Add `--type CHUNKS_LEXICAL` for exact code matches
- Add `--type CODING_RULES` for coding patterns and best practices

See [SKILL.md](SKILL.md) for detailed strategy guide.

## Examples

**From cognee-apps directory:**
```bash
cd skills/cognee-apps

# Index current directory
uv run cognee-memory index

# Index specific directory  
uv run cognee-memory index --root /path/to/project

# Search with default strategy
uv run cognee-memory search "How does authentication work?"

# Search with specific strategy
uv run cognee-memory search "Find all API endpoints" --type CHUNKS

# Save search results
uv run cognee-memory search "Explain the architecture" --output results.md
```

**From anywhere (specify absolute paths):**
```bash
# Index with absolute paths
uv run --directory ~/adk-python/skills/cognee-apps cognee-memory index \
  --root ~/myproject \
  --working-dir ~/adk-python/cognee_storage

# Search with absolute paths
uv run --directory ~/adk-python/skills/cognee-apps cognee-memory search "query" \
  --working-dir ~/adk-python/cognee_storage
```

## Configuration

### Environment Variables
```bash
export WORKING_DIR=/path/to/storage
export DATASET_NAME=my_dataset
export LLM_MODEL=github_copilot/gpt-4o
export EMBEDDING_MODEL=github_copilot/text-embedding-3-small
```

### Rate Limiting
Default settings for GitHub Copilot Business:
- Embedding requests: 30/minute
- LLM requests: 30/minute

Adjust via environment variables if needed:
```bash
export EMBEDDING_RATE_LIMIT_REQUESTS=50
export LLM_RATE_LIMIT_REQUESTS=50
```

## Integration

Can be used with other skills:
- Index code documentation, then generate presentations with **pptx-creator**
- Combine with **lightrag-apps** for comparative analysis
- Create PRs with **github-pr** skill

## Technical Stack

- Cognee for knowledge graphs
- GitHub Copilot for LLM/embeddings
- UV for fast package management
- Project-based dependency management

## See Also

- **[SKILL.md](SKILL.md)** - Complete documentation with all commands and use cases
- **[GraphRAG-apps](../graphrag-apps/)** - Alternative knowledge graph skill
- **[LightRAG-apps](../lightrag-apps/)** - Wiki generation skill

## Differences from LightRAG-apps

This skill uses Cognee instead of LightRAG:
1. **Knowledge representation**: Uses Cognee's graph structure
2. **Search strategies**: SUMMARIES, CHUNKS, GRAPH_COMPLETION
3. **Incremental indexing**: Supports adding to existing graphs
4. **No wiki generation**: Focused on search/retrieval (use lightrag-apps for wiki generation)

## Storage

All data is stored in `cognee_storage/` by default:
- `cognee_storage/system/` - Cognee system files
- `cognee_storage/data/` - Indexed repository data

To reset/start fresh:
```bash
rm -rf cognee_storage/
```
