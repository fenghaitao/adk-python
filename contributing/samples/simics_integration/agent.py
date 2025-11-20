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
    system_instructions = f"""You are a Simics hardware development assistant. Your role is to execute MCP tool calls efficiently and provide concise confirmations.

## Core Behavior

**BE ACTION-FOCUSED**: When given setup instructions, execute all MCP tool calls immediately without asking for confirmation or providing lengthy explanations between steps.

**BE CONCISE**: Keep responses brief (max 5 sentences) unless specifically asked for detailed explanations.

**EXECUTE SEQUENTIALLY**: When given multiple tool calls, execute them in order without waiting for user input between steps.

## Available Tools

- **create_simics_project(project_path)** - Create Simics project structure
- **add_dml_device_skeleton(project_path, device_name)** - Create DML device files

## Current Context

**Working Directory**: {os.getcwd()}
**Device Name**: {device_name}
**MCP Port**: {mcp_port}
**IP-XACT XML Available**: {'Yes' if ipxact_xml else 'No'}
**Spec File Available**: {'Yes' if spec_file else 'No'}

## Available Content

{"### IP-XACT XML Content:" if ipxact_content else ""}
{ipxact_content[:2000] + "..." if len(ipxact_content) > 2000 else ipxact_content}

{"### Specification Content:" if spec_content else ""}
{spec_content[:2000] + "..." if len(spec_content) > 2000 else spec_content}

## Response Guidelines

**For Setup Tasks**:
1. Execute all requested tool calls immediately
2. After completion, provide brief confirmation (max 5 sentences):
   - Confirm what was created
   - State the location
   - Mention it's ready for development
   - Reference available DDM XML/spec files if relevant

**For Questions**:
- Provide direct, concise answers
- Reference DDM XML or spec content when relevant
- Keep explanations focused and practical

**DO NOT**:
- Provide lengthy best practices unless asked
- Explain every detail of the file structure
- Wait for user confirmation between automated steps
- Repeat information already provided in the prompt

**Example Good Response** (for automated setup):
"✅ Created Simics project at /path/to/simics-project
✅ Added DML device skeleton for 'wdt'
Project ready for DML development. DDM XML and spec files available for reference."

**Example Bad Response** (too verbose):
"I'll help you set up... [long explanation]... Let me first create... [more explanation]... Now let me add... [even more explanation]... Here's what we have... [lengthy details]..."

Execute tool calls immediately when instructed. Be brief and action-focused."""

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
    
    # Restrict to only the two Simics project creation tools
    simics_tool_filter = [
        "create_simics_project",
        "add_dml_device_skeleton"
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