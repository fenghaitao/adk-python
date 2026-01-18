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

"""DSPy module for OpenSpec archive agent.

This module uses ChainOfThought with the ArchiveSignature to finalize
OpenSpec changes following the workflow defined in the instruction markdown.
"""

from __future__ import annotations

import dspy
from dspy_openspec.signatures.archive import ArchiveSignature


class ArchiveModule(dspy.Module):
  """Archive OpenSpec changes after implementation.
  
  This module follows the archive workflow defined in
  archive_agent_instruction.md, including:
  - Validating change ID
  - Running openspec archive command
  - Updating specs
  - Final validation
  
  The instruction content is embedded in the ArchiveSignature docstring.
  """
  
  def __init__(self):
    """Initialize the archive module."""
    super().__init__()
    # Use ChainOfThought for step-by-step archiving
    self.archive = dspy.ChainOfThought(ArchiveSignature)
  
  def forward(
      self,
      change_id: str,
      skip_specs: bool = False
  ) -> dspy.Prediction:
    """Archive the specified change.
    
    Args:
      change_id: Change ID to archive
      skip_specs: Skip spec updates (for tooling-only work)
      
    Returns:
      Prediction with archive_status and archive_path fields
    """
    result = self.archive(
      change_id=change_id,
      skip_specs=skip_specs
    )
    return result
