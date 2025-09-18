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

"""YAML configuration loader for Agent OS integration."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

# Import from the parent directory
import sys
from pathlib import Path as PathLib

# Add the src directory to Python path for imports
current_dir = PathLib(__file__).parent
src_dir = current_dir.parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from .agent_os_agent import AgentOsAgent
    from .agent_os_tools import create_agent_os_toolset
except ImportError:
    from agent_os_agent import AgentOsAgent
    from agent_os_tools import create_agent_os_toolset


class AgentOsYamlLoader:
    """YAML configuration loader for Agent OS agents."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the YAML loader.
        
        Args:
            config_path: Path to the YAML configuration file. If None, uses default.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "root_agent.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the YAML configuration file.
        
        Returns:
            Loaded configuration dictionary.
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def _resolve_environment_variables(self, value: str) -> str:
        """Resolve environment variables in a string value.
        
        Args:
            value: String that may contain environment variables.
            
        Returns:
            String with environment variables resolved.
        """
        if isinstance(value, str):
            # Handle ${VAR} and $VAR syntax
            import re
            pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'
            
            def replace_var(match):
                var_name = match.group(1) or match.group(2)
                return os.getenv(var_name, match.group(0))
            
            return re.sub(pattern, replace_var, value)
        return value
    
    def _resolve_config_values(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve environment variables in configuration.
        
        Args:
            config: Configuration dictionary.
            
        Returns:
            Configuration with environment variables resolved.
        """
        if isinstance(config, dict):
            return {key: self._resolve_config_values(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._resolve_config_values(item) for item in config]
        elif isinstance(config, str):
            return self._resolve_environment_variables(config)
        else:
            return config
    
    def create_agent(self) -> AgentOsAgent:
        """Create an Agent OS agent from the YAML configuration.
        
        Returns:
            Configured Agent OS agent.
        """
        # Resolve environment variables
        resolved_config = self._resolve_config_values(self.config)
        
        agent_config = resolved_config.get('agent', {})
        
        # Extract basic agent configuration
        name = agent_config.get('name', 'agent_os_agent')
        model = agent_config.get('model', 'iflow/Qwen3-Coder')
        description = agent_config.get('description', 'Agent OS Agent')
        instruction = agent_config.get('instruction', '')
        
        # Extract Agent OS specific configuration
        agent_os_config = agent_config.get('agent_os', {})
        # Default to .agent-os directory (users install agent-os here)
        default_agent_os_path = ".agent-os"
        agent_os_path = agent_os_config.get('path', default_agent_os_path)
        project_path = agent_os_config.get('project_path', '.')
        auto_load_config = agent_os_config.get('auto_load_config', True)
        auto_add_subagents = agent_os_config.get('auto_add_subagents', True)
        
        # Create the agent
        if auto_load_config:
            agent = AgentOsAgent.create_with_agent_os_config(
                agent_os_path=agent_os_path,
                project_path=project_path,
                name=name,
                model=model,
                description=description
            )
            # Override instruction if provided
            if instruction:
                agent.instruction = instruction
        else:
            agent = AgentOsAgent(
                name=name,
                model=model,
                instruction=instruction,
                description=description
            )
        
        # Add subagents if configured
        subagents_config = agent_config.get('subagents', {})
        if subagents_config.get('enabled', True) and auto_add_subagents:
            agent.add_agent_os_subagents(agent_os_path)
        
        return agent
    
    def get_workflows(self) -> Dict[str, Any]:
        """Get available workflows from the configuration.
        
        Returns:
            Dictionary of workflow configurations.
        """
        return self.config.get('workflows', {})
    
    def get_runner_config(self) -> Dict[str, Any]:
        """Get runner configuration.
        
        Returns:
            Runner configuration dictionary.
        """
        return self.config.get('runner', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration.
        
        Returns:
            Logging configuration dictionary.
        """
        return self.config.get('logging', {})
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment configuration.
        
        Returns:
            Environment configuration dictionary.
        """
        return self.config.get('environment', {})
    
    def validate_environment(self) -> bool:
        """Validate that required environment variables are set.
        
        Returns:
            True if all required environment variables are set, False otherwise.
        """
        env_config = self.get_environment_config()
        required_vars = env_config.get('required_vars', [])
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def print_config_summary(self):
        """Print a summary of the loaded configuration."""
        agent_config = self.config.get('agent', {})
        agent_os_config = agent_config.get('agent_os', {})
        
        print("🤖 Agent OS Configuration Summary")
        print("=" * 40)
        print(f"Agent Name: {agent_config.get('name', 'N/A')}")
        print(f"Model: {agent_config.get('model', 'N/A')}")
        print(f"Agent OS Path: {agent_os_config.get('path', 'N/A')}")
        print(f"Project Path: {agent_os_config.get('project_path', 'N/A')}")
        print(f"Auto Load Config: {agent_os_config.get('auto_load_config', 'N/A')}")
        print(f"Auto Add Subagents: {agent_os_config.get('auto_add_subagents', 'N/A')}")
        
        subagents_config = agent_config.get('subagents', {})
        if subagents_config.get('enabled', False):
            print(f"Subagents: {len([k for k, v in subagents_config.items() if isinstance(v, dict) and v.get('enabled', False)])} enabled")
        
        workflows = self.get_workflows()
        print(f"Available Workflows: {len(workflows)}")
        for workflow_name, workflow_config in workflows.items():
            print(f"  - {workflow_config.get('name', workflow_name)}")


def load_agent_from_yaml(config_path: Optional[str] = None) -> AgentOsAgent:
    """Convenience function to load an Agent OS agent from YAML configuration.
    
    Args:
        config_path: Path to the YAML configuration file. If None, uses default.
        
    Returns:
        Configured Agent OS agent.
    """
    loader = AgentOsYamlLoader(config_path)
    return loader.create_agent()


def main():
    """Main function for testing the YAML loader."""
    try:
        # Load configuration
        loader = AgentOsYamlLoader()
        
        # Print configuration summary
        loader.print_config_summary()
        
        # Validate environment
        if not loader.validate_environment():
            print("\n⚠️  Environment validation failed. Some features may not work properly.")
        else:
            print("\n✅ Environment validation passed.")
        
        # Create agent
        print("\n🔧 Creating Agent OS agent...")
        agent = loader.create_agent()
        
        print(f"✅ Created agent: {agent.name}")
        print(f"✅ Model: {agent.model}")
        print(f"✅ Tools: {len(agent.tools)}")
        print(f"✅ Subagents: {len(agent.sub_agents)}")
        
        # Show available workflows
        workflows = loader.get_workflows()
        if workflows:
            print(f"\n📋 Available Workflows:")
            for workflow_name, workflow_config in workflows.items():
                print(f"  - {workflow_config.get('name', workflow_name)}: {workflow_config.get('description', 'No description')}")
        
        print("\n🎉 Agent OS YAML configuration loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
