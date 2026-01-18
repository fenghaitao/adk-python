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

"""DSPy signature for OpenSpec proposal generation.

This signature uses the proposal_initial_agent_instruction.md file directly
as its docstring, ensuring consistency with the ADK-Python implementation.
"""

from __future__ import annotations

from pathlib import Path
import dspy

# Load instruction markdown from ADK implementation
INSTRUCTION_FILE = (
  Path(__file__).parent.parent.parent.parent
  / "contributing/samples/openspec_integration"
  / "proposal_initial_agent_instruction.md"
)

# Read instruction content
PROPOSAL_INSTRUCTION = INSTRUCTION_FILE.read_text()


class ProposalSignature(dspy.Signature):
  # Use instruction markdown as docstring
  __doc__ = PROPOSAL_INSTRUCTION
  
  # Input fields (from "Input Format" section of instruction)
  task_description: str = dspy.InputField(
    desc="Task description or /proposal command with summary/title"
  )
  device_hint: str = dspy.InputField(
    desc="Optional device name hint for change ID generation",
    default=""
  )
  
  # Output fields (from "Output Schema" section of instruction)
  change_id: str = dspy.OutputField(
    desc="Unique change identifier (e.g., 'implement-wdt-device')"
  )
  summary: str = dspy.OutputField(
    desc="Concise summary of the proposal"
  )
  completed: bool = dspy.OutputField(
    desc="True only after proposal.md and tasks.md files have been written"
  )
