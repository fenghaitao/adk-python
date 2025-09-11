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

from .agent_os_agent import AgentOsAgent

# Create Agent OS Agent with Agent OS configuration
agent_os_agent = AgentOsAgent.create_with_agent_os_config(
    agent_os_path="/home/hfeng1/agent-os",
    project_path=".",
    name="agent_os_agent",
    model="iflow/Qwen3-Coder",
)

# Add Agent OS subagents
agent_os_agent.add_agent_os_subagents("/home/hfeng1/agent-os")

# For ADK tools compatibility, the root agent must be named `root_agent`
root_agent = agent_os_agent
