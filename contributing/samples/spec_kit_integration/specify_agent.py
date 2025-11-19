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

"""SpecifyAgent for creating feature specifications."""

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
    from .spec_kit_tools import create_spec_kit_toolset
except ImportError:
    from spec_kit_tools import create_spec_kit_toolset



def get_spec_kit_model():
    """Get Spec-Kit model from environment or use default."""
    return os.environ.get("SPEC_KIT_MODEL", "iflow/qwen3-coder-plus")


class SpecifyAgent(LlmAgent):
    """Agent specialized for the /specify command - creating feature specifications."""

    def __init__(self, **kwargs):
        instruction = """
You are a SpecifyAgent that creates feature specifications using the Spec-Kit /specify command.

## CRITICAL: Your ONLY Job

**ALWAYS read `.adk/commands/specify.md` FIRST and follow its instructions EXACTLY.**

Do NOT improvise. Do NOT create your own workflow. The command file contains ALL the steps you need.

## Execution Protocol

1. **Read the command file**: `read_file(".adk/commands/specify.md")`
2. **Follow every step** in the command file exactly as written
3. **Use the tools** specified in the command file
4. **Report results** in the format specified in the command file

Your instructions are in `.adk/commands/specify.md` - read it and follow it.
"""

        # Add only basic tools - no MCP tools for specify
        tools = kwargs.get("tools", [])
        tools.append(create_spec_kit_toolset())
        kwargs["tools"] = tools

        # Remove name and model from kwargs to avoid conflicts
        agent_name = kwargs.pop("name", "specify_agent")
        agent_model = kwargs.pop("model", get_spec_kit_model())

        super().__init__(
            name=agent_name,
            model=agent_model,
            instruction=instruction,
            description="Agent specialized for creating feature specifications using /specify command",
            **kwargs
        )


# Create the specify agent
specify_agent = SpecifyAgent(
    name="specify_agent",
    model=get_spec_kit_model()
)