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

"""Session log parser."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class SessionParser:
  """Parser for agent session logs."""
  
  def parse_file(self, file_path: Path) -> Dict:
    """Parse a session log file.
    
    Args:
      file_path: Path to session log file
    
    Returns:
      Dictionary with parsed session data
    """
    content = file_path.read_text()
    
    # Try to parse as JSON first
    try:
      data = json.loads(content)
      return self._parse_json_session(data)
    except json.JSONDecodeError:
      # Fall back to text parsing
      return self._parse_text_session(content)
  
  def _parse_json_session(self, data: Dict) -> Dict:
    """Parse JSON-formatted session log."""
    return {
      "total_turns": len(data.get("turns", [])),
      "tool_calls": self._extract_tool_calls_json(data),
      "doc_reads": self._count_doc_reads_json(data),
      "file_operations": self._count_file_operations_json(data),
      "build_attempts": self._count_build_attempts_json(data),
      "errors": self._extract_errors_json(data),
    }
  
  def _parse_text_session(self, content: str) -> Dict:
    """Parse text-formatted session log."""
    return {
      "total_turns": self._count_turns_text(content),
      "tool_calls": self._extract_tool_calls_text(content),
      "doc_reads": self._count_doc_reads_text(content),
      "file_operations": self._count_file_operations_text(content),
      "build_attempts": self._count_build_attempts_text(content),
      "errors": self._extract_errors_text(content),
    }
  
  def _extract_tool_calls_json(self, data: Dict) -> List[str]:
    """Extract tool calls from JSON session."""
    tool_calls = []
    for turn in data.get("turns", []):
      for action in turn.get("actions", []):
        if "tool" in action:
          tool_calls.append(action["tool"])
    return tool_calls
  
  def _count_doc_reads_json(self, data: Dict) -> int:
    """Count documentation reads from JSON session."""
    count = 0
    for turn in data.get("turns", []):
      for action in turn.get("actions", []):
        if action.get("tool") in ["readFile", "webFetch"]:
          if "doc" in str(action.get("args", {})).lower():
            count += 1
    return count
  
  def _count_file_operations_json(self, data: Dict) -> int:
    """Count file operations from JSON session."""
    file_tools = ["fsWrite", "strReplace", "fsAppend", "readFile"]
    count = 0
    for turn in data.get("turns", []):
      for action in turn.get("actions", []):
        if action.get("tool") in file_tools:
          count += 1
    return count
  
  def _count_build_attempts_json(self, data: Dict) -> int:
    """Count build attempts from JSON session."""
    count = 0
    for turn in data.get("turns", []):
      for action in turn.get("actions", []):
        if "make" in str(action.get("args", {})).lower():
          count += 1
    return count
  
  def _extract_errors_json(self, data: Dict) -> List[str]:
    """Extract errors from JSON session."""
    errors = []
    for turn in data.get("turns", []):
      if "error" in turn:
        errors.append(turn["error"])
    return errors
  
  def _count_turns_text(self, content: str) -> int:
    """Count turns in text session."""
    return len(re.findall(r'Turn \d+', content))
  
  def _extract_tool_calls_text(self, content: str) -> List[str]:
    """Extract tool calls from text session."""
    pattern = r'Tool: (\w+)'
    return re.findall(pattern, content)
  
  def _count_doc_reads_text(self, content: str) -> int:
    """Count documentation reads from text session."""
    return len(re.findall(r'readFile.*doc', content, re.IGNORECASE))
  
  def _count_file_operations_text(self, content: str) -> int:
    """Count file operations from text session."""
    patterns = [r'fsWrite', r'strReplace', r'fsAppend', r'readFile']
    count = 0
    for pattern in patterns:
      count += len(re.findall(pattern, content))
    return count
  
  def _count_build_attempts_text(self, content: str) -> int:
    """Count build attempts from text session."""
    return len(re.findall(r'make', content, re.IGNORECASE))
  
  def _extract_errors_text(self, content: str) -> List[str]:
    """Extract errors from text session."""
    pattern = r'Error: (.+)'
    return re.findall(pattern, content)
