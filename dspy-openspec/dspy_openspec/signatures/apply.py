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

"""DSPy signature for OpenSpec apply agent.

This signature uses the apply_agent_instruction.md file directly as its
docstring, ensuring consistency with the ADK-Python implementation.
"""

from __future__ import annotations

from pathlib import Path
import dspy

# Load instruction markdown from ADK implementation
INSTRUCTION_FILE = (
  Path(__file__).parent.parent.parent.parent
  / "contributing/samples/openspec_integration"
  / "apply_agent_instruction.md"
)

# Read instruction content
APPLY_INSTRUCTION = INSTRUCTION_FILE.read_text()


class ApplySignature(dspy.Signature):
  # Use instruction markdown as docstring
  __doc__ = APPLY_INSTRUCTION
  
  # Input fields
  change_id: str = dspy.InputField(
    desc="Change ID to apply (from proposal phase)"
  )
  
  # Output fields
  implementation_status: str = dspy.OutputField(
    desc="Status of implementation (success/partial/failed)"
  )
  files_modified: str = dspy.OutputField(
    desc="List of files modified during implementation"
  )
  validation_result: str = dspy.OutputField(
    desc="Result of validation checks"
  )
  completed: bool = dspy.OutputField(
    desc="True only after all DML files and tests have been written and validated"
  )
