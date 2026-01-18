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

"""Example: Apply agent with memory retrieval integration.

This example demonstrates how to use the ApplyModule with
memory retrieval enabled to leverage past implementation knowledge.

Prerequisites:
1. Index memories: dspy-memory index openspec-memories
2. Configure LM: export OPENAI_API_KEY=your_key
3. Have a change ready: openspec list

Usage:
  python examples/apply_with_memory.py --change-id <id>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import dspy
from dspy_openspec.modules.apply_module import ApplyModule
from dspy_openspec.config.lm_config import configure_lm


def main():
  """Run apply agent with memory retrieval."""
  parser = argparse.ArgumentParser(
    description="Apply OpenSpec changes with memory retrieval"
  )
  parser.add_argument(
    "--change-id",
    required=True,
    help="Change ID to apply"
  )
  parser.add_argument(
    "--model",
    default="openai/gpt-4",
    help="Language model to use"
  )
  parser.add_argument(
    "--no-memory",
    action="store_true",
    help="Disable memory retrieval"
  )
  parser.add_argument(
    "--memory-dir",
    default=".chromadb",
    help="ChromaDB persist directory"
  )
  parser.add_argument(
    "--memory-k",
    type=int,
    default=3,
    help="Number of memory chunks to retrieve"
  )
  
  args = parser.parse_args()
  
  # Configure language model
  print(f"🔧 Configuring language model: {args.model}")
  configure_lm(args.model)
  
  # Initialize apply module with memory
  print(f"\n🚀 Initializing apply module...")
  print(f"   Memory: {'enabled' if not args.no_memory else 'disabled'}")
  if not args.no_memory:
    print(f"   Memory dir: {args.memory_dir}")
    print(f"   Memory k: {args.memory_k}")
  
  apply_module = ApplyModule(
    interactive=True,
    enable_memory=not args.no_memory,
    memory_persist_dir=args.memory_dir,
    memory_k=args.memory_k
  )
  
  # Execute apply
  print(f"\n📝 Applying change: {args.change_id}\n")
  print("=" * 80)
  
  try:
    result = apply_module(change_id=args.change_id)
    
    print("\n" + "=" * 80)
    print("\n✅ Apply completed!")
    print(f"\nStatus: {result.implementation_status}")
    print(f"Files modified: {result.files_modified}")
    print(f"Validation: {result.validation_result}")
    print(f"Completed: {result.completed}")
    
    return 0 if result.completed else 1
    
  except Exception as e:
    print("\n" + "=" * 80)
    print(f"\n❌ Apply failed: {e}")
    import traceback
    traceback.print_exc()
    return 1


if __name__ == "__main__":
  sys.exit(main())
