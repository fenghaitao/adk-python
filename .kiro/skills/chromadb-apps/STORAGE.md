# Storage Location Guide

This document explains where the `.chromadb` folder should be located and why.

## TL;DR

**Store `.chromadb` in your project directory, not in the skill directory.**

```bash
# ✅ Good: Index from your project directory
cd /path/to/your-project
uv run --directory /path/to/.kiro/skills/chromadb-apps chromadb-memory index docs/
# Creates: /path/to/your-project/.chromadb/

# ❌ Bad: Don't put it in the skill directory
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir {baseDir}/.chromadb
```

## Why Project Directory?

### 1. Separation of Concerns

- **Skill directory** = Tool/code (shared across projects)
- **Project directory** = Data (specific to each project)

### 2. Easy Management

```bash
# Delete index for one project
cd /path/to/project-a
rm -rf .chromadb/

# Doesn't affect other projects
cd /path/to/project-b
# .chromadb/ still intact
```

### 3. Portability

- Skill directory stays clean
- Can move/copy skill without carrying project data
- Can share skill with others without exposing your indexed data

### 4. Multiple Projects

Each project gets its own index:

```
/home/user/
├── project-a/
│   ├── docs/
│   └── .chromadb/          # Index for project-a
├── project-b/
│   ├── docs/
│   └── .chromadb/          # Index for project-b
└── .kiro/skills/chromadb-apps/
    ├── chromadb_apps/      # Skill code (shared)
    └── .venv/              # Dependencies (shared)
```

## Default Behavior

By default, chromadb-memory creates `.chromadb` in the **current working directory**:

```bash
# If you run from project directory
cd /path/to/my-project
uv run --directory /path/to/.kiro/skills/chromadb-apps chromadb-memory index docs/
# Creates: /path/to/my-project/.chromadb/

# If you run from skill directory (not recommended)
cd /path/to/.kiro/skills/chromadb-apps
uv run --directory . chromadb-memory index /path/to/my-project/docs/
# Creates: /path/to/.kiro/skills/chromadb-apps/.chromadb/ (pollutes skill dir)
```

## Custom Locations

### Shared Index for Related Projects

```bash
# Multiple related projects share one index
uv run --directory {baseDir} chromadb-memory index project-a/docs/ --persist-dir ~/shared-indexes/my-suite
uv run --directory {baseDir} chromadb-memory index project-b/docs/ --persist-dir ~/shared-indexes/my-suite

# Search across all
uv run --directory {baseDir} chromadb-memory search "query" --persist-dir ~/shared-indexes/my-suite
```

### Project-Specific Subdirectory

```bash
# Keep indexes in a dedicated subdirectory
cd /path/to/my-project
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir ./.indexes/chromadb

# Easier to .gitignore
echo ".indexes/" >> .gitignore
```

### Temporary/Scratch Index

```bash
# Use /tmp for temporary indexes
uv run --directory {baseDir} chromadb-memory index docs/ --persist-dir /tmp/chromadb-scratch

# Automatically cleaned up on reboot
```

## .gitignore Recommendations

Add to your project's `.gitignore`:

```gitignore
# ChromaDB indexes (regenerate as needed)
.chromadb/

# Or if using custom location
.indexes/
```

**Why ignore?**
- Indexes can be regenerated from source documents
- Large binary files (embeddings)
- Not useful for code review
- Different per developer

## Best Practices Summary

1. **Always run from project directory** - Let default behavior work for you
2. **One index per project** - Unless projects are closely related
3. **Add to .gitignore** - Indexes are derived data
4. **Use --persist-dir for special cases** - Shared indexes, custom locations
5. **Keep skill directory clean** - No project data in skill directory

## Troubleshooting

### "Can't find my index"

Check your current directory when you indexed:

```bash
# Where did I create the index?
pwd  # Check current directory
ls -la .chromadb/  # Is it here?

# Search with explicit path
uv run --directory {baseDir} chromadb-memory search "query" --persist-dir /path/to/actual/.chromadb
```

### "Index is huge"

ChromaDB stores embeddings (vectors) which can be large:

```bash
# Check size
du -sh .chromadb/

# If too large, consider:
# 1. Index only essential documents
# 2. Use smaller chunk size
# 3. Filter by file type
```

### "Multiple projects sharing index"

If you want multiple projects to share an index:

```bash
# Create shared location
mkdir -p ~/shared-indexes/my-suite

# Index all projects there
uv run --directory {baseDir} chromadb-memory index project-a/docs/ --persist-dir ~/shared-indexes/my-suite
uv run --directory {baseDir} chromadb-memory index project-b/docs/ --persist-dir ~/shared-indexes/my-suite

# Search across all
uv run --directory {baseDir} chromadb-memory search "query" --persist-dir ~/shared-indexes/my-suite
```

## See Also

- [SKILL.md](./SKILL.md) - Main documentation
- [Configuration section](./SKILL.md#configuration) - Default settings
- [Storage and Data Management](./SKILL.md#storage-and-data-management) - Managing indexes
