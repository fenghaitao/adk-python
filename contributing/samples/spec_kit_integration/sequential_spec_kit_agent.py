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

"""Sequential Spec-Kit Agent that orchestrates the 4 specialized subagents."""

import os
import sys
from pathlib import Path

# Import ADK
try:
    from google.adk.agents.sequential_agent import SequentialAgent
    from google.adk.agents.sequential_agent_config import SequentialAgentConfig
except ImportError:
    current_dir = Path(__file__).parent
    adk_src_dir = current_dir.parent.parent.parent / "src"
    if adk_src_dir.exists():
        sys.path.insert(0, str(adk_src_dir))
        from google.adk.agents.sequential_agent import SequentialAgent
        from google.adk.agents.sequential_agent_config import SequentialAgentConfig

try:
    from .specify_agent import SpecifyAgent
    from .plan_agent import PlanAgent
    from .tasks_agent import TasksAgent
    from .implement_agent import ImplementAgent
except ImportError:
    from specify_agent import SpecifyAgent
    from plan_agent import PlanAgent
    from tasks_agent import TasksAgent
    from implement_agent import ImplementAgent


def get_spec_kit_model():
    """Get Spec-Kit model from environment or use default."""
    return os.environ.get("SPEC_KIT_MODEL", "iflow/Qwen3-Coder")


def create_sequential_spec_kit_agent(**kwargs):
    """Create a sequential Spec-Kit agent with 4 specialized subagents."""
    
    # Create the 4 specialized subagents
    specify_agent = SpecifyAgent(
        name="specify_agent",
        model=get_spec_kit_model()
    )
    
    plan_agent = PlanAgent(
        name="plan_agent", 
        model=get_spec_kit_model()
    )
    
    tasks_agent = TasksAgent(
        name="tasks_agent",
        model=get_spec_kit_model()
    )
    
    implement_agent = ImplementAgent(
        name="implement_agent",
        model=get_spec_kit_model()
    )
    
    # Create the sequential agent directly with sub_agents
    sequential_agent = SequentialAgent(
        name=kwargs.get("name", "sequential_spec_kit_agent"),
        description=kwargs.get("description", "Sequential Spec-Kit agent that orchestrates /specify, /plan, /tasks, and /implement commands"),
        sub_agents=[specify_agent, plan_agent, tasks_agent, implement_agent]
    )
    
    return sequential_agent


# Create the root sequential agent
root_agent = create_sequential_spec_kit_agent(
    name="sequential_spec_kit_agent"
)