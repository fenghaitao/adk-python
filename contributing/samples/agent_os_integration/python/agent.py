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

"""Agent OS Agent configuration for ADK."""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from agent_os_agent import AgentOsAgent


def get_agent_os_path():
    """Get Agent OS path from environment or use default."""
    # Default to .agent-os directory (users install agent-os here)
    default_path = ".agent-os"
    return os.environ.get("AGENT_OS_PATH", default_path)


def get_agent_os_model():
    """Get Agent OS model from environment or use default."""
    return os.environ.get("AGENT_OS_MODEL", "github_copilot/gpt-5-mini")


# Create Agent OS Agent with Agent OS configuration
agent_os_agent = AgentOsAgent.create_with_agent_os(
    agent_os_path=get_agent_os_path(),
    project_path=".",
    name="agent_os_agent",
    model=get_agent_os_model(),
)

# Add Agent OS subagents
agent_os_agent.add_agent_os_subagents(get_agent_os_path())

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = agent_os_agent
