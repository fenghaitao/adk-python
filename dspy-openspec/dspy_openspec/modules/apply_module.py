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

"""DSPy module for OpenSpec apply agent.

This module uses ReAct with the ApplySignature to implement
OpenSpec changes following the workflow defined in the instruction markdown.
"""

from __future__ import annotations

from typing import Optional
import dspy

# Maximum iterations for apply agent
# Based on workflow: read docs, implement DML, create tests, validate
# 50 provides buffer for complex devices with multiple files
MAX_APPLY_ITERS = 50

from dspy_openspec.signatures.apply import ApplySignature
from dspy_openspec.tools import get_file_tools
from dspy_openspec.modules.verbose_react import VerboseReAct

try:
  from dspy_openspec.memory.retriever import MemoryRetriever
  MEMORY_AVAILABLE = True
except ImportError:
  MEMORY_AVAILABLE = False


class ApplyModule(dspy.Module):
  """Apply OpenSpec changes to implement Simics devices.
  
  This module follows the apply workflow defined in
  apply_agent_instruction.md, including:
  - Reading change proposal and spec deltas
  - Implementing DML code with register side-effects
  - Creating comprehensive test cases
  - Validation and quality checks
  
  The instruction content is embedded in the ApplySignature docstring.
  Uses ReAct to enable tool calling for file operations.
  
  Optionally integrates memory retrieval to provide relevant knowledge
  from past implementations during the apply process.
  """
  
  def __init__(
      self,
      interactive: bool = True,
      enable_memory: bool = True,
      memory_persist_dir: str = ".chromadb",
      memory_k: int = 3
  ):
    """Initialize the apply module with ReAct and file tools.
    
    Args:
      interactive: Show tool calls and thoughts in real-time
      enable_memory: Enable memory retrieval integration
      memory_persist_dir: Directory where ChromaDB is persisted
      memory_k: Number of memory chunks to retrieve
    """
    super().__init__()
    
    # Initialize memory retriever if enabled
    self.memory_retriever = None
    if enable_memory and MEMORY_AVAILABLE:
      try:
        self.memory_retriever = MemoryRetriever(
          persist_directory=memory_persist_dir,
          k=memory_k
        )
        print(f"✅ Memory retrieval enabled (k={memory_k})")
      except Exception as e:
        print(f"⚠️  Memory retrieval disabled: {e}")
        self.memory_retriever = None
    elif enable_memory and not MEMORY_AVAILABLE:
      print("⚠️  Memory retrieval disabled: chromadb not installed")
    
    # Get base tools
    base_tools = get_file_tools()
    
    # Add memory retrieval tool if available
    if self.memory_retriever:
      base_tools = base_tools + [self._create_memory_tool()]
    
    # Don't wrap tools with monitoring since VerboseReAct shows everything
    tools = base_tools
    
    # Use VerboseReAct for interactive mode, regular ReAct otherwise
    if interactive:
      self.apply = VerboseReAct(
        ApplySignature,
        tools=tools,
        max_iters=MAX_APPLY_ITERS
      )
    else:
      self.apply = dspy.ReAct(
        ApplySignature,
        tools=tools,
        max_iters=MAX_APPLY_ITERS
      )
  
  def _create_memory_tool(self):
    """Create a memory retrieval tool for the agent.
    
    Returns:
      Tool function that retrieves relevant memories
    """
    def retrieve_memory(
        task_description: str,
        error_context: str = "",
        category: Optional[str] = None
    ) -> str:
      """Retrieve relevant knowledge from past implementations.
      
      Use this tool to search for relevant examples, patterns, and
      solutions from previous Simics device implementations.
      
      Args:
        task_description: What you're trying to implement or solve
        error_context: Any error messages or failures (optional)
        category: Filter by DML, Test, or General (optional)
      
      Returns:
        Relevant knowledge chunks from memory
      """
      result = self.memory_retriever.forward(
        task_description=task_description,
        error_context=error_context,
        category=category
      )
      
      if result.passages:
        output = f"Found {len(result.passages)} relevant memories:\n\n"
        for i, passage in enumerate(result.passages, 1):
          output += f"--- Memory {i} ---\n{passage}\n\n"
        return output
      else:
        return "No relevant memories found for this query."
    
    return retrieve_memory
  
  def forward(self, change_id: str) -> dspy.Prediction:
    """Apply the specified change.
    
    Args:
      change_id: Change ID to apply (from proposal phase)
      
    Returns:
      Prediction with implementation_status, files_modified, and
      validation_result fields
    """
    print("🤖 Starting ReAct reasoning loop for apply...")
    print(f"   Max iterations: {MAX_APPLY_ITERS}")
    print("   The agent will show thoughts, actions, and observations\n")
    
    import sys
    sys.stdout.flush()
    
    try:
      result = self.apply(change_id=change_id)
    except Exception as e:
      print(f"\n❌ Error during apply: {type(e).__name__}: {e}")
      import traceback
      traceback.print_exc()
      raise
    
    # Log iteration usage for monitoring
    if hasattr(result, 'trajectory') and result.trajectory:
      iter_count = sum(1 for k in result.trajectory.keys() if k.startswith('thought_'))
      print(f"\n✓ Completed in {iter_count}/{MAX_APPLY_ITERS} iterations")
      if iter_count > MAX_APPLY_ITERS * 0.8:
        print(f"⚠️  Warning: Used {iter_count}/{MAX_APPLY_ITERS} iterations (>80%)")
        print("   Consider increasing MAX_APPLY_ITERS if this fails frequently")
    
    return result
