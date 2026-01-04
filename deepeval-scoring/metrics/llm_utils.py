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
import os
from typing import Dict

import litellm


def call_llm_for_evaluation(prompt: str, model: str) -> Dict:
  """Call LLM for evaluation with error handling.
  
  Args:
    prompt: Evaluation prompt
    model: Model name (e.g., "iflow/qwen3-coder-plus")
  
  Returns:
    Dictionary with score, reason, and criteria_scores
  """
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
  
  try:
    response = litellm.completion(**completion_kwargs)
    content = response.choices[0].message.content
    
    if not content or content.strip() == "":
      raise ValueError("Empty response from LLM")
    
    data = json.loads(content)
    
    return {
      "score": data.get("overall_score", 0.0),
      "reason": data.get("reason", "No reason provided"),
      "criteria_scores": data.get("criteria_scores", {})
    }
  except json.JSONDecodeError as e:
    print(f"⚠️  Warning: Failed to parse JSON response: {e}")
    print(f"Response content: {content[:200] if content else 'None'}")
    # Return default values
    return {
      "score": 0.0,
      "reason": f"Failed to parse LLM response: {str(e)}",
      "criteria_scores": {}
    }
  except Exception as e:
    print(f"⚠️  Warning: LLM call failed: {e}")
    return {
      "score": 0.0,
      "reason": f"LLM call failed: {str(e)}",
      "criteria_scores": {}
    }
