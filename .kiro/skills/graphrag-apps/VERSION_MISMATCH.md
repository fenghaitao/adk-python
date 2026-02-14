# GraphRAG Version Mismatch Issue

## Critical Finding

The GraphRAG indexing issue is caused by a **version mismatch** between:

1. **Forked GraphRAG 2.7.0** (in `graphrag/` folder) - Monolithic architecture
2. **PyPI GraphRAG 3.0.1** (installed by `uv run`) - Modular architecture

## Version Comparison

### GraphRAG 2.7.0 (Your Fork)
- **Location**: `graphrag/` folder
- **Architecture**: Monolithic package
- **Cache module**: `graphrag.cache.factory.CacheFactory`
- **Supported cache types**: `none`, `memory`, `file`, `blob`, `cosmosdb`
- **Cache registration**: Built-in at module load time

### GraphRAG 3.0.1 (PyPI)
- **Location**: Installed by `uv run` in `~/.cache/uv/environments-v2/`
- **Architecture**: Modular (separate packages)
  - `graphrag-3.0.1`
  - `graphrag_cache-3.0.1`
  - `graphrag_chunking-3.0.1`
  - `graphrag_common-3.0.1`
  - `graphrag_input-3.0.1`
  - `graphrag_llm-3.0.1`
  - `graphrag_storage-3.0.1`
  - `graphrag_vectors-3.0.1`
- **Cache module**: `graphrag_cache` (separate package)
- **Supported cache types**: Limited (appears to not include `file`)

## Why graphrag/openspec_graphrag Works

The working installation at `graphrag/openspec_graphrag` uses:
```bash
../../.venv/bin/python -m graphrag index
```

This uses the workspace `.venv` which likely has your forked GraphRAG 2.7.0 installed, not the PyPI 3.0.1 version.

## Why skills/graphrag-apps Fails

The skill uses:
```bash
uv run skills/graphrag-apps/scripts/graphrag_memory.py index
```

The PEP 723 dependency specification in the script is:
```python
# dependencies = [
#     "graphrag>=2.7.0",
#     ...
# ]
```

This causes `uv` to install the **latest** GraphRAG from PyPI (3.0.1), which has:
- Different package structure
- Different cache implementation
- Incompatible cache type support

## Solutions

### Option 1: Pin to GraphRAG 2.7.0 (Recommended for Compatibility)
Update the PEP 723 dependencies in `graphrag_memory.py`:

```python
# dependencies = [
#     "graphrag==2.7.0",  # Pin to exact version
#     "pyyaml>=6.0.0",
#     "typer>=0.16.0",
# ]
```

**Pros:**
- Matches your forked version
- Supports `cache.type: file`
- Known working configuration

**Cons:**
- Doesn't use latest features from 3.0.1
- May have security/bug fixes missing

### Option 2: Use Your Forked GraphRAG
Install your forked version in the environment:

```bash
# Install your fork
cd graphrag
uv pip install -e .

# Then run the skill
cd ..
uv run skills/graphrag-apps/scripts/graphrag_memory.py index
```

**Pros:**
- Uses your customized fork
- Full control over the version

**Cons:**
- Requires manual installation step
- Not self-contained via PEP 723

### Option 3: Upgrade to GraphRAG 3.0.1 (Future-proof)
Update the skill to work with GraphRAG 3.0.1's modular architecture:

1. Update dependencies to use 3.0.1
2. Investigate which cache types are supported in `graphrag_cache` 3.0.1
3. Update configuration accordingly
4. Test with the new architecture

**Pros:**
- Uses latest version
- Future-proof
- Gets latest features and fixes

**Cons:**
- Requires significant testing
- May have breaking changes
- Cache type support unclear

### Option 4: Keep cache.type: none (Current Workaround)
Continue using `cache.type: none` as currently implemented.

**Pros:**
- Works with both versions
- Simple and reliable
- No version conflicts

**Cons:**
- No caching benefits
- Slower re-indexing
- Higher API costs

## Recommendation

**For immediate use**: Keep the current fix with `cache.type: none` (Option 4)

**For long-term**: Either:
- Pin to GraphRAG 2.7.0 if you need file caching and want stability (Option 1)
- Upgrade to 3.0.1 and adapt to the new architecture (Option 3)

## Testing with Your Fork

To test with your forked GraphRAG 2.7.0:

```bash
# Use the workspace .venv that has your fork
cd graphrag/openspec_graphrag
../../.venv/bin/python -m graphrag index --root .

# Or install your fork globally
cd graphrag
pip install -e .
cd ../skills/graphrag-apps
python scripts/graphrag_memory.py index --input ../../openspec-memories
```

## Related Files
- `graphrag/pyproject.toml` - Your fork's version (2.7.0)
- `skills/graphrag-apps/scripts/graphrag_memory.py` - PEP 723 dependencies
- `~/.cache/uv/environments-v2/graphrag-memory-*/` - Installed 3.0.1 packages

## Conclusion

The root cause is not a configuration error, but a **version mismatch**. The skill's PEP 723 dependency `graphrag>=2.7.0` installs 3.0.1 from PyPI, which has a completely different architecture than your forked 2.7.0.

The current fix (`cache.type: none`) works as a compatibility layer between versions, but for full functionality, you need to either pin to 2.7.0 or upgrade the skill to work with 3.0.1's modular architecture.
