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

"""Example demonstrating Gemini CLI authentication in ADK Python.

This example shows how to use the ported Gemini CLI authentication logic
to authenticate with Gemini models using various methods:
- OAuth (LOGIN_WITH_GOOGLE)
- API Key (USE_GEMINI)
- Vertex AI (USE_VERTEX_AI)
- Cloud Shell (CLOUD_SHELL)
"""

import asyncio
import os
from google.adk.agents import Agent
from google.adk.auth import AuthType
from google.adk.models import GeminiCLI


async def main():
    """Demonstrate different authentication methods."""
    
    print("Gemini CLI Authentication Example")
    print("=" * 40)
    
    # Example 1: Auto-detect authentication method
    print("\n1. Auto-detecting authentication method...")
    try:
        agent = Agent(
            model=GeminiCLI(model="gemini-2.5-flash"),
            system_instruction="You are a helpful assistant."
        )
        
        response = await agent.run("What authentication method are you using?")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Auto-detection failed: {e}")
    
    # Example 2: Explicit OAuth authentication
    print("\n2. Using OAuth authentication...")
    try:
        agent = Agent(
            model=GeminiCLI(
                model="gemini-2.5-flash",
                auth_type=AuthType.LOGIN_WITH_GOOGLE
                # Device code flow is now used automatically (no port needed)
            ),
            system_instruction="You are a helpful assistant."
        )
        
        response = await agent.run("Hello! Can you tell me about OAuth authentication?")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"OAuth authentication failed: {e}")
    
    # Example 3: API Key authentication (if GEMINI_API_KEY is set)
    if os.environ.get("GEMINI_API_KEY"):
        print("\n3. Using Gemini API Key authentication...")
        try:
            agent = Agent(
                model=GeminiCLI(
                    model="gemini-2.5-flash",
                    auth_type=AuthType.USE_GEMINI
                ),
                system_instruction="You are a helpful assistant."
            )
            
            response = await agent.run("Hello! Can you tell me about API key authentication?")
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"API Key authentication failed: {e}")
    else:
        print("\n3. Skipping API Key authentication (GEMINI_API_KEY not set)")
    
    # Example 4: Vertex AI authentication (if project/location are set)
    if os.environ.get("GOOGLE_CLOUD_PROJECT") and os.environ.get("GOOGLE_CLOUD_LOCATION"):
        print("\n4. Using Vertex AI authentication...")
        try:
            agent = Agent(
                model=GeminiCLI(
                    model="gemini-2.5-flash",
                    auth_type=AuthType.USE_VERTEX_AI
                ),
                system_instruction="You are a helpful assistant."
            )
            
            response = await agent.run("Hello! Can you tell me about Vertex AI authentication?")
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"Vertex AI authentication failed: {e}")
    else:
        print("\n4. Skipping Vertex AI authentication (GOOGLE_CLOUD_PROJECT/GOOGLE_CLOUD_LOCATION not set)")
    
    # Example 5: Cloud Shell authentication (if in Cloud Shell environment)
    if os.environ.get("GOOGLE_CLOUD_SHELL"):
        print("\n5. Using Cloud Shell authentication...")
        try:
            agent = Agent(
                model=GeminiCLI(
                    model="gemini-2.5-flash",
                    auth_type=AuthType.CLOUD_SHELL
                ),
                system_instruction="You are a helpful assistant."
            )
            
            response = await agent.run("Hello! Can you tell me about Cloud Shell authentication?")
            print(f"Response: {response}")
            
        except Exception as e:
            print(f"Cloud Shell authentication failed: {e}")
    else:
        print("\n5. Skipping Cloud Shell authentication (not in Cloud Shell environment)")


def print_environment_info():
    """Print information about the current environment."""
    print("\nEnvironment Information:")
    print("-" * 25)
    
    env_vars = [
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY", 
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_CLOUD_LOCATION",
        "GOOGLE_CLOUD_SHELL",
        "NO_BROWSER",
        "HTTP_PROXY",
        "HTTPS_PROXY"
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: {value}")
        else:
            print(f"{var}: (not set)")


if __name__ == "__main__":
    print_environment_info()
    asyncio.run(main())