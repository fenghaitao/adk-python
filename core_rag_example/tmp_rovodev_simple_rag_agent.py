#!/usr/bin/env python3
"""
Simple Local Files RAG Agent Example
This is a simplified version that reads documents directly without complex embeddings.
"""

import os
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools.function_tool import FunctionTool

def create_simple_document_search_tool(documents_path):
    """Create a simple document search tool that reads files directly."""
    
    def search_local_documents(query: str) -> str:
        """
        Search through local documents for information related to the query.
        
        Args:
            query: The search query to find relevant information
            
        Returns:
            Relevant text from local documents
        """
        docs_path = Path(documents_path)
        relevant_content = []
        
        # Read all text files and look for relevant content
        for doc_file in docs_path.glob("*.txt"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Simple keyword matching (case insensitive)
                query_words = query.lower().split()
                content_lower = content.lower()
                
                # Check if any query words appear in the content
                if any(word in content_lower for word in query_words):
                    relevant_content.append(f"From {doc_file.name}:\n{content}\n")
                    
            except Exception as e:
                print(f"Error reading {doc_file}: {e}")
        
        if relevant_content:
            return "\n".join(relevant_content)
        else:
            return "No relevant information found in local documents."
    
    return FunctionTool(search_local_documents)

def create_simple_rag_agent(documents_path):
    """Creates a simple RAG agent using direct file reading and web search."""
    
    # Configure the simple document search tool
    doc_search_tool = create_simple_document_search_tool(documents_path)
    
    # Configure the Google Search tool
    google_search_tool = GoogleSearchTool()
    
    # Create the agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="simple_rag_agent",
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
        tools=[doc_search_tool, google_search_tool],
    )
    
    return agent

def main():
    """Main function to run the simple RAG agent."""
    print("📁 Starting Simple Local Files RAG + Web Search Agent Example")
    print("=" * 60)
    
    try:
        # Set up documents path
        docs_path = Path("sample_documents")
        print(f"📚 Using documents from: {docs_path}")
        
        # Show available documents
        print("📋 Available documents:")
        for doc_file in docs_path.glob("*.txt"):
            print(f"   - {doc_file.name}")
        print()
        
        # Create the agent
        agent = create_simple_rag_agent(str(docs_path))
        print("✅ Simple RAG agent created successfully!")
        print()
        
        # Demo queries
        demo_queries = [
            "What are the different types of machine learning?",
            "What are the benefits of cloud computing?", 
            "How is Python used in data science?",
        ]
        
        print("🚀 Demo mode - Running example queries automatically!")
        print("   The agent will use local docs and web search as needed.")
        print("-" * 60)
        
        for i, query in enumerate(demo_queries, 1):
            try:
                print(f"\n📖 Query {i}: {query}")
                print("🔍 Processing...")
                response = agent.run(query)
                print(f"\n🤖 Agent Response:\n{response}")
                print("-" * 60)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
        
        print("\n✅ Demo completed! All example queries have been processed.")
                
    except Exception as e:
        print(f"❌ Error setting up simple RAG agent: {e}")
        print("   Please check your installation and try again.")

if __name__ == "__main__":
    main()