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

"""ApplyAgent for executing OpenSpec Apply changes.

This agent focuses on the Apply phase of the OpenSpec workflow. It follows
openspec-commands/apply.md strictly and mirrors the pattern used by other
OpenSpec agents in this sample.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

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

# Simics MCP tools are used heavily during Apply
try:
  from .simics_mcp_tools import create_simics_mcp_toolset
except Exception:
  from simics_mcp_tools import create_simics_mcp_toolset

def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class ApplyResult(BaseModel):
  """Structured result for /apply slash command."""
  change_id: str
  status: str  # "completed", "partial", "failed"
  completed_tasks: List[str]
  remaining_tasks: List[str]
  errors: Optional[List[str]] = None
  build_status: Optional[str] = None
  test_status: Optional[str] = None


class ApplyAgent(LlmAgent):
  """Agent specialized for the OpenSpec Apply phase."""

  def __init__(self, **kwargs):
    # Load instruction from external file
    instruction_file = Path(__file__).parent / "apply_agent_instruction.md"
    try:
      instruction = instruction_file.read_text()
    except FileNotFoundError:
      raise RuntimeError(
        f"Apply agent instruction file not found: {instruction_file}"
      )
  
    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())

    # Add Simics MCP toolset where available
    try:
      tools.append(create_simics_mcp_toolset())
      print("✓ Simics MCP tools integrated for apply phase")
    except Exception as e:
      print(f"ℹ Simics MCP toolset not available for apply: {e}")

    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "apply_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description="Agent specialized for executing OpenSpec Apply changes for Simics devices",
      output_schema=ApplyResult,
      **kwargs,
    )


# Create the apply agent instance for ADK discovery
apply_agent = ApplyAgent(name="apply_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = apply_agent
