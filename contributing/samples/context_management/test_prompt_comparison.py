#!/usr/bin/env python3
"""
Test both Custom and OpenHands-style prompts to compare their effectiveness
Demonstrates the different summarization strategies available
"""

import asyncio
import os
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from advanced_context_manager import SmartAgent, ContextConfig


async def test_custom_vs_openhands_prompts():
    """Compare Custom vs OpenHands prompt styles"""
    
    print("🚀 Testing Custom vs OpenHands Prompt Styles")
    print("=" * 70)
    
    # Verify API key
    api_key = os.getenv('IFLOW_API_KEY')
    if not api_key:
        print("❌ IFLOW_API_KEY environment variable not set")
        return
    
    print(f"✅ API Key configured: {api_key[:10]}...")
    
    # Test questions to generate substantial conversation
    test_questions = [
        "Help me create a Python web scraper using BeautifulSoup",
        "How do I handle error cases and retry logic in the scraper?",
        "What's the best way to store the scraped data in a database?",
        "How can I make the scraper respect robots.txt and rate limits?",
        "Show me how to deploy this scraper to the cloud"
    ]
    
    # Test both prompt styles
    for style_name, prompt_style in [("CUSTOM", "custom"), ("OPENHANDS", "openhands")]:
        print(f"\n🎯 Testing {style_name} Prompt Style")
        print("=" * 50)
        
        # Create agent with specific prompt style
        base_agent = Agent(
            name=f"test_agent_{style_name.lower()}",
            model="iflow/Qwen3-Coder",
            instruction="You are a helpful Python development assistant.",
            tools=[]
        )
        
        # Configure with low token limit to force condensation
        smart_agent = SmartAgent(base_agent, ContextConfig(
            max_tokens=300,  # Force condensation quickly
            keep_system_messages=1,
            keep_recent_turns=1,
            summarization_model="iflow/Qwen3-Coder",
            enable_memory_storage=True,
            prompt_style=prompt_style  # Use specified prompt style
        ))
        
        print(f"🔧 Prompt style: {prompt_style}")
        print(f"🎯 Token limit: 300 (aggressive condensation)")
        
        # Set up runner
        runner = InMemoryRunner(agent=smart_agent.agent, app_name=f'prompt_test_{style_name.lower()}')
        session = await runner.session_service.create_session(
            app_name=f'prompt_test_{style_name.lower()}', 
            user_id=f'test_user_{style_name.lower()}'
        )
        
        condensation_count = 0
        
        # Process questions
        for i, question in enumerate(test_questions, 1):
            print(f"\n📝 Question {i}: {question[:60]}...")
            
            try:
                content = types.Content(role='user', parts=[types.Part.from_text(text=question)])
                
                async def get_response():
                    async for event in runner.run_async(
                        user_id=f'test_user_{style_name.lower()}',
                        session_id=session.id,
                        new_message=content,
                    ):
                        if event.content and event.content.parts and event.content.parts[0].text:
                            return event.content.parts[0].text
                    return "No response"
                
                response = await asyncio.wait_for(get_response(), timeout=60.0)
                print(f"🤖 Response: {response[:80]}...")
                
                # Check for condensation
                memory = smart_agent.get_memory_summary()
                if "No conversation memories stored yet" not in memory:
                    current_memory_count = len(smart_agent.context_manager.conversation_memory)
                    if current_memory_count > condensation_count:
                        condensation_count = current_memory_count
                        print(f"🔄 CONDENSATION #{condensation_count} using {style_name} style!")
                        
            except asyncio.TimeoutError:
                print(f"⏰ Question {i} timed out")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        # Show final memory for this style
        print(f"\n📚 Final {style_name} Memory Summary:")
        final_memory = smart_agent.get_memory_summary()
        print("-" * 60)
        print(final_memory)
        print("-" * 60)
        
        print(f"✅ {style_name} test completed with {condensation_count} condensations")
    
    print(f"\n🎉 Prompt comparison test completed!")
    print(f"📊 Both styles demonstrated - you can now choose which works better for your use case")


async def main():
    """Main test function"""
    try:
        await test_custom_vs_openhands_prompts()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Context Management Prompt Comparison Test")
    print("This test compares Custom vs OpenHands-style summarization prompts\n")
    
    asyncio.run(main())