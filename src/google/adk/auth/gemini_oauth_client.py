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

"""Gemini CLI OAuth2 integration using ADK's authentication infrastructure."""

from __future__ import annotations

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from google.oauth2.credentials import Credentials

from ..utils.feature_decorator import experimental
from .auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth
from .auth_schemes import OpenIdConnectWithConfig
from .auth_tool import AuthConfig
from .credential_manager import CredentialManager


@experimental
class GeminiOAuthHelper:
    """Helper for Gemini CLI OAuth2 authentication using Google's device code flow."""
    
    # OAuth configuration compatible with Gemini CLI
    # These are the same public OAuth client credentials used by the official Gemini CLI.
    # These are public client credentials (not confidential) designed for desktop/CLI applications.
    # Similar to how mobile apps handle OAuth, these credentials are embedded in the client.
    # For production use, set GEMINI_CLI_CLIENT_ID and GEMINI_CLI_CLIENT_SECRET environment variables.
    DEFAULT_CLIENT_ID = os.environ.get(
        "GEMINI_CLI_CLIENT_ID", 
        "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com"
    )
    DEFAULT_CLIENT_SECRET = os.environ.get(
        "GEMINI_CLI_CLIENT_SECRET",
        "d-FL95Q19q7MQmFpd7hHD0Ty"
    )
    SCOPES = [
        "https://www.googleapis.com/auth/cloud-platform",
        "openid",
        "email", 
        "profile"
    ]
    
    @staticmethod
    def create_auth_config(
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ) -> AuthConfig:
        """Create ADK-compatible auth config for Gemini CLI OAuth."""
        return AuthConfig(
            auth_scheme=OpenIdConnectWithConfig(
                authorization_endpoint="https://accounts.google.com/o/oauth2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
                scopes=scopes or GeminiOAuthHelper.SCOPES
            ),
            raw_auth_credential=AuthCredential(
                auth_type=AuthCredentialTypes.OAUTH2,
                oauth2=OAuth2Auth(
                    client_id=client_id or GeminiOAuthHelper.DEFAULT_CLIENT_ID,
                    client_secret=client_secret or GeminiOAuthHelper.DEFAULT_CLIENT_SECRET,
                )
            )
        )
    
    @staticmethod
    async def authenticate_with_device_code(
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scopes: Optional[list[str]] = None,
        proxy: Optional[str] = None,
    ) -> Optional[Credentials]:
        """Perform device code OAuth2 flow - no browser/port needed."""
        actual_client_id = client_id or GeminiOAuthHelper.DEFAULT_CLIENT_ID
        actual_client_secret = client_secret or GeminiOAuthHelper.DEFAULT_CLIENT_SECRET
        actual_scopes = scopes or GeminiOAuthHelper.SCOPES
        actual_proxy = proxy or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        
        try:
            # Request device code
            device_code_data = {
                "client_id": actual_client_id,
                "scope": " ".join(actual_scopes)
            }
            
            # httpx AsyncClient doesn't take proxies in constructor, pass to requests
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/device/code",
                    data=device_code_data
                )
                response.raise_for_status()
                device_data = response.json()
            
            # Display user code
            print("\n🔐 Gemini CLI Authentication")
            print("=" * 35)
            print(f"\n📱 Please visit: {device_data['verification_url']}")
            print(f"🔑 Enter this code: {device_data['user_code']}")
            print("\n⏳ Waiting for authentication...")
            
            # Poll for authorization
            token_data = {
                "client_id": actual_client_id,
                "client_secret": actual_client_secret,
                "device_code": device_data["device_code"],
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
            }
            
            interval = device_data.get("interval", 5)
            expires_in = device_data.get("expires_in", 1800)
            start_time = time.time()
            
            async with httpx.AsyncClient() as client:
                while time.time() - start_time < expires_in:
                    response = await client.post(
                        "https://oauth2.googleapis.com/token",
                        data=token_data
                    )
                    
                    if response.status_code == 200:
                        token_info = response.json()
                        
                        # Create credentials
                        credentials = Credentials(
                            token=token_info["access_token"],
                            refresh_token=token_info.get("refresh_token"),
                            token_uri="https://oauth2.googleapis.com/token",
                            client_id=actual_client_id,
                            client_secret=actual_client_secret,
                            scopes=actual_scopes
                        )
                        
                        print("✅ Authentication successful!")
                        return credentials
                    
                    elif response.status_code == 400:
                        error_data = response.json()
                        error = error_data.get("error")
                        
                        if error == "authorization_pending":
                            await asyncio.sleep(interval)
                            continue
                        elif error == "slow_down":
                            interval += 5
                            await asyncio.sleep(interval)
                            continue
                        elif error == "expired_token":
                            print("❌ Authentication timeout. Please try again.")
                            return None
                        elif error == "access_denied":
                            print("❌ Authentication was denied.")
                            return None
                        else:
                            print(f"❌ Authentication error: {error}")
                            return None
                    else:
                        print(f"❌ Unexpected response: {response.status_code}")
                        return None
                        
                print("❌ Authentication timeout. Please try again.")
                return None
                
        except Exception as e:
            print(f"❌ Device code flow failed: {e}")
            return None
    
    @staticmethod
    def get_cache_file() -> Path:
        """Get the credential cache file path (same as Gemini CLI)."""
        gemini_dir = Path.home() / ".gemini"
        gemini_dir.mkdir(exist_ok=True)
        return gemini_dir / "oauth_creds.json"
    
    @staticmethod
    def load_cached_credentials() -> Optional[Credentials]:
        """Load credentials from Gemini CLI cache file."""
        cache_file = GeminiOAuthHelper.get_cache_file()
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r') as f:
                cred_data = json.load(f)
                
            return Credentials(
                token=cred_data.get("token"),
                refresh_token=cred_data.get("refresh_token"),
                token_uri=cred_data.get("token_uri"),
                client_id=cred_data.get("client_id"),
                client_secret=cred_data.get("client_secret"),
                scopes=cred_data.get("scopes")
            )
        except Exception:
            return None
    
    @staticmethod
    def save_credentials(credentials: Credentials) -> None:
        """Save credentials to Gemini CLI cache file."""
        if not credentials:
            return
            
        cred_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
        
        try:
            cache_file = GeminiOAuthHelper.get_cache_file()
            cache_file.parent.mkdir(exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump(cred_data, f, indent=2)
        except Exception:
            pass


@experimental  
class GeminiOAuthCredentialManager:
    """Credential manager for Gemini CLI OAuth using ADK infrastructure."""
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ):
        self._auth_config = GeminiOAuthHelper.create_auth_config(
            client_id, client_secret, scopes
        )
        self._credential_manager = CredentialManager(self._auth_config)
        self._cached_credentials: Optional[Credentials] = None
    
    async def get_credentials(self) -> Optional[Credentials]:
        """Get valid OAuth2 credentials, using ADK's credential management."""
        # Check if we have valid cached credentials
        if self._cached_credentials and self._cached_credentials.valid:
            return self._cached_credentials
        
        # Try to load from Gemini CLI cache first
        self._cached_credentials = GeminiOAuthHelper.load_cached_credentials()
        if self._cached_credentials and self._cached_credentials.valid:
            return self._cached_credentials
            
        # Try to refresh if we have refresh token
        if self._cached_credentials and self._cached_credentials.refresh_token:
            try:
                from google.auth.transport.requests import Request
                self._cached_credentials.refresh(Request())
                if self._cached_credentials.valid:
                    GeminiOAuthHelper.save_credentials(self._cached_credentials)
                    return self._cached_credentials
            except Exception:
                # Refresh failed, need to re-authenticate
                pass
        
        # Need to authenticate using device code flow
        print("🔐 OAuth authentication required for Gemini CLI")
        self._cached_credentials = await GeminiOAuthHelper.authenticate_with_device_code(
            self._auth_config.raw_auth_credential.oauth2.client_id,
            self._auth_config.raw_auth_credential.oauth2.client_secret,
            self._auth_config.auth_scheme.scopes,
        )
        
        if self._cached_credentials:
            GeminiOAuthHelper.save_credentials(self._cached_credentials)
            return self._cached_credentials
            
        return None
    
    async def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get user information from OAuth2 userinfo endpoint."""
        credentials = await self.get_credentials()
        if not credentials or not credentials.valid:
            return None
            
        try:
            proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {credentials.token}"}
                )
                response.raise_for_status()
                return response.json()
                
        except Exception:
            return None
    
    async def revoke_credentials(self) -> bool:
        """Revoke the current credentials."""
        credentials = await self.get_credentials()
        if not credentials:
            return False
            
        try:
            proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/revoke",
                    data={"token": credentials.token}
                )
                response.raise_for_status()
                
            # Clear cache
            cache_file = GeminiOAuthHelper.get_cache_file()
            if cache_file.exists():
                cache_file.unlink()
                
            self._cached_credentials = None
            return True
            
        except Exception:
            return False


# For backward compatibility
GeminiOAuthClient = GeminiOAuthCredentialManager