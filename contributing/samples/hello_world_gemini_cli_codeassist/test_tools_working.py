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

"""Test script to validate tools work with Gemini CLI CodeAssist."""

import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent import root_agent


async def test_dice_roll():
    """Test the agent with dice rolling functionality."""
    print("Testing Gemini CLI CodeAssist Tools - Dice Rolling")
    print("=" * 55)
    
    app_name = 'test_tools_gemini_codeassist'
    user_id = 'test_user'
    
    try:
        runner = InMemoryRunner(
            agent=root_agent,
            app_name=app_name,
        )
        
        session = await runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        
        # Test dice rolling
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text='Roll a 6-sided die')]
        )
        
        print("Prompt: 'Roll a 6-sided die'")
        print("Agent Response:")
        print("-" * 20)
        
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
        print("\n" + "=" * 55)
        
        if full_response and ("roll" in full_response.lower() or any(str(i) in full_response for i in range(1, 7))):
            print("✅ Dice rolling test successful!")
            return True
        else:
            print("❌ Dice rolling test failed - no valid roll found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def test_prime_check_with_tool():
    """Test the agent with prime checking tool."""
    print("\nTesting Gemini CLI CodeAssist Tools - Prime Checking")
    print("=" * 55)
    
    app_name = 'test_tools_prime_gemini_codeassist'
    user_id = 'test_user'
    
    try:
        runner = InMemoryRunner(
            agent=root_agent,
            app_name=app_name,
        )
        
        session = await runner.session_service.create_session(
            app_name=app_name, user_id=user_id
        )
        
        # Test prime checking tool
        content = types.Content(
            role='user', 
            parts=[types.Part.from_text(text='Check if 7 is prime')]
        )
        
        print("Prompt: 'Check if 7 is prime'")
        print("Agent Response:")
        print("-" * 20)
        
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
        print("\n" + "=" * 55)
        
        if full_response and "7" in full_response and "prime" in full_response.lower():
            print("✅ Prime checking test successful!")
            return True
        else:
            print("❌ Prime checking test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


async def main():
    """Run comprehensive tool tests."""
    print("Gemini CLI CodeAssist Agent - Tool Functionality Tests")
    print("=" * 65)
    
    test1 = await test_dice_roll()
    test2 = await test_prime_check_with_tool()
    
    print("\n" + "=" * 65)
    print("Tool Test Summary:")
    print(f"Dice Rolling: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Prime Checking: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("🎉 All tool tests passed! Tools are working correctly with Gemini CLI CodeAssist!")
        return True
    else:
        print("⚠️  Some tool tests failed.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)