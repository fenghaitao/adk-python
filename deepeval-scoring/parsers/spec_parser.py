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

"""Specification parser."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


class SpecParser:
  """Parser for specification files."""
  
  def parse_file(self, file_path: Path) -> Dict:
    """Parse a specification file.
    
    Args:
      file_path: Path to spec file
    
    Returns:
      Dictionary with parsed spec data
    """
    content = file_path.read_text()
    
    return {
      "required_registers": self._extract_required_registers(content),
      "requirements": self._extract_requirements(content),
      "constraints": self._extract_constraints(content),
    }
  
  def _extract_required_registers(self, content: str) -> List[str]:
    """Extract required register names from spec."""
    # Look for register definitions in spec
    # Common patterns: "Register: NAME", "- NAME register", etc.
    patterns = [
      r'Register:\s*(\w+)',
      r'-\s*(\w+)\s+register',
      r'`(\w+)`\s+register',
    ]
    registers = []
    for pattern in patterns:
      registers.extend(re.findall(pattern, content, re.IGNORECASE))
    return list(set(registers))
  
  def _extract_requirements(self, content: str) -> List[str]:
    """Extract requirements from spec."""
    # Look for requirement sections
    requirements = []
    
    # Find sections with "Requirements", "Must", "Should"
    lines = content.split('\n')
    for i, line in enumerate(lines):
      if any(keyword in line.lower() for keyword in ['requirement', 'must', 'should']):
        # Extract the requirement text
        if ':' in line:
          req = line.split(':', 1)[1].strip()
          if req:
            requirements.append(req)
        elif i + 1 < len(lines):
          requirements.append(lines[i + 1].strip())
    
    return requirements
  
  def _extract_constraints(self, content: str) -> List[str]:
    """Extract constraints from spec."""
    # Look for constraint sections
    constraints = []
    
    # Find sections with "Constraint", "Limitation", "Not"
    lines = content.split('\n')
    for i, line in enumerate(lines):
      if any(keyword in line.lower() for keyword in ['constraint', 'limitation', 'must not']):
        if ':' in line:
          constraint = line.split(':', 1)[1].strip()
          if constraint:
            constraints.append(constraint)
        elif i + 1 < len(lines):
          constraints.append(lines[i + 1].strip())
    
    return constraints
