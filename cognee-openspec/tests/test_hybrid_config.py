#!/usr/bin/env python3
"""Test hybrid configuration: iflow LLM + GitHub Copilot embeddings."""

import os
import asyncio
import sys

# Set up hybrid configuration
os.environ["LLM_API_KEY"] = "sk-7b379fee9dea264d691818b5fc5fd493"
os.environ["LLM_MODEL"] = "dashscope/qwen3-coder-plus"
os.environ["LLM_ENDPOINT"] = "https://apis.iflow.cn/v1/"
os.environ["LLM_PROVIDER"] = "custom"
os.environ["EMBEDDING_MODEL"] = "github_copilot/text-embedding-3-small"
os.environ["EMBEDDING_DIMENSIONS"] = "1536"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["LOG_LEVEL"] = "ERROR"

print("🧪 Testing Hybrid Configuration")
print("="*60)
print("   LLM: iflow qwen3-coder-plus")
print("   Embeddings: GitHub Copilot text-embedding-3-small")
print("="*60)
print()

async def test_llm():
    """Test iflow LLM."""
    try:
        from cognee.infrastructure.llm.structured_output_framework.litellm_instructor.llm.get_llm_client import get_llm_client
        from pydantic import BaseModel
        
        print("📡 Testing LLM (iflow qwen3-coder-plus)...")
        
        client = get_llm_client()
        print(f"   Client: {client.__class__.__name__}")
        print(f"   Provider: {client.name if hasattr(client, 'name') else 'N/A'}")
        print(f"   Model: {client.model if hasattr(client, 'model') else 'N/A'}")
        
        class SimpleResponse(BaseModel):
            summary: str
            language: str
        
        response = await client.acreate_structured_output(
            text_input="What is DML in Simics device modeling?",
            system_prompt="Provide a brief summary in 1-2 sentences.",
            response_model=SimpleResponse
        )
        
        print(f"✅ LLM Response:")
        print(f"   Summary: {response.summary[:100]}...")
        print(f"   Language: {response.language}")
        print()
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_embeddings():
    """Test GitHub Copilot embeddings."""
    try:
        from cognee.infrastructure.databases.vector.embeddings.get_embedding_engine import get_embedding_engine
        
        print("📊 Testing Embeddings (GitHub Copilot)...")
        
        engine = get_embedding_engine()
        print(f"   Engine: {engine.__class__.__name__}")
        print(f"   Model: {engine.model if hasattr(engine, 'model') else 'N/A'}")
        
        # Test embedding
        texts = [
            "DML is a device modeling language for Simics",
            "Test cases validate device behavior"
        ]
        
        print(f"   Embedding {len(texts)} texts...")
        embeddings = await engine.embed_text(texts)
        
        print(f"✅ Embeddings generated:")
        print(f"   Count: {len(embeddings)}")
        print(f"   Dimensions: {len(embeddings[0])}")
        print(f"   First embedding sample: [{embeddings[0][0]:.4f}, {embeddings[0][1]:.4f}, ...]")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("Starting tests...\n")
    
    llm_ok = await test_llm()
    embed_ok = await test_embeddings()
    
    print("="*60)
    if llm_ok and embed_ok:
        print("🎉 HYBRID CONFIGURATION TEST PASSED!")
        print()
        print("✅ iflow LLM: Working")
        print("✅ GitHub Copilot Embeddings: Working")
        print()
        print("🚀 Ready to index OpenSpec memories!")
        print()
        print("Next step:")
        print("  ../.venv/bin/cognee-memory index ../openspec-memories --visualize")
        return True
    else:
        print("❌ HYBRID CONFIGURATION TEST FAILED")
        print()
        if not llm_ok:
            print("   ❌ iflow LLM test failed")
        if not embed_ok:
            print("   ❌ GitHub Copilot Embeddings test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
