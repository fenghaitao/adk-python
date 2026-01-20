#!/usr/bin/env python3
"""Test indexing a single file with GitHub Copilot."""

import os
import asyncio
import sys
from pathlib import Path

# Configure BEFORE importing cognee
os.environ["LLM_MODEL"] = "github_copilot/gpt-4o"
os.environ["LLM_PROVIDER"] = "custom"
os.environ["EMBEDDING_MODEL"] = "github_copilot/text-embedding-3-small"
os.environ["EMBEDDING_DIMENSIONS"] = "1536"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["REQUIRE_AUTHENTICATION"] = "false"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["TELEMETRY_DISABLED"] = "1"

# Use local temp directory
os.environ["SYSTEM_ROOT_DIRECTORY"] = "/tmp/cognee_test_system"
os.environ["DATA_ROOT_DIRECTORY"] = "/tmp/cognee_test_data"

# More aggressive rate limiting for testing
os.environ["EMBEDDING_RATE_LIMIT_ENABLED"] = "true"
os.environ["EMBEDDING_RATE_LIMIT_REQUESTS"] = "50"
os.environ["EMBEDDING_RATE_LIMIT_INTERVAL"] = "60"
os.environ["LLM_RATE_LIMIT_ENABLED"] = "true"
os.environ["LLM_RATE_LIMIT_REQUESTS"] = "50"
os.environ["LLM_RATE_LIMIT_INTERVAL"] = "60"

print("🧪 Testing Single File Indexing with GitHub Copilot")
print("="*60)

import cognee
from cognee.modules.search.types.SearchType import SearchType

async def main():
    """Test with a single small file."""
    
    try:
        # Step 1: Prune
        print("🧹 Pruning system...")
        await cognee.prune.prune_system(metadata=True)
        print("✅ System pruned\n")
        
        # Step 2: Add single file
        test_file = Path("../../openspec-memories/dml_basics.md")
        if not test_file.exists():
            # Try first file we can find
            memory_dir = Path("../../openspec-memories")
            test_file = next(memory_dir.glob("*.md"))
        
        print(f"📄 Adding single file: {test_file.name}")
        await cognee.add(
            data=str(test_file),
            dataset_name="test_single"
        )
        print("✅ File added\n")
        
        # Step 3: Cognify
        print("🧠 Building knowledge graph...")
        await cognee.cognify(dataset_name="test_single")
        print("✅ Knowledge graph built\n")
        
        # Step 4: Search
        print("🔍 Testing search...")
        results = await cognee.search(
            query_text="What is DML?",
            query_type=SearchType.GRAPH_COMPLETION
        )
        
        print(f"   Results: {len(results)} found")
        if results:
            print(f"   Preview: {str(results[0])[:100]}...")
        
        print("\n✅ SUCCESS!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
