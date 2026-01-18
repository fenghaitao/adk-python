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

"""Language model configuration for DSPy OpenSpec.

Provides utilities for configuring different LM providers including iflow,
OpenAI, and GitHub Copilot.
"""

from __future__ import annotations

import os
from typing import Dict, Optional

import dspy


def configure_iflow_model(
    model_name: str = "qwen3-coder-plus",
    api_key: Optional[str] = None,
    cache: bool = False,  # Disable cache by default for debugging
    **kwargs
) -> dspy.LM:
  """Configure iflow model for DSPy.
  
  iflow uses the OpenAI-compatible API with custom base URL.
  Model names are prefixed with "dashscope/" for LiteLLM.
  
  Args:
    model_name: iflow model name (e.g., "qwen3-coder-plus")
    api_key: iflow API key (defaults to IFLOW_API_KEY env var)
    cache: Enable response caching (default: False for debugging)
    **kwargs: Additional arguments for dspy.LM
    
  Returns:
    Configured DSPy LM instance
    
  Raises:
    ValueError: If API key is not provided or found in environment
    
  Example:
    >>> lm = configure_iflow_model("qwen3-coder-plus")
    >>> dspy.settings.configure(lm=lm)
  """
  # Get API key from environment if not provided
  if api_key is None:
    api_key = os.getenv("IFLOW_API_KEY")
  
  if not api_key:
    raise ValueError(
      "iflow API key not found. Set IFLOW_API_KEY environment variable "
      "or pass api_key parameter."
    )
  
  # Convert model name to LiteLLM format
  # iflow/qwen3-coder-plus -> dashscope/qwen3-coder-plus
  litellm_model = f"dashscope/{model_name}"
  
  # Configure DSPy LM with iflow settings
  return dspy.LM(
    model=litellm_model,
    api_key=api_key,
    api_base="https://apis.iflow.cn/v1/",
    cache=cache,
    **kwargs
  )


def configure_openai_model(
    model_name: str = "gpt-4",
    api_key: Optional[str] = None,
    cache: bool = False,  # Disable cache by default for debugging
    **kwargs
) -> dspy.LM:
  """Configure OpenAI model for DSPy.
  
  Args:
    model_name: OpenAI model name (e.g., "gpt-4", "gpt-4-turbo")
    api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
    cache: Enable response caching (default: False for debugging)
    **kwargs: Additional arguments for dspy.LM
    
  Returns:
    Configured DSPy LM instance
    
  Raises:
    ValueError: If API key is not provided or found in environment
  """
  if api_key is None:
    api_key = os.getenv("OPENAI_API_KEY")
  
  if not api_key:
    raise ValueError(
      "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
      "or pass api_key parameter."
    )
  
  return dspy.LM(
    model=f"openai/{model_name}",
    api_key=api_key,
    cache=cache,
    **kwargs
  )


def configure_github_copilot_model(
    model_name: str = "gpt-5-mini",
    cache: bool = False,  # Disable cache by default for debugging
    **kwargs
) -> dspy.LM:
  """Configure GitHub Copilot model for DSPy.
  
  Args:
    model_name: Copilot model name (e.g., "gpt-5-mini")
    cache: Enable response caching (default: False for debugging)
    **kwargs: Additional arguments for dspy.LM
    
  Returns:
    Configured DSPy LM instance
  """
  # GitHub Copilot requires special headers
  # Pass extra_headers directly to dspy.LM
  extra_headers = kwargs.pop("extra_headers", {})
  extra_headers.update({
    "Editor-Version": "vscode/1.85.0",
    "Copilot-Integration-Id": "vscode-chat"
  })
  
  return dspy.LM(
    model=f"github_copilot/{model_name}",
    extra_headers=extra_headers,
    cache=cache,
    **kwargs
  )


def configure_model_from_string(
    model_string: str,
    **kwargs
) -> dspy.LM:
  """Configure model from a string identifier.
  
  Automatically detects provider from model string format:
  - "iflow/model-name" -> iflow
  - "openai/model-name" -> OpenAI
  - "github_copilot/model-name" -> GitHub Copilot
  - "model-name" -> Defaults to OpenAI
  
  Args:
    model_string: Model identifier string
    **kwargs: Additional arguments for dspy.LM
    
  Returns:
    Configured DSPy LM instance
    
  Example:
    >>> lm = configure_model_from_string("iflow/qwen3-coder-plus")
    >>> lm = configure_model_from_string("openai/gpt-4")
    >>> lm = configure_model_from_string("github_copilot/gpt-5-mini")
  """
  if model_string.startswith("iflow/"):
    model_name = model_string.replace("iflow/", "")
    return configure_iflow_model(model_name, **kwargs)
  
  elif model_string.startswith("openai/"):
    model_name = model_string.replace("openai/", "")
    return configure_openai_model(model_name, **kwargs)
  
  elif model_string.startswith("github_copilot/"):
    model_name = model_string.replace("github_copilot/", "")
    return configure_github_copilot_model(model_name, **kwargs)
  
  else:
    # Default to OpenAI
    return configure_openai_model(model_string, **kwargs)


def get_model_config() -> Dict[str, str]:
  """Get current model configuration from environment.
  
  Returns:
    Dictionary with model configuration:
      - default_model: Default model to use
      - iflow_api_key: iflow API key (if set)
      - openai_api_key: OpenAI API key (if set)
  """
  return {
    "default_model": os.getenv("OPENSPEC_MODEL", "iflow/qwen3-coder-plus"),
    "iflow_api_key": os.getenv("IFLOW_API_KEY", ""),
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
  }


def print_model_info(model_string: str):
  """Print information about model configuration.
  
  Args:
    model_string: Model identifier string
  """
  print(f"🤖 Model Configuration:")
  print(f"   Model: {model_string}")
  
  if model_string.startswith("iflow/"):
    api_key = os.getenv("IFLOW_API_KEY")
    print(f"   Provider: iflow")
    print(f"   Base URL: https://apis.iflow.cn/v1/")
    print(f"   API Key: {'✓ Set' if api_key else '✗ Not set (IFLOW_API_KEY)'}")
  
  elif model_string.startswith("openai/"):
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"   Provider: OpenAI")
    print(f"   API Key: {'✓ Set' if api_key else '✗ Not set (OPENAI_API_KEY)'}")
  
  elif model_string.startswith("github_copilot/"):
    print(f"   Provider: GitHub Copilot")
    print(f"   Headers: Editor-Version, Copilot-Integration-Id")
  
  else:
    print(f"   Provider: OpenAI (default)")
