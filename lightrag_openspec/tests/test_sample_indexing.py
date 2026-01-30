"""Integration test for indexing and querying with sample_book.txt."""

import pytest
from pathlib import Path

from lightrag import LightRAG, QueryParam
from lightrag.llm.llama_index_impl import (
    llama_index_complete_if_cache,
    llama_index_embed,
)
from lightrag.utils import EmbeddingFunc
from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

LLM_MODEL = "github_copilot/gpt-4o-mini"
EMBEDDING_MODEL = "github_copilot/text-embedding-3-small"
EMBEDDING_DIM = 1536


async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    """LLM function using GitHub Copilot."""
    if "llm_instance" not in kwargs:
        kwargs["llm_instance"] = LiteLLM(
            model=LLM_MODEL,
            api_key="oauth2",
            temperature=0.7,
        )
    return await llama_index_complete_if_cache(
        kwargs["llm_instance"], prompt, system_prompt, history_messages
    )


async def embedding_func(texts):
    """Embedding function using GitHub Copilot."""
    embed_model = LiteLLMEmbedding(
        model_name=EMBEDDING_MODEL,
        api_key="oauth2",
    )
    return await llama_index_embed(texts, embed_model=embed_model)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.requires_api
@pytest.mark.asyncio
async def test_sample_book_indexing(temp_storage_dir, sample_book_path, sample_book_content):
    """Test indexing and querying with sample_book.txt."""
    
    print("\n" + "="*70)
    print("📚 Testing LightRAG with sample_book.txt")
    print("="*70)
    print()
    
    print(f"📖 Reading: {sample_book_path}")
    print(f"   Length: {len(sample_book_content)} characters")
    print()
    
    # Initialize LightRAG
    print("🔧 Initializing LightRAG...")
    rag = LightRAG(
        working_dir=temp_storage_dir,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=EMBEDDING_DIM,
            max_token_size=8192,
            func=embedding_func,
        ),
        llm_model_name=LLM_MODEL,
        llm_model_max_async=4,
        embedding_func_max_async=4,
    )
    
    await rag.initialize_storages()
    print("✅ Initialized")
    print()
    
    # Index the book
    print("📝 Indexing sample_book.txt...")
    await rag.ainsert(sample_book_content, ids="sample_book")
    print("✅ Indexed")
    print()
    
    # Test queries
    queries = [
        "What is the story about?",
        "What is LightRAG?",
        "What is ADK?",
        "What happens when ADK and LightRAG are combined?",
    ]
    
    print("🔍 Testing Queries:")
    print("-" * 70)
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] ❓ {query}")
        
        try:
            result = await rag.aquery(query, param=QueryParam(mode="hybrid"))
            print(f"💡 {result[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("-" * 70)
    
    # Get entities
    try:
        labels = await rag.get_graph_labels()
        if labels:
            print(f"\n🕸️  Extracted Entities: {len(labels)}")
            print(f"   {', '.join(list(labels)[:10])}")
            if len(labels) > 10:
                print(f"   ... and {len(labels) - 10} more")
    except Exception as e:
        print(f"⚠️  Could not retrieve entities: {e}")
    
    # Cleanup
    await rag.finalize_storages()
    
    print()
    print("="*70)
    print("✅ Test Complete!")
    print("="*70)
    print()
    print(f"💾 Storage: {temp_storage_dir}")
    print(f"📖 Source: {sample_book_path}")
    print()
