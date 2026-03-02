# GraphRAG Memory - Quick Start Guide

Get started with GraphRAG knowledge graph indexing in 5 minutes.

## Prerequisites

- `uv` package manager installed
- GitHub Copilot subscription OR OpenAI API key

## Setup (One-Time)

```bash
# Test setup
uv run --directory {baseDir} graphrag-memory test
```

## Basic Workflow

### 1. Initialize Project

```bash
# Navigate to your project directory
cd /path/to/your-project

# Initialize GraphRAG
uv run --directory {baseDir} graphrag-memory init
```

This creates:
- `settings.yaml` - Configuration
- `prompts/` - LLM prompt templates
- `input/` - Document directory
- `output/` - Knowledge graph storage
- `cache/` - LLM response cache

### 2. Add Documents

```bash
# Copy your markdown files to input/
cp docs/*.md input/
```

### 3. Index Documents

```bash
# Index from a directory
uv run --directory {baseDir} graphrag-memory index --input openspec-memories

# Or index from the input/ folder
uv run --directory {baseDir} graphrag-memory index --input input/
```

This will:
- Extract entities and relationships using LLM
- Build knowledge graph
- Create embeddings
- Detect communities

**Note:** Indexing can take 5-60 minutes depending on document size and uses LLM extensively.

### 4. Query Knowledge Graph

```bash
# Local search - detailed, entity-focused
uv run --directory {baseDir} graphrag-memory query \
  "How to implement timer?" \
  --method local

# Global search - high-level overview
uv run --directory {baseDir} graphrag-memory query \
  "What are the main concepts?" \
  --method global
```

### 5. Check Status

```bash
uv run --directory {baseDir} graphrag-memory status
```

## Configuration

### Using GitHub Copilot (Default)

No configuration needed! The default `settings.yaml` uses GitHub Copilot.

### Using OpenAI

Edit `settings.yaml`:

```yaml
models:
  default_chat_model:
    model_provider: openai
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o
```

Set environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

## Query Methods

- **Local search** - Best for specific questions about entities
- **Global search** - Best for broad questions about themes
- **Drift search** - Best for exploratory analysis

## Cost Warning

⚠️ GraphRAG uses LLMs extensively. Estimated costs:
- Small (10-20 files): $5-10
- Medium (50-100 files): $20-50
- Large (200+ files): $100+

**Start small!** Test with 5-10 files first.

## Troubleshooting

### Project not found
```bash
# Make sure you initialized first
uv run --directory {baseDir} graphrag-memory init
```

### No indexed data
```bash
# Run indexing first
uv run --directory {baseDir} graphrag-memory index --input openspec-memories
```

## Next Steps

- Read [SKILL.md](SKILL.md) for detailed documentation
- Adjust `settings.yaml` for your needs
- Experiment with different query methods
- Check [GraphRAG documentation](https://microsoft.github.io/graphrag/)
