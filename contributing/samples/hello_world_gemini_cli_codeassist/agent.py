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

import random

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.models import GeminiCLICodeAssist
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.genai import types
import os


def roll_die(sides: int, tool_context: ToolContext) -> int:
  """Roll a die and return the rolled result.

  Args:
    sides: The integer number of sides the die has.

  Returns:
    An integer of the result of rolling the die.
  """
  result = random.randint(1, sides)
  if not 'rolls' in tool_context.state:
    tool_context.state['rolls'] = []

  tool_context.state['rolls'] = tool_context.state['rolls'] + [result]
  return result


async def check_prime(nums: list[int]) -> str:
  """Check if a given list of numbers are prime.

  Args:
    nums: The list of numbers to check.

  Returns:
    A str indicating which number is prime.
  """
  primes = set()
  for number in nums:
    number = int(number)
    if number <= 1:
      continue
    is_prime = True
    for i in range(2, int(number**0.5) + 1):
      if number % i == 0:
        is_prime = False
        break
    if is_prime:
      primes.add(number)
  return (
      'No prime numbers found.'
      if not primes
      else f"{', '.join(str(num) for num in primes)} are prime numbers."
  )


# Configure MCP file system tools
# Using SSE connection to local filesystem server
file_tools = MCPToolset(
    connection_params=SseConnectionParams(
        url='http://localhost:3000/sse',
        headers={'Accept': 'text/event-stream'},
        timeout=10.0
    ),
    tool_filter=[
        'read_file',                # Read file contents
        'list_directory',           # List files and folders
        'write_file',              # Create/edit files
        'get_cwd',                 # Get current working directory
        'list_allowed_directories', # Show allowed directories
    ]
)


root_agent = Agent(
    model=GeminiCLICodeAssist(model="gemini-2.5-flash"),
    name='hello_codeassist_agent',
    description=(
        'hello world agent that can roll a dice of 8 sides and check prime'
        ' numbers using Gemini CLI CodeAssist.'
    ),
    instruction="""
      You are a helpful assistant that can:
      1. Roll dice and answer questions about the outcome of dice rolls
      2. Check if numbers are prime
      3. Read and work with files in the workspace
      
      DICE ROLLING:
      - You can roll dice of different sizes
      - When asked to roll a die, call the roll_die tool with the number of sides (integer)
      - You should never roll a die on your own
      
      PRIME CHECKING:
      - Call the check_prime tool with a list of integers
      - You should not check prime numbers before calling the tool
      
      FILE OPERATIONS:
      - You can read files when users ask about file contents
      - You can list directory contents to help users understand project structure
      - You can write files when users need to create or modify files
      - You can get the current working directory
      - You can check which directories are allowed for file operations
      - Always be helpful with file-related requests
      
      IMPORTANT: File operations require the filesystem server to be running.
      If file operations fail, remind the user to start the server with:
      python filesystem_server.py
      
      PARALLEL TOOLS:
      - You can use multiple tools in parallel by calling functions in parallel (in one request and in one round)
      
      When rolling dice and checking primes together:
      1. First call roll_die tool and wait for response
      2. Then call check_prime tool with the result
      3. Include the roll result in your response
    """,
    tools=[
        roll_die,
        check_prime,
        file_tools,  # Add file system capabilities
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
