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

"""Test script to verify LLM model configuration."""

from __future__ import annotations

import os
import sys


def check_env_var(name: str, required: bool = True) -> tuple[bool, str]:
  """Check if environment variable is set."""
  value = os.getenv(name)
  if value:
    # Mask API keys
    if "KEY" in name or "TOKEN" in name:
      display_value = f"{value[:10]}..." if len(value) > 10 else "***"
    else:
      display_value = value
    return True, display_value
  elif required:
    return False, "NOT SET (required)"
  else:
    return False, "not set (optional)"


def main():
  """Check model configuration."""
  print("🔍 Checking Cognee-OpenSpec Model Configuration\n")
  
  # Check LLM configuration
  print("📝 LLM Configuration:")
  checks = [
    ("LLM_API_KEY", True),
    ("LLM_MODEL", False),
    ("LLM_ENDPOINT", False),
    ("LLM_PROVIDER", False),
    ("LLM_MAX_TOKENS", False),
  ]
  
  all_good = True
  for var_name, required in checks:
    is_set, value = check_env_var(var_name, required)
    status = "✅" if is_set or not required else "❌"
    print(f"  {status} {var_name}: {value}")
    if required and not is_set:
      all_good = False
  
  print("\n📊 Embedding Configuration:")
  embed_checks = [
    ("EMBEDDING_API_KEY", False),
    ("EMBEDDING_MODEL", False),
    ("EMBEDDING_ENDPOINT", False),
    ("EMBEDDING_DIMENSIONS", False),
  ]
  
  for var_name, required in embed_checks:
    is_set, value = check_env_var(var_name, required)
    status = "✅" if is_set else "ℹ️"
    print(f"  {status} {var_name}: {value}")
  
  print("\n🔧 Other Settings:")
  other_checks = [
    ("ENABLE_BACKEND_ACCESS_CONTROL", False),
    ("LOG_LEVEL", False),
  ]
  
  for var_name, required in other_checks:
    is_set, value = check_env_var(var_name, required)
    status = "✅" if is_set else "ℹ️"
    print(f"  {status} {var_name}: {value}")
  
  # Determine model type
  print("\n🤖 Detected Configuration:")
  llm_model = os.getenv("LLM_MODEL", "")
  llm_endpoint = os.getenv("LLM_ENDPOINT", "")
  
  if "dashscope" in llm_model or "iflow" in llm_endpoint:
    print("  Model Type: iflow (Alibaba Cloud)")
    print("  Endpoint: https://apis.iflow.cn/v1/")
    print("  Recommended models: qwen3-coder-plus (best for code), qwen-turbo, qwen-max")
  elif "github_copilot" in llm_model:
    print("  Model Type: GitHub Copilot")
    print("  Authentication: OAuth via GitHub CLI")
    print("  Recommended models: gpt-4o, gpt-4")
  elif "openai" in llm_model or not llm_model:
    print("  Model Type: OpenAI (default)")
    print("  Recommended models: gpt-4o-mini, gpt-4o")
  else:
    print(f"  Model Type: Custom ({llm_model})")
  
  # Final verdict
  print("\n" + "="*60)
  if all_good:
    print("✅ Configuration looks good!")
    print("\n🚀 Next steps:")
    print("  1. Index memories:")
    print("     cognee-memory index openspec-memories --visualize")
    print("  2. Search:")
    print("     cognee-memory search 'What is DML?'")
  else:
    print("❌ Configuration incomplete!")
    print("\n💡 Quick setup:")
    print("  OpenAI:")
    print("    export LLM_API_KEY='sk-your-key'")
    print("  iflow:")
    print("    ./setup_iflow.sh your-iflow-key")
    print("  GitHub Copilot:")
    print("    ./setup_github_copilot.sh")
    print("\n📖 See MODEL_SETUP.md for detailed instructions")
    sys.exit(1)


if __name__ == "__main__":
  main()
