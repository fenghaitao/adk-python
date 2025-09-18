#!/usr/bin/env python3
"""
Test if ADK can load the YAML configuration directly.
This simulates what 'adk run' does internally.
"""

import sys
from pathlib import Path

# Add parent directory to path for python.agent_os_tools import
sys.path.insert(0, str(Path(__file__).parent))

# Import ADK
try:
    from google.adk.agents.config_agent_utils import from_config
    print("✅ ADK imports successful")
except ImportError as e:
    print(f"❌ ADK import failed: {e}")
    sys.exit(1)

def test_yaml_config_loading():
    """Test loading YAML config like ADK would."""
    yaml_file = Path(__file__).parent / "yaml_agent" / "root_agent.yaml"
    
    print(f"🧪 Testing YAML config loading: {yaml_file}")
    
    try:
        # This is what ADK's `adk run` does internally
        agent = from_config(str(yaml_file))
        
        print(f"✅ Successfully loaded agent: {agent.name}")
        print(f"   Description: {agent.description}")
        print(f"   Model: {agent.model}")
        print(f"   Tools: {len(agent.tools)}")
        print(f"   Sub-agents: {len(agent.sub_agents)}")
        
        # Show sub-agents
        if agent.sub_agents:
            print("   Sub-agent names:")
            for i, sub in enumerate(agent.sub_agents):
                print(f"     {i+1}. {sub.name}")
        
        # Show tools
        if agent.tools:
            print("   Tool details:")
            for i, tool in enumerate(agent.tools):
                tool_name = getattr(tool, 'name', str(type(tool).__name__))
                print(f"     {i+1}. {tool_name}")
                if hasattr(tool, 'tools'):
                    for j, subtool in enumerate(tool.tools):
                        subtool_name = getattr(subtool, 'name', str(type(subtool).__name__))
                        print(f"        {i+1}.{j+1}. {subtool_name}")
        
        return True, agent
        
    except Exception as e:
        print(f"❌ Failed to load YAML config: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Main test function."""
    print("🚀 Testing ADK YAML Configuration Loading")
    print("=" * 50)
    
    success, agent = test_yaml_config_loading()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: ADK can load the YAML configuration!")
        print("   This means 'adk run yaml_agent/' should work.")
        return 0
    else:
        print("❌ FAILED: ADK cannot load the YAML configuration.")
        print("   The 'adk run' command will not work until this is fixed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())