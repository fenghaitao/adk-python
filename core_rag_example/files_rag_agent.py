#!/usr/bin/env python3
"""
Local Files RAG Agent Example using FilesRetrieval

This example demonstrates how to use ADK's FilesRetrieval for local file-based RAG
without requiring cloud services. Perfect for testing or when working with local documents.
"""

import os
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
from google.adk.tools.google_search_tool import GoogleSearchTool

# Configure LlamaIndex to use local embeddings
from llama_index.core import Settings
try:
    # Try to use a simple local embedding model
    from llama_index.embeddings.fastembed import FastEmbedEmbedding
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
except ImportError:
    try:
        # Fallback to OpenAI with a dummy key to avoid the error
        import os
        os.environ['OPENAI_API_KEY'] = 'dummy-key-for-local-use'
        print("⚠️  Using dummy OpenAI key - this may cause issues with actual embedding requests")
    except Exception:
        print("⚠️  Could not configure embeddings - proceeding with defaults")
def create_files_rag_agent(documents_path):
    """Creates a RAG agent using local files retrieval and web search."""
    
    # Configure the Files Retrieval tool
    files_retrieval_tool = FilesRetrieval(
        name="search_local_documents",
        description=(
            "Use this tool to search through local documents and files "
            "to find relevant information. This searches through text files, "
            "documentation, and other local resources. Use this FIRST for "
            "questions that might be answered by the local knowledge base."
        ),
        # Path to the directory containing documents
        input_dir=str(documents_path),
    )
    
    # Configure the Google Search tool
    google_search_tool = GoogleSearchTool(
        name="search_web",
        description=(
            "Use this tool to search the web for current information, news, "
            "or topics not covered in the local documents. Use this as a "
            "fallback when local documents don't have the information needed."
        ),
        num_results=5,
    )
    
    # Create the agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="files_rag_agent",
        instruction=(
            "You are a helpful AI assistant with access to both local documents and web search. "
            "You have two main tools for finding information:\n\n"
            
            "1. **search_local_documents**: Local knowledge base with curated documents\n"
            "2. **search_web**: Web search for current/general information\n\n"
            
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
        tools=[files_retrieval_tool, google_search_tool],
    )
    
    return agent


def main():
    """Main function to run the files-based RAG agent."""
    print("📁 Starting Local Files RAG + Web Search Agent Example")
    print("=" * 50)
    
    try:
        # Create sample documents
        print("📚 Setting up sample documents...")
        docs_path = Path("sample_documents")
        print(f"✅ Documents ready in: {docs_path}")
        print()
        
        # Create the agent
        agent = create_files_rag_agent(str(docs_path))
        print("✅ Files RAG agent created successfully!")
        print()
        
        # Show available documents
        print("📋 Available documents:")
        for doc_file in docs_path.glob("*.txt"):
            print(f"   - {doc_file.name}")
        print()
        
        # Example queries
        example_queries = [
            "What are the different types of machine learning?",  # Local docs
            "What are the benefits of cloud computing?",  # Local docs
            "What are the latest developments in AI in 2024?",  # Web search
            "How is Python used in data science?",  # Local docs
            "What are current cybersecurity threats?",  # Combination
            "Compare TensorFlow and PyTorch frameworks",  # Web search
        ]
        
        print("💡 Example queries you can try:")
        for i, query in enumerate(example_queries, 1):
            print(f"   {i}. {query}")
        print()
        
        # Automatic demo mode - run some example queries
        print("🚀 Demo mode - Running example queries automatically!")
        print("   The agent will use local docs and web search as needed.")
        print("-" * 50)
        
        # Run a few example queries automatically
        demo_queries = [
            "What are the different types of machine learning?",  # Local docs
            "What are the benefits of cloud computing?",  # Local docs
            "How is Python used in data science?",  # Local docs
        ]
        
        for i, query in enumerate(demo_queries, 1):
            try:
                print(f"\n📖 Query {i}: {query}")
                print("🔍 Processing...")
                response = agent.run(query)
                print(f"\n🤖 Agent Response:\n{response}")
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("   Please check that the sample documents exist and try again.")
        
        print("\n✅ Demo completed! All example queries have been processed.")
                
    except Exception as e:
        print(f"❌ Error setting up files RAG agent: {e}")
        print("   Please check your installation and try again.")


if __name__ == "__main__":
    main()