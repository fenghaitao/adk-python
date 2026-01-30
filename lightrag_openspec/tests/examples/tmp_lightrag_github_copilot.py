#!/usr/bin/env python3
"""
LightRAG with GitHub Copilot
Uses GitHub Copilot's gpt-4o for chat and text-embedding-3-small for embeddings
"""

import os
import sys
import asyncio

sys.path.insert(0, '../../lightrag')

from lightrag import LightRAG, QueryParam
from lightrag.llm.llama_index_impl import (
    llama_index_complete_if_cache,
    llama_index_embed,
)
from lightrag.utils import EmbeddingFunc
from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

# Configuration
WORKING_DIR = "../lightrag_github_copilot"
LLM_MODEL = "github_copilot/gpt-4o-mini"  # or gpt-4o for higher quality
EMBEDDING_MODEL = "github_copilot/text-embedding-3-small"
EMBEDDING_DIM = 1536  # text-embedding-3-small dimension

# Create working directory
os.makedirs(WORKING_DIR, exist_ok=True)

print("\n" + "="*70)
print("🤖 LightRAG with GitHub Copilot")
print("="*70)
print(f"   LLM Model: {LLM_MODEL}")
print(f"   Embedding Model: {EMBEDDING_MODEL}")
print("="*70)
print()

# LLM function using GitHub Copilot
async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    """LLM function using GitHub Copilot's GPT models."""
    try:
        if "llm_instance" not in kwargs:
            llm_instance = LiteLLM(
                model=LLM_MODEL,
                api_key="oauth2",  # GitHub Copilot uses OAuth2
                temperature=0.7,
            )
            kwargs["llm_instance"] = llm_instance
        
        response = await llama_index_complete_if_cache(
            kwargs["llm_instance"],
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
        )
        return response
    except Exception as e:
        print(f"❌ LLM request failed: {e}")
        raise

# Embedding function using GitHub Copilot
async def embedding_func(texts):
    """Embedding function using GitHub Copilot's embeddings."""
    try:
        embed_model = LiteLLMEmbedding(
            model_name=EMBEDDING_MODEL,
            api_key="oauth2",  # GitHub Copilot uses OAuth2
        )
        return await llama_index_embed(texts, embed_model=embed_model)
    except Exception as e:
        print(f"❌ Embedding request failed: {e}")
        raise

async def main():
    """Main function to demonstrate LightRAG with GitHub Copilot."""
    
    print("🔧 Initializing LightRAG with GitHub Copilot...")
    
    # Initialize LightRAG
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=EMBEDDING_DIM,
            max_token_size=8192,
            func=embedding_func,
        ),
        llm_model_name="gpt-4o-mini",
        # Rate limiting for GitHub Copilot
        llm_model_max_async=4,
        embedding_func_max_async=4,
        max_parallel_insert=1,
    )
    
    await rag.initialize_storages()
    print("✅ LightRAG initialized\n")
    
    # Insert sample documents
    documents = [
        """
        The Agent Development Kit (ADK) is an open-source Python toolkit developed 
        by Google for building sophisticated AI agents. It supports multiple language 
        models including Gemini, OpenAI's GPT, and Anthropic's Claude. ADK provides
        features like tool calling, memory management, and multi-agent orchestration.
        """,
        """
        LightRAG is a knowledge graph-based Retrieval-Augmented Generation system.
        Unlike traditional RAG that relies solely on vector similarity, LightRAG builds
        knowledge graphs by extracting entities and their relationships from documents.
        This enables multi-hop reasoning and better context retrieval.
        """,
        """
        GitHub Copilot provides access to OpenAI's models for Copilot subscribers.
        It supports GPT-4o and GPT-4o-mini for chat, and text-embedding models for 
        semantic search. Authentication is handled through GitHub CLI using OAuth2.
        This makes it cost-effective for developers who already have Copilot subscriptions.
        """,
    ]
    
    print("📝 Inserting documents...")
    for i, doc in enumerate(documents):
        await rag.ainsert(doc.strip(), ids=f"doc_{i+1}")
        print(f"   ✓ Inserted document {i+1}")
    print()
    
    # Test queries with different modes
    queries = [
        "What is ADK?",
        "How does LightRAG differ from traditional RAG?",
        "How do I authenticate with GitHub Copilot?",
    ]
    
    print("🔍 Testing queries...\n")
    
    for query in queries:
        print(f"❓ Query: {query}")
        print("-" * 70)
        
        # Test with hybrid mode (recommended)
        result = await rag.aquery(query, param=QueryParam(mode="hybrid"))
        print(f"💡 Answer:")
        print(f"   {result[:400]}...")
        print()
    
    # Cleanup
    await rag.finalize_storages()
    
    print("="*70)
    print("✅ Demo completed successfully!")
    print("="*70)
    print(f"\n💾 Storage location: {WORKING_DIR}")
    print("\n💡 Tips:")
    print("   - Use gpt-4o for higher quality (slower)")
    print("   - Use gpt-4o-mini for faster processing (default)")
    print("   - Free with GitHub Copilot subscription!")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check GitHub CLI authentication: gh auth status")
        print("   2. Re-authenticate if needed: gh auth login")
        print("   3. Verify LiteLLM fork: uv pip install git+https://github.com/fenghaitao/litellm.git")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
