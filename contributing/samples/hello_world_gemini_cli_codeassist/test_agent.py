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

"""Test script for the Gemini CLI CodeAssist Hello World agent."""

import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import root_agent


async def test_prime_check():
    """Test the agent with the prompt 'whether 3 is prime'."""
    print("Testing Gemini CLI CodeAssist Hello World Agent")
    print("=" * 50)
    print("Test prompt: 'whether 3 is prime'")
    print("=" * 50)
    
    app_name = 'test_gemini_codeassist'
    user_id = 'test_user'
    
    try:
        # Create runner and session
        runner = InMemoryRunner(
            agent=root_agent,
            app_name=app_name,
        )
        
        session = await runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        
        # Create the test prompt
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text='whether 3 is prime')]
        )
        
        print("Agent Response:")
        print("-" * 20)
        
        # Collect response
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
        
        print("\n" + "=" * 50)
        
        # Validate the response
        full_response = "".join(response_texts)
        if full_response:
            print("✅ Test completed successfully!")
            print(f"Response length: {len(full_response)} characters")
            
            # Check if the response contains expected content about prime numbers
            if "3" in full_response and ("prime" in full_response.lower()):
                print("✅ Response contains expected content about 3 and prime numbers")
            else:
                print("⚠️  Response may not contain expected prime number content")
                
        else:
            print("❌ No response received from agent")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_prime_check())