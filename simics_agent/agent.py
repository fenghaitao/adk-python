import os
import sys
import argparse
from pathlib import Path
from typing import Optional

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
from google.adk.tools import agent_tool

try:
    from spec_kit_tools import create_spec_kit_toolset
except ImportError:
    # Fallback if direct import fails, though sys.path should handle it
    sys.path.append(str(spec_kit_integration_dir))
    from spec_kit_tools import create_spec_kit_toolset

# Import and add simicsDocAgent
sys.path.append(str(current_dir.parent / "simics_doc_agents"))
from simics_doc_agents.agent import root_agent as simicsDocAgent

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
        # Core project management tools
        "list_installed_packages",
        "list_simics_platforms",
        "get_simics_version",

        # Device modeling and development tools
        "create_simics_project",
        "add_dml_device_skeleton",
        "build_simics_project",
        "setup_project",
        # "run_simics_test",

        # RAG query tool for documentation and source code search
        "perform_rag_query",

        # "get_concepts_doc",
        # "get_test_example",
        "search_simics_docs",
        "get_simics_device_example_i2c",
        "get_simics_device_example_ds12887",
        # "get_simics_dml_template",

    ]

    return MCPToolset(
        connection_params=connection_params,
        tool_filter=tool_filter
    )


class SimicsAgent(LlmAgent):
    """Simics Agent using LiteLLM and Spec-Kit tools."""
    pass


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

# Read instructions
instruction_path = current_dir / "instructions.md"

if not instruction_path.exists():
    print(f"Error: Instruction file not found at {instruction_path}")
    exit(1)

with open(instruction_path, 'r') as f:
    instruction_template = f.read()

# Read additional files and replace placeholders in instruction_template
concepts_path = current_dir / "simics_concepts.md"
example_path = current_dir / "sample-device.dml"
test_path = current_dir / "simics_test.md"

with open(concepts_path, 'r') as f:
    concepts_content = f.read()

with open(example_path, 'r') as f:
    example_content = f.read()

with open(test_path, 'r') as f:
    test_content = f.read()

instruction_template = instruction_template.replace("$CONCEPTS", concepts_content)
instruction_template = instruction_template.replace("$EXAMPLE", example_content)
instruction_template = instruction_template.replace("$TEST", test_content)

instruction = instruction_template

# Initialize LiteLLM
llm = LiteLlm(
    model=model_name,
    api_key=api_key,
    base_url=base_url
)

# Initialize Tools
tools = []
tools.append(create_spec_kit_toolset())
try:
    tools.append(create_simics_mcp_toolset())
except Exception as e:
    print(f"Warning: Simics MCP toolset not available: {e}")

tools.append(agent_tool.AgentTool(agent=simicsDocAgent))


# Initialize Agent
root_agent = SimicsAgent(
    name="simics_agent",
    model=llm,
    instruction=instruction,
    tools=tools
)

print(f"Agent initialized with model {model_name}")
