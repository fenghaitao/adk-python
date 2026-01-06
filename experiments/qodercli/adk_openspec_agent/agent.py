import sys
import os

# Add samples directory to path first for package imports
sys.path.insert(0, '/home/hfeng1/adk-python/contributing/samples')

# Import the OpenSpec agent as a package module (enables relative imports)
from openspec_integration.agent import root_agent
