#!/usr/bin/env python3
"""
Demo script comparing original FilesRetrieval vs CachedFilesRetrieval
"""

import time
import os
from pathlib import Path
from cached_files_retrieval import CachedFilesRetrieval, create_cached_rag_agent

def setup_embedding_model():
    """Setup a local embedding model for testing."""
    try:
        from llama_index.core import Settings
        # Set a dummy OpenAI key to avoid the error (for demo purposes)
        os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-demo'
        print("⚠️  Using dummy OpenAI key for demo (embeddings may not work)")
        return True
    except Exception as e:
        print(f"❌ Error setting up embedding model: {e}")
        return False

def demo_cache_performance():
    """Demonstrate the performance benefits of caching."""
    print("🚀 CachedFilesRetrieval Performance Demo")
    print("=" * 60)
    
    if not setup_embedding_model():
        print("❌ Cannot proceed without embedding model setup")
        return
    
    docs_path = "sample_documents"
    cache_dir = "sample_documents/.cache_demo"
    
    # Clean up any existing cache for fair comparison
    cache_path = Path(cache_dir)
    if cache_path.exists():
        import shutil
        shutil.rmtree(cache_path)
        print("🧹 Cleaned up existing cache for fair test")
    
    print(f"📁 Using documents from: {docs_path}")
    print(f"💾 Cache directory: {cache_dir}")
    
    # Test 1: First creation (will build cache)
    print("\n" + "="*50)
    print("🔄 TEST 1: First creation (building cache)")
    print("="*50)
    
    start_time = time.time()
    try:
        tool1 = CachedFilesRetrieval(
            name="test_retrieval_1",
            description="Test cached retrieval",
            input_dir=docs_path,
            cache_dir=cache_dir
        )
        
        first_creation_time = time.time() - start_time
        print(f"⏱️  First creation time: {first_creation_time:.2f} seconds")
        
        # Show cache info
        cache_info = tool1.get_cache_info()
        print(f"📊 Cache created:")
        print(f"   - Documents: {cache_info['documents_count']}")
        print(f"   - Cache size: {cache_info['cache_size_mb']} MB")
        print(f"   - Cache valid: {cache_info['cache_valid']}")
        
    except Exception as e:
        print(f"❌ Error in first creation: {e}")
        return
    
    # Test 2: Second creation (should use cache)
    print("\n" + "="*50)
    print("🔄 TEST 2: Second creation (using cache)")
    print("="*50)
    
    start_time = time.time()
    try:
        tool2 = CachedFilesRetrieval(
            name="test_retrieval_2",
            description="Test cached retrieval", 
            input_dir=docs_path,
            cache_dir=cache_dir
        )
        
        second_creation_time = time.time() - start_time
        print(f"⏱️  Second creation time: {second_creation_time:.2f} seconds")
        
        # Calculate speedup
        if first_creation_time > 0:
            speedup = first_creation_time / second_creation_time
            print(f"🚀 Speedup: {speedup:.2f}x faster!")
        
    except Exception as e:
        print(f"❌ Error in second creation: {e}")
        return
    
    # Test 3: Cache invalidation
    print("\n" + "="*50)
    print("🔄 TEST 3: Cache invalidation")
    print("="*50)
    
    print("🗑️  Invalidating cache...")
    tool2.invalidate_cache()
    
    start_time = time.time()
    tool3 = CachedFilesRetrieval(
        name="test_retrieval_3",
        description="Test cached retrieval",
        input_dir=docs_path,
        cache_dir=cache_dir
    )
    third_creation_time = time.time() - start_time
    print(f"⏱️  Creation time after invalidation: {third_creation_time:.2f} seconds")
    
    # Summary
    print("\n" + "="*60)
    print("📊 PERFORMANCE SUMMARY")
    print("="*60)
    print(f"🏗️  First creation (build cache): {first_creation_time:.2f}s")
    print(f"⚡ Second creation (use cache):  {second_creation_time:.2f}s")
    print(f"🔄 After invalidation:          {third_creation_time:.2f}s")
    
    if first_creation_time > 0 and second_creation_time > 0:
        speedup = first_creation_time / second_creation_time
        print(f"\n🎯 Key Benefits:")
        print(f"   - {speedup:.1f}x faster startup with cache")
        print(f"   - Persistent across Python sessions")
        print(f"   - Automatic file change detection")

def demo_agent_with_cache():
    """Demonstrate using the cached agent."""
    print("\n" + "="*60)
    print("🤖 AGENT DEMO with CachedFilesRetrieval")
    print("="*60)
    
    if not setup_embedding_model():
        return
    
    docs_path = "sample_documents"
    
    try:
        print("🚀 Creating agent with cached retrieval...")
        agent, retrieval_tool = create_cached_rag_agent(docs_path)
        
        # Show cache info
        cache_info = retrieval_tool.get_cache_info()
        print(f"📊 Agent cache info:")
        print(f"   - Documents indexed: {cache_info['documents_count']}")
        print(f"   - Available documents: {', '.join(cache_info['documents'])}")
        print(f"   - Cache size: {cache_info['cache_size_mb']} MB")
        
        print("\n✅ Agent created successfully!")
        print("💡 The agent is now ready to answer questions using cached embeddings")
        
        # Example queries (commented out to avoid actual LLM calls in demo)
        print("\n📝 Example queries you could run:")
        example_queries = [
            "What are the different types of machine learning?",
            "What are the benefits of cloud computing?",
            "How is Python used in data science?"
        ]
        
        for i, query in enumerate(example_queries, 1):
            print(f"   {i}. {query}")
        
        print("\n💻 To run queries:")
        print("   response = agent.run('Your question here')")
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")

def show_cache_internals():
    """Show what's inside the cache directory."""
    print("\n" + "="*60)
    print("🔍 CACHE INTERNALS")
    print("="*60)
    
    cache_dir = Path("sample_documents/.cache_demo")
    
    if not cache_dir.exists():
        print("❌ No cache directory found")
        return
    
    print(f"📁 Cache directory: {cache_dir}")
    print("📄 Cache files:")
    
    for file_path in cache_dir.iterdir():
        if file_path.is_file():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   - {file_path.name}: {size_mb:.2f} MB")
    
    # Show metadata if available
    metadata_file = cache_dir / "cache_metadata.json"
    if metadata_file.exists():
        import json
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            print(f"\n📋 Cached documents metadata:")
            for doc_name, info in metadata.items():
                print(f"   - {doc_name}:")
                print(f"     Size: {info['size']} bytes")
                print(f"     Hash: {info['hash'][:16]}...")
        except Exception as e:
            print(f"❌ Error reading metadata: {e}")

if __name__ == "__main__":
    # Run all demos
    demo_cache_performance()
    demo_agent_with_cache()
    show_cache_internals()
    
    print("\n" + "="*60)
    print("🎉 Demo completed!")
    print("="*60)
    print("🔑 Key takeaways:")
    print("   1. CachedFilesRetrieval provides significant speedup for repeated use")
    print("   2. Embeddings are persisted across Python sessions")
    print("   3. Automatic cache invalidation when files change")
    print("   4. Easy drop-in replacement for original FilesRetrieval")
    print("   5. Configurable cache location and behavior")
    
    print(f"\n📁 Cache files are stored in: sample_documents/.cache_demo/")
    print("🧹 To clean up cache: rm -rf sample_documents/.cache_demo/")