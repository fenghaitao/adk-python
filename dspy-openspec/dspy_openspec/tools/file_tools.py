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

"""File operation tools for DSPy OpenSpec.

Provides tools for reading, writing, listing files, string replacement,
bash command execution, and file searching.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


def read_file(path: str) -> str:
  """Read content from a file.
  
  Args:
    path: Path to the file to read
    
  Returns:
    File content as string
    
  Raises:
    FileNotFoundError: If file doesn't exist
    PermissionError: If file can't be read
  """
  file_path = Path(path)
  
  if not file_path.exists():
    raise FileNotFoundError(f"File not found: {path}")
  
  if not file_path.is_file():
    raise ValueError(f"Path is not a file: {path}")
  
  return file_path.read_text()


def write_file(path: str, content: str) -> str:
  """Write content to a file.
  
  Args:
    path: Path to the file to write
    content: Content to write
    
  Returns:
    Success message
    
  Raises:
    PermissionError: If file can't be written
  """
  file_path = Path(path)
  
  # Create parent directories if needed
  file_path.parent.mkdir(parents=True, exist_ok=True)
  
  file_path.write_text(content)
  
  return f"Successfully wrote {len(content)} characters to {path}"


def list_directory(path: str = ".") -> str:
  """List files and directories in a path.
  
  Args:
    path: Path to list (default: current directory)
    
  Returns:
    String with file and directory names (one per line)
    
  Raises:
    FileNotFoundError: If directory doesn't exist
    NotADirectoryError: If path is not a directory
  """
  dir_path = Path(path)
  
  if not dir_path.exists():
    raise FileNotFoundError(f"Directory not found: {path}")
  
  if not dir_path.is_dir():
    raise NotADirectoryError(f"Path is not a directory: {path}")
  
  # List all items with type indicator
  items = []
  for item in sorted(dir_path.iterdir()):
    if item.is_dir():
      items.append(f"{item.name}/")
    else:
      items.append(item.name)
  
  return "\n".join(items)


def file_exists(path: str) -> bool:
  """Check if a file or directory exists.
  
  Args:
    path: Path to check
    
  Returns:
    True if path exists, False otherwise
  """
  return Path(path).exists()


def replace_string_in_file(
    file_path: str,
    old_string: str,
    new_string: str,
    expected_replacements: int = 1
) -> str:
  """Replace an exact string in a file with a new string.
  
  Use this for precise edits like updating specific code sections.
  Requires exact match with context for safety.
  
  Args:
    file_path: Path to the file to edit
    old_string: Exact string to find and replace (include context lines)
    new_string: String to replace old_string with
    expected_replacements: Number of expected replacements (default: 1)
    
  Returns:
    Success message with replacement count
    
  Raises:
    FileNotFoundError: If file doesn't exist
    ValueError: If string not found or replacement count doesn't match expected
  """
  path = Path(file_path)
  
  if not path.exists():
    raise FileNotFoundError(f"File not found: {file_path}")
  
  if not path.is_file():
    raise ValueError(f"Path is not a file: {file_path}")
  
  # Read file content
  try:
    content = path.read_text()
  except UnicodeDecodeError:
    raise ValueError(f"File is not a valid UTF-8 text file: {file_path}")
  
  # Check if old_string exists
  if old_string not in content:
    raise ValueError(
      f"String not found in file.\n"
      f"Looking for: {repr(old_string[:200])}\n"
      f"File: {file_path}"
    )
  
  # Count occurrences
  occurrences = content.count(old_string)
  
  # Validate expected replacements
  if occurrences != expected_replacements:
    raise ValueError(
      f"Found {occurrences} occurrences, but expected {expected_replacements}.\n"
      f"String: {repr(old_string[:200])}\n"
      f"File: {file_path}\n"
      f"Tip: Include more context (3-5 lines before/after) to make match unique."
    )
  
  # Perform replacement
  new_content = content.replace(old_string, new_string, expected_replacements)
  
  # Write back to file
  path.write_text(new_content)
  
  return (
    f"Successfully replaced {occurrences} occurrence(s) in {file_path}\n"
    f"Old: {old_string[:100]}{'...' if len(old_string) > 100 else ''}\n"
    f"New: {new_string[:100]}{'...' if len(new_string) > 100 else ''}"
  )


def bash_command(
    command: str,
    working_directory: str = ".",
    timeout: int = 60
) -> str:
  """Execute a bash command.
  
  Use this to run shell commands, git operations, build commands, and tests.
  
  Args:
    command: Bash command to execute
    working_directory: Directory to run command in (default: current directory)
    timeout: Timeout in seconds (default: 60)
    
  Returns:
    Command output (stdout and stderr combined)
    
  Raises:
    subprocess.TimeoutExpired: If command times out
    RuntimeError: If command fails with non-zero exit code
  """
  try:
    result = subprocess.run(
      command,
      shell=True,
      cwd=working_directory,
      capture_output=True,
      text=True,
      timeout=timeout,
    )
    
    # Combine stdout and stderr
    output = ""
    if result.stdout:
      output += result.stdout
    if result.stderr:
      if output:
        output += "\n--- stderr ---\n"
      output += result.stderr
    
    # Add return code info
    output += f"\n--- exit code: {result.returncode} ---"
    
    # Truncate if too long
    max_length = 50000
    if len(output) > max_length:
      output = (
        output[:max_length] +
        f"\n\n[OUTPUT TRUNCATED - Original length: {len(output)} chars]"
      )
    
    return output
    
  except subprocess.TimeoutExpired:
    raise subprocess.TimeoutExpired(
      command, timeout, f"Command timed out after {timeout} seconds"
    )
  except Exception as e:
    raise RuntimeError(f"Error executing command: {str(e)}")


def search_files(
    pattern: str,
    directory: str = ".",
    file_pattern: str = "*",
    case_sensitive: bool = False,
    max_results: int = 50
) -> str:
  """Search for text patterns in files using regex.
  
  Returns matching lines with file paths and line numbers.
  
  Args:
    pattern: Text pattern or regex to search for
    directory: Directory to search in (default: current directory)
    file_pattern: File pattern to match (e.g., '*.py', '*.md'). Default: '*'
    case_sensitive: If True, search is case-sensitive (default: False)
    max_results: Maximum number of results to return (default: 50)
    
  Returns:
    String with search results (file:line_number: matched_line)
    
  Raises:
    FileNotFoundError: If directory doesn't exist
    ValueError: If pattern is invalid regex
  """
  dir_path = Path(directory)
  
  if not dir_path.exists():
    raise FileNotFoundError(f"Directory not found: {directory}")
  
  # Compile regex pattern
  flags = 0 if case_sensitive else re.IGNORECASE
  try:
    regex = re.compile(pattern, flags)
  except re.error as e:
    raise ValueError(f"Invalid regex pattern: {str(e)}")
  
  matches = []
  files_searched = 0
  
  # Search through files
  for file_path in dir_path.rglob(file_pattern):
    if not file_path.is_file():
      continue
    
    # Skip hidden files and common ignore patterns
    if any(part.startswith('.') for part in file_path.parts):
      continue
    
    files_searched += 1
    
    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
      
      for line_num, line in enumerate(lines, start=1):
        if regex.search(line):
          rel_path = file_path.relative_to(dir_path)
          matches.append(f"{rel_path}:{line_num}: {line.rstrip()}")
          
          if len(matches) >= max_results:
            break
    
    except (UnicodeDecodeError, PermissionError):
      # Skip binary files and files we can't read
      continue
    except Exception:
      # Skip files that cause other errors
      continue
    
    if len(matches) >= max_results:
      break
  
  # Format results
  result = f"Searched {files_searched} files, found {len(matches)} matches"
  if len(matches) >= max_results:
    result += f" (truncated to {max_results})"
  result += ":\n\n"
  
  if matches:
    result += "\n".join(matches)
  else:
    result += "No matches found."
  
  return result


def get_file_tools():
  """Get list of file operation tools for DSPy ReAct.
  
  Returns:
    List of tool functions
  """
  return [
    read_file,
    write_file,
    list_directory,
    file_exists,
    replace_string_in_file,
    bash_command,
    search_files,
  ]
