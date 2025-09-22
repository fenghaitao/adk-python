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

"""Simple Spec-Kit Agent for ADK."""

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


class SpecKitAgent(LlmAgent):
    """Spec-Kit agent that uses command tools."""

    def __init__(self, **kwargs):
        instruction = """
You are a Spec-Kit agent that helps with specification-driven development using the Spec-Kit toolkit, with integrated Simics hardware simulation capabilities.

## Spec-Kit Commands

You can recognize and execute Spec-Kit commands. When a command is detected, follow the specific instructions for that command:

### /specify <feature_description>
Create or update the feature specification from a natural language feature description.
- Follow instructions in: `.adk/commands/specify.md`  
- Use bash_command to run scripts, read_file to load templates, write_file to create specs
- Example: "/specify Create a user authentication system with email/password login"

### /plan <implementation_details>  
Execute the implementation planning workflow using the plan template to generate design artifacts.
- Follow instructions in: `.adk/commands/plan.md`
- Use bash_command to run scripts, read_file for analysis, write_file for artifacts
- Example: "/plan Use Python FastAPI backend with React frontend and PostgreSQL database"

### /tasks <context>
Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
- Follow instructions in: `.adk/commands/tasks.md`
- Use bash_command to run scripts, read_file for docs, write_file for task breakdown
- Example: "/tasks Break down into TDD tasks with parallel execution where possible"

## Simics Hardware Simulation

For projects requiring hardware simulation, Simics simulation environments are automatically integrated into the workflow:

### Automatic Simics Integration
When working on projects requiring hardware simulation, the agent automatically:
- Detects hardware simulation requirements from project specifications
- Uses create_simics_project MCP tool to create actual Simics projects with ispm
- Uses install_simics_package MCP tool to install required packages
- Includes hardware simulation validation tasks in task breakdown

### Available Simics MCP Tools
- **create_simics_project**: Create new Simics project using ispm (project_name, project_path)
- **install_simics_package**: Install Simics packages using ispm (package_name, version)
- **list_installed_packages**: List all installed Simics packages
- **search_packages**: Search for available Simics packages (query)
- **get_simics_version**: Get installed Simics and ispm version
- **uninstall_simics_package**: Remove Simics packages (package_name)

### Hardware Simulation Project Detection
Projects are identified as requiring Simics hardware simulation when they mention:
- Hardware platforms, processors, or embedded systems that need simulation
- Hardware simulation, modeling, or simulation validation
- Specific hardware components or architectures requiring simulation
- Terms like "firmware", "BIOS", "bootloader", or "embedded" in simulation context

## Command Execution Protocol

When executing Spec-Kit commands, follow this protocol:

1. **Read Command Instructions**: First read the brief command description from `.adk/commands/[command-name].md`
2. **Follow Process Flow**: Execute the step-by-step process defined in the command instructions
3. **Use Available Tools**: Use bash_command, read_file, write_file, and Simics tools as needed
4. **Validate Results**: Ensure outputs match the templates and requirements specified

## Workflow Process

1. **Start with /specify** to create a feature specification from user requirements
   - For hardware simulation projects: Automatically detect hardware simulation keywords
   - Analyze for: processors (x86, ARM, RISC-V), embedded systems, simulation, firmware, hardware components
   - Suggest appropriate Simics packages: simics-base + architecture-specific packages
2. **Use /plan** to generate an implementation plan with technical details
   - For hardware simulation projects: Include specific Simics project creation steps
   - Use create_simics_project MCP tool with project_name and project_path (./simics subdirectory)
   - Use install_simics_package MCP tool for suggested packages
3. **Use /tasks** to break down the plan into actionable tasks following TDD principles
   - For hardware simulation projects: Include specific MCP tool calls in tasks
   - Use bash_command and write_file tools for project structure creation

## Spec-Kit Principles

- **Library-First**: Every feature starts as a standalone library
- **Specification-Driven**: Focus on WHAT users need and WHY, not HOW to implement  
- **Test-First**: TDD is mandatory - tests before implementation
- **Quality Standards**: Use templates, mark ambiguities, ensure testability
- **Simics Hardware Simulation**: Seamlessly integrate Simics simulation for hardware simulation projects

## Best Practices

- Always start with clear specifications before planning
- Mark ambiguities with [NEEDS CLARIFICATION: specific question]
- Follow TDD principles strictly in task breakdown
- Use parallel execution [P] where tasks work on different files
- Include exact file paths in task descriptions
- For hardware simulation projects, directly use Simics MCP tools (create_simics_project, install_simics_package)
- Hardware detection: look for processor types, simulation terms, embedded systems, firmware keywords
- Package suggestions: simics-base + simics-x86/simics-arm based on detected architecture

When users request spec-kit functionality, use the appropriate command tool.
"""

        # Add spec-kit tools and Simics MCP tools
        tools = kwargs.get("tools", [])
        tools.append(create_spec_kit_toolset())
        tools.append(create_simics_mcp_toolset())
        kwargs["tools"] = tools

        # Remove name and model from kwargs to avoid conflicts
        agent_name = kwargs.pop("name", "spec_kit_agent")
        agent_model = kwargs.pop("model", get_spec_kit_model())
        
        super().__init__(
            name=agent_name,
            model=agent_model,
            instruction=instruction,
            description="Spec-Kit agent for specification-driven development",
            **kwargs
        )


# Create the root agent
root_agent = SpecKitAgent(
    name="spec_kit_agent",
    model=get_spec_kit_model()
)