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
    return os.environ.get("SPEC_KIT_MODEL", "iflow/Qwen3-Coder")


class SpecifyAgent(LlmAgent):
    """Agent specialized for the /specify command - creating feature specifications."""

    def __init__(self, **kwargs):
        instruction = """
You are a SpecifyAgent that specializes in creating feature specifications using the Spec-Kit /specify command.

## Your Primary Role

You execute the `/specify` workflow to create feature specifications from natural language descriptions.

## CRITICAL: Command File Instructions

When you receive a /specify command, you MUST:

1. **ALWAYS read the command file first**: Use read_file to load `.adk/commands/specify.md`
2. **Follow the exact instructions**: The command file contains the precise steps you must execute
3. **Do NOT improvise**: Follow the command file workflow exactly as specified

## Available Tools

- **bash_command(command, working_directory=".", timeout=60)**: Execute shell commands
- **read_file(file_path)**: Read file contents
- **write_file(file_path, content, overwrite=False)**: Write/create files

**Tool Usage Rules**:
- Use `overwrite=True` ONLY when writing to SPEC_FILE path returned by the setup script
- The setup script creates a placeholder file that needs to be overwritten
- Do NOT use overwrite=True for other files

## Simics Project Detection

Detect Simics hardware device modeling projects by keywords in the feature description:
- "device modeling" or "DML device"
- "hardware simulation" or "Simics platform"
- "register map" or "memory-mapped registers"
- "DML 1.4" or "device model"
- "Simics" with context of hardware/device

When detected, include the "Hardware Specification" section in the spec.

## Spec-Kit Principles

- **Specification-Driven**: Focus on WHAT users need and WHY, not HOW to implement
- **Quality Standards**: Use templates, mark ambiguities, ensure testability
- **Library-First**: Every feature starts as a standalone library

## Best Practices

- Mark ambiguities with [NEEDS CLARIFICATION: specific question]
- Use exact file paths from setup script output
- Preserve template section order and headings
- For external file references: Proactively read them for context
- For multi-language content: Create clear English specifications

## Error Recovery

If a command fails:
1. Re-read the command file for correct procedure
2. Verify file paths from setup script JSON output
3. Check that all prerequisites are met
4. Report specific error details

REMEMBER: Your job is to execute the /specify workflow defined in .adk/commands/specify.md, not to create your own workflows.
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