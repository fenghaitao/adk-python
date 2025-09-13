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

"""Authentication types and enums for Gemini CLI compatibility."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class AuthType(Enum):
    """Authentication types supported by Gemini CLI."""
    
    LOGIN_WITH_GOOGLE = "oauth-personal"
    USE_GEMINI = "gemini-api-key"
    USE_VERTEX_AI = "vertex-ai"
    CLOUD_SHELL = "cloud-shell"


class GeminiAuthConfig:
    """Configuration for Gemini authentication."""
    
    def __init__(
        self,
        auth_type: AuthType,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        proxy: Optional[str] = None,
    ):
        self.auth_type = auth_type
        self.api_key = api_key
        self.project_id = project_id
        self.location = location
        self.proxy = proxy
        
    @property
    def is_vertex_ai(self) -> bool:
        """Check if this configuration uses Vertex AI."""
        return self.auth_type == AuthType.USE_VERTEX_AI
        
    @property
    def is_gemini_api(self) -> bool:
        """Check if this configuration uses Gemini API."""
        return self.auth_type == AuthType.USE_GEMINI
        
    @property
    def is_oauth(self) -> bool:
        """Check if this configuration uses OAuth."""
        return self.auth_type == AuthType.LOGIN_WITH_GOOGLE
        
    @property
    def is_cloud_shell(self) -> bool:
        """Check if this configuration uses Cloud Shell."""
        return self.auth_type == AuthType.CLOUD_SHELL