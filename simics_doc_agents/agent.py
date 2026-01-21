import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Any, Dict

# Add adk-python/src to sys.path
current_dir = Path(__file__).parent.resolve()
adk_src_dir = current_dir.parent / "src"
if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))

# Add spec_kit_integration to sys.path to import tools
spec_kit_integration_dir = current_dir.parent / "contributing" / "samples" / "spec_kit_integration"
if spec_kit_integration_dir.exists():
    sys.path.insert(0, str(spec_kit_integration_dir))

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext

try:
    from spec_kit_tools import create_spec_kit_toolset
except ImportError:
    # Fallback if direct import fails, though sys.path should handle it
    sys.path.append(str(spec_kit_integration_dir))
    from spec_kit_tools import create_spec_kit_toolset


# Load interface documentation
interface_docs_path = current_dir / "all_interfaces.json"
with open(interface_docs_path, 'r', encoding='utf-8') as f:
    interface_docs = json.load(f)


class InterfaceDocTool(BaseTool):
    """Tool for retrieving full documentation of Simics interfaces."""

    def __init__(self, interface_docs: Dict[str, Any]):
        super().__init__(
            name="get_interface_doc",
            description="Get the full documentation for a specific Simics interface by its name.",
        )
        self.interface_docs = interface_docs

    def _get_declaration(self) -> Optional['types.FunctionDeclaration']:
        """Get function declaration for the LLM."""
        try:
            from google.genai import types
            return types.FunctionDeclaration(
                name="get_interface_doc",
                description="Get the full documentation for a specific Simics interface by its name.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "interface_name": types.Schema(
                            type=types.Type.STRING,
                            description="The name of the Simics interface to retrieve documentation for"
                        )
                    },
                    required=["interface_name"]
                )
            )
        except ImportError:
            return None

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext
    ) -> Any:
        interface_name = args.get("interface_name")
        if not interface_name:
            return {"error": "interface_name is required"}

        # Check if interface exists in contents
        if interface_name not in self.interface_docs.get("contents", {}):
            available_interfaces = list(self.interface_docs.get("descs", {}).keys())
            return {
                "error": f"Interface '{interface_name}' not found in documentation.",
                "suggestion": f"Available interfaces: {len(available_interfaces)} total. Did you mean one of these similar names?",
                "sample_interfaces": [iface for iface in available_interfaces if interface_name.lower() in iface.lower()][:5]
            }

        full_doc = self.interface_docs["contents"][interface_name]
        short_desc = self.interface_docs.get("descs", {}).get(interface_name, "No short description available")

        return {
            "interface_name": interface_name,
            "short_description": short_desc,
            "full_documentation": full_doc
        }


class SimicsDocToolset(BaseToolset):
    """Toolset for Simics interface documentation tools."""

    def __init__(self, interface_docs: Dict[str, Any]):
        super().__init__()
        self.name = "simics_doc_toolset"
        self.tools = [
            InterfaceDocTool(interface_docs)
        ]

    async def get_tools(self, readonly_context=None):
        """Return all tools in this toolset."""
        return self.tools


def create_simics_mcp_toolset(port: Optional[int] = None) -> MCPToolset:
    """Create a MCP toolset that connects to the simics-mcp-server with content truncation.
    
    Args:
        port: MCP server port. If not provided, reads from MCP_PORT environment variable
              or defaults to 8051.
    """
    # Get port from parameter, environment variable, or default
    if port is None:
        port = int(os.environ.get('MCP_PORT', '8051'))
    
    print(f"Creating Simics MCP toolset connecting to port {port}...")
    connection_params = SseConnectionParams(
        url=f"http://127.0.0.1:{port}/sse",
        headers={"Accept": "text/event-stream"},
        timeout=10.0,
        sse_read_timeout=300.0
    )

    # Filter for specific Simics tools we want to expose
    tool_filter = [
        # RAG query tool for documentation and source code search
        # "perform_rag_query",

        # "get_concepts_doc",
        # "get_test_example",
        "search_simics_docs",
        "get_simics_dml_template",
    ]

    return MCPToolset(
        connection_params=connection_params,
        tool_filter=tool_filter
    )

# Load instruction prompt
instruction_path = current_dir / "doc_instructions.md"
with open(instruction_path, 'r', encoding='utf-8') as f:
    instruction_template = f.read()

# Format instruction with interface descriptions JSON
interface_descs_json = json.dumps(interface_docs["descs"], indent=2)
instruction = instruction_template.replace("{INTERFACE_DESCS_JSON}", interface_descs_json)

# Load .env
env_path = current_dir / ".env"
# load_dotenv(env_path)

# Get config from env
base_url = os.environ.get("LITELLM_BASE_URL")
api_key = os.environ.get("LITELLM_API_KEY")
model_name = os.environ.get("LITELLM_MODEL")

if not all([base_url, api_key, model_name]):
    print("Error: BASE_URL, API_KEY, MODEL and REQ must be set in .env file or environment variables.")
    exit(1)

# Initialize LiteLLM
llm = LiteLlm(
    model=model_name,
    api_key=api_key,
    base_url=base_url
)

# Initialize Tools
tools = []
# Add Simics documentation toolset
tools.append(SimicsDocToolset(interface_docs))
# tools.append(create_spec_kit_toolset())
try:
    tools.append(create_simics_mcp_toolset())
except Exception as e:
    print(f"Warning: Simics MCP toolset not available: {e}")

# Initialize Agent
root_agent = LlmAgent(
    name="simics_interface_agent",
    description="Agent for finding Simics interfaces by your demands",
    model=llm,
    instruction=instruction,
    tools=tools
)

print(f"Agent initialized with model {model_name}")
