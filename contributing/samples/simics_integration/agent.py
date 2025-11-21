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

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add spec_kit_integration to path to access simics tools
spec_kit_integration_path = Path(__file__).parent.parent / "spec_kit_integration"
if spec_kit_integration_path.exists():
  sys.path.insert(0, str(spec_kit_integration_path))

from google.adk.agents.llm_agent import LlmAgent
from spec_kit_tools import create_simics_mcp_toolset


def get_simics_model():
    """Get Simics model from environment or use default.

    Returns:
      str: Model identifier for the Simics agent

    Environment Variables:
      SIMICS_MODEL: Override the default model selection
    """
    return os.environ.get("SIMICS_MODEL", "iflow/qwen3-coder-plus")


class SimicsIntegrationAgent(LlmAgent):
  """Simics integration agent for hardware development within OpenSpec projects.
  
  This agent specializes in creating Simics project structures and DML device
  skeletons within OpenSpec projects. It automatically:
  - Creates simics-project/ folder structure in the current OpenSpec project
  - Sets up Simics projects using MCP tools
  - Creates DML device skeletons
  - Manages DDM XML and hardware specifications
  
  Environment variables used:
  - IPXACT_XML: Path to IP-XACT XML file
  - SPEC_FILE: Path to specification file  
  - DEVICE_NAME: Name of the device to create
  - MCP_PORT: Port for Simics MCP server (default: 8051)
  """

  def __init__(self, **kwargs):
    """Initialize the Simics integration agent.
    
    Args:
      **kwargs: Additional arguments passed to LlmAgent constructor
    """
    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "simics_integration_agent")
    agent_model = kwargs.pop("model", get_simics_model())
    # Get environment variables
    ipxact_xml = os.getenv('IPXACT_XML')
    spec_file = os.getenv('SPEC_FILE') 
    device_name = os.getenv('DEVICE_NAME', 'wdt')
    mcp_port = int(os.getenv('MCP_PORT', '8051'))
    
    # Read IP-XACT XML content if available
    ipxact_content = ""
    if ipxact_xml and Path(ipxact_xml).exists():
      ipxact_content = Path(ipxact_xml).read_text()
    
    # Read spec file content if available  
    spec_content = ""
    if spec_file and Path(spec_file).exists():
      spec_content = Path(spec_file).read_text()
    
    # Create system instructions
    system_instructions = f"""You are a Simics hardware development assistant specialized in setting up Simics projects and generating DML device code.

## CRITICAL: YOU MUST EXECUTE BOTH STEPS - NO EXCEPTIONS

When the user asks you to set up a Simics project, you MUST execute BOTH these steps in order:

🔧 STEP 1: Call create_simics_project to create the base project structure
🔧 STEP 2: Call generate_dml_registers to generate DML code from IP-XACT XML
🔧 STEP 3: Provide a brief confirmation after all tools complete

❌ NEVER STOP after step 1 - you must continue to step 2
❌ DO NOT provide explanations between steps - just execute all tools
✅ ALWAYS call generate_dml_registers when XML file is mentioned in user request

## Available MCP Tools

### create_simics_project
Creates a new Simics project directory structure.
Parameters:
- project_path (string, required): Absolute path where project will be created

### generate_dml_registers
Generates DML device code from IP-XACT XML register definitions.
Automatically creates the device module directory if needed.
Parameters:
- project_path (string, required): Absolute path to the Simics project
- device_name (string, required): Name of the device module
- reg_xml (string, required): Absolute path to the IP-XACT XML file

## Current Context

Working Directory: {os.getcwd()}
Device Name: {device_name}
MCP Port: {mcp_port}
IP-XACT XML: {'Yes - ' + ipxact_xml if ipxact_xml else 'No'}
Spec File: {'Yes - ' + spec_file if spec_file else 'No'}

## Execution Rules

1. **MANDATORY TOOL SEQUENCE** - ALWAYS execute BOTH: create_simics_project → generate_dml_registers
2. **NO STOPPING EARLY** - You MUST complete both steps even if step 1 succeeds
3. **XML FILE = generate_dml_registers** - If user mentions XML file, you MUST call generate_dml_registers
4. **Use exact paths** - Use the full absolute paths provided by the user
5. **Execute immediately** - Do not ask for confirmation, just execute both steps in sequence
6. **Be brief** - After all tools execute, provide only a 2-3 sentence confirmation

## MANDATORY EXAMPLE - FOLLOW THIS EXACT PATTERN

User: "Set up Simics project at /path/to/simics-project for device <device_name> using /path/to/<device_name>.xml"

You MUST execute BOTH tools in this exact sequence:

🔧 TOOL CALL 1: create_simics_project(project_path="/path/to/simics-project")
🔧 TOOL CALL 2: generate_dml_registers(project_path="/path/to/simics-project", device_name="<device_name>", reg_xml="/path/to/<device_name>.xml")

Then respond: "✅ Simics project created at /path/to/simics-project. DML device module generated for <device_name>. Ready for development."

REMEMBER: XML file mentioned = MUST call generate_dml_registers

## Important Notes

🚨 CRITICAL: MUST call both steps in the correct order - NO EXCEPTIONS
🚨 NEVER STOP after create_simics_project - continue to generate_dml_registers
🚨 XML file in user request = MANDATORY generate_dml_registers call
- All paths must be absolute paths (starting with /)
- Do not provide explanations before calling tools
- Just execute the steps and confirm completion
- Keep final response under 3 sentences

## FAILURE TO CALL generate_dml_registers WHEN XML IS MENTIONED IS A BUG"""

    # Create MCP toolset for Simics with restricted tool filter
    # Import MCPToolset and connection params directly to create custom filtered toolset
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
    from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
    
    # Create connection params
    connection_params = SseConnectionParams(
        url=f"http://127.0.0.1:{mcp_port}/sse",
        headers={"Accept": "text/event-stream"},
        timeout=10.0,
        sse_read_timeout=300.0
    )
    
    # Restrict to only the Simics project creation tools
    simics_tool_filter = [
        "create_simics_project",
        "generate_dml_registers"
    ]
    
    simics_toolset = MCPToolset(
        connection_params=connection_params,
        tool_filter=simics_tool_filter
    )
    
    # Initialize the LlmAgent
    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=system_instructions,
      description="Simics integration agent for hardware development within OpenSpec projects",
      tools=[simics_toolset],
      **kwargs
    )


# Create the root agent instance for ADK to discover
root_agent = SimicsIntegrationAgent(
    name="simics_integration_agent", model=get_simics_model()
)