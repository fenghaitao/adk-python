# RepoWiki - LightRAG Wiki Generator

Generate comprehensive hierarchical wiki documentation from any code repository using LightRAG knowledge graphs.

## What is RepoWiki?

RepoWiki uses LightRAG to build a knowledge graph from your code repository and generates well-structured, hierarchical wiki documentation. It understands your code's structure, relationships, and context to create comprehensive documentation automatically.

## Quick Links

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [SKILL.md](SKILL.md) - Complete documentation
- [LightRAG](https://github.com/HKUDS/LightRAG) - Knowledge graph framework

## Installation

```bash
# One-time setup
uv sync --directory .kiro/skills/lightrag-apps
```

## Basic Usage

```bash
# Navigate to your repository
cd /path/to/your/project

# Generate wiki
uv run --directory .kiro/skills/lightrag-apps repowiki all --extended
```

## Features

✅ Works with any repository  
✅ Auto-detects repository name  
✅ Uses GitHub Copilot by default (FREE)  
✅ Hierarchical organization (3-4 levels deep)  
✅ Multiple query modes (global, local, mix, hybrid, naive)  
✅ Persistent .venv for fast execution  
✅ Breadcrumb navigation  
✅ Category indexes

## Wiki Modes

### Base Mode (~13 pages, 2-3 min)
- Home page
- Overview & architecture
- Design decisions

### Extended Mode (~19 pages, 5-10 min, recommended)
- Home page
- Overview & architecture
- Getting started
- Core concepts
- API reference
- Development guide

## When to Use RepoWiki

**Use RepoWiki when:**
- You need comprehensive documentation for a codebase
- You want hierarchical, well-organized wiki structure
- You have GitHub Copilot (FREE) or OpenAI API access
- You want to understand code relationships and architecture

**Use other tools when:**
- You need simple API docs → Use docstring generators
- You need quick Q&A → Use ChromaDB-apps
- You need complex reasoning → Use GraphRAG-apps

## Configuration

### Default (GitHub Copilot)
Works out of the box - no API key needed!

### Custom Model
```bash
export LLM_MODEL="gpt-4o-mini"
uv run --directory .kiro/skills/lightrag-apps repowiki all --extended
```

## Performance

- **Indexing**: First-time indexing may take longer for large repos
- **Generation**: ~30 seconds with warm cache
- **Parallelism**: Optimized for GitHub Copilot Business (48/96/48 concurrent)

## Migration from PEP 723

This skill was migrated from PEP 723 inline dependencies to `pyproject.toml` for:
- Persistent virtual environment (faster execution)
- Better dependency management
- Consistent with other skills

Old usage: `uv run scripts/repowiki.py`  
New usage: `uv run --directory .kiro/skills/lightrag-apps repowiki`

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [SKILL.md](SKILL.md) - Complete documentation with all features
- [pyproject.toml](pyproject.toml) - Package configuration

## Examples

### Document Your Project
```bash
cd ~/my-project
uv run --directory ~/.kiro/skills/lightrag-apps repowiki all --extended
```

### Document Open Source Project
```bash
git clone https://github.com/user/awesome-project
cd awesome-project
uv run --directory ~/.kiro/skills/lightrag-apps repowiki all --extended
```

### CI/CD Integration
```yaml
- name: Generate Wiki
  run: |
    uv sync --directory .kiro/skills/lightrag-apps
    uv run --directory .kiro/skills/lightrag-apps repowiki all --extended
    
- name: Deploy Wiki
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./wiki_docs
```

## Support

For issues or questions:
1. Check [SKILL.md](SKILL.md) troubleshooting section
2. Review [LightRAG documentation](https://github.com/HKUDS/LightRAG)
3. Open an issue in the repository

## Technical Details

Built with:
- LightRAG - Knowledge graph framework
- GitHub Copilot models - LLM and embeddings
- NetworkX - Graph operations
- Nano-VectorDB - Vector storage

Architecture:
1. Indexer scans repository and builds knowledge graph
2. Generator queries graph with multiple modes
3. Wiki builder creates hierarchical documentation
