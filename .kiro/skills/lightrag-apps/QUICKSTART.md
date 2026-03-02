# RepoWiki - Quick Start Guide

Generate comprehensive wiki documentation from your code repository in minutes.

## Prerequisites

- `uv` package manager installed
- GitHub Copilot subscription (or OpenAI API key)

## Setup (One-Time)

```bash
# Test setup
uv run --directory {baseDir} repowiki test
```

## Generate Wiki (All-in-One)

```bash
# Navigate to your repository
cd /path/to/your/project

# Generate extended wiki (~19 pages, recommended)
uv run --directory {baseDir} repowiki all --extended

# Or basic wiki (~13 pages, faster)
uv run --directory {baseDir} repowiki all
```

That's it! Your wiki will be in `./wiki_docs/`

## Two-Step Process (Optional)

If you prefer to index and generate separately:

### 1. Index Repository

```bash
cd /path/to/your/project
uv run --directory {baseDir} repowiki index
```

This creates a knowledge graph in `./repowiki_storage/`

### 2. Generate Wiki

```bash
# Extended wiki (~19 pages)
uv run --directory {baseDir} repowiki generate --extended

# Or basic wiki (~13 pages)
uv run --directory {baseDir} repowiki generate
```

## Wiki Structure

### Base Wiki (~13 pages)
- Home page
- Overview & architecture
- Design decisions

### Extended Wiki (~19 pages)
- Home page
- Overview & architecture
- Getting started (installation, configuration)
- Core concepts (components, workflows)
- API reference (public API, examples)
- Development (dependencies, testing, extensions)

## Configuration

### Default (GitHub Copilot)

Works out of the box with GitHub Copilot - no configuration needed!

### Custom Model

```bash
# Use different model
uv run --directory {baseDir} repowiki all --model gpt-4o-mini --extended

# Or set environment variable
export LLM_MODEL="gpt-4o-mini"
uv run --directory {baseDir} repowiki all --extended
```

## Performance

| Mode | Pages | Time | Cost |
|------|-------|------|------|
| Base | ~13 | 2-3 min | FREE (with Copilot) |
| Extended | ~19 | 5-10 min | FREE (with Copilot) |

## Examples

### Document Your Project
```bash
cd ~/my-project
uv run --directory ~/.kiro/skills/lightrag-apps repowiki all --extended
```

### Document Open Source Project
```bash
git clone https://github.com/user/project
cd project
uv run --directory ~/.kiro/skills/lightrag-apps repowiki all --extended
```

### Re-generate After Changes
```bash
# Re-index
uv run --directory {baseDir} repowiki index

# Generate fresh wiki
uv run --directory {baseDir} repowiki generate --extended
```

## Troubleshooting

### Check Setup
```bash
uv run --directory {baseDir} repowiki test
```

### Repository Not Found
```bash
# Specify path explicitly
uv run --directory {baseDir} repowiki index --repo /full/path/to/project
```

## Next Steps

- Read [SKILL.md](SKILL.md) for detailed documentation
- Customize output directory: `--output ./custom-wiki`
- Try different query modes for different sections
- Integrate with CI/CD for automatic wiki updates

## Output

After generation:
```
repowiki_storage/     # Knowledge graph (internal)
wiki_docs/            # Your wiki documentation
  ├── README.md       # Start here!
  ├── 01-overview/
  ├── 02-getting-started/
  └── ...
```

Open `wiki_docs/README.md` in your browser or editor to start exploring!
