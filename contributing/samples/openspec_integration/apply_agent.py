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

# Simics MCP tools are used heavily during Apply
try:
  from .simics_mcp_tools import create_simics_mcp_toolset
except Exception:
  create_simics_mcp_toolset = None  # Optional


def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class ApplyArgs(BaseModel):
  """Arguments for /apply slash command."""
  change_id: str


class ApplyAgent(LlmAgent):
  """Agent specialized for the OpenSpec Apply phase."""

  def __init__(self, **kwargs):
    instruction = """
You are an ApplyAgent that executes OpenSpec Apply changes.

Scope
- This agent handles only the Apply phase for an OpenSpec change.
- Keep the scope tight and changes minimal unless explicitly expanded.

Guardrails
- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Refer to `openspec/AGENTS.md` (located inside the `openspec/` directory—run `ls openspec` or `openspec update` if you don't see it) if you need additional OpenSpec conventions or clarifications.

Steps
Track these steps as TODOs and complete them one by one.
1. Read `changes/<id>/proposal.md`, `design.md` (if present), and `tasks.md` to confirm scope and acceptance criteria.
2. Work through tasks sequentially, keeping edits minimal and focused on the requested change.
3. Confirm completion before updating statuses—make sure every item in `tasks.md` is finished.
4. Update the checklist after all work is done so each task is marked `- [x]` and reflects reality.
5. Reference `openspec list` or `openspec show <item>` when additional context is required.

Slash Command Arguments
- Usage: `/apply --id CHANGE_ID`
- Behavior:
  - `--id` is required; if absent, ask the user to provide it or run `openspec list` and have them pick one.

Reference
- Use `openspec show <id> --json --deltas-only` if you need additional context from the proposal while implementing.

Simics Integration (best practices)

MEMORY LOADING PROTOCOL (for token-efficient knowledge loading):
1. ALWAYS read `openspec-memories/00_DML_Best_Practices_Index.md` FIRST to understand document structure
2. Use the index's "I want to..." section to identify which 1-2 documents are relevant to your task
3. Load ONLY the specific documents needed (avoid loading all documents - be token-efficient)
4. For timer/counter/watchdog devices: MUST read `openspec-memories/02_DML_Anti_Patterns.md` FIRST before any implementation
   - Anti-Pattern #1 (clock signal modeling) causes 100-1000x performance degradation
   - Anti-Pattern #2 (SIM_cycle_count in init) causes runtime crashes
   - Anti-Pattern #3 (incomplete timer) causes non-functional devices
   - Reading anti-patterns first prevents generating "obvious but wrong" code that needs fixing
5. For test development, load relevant test guidance from index:
   - Test file location requirements (CRITICAL - read first)
   - Test configuration setup
   - Testing registers and fields
   - Testing device output signals with fake objects
   - Testing DMA and memory operations
   - Testing timers and timing behavior
6. Use `perform_rag_query` for additional Simics/DML/Python docs as needed
- Follow TDD-first implementation order:
  - Create tests first in `simics-project/modules/<device>/test/s-*.py`
  - Implement DML updates in `simics-project/modules/<device>/<device>.dml`
  - Build with `build_simics_project(project_path="simics-project", module="<device>")`
  - Run tests with `run_simics_test(project_path="simics-project", suite="modules/<device>/test")`
- Critical rules: preserve imports, DML 1.4 syntax, event-based timing, session variables; avoid editing auto-generated files (`<device>-registers.dml`, `<device>-glue.dml`), adding new .dml files, or modifying XML/Makefiles.
- Quality gates: meaningful tests and assertions; substantive DML implementation; timers/counters use lazy evaluation and events.
- Error recovery: create missing spec deltas, fix invalid formats by adding `#### Scenario:`, commit uncommitted changes if needed, fix build/test issues and document any remaining problems.
"""

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())

    # Add Simics MCP toolset where available
    if create_simics_mcp_toolset:
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
      description="Agent specialized for executing OpenSpec Apply changes",
      **kwargs,
    )


# Create the apply agent instance for ADK discovery
apply_agent = ApplyAgent(name="apply_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = apply_agent
