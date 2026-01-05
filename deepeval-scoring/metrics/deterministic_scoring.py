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

"""Deterministic scoring using parsers without LLM calls."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import sys
sys.path.append(str(Path(__file__).parent.parent))

from parsers.dml_parser import DMLParser
from parsers.test_parser import TestParser
from parsers.spec_parser import SpecParser


class DeterministicScorer:
  """Provides deterministic scoring without LLM calls."""
  
  def __init__(self, workdir: str, device_name: str):
    self.workdir = Path(workdir)
    self.device_name = device_name
    
    # Initialize parsers
    self.dml_parser = DMLParser()
    self.test_parser = TestParser()
    self.spec_parser = SpecParser()
  
  def score_implementation(self) -> Dict:
    """Score implementation using deterministic rules."""
    # Load and parse files
    dml_data = self._parse_dml_files()
    test_data = self._parse_test_files()
    spec_data = self._parse_spec_files()
    
    # Calculate scores
    scores = {
      "build_success": self._score_build_success(),
      "register_coverage": self._score_register_coverage(dml_data, spec_data),
      "test_coverage": self._score_test_coverage(dml_data, test_data),
      "implementation_completeness": self._score_implementation_completeness(dml_data),
      "code_structure": self._score_code_structure(dml_data),
    }
    
    # Calculate overall score
    weights = {
      "build_success": 0.2,
      "register_coverage": 0.25,
      "test_coverage": 0.25,
      "implementation_completeness": 0.2,
      "code_structure": 0.1,
    }
    
    overall_score = sum(scores[key] * weights[key] for key in scores)
    
    return {
      "overall_score": overall_score,
      "component_scores": scores,
      "weights": weights,
      "details": self._get_scoring_details(dml_data, test_data, spec_data)
    }
  
  def _parse_dml_files(self) -> Dict:
    """Parse DML implementation files."""
    dml_path = (
      self.workdir / 
      "simics-project" / 
      "modules" / 
      self.device_name / 
      f"{self.device_name}.dml"
    )
    
    if not dml_path.exists():
      return {"exists": False}
    
    parsed_data = self.dml_parser.parse_file(dml_path)
    parsed_data["exists"] = True
    parsed_data["file_size"] = dml_path.stat().st_size
    parsed_data["content"] = dml_path.read_text()
    
    return parsed_data
  
  def _parse_test_files(self) -> List[Dict]:
    """Parse test files."""
    test_dir = (
      self.workdir / 
      "simics-project" / 
      "modules" / 
      self.device_name / 
      "test"
    )
    
    if not test_dir.exists():
      return []
    
    test_files = []
    for test_file in test_dir.glob("s-*.py"):
      parsed_test = self.test_parser.parse_file(test_file)
      parsed_test["file_name"] = test_file.name
      test_files.append(parsed_test)
    
    return test_files
  
  def _parse_spec_files(self) -> Dict:
    """Parse specification files."""
    spec_files = list((self.workdir / "openspec" / "specs").rglob("spec.md"))
    
    if not spec_files:
      return {"exists": False}
    
    spec_data = self.spec_parser.parse_file(spec_files[0])
    spec_data["exists"] = True
    
    return spec_data
  
  def _score_build_success(self) -> float:
    """Score based on build success indicators."""
    # Check for common build artifacts or success indicators
    build_indicators = [
      self.workdir / "simics-project" / "modules" / self.device_name / f"{self.device_name}.dml",
      # Add more build success indicators as needed
    ]
    
    existing_indicators = sum(1 for indicator in build_indicators if indicator.exists())
    return existing_indicators / len(build_indicators) if build_indicators else 0.0
  
  def _score_register_coverage(self, dml_data: Dict, spec_data: Dict) -> float:
    """Score register implementation coverage."""
    if not dml_data.get("exists") or not spec_data.get("exists"):
      return 0.0
    
    # Extract required registers from spec
    spec_registers = spec_data.get("registers", [])
    implemented_registers = dml_data.get("registers", [])
    
    if not spec_registers:
      return 1.0  # No registers required
    
    # Calculate coverage
    covered_registers = set(implemented_registers) & set(spec_registers)
    coverage = len(covered_registers) / len(spec_registers)
    
    return min(coverage, 1.0)
  
  def _score_test_coverage(self, dml_data: Dict, test_data: List[Dict]) -> float:
    """Score test coverage."""
    if not dml_data.get("exists"):
      return 0.0
    
    implemented_registers = dml_data.get("registers", [])
    
    if not implemented_registers:
      return 1.0 if not test_data else 0.0
    
    # Check which registers have tests
    tested_registers = set()
    for test_file in test_data:
      test_functions = test_file.get("test_functions", [])
      for func in test_functions:
        # Simple heuristic: if register name appears in test function name
        for register in implemented_registers:
          if register.lower() in func.lower():
            tested_registers.add(register)
    
    coverage = len(tested_registers) / len(implemented_registers)
    return min(coverage, 1.0)
  
  def _score_implementation_completeness(self, dml_data: Dict) -> float:
    """Score implementation completeness."""
    if not dml_data.get("exists"):
      return 0.0
    
    # Check for key implementation features
    features = {
      "has_session_vars": dml_data.get("has_session_vars", False),
      "has_reset_logic": dml_data.get("has_reset_logic", False),
      "has_interrupt_logic": dml_data.get("has_interrupt_logic", False),
      "has_methods": len(dml_data.get("methods", [])) > 0,
      "has_events": len(dml_data.get("events", [])) > 0,
    }
    
    # Calculate completeness score
    implemented_features = sum(1 for feature in features.values() if feature)
    completeness = implemented_features / len(features)
    
    return completeness
  
  def _score_code_structure(self, dml_data: Dict) -> float:
    """Score code structure and organization."""
    if not dml_data.get("exists"):
      return 0.0
    
    content = dml_data.get("content", "")
    
    # Check for good structure indicators
    structure_indicators = {
      "has_imports": len(dml_data.get("imports", [])) > 0,
      "has_comments": "USER-TODO" not in content or content.count("//") > 5,
      "reasonable_size": 100 < len(content.split('\n')) < 2000,
      "proper_formatting": content.count('{') == content.count('}'),
    }
    
    score = sum(1 for indicator in structure_indicators.values() if indicator)
    return score / len(structure_indicators)
  
  def _get_scoring_details(self, dml_data: Dict, test_data: List[Dict], spec_data: Dict) -> Dict:
    """Get detailed scoring information."""
    return {
      "dml_file_exists": dml_data.get("exists", False),
      "registers_found": len(dml_data.get("registers", [])),
      "methods_found": len(dml_data.get("methods", [])),
      "events_found": len(dml_data.get("events", [])),
      "test_files_found": len(test_data),
      "spec_file_exists": spec_data.get("exists", False),
      "has_session_variables": dml_data.get("has_session_vars", False),
      "has_reset_logic": dml_data.get("has_reset_logic", False),
      "has_interrupt_logic": dml_data.get("has_interrupt_logic", False),
    }