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

"""Configuration utilities for DSPy OpenSpec."""

from __future__ import annotations

from dspy_openspec.config.lm_config import (
  configure_iflow_model,
  configure_openai_model,
  configure_github_copilot_model,
  configure_model_from_string,
  get_model_config,
  print_model_info,
)

__all__ = [
  "configure_iflow_model",
  "configure_openai_model",
  "configure_github_copilot_model",
  "configure_model_from_string",
  "get_model_config",
  "print_model_info",
]
