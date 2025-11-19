import sys
sys.path.insert(0, '/nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/contributing/samples')

# Import the root_agent from the openspec_integration package using proper package import
# This allows relative imports within openspec_integration to work correctly (e.g., MCP tools)
from openspec_integration.agent import root_agent
