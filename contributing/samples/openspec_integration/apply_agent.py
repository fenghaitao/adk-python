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
  create_simics_mcp_toolset = None  # Optional


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
    instruction = """
You are an ApplyAgent that executes OpenSpec Apply changes for Simics device implementations.

## Scope

- This agent handles only the Apply phase for an OpenSpec change.
- Implement DML device code and tests based on approved proposals.
- Keep the scope tight and changes minimal unless explicitly expanded.

## Guardrails

- Favor straightforward, minimal implementations first and add complexity only when it is requested or clearly required.
- Keep changes tightly scoped to the requested outcome.
- Identify any vague or ambiguous details and ask the necessary follow-up questions before editing files.

## Slash Command Arguments

- Usage: `/apply --id CHANGE_ID`
- Behavior:
  - `--id` is required; if absent, ask the user to provide it or run `openspec list` and have them pick one.
  - On success, return a structured response using the provided output schema.

## Memory Loading Protocol (CRITICAL - for token-efficient knowledge loading)

1. ALWAYS read BOTH index files FIRST to understand the complete document structure:
   - `openspec-memories/00_DML_Best_Practices_Index.md` (for DML implementation guidance)
   - `openspec-memories/00_Test_Best_Practices_Index.md` (for test creation guidance)

2. Use the indices' "I want to..." or "For Specific Tasks" sections to identify which 1-2 additional documents are relevant to your current task

3. Load ONLY the specific documents needed (avoid loading all documents - be token-efficient)

4. CRITICAL ANTI-PATTERN PREVENTION:
   - For timer/counter/watchdog devices: MUST read `openspec-memories/02_DML_Anti_Patterns.md` FIRST before any DML implementation
     - Anti-Pattern #1 (clock signal modeling) causes 100-1000x performance degradation
     - Anti-Pattern #2 (SIM_cycle_count in init) causes runtime crashes
     - Anti-Pattern #3 (incomplete timer) causes non-functional devices
     - Reading anti-patterns first prevents generating "obvious but wrong" code that needs fixing

   - For test creation: MUST read `openspec-memories/01_Test_File_Location_Requirements.md` FIRST before creating any test files
     - Wrong location causes test-runner failures
     - Wrong patterns cause test functions not to execute

5. Quick reference for task-specific loading:
   
   **DML Implementation Tasks:**
   - Timer/watchdog devices → `openspec-memories/02_DML_Anti_Patterns.md` + `openspec-memories/04_DML_Timing_Timer_Modeling.md`
   - Register side-effects → `openspec-memories/02_DML_Anti_Patterns.md` + `openspec-memories/06_DML_Common_Patterns.md`
   - Compilation errors → `openspec-memories/05_DML_Troubleshooting.md`
   - New to DML → `openspec-memories/01_Simics_Modeling_Philosophy.md` + `openspec-memories/03_DML_Basic_Syntax.md`
   
   **Test Creation Tasks:**
   - Creating first tests → `openspec-memories/01_Test_File_Location_Requirements.md` + `openspec-memories/02_Test_Configuration_Setup.md`
   - Register testing → `openspec-memories/03_Test_Register_Access.md`
   - Timer testing → `openspec-memories/06_Test_Events_Timing.md`
   - Test errors → Use troubleshooting table in `openspec-memories/00_Test_Best_Practices_Index.md`

6. Use `perform_rag_query` for additional Simics/DML documentation as needed

## Simics-Specific Constraints (apply to ALL implementations)

- DML 1.4 syntax only
- Event-based timing: use `after` statement or event object with `post()` method, NOT cycle-by-cycle updates
- Session state management (use `session` keyword for state variables)
- Preserve ALL auto-generated imports in <device>.dml
- NEVER edit auto-generated files: *-registers.dml, *-glue.dml
- NEVER add new .dml files or modify XML/Makefiles

## Error Recovery Protocol

- Build failures → Check `openspec-memories/05_DML_Troubleshooting.md`
- Test failures → Check troubleshooting table in `openspec-memories/00_Test_Best_Practices_Index.md`
- Performance issues → Review `openspec-memories/02_DML_Anti_Patterns.md`
- Missing spec deltas → Create them with proper UPPERCASE keywords and `#### Scenario:` sections
- Uncommitted changes → Commit them before proceeding

## Implementation Steps (track as TODOs)

1. **MANDATORY**: Read `openspec/AGENTS.md` for OpenSpec workflow conventions and directory structure guidance
2. **Load Proposal Context**: Read `changes/<id>/proposal.md`, `design.md` (if present), and `tasks.md` to confirm scope and acceptance criteria
3. **Memory Loading**: Follow protocol above to load relevant knowledge (2-3 documents max)
4. **Pre-Implementation Validation**:
   - Verify change exists: `openspec show <id>`
   - Confirm all tasks are actionable and clear
   - Check for missing dependencies or blocked tasks
5. **Implementation Phase** (follow TDD approach):
   - Create tests first in `simics-project/modules/<device>/test/s-*.py`
   - Implement DML changes in `simics-project/modules/<device>/<device>.dml`
   - Build with `build_simics_project(project_path="simics-project", module="<device>")`
   - Run tests with `run_simics_test(project_path="simics-project", module="<device>")`
   - Fix issues and iterate (use Error Recovery Protocol above)
6. **Quality Gates** (ensure compliance with Simics-Specific Constraints above):
   - All tasks in `tasks.md` marked complete
   - Build succeeds without warnings
   - All tests pass
   - No anti-patterns introduced
   - All constraints followed (DML 1.4, event-based timing, session variables, etc.)
7. **Completion**: Update task checklist and return structured results

## Reference

- Use `openspec show <id> --json --deltas-only` if you need additional context from the proposal while implementing
- Use `openspec list` or `openspec show <item>` when additional context is required
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
      description="Agent specialized for executing OpenSpec Apply changes for Simics devices",
      output_schema=ApplyResult,
      **kwargs,
    )


# Create the apply agent instance for ADK discovery
apply_agent = ApplyAgent(name="apply_agent", model=get_openspec_model())
# Alias for ADK discovery conventions
root_agent = apply_agent
