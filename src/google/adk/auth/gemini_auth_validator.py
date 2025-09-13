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

"""Authentication validation for Gemini CLI compatibility."""

from __future__ import annotations

import os
from typing import Optional

from .gemini_auth_types import AuthType


class GeminiAuthValidator:
    """Validates authentication methods for Gemini CLI compatibility."""
    
    @staticmethod
    def validate_auth_method(auth_method: AuthType) -> Optional[str]:
        """Validate an authentication method.
        
        Args:
            auth_method: The authentication method to validate.
            
        Returns:
            None if valid, error message string if invalid.
        """
        if auth_method in (AuthType.LOGIN_WITH_GOOGLE, AuthType.CLOUD_SHELL):
            return None
            
        if auth_method == AuthType.USE_GEMINI:
            if not os.environ.get("GEMINI_API_KEY"):
                return (
                    "GEMINI_API_KEY environment variable not found. "
                    "Add that to your environment and try again "
                    "(no reload needed if using .env)!"
                )
            return None
            
        if auth_method == AuthType.USE_VERTEX_AI:
            has_vertex_config = (
                bool(os.environ.get("GOOGLE_CLOUD_PROJECT")) and
                bool(os.environ.get("GOOGLE_CLOUD_LOCATION"))
            )
            has_google_api_key = bool(os.environ.get("GOOGLE_API_KEY"))
            
            if not has_vertex_config and not has_google_api_key:
                return (
                    "When using Vertex AI, you must specify either:\n"
                    "• GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION environment variables.\n"
                    "• GOOGLE_API_KEY environment variable (if using express mode).\n"
                    "Update your environment and try again (no reload needed if using .env)!"
                )
            return None
            
        return "Invalid auth method selected."
    
    @staticmethod
    def create_auth_config_from_env(auth_type: AuthType) -> dict:
        """Create authentication configuration from environment variables.
        
        Args:
            auth_type: The authentication type to configure.
            
        Returns:
            Dictionary containing authentication configuration.
        """
        config = {
            "auth_type": auth_type,
            "proxy": os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY"),
        }
        
        if auth_type == AuthType.USE_GEMINI:
            config["api_key"] = os.environ.get("GEMINI_API_KEY")
            
        elif auth_type == AuthType.USE_VERTEX_AI:
            config["api_key"] = os.environ.get("GOOGLE_API_KEY")
            config["project_id"] = os.environ.get("GOOGLE_CLOUD_PROJECT")
            config["location"] = os.environ.get("GOOGLE_CLOUD_LOCATION")
            
        return config
    
    @staticmethod
    def get_default_auth_type() -> AuthType:
        """Get the default authentication type based on environment.
        
        Returns:
            The most appropriate authentication type for the current environment.
        """
        # Check for Cloud Shell environment
        if os.environ.get("GOOGLE_CLOUD_SHELL"):
            return AuthType.CLOUD_SHELL
            
        # Check for Gemini API key
        if os.environ.get("GEMINI_API_KEY"):
            return AuthType.USE_GEMINI
            
        # Check for Vertex AI configuration
        if (os.environ.get("GOOGLE_CLOUD_PROJECT") and 
            os.environ.get("GOOGLE_CLOUD_LOCATION")):
            return AuthType.USE_VERTEX_AI
            
        # Check for Google API key (Vertex express mode)
        if os.environ.get("GOOGLE_API_KEY"):
            return AuthType.USE_VERTEX_AI
            
        # Default to OAuth
        return AuthType.LOGIN_WITH_GOOGLE