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

"""DSPy module for OpenSpec proposal generation.

This module uses ReAct with tools to generate OpenSpec proposals following
the workflow defined in the instruction markdown.
"""

from __future__ import annotations

import dspy

# Maximum iterations for proposal generation
# Based on workflow analysis: typical proposals need 18-22 iterations
# 30 provides 35% buffer for quality checks and complex scenarios
MAX_PROPOSAL_ITERS = 30

from dspy_openspec.signatures.proposal import ProposalSignature
from dspy_openspec.tools import (
  read_file,
  write_file,
  list_directory,
  file_exists
)
from dspy_openspec.modules.verbose_react import VerboseReAct


class ProposalModule(dspy.Module):
  """Generate OpenSpec proposals for Simics device implementations.
  
  This module follows the proposal workflow defined in
  proposal_initial_agent_instruction.md, including:
  - Reading OpenSpec workflow documentation
  - Creating proposal and spec deltas
  - Quality checks (coverage, tasks, context)
  - Validation
  
  Uses ReAct pattern with tools for file operations.
  """
  
  def __init__(self, interactive: bool = True):
    """Initialize the proposal module.
    
    Args:
      interactive: Show thoughts, actions, and observations in real-time
    """
    super().__init__()
    
    # Get base tools
    tools = [read_file, write_file, list_directory, file_exists]
    
    # Use VerboseReAct for interactive mode, regular ReAct otherwise
    if interactive:
      self.generate = VerboseReAct(
        signature=ProposalSignature,
        tools=tools,
        max_iters=MAX_PROPOSAL_ITERS
      )
    else:
      self.generate = dspy.ReAct(
        signature=ProposalSignature,
        tools=tools,
        max_iters=MAX_PROPOSAL_ITERS
      )
  
  def forward(
      self,
      task_description: str,
      device_hint: str = ""
  ) -> dspy.Prediction:
    """Generate a proposal for the given task.
    
    Args:
      task_description: Task description or /proposal command
      device_hint: Optional device name hint for change ID generation
      
    Returns:
      Prediction with change_id and summary fields
    """
    print("🤖 Starting ReAct reasoning loop for proposal...")
    print(f"   Max iterations: {MAX_PROPOSAL_ITERS}")
    print("   The agent will show thoughts, actions, and observations\n")
    
    result = self.generate(
      task_description=task_description,
      device_hint=device_hint
    )
    
    # Log iteration usage for monitoring
    if hasattr(result, 'trajectory') and result.trajectory:
      iter_count = sum(1 for k in result.trajectory.keys() if k.startswith('thought_'))
      print(f"\n✓ Completed in {iter_count}/{MAX_PROPOSAL_ITERS} iterations")
      if iter_count > MAX_PROPOSAL_ITERS * 0.8:
        print(f"⚠️  Warning: Used {iter_count}/{MAX_PROPOSAL_ITERS} iterations (>80%)")
        print("   Consider increasing MAX_PROPOSAL_ITERS if this fails frequently")
    
    return result
