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

"""ScoreAgent for evaluating apply_agent implementation results.

This agent evaluates the quality of DML implementations and test files
produced by the apply_agent, as well as analyzing how well the agent
followed best practices during execution.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Import ADK
try:
  from google.adk.agents.llm_agent import LlmAgent
except ImportError:
  current_dir = Path(__file__).parent
  adk_src_dir = current_dir.parent.parent.parent / "src"
  if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))
    from google.adk.agents.llm_agent import LlmAgent

try:
  from .openspec_tools import create_openspec_toolset
except ImportError:
  from openspec_tools import create_openspec_toolset


def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class CodeQualityScore(BaseModel):
  """Code quality evaluation scores."""
  build_pass: int = Field(..., description="Score for passing build (0-30)")
  test_pass: int = Field(..., description="Score for passing tests (0-10)")
  dml_quality: int = Field(..., description="Score for DML code quality (0-30)")
  test_quality: int = Field(..., description="Score for test code quality (0-20)")
  total_code_score: int = Field(..., description="Total code quality score (0-90)")
  evidence: Dict[str, Any] = Field(..., description="Evidence/proof for each scoring criterion (can be strings, numbers, or other data)")


class AgentBehaviorScore(BaseModel):
  """Agent behavior and process compliance scores."""
  documentation_reading: int = Field(..., description="Score for reading required docs (0-50)")
  efficiency: int = Field(..., description="Score for efficiency and best practices (0-30)")
  time_score: int = Field(..., description="Score based on completion time (0-10)")
  total_behavior_score: int = Field(..., description="Total agent behavior score (0-90)")
  evidence: Dict[str, Any] = Field(..., description="Evidence/proof for each scoring criterion (can be strings, numbers, or other data)")


class FinalScore(BaseModel):
  """Final comprehensive evaluation score."""
  code_quality_score: CodeQualityScore
  agent_behavior_score: AgentBehaviorScore
  overall_score: int = Field(..., description="Overall total score (0-180)")
  summary: str = Field(..., description="Executive summary of the evaluation")
  report_file: str = Field(..., description="Full absolute path to the saved score.md report")


class ScoreAgent(LlmAgent):
  """Agent that scores apply_agent implementation quality."""

  def __init__(self, **kwargs):
    # Load instruction from external markdown file
    instruction_file = Path(__file__).parent / "score_agent_instruction.md"
    try:
      instruction = instruction_file.read_text()
    except FileNotFoundError:
      raise RuntimeError(f"Score agent instruction file not found: {instruction_file}")
    
    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "score_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description=(
        "Agent that evaluates apply_agent implementation quality "
        "and behavior compliance"
      ),
      output_schema=FinalScore,
      **kwargs,
    )


# Create the score agent instance for ADK discovery
score_agent = ScoreAgent(
  name="score_agent",
  model=get_openspec_model()
)

# Alias for ADK discovery conventions
root_agent = score_agent
