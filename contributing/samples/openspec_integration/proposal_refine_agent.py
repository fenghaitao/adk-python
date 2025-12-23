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

"""ProposalRefineAgent for creating OpenSpec proposals for refinements/enhancements.

This agent focuses on the Proposal phase for REFINEMENTS (working code → enhanced code).
It follows openspec-commands/proposal.md and is specialized for Simics device enhancements.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

# Import ADK
try:
  from google.adk.agents.llm_agent import LlmAgent
except ImportError:
  current_dir = Path(__file__).parent
  adk_src_dir = current_dir.parent.parent.parent / "src"
  if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))
    from google.adk.agents.llm_agent import LlmAgent

try:
  from .openspec_tools import create_openspec_toolset
except ImportError:
  from openspec_tools import create_openspec_toolset

# Simics MCP tools are optional for proposal
create_simics_mcp_toolset = None  # Optional

def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class ProposalResult(BaseModel):
  """Structured result for /proposal slash command."""
  change_id: str
  summary: Optional[str] = None


class ProposalRefineAgent(LlmAgent):
  """Agent specialized for OpenSpec Proposal phase - REFINEMENTS."""

  def __init__(self, **kwargs):
    # Load instruction from external file
    instruction_file = Path(__file__).parent / "proposal_refine_agent_instruction.md"
    try:
      instruction = instruction_file.read_text()
    except FileNotFoundError:
      raise RuntimeError(
        f"Proposal_Refine agent instruction file not found: {instruction_file}"
      )

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())

    # Add Simics MCP toolset (RAG/build/test utilities) if available
    if create_simics_mcp_toolset:
      try:
        tools.append(create_simics_mcp_toolset())
        print("✓ Simics MCP tools integrated for proposal phase")
      except Exception as e:
        print(f"ℹ Simics MCP toolset not available for proposal: {e}")

    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "proposal_refine_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description="Agent specialized for creating OpenSpec proposals for refinements/enhancements",
      output_schema=ProposalResult,
      **kwargs,
    )


# Create the proposal refine agent instance for ADK discovery
proposal_refine_agent = ProposalRefineAgent(name="proposal_refine_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = proposal_refine_agent
