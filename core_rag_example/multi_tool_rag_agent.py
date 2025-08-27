#!/usr/bin/env python3
"""
Multi-Tool RAG Agent Example

This example demonstrates how to combine multiple RAG tools:
- VertexAiRagRetrieval for document retrieval
- VertexAiSearchTool for search functionality
- GoogleSearchTool for web search as fallback
"""

import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
from google.adk.tools.google_search_tool import GoogleSearchTool
from vertexai.preview import rag


def create_multi_tool_rag_agent():
    """Creates a RAG agent with multiple retrieval and search tools."""
    
    # 1. Vertex AI RAG Retrieval Tool
    rag_retrieval_tool = VertexAiRagRetrieval(
        name="retrieve_knowledge_base",
        description=(
            "Use this tool to retrieve information from the internal knowledge base. "
            "This contains curated documents and information specific to your organization "
            "or domain. Use this FIRST for any questions that might be answered by "
            "internal documentation."
        ),
        rag_resources=[
            rag.RagResource(
                rag_corpus=os.environ.get(
                    "RAG_CORPUS",
                    "projects/your-project/locations/us-central1/ragCorpora/your-corpus-id"
                ),
            )
        ],
        similarity_top_k=3,
        vector_distance_threshold=0.5,
    )
    
    # 2. Vertex AI Search Tool
    vertex_search_tool = VertexAiSearchTool(
        data_store_id=os.environ.get(
            "VERTEX_AI_SEARCH_DATASTORE",
            "projects/your-project/locations/global/collections/default_collection/dataStores/your-datastore"
        ),
        max_results=5,
    )
    
    # 3. Google Search Tool (fallback for general web information)
    google_search_tool = GoogleSearchTool(
        name="search_web",
        description=(
            "Use this tool to search the web for current information, news, "
            "or topics not covered in the internal knowledge base. Use this "
            "as a fallback when internal sources don't have the information needed."
        ),
        num_results=5,
    )
    
    # Create the multi-tool RAG agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="multi_tool_rag_agent",
        instruction=(
            "You are an advanced AI assistant with access to multiple information sources. "
            "You have three main tools for finding information:\n\n"
            
            "1. **retrieve_knowledge_base**: Internal knowledge base with curated documents\n"
            "2. **vertex_ai_search**: Vertex AI Search for structured data\n"
            "3. **search_web**: Web search for current/general information\n\n"
            
            "**Search Strategy:**\n"
            "- Start with internal sources (retrieve_knowledge_base) for domain-specific questions\n"
            "- Use Vertex AI Search for structured data queries\n"
            "- Use web search for current events, general knowledge, or when internal sources lack information\n"
            "- Combine information from multiple sources when helpful\n"
            "- Always cite your sources and indicate which tool provided the information\n\n"
            
            "**Response Format:**\n"
            "- Provide comprehensive answers combining relevant information\n"
            "- Clearly indicate information sources\n"
            "- Mention if information is from internal knowledge vs. external sources\n"
            "- Suggest follow-up questions when appropriate"
        ),
        tools=[rag_retrieval_tool, vertex_search_tool, google_search_tool],
    )
    
    return agent


def main():
    """Main function to run the multi-tool RAG agent."""
    print("🔧 Starting Multi-Tool RAG Agent Example")
    print("=" * 50)
    
    # Check environment variables
    missing_vars = []
    
    if not os.environ.get("RAG_CORPUS"):
        missing_vars.append("RAG_CORPUS")
    
    if not os.environ.get("VERTEX_AI_SEARCH_DATASTORE"):
        missing_vars.append("VERTEX_AI_SEARCH_DATASTORE")
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n   Some tools may not work without proper configuration.")
        print("   See README.md for setup instructions.")
        print()
    
    try:
        # Create the agent
        agent = create_multi_tool_rag_agent()
        print("✅ Multi-tool RAG agent created successfully!")
        print()
        
        # Example queries that demonstrate different tools
        example_queries = [
            {
                "query": "What is our company's policy on remote work?",
                "expected_tool": "Internal knowledge base",
                "description": "Should use internal knowledge base"
            },
            {
                "query": "What are the latest developments in AI technology?",
                "expected_tool": "Web search",
                "description": "Should use web search for current information"
            },
            {
                "query": "Find customer data for account ID 12345",
                "expected_tool": "Vertex AI Search",
                "description": "Should use structured search"
            },
            {
                "query": "Compare our product features with competitors",
                "expected_tool": "Multiple tools",
                "description": "Should combine internal knowledge + web search"
            },
        ]
        
        print("🎯 Example queries that demonstrate different tools:")
        for i, example in enumerate(example_queries, 1):
            print(f"   {i}. {example['query']}")
            print(f"      → {example['description']}")
        print()
        
        # Interactive mode
        print("💬 Interactive mode - Ask questions to see different tools in action!")
        print("   The agent will choose the best tool(s) for each query.")
        print("-" * 50)
        
        while True:
            user_input = input("\n🔍 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'examples':
                print("\n📋 Try these example queries:")
                for i, example in enumerate(example_queries, 1):
                    print(f"   {i}. {example['query']}")
                continue
                
            if not user_input:
                continue
                
            try:
                print("\n🔄 Analyzing query and selecting appropriate tools...")
                response = agent.run(user_input)
                print(f"\n🤖 Agent Response:\n{response}")
                
                print("\n💡 Tip: Notice which tools the agent chose to use!")
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("   Some tools may not be configured. Check your environment setup.")
                
    except Exception as e:
        print(f"❌ Error creating multi-tool RAG agent: {e}")
        print("   Please check your environment setup and try again.")


if __name__ == "__main__":
    main()