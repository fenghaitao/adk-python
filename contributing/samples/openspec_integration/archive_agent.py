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

"""ArchiveAgent for finalizing OpenSpec changes.

This agent focuses on the Archive phase of the OpenSpec workflow. It follows
openspec-commands/archive.md strictly and mirrors the pattern used by other
OpenSpec agents in this sample.
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


def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class ArchiveArgs(BaseModel):
  """Arguments for /archive slash command."""
  change_id: Optional[str] = None
  skip_specs: Optional[bool] = None


class ArchiveAgent(LlmAgent):
  """Agent specialized for the OpenSpec Archive phase."""

  def __init__(self, **kwargs):
    # Load instruction from external file
    instruction_file = Path(__file__).parent / "archive_agent_instruction.md"
    try:
      instruction = instruction_file.read_text()
    except FileNotFoundError:
      raise RuntimeError(
        f"Apply agent instruction file not found: {instruction_file}"
      )

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "archive_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description="Agent specialized for archiving OpenSpec changes",
      **kwargs,
    )


# Create the archive agent instance for ADK discovery
archive_agent = ArchiveAgent(name="archive_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = archive_agent
