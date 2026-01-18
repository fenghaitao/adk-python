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

"""Session logging for DSPy OpenSpec.

Provides ADK-Python-style session logging for DSPy interactions.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import dspy


class SessionLogger:
  """Logger for DSPy OpenSpec sessions.
  
  Captures LLM interactions in a format similar to ADK-Python sessions.
  """
  
  def __init__(
      self,
      session_id: Optional[str] = None,
      log_dir: Path = Path("sessions")
  ):
    """Initialize session logger.
    
    Args:
      session_id: Unique session identifier (generated if not provided)
      log_dir: Directory to store session logs
    """
    self.session_id = session_id or str(uuid.uuid4())
    self.log_dir = Path(log_dir)
    self.log_dir.mkdir(parents=True, exist_ok=True)
    
    self.start_time = datetime.now()
    self.events: List[Dict[str, Any]] = []
    self.metadata: Dict[str, Any] = {}
  
  def log_user_input(self, content: str, **kwargs):
    """Log user input.
    
    Args:
      content: User input text
      **kwargs: Additional metadata
    """
    event = {
      "timestamp": datetime.now().isoformat(),
      "author": "user",
      "content": content,
      "metadata": kwargs
    }
    self.events.append(event)
  
  def log_agent_response(
      self,
      agent_name: str,
      content: str,
      **kwargs
  ):
    """Log agent response.
    
    Args:
      agent_name: Name of the agent (e.g., "proposal_agent")
      content: Agent response text
      **kwargs: Additional metadata
    """
    event = {
      "timestamp": datetime.now().isoformat(),
      "author": agent_name,
      "content": content,
      "metadata": kwargs
    }
    self.events.append(event)
  
  def log_llm_call(
      self,
      messages: List[Dict[str, str]],
      response: Any,
      model: str
  ):
    """Log LLM API call.
    
    Args:
      messages: Input messages to LLM
      response: LLM response
      model: Model identifier
    """
    event = {
      "timestamp": datetime.now().isoformat(),
      "type": "llm_call",
      "model": model,
      "messages": messages,
      "response": self._extract_response_content(response),
    }
    self.events.append(event)
  
  def _extract_response_content(self, response: Any) -> str:
    """Extract content from LLM response.
    
    Args:
      response: LLM response object
      
    Returns:
      Response content as string
    """
    if hasattr(response, 'choices') and response.choices:
      return response.choices[0].message.content
    elif isinstance(response, str):
      return response
    else:
      return str(response)
  
  def capture_dspy_history(self, agent_name: str):
    """Capture DSPy LLM history.
    
    Args:
      agent_name: Name of the agent making the calls
    """
    lm = dspy.settings.lm
    if hasattr(lm, 'history') and lm.history:
      for entry in lm.history:
        messages = entry.get('messages', [])
        response = entry.get('response')
        
        self.log_llm_call(
          messages=messages,
          response=response,
          model=getattr(lm, 'model', 'unknown')
        )
  
  def set_metadata(self, **kwargs):
    """Set session metadata.
    
    Args:
      **kwargs: Metadata key-value pairs
    """
    self.metadata.update(kwargs)
  
  def save_text_log(self, filename: Optional[str] = None) -> Path:
    """Save session as text log (ADK-Python style).
    
    Args:
      filename: Log filename (auto-generated if not provided)
      
    Returns:
      Path to saved log file
    """
    if filename is None:
      timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
      filename = f"session_{timestamp}.log"
    
    log_path = self.log_dir / filename
    
    with open(log_path, 'w') as f:
      # Write header
      f.write(f"Session ID: {self.session_id}\n")
      f.write(f"Start Time: {self.start_time.isoformat()}\n")
      f.write(f"Metadata: {json.dumps(self.metadata, indent=2)}\n")
      f.write("=" * 60 + "\n\n")
      
      # Write events
      for event in self.events:
        timestamp = event.get('timestamp', '')
        author = event.get('author', 'system')
        
        if event.get('type') == 'llm_call':
          # LLM call format
          f.write(f"{timestamp} - LLM Call\n")
          f.write(f"Model: {event.get('model')}\n")
          f.write(f"Messages:\n")
          for msg in event.get('messages', []):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            f.write(f"  [{role.upper()}]: {content[:200]}")
            if len(content) > 200:
              f.write("...")
            f.write("\n")
          f.write(f"Response: {event.get('response', '')[:200]}\n")
          f.write("\n")
        else:
          # User/agent message format
          content = event.get('content', '')
          f.write(f"[{author}]: {timestamp} - {content}\n\n")
    
    return log_path
  
  def save_json_log(self, filename: Optional[str] = None) -> Path:
    """Save session as JSON (for programmatic access).
    
    Args:
      filename: Log filename (auto-generated if not provided)
      
    Returns:
      Path to saved log file
    """
    if filename is None:
      timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
      filename = f"session_{timestamp}.json"
    
    log_path = self.log_dir / filename
    
    session_data = {
      "id": self.session_id,
      "start_time": self.start_time.isoformat(),
      "metadata": self.metadata,
      "events": self.events
    }
    
    with open(log_path, 'w') as f:
      json.dump(session_data, f, indent=2)
    
    return log_path
  
  def save(self, format: str = "both") -> Dict[str, Path]:
    """Save session logs.
    
    Args:
      format: Log format ("text", "json", or "both")
      
    Returns:
      Dictionary mapping format to file path
    """
    paths = {}
    
    if format in ("text", "both"):
      paths["text"] = self.save_text_log()
    
    if format in ("json", "both"):
      paths["json"] = self.save_json_log()
    
    return paths
