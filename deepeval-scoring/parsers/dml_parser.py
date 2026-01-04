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

"""DML code parser."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional


class DMLParser:
  """Parser for DML code files."""
  
  def parse_file(self, file_path: Path) -> Dict:
    """Parse a DML file and extract key components.
    
    Args:
      file_path: Path to DML file
    
    Returns:
      Dictionary with parsed components
    """
    content = file_path.read_text()
    
    return {
      "registers": self._extract_registers(content),
      "events": self._extract_events(content),
      "methods": self._extract_methods(content),
      "imports": self._extract_imports(content),
      "has_session_vars": self._has_session_variables(content),
      "has_reset_logic": self._has_reset_logic(content),
      "has_interrupt_logic": self._has_interrupt_logic(content),
    }
  
  def _extract_registers(self, content: str) -> List[str]:
    """Extract register names from DML code."""
    # Match: register <name> ...
    pattern = r'register\s+(\w+)'
    return re.findall(pattern, content)
  
  def _extract_events(self, content: str) -> List[str]:
    """Extract event names from DML code."""
    # Match: event <name>
    pattern = r'event\s+(\w+)'
    return re.findall(pattern, content)
  
  def _extract_methods(self, content: str) -> List[str]:
    """Extract method names from DML code."""
    # Match: method <name>
    pattern = r'method\s+(\w+)'
    return re.findall(pattern, content)
  
  def _extract_imports(self, content: str) -> List[str]:
    """Extract import statements."""
    # Match: import "..."
    pattern = r'import\s+"([^"]+)"'
    return re.findall(pattern, content)
  
  def _has_session_variables(self, content: str) -> bool:
    """Check if code uses session variables."""
    return 'session' in content.lower()
  
  def _has_reset_logic(self, content: str) -> bool:
    """Check if code has reset logic."""
    return 'reset' in content.lower()
  
  def _has_interrupt_logic(self, content: str) -> bool:
    """Check if code has interrupt logic."""
    return 'interrupt' in content.lower() or 'signal' in content.lower()
