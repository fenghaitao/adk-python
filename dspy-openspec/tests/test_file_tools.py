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

"""Tests for file operation tools."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from dspy_openspec.tools.file_tools import (
  read_file,
  write_file,
  list_directory,
  file_exists,
  replace_string_in_file,
  bash_command,
  search_files,
)


def test_read_file():
  """Test reading a file."""
  with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    f.write("test content")
    temp_path = f.name
  
  try:
    content = read_file(temp_path)
    assert content == "test content"
  finally:
    Path(temp_path).unlink()


def test_write_file():
  """Test writing a file."""
  with tempfile.TemporaryDirectory() as tmpdir:
    file_path = Path(tmpdir) / "test.txt"
    result = write_file(str(file_path), "hello world")
    
    assert "Successfully wrote" in result
    assert file_path.read_text() == "hello world"


def test_list_directory():
  """Test listing directory contents."""
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create some test files
    (Path(tmpdir) / "file1.txt").write_text("test")
    (Path(tmpdir) / "file2.py").write_text("test")
    (Path(tmpdir) / "subdir").mkdir()
    
    result = list_directory(tmpdir)
    
    assert "file1.txt" in result
    assert "file2.py" in result
    assert "subdir/" in result


def test_file_exists():
  """Test checking file existence."""
  with tempfile.NamedTemporaryFile(delete=False) as f:
    temp_path = f.name
  
  try:
    assert file_exists(temp_path) is True
    assert file_exists("/nonexistent/path") is False
  finally:
    Path(temp_path).unlink()


def test_replace_string_in_file():
  """Test replacing string in file."""
  with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    f.write("line 1\nline 2\nline 3\n")
    temp_path = f.name
  
  try:
    result = replace_string_in_file(
      temp_path,
      "line 2",
      "modified line 2",
      expected_replacements=1
    )
    
    assert "Successfully replaced" in result
    content = Path(temp_path).read_text()
    assert "modified line 2" in content
    assert "line 2" not in content
  finally:
    Path(temp_path).unlink()


def test_replace_string_validation():
  """Test replace_string_in_file validation."""
  with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
    f.write("test\ntest\ntest\n")
    temp_path = f.name
  
  try:
    # Should fail because there are 3 occurrences but we expect 1
    with pytest.raises(ValueError, match="Found 3 occurrences"):
      replace_string_in_file(
        temp_path,
        "test",
        "modified",
        expected_replacements=1
      )
  finally:
    Path(temp_path).unlink()


def test_bash_command():
  """Test executing bash command."""
  result = bash_command("echo 'hello world'")
  
  assert "hello world" in result
  assert "exit code: 0" in result


def test_bash_command_with_working_directory():
  """Test bash command with working directory."""
  with tempfile.TemporaryDirectory() as tmpdir:
    result = bash_command("pwd", working_directory=tmpdir)
    assert tmpdir in result


def test_search_files():
  """Test searching files."""
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create test files
    (Path(tmpdir) / "file1.txt").write_text("hello world\ntest line\n")
    (Path(tmpdir) / "file2.txt").write_text("another file\nhello again\n")
    
    result = search_files("hello", directory=tmpdir)
    
    assert "file1.txt" in result
    assert "file2.txt" in result
    assert "hello world" in result
    assert "hello again" in result


def test_search_files_with_pattern():
  """Test searching files with file pattern."""
  with tempfile.TemporaryDirectory() as tmpdir:
    # Create test files
    (Path(tmpdir) / "test.py").write_text("import os\n")
    (Path(tmpdir) / "test.txt").write_text("import os\n")
    
    result = search_files("import", directory=tmpdir, file_pattern="*.py")
    
    assert "test.py" in result
    assert "test.txt" not in result
