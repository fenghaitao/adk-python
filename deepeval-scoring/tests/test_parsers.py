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

"""Tests for parser modules."""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.dml_parser import DMLParser
from parsers.test_parser import TestParser
from parsers.spec_parser import SpecParser


def test_dml_parser_extract_registers():
  """Test DML parser can extract register names."""
  parser = DMLParser()
  
  dml_code = """
  register control_reg {
    field enable;
  }
  
  register status_reg {
    field ready;
  }
  """
  
  registers = parser._extract_registers(dml_code)
  assert "control_reg" in registers
  assert "status_reg" in registers
  assert len(registers) == 2


def test_dml_parser_extract_events():
  """Test DML parser can extract event names."""
  parser = DMLParser()
  
  dml_code = """
  event timeout_event;
  event interrupt_event;
  """
  
  events = parser._extract_events(dml_code)
  assert "timeout_event" in events
  assert "interrupt_event" in events
  assert len(events) == 2


def test_dml_parser_has_session_variables():
  """Test DML parser can detect session variables."""
  parser = DMLParser()
  
  dml_code_with_session = "session int counter;"
  dml_code_without_session = "int counter;"
  
  assert parser._has_session_variables(dml_code_with_session) is True
  assert parser._has_session_variables(dml_code_without_session) is False


def test_test_parser_extract_test_functions():
  """Test parser can extract test function names."""
  parser = TestParser()
  
  test_code = """
  def test_register_read():
    pass
  
  def test_register_write():
    pass
  
  def helper_function():
    pass
  """
  
  test_functions = parser._extract_test_functions(test_code)
  assert "test_register_read" in test_functions
  assert "test_register_write" in test_functions
  assert "helper_function" not in test_functions
  assert len(test_functions) == 2


def test_test_parser_count_assertions():
  """Test parser can count assertions."""
  parser = TestParser()
  
  test_code = """
  def test_something():
    assert x == 1
    assertEqual(y, 2)
    assertTrue(z)
  """
  
  count = parser._count_assertions(test_code)
  assert count == 3


def test_spec_parser_extract_requirements():
  """Test spec parser can extract requirements."""
  parser = SpecParser()
  
  spec_content = """
  ## Requirements
  
  - Must implement timeout functionality
  - Should handle interrupts
  - Must support reset
  """
  
  requirements = parser._extract_requirements(spec_content)
  assert len(requirements) > 0


if __name__ == "__main__":
  # Run tests manually
  test_dml_parser_extract_registers()
  test_dml_parser_extract_events()
  test_dml_parser_has_session_variables()
  test_test_parser_extract_test_functions()
  test_test_parser_count_assertions()
  test_spec_parser_extract_requirements()
  print("✅ All parser tests passed!")
