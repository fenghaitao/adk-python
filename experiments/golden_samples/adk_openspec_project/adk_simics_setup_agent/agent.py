import sys
import os

# Add parent directory to path for simics_integration imports
sys.path.insert(0, os.path.dirname('/nfs/site/disks/ssm_yongzhuo_001/ai_agents/adk-openspec/contributing/samples/simics_integration'))

# Import the Simics integration agent
sys.path.insert(0, '/nfs/site/disks/ssm_yongzhuo_001/ai_agents/adk-openspec/contributing/samples/simics_integration')
from agent import root_agent
