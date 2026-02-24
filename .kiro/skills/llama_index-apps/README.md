# LlamaIndex Apps - Code Graph & Property Graph Skill

Two graph tools powered by LlamaIndex:

- **code-graph** — tree-sitter based code scope hierarchy (no LLM needed for parsing)
- **property-graph** — LLM-based typed entity/relation extraction from documents

## Quick Start

```bash
# One-time setup
uv sync --directory {baseDir}

# Parse a Python codebase and print its repo map
uv run --directory {baseDir} code-graph map --root /path/to/project

# Build a property graph from documents
uv run --directory {baseDir} property-graph build docs/ --output pg_storage/

# Query the property graph
uv run --directory {baseDir} property-graph query "Find all Agent entities"
```

## code-graph

Parses source code into a navigable scope hierarchy using tree-sitter.
No LLM required for parsing — purely structural.

### Commands

```bash
# Generate a repo map (markdown outline of all scopes)
uv run --directory {baseDir} code-graph map --root /path/to/project --language python

# Save repo map to file
uv run --directory {baseDir} code-graph map --root /path/to/project --output repo_map.md

# Look up a class or function by name
uv run --directory {baseDir} code-graph query --root /path/to/project MyClass

# Look up by UUID (from a 'Code replaced for brevity' stub)
uv run --directory {baseDir} code-graph query --root /path/to/project <uuid>

# List all parsed scope nodes with metadata
uv run --directory {baseDir} code-graph inspect --root /path/to/project
```

### Supported Languages

python, javascript, typescript, java, go, rust, c, cpp, ruby, c_sharp

## property-graph

Extracts typed entities and relations from documents using an LLM.
Persists as JSON — no external graph database required.

### Commands

```bash
# Build from a directory of documents (simple extractor, GitHub Copilot)
uv run --directory {baseDir} property-graph build docs/

# Build with dynamic extractor (infers entity/relation types)
uv run --directory {baseDir} property-graph build docs/ --extractor dynamic

# Build with implicit extractor (no LLM, uses noun chunks)
uv run --directory {baseDir} property-graph build docs/ --extractor implicit

# Query the graph
uv run --directory {baseDir} property-graph query "What are the main components?"

# Inspect nodes and triplets
uv run --directory {baseDir} property-graph inspect
```

### Extractors

| Extractor | LLM needed | Best for |
|-----------|-----------|----------|
| `simple` (default) | Yes | General triple extraction |
| `implicit` | No | Fast, noun-chunk based |
| `dynamic` | Yes | Richer typed entities/relations |

## Files

- `SKILL.md` — complete documentation
- `pyproject.toml` — dependencies
- `llama_index_apps/code_graph.py` — code-graph CLI
- `llama_index_apps/property_graph.py` — property-graph CLI
