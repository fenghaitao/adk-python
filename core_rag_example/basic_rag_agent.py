#!/usr/bin/env python3
"""
Basic RAG Agent Example using VertexAiRagRetrieval

This example demonstrates the simplest way to use ADK's core RAG components
with Vertex AI RAG for document retrieval.
"""

import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag


def create_basic_rag_agent():
    """Creates a basic RAG agent using Vertex AI RAG retrieval."""
    
    # Configure the RAG retrieval tool
    rag_retrieval_tool = VertexAiRagRetrieval(
        name="retrieve_documents",
        description=(
            "Use this tool to retrieve relevant documents and information "
            "from the knowledge base to answer user questions accurately."
        ),
        rag_resources=[
            rag.RagResource(
                # Use environment variable or provide your RAG corpus ID
                rag_corpus=os.environ.get(
                    "RAG_CORPUS", 
                    "projects/your-project/locations/us-central1/ragCorpora/your-corpus-id"
                ),
            )
        ],
        # Retrieve top 3 most similar documents
        similarity_top_k=3,
        # Only include documents with similarity score above 0.5
        vector_distance_threshold=0.5,
    )

    # Create the RAG agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="basic_rag_agent",
        instruction=(
            "You are a helpful AI assistant with access to a knowledge base. "
            "When users ask questions, use the retrieve_documents tool to find "
            "relevant information from the knowledge base, then provide accurate "
            "and comprehensive answers based on the retrieved content. "
            "Always cite the sources when possible and be clear about what "
            "information comes from the knowledge base versus your general knowledge."
        ),
        tools=[rag_retrieval_tool],
    )
    
    return agent


def main():
    """Main function to run the basic RAG agent."""
    print("🚀 Starting Basic RAG Agent Example")
    print("=" * 50)
    
    # Check if RAG corpus is configured
    rag_corpus = os.environ.get("RAG_CORPUS")
    if not rag_corpus:
        print("⚠️  Warning: RAG_CORPUS environment variable not set.")
        print("   Please set it to your Vertex AI RAG corpus ID:")
        print("   export RAG_CORPUS='projects/your-project/locations/us-central1/ragCorpora/your-corpus-id'")
        print()
    
    try:
        # Create the agent
        agent = create_basic_rag_agent()
        print("✅ Basic RAG agent created successfully!")
        print()
        
        # Example queries to test the RAG functionality
        example_queries = [
            "What is machine learning and how does it work?",
            "Can you explain the benefits of cloud computing?",
            "What are the best practices for cybersecurity?",
            "How do neural networks process information?",
        ]
        
        print("📝 Example queries you can try:")
        for i, query in enumerate(example_queries, 1):
            print(f"   {i}. {query}")
        print()
        
        # Interactive mode
        print("💬 Interactive mode - Type your questions (or 'quit' to exit):")
        print("-" * 50)
        
        while True:
            user_input = input("\n🤔 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            try:
                print("\n🔍 Searching knowledge base and generating response...")
                response = agent.run(user_input)
                print(f"\n🤖 Agent Response:\n{response}")
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("   Please check your RAG corpus configuration and try again.")
                
    except Exception as e:
        print(f"❌ Error creating RAG agent: {e}")
        print("   Please check your environment setup and try again.")


if __name__ == "__main__":
    main()