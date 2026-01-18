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

"""OpenSpec tools for file operations and validation.

Provides utilities that can be used by DSPy modules to interact with
the OpenSpec system, read files, and run validation commands.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class OpenSpecTools:
  """Tools for OpenSpec operations."""
  
  @staticmethod
  def read_spec(spec_path: str) -> str:
    """Read specification file.
    
    Args:
      spec_path: Path to spec.md file
      
    Returns:
      Content of the specification file
      
    Raises:
      FileNotFoundError: If spec file doesn't exist
    """
    path = Path(spec_path)
    if not path.exists():
      raise FileNotFoundError(f"Spec file not found: {spec_path}")
    return path.read_text()
  
  @staticmethod
  def read_memory_doc(doc_path: str) -> str:
    """Read memory document from openspec-memories.
    
    Args:
      doc_path: Path to memory document
      
    Returns:
      Content of the memory document
      
    Raises:
      FileNotFoundError: If memory document doesn't exist
    """
    path = Path(doc_path)
    if not path.exists():
      raise FileNotFoundError(f"Memory document not found: {doc_path}")
    return path.read_text()
  
  @staticmethod
  def list_memory_docs(memory_dir: str = "openspec-memories") -> List[str]:
    """List available memory documents.
    
    Args:
      memory_dir: Directory containing memory documents
      
    Returns:
      List of memory document paths
    """
    path = Path(memory_dir)
    if not path.exists():
      return []
    return [str(p) for p in path.glob("*.md")]
  
  @staticmethod
  def validate_proposal(
      change_id: str,
      strict: bool = True
  ) -> Dict[str, any]:
    """Run openspec validate command.
    
    Args:
      change_id: Change ID to validate
      strict: Use strict validation mode
      
    Returns:
      Dictionary with validation results:
        - success: bool
        - output: str (command output)
        - errors: List[str] (validation errors if any)
    """
    cmd = ["openspec", "validate", change_id]
    if strict:
      cmd.append("--strict")
    
    try:
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
      )
      
      return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "errors": result.stderr.split("\n") if result.stderr else []
      }
    except FileNotFoundError:
      return {
        "success": False,
        "output": "",
        "errors": ["openspec command not found"]
      }
  
  @staticmethod
  def list_changes() -> Dict[str, any]:
    """List OpenSpec changes.
    
    Returns:
      Dictionary with change list results:
        - success: bool
        - changes: List[str] (change IDs)
        - output: str (raw output)
    """
    try:
      result = subprocess.run(
        ["openspec", "list"],
        capture_output=True,
        text=True,
        check=False
      )
      
      # Parse change IDs from output
      changes = []
      for line in result.stdout.split("\n"):
        if line.strip() and not line.startswith("#"):
          # Extract change ID (first column)
          parts = line.split()
          if parts:
            changes.append(parts[0])
      
      return {
        "success": result.returncode == 0,
        "changes": changes,
        "output": result.stdout
      }
    except FileNotFoundError:
      return {
        "success": False,
        "changes": [],
        "output": "openspec command not found"
      }
  
  @staticmethod
  def show_change(
      change_id: str,
      json_format: bool = False,
      deltas_only: bool = False
  ) -> Dict[str, any]:
    """Show OpenSpec change details.
    
    Args:
      change_id: Change ID to show
      json_format: Return JSON format
      deltas_only: Show only deltas
      
    Returns:
      Dictionary with change details:
        - success: bool
        - output: str (change details)
    """
    cmd = ["openspec", "show", change_id]
    if json_format:
      cmd.append("--json")
    if deltas_only:
      cmd.append("--deltas-only")
    
    try:
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
      )
      
      return {
        "success": result.returncode == 0,
        "output": result.stdout
      }
    except FileNotFoundError:
      return {
        "success": False,
        "output": "openspec command not found"
      }
  
  @staticmethod
  def archive_change(
      change_id: str,
      skip_specs: bool = False,
      yes: bool = True
  ) -> Dict[str, any]:
    """Archive OpenSpec change.
    
    Args:
      change_id: Change ID to archive
      skip_specs: Skip spec updates
      yes: Auto-confirm without prompts
      
    Returns:
      Dictionary with archive results:
        - success: bool
        - output: str (command output)
    """
    cmd = ["openspec", "archive", change_id]
    if skip_specs:
      cmd.append("--skip-specs")
    if yes:
      cmd.append("--yes")
    
    try:
      result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
      )
      
      return {
        "success": result.returncode == 0,
        "output": result.stdout
      }
    except FileNotFoundError:
      return {
        "success": False,
        "output": "openspec command not found"
      }
