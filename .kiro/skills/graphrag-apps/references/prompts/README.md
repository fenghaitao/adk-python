# GraphRAG Prompt Templates

This directory contains production-ready prompt templates for GraphRAG knowledge graph construction and querying.

## Source

These prompts are copied from `graphrag/openspec_graphrag/prompts/` and represent production-tested templates that have been used successfully for document analysis.

## Prompts Included

### Entity & Relationship Extraction
- **extract_graph.txt** (120 lines) - Main entity and relationship extraction prompt with examples
- **extract_claims.txt** (51 lines) - Extract claims and assertions from text
- **summarize_descriptions.txt** (14 lines) - Summarize entity descriptions

### Community Reports
- **community_report_graph.txt** (148 lines) - Generate reports from graph structure
- **community_report_text.txt** (95 lines) - Generate reports from text content

### Search Prompts
- **local_search_system_prompt.txt** (63 lines) - Local search over entities and relationships
- **global_search_map_system_prompt.txt** (79 lines) - Map phase of global search
- **global_search_reduce_system_prompt.txt** (75 lines) - Reduce phase of global search
- **global_search_knowledge_system_prompt.txt** (3 lines) - Knowledge retrieval prompt
- **basic_search_system_prompt.txt** (67 lines) - Basic search functionality

### Drift Search
- **drift_search_system_prompt.txt** (67 lines) - Drift search system prompt
- **drift_reduce_prompt.txt** (60 lines) - Drift search reduce phase

### Utilities
- **question_gen_system_prompt.txt** (22 lines) - Generate questions from content

## Usage

These prompts are automatically copied to your GraphRAG project when you run:

```bash
uv run scripts/graphrag_memory.py init
```

The prompts will be placed in your project's `prompts/` directory.

## Customization

You can customize these prompts for your specific domain:

1. Copy the prompts from your initialized project's `prompts/` directory
2. Modify them to include domain-specific instructions
3. Add examples relevant to your use case
4. Adjust entity types, relationship types, etc.

## Format

All prompts follow the GraphRAG prompt format:
- Clear goal and instructions
- Examples where applicable
- Structured output format specifications
- Delimiter definitions for parsing

## Total Size

864 lines of carefully crafted LLM instructions across 13 prompt files.
