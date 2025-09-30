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
    from .plan_agent_improved import IMPROVED_PLAN_INSTRUCTION
except ImportError:
    from spec_kit_tools import create_spec_kit_toolset, create_simics_mcp_toolset
    from plan_agent_improved import IMPROVED_PLAN_INSTRUCTION


def get_spec_kit_model():
    """Get Spec-Kit model from environment or use default."""
    return os.environ.get("SPEC_KIT_MODEL", "iflow/Qwen3-Coder")


class PlanAgent(LlmAgent):
    """Agent specialized for the /plan command - creating implementation plans."""

    def __init__(self, **kwargs):
        # Use improved instructions with better structure and clarity
        instruction = IMPROVED_PLAN_INSTRUCTION

        # Add both toolsets for plan command
        tools = kwargs.get("tools", [])
        tools.append(create_spec_kit_toolset())
        tools.append(create_simics_mcp_toolset())
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