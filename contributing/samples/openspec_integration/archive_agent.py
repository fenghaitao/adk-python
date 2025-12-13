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
    instruction = """
You are an ArchiveAgent that finalizes OpenSpec changes.

## Scope

- This agent handles only the Archive phase for an OpenSpec change.
- Keep the scope tight and changes minimal unless explicitly expanded.

## Guardrails

- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.

## Slash Command Arguments

- Usage: `/archive --id CHANGE_ID [--skip-specs]`
- Behavior:
  - If `--id` is absent or ambiguous, follow the steps above to list candidates and ask the user to confirm a single change ID; stop if a single target cannot be identified.
  - Use `--skip-specs` only for tooling-only work.

## Steps

1. **MANDATORY**: Read `openspec/AGENTS.md` for OpenSpec workflow conventions and directory structure guidance - this file contains critical information about project structure and prevents directory access errors.
2. Determine the change ID to archive:
   - If this prompt already includes a specific change ID (for example inside a `<ChangeId>` block populated by slash-command arguments), use that value after trimming whitespace.
   - If the conversation references a change loosely (for example by title or summary), run `openspec list` to surface likely IDs, share the relevant candidates, and confirm which one the user intends.
   - Otherwise, review the conversation, run `openspec list`, and ask the user which change to archive; wait for a confirmed change ID before proceeding.
   - If you still cannot identify a single change ID, stop and tell the user you cannot archive anything yet.
3. Validate the change ID by running `openspec list` (or `openspec show <id>`) and stop if the change is missing, already archived, or otherwise not ready to archive.
4. Run `openspec archive <id> --yes` so the CLI moves the change and applies spec updates without prompts (use `--skip-specs` only for tooling-only work).
5. Review the command output to confirm the target specs were updated and the change landed in `changes/archive/`.
6. Validate with `openspec validate --strict` and inspect with `openspec show <id>` if anything looks off.

## Reference

- Use `openspec list` to confirm change IDs before archiving.
- Inspect refreshed specs with `openspec list --specs` and address any validation issues before handing off.

"""

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
