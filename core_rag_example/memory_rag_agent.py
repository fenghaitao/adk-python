#!/usr/bin/env python3
"""
Memory-Powered RAG Agent Example using VertexAiRagMemoryService

This example demonstrates how to use ADK's RAG memory service to create
an agent that can remember and retrieve information from past conversations.
"""

import os
from google.adk.agents.llm_agent import Agent
from google.adk.memory.vertex_ai_rag_memory_service import VertexAiRagMemoryService
from google.adk.tools.load_memory_tool import LoadMemoryTool
from google.adk.tools.preload_memory_tool import PreloadMemoryTool


def create_memory_rag_agent():
    """Creates a RAG agent with persistent memory using Vertex AI RAG."""
    
    # Configure the RAG memory service
    rag_memory_service = VertexAiRagMemoryService(
        rag_corpus=os.environ.get(
            "RAG_CORPUS",
            "projects/your-project/locations/us-central1/ragCorpora/your-corpus-id"
        ),
        # Retrieve top 5 most relevant memories
        similarity_top_k=5,
        # Only include memories with similarity score above 0.4
        vector_distance_threshold=0.4,
    )
    
    # Create memory tools
    load_memory_tool = LoadMemoryTool(
        name="load_relevant_memories",
        description=(
            "Use this tool to load relevant memories and past conversations "
            "that might help answer the current question. This searches through "
            "previous interactions and stored knowledge."
        ),
        memory_service=rag_memory_service,
    )
    
    preload_memory_tool = PreloadMemoryTool(
        name="save_important_info",
        description=(
            "Use this tool to save important information from the current "
            "conversation to memory for future reference. This helps build "
            "a knowledge base of useful information."
        ),
        memory_service=rag_memory_service,
    )
    
    # Create the agent with memory capabilities
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="memory_rag_agent",
        instruction=(
            "You are an intelligent AI assistant with persistent memory capabilities. "
            "You can remember information from past conversations and build knowledge over time. "
            "\n\nFor each user question:"
            "\n1. First, use 'load_relevant_memories' to check if you have relevant "
            "information from past conversations"
            "\n2. Provide a helpful response based on both your general knowledge "
            "and any relevant memories found"
            "\n3. If the conversation contains important information that might be "
            "useful later, use 'save_important_info' to store it"
            "\n\nAlways be clear about whether information comes from your memory, "
            "general knowledge, or both."
        ),
        tools=[load_memory_tool, preload_memory_tool],
        memory_service=rag_memory_service,
    )
    
    return agent


def main():
    """Main function to run the memory-powered RAG agent."""
    print("🧠 Starting Memory-Powered RAG Agent Example")
    print("=" * 55)
    
    # Check if RAG corpus is configured
    rag_corpus = os.environ.get("RAG_CORPUS")
    if not rag_corpus:
        print("⚠️  Warning: RAG_CORPUS environment variable not set.")
        print("   Please set it to your Vertex AI RAG corpus ID:")
        print("   export RAG_CORPUS='projects/your-project/locations/us-central1/ragCorpora/your-corpus-id'")
        print()
    
    try:
        # Create the agent
        agent = create_memory_rag_agent()
        print("✅ Memory-powered RAG agent created successfully!")
        print()
        
        # Example conversation flow
        print("📚 This agent can remember information across conversations!")
        print("   Try teaching it something, then ask about it later.")
        print()
        
        example_interactions = [
            "Tell me about your favorite programming language and why you like it.",
            "What did I just tell you about programming languages?",
            "My name is Alice and I work as a data scientist at TechCorp.",
            "What do you remember about me?",
            "I'm working on a machine learning project using Python and TensorFlow.",
            "What projects am I working on?",
        ]
        
        print("💡 Example conversation flow:")
        for i, interaction in enumerate(example_interactions, 1):
            print(f"   {i}. {interaction}")
        print()
        
        # Interactive mode
        print("💬 Interactive mode - Type your messages (or 'quit' to exit):")
        print("   The agent will remember important information for future conversations!")
        print("-" * 55)
        
        conversation_count = 0
        
        while True:
            user_input = input(f"\n💭 Message {conversation_count + 1}: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Your conversation has been saved to memory.")
                break
                
            if not user_input:
                continue
                
            try:
                print("\n🔍 Checking memory and generating response...")
                response = agent.run(user_input)
                print(f"\n🤖 Agent Response:\n{response}")
                
                conversation_count += 1
                
                if conversation_count % 3 == 0:
                    print(f"\n📊 Conversation #{conversation_count} completed!")
                    print("   The agent has been building its memory throughout our chat.")
                
                print("-" * 55)
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                print("   Please check your RAG corpus configuration and try again.")
                
    except Exception as e:
        print(f"❌ Error creating memory RAG agent: {e}")
        print("   Please check your environment setup and try again.")


if __name__ == "__main__":
    main()