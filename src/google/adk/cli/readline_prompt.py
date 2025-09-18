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

from __future__ import annotations

import os
import sys
from typing import Optional


class ReadlinePrompt:
  """Enhanced prompt handler with readline, history and arrow key support."""

  def __init__(self, history_file: Optional[str] = None):
    """Initialize the readline prompt handler.
    
    Args:
      history_file: Optional path to save/load command history.
    """
    self.history = []
    self.history_file = history_file or os.path.expanduser('~/.adk_history')
    self._load_history()
    self._setup_readline()

  def _setup_readline(self) -> None:
    """Set up readline functionality for arrow key and history support."""
    try:
      import readline
      import atexit
      
      # Configure readline
      readline.set_history_length(1000)
      
      # Enable tab completion
      readline.parse_and_bind('tab: complete')
      
      # Enable arrow key navigation
      readline.parse_and_bind('"\e[A": history-search-backward')
      readline.parse_and_bind('"\e[B": history-search-forward')
      readline.parse_and_bind('"\e[C": forward-char')
      readline.parse_and_bind('"\e[D": backward-char')
      
      # Load existing history into readline
      for item in self.history:
        readline.add_history(item)
      
      # Save history on exit
      atexit.register(self._save_history)
      
    except ImportError:
      # Readline not available (e.g., on Windows without pyreadline)
      print("Info: Enhanced readline features not available.")
      print("For full arrow key and history support:")
      print("  - On Windows: pip install pyreadline3")
      print("  - On macOS/Linux: readline should be built-in")
      print("Basic input functionality will still work.")

  def _load_history(self) -> None:
    """Load command history from file."""
    try:
      if os.path.exists(self.history_file):
        with open(self.history_file, 'r', encoding='utf-8') as f:
          self.history = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
      print(f"Warning: Could not load history from {self.history_file}: {e}")

  def _save_history(self) -> None:
    """Save command history to file."""
    try:
      # Use our internal history which we've been maintaining without duplicates
      # Don't pull from readline again as that would introduce duplicates
      
      # Save to file
      os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
      with open(self.history_file, 'w', encoding='utf-8') as f:
        # Remove any potential duplicates and keep last 1000 items
        unique_history = []
        for item in self.history[-1000:]:
          if not unique_history or item != unique_history[-1]:
            unique_history.append(item)
        
        for item in unique_history:
          f.write(f"{item}\n")
    except Exception as e:
      print(f"Warning: Could not save history to {self.history_file}: {e}")

  def get_input(self, prompt: str = '[user]: ') -> str:
    """Get input from user with history and arrow key support.
    
    Args:
      prompt: The prompt string to display.
      
    Returns:
      The user input string.
    """
    try:
      user_input = input(prompt)
      
      # Add to history if it's not empty and not the same as last entry
      # Only add to our internal history - readline manages its own
      if user_input.strip() and (not self.history or user_input.strip() != self.history[-1]):
        try:
          import readline
          # readline automatically adds to its history, so we don't need to call add_history
          # Just add to our internal history for saving to file
          self.history.append(user_input.strip())
        except ImportError:
          # If readline not available, manage history ourselves
          self.history.append(user_input.strip())
      
      return user_input
      
    except (EOFError, KeyboardInterrupt):
      # Handle Ctrl+C or Ctrl+D gracefully
      print("\nExiting...")
      sys.exit(0)

  def clear_history(self) -> None:
    """Clear the command history."""
    self.history.clear()
    try:
      import readline
      readline.clear_history()
    except ImportError:
      pass
    
    # Remove history file
    try:
      if os.path.exists(self.history_file):
        os.remove(self.history_file)
    except Exception as e:
      print(f"Warning: Could not remove history file: {e}")