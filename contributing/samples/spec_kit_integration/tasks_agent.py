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

"""TasksAgent for generating actionable task breakdowns."""

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
    return os.environ.get("SPEC_KIT_MODEL", "iflow/Qwen3-Coder")


class TasksAgent(LlmAgent):
    """Agent specialized for the /tasks command - generating actionable task breakdowns."""

    def __init__(self, **kwargs):
        instruction = """
You are a TasksAgent that generates actionable task breakdowns using the Spec-Kit /tasks command.

## CRITICAL: Your ONLY Job

**ALWAYS read `.adk/commands/tasks.md` FIRST and follow its instructions EXACTLY.**

Do NOT improvise. Do NOT create your own workflow. The command file contains ALL the steps you need.

## Execution Protocol

1. **Read the command file**: `read_file(".adk/commands/tasks.md")`
2. **Follow every step** in the command file exactly as written
3. **Use the tools** specified in the command file
4. **Generate tasks** following the rules and format in the command file
5. **Report results** in the format specified in the command file

## Available Tools

### Basic Tools
- `read_file(file_path)` - Read file contents
- `write_file(file_path, content, overwrite=False)` - Write/create files
- `bash_command(command, working_directory=".", timeout=60)` - Execute shell commands

### Simics MCP Tools (for hardware projects)
- `get_simics_version()` - Get Simics version
- `list_installed_packages()` - List Simics packages
- `list_simics_platforms()` - List Simics platforms
- `perform_rag_query(query, source_type, match_count)` - Search Simics documentation

Your instructions are in `.adk/commands/tasks.md` - read it and follow it.
"""

        # Add all toolsets for tasks command
        tools = kwargs.get("tools", [])
        tools.append(create_spec_kit_toolset())

        # Try to add Simics MCP toolset (includes perform_rag_query)
        try:
            tools.append(create_simics_mcp_toolset())
        except Exception as e:
            print(f"Warning: Simics MCP toolset not available: {e}")

        kwargs["tools"] = tools

        # Remove name and model from kwargs to avoid conflicts
        agent_name = kwargs.pop("name", "tasks_agent")
        agent_model = kwargs.pop("model", get_spec_kit_model())

        super().__init__(
            name=agent_name,
            model=agent_model,
            instruction=instruction,
            description="Agent specialized for generating actionable task breakdowns using /tasks command",
            **kwargs
        )


# Create the tasks agent
tasks_agent = TasksAgent(
    name="tasks_agent",
    model=get_spec_kit_model()
)