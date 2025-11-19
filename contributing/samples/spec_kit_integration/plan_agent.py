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

"""PlanAgent for creating implementation plans."""

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
    from .spec_kit_tools import create_spec_kit_toolset, create_simics_mcp_toolset
except ImportError:
    from spec_kit_tools import create_spec_kit_toolset, create_simics_mcp_toolset


def get_spec_kit_model():
    """Get Spec-Kit model from environment or use default."""
    return os.environ.get("SPEC_KIT_MODEL", "iflow/qwen3-coder-plus")


class PlanAgent(LlmAgent):
    """Agent specialized for the /plan command - creating implementation plans."""

    def __init__(self, **kwargs):
        instruction = """
You are a PlanAgent that creates implementation plans using the Spec-Kit /plan command.

## CRITICAL: Your ONLY Job

**ALWAYS read `.adk/commands/plan.md` FIRST and follow its instructions EXACTLY.**

Do NOT improvise. Do NOT create your own workflow. The command file contains ALL the steps you need.

## Execution Protocol

1. **Read the command file**: `read_file(".adk/commands/plan.md")`
2. **Read the plan template**: `read_file(".specify/templates/plan-template.md")`
3. **Follow every step** in the template exactly as written - ALL phases, ALL steps
4. **Use the tools** specified in the template
5. **Validate completion** using the checklists in the template
6. **Report results** in the exact format specified in the template

Your instructions are in `.adk/commands/plan.md` - read it and follow it.
"""

        # Add all toolsets for plan command
        tools = kwargs.get("tools", [])
        tools.append(create_spec_kit_toolset())

        # Try to add Simics MCP toolset (includes perform_rag_query)
        try:
            tools.append(create_simics_mcp_toolset())
        except Exception as e:
            print(f"Warning: Simics MCP toolset not available: {e}")

        kwargs["tools"] = tools

        # Remove name and model from kwargs to avoid conflicts
        agent_name = kwargs.pop("name", "plan_agent")
        agent_model = kwargs.pop("model", get_spec_kit_model())

        super().__init__(
            name=agent_name,
            model=agent_model,
            instruction=instruction,
            description="Agent specialized for creating implementation plans using /plan command",
            **kwargs
        )


# Create the plan agent
plan_agent = PlanAgent(
    name="plan_agent",
    model=get_spec_kit_model()
)