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

"""Shared LLM utilities for metrics."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

import litellm


def _extract_json_from_response(content: str) -> str:
  """Extract JSON object from LLM response that may contain extra text."""
  # Try to find JSON object in the response
  # Look for content between { and } (handling nested braces)
  brace_count = 0
  start_idx = -1
  end_idx = -1
  
  for i, char in enumerate(content):
    if char == '{':
      if start_idx == -1:
        start_idx = i
      brace_count += 1
    elif char == '}':
      brace_count -= 1
      if brace_count == 0 and start_idx != -1:
        end_idx = i + 1
        break
  
  if start_idx != -1 and end_idx != -1:
    return content[start_idx:end_idx]
  
  # Fallback: return original content
  return content


def _setup_litellm_logging():
  """Setup LiteLLM logging to save session logs in .deepeval folder."""
  # Create .deepeval directory if it doesn't exist
  deepeval_dir = Path(".deepeval")
  deepeval_dir.mkdir(exist_ok=True)
  
  # Generate timestamp for log files
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  
  # Setup LiteLLM logging with timestamp
  litellm_log_file = deepeval_dir / f"litellm_session_{timestamp}.log"
  
  # Configure LiteLLM logger
  litellm_logger = logging.getLogger("LiteLLM")
  litellm_logger.setLevel(logging.INFO)
  
  # Remove existing handlers to avoid duplicates
  for handler in litellm_logger.handlers[:]:
    litellm_logger.removeHandler(handler)
  
  # Create file handler for LiteLLM logs
  file_handler = logging.FileHandler(litellm_log_file, mode='a')
  file_handler.setLevel(logging.INFO)
  
  # Create formatter for detailed logging
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  file_handler.setFormatter(formatter)
  
  # Add handler to logger
  litellm_logger.addHandler(file_handler)
  
  # Setup custom callback for detailed session logging
  def custom_callback(
      kwargs,                 # kwargs to completion
      completion_response,    # response from completion
      start_time, end_time    # start/end time
  ):
    """Custom callback to log detailed LiteLLM session information."""
    try:
      session_log_file = deepeval_dir / f"litellm_detailed_session_{timestamp}.log"
      
      # Prepare safe kwargs (remove sensitive data)
      safe_kwargs = kwargs.copy()
      if "api_key" in safe_kwargs:
        safe_kwargs["api_key"] = "***REDACTED***"
      
      # Log detailed session information
      session_info = {
        "timestamp": start_time.isoformat() if start_time else None,
        "duration_seconds": (end_time - start_time).total_seconds() if start_time and end_time else None,
        "model": kwargs.get("model"),
        "messages": kwargs.get("messages", []),
        "response": {
          "choices": getattr(completion_response, 'choices', []),
          "usage": getattr(completion_response, 'usage', {}),
          "model": getattr(completion_response, 'model', None)
        } if completion_response else None
      }
      
      # Write to detailed session log
      with open(session_log_file, 'a', encoding='utf-8') as f:
        f.write(f"{json.dumps(session_info, indent=2, default=str)}\n")
        f.write("=" * 80 + "\n")
      
    except Exception as e:
      # Use a basic logger if the main logger isn't available yet
      try:
        logger = _get_litellm_logger()
        logger.error(f"Failed to log session details: {e}")
      except:
        print(f"Failed to log session details: {e}")
  
  # Set the custom callback
  litellm.success_callback = [custom_callback]
  litellm.failure_callback = [custom_callback]
  
  # Enable LiteLLM verbose logging if debug mode is enabled
  debug_mode = os.getenv("DEEPEVAL_DEBUG", "").lower() in ("1", "true", "yes")
  if debug_mode:
    litellm.set_verbose = True
    os.environ["LITELLM_LOG"] = "INFO"
    print(f"🔍 LiteLLM debug logging enabled. Logs saved to: {litellm_log_file}")
    print(f"🔍 Detailed session logs saved to: {deepeval_dir / f'litellm_detailed_session_{timestamp}.log'}")
  
  return litellm_logger


# Initialize logging on module import
_litellm_logger = None


def _get_litellm_logger():
  """Get or initialize the LiteLLM logger lazily."""
  global _litellm_logger
  if _litellm_logger is None:
    _litellm_logger = _setup_litellm_logging()
  return _litellm_logger


def call_llm_for_evaluation(prompt: str, model: str) -> Dict:
  """Call LLM for evaluation with error handling.
  
  Args:
    prompt: Evaluation prompt
    model: Model name (e.g., "iflow/qwen3-coder-plus")
  
  Returns:
    Dictionary with score, reason, and criteria_scores
  """
  # Initialize logging only when LLM is actually used
  logger = _get_litellm_logger()
  
  # Log the evaluation request
  logger.info(f"Starting LLM evaluation with model: {model}")
  logger.info(f"Prompt length: {len(prompt)} characters")
  
  # Convert model name for iflow
  model_name = model
  if model_name.startswith("iflow/"):
    model_name = model_name.replace("iflow/", "dashscope/")
  
  # Build completion kwargs
  completion_kwargs = {
    "model": model_name,
    "messages": [{"role": "user", "content": prompt}],
    "response_format": {"type": "json_object"}
  }
  
  # Add iflow api_base if using iflow model
  if model.startswith("iflow/"):
    completion_kwargs["api_base"] = "https://apis.iflow.cn/v1/"
    completion_kwargs["api_key"] = os.getenv("IFLOW_API_KEY")
    if not completion_kwargs["api_key"]:
      raise ValueError(
        "IFLOW_API_KEY environment variable not set. "
        "Please set it with: export IFLOW_API_KEY='your-key'"
      )
  
  # Add GitHub Copilot headers if needed
  if model.startswith("github_copilot/"):
    completion_kwargs["extra_headers"] = {
      "Editor-Version": "vscode/1.85.0",
      "Copilot-Integration-Id": "vscode-chat"
    }
  
  # Log request details (without sensitive data)
  safe_kwargs = completion_kwargs.copy()
  if "api_key" in safe_kwargs:
    safe_kwargs["api_key"] = "***REDACTED***"
  logger.info(f"LLM request kwargs: {safe_kwargs}")
  
  try:
    response = litellm.completion(**completion_kwargs)
    content = response.choices[0].message.content
    
    # Log response details
    logger.info(f"LLM response received. Content length: {len(content) if content else 0}")
    logger.info(f"Response usage: {getattr(response, 'usage', 'N/A')}")
    
    if not content or content.strip() == "":
      raise ValueError("Empty response from LLM")
    
    # Extract JSON from response (handle cases where LLM adds extra text)
    try:
      data = json.loads(content)
    except json.JSONDecodeError:
      # Fallback: try to extract JSON from response
      json_content = _extract_json_from_response(content)
      data = json.loads(json_content)
    
    # Log parsed results
    result = {
      "score": data.get("score", data.get("overall_score", 0.0)),
      "reason": data.get("reason", "No reason provided"),
      "criteria_scores": data.get("criteria_scores", {})
    }
    
    logger.info(f"Evaluation completed. Score: {result['score']}")
    
    return result
    
  except json.JSONDecodeError as e:
    error_msg = f"Failed to parse JSON response: {e}"
    logger.error(error_msg)
    logger.error(f"Response content: {content[:200] if content else 'None'}")
    print(f"⚠️  Warning: {error_msg}")
    print(f"Response content: {content[:200] if content else 'None'}")
    # Return default values
    return {
      "score": 0.0,
      "reason": f"Failed to parse LLM response: {str(e)}",
      "criteria_scores": {}
    }
  except Exception as e:
    error_msg = f"LLM call failed: {e}"
    logger.error(error_msg)
    print(f"⚠️  Warning: {error_msg}")
    return {
      "score": 0.0,
      "reason": f"LLM call failed: {str(e)}",
      "criteria_scores": {}
    }
