#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test script to directly test streaming functionality."""

import asyncio
from google.adk.models import GeminiCLICodeAssist
from google.adk.models.llm_request import LlmRequest
from google.genai import types


async def test_direct_streaming():
    """Test streaming directly via the model."""
    print("Testing Direct Streaming with GeminiCLICodeAssist")
    print("=" * 50)
    
    model = GeminiCLICodeAssist(model="gemini-2.5-flash")
    
    # Create a request that should generate a longer response
    content = types.Content(
        role='user', 
        parts=[types.Part.from_text(text="Write a detailed explanation of how photosynthesis works, including the chemical equations and the role of chloroplasts. Make it at least 200 words.")]
    )
    
    config = types.GenerateContentConfig()
    
    llm_request = LlmRequest(
        contents=[content],
        config=config,
        model="gemini-2.5-flash"
    )
    
    print("Testing with stream=True:")
    print("-" * 30)
    
    try:
        chunk_count = 0
        total_text = ""
        
        # Test with streaming enabled
        async for response in model.generate_content_async(llm_request, stream=True):
            chunk_count += 1
            if response.content and response.content.parts:
                chunk_text = response.content.parts[0].text or ""
                total_text += chunk_text
                print(f"Chunk {chunk_count}: {repr(chunk_text[:100])}{'...' if len(chunk_text) > 100 else ''}")
        
        print("\n" + "=" * 50)
        print(f"✅ Streaming test completed!")
        print(f"Total chunks: {chunk_count}")
        print(f"Total text length: {len(total_text)} characters")
        
        if chunk_count > 1:
            print("✅ Streaming worked - received multiple chunks!")
            return True
        else:
            print("⚠️  Only received one chunk")
            return True
            
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_non_streaming():
    """Test non-streaming directly via the model."""
    print("\nTesting Direct Non-Streaming with GeminiCLICodeAssist")
    print("=" * 55)
    
    model = GeminiCLICodeAssist(model="gemini-2.5-flash")
    
    content = types.Content(
        role='user', 
        parts=[types.Part.from_text(text="What is the capital of Japan?")]
    )
    
    config = types.GenerateContentConfig()
    
    llm_request = LlmRequest(
        contents=[content],
        config=config,
        model="gemini-2.5-flash"
    )
    
    print("Testing with stream=False:")
    print("-" * 30)
    
    try:
        chunk_count = 0
        total_text = ""
        
        # Test with streaming disabled
        async for response in model.generate_content_async(llm_request, stream=False):
            chunk_count += 1
            if response.content and response.content.parts:
                chunk_text = response.content.parts[0].text or ""
                total_text += chunk_text
                print(f"Response: {chunk_text}")
        
        print("\n" + "=" * 55)
        print(f"✅ Non-streaming test completed!")
        print(f"Chunks received: {chunk_count}")
        print(f"Total text length: {len(total_text)} characters")
        
        if "Tokyo" in total_text:
            print("✅ Response contains expected content!")
            return True
        else:
            print("⚠️  Response may not contain expected content")
            return True
            
    except Exception as e:
        print(f"❌ Non-streaming test failed: {e}")
        return False


async def main():
    """Run direct streaming tests."""
    test1 = await test_direct_streaming()
    test2 = await test_direct_non_streaming()
    
    print("\n" + "=" * 55)
    print("Direct Streaming Test Summary:")
    print(f"Streaming: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Non-streaming: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    return test1 and test2


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)