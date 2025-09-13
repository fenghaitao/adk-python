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

from google.adk import Agent
from google.adk.models import GeminiCLICodeAssist


# Simple agent without tools - compatible with Gemini CLI CodeAssist
root_agent = Agent(
    model=GeminiCLICodeAssist(model="gemini-2.5-flash"),
    name='hello_codeassist_agent',
    description='Simple hello world agent using Gemini CLI CodeAssist for basic validation',
    instruction="""
    You are a helpful assistant that can answer questions about mathematics, programming, 
    and general topics. You should provide clear, accurate, and helpful responses.
    
    When asked about prime numbers, explain what makes a number prime and whether 
    the given number meets those criteria.
    
    When asked about mathematical operations, show your reasoning clearly.
    """,
)


async def main():
    """Main function to run the Gemini CLI CodeAssist Hello World agent."""
    print("Gemini CLI CodeAssist Hello World Agent")
    print("=" * 45)
    print("This agent demonstrates basic Gemini CLI CodeAssist functionality.")
    print("Try asking: 'whether 3 is prime' or 'what is 2 + 2?'")
    print("Type 'quit' or 'exit' to stop.")
    print("=" * 45)
    
    from google.adk.runners import InMemoryRunner
    
    app_name = 'gemini_codeassist_hello_world'
    user_id = 'test_user'
    
    runner = InMemoryRunner(
        agent=root_agent,
        app_name=app_name,
    )
    
    session = await runner.session_service.create_session(
        app_name=app_name, user_id=user_id
    )
    
    # Interactive loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
                
            from google.genai import types
            content = types.Content(
                role='user', parts=[types.Part.from_text(text=user_input)]
            )
            
            print("Agent: ", end="", flush=True)
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=content,
            ):
                if event.content.parts and event.content.parts[0].text:
                    print(event.content.parts[0].text, end="", flush=True)
            print()  # New line after response
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Unexpected error: {e}")