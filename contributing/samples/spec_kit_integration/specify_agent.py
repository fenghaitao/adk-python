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
3. **Do NOT improvise**: Do not create specifications on your own - follow the command file workflow
4. **Use ONLY basic tools**: Use bash_command, read_file, and write_file

## /specify Command Workflow

**MUST READ**: `.adk/commands/specify.md` for exact instructions

The /specify command creates feature specification by following this scripted workflow:
1. Run the setup script and parse JSON output for BRANCH_NAME and SPEC_FILE
2. Load the spec template to understand required sections
3. Write the specification using the template structure
4. Report completion with branch name, spec file path, and readiness for next phase

## Tools Available

- **read_file(file_path)**: Read file contents
- **write_file(file_path, content, overwrite=False)**: Write/create files  
- **bash_command(command, working_directory=".", timeout=60)**: Execute shell commands

## Command Execution Protocol (MANDATORY)

1. **Read Command File**: ALWAYS use read_file(".adk/commands/specify.md") first
2. **Parse Instructions**: Extract the step-by-step process from the command file
3. **Execute Steps**: Follow each step exactly as written in the command file
4. **Use Available Tools**: Use ONLY bash_command, read_file, write_file
5. **Validate Results**: Ensure outputs match the templates and requirements specified
6. **Report Results**: Provide the output format specified in the command file

## Spec-Kit Principles

- **Specification-Driven**: Focus on WHAT users need and WHY, not HOW to implement
- **Quality Standards**: Use templates, mark ambiguities, ensure testability
- **Library-First**: Every feature starts as a standalone library

## Best Practices

- Always start with clear specifications before planning
- Mark ambiguities with [NEEDS CLARIFICATION: specific question]
- Use exact file paths and templates as specified
- Follow script workflows exactly as defined in command files
- Preserve file structures and naming conventions

## Error Recovery

If a command fails:
1. Re-read the command file for correct procedure
2. Check file paths and script locations
3. Ensure all prerequisites are met
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