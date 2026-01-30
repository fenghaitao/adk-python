#!/usr/bin/env python3
"""
LightRAG with OpenAI Example
Simple demonstration of LightRAG using OpenAI's models
"""

import os
import asyncio
import sys

# Add lightrag to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lightrag'))

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed

WORKING_DIR = "../lightrag_openspec/tmp_lightrag_openai_test"

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set it with: export OPENAI_API_KEY='your-openai-api-key'")
    sys.exit(1)

# Create working directory
if not os.path.exists(WORKING_DIR):
    os.makedirs(WORKING_DIR)
    print(f"✅ Created working directory: {WORKING_DIR}")

async def initialize_rag():
    """Initialize LightRAG with OpenAI."""
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=openai_embed,
    )
    await rag.initialize_storages()
    return rag

async def main():
    print("\n" + "="*60)
    print("LightRAG with OpenAI Demo")
    print("="*60)
    
    # Initialize RAG
    print("\n🔧 Initializing LightRAG...")
    rag = await initialize_rag()
    print("✅ LightRAG initialized with OpenAI models")
    
    # Sample document about ADK and LightRAG
    sample_text = """
    The Agent Development Kit (ADK) is an open-source Python toolkit developed by Google
    for building sophisticated AI agents. ADK supports multiple language models including
    Gemini, OpenAI's GPT models, and Anthropic's Claude. It provides features like tool
    calling, memory management, multi-agent orchestration, and streaming responses.
    
    LightRAG is a Retrieval-Augmented Generation system that uses knowledge graphs to
    improve context retrieval. Unlike traditional RAG systems that rely solely on vector
    similarity, LightRAG builds a knowledge graph from documents, extracting entities
    and their relationships. This allows for more sophisticated queries that can traverse
    the graph to find relevant information.
    
    When integrating LightRAG with ADK, developers can create agents with graph-based
    memory systems. This enables agents to understand complex relationships between
    entities and perform multi-hop reasoning. For example, an agent could answer questions
    that require connecting information across multiple documents or understanding
    indirect relationships between concepts.
    
    The combination of ADK's agent orchestration capabilities and LightRAG's knowledge
    graph retrieval creates powerful systems for tasks like question answering,
    document analysis, and knowledge management.
    """
    
    print("\n📝 Inserting sample document...")
    await rag.ainsert(sample_text)
    print("✅ Document inserted and processed")
    
    # Test queries with different modes
    queries = [
        "What is ADK?",
        "How does LightRAG differ from traditional RAG?",
        "What benefits come from integrating ADK with LightRAG?",
    ]
    
    modes = ["naive", "local", "global", "hybrid"]
    
    for query in queries:
        print("\n" + "-"*60)
        print(f"❓ Query: {query}")
        print("-"*60)
        
        for mode in modes:
            print(f"\n📊 {mode.upper()} mode:")
            result = await rag.aquery(query, param=QueryParam(mode=mode))
            # Print first 200 characters
            print(result[:200] + "..." if len(result) > 200 else result)
        
        # Just show one query with all modes for demo
        break
    
    # Cleanup
    await rag.finalize_storages()
    print("\n✅ Demo completed successfully!")
    print(f"\n💾 Storage location: {WORKING_DIR}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
