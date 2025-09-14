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

"""Validation test for Gemini CLI CodeAssist agent."""

import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from simple_agent import root_agent


async def run_test(prompt: str, description: str):
    """Run a single test with the given prompt."""
    print(f"\n🧪 Test: {description}")
    print(f"Prompt: '{prompt}'")
    print("-" * 50)
    
    app_name = 'test_gemini_codeassist_validation'
    user_id = 'test_user'
    
    try:
        runner = InMemoryRunner(
            agent=root_agent,
            app_name=app_name,
        )
        
        session = await runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text=prompt)]
        )
        
        print("Agent Response: ", end="")
        response_texts = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts and event.content.parts[0].text:
                response_text = event.content.parts[0].text
                response_texts.append(response_text)
                print(response_text, end="", flush=True)
        
        full_response = "".join(response_texts)
        print(f"\n✅ Test completed - Response length: {len(full_response)} chars")
        return full_response
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None


async def main():
    """Run validation tests for the Gemini CLI CodeAssist agent."""
    print("Gemini CLI CodeAssist Agent Validation Tests")
    print("=" * 60)
    
    # Test cases
    tests = [
        ("whether 3 is prime", "Prime number validation (original request)"),
        ("what is 2 + 2?", "Basic arithmetic"),
        ("explain what makes a number prime", "Mathematical concept explanation"),
        ("is 17 prime?", "Another prime number check"),
        ("what is the capital of France?", "General knowledge question"),
    ]
    
    successful_tests = 0
    total_tests = len(tests)
    
    for prompt, description in tests:
        response = await run_test(prompt, description)
        if response and len(response.strip()) > 0:
            successful_tests += 1
        await asyncio.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 60)
    print(f"Validation Summary: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Gemini CLI CodeAssist agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return successful_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)