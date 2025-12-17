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

"""OpenSpec Agent (system-level instructions copied from OpenSpec/AGENTS.md).

This agent uses a system instruction that mirrors the content of
OpenSpec/AGENTS.md to avoid runtime file dependencies. Per-run, user-level
instructions (e.g., for /apply) can still be injected by the runner scripts.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

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


def get_openspec_model() -> str:
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class OpenSpecAgent(LlmAgent):
  """OpenSpec agent using system-level instructions from OpenSpec/AGENTS.md."""

  def __init__(self, **kwargs):
    # System instruction copied from OpenSpec/AGENTS.md
    instruction = """<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->
"""

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())

    # Optionally add Simics MCP tools when available
    try:
      from .simics_mcp_tools import create_simics_mcp_toolset
      tools.append(create_simics_mcp_toolset())
      print("✓ Simics MCP tools integrated successfully")
    except ImportError as e:
      print(f"ℹ Simics MCP tools not available (import): {e}")
    except Exception as e:
      print(f"⚠ Simics MCP tools initialization failed: {e}")

    kwargs["tools"] = tools

    # Agent params
    agent_name = kwargs.pop("name", "openspec_simics_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description=(
        "OpenSpec agent that uses system-level instructions copied from "
        "OpenSpec/AGENTS.md"
      ),
      **kwargs,
    )


# Create the root agent instance for ADK to discover
root_agent = OpenSpecAgent(name="openspec_simics_agent", model=get_openspec_model())
