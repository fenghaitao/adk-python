#!/usr/bin/env python3
"""
Enhanced RAG Agent using CachedFilesRetrieval

This is a drop-in replacement for files_rag_agent.py that uses caching
for much better performance on subsequent runs.
"""

import os
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from cached_files_retrieval import CachedFilesRetrieval

# Configure LlamaIndex to use a dummy OpenAI key (for demo)
# In production, you'd set up proper local embeddings
os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-demo'

def create_cached_rag_agent(documents_path, cache_dir=None):
    """Creates a RAG agent using cached files retrieval and web search."""
    
    # Configure the cached document search tool
    cached_retrieval_tool = CachedFilesRetrieval(
        name="search_local_documents",
        description=(
            "Use this tool to search through local documents and files "
            "to find relevant information. This searches through text files, "
            "documentation, and other local resources. Use this FIRST for "
            "questions that might be answered by the local knowledge base. "
            "This tool uses cached embeddings for fast performance."
        ),
        input_dir=documents_path,
        cache_dir=cache_dir
    )
    
    # Configure the Google Search tool
    google_search_tool = GoogleSearchTool()
    
    # Create the agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="cached_rag_agent",
        instruction=(
            "You are a helpful AI assistant with access to both local documents and web search. "
            "You have two main tools for finding information:\n\n"
            
            "1. **search_local_documents**: Local knowledge base with curated documents (cached for fast performance)\n"
            "2. **google_search**: Web search for current/general information\n\n"
            
            "Available local document topics include:\n"
            "- Artificial Intelligence and Machine Learning\n"
            "- Cloud Computing\n"
            "- Cybersecurity\n"
            "- Python Programming\n\n"
            
            "**Search Strategy:**\n"
            "- Start with local documents for topics covered in the knowledge base\n"
            "- Use web search for current events, recent developments, or topics not in local docs\n"
            "- Combine information from both sources when helpful\n"
            "- Always cite your sources and indicate which tool provided the information\n\n"
            
            "**Response Format:**\n"
            "- Provide comprehensive answers combining relevant information\n"
            "- Clearly indicate information sources (local docs vs. web search)\n"
            "- Mention if information is from local knowledge vs. external sources"
        ),
        tools=[cached_retrieval_tool, google_search_tool],
    )
    
    return agent, cached_retrieval_tool

def main():
    """Main function to run the cached RAG agent."""
    print("📁 Starting Cached Local Files RAG + Web Search Agent Example")
    print("=" * 70)
    
    try:
        # Set up documents path
        docs_path = Path("sample_documents")
        cache_path = docs_path / ".embeddings_cache"
        
        print(f"📚 Using documents from: {docs_path}")
        print(f"💾 Cache directory: {cache_path}")
        
        # Show available documents
        print("\n📋 Available documents:")
        if docs_path.exists():
            for doc_file in docs_path.glob("*.txt"):
                print(f"   - {doc_file.name}")
        else:
            print("   ❌ No sample_documents directory found!")
            return
        
        # Create the agent with timing
        print(f"\n🚀 Creating cached RAG agent...")
        import time
        start_time = time.time()
        
        agent, retrieval_tool = create_cached_rag_agent(str(docs_path))
        
        creation_time = time.time() - start_time
        print(f"✅ Agent created in {creation_time:.2f} seconds!")
        
        # Show cache information
        cache_info = retrieval_tool.get_cache_info()
        print(f"\n📊 Cache Information:")
        print(f"   - Documents indexed: {cache_info['documents_count']}")
        print(f"   - Cache size: {cache_info['cache_size_mb']} MB")
        print(f"   - Cache valid: {cache_info['cache_valid']}")
        print(f"   - Cache exists: {cache_info['cache_exists']}")
        
        if cache_info['cache_exists'] and cache_info['cache_valid']:
            print("   🎯 Using existing cache (fast startup!)")
        else:
            print("   🔧 Built new cache (first run or files changed)")
        
        # Demo queries
        demo_queries = [
            "What are the different types of machine learning?",
            "What are the benefits of cloud computing?", 
            "How is Python used in data science?",
        ]
        
        print(f"\n🚀 Demo mode - Running example queries automatically!")
        print("   The agent will use cached local docs and web search as needed.")
        print("-" * 70)
        
        for i, query in enumerate(demo_queries, 1):
            try:
                print(f"\n📖 Query {i}: {query}")
                print("🔍 Processing...")
                
                # Time the query
                query_start = time.time()
                response = agent.run(query)
                query_time = time.time() - query_start
                
                print(f"\n🤖 Agent Response (took {query_time:.2f}s):\n{response}")
                print("-" * 70)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
        
        print(f"\n✅ Demo completed! All example queries processed.")
        
        # Show cache management options
        print(f"\n🛠️  Cache Management:")
        print(f"   - Cache location: {cache_info['cache_dir']}")
        print(f"   - To force rebuild: CachedFilesRetrieval(..., force_rebuild=True)")
        print(f"   - To clear cache: retrieval_tool.invalidate_cache()")
        print(f"   - To clean up: rm -rf {cache_path}")
        
    except Exception as e:
        print(f"❌ Error setting up cached RAG agent: {e}")
        print("   Please check your installation and try again.")
        
        # Show troubleshooting tips
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Make sure sample_documents/ directory exists")
        print(f"   2. Ensure you have proper embedding model configured")
        print(f"   3. Check file permissions for cache directory")

def interactive_mode():
    """Run the agent in interactive mode."""
    print("💬 Interactive mode - Ask questions using cached local docs and web search!")
    print("   Type 'cache info' to see cache status, 'rebuild' to rebuild cache, or 'quit' to exit.")
    print("-" * 70)
    
    docs_path = "sample_documents"
    agent, retrieval_tool = create_cached_rag_agent(docs_path)
    
    while True:
        user_input = input("\n📖 Your question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if user_input.lower() == 'cache info':
            cache_info = retrieval_tool.get_cache_info()
            print(f"\n📊 Cache Information:")
            for key, value in cache_info.items():
                print(f"   {key}: {value}")
            continue
            
        if user_input.lower() == 'rebuild':
            print("🔄 Rebuilding cache...")
            retrieval_tool.invalidate_cache()
            print("✅ Cache rebuilt!")
            continue
            
        if not user_input:
            continue
            
        try:
            print("🔍 Searching...")
            response = agent.run(user_input)
            print(f"\n🤖 Agent Response:\n{response}")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        main()