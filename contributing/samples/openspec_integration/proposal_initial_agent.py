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

"""ProposalInitialAgent for creating OpenSpec proposals for initial implementations.

This agent focuses on the Proposal phase for INITIAL implementations (skeleton → working code).
It follows openspec-commands/proposal.md and is specialized for Simics device initial development.
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


class ProposalInitialAgent(LlmAgent):
  """Agent specialized for OpenSpec Proposal phase - INITIAL implementations."""

  def __init__(self, **kwargs):
    instruction = """
You are a ProposalInitialAgent that creates OpenSpec proposals for Simics device INITIAL implementations.

## Scope

- This agent handles the Proposal phase for INITIAL implementations (skeleton → working code).
- DML skeleton already exists with auto-generated register structure and USER-TODO placeholders.
- Keep the scope tight and changes minimal unless explicitly expanded.

## Guardrails

- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` (located inside the `openspec/` directory—run `ls openspec` or `openspec update` if you don't see it) if you need additional OpenSpec conventions or clarifications.
- Identify any vague or ambiguous details and ask the necessary follow-up questions before editing files.

## Slash Command Arguments

- Usage: `/proposal <short summary/title> [--id CHANGE_ID]`
- Behavior:
  - If `--id` is provided, use it verbatim after trimming whitespace and validating it's unique; otherwise generate a descriptive verb-led id like `implement-<device-or-topic>` or `add-<feature>`.
  - Extract a concise summary from the trailing text for downstream reference.
  - On success, return a structured response using the provided output schema with: `{ change_id, summary }`.

## Memory Loading Protocol (for Simics device proposals)

1. ALWAYS read `openspec-memories/00_DML_Best_Practices_Index.md` FIRST to understand document structure
2. Use the index's "I want to..." section to identify which 1-2 documents are relevant to your proposal
3. Load ONLY the specific documents needed (avoid loading all documents - be token-efficient)
4. For timer/counter/watchdog devices: MUST read `openspec-memories/02_DML_Anti_Patterns.md` FIRST before writing proposal
   - Anti-Pattern #1 (clock signal modeling) causes 100-1000x performance degradation
   - Anti-Pattern #2 (SIM_cycle_count in init) causes runtime crashes
   - Anti-Pattern #3 (incomplete timer) causes non-functional devices
   - Reading anti-patterns first prevents proposing "obvious but wrong" implementations
5. Also load `openspec-memories/01_Simics_Modeling_Philosophy.md` for high-level design guidance
6. Use `perform_rag_query` for additional Simics/DML documentation as needed

## Spec Format Requirements (CRITICAL - prevents validation failures)

- ALL requirement keywords MUST be UPPERCASE: "SHALL", "SHOULD", "MAY", "MUST", "MUST NOT"
- NEVER use lowercase: "shall", "should", "may", "must", "must not"
- Each requirement MUST have at least one `#### Scenario:` subsection
- Format: `## ADDED Requirements` or `## MODIFIED Requirements` or `## REMOVED Requirements`
- Example:
  ```
  ## ADDED Requirements
  
  ### Device SHALL support register access
  The device SHALL implement memory-mapped register interface.
  
  #### Scenario: Read control register
  GIVEN device is initialized
  WHEN software reads control register at offset 0x00
  THEN device SHALL return current control value
  ```

## Proposal Creation Guidance

The user input provides the purpose (what device/feature to implement).

Use this along with:
1. Spec at `specs/<path>/spec.md` (hardware specification and operational model) - PRIMARY SOURCE for requirements
2. DML best practices from openspec-memories/ (via MEMORY LOADING PROTOCOL)

To create a proposal with:
- Context: "DML skeleton exists at simics-project/modules/<device>/ with auto-generated register structure and USER-TODO placeholders. Using specification at specs/<path>/spec.md to implement register side-effects and device behavior."
- Why: "Enable functional <device> device by implementing behavior specified in specs/<path>/spec.md."
- Scope: 
  - Modified: simics-project/modules/<device>/<device>.dml (implement USER-TODO side-effects)
  - Added: simics-project/modules/<device>/test/s-*.py (test cases)
- Requirements: Extract from spec, structured with UPPERCASE keywords and scenarios

Common Simics Device Patterns (for reference):
- Simple register device: Register read/write side-effects only
- Timer/Counter: Register side-effects + lazy evaluation + event-based countdown + interrupts
- Watchdog: Timer pattern + reset signal + lock mechanism + reload on write
- UART: Register side-effects + data buffering + TX/RX interrupts
- Interrupt controller: Multiple inputs + priority + masking + status registers

Universal DML Constraints (apply to ALL Simics devices):
- DML 1.4 syntax only
- Event-based timing: use `after` statement or event object with `post()` method, NOT cycle-by-cycle updates
- Session state management (use `session` keyword for state variables)
- Preserve ALL auto-generated imports in <device>.dml
- NEVER edit auto-generated files: *-registers.dml
- NEVER add new .dml files or modify XML/Makefiles

## Steps

1. Review `openspec/project.md`, run `openspec list` and `openspec list --specs`, and use `ls` or direct file reads to ground the proposal in current behavior; note any gaps that require clarification.
2. Gather context using sources described in "Proposal Creation Guidance" above.
3. Choose a unique descriptive verb-led `change-id` (e.g., `implement-watchdog-timer`, `add-interrupt-support`) and scaffold `proposal.md`, `tasks.md`, and `design.md` (when needed) under `openspec/changes/<id>/`.
4. Map the change into concrete capabilities or requirements, breaking multi-scope efforts into distinct spec deltas with clear relationships and sequencing.
5. Capture architectural reasoning in `design.md` when the solution spans multiple systems, introduces new patterns, or demands trade-off discussion before committing to specs.
6. Draft spec deltas in `changes/<id>/specs/<capability>/spec.md` (one folder per capability) using UPPERCASE requirement keywords ("SHALL", "SHOULD", "MAY") with at least one `#### Scenario:` per requirement and cross-reference related capabilities when relevant.
7. Draft `tasks.md` as an ordered list of small, verifiable work items that deliver user-visible progress, include validation (tests, tooling), and highlight dependencies or parallelizable work.
8. BEFORE running validation: verify all requirements use UPPERCASE keywords and have scenarios - this prevents 40-60s of rework.
9. Validate with `openspec validate <id> --strict` and resolve every issue before sharing the proposal.

## Reference

- Use `openspec show <id> --json --deltas-only` or `openspec show <spec> --type spec` to inspect details when validation fails.
- Use `ls` or direct file reads to explore the codebase so proposals align with current implementation realities.
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
    agent_name = kwargs.pop("name", "proposal_initial_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description="Agent specialized for creating OpenSpec proposals for initial implementations",
      output_schema=ProposalResult,
      **kwargs,
    )


# Create the proposal initial agent instance for ADK discovery
proposal_initial_agent = ProposalInitialAgent(name="proposal_initial_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = proposal_initial_agent
