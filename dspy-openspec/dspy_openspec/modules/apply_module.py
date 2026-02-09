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

import dspy

# Maximum iterations for apply agent
# Based on workflow: read docs, implement DML, create tests, validate
# Increased to 100 to provide sufficient buffer for:
# - Reading multiple spec delta files
# - Implementing DML and Python tests (two languages)
# - Build and test cycles with error recovery
# - Complex devices with multiple files
MAX_APPLY_ITERS = 100

from dspy_openspec.signatures.apply import ApplySignature
from dspy_openspec.tools import get_file_tools
from dspy_openspec.modules.verbose_react import VerboseReAct


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
  """
  
  def __init__(self, interactive: bool = True):
    """Initialize the apply module with ReAct and file tools.
    
    Args:
      interactive: Show tool calls and thoughts in real-time
    """
    super().__init__()
    
    # Get base tools
    base_tools = get_file_tools()
    
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
