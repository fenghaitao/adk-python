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

"""Tests for GitHub Copilot LLM implementation."""

import pytest

from google.adk.models.github_copilot_llm import GitHubCopilotLlm


class TestGitHubCopilotLlm:
  """Test cases for GitHubCopilotLlm."""

  def test_model_initialization_with_prefix(self):
    """Test that model initialization works with github_copilot/ prefix."""
    llm = GitHubCopilotLlm(model="github_copilot/gpt-4o")
    assert llm.model == "github_copilot/gpt-4o"

  def test_model_initialization_without_prefix(self):
    """Test that model initialization adds github_copilot/ prefix when missing."""
    llm = GitHubCopilotLlm(model="gpt-4o")
    assert llm.model == "github_copilot/gpt-4o"

  def test_model_initialization_with_additional_args(self):
    """Test that additional arguments are passed through correctly."""
    llm = GitHubCopilotLlm(model="gpt-4o", temperature=0.7, max_tokens=100)
    assert llm.model == "github_copilot/gpt-4o"
    assert llm._additional_args["temperature"] == 0.7
    assert llm._additional_args["max_tokens"] == 100

  def test_supported_models(self):
    """Test that supported_models returns expected patterns."""
    supported = GitHubCopilotLlm.supported_models()
    
    # Check that we have the expected number of patterns
    assert len(supported) == 18  # 9 with github_copilot/ prefix + 9 without
    
    # Check for specific patterns with github_copilot/ prefix
    assert r"github_copilot/gpt-4o.*" in supported
    assert r"github_copilot/gpt-4o-mini.*" in supported
    assert r"github_copilot/gpt-5.*" in supported
    assert r"github_copilot/gpt-5-mini.*" in supported
    assert r"github_copilot/o1-preview.*" in supported
    assert r"github_copilot/o1-mini.*" in supported
    assert r"github_copilot/claude-3-5-sonnet.*" in supported
    assert r"github_copilot/claude-3-haiku.*" in supported
    assert r"github_copilot/claude-sonnet-4.*" in supported
    
    # Check patterns without prefix
    assert r"gpt-4o.*" in supported
    assert r"gpt-4o-mini.*" in supported
    assert r"gpt-5.*" in supported
    assert r"gpt-5-mini.*" in supported
    assert r"o1-preview.*" in supported
    assert r"o1-mini.*" in supported
    assert r"claude-3-5-sonnet.*" in supported
    assert r"claude-3-haiku.*" in supported
    assert r"claude-sonnet-4.*" in supported

  def test_inheritance_from_litellm(self):
    """Test that GitHubCopilotLlm properly inherits from LiteLlm."""
    from google.adk.models.lite_llm import LiteLlm
    
    llm = GitHubCopilotLlm(model="gpt-4o")
    assert isinstance(llm, LiteLlm)

  @pytest.mark.parametrize("model_name,expected", [
    ("gpt-4o", "github_copilot/gpt-4o"),
    ("github_copilot/gpt-4o", "github_copilot/gpt-4o"),
    ("gpt-4o-mini", "github_copilot/gpt-4o-mini"),
    ("github_copilot/gpt-4o-mini", "github_copilot/gpt-4o-mini"),
    ("gpt-5", "github_copilot/gpt-5"),
    ("github_copilot/gpt-5", "github_copilot/gpt-5"),
    ("gpt-5-mini", "github_copilot/gpt-5-mini"),
    ("github_copilot/gpt-5-mini", "github_copilot/gpt-5-mini"),
    ("o1-preview", "github_copilot/o1-preview"),
    ("github_copilot/o1-preview", "github_copilot/o1-preview"),
    ("claude-3-5-sonnet", "github_copilot/claude-3-5-sonnet"),
    ("github_copilot/claude-3-5-sonnet", "github_copilot/claude-3-5-sonnet"),
    ("claude-sonnet-4", "github_copilot/claude-sonnet-4"),
    ("github_copilot/claude-sonnet-4", "github_copilot/claude-sonnet-4"),
  ])
  def test_model_name_normalization(self, model_name, expected):
    """Test that model names are normalized correctly."""
    llm = GitHubCopilotLlm(model=model_name)
    assert llm.model == expected