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

"""Test file parser."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


class TestParser:
  """Parser for test files."""
  
  def parse_file(self, file_path: Path) -> Dict:
    """Parse a test file and extract key components.
    
    Args:
      file_path: Path to test file
    
    Returns:
      Dictionary with parsed components
    """
    content = file_path.read_text()
    
    return {
      "test_functions": self._extract_test_functions(content),
      "assertions": self._count_assertions(content),
      "register_tests": self._extract_register_tests(content),
      "has_edge_cases": self._has_edge_case_tests(content),
      "has_error_tests": self._has_error_tests(content),
    }
  
  def _extract_test_functions(self, content: str) -> List[str]:
    """Extract test function names."""
    # Match: def test_<name>
    pattern = r'def\s+(test_\w+)'
    return re.findall(pattern, content)
  
  def _count_assertions(self, content: str) -> int:
    """Count assertion statements."""
    # Match: assert, assertEqual, etc.
    patterns = [
      r'\bassert\b',
      r'\bassertEqual',
      r'\bassertTrue',
      r'\bassertFalse',
    ]
    count = 0
    for pattern in patterns:
      count += len(re.findall(pattern, content))
    return count
  
  def _extract_register_tests(self, content: str) -> List[str]:
    """Extract which registers are tested."""
    # Look for register access patterns
    # Match: obj.<register_name>
    pattern = r'obj\.(\w+)'
    return list(set(re.findall(pattern, content)))
  
  def _has_edge_case_tests(self, content: str) -> bool:
    """Check if tests include edge cases."""
    edge_case_keywords = [
      'boundary',
      'edge',
      'max',
      'min',
      'overflow',
      'underflow',
      '0xff',
      '0x00',
    ]
    return any(keyword in content.lower() for keyword in edge_case_keywords)
  
  def _has_error_tests(self, content: str) -> bool:
    """Check if tests include error conditions."""
    error_keywords = [
      'error',
      'invalid',
      'exception',
      'fail',
      'raises',
    ]
    return any(keyword in content.lower() for keyword in error_keywords)
