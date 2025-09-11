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

"""iFlow LLM implementation using LiteLLM with API key authentication."""

from __future__ import annotations

import os
from typing_extensions import override

from .lite_llm import LiteLlm


class IFlowLlm(LiteLlm):
  """iFlow LLM implementation using LiteLLM with API key authentication.

  This class provides access to iFlow models through LiteLLM.
  Authentication is handled via API key from the IFLOW_API_KEY environment variable.

  Example usage:
  ```
  os.environ["IFLOW_API_KEY"] = "your-iflow-api-key"
  
  agent = Agent(
      model=IFlowLlm(model="iflow/Qwen3-Coder"),
      ...
  )
  ```

  Supported models:
  - iflow/Qwen3-Coder

  Attributes:
    model: The name of the iFlow model.
  """

  def __init__(self, model: str, **kwargs):
    """Initializes the IFlowLlm class.

    Args:
      model: The name of the iFlow model (e.g., "iflow/Qwen3-Coder").
      **kwargs: Additional arguments to pass to the litellm completion api.
    
    Raises:
      ValueError: If IFLOW_API_KEY environment variable is not set.
    """
    # Check for API key
    api_key = os.getenv("IFLOW_API_KEY")
    if not api_key:
      raise ValueError(
          "IFLOW_API_KEY environment variable must be set to use iFlow models"
      )
    
    # Ensure the model has the iflow/ prefix if not already present
    if not model.startswith("iflow/"):
      model = f"dashscope/{model}"
    else:
      model = model.replace("iflow/", "dashscope/")
    
    # Set up the base URL and API key for iFlow
    kwargs.setdefault("api_base", "https://apis.iflow.cn/v1/")
    kwargs.setdefault("api_key", api_key)
    
    super().__init__(model=model, **kwargs)

  @staticmethod
  @override
  def supported_models() -> list[str]:
    """Provides the list of supported iFlow models.

    Returns:
      A list of regex patterns matching supported iFlow models.
    """
    return [
      r"iflow/Qwen3-Coder.*",
      # Support models without iflow/ prefix for convenience
      r"Qwen3-Coder.*",
    ]