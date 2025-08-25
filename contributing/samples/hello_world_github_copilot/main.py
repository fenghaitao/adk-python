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

"""Main script to run the GitHub Copilot Hello World agent."""

import asyncio
import os
import warnings

from google.adk.runners import InMemoryRunner
from google.genai import types

from agent import root_agent


async def main():
  """Main function to run the GitHub Copilot agent."""
  print("GitHub Copilot Hello World Agent")
  print("=" * 40)
  print("This agent can roll dice and check prime numbers using GitHub Copilot models.")
  print("Authentication is handled automatically via OAuth2.")
  print("Try asking: 'Roll a 6-sided die and check if the result is prime'")
  print("Type 'quit' or 'exit' to stop.")
  print("=" * 40)
  
  app_name = 'github_copilot_hello_world'
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
  # Suppress LiteLLM logging warnings
  warnings.filterwarnings("ignore", message="coroutine.*was never awaited")
  
  try:
      asyncio.run(main())
  except KeyboardInterrupt:
      print("\nGoodbye!")
  except Exception as e:
      print(f"Unexpected error: {e}")