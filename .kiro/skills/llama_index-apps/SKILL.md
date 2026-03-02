---
name: llama_index-apps
description: Index and search code repositories using LlamaIndex code graph (tree-sitter) and property graph (LLM-based entity extraction)
version: 1.0.0
author: Google LLC
license: Apache-2.0
tags: [llama-index, code-graph, property-graph, tree-sitter, knowledge-graph, code-search]
python: ">=3.10,<3.13"
---

# LlamaIndex Apps - Code Graph & Property Graph Skill

Two complementary graph tools built on LlamaIndex:

1. **code-graph** — Parses source code into a navigable scope hierarchy using tree-sitter. No LLM needed for parsing.
2. **property-graph** — Extracts typed entities and relations from any documents using an LLM. Persists as JSON with no external DB.

## code-graph

### Overview

`CodeHierarchyNodeParser` uses tree-sitter to parse source files into a tree of scopes (modules, classes, functions, methods). Each scope becomes a node. Parent nodes are "skeletonized" — child bodies are replaced with stub comments like:

```python
class MyClass:
    # Code replaced for brevity. See node_id <uuid>
```

This lets an LLM navigate large codebases lazily, only fetching the scope it needs.

### Commands

#### map — Generate a repo map

```bash
# Print repo map to stdout
uv run --directory {baseDir} code-graph map --root /path/to/project

# Save to file
uv run --directory {baseDir} code-graph map --root /path/to/project --output repo_map.md

# Limit depth
uv run --directory {baseDir} code-graph map --root /path/to/project --depth 2

# Different language
uv run --directory {baseDir} code-graph map --root /path/to/project --language typescript
```

Example output:
```
- my_project
  - my_module
    - MyClass
      - __init__
      - my_method
    - helper_function
```

#### query — Look up a scope by name or UUID

```bash
# By class or function name
uv run --directory {baseDir} code-graph query --root /path/to/project MyClass

# By method name
uv run --directory {baseDir} code-graph query --root /path/to/project my_method

# By UUID (from a 'Code replaced for brevity' stub)
uv run --directory {baseDir} code-graph query --root /path/to/project a1b2c3d4-...
```

Returns the skeletonized text of that scope. If the body was replaced with a stub, query the UUID to drill deeper.

#### inspect — List all parsed nodes

```bash
uv run --directory {baseDir} code-graph inspect --root /path/to/project
```

Shows every scope node with its UUID, scope path, file, and byte range.

### Supported Languages

| Language | Extensions |
|----------|-----------|
| python | .py |
| javascript | .js, .mjs |
| typescript | .ts, .tsx |
| java | .java |
| go | .go |
| rust | .rs |
| c | .c, .h |
| cpp | .cpp, .cc, .cxx, .hpp |
| ruby | .rb |
| c_sharp | .cs |

Language support is provided by `tree-sitter-language-pack`. For languages with `.scm` query files in the pack, scope detection is automatic. For others, `_DEFAULT_SIGNATURE_IDENTIFIERS` in the pack defines the rules.

### How it works

1. `SimpleDirectoryReader` loads source files with `filepath` metadata
2. `CodeHierarchyNodeParser` runs tree-sitter on each file, walking the AST recursively
3. Each scope matching `signature_identifiers` (or `.scm` queries) becomes a `TextNode`
4. Parent/child `NodeRelationship` links are wired between nodes
5. `_skeletonize_list` rewrites parent nodes, replacing child bodies with UUID stubs
6. `CodeHierarchyKeywordQueryEngine` indexes nodes by name, module, and UUID for lookup

## property-graph

### Overview

`PropertyGraphIndex` uses an LLM to extract typed entities and relations from documents, storing them in a `SimplePropertyGraphStore` (in-memory, JSON-persisted). No external graph database (Neo4j, etc.) is required.

### Commands

#### build — Extract and persist a property graph

```bash
# From a directory (simple extractor, GitHub Copilot)
uv run --directory {baseDir} property-graph build docs/

# From a single file
uv run --directory {baseDir} property-graph build paper.md

# Custom storage directory
uv run --directory {baseDir} property-graph build docs/ --output my_graph/

# Dynamic extractor (infers entity/relation types)
uv run --directory {baseDir} property-graph build docs/ --extractor dynamic

# Implicit extractor (no LLM, noun chunks)
uv run --directory {baseDir} property-graph build docs/ --extractor implicit

# OpenAI model
uv run --directory {baseDir} property-graph build docs/ --model gpt-4o-mini
```

#### query — Retrieve relevant nodes

```bash
# Default storage dir
uv run --directory {baseDir} property-graph query "What are the main components?"

# Custom storage dir
uv run --directory {baseDir} property-graph query "Find all Person entities" --storage-dir my_graph/
```

#### inspect — Show nodes and triplets

```bash
uv run --directory {baseDir} property-graph inspect

uv run --directory {baseDir} property-graph inspect --storage-dir my_graph/
```

### Extractors

| Extractor | LLM | Description |
|-----------|-----|-------------|
| `simple` (default) | Yes | Extracts (subject, relation, object) triples |
| `implicit` | No | Noun-chunk co-occurrence, fast but shallow |
| `dynamic` | Yes | LLM infers entity types and relation types |

### Models

**GitHub Copilot (default, no API key needed):**
```bash
--model github_copilot/gpt-4o        # default
--model github_copilot/gpt-4o-mini   # faster, cheaper
```

**OpenAI (requires OPENAI_API_KEY):**
```bash
export OPENAI_API_KEY=sk-...
--model gpt-4o-mini
--model gpt-4o
```

### Storage

The graph is persisted as a single JSON file:
```
pg_storage/
└── property_graph.json
```

To reset:
```bash
rm -rf pg_storage/
```

## Comparison

| Feature | code-graph | property-graph |
|---------|-----------|----------------|
| Input | Source code files | Any text/documents |
| Parsing | tree-sitter (structural) | LLM extraction (semantic) |
| LLM for building | Not required | Required (except `implicit`) |
| Output | Scope hierarchy + repo map | Typed entity/relation graph |
| Storage | Stateless (rebuilt from source) | JSON-persisted |
| Best for | Code navigation, repo maps | Knowledge extraction from docs |

## Use Cases

### Code navigation with code-graph
```bash
# Understand a new codebase
uv run --directory {baseDir} code-graph map --root ~/new-project --output repo_map.md

# Find a specific function
uv run --directory {baseDir} code-graph query --root ~/new-project authenticate_user

# Drill into a skeletonized scope
uv run --directory {baseDir} code-graph query --root ~/new-project <uuid-from-stub>
```

### Knowledge extraction with property-graph
```bash
# Extract knowledge from research papers
uv run --directory {baseDir} property-graph build papers/ --extractor dynamic

# Query relationships
uv run --directory {baseDir} property-graph query "What methods are described?"

# Inspect what was extracted
uv run --directory {baseDir} property-graph inspect
```

## See Also

- [LlamaIndex CodeHierarchyNodeParser](https://github.com/run-llama/llama_index/tree/main/llama-index-packs/llama-index-packs-code-hierarchy)
- [LlamaIndex PropertyGraphIndex](https://docs.llamaindex.ai/en/stable/module_guides/indexing/lpg_index_guide/)
- [tree-sitter-language-pack](https://github.com/Goldziher/tree-sitter-language-pack)
