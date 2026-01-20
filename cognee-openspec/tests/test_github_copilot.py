#!/usr/bin/env python3
"""Test GitHub Copilot for both LLM and embeddings."""

import os
import asyncio
import sys

# Set up GitHub Copilot configuration
os.environ["LLM_MODEL"] = "github_copilot/gpt-4o"
os.environ["LLM_PROVIDER"] = "custom"
os.environ["EMBEDDING_MODEL"] = "github_copilot/text-embedding-3-small"
os.environ["EMBEDDING_DIMENSIONS"] = "1536"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["LOG_LEVEL"] = "ERROR"

print("🧪 Testing GitHub Copilot (LLM + Embeddings)...")
print(f"   LLM Model: {os.environ['LLM_MODEL']}")
print(f"   Embedding Model: {os.environ['EMBEDDING_MODEL']}")
print()

async def test_llm():
    """Test GitHub Copilot LLM."""
    try:
        from cognee.infrastructure.llm.structured_output_framework.litellm_instructor.llm.get_llm_client import get_llm_client
        from pydantic import BaseModel
        
        print("📡 Testing LLM (GitHub Copilot GPT-4o)...")
        
        client = get_llm_client()
        print(f"✅ LLM Client: {client.__class__.__name__}")
        
        class SimpleResponse(BaseModel):
            summary: str
            language: str
        
        response = await client.acreate_structured_output(
            text_input="What is DML in Simics?",
            system_prompt="Provide a brief summary.",
            response_model=SimpleResponse
        )
        
        print(f"✅ LLM Response: {response.summary[:80]}...")
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
        
        print("\n📊 Testing Embeddings (GitHub Copilot)...")
        
        engine = get_embedding_engine()
        print(f"✅ Embedding Engine: {engine.__class__.__name__}")
        
        # Test embedding
        text = "DML is a device modeling language"
        embeddings = await engine.embed_text([text])
        
        print(f"✅ Generated embedding: dimension={len(embeddings[0])}")
        return True
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    llm_ok = await test_llm()
    embed_ok = await test_embeddings()
    
    print("\n" + "="*60)
    if llm_ok and embed_ok:
        print("🎉 All tests PASSED!")
        print("   GitHub Copilot is ready for both LLM and embeddings")
        return True
    else:
        print("❌ Some tests failed")
        if not llm_ok:
            print("   - LLM test failed")
        if not embed_ok:
            print("   - Embedding test failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
