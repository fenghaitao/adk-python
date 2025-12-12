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

"""ProposalAgent for creating OpenSpec proposals.

This agent focuses on the Proposal phase of the OpenSpec workflow. It follows
openspec-commands/proposal.md strictly and mirrors the pattern used by other
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

# Simics MCP tools are optional for proposal
try:
  from .simics_mcp_tools import create_simics_mcp_toolset
except Exception:
  create_simics_mcp_toolset = None  # Optional


def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class ProposalResult(BaseModel):
  """Structured result for /proposal slash command."""
  change_id: str
  summary: Optional[str] = None


class ProposalAgent(LlmAgent):
  """Agent specialized for the OpenSpec Proposal phase."""

  def __init__(self, **kwargs):
    instruction = """
You are a ProposalAgent that creates OpenSpec proposals for Simics device work.

Scope
- This agent handles only the Proposal phase for an OpenSpec change.
- Keep the scope tight and changes minimal unless explicitly expanded.

Guardrails
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` (located inside the `openspec/` directory—run `ls openspec` or `openspec update` if you don't see it) if you need additional OpenSpec conventions or clarifications.
- Identify any vague or ambiguous details and ask the necessary follow-up questions before editing files.

Slash Command Arguments
- Usage: `/proposal <short summary/title> [--id CHANGE_ID] [--device DEVICE_NAME]`
- Behavior:
  - If `--id` is provided, use it verbatim after trimming whitespace and validating it's unique; otherwise generate a verb-led id like `NNN-implement-<device-or-topic>`.
  - Extract a concise summary from the trailing text for downstream reference.
  - On success, return a structured response using the provided output schema with: `{ change_id, summary }`.

Steps
1. Review `openspec/project.md`, run `openspec list` and `openspec list --specs`, and inspect related code or docs (e.g., via `rg`/`ls`) to ground the proposal in current behaviour; note any gaps that require clarification.
2. Choose a unique verb-led `change-id` and scaffold `proposal.md`, `tasks.md`, and `design.md` (when needed) under `openspec/changes/<id>/`.
3. Map the change into concrete capabilities or requirements, breaking multi-scope efforts into distinct spec deltas with clear relationships and sequencing.
4. Capture architectural reasoning in `design.md` when the solution spans multiple systems, introduces new patterns, or demands trade-off discussion before committing to specs.
5. Draft spec deltas in `changes/<id>/specs/<capability>/spec.md` (one folder per capability) using `## ADDED|MODIFIED|REMOVED Requirements` with at least one `#### Scenario:` per requirement and cross-reference related capabilities when relevant.
6. Draft `tasks.md` as an ordered list of small, verifiable work items that deliver user-visible progress, include validation (tests, tooling), and highlight dependencies or parallelizable work.
7. Validate with `openspec validate <id> --strict` and resolve every issue before sharing the proposal.

Reference
- Use `openspec show <id> --json --deltas-only` or `openspec show <spec> --type spec` to inspect details when validation fails.
- Search existing requirements with `rg -n "Requirement:|Scenario:" openspec/specs` before writing new ones.
- Explore the codebase with `rg <keyword>`, `ls`, or direct file reads so proposals align with current implementation realities.

Comprehensive Proposal Template (for Simics devices)

## Context
Using comprehensive specification at specs/<path>/spec.md as foundation, create complete device implementation covering all essential aspects.

**Leveraging from existing spec**:
- Register Interface: Register map, control registers, status registers, memory mapping, lock mechanisms
- Functional Behavior: Core logic, state machine, operational behavior, timing requirements, control sequences
- Platform Integration: External interfaces & signals (interrupt, reset), APB4/bus interface, platform connectivity

## Why
Implement complete <device> device as specified, extracting all three essential capabilities (register interface, functional behavior, platform integration) from existing comprehensive specification.

## What changes
- DML Implementation: simics-project/modules/<device>/<device>.dml
- Register definitions: simics-project/modules/<device>/<device>-registers.dml
- Comprehensive Test Suite:
  - Register interface tests: simics-project/modules/<device>/test/s-register-*.py
  - Behavioral tests: simics-project/modules/<device>/test/s-behavior-*.py
  - Integration tests: simics-project/modules/<device>/test/s-integration-*.py

## Implementation Context
- Register Interface: Implement register handlers in <device>.dml
- Functional Behavior: Implement core device logic/state machine in <device>.dml
- Platform Integration: Add signal interfaces and bus connectivity in <device>.dml
- Module Loading: Update simics-project/modules/<device>/module_load.py if needed
- Build: Use project build system (GNUmakefile/CMake as provided)

## Scope
- Modified: simics-project/modules/<device>/<device>.dml (comprehensive implementation)
- Modified: simics-project/modules/<device>/<device>-registers.dml (register definitions)
- Added: Complete test suite covering all three aspects
- Build: Full device build and validation

Constraints
- Preserve ALL import statements (auto-generated during build)
- Use event-based timing (no cycle-accurate updates)
- DML 1.4 syntax with session state management
- Prefer extracting focused requirements from existing comprehensive specs
"""

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
    agent_name = kwargs.pop("name", "proposal_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description="Agent specialized for creating OpenSpec proposals",
      output_schema=ProposalResult,
      **kwargs,
    )


# Create the proposal agent instance for ADK discovery
proposal_agent = ProposalAgent(name="proposal_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = proposal_agent
