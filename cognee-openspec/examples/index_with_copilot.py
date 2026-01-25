#!/usr/bin/env python3
"""Index openspec-memories using GitHub Copilot (bypassing CLI)."""

import os
import asyncio
import sys
from pathlib import Path

# Configure BEFORE importing cognee
os.environ["LLM_MODEL"] = "github_copilot/gpt-4o"
os.environ["LLM_PROVIDER"] = "custom"
os.environ["LLM_API_KEY"] = "oauth2"  # Dummy key for OAuth2 authentication
os.environ["EMBEDDING_MODEL"] = "github_copilot/text-embedding-3-small"
os.environ["EMBEDDING_DIMENSIONS"] = "1536"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["REQUIRE_AUTHENTICATION"] = "false"
os.environ["LOG_LEVEL"] = "ERROR"
os.environ["TELEMETRY_DISABLED"] = "1"

# Use local temp directory to avoid NFS locking issues
os.environ["SYSTEM_ROOT_DIRECTORY"] = "/tmp/cognee_openspec_system"
os.environ["DATA_ROOT_DIRECTORY"] = "/tmp/cognee_openspec_data"

# Rate limiting for GitHub Copilot
os.environ["EMBEDDING_RATE_LIMIT_ENABLED"] = "true"
os.environ["EMBEDDING_RATE_LIMIT_REQUESTS"] = "30"
os.environ["EMBEDDING_RATE_LIMIT_INTERVAL"] = "60"
os.environ["LLM_RATE_LIMIT_ENABLED"] = "true"
os.environ["LLM_RATE_LIMIT_REQUESTS"] = "30"
os.environ["LLM_RATE_LIMIT_INTERVAL"] = "60"

print("📚 Indexing OpenSpec Memories with GitHub Copilot")
print("="*60)
print(f"   LLM: {os.environ['LLM_MODEL']}")
print(f"   Embeddings: {os.environ['EMBEDDING_MODEL']}")
print(f"   Access Control: {os.environ['ENABLE_BACKEND_ACCESS_CONTROL']}")
print(f"   Rate Limiting: {os.environ['EMBEDDING_RATE_LIMIT_REQUESTS']}/min")
print("="*60)
print()

# Now import cognee
import cognee
from cognee.modules.search.types.SearchType import SearchType

async def main():
    """Index and search openspec memories."""
    
    script_dir = Path(__file__).parent
    memory_dir = (script_dir / "../../openspec-memories").resolve()
    if not memory_dir.exists():
        print(f"❌ Memory directory not found: {memory_dir}")
        return False
    
    try:
        # Step 1: Prune system
        print("🧹 Pruning system...")
        await cognee.prune.prune_system(metadata=True)
        print("✅ System pruned\n")
        
        # Step 2: Add files
        print(f"📂 Adding files from {memory_dir}...")
        md_files = list(memory_dir.glob("*.md"))
        print(f"   Found {len(md_files)} markdown files")
        
        import time
        start_time = time.time()
        
        # Add files one by one
        for md_file in md_files:
            await cognee.add(
                data=str(md_file),
                dataset_name="openspec_memories"
            )
        
        add_time = time.time() - start_time
        print(f"✅ Files added in {add_time:.1f}s\n")
        
        # Step 3: Cognify (build knowledge graph)
        print("🧠 Building knowledge graph...")
        print("   (This may take a few minutes with rate limiting...)")
        start_time = time.time()
        
        await cognee.cognify(dataset_name="openspec_memories")
        
        cognify_time = time.time() - start_time
        print(f"✅ Knowledge graph built in {cognify_time:.1f}s\n")
        
        # Step 4: Test search
        print("🔍 Testing search...")
        query = "What is DML?"
        results = await cognee.search(
            query_text=query,
            query_type=SearchType.GRAPH_COMPLETION
        )
        
        print(f"   Query: {query}")
        print(f"   Results: {len(results)} passages found")
        if results:
            print(f"   First result preview: {str(results[0])[:150]}...")
        print()
        
        print("="*60)
        print("🎉 SUCCESS! GitHub Copilot indexing complete!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
