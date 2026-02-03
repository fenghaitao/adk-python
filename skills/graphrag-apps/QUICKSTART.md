# GraphRAG Memory - Quick Start Guide

Get started with GraphRAG Memory in 5 minutes!

## Prerequisites

- Python 3.10-3.12
- `uv` package manager (or `pip`)
- GitHub Copilot access OR OpenAI API key

## Installation

No installation needed! The script uses PEP 723 inline dependencies.

```bash
# Just run with uv
uv run skills/graphrag-apps/scripts/graphrag_memory.py --help
```

## Quick Start (4 Steps)

### Step 1: Verify Installation

```bash
cd /path/to/your/project
uv run skills/graphrag-apps/scripts/graphrag_memory.py test
```

**Expected output:**
```
🧪 Testing GraphRAG Memory Skill...
✅ GraphRAG import: OK
✅ YAML import: OK
✅ Typer import: OK
✅ All dependencies available!
```

### Step 2: Initialize Project

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py init
```

This creates:
- `settings.yaml` - Configuration file
- `prompts/` - LLM prompt templates
- `input/` - Place markdown files here
- `output/` - Indexed graph data
- `cache/` - LLM response cache

### Step 3: Add Documents and Index

```bash
# Copy markdown files to input/ OR use --input flag
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input openspec-memories
```

**What happens:**
- Chunks documents into manageable pieces
- Extracts entities and relationships using LLM
- Builds knowledge graph
- Creates embeddings for vector search
- Detects communities for hierarchical understanding

**Time:** ~5-15 minutes depending on data size and LLM speed

### Step 4: Query

```bash
# Local search - detailed answers about specific entities
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "How to implement timer in DML?"

# Global search - high-level overview
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "What are the main concepts?" --method global
```

## Configuration

### Using GitHub Copilot (Recommended)

The default `settings.yaml` uses GitHub Copilot:

```yaml
models:
  default_chat_model:
    model_provider: github_copilot
    model: gpt-4o
    
  default_embedding_model:
    model_provider: github_copilot
    model: text-embedding-3-small
```

No API key needed - OAuth2 authentication is automatic!

### Using OpenAI

Edit `settings.yaml`:

```yaml
models:
  default_chat_model:
    model_provider: openai
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o
    
  default_embedding_model:
    model_provider: openai
    api_key: ${OPENAI_API_KEY}
    model: text-embedding-3-small
```

Set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

## Query Methods

### Local Search
Best for specific, detailed questions about entities.

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py query \
  "What are the best practices for DML register access?" \
  --method local
```

**Use when:**
- Asking about specific entities or concepts
- Need detailed, cited information
- Want to see relationships between entities

### Global Search
Best for broad, thematic questions.

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py query \
  "What are the main architectural patterns in the codebase?" \
  --method global
```

**Use when:**
- Want high-level overview
- Asking about themes or trends
- Need summary across entire dataset

### Drift Search
Best for exploratory analysis.

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py query \
  "Explain the testing methodology" \
  --method drift
```

**Use when:**
- Exploring unfamiliar domain
- Want contextual connections
- Open-ended investigation

## Troubleshooting

### Dependencies downloading slowly?

First run downloads GraphRAG and dependencies (~200MB). Subsequent runs are instant.

```bash
# The script uses uv run with inline dependencies (PEP 723)
# No manual installation needed
```

### "No GraphRAG project found" error?

```bash
# Initialize first
uv run skills/graphrag-apps/scripts/graphrag_memory.py init

# Or specify root directory
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "..." --root ./my_project
```

### "No indexed data found" error?

```bash
# Run indexing first
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input openspec-memories
```

### LLM rate limits?

Edit `settings.yaml` to adjust:

```yaml
models:
  default_chat_model:
    concurrent_requests: 5  # Lower this
    requests_per_minute: 30  # Lower this
```

### Indexing takes too long?

For large datasets:
1. Reduce chunk size in `settings.yaml`
2. Disable claims extraction (already disabled by default)
3. Use faster LLM model (e.g., gpt-3.5-turbo)

## Project Structure

After initialization:

```
.
├── settings.yaml          # Main configuration
├── prompts/              # LLM prompt templates
│   ├── extract_graph.txt
│   ├── community_report.txt
│   └── local_search_system_prompt.txt
├── input/                # Your markdown files
├── output/               # Generated knowledge graph
│   └── lancedb/         # Vector database
├── cache/                # LLM response cache (saves money!)
└── logs/                 # Indexing logs
```

## Advanced Usage

### Check Project Status

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py status
```

Shows:
- Settings file location
- Number of input files
- Indexed data status
- Cache size

### Verbose Output

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input docs/ --verbose
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "..." --verbose
```

### Custom Root Directory

```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py init --root ./my_kb
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --root ./my_kb --input docs/
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "..." --root ./my_kb
```

## Next Steps

1. **Read full docs**: `skills/graphrag-apps/SKILL.md`
2. **Tune prompts**: Edit files in `prompts/` directory
3. **Optimize settings**: Adjust `settings.yaml` for your use case

## Cost Considerations

⚠️ **Warning**: GraphRAG indexing uses LLMs extensively and can be expensive!

**Estimated costs** (using GPT-4o):
- Small dataset (10-20 files, ~100KB): ~$5-10
- Medium dataset (50-100 files, ~500KB): ~$20-50
- Large dataset (200+ files, ~2MB): ~$100+

**Cost-saving tips:**
1. Use cheaper model (gpt-3.5-turbo) for initial testing
2. Enable caching (on by default) to avoid re-processing
3. Start small - test with 5-10 files first
4. Use GitHub Copilot (included in subscription)

## Summary

```bash
# 1. Test
uv run skills/graphrag-apps/scripts/graphrag_memory.py test

# 2. Initialize
uv run skills/graphrag-apps/scripts/graphrag_memory.py init

# 3. Index
uv run skills/graphrag-apps/scripts/graphrag_memory.py index --input openspec-memories

# 4. Query
uv run skills/graphrag-apps/scripts/graphrag_memory.py query "your question"

# 5. Status
uv run skills/graphrag-apps/scripts/graphrag_memory.py status
```

That's it! You're ready to use GraphRAG Memory. 🚀
