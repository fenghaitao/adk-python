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

"""Gemini CLI OAuth2 compatibility helpers.

This module intentionally does not implement any interactive OAuth flows.
Instead, it relies on Gemini CLI / Code Assist to perform authentication and
store credentials at ``~/.gemini/oauth_creds.json``. We:

- Read cached credentials from that file
- Refresh access tokens when possible using the stored refresh token
- Write credentials back to the same file using the same JSON format used by
  the Gemini CLI (do not introduce ADK-specific fields)

This ensures ADK does not break the Gemini CLI's expectations.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from ..utils.feature_decorator import experimental


# Constants align with Gemini CLI expectations and Google's OAuth endpoints.
_TOKEN_URI = "https://oauth2.googleapis.com/token"
# Public client for installed apps; used only for token refreshes. We do not
# write these values back to the credential file.
_DEFAULT_CLIENT_ID = (
    os.environ.get(
        "GEMINI_CLI_CLIENT_ID",
        "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com",
    )
)
_DEFAULT_CLIENT_SECRET = (
    os.environ.get("GEMINI_CLI_CLIENT_SECRET", "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")
)


def _cli_oauth_path() -> Path:
  """Returns the path to the Gemini CLI oauth credentials file.

  Preferred filename is ~/.gemini/oauth_creds.json (gemini-cli).
  For compatibility, if ~/.gemini/oauth.json exists, we read/write that file
  instead to avoid breaking existing setups.
  """
  base = Path.home() / ".gemini"
  preferred = base / "oauth_creds.json"
  legacy = base / "oauth.json"
  if preferred.exists():
    return preferred
  if legacy.exists():
    return legacy
  return preferred


def _read_cli_oauth_json() -> Optional[Dict[str, Any]]:
  """Reads the Gemini CLI oauth JSON if it exists.

  Returns:
    A dict of the JSON content, or None if the file does not exist or cannot
    be parsed.
  """
  p = _cli_oauth_path()
  if not p.exists():
    return None
  try:
    with p.open("r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return None


def _write_cli_oauth_json(data: Dict[str, Any]) -> None:
  """Writes credentials using the same JSON shape the Gemini CLI wrote.

  We do not filter fields; we preserve the JSON structure (including any
  additional properties) to avoid breaking the Gemini CLI or other tools that
  may have written extra fields.
  """
  p = _cli_oauth_path()
  try:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
      json.dump(data, f, indent=2)

    # Set restrictive permissions similar to CLI (0600).
    try:
      os.chmod(p, 0o600)
    except Exception:
      # Not critical on all platforms.
      pass
  except Exception:
    # Silent failure: don't crash the app due to IO issues.
    pass


def _to_credentials(cli_data: Dict[str, Any]) -> Credentials:
  """Converts the CLI JSON format into google.oauth2.credentials.Credentials.

  We use the default token endpoint and a public client id/secret so that
  refresh can work if a refresh_token is present. We do not write these values
  back to the CLI file.
  """
  token = cli_data.get("access_token") or cli_data.get("token")
  refresh_token = cli_data.get("refresh_token")

  # CLI stores scope as a single space-separated string; sometimes tests may
  # use "scopes" as a list. Support both defensively.
  scopes: Optional[list[str]] = None
  if isinstance(cli_data.get("scopes"), list):
    scopes = list(cli_data.get("scopes") or [])
  elif isinstance(cli_data.get("scope"), str):
    scopes = [s for s in cli_data.get("scope", "").split(" ") if s]

  creds = Credentials(
      token=token,
      refresh_token=refresh_token,
      token_uri=_TOKEN_URI,
      client_id=_DEFAULT_CLIENT_ID,
      client_secret=_DEFAULT_CLIENT_SECRET,
      scopes=scopes,
  )

  # Populate expiry if available (CLI stores epoch millis in 'expiry_date').
  try:
    expiry_ms = cli_data.get("expiry_date")
    if isinstance(expiry_ms, (int, float)):
      # Use naive UTC to avoid aware/naive comparison issues in google-auth
      creds.expiry = datetime.utcfromtimestamp(expiry_ms / 1000)
  except Exception:
    pass

  return creds


def _merge_cli_json_with_credentials(
    base: Dict[str, Any], creds: Credentials
) -> Dict[str, Any]:
  """Returns a CLI-style JSON with values updated from Credentials.

  We preserve unknown keys from the base file and only update known fields the
  CLI expects. The goal is to avoid removing any fields the CLI may depend on.
  """
  updated = dict(base) if base is not None else {}

  # access_token
  if getattr(creds, "token", None):
    updated["access_token"] = creds.token

  # refresh_token
  if getattr(creds, "refresh_token", None):
    updated["refresh_token"] = creds.refresh_token

  # scope (space-separated)
  if getattr(creds, "scopes", None):
    try:
      updated["scope"] = " ".join(creds.scopes or [])
    except Exception:
      pass

  # token_type (commonly 'Bearer'); preserve existing value if present.
  updated.setdefault("token_type", "Bearer")

  # expiry_date in epoch millis if we have an expiry.
  try:
    if getattr(creds, "expiry", None):
      dt = creds.expiry
      if isinstance(dt, datetime):
        # Treat naive datetimes as UTC; if tz-aware, convert to UTC
        if dt.tzinfo is not None:
          dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        updated["expiry_date"] = int(dt.timestamp() * 1000)
  except Exception:
    pass

  return updated


@experimental
class GeminiOAuthCredentialManager:
  """Minimal credential manager that relies on the Gemini CLI cache.

  Behavior:
  - Load from ~/.gemini/oauth_creds.json
  - If token is valid, return Credentials
  - If token needs refresh and a refresh_token is present, refresh and write
    back to ~/.gemini/oauth_creds.json using the same JSON format
  - Never trigger interactive auth; return None if credentials are missing
    or cannot be refreshed.
  """

  def __init__(self) -> None:
    self._cached: Optional[Credentials] = None

  async def get_credentials(self) -> Optional[Credentials]:
    # If we already have valid creds cached, use them.
    if self._cached and self._cached.valid:
      return self._cached

    cli_data = _read_cli_oauth_json()
    if not cli_data:
      return None

    creds = _to_credentials(cli_data)
    # If current token is valid, cache and return.
    if creds.valid:
      self._cached = creds
      return creds

    # Attempt refresh if we have a refresh token.
    if creds.refresh_token:
      try:
        creds.refresh(Request())
        if creds.valid:
          # Persist back in CLI format.
          merged = _merge_cli_json_with_credentials(cli_data, creds)
          _write_cli_oauth_json(merged)
          self._cached = creds
          return creds
      except Exception:
        # If refresh failed, keep returning None so caller can handle it.
        return None

    return None

  async def revoke_credentials(self) -> bool:
    """Removes the local CLI credential file and clears cache.

    We do not perform remote token revocation here; the Gemini CLI can handle
    full sign-out if needed. This merely deletes ~/.gemini/oauth_creds.json.
    """
    try:
      p = _cli_oauth_path()
      if p.exists():
        p.unlink()
      self._cached = None
      return True
    except Exception:
      return False
