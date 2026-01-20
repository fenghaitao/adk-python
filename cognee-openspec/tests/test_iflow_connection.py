#!/usr/bin/env python3
"""Quick test to verify iflow connection works."""

import os
import asyncio
import sys

# Set up iflow configuration
os.environ["LLM_API_KEY"] = "sk-7b379fee9dea264d691818b5fc5fd493"
os.environ["LLM_MODEL"] = "dashscope/qwen3-coder-plus"
os.environ["LLM_ENDPOINT"] = "https://apis.iflow.cn/v1/"
os.environ["LLM_PROVIDER"] = "custom"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["LOG_LEVEL"] = "ERROR"

print("🧪 Testing iflow connection with qwen3-coder-plus...")
print(f"   Model: {os.environ['LLM_MODEL']}")
print(f"   Endpoint: {os.environ['LLM_ENDPOINT']}")
print()

async def test_connection():
    """Test basic LLM connection."""
    try:
        # Import after setting env vars
        from cognee.infrastructure.llm.structured_output_framework.litellm_instructor.llm.get_llm_client import get_llm_client
        
        print("📡 Getting LLM client...")
        client = get_llm_client()
        print(f"✅ Client created: {client.__class__.__name__}")
        print(f"   Provider: {client.name if hasattr(client, 'name') else 'N/A'}")
        print(f"   Model: {client.model if hasattr(client, 'model') else 'N/A'}")
        print()
        
        # Test a simple structured output
        from pydantic import BaseModel
        
        class SimpleResponse(BaseModel):
            summary: str
            language: str
        
        print("🤖 Testing LLM call...")
        print("   Query: What is DML?")
        
        response = await client.acreate_structured_output(
            text_input="What is DML in the context of Simics device modeling?",
            system_prompt="You are a helpful assistant. Provide a brief summary.",
            response_model=SimpleResponse
        )
        
        print()
        print("✅ LLM Response:")
        print(f"   Summary: {response.summary[:100]}...")
        print(f"   Language: {response.language}")
        print()
        print("🎉 iflow connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
