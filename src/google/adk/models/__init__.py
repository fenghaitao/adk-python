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

"""Defines the interface to support a model."""

from .base_llm import BaseLlm
from .gemini_cli_codeassist import GeminiCLICodeAssist
from .github_copilot_llm import GitHubCopilotLlm
from .google_llm import Gemini
from .iflow_llm import IFlowLlm
from .llm_request import LlmRequest
from .llm_response import LlmResponse
from .registry import LLMRegistry

__all__ = [
    'BaseLlm',
    'Gemini',
    'GeminiCLICodeAssist',
    'GitHubCopilotLlm',
    'IFlowLlm',
    'LLMRegistry',
]


for regex in Gemini.supported_models():
  LLMRegistry.register(Gemini)

# Register GitHub Copilot LLM
LLMRegistry.register(GitHubCopilotLlm)

# Register iFlow LLM
LLMRegistry.register(IFlowLlm)

# Register Gemini CLI Code Assist LLM
LLMRegistry.register(GeminiCLICodeAssist)
