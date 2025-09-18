#!/usr/bin/env python3
"""Example usage of Agent OS YAML configuration."""

import asyncio
import os
from pathlib import Path

# Add the parent directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from yaml_loader import load_agent_from_yaml, AgentOsYamlLoader
from google.adk.runners import InMemoryRunner


async def main():
    """Example usage of Agent OS YAML configuration."""
    print("🤖 Agent OS YAML Configuration Example")
    print("=" * 50)
    
    try:
        # Method 1: Load agent directly from YAML
        print("\n1. Loading agent from YAML configuration...")
        agent = load_agent_from_yaml()
        print(f"✅ Created agent: {agent.name}")
        print(f"✅ Model: {agent.model}")
        print(f"✅ Tools: {len(agent.tools)}")
        print(f"✅ Subagents: {len(agent.sub_agents)}")
        
        # Method 2: Use the loader for more control
        print("\n2. Using YAML loader for configuration details...")
        loader = AgentOsYamlLoader()
        loader.print_config_summary()
        
        # Validate environment
        if loader.validate_environment():
            print("✅ Environment validation passed")
        else:
            print("⚠️  Environment validation failed")
        
        # Show available workflows
        workflows = loader.get_workflows()
        if workflows:
            print(f"\n📋 Available Workflows:")
            for workflow_name, workflow_config in workflows.items():
                print(f"  - {workflow_config.get('name', workflow_name)}")
                print(f"    Description: {workflow_config.get('description', 'No description')}")
                steps = workflow_config.get('steps', [])
                if steps:
                    print(f"    Steps: {' → '.join(steps)}")
        
        # Method 3: Use with ADK runner
        print("\n3. Using agent with ADK runner...")
        runner = InMemoryRunner(agent)
        print("✅ Runner created successfully")
        
        # Example conversation (commented out to avoid actual LLM calls)
        print("\n4. Example conversation (simulated)...")
        print("   User: 'Help me plan a new web application'")
        print("   Agent: [Would respond using Agent OS workflows]")
        print("   User: 'Create a spec for user authentication'")
        print("   Agent: [Would create comprehensive specification]")
        
        print("\n🎉 YAML configuration example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_yaml_configuration():
    """Test the YAML configuration loading."""
    print("🧪 Testing YAML Configuration")
    print("=" * 30)
    
    try:
        # Test loading configuration
        loader = AgentOsYamlLoader()
        
        # Test agent creation
        agent = loader.create_agent()
        assert agent.name == "agent_os_agent"
        assert agent.model == "iflow/Qwen3-Coder"
        assert len(agent.tools) == 1  # Should have Agent OS toolset
        assert len(agent.sub_agents) == 6  # Should have 6 subagents
        
        print("✅ Agent creation test passed")
        
        # Test workflow loading
        workflows = loader.get_workflows()
        assert len(workflows) > 0
        assert "product_planning" in workflows
        assert "spec_creation" in workflows
        
        print("✅ Workflow loading test passed")
        
        # Test configuration access
        runner_config = loader.get_runner_config()
        logging_config = loader.get_logging_config()
        env_config = loader.get_environment_config()
        
        assert "type" in runner_config
        assert "level" in logging_config
        assert "required_vars" in env_config
        
        print("✅ Configuration access test passed")
        
        print("\n🎉 All YAML configuration tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run tests first
    test_yaml_configuration()
    
    # Then run example
    asyncio.run(main())
