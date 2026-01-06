import sys
import os

# Add parent directory to path for simics_integration imports
sys.path.insert(0, os.path.dirname('/home/hfeng1/adk-python/contributing/samples/simics_integration'))

# Import the Simics integration agent
sys.path.insert(0, '/home/hfeng1/adk-python/contributing/samples/simics_integration')
from agent import root_agent
