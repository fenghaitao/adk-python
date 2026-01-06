import sys
import os

# Add samples directory to path first for package imports
sys.path.insert(0, '/nfs/site/disks/stod.ssm.hfeng1.0/coder/adk-python/contributing/samples')

# Import the OpenSpec agent as a package module (enables relative imports)
from openspec_integration.agent import root_agent
