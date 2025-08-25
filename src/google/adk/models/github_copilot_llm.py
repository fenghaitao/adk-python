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

"""GitHub Copilot LLM implementation using LiteLLM direct mode."""

from __future__ import annotations

from typing_extensions import override

from .lite_llm import LiteLlm

class GitHubCopilotLlm(LiteLlm):
  """GitHub Copilot LLM implementation using LiteLLM direct mode.

  This class provides access to GitHub Copilot models through LiteLLM.
  Authentication is handled via OAuth2 through LiteLLM's GitHub integration.

  Example usage:
  ```
  agent = Agent(
      model=GitHubCopilotLlm(model="github_copilot/gpt-4o"),
      ...
  )
  ```

  Supported models:
  - github_copilot/gpt-4o
  - github_copilot/gpt-4o-mini
  - github_copilot/gpt-5
  - github_copilot/gpt-5-mini
  - github_copilot/o1-preview
  - github_copilot/o1-mini
  - github_copilot/claude-3-5-sonnet
  - github_copilot/claude-3-haiku
  - github_copilot/claude-sonnet-4

  Attributes:
    model: The name of the GitHub Copilot model.
  """

  def __init__(self, model: str, **kwargs):
    """Initializes the GitHubCopilotLlm class.

    Args:
      model: The name of the GitHub Copilot model (e.g., "github_copilot/gpt-4o").
      **kwargs: Additional arguments to pass to the litellm completion api.
    """
    # Ensure the model has the github_copilot/ prefix if not already present
    if not model.startswith("github_copilot/"):
      model = f"github_copilot/{model}"
    
    # Add GitHub Copilot specific headers
    extra_headers = kwargs.get("extra_headers", {})
    extra_headers.update({
      "Editor-Version": "vscode/1.85.0",
      "Copilot-Integration-Id": "vscode-chat"
    })
    kwargs["extra_headers"] = extra_headers
    
    super().__init__(model=model, **kwargs)

  @staticmethod
  @override
  def supported_models() -> list[str]:
    """Provides the list of supported GitHub Copilot models.

    Returns:
      A list of regex patterns matching supported GitHub Copilot models.
    """
    return [
      r"github_copilot/gpt-4o.*",
      r"github_copilot/gpt-4o-mini.*", 
      r"github_copilot/gpt-5.*",
      r"github_copilot/gpt-5-mini.*",
      r"github_copilot/o1-preview.*",
      r"github_copilot/o1-mini.*",
      r"github_copilot/claude-3-5-sonnet.*",
      r"github_copilot/claude-3-haiku.*",
      r"github_copilot/claude-sonnet-4.*",
      # Support models without github_copilot/ prefix for convenience
      r"gpt-4o.*",
      r"gpt-4o-mini.*",
      r"gpt-5.*",
      r"gpt-5-mini.*",
      r"o1-preview.*", 
      r"o1-mini.*",
      r"claude-3-5-sonnet.*",
      r"claude-3-haiku.*",
      r"claude-sonnet-4.*",
    ]