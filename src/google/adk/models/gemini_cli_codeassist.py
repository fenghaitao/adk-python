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
"""Gemini CLI CodeAssist-backed LLM provider.

This provider mirrors the Gemini CLI OAuth path by calling the Code Assist
service (cloudcode-pa.googleapis.com) with Google OAuth credentials, and it
handles managed project selection for free tier when possible.

Use this when LOGIN_WITH_GOOGLE OAuth is desired but Vertex AI ADC/project
isn't configured. If GOOGLE_CLOUD_PROJECT is set, that project will be used.
Otherwise it will attempt to determine or create a managed project via the
Code Assist API.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from typing import AsyncGenerator, Optional

import httpx
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials as GoogleCredentials
from google.genai import types
from typing_extensions import override

from .base_llm import BaseLlm
from .llm_request import LlmRequest
from .llm_response import LlmResponse
from ..auth.gemini_oauth_client import GeminiOAuthCredentialManager


CODE_ASSIST_ENDPOINT = "https://cloudcode-pa.googleapis.com"
CODE_ASSIST_API_VERSION = "v1internal"
FREE_TIER_ID = "free-tier"

# Timeout constants
DEFAULT_REQUEST_TIMEOUT = 60  # seconds
PROJECT_SETUP_TIMEOUT = 30  # seconds
LRO_POLL_TIMEOUT = 120  # seconds
LRO_POLL_INTERVAL = 5  # seconds

# HTTP status codes
HTTP_UNAUTHORIZED = 401

async def _handle_streaming_response(
      response: httpx.Response
  ) -> AsyncGenerator[LlmResponse, None]:
    """Handle streaming response from Code Assist API.
    
    Args:
      response: The streaming HTTP response from Code Assist API.
      
    Yields:
      LlmResponse objects for each streaming chunk.
    """
    accumulated_text = ""
    accumulated_parts = []
    usage_metadata = None
    
    async for line in response.aiter_lines():
      if not line.strip():
        continue
        
      # Handle Server-Sent Events (SSE) format
      if line.startswith("data: "):
        data = line[6:]  # Remove "data: " prefix
        if data == "[DONE]":
          break
          
        try:
          chunk_data = json.loads(data)
          # Process the chunk data
          if "response" in chunk_data:
            response_data = chunk_data["response"]
            
            # Handle candidates in the response
            if "candidates" in response_data:
              for candidate in response_data["candidates"]:
                if "content" in candidate and "parts" in candidate["content"]:
                  for part in candidate["content"]["parts"]:
                    if "text" in part:
                      text_chunk = part["text"]
                      accumulated_text += text_chunk
                      
                      # Create a partial response for this chunk
                      partial_content = types.Content(
                          role="model",
                          parts=[types.Part(text=text_chunk)]
                      )
                      partial_response = types.GenerateContentResponse(
                          candidates=[types.Candidate(content=partial_content)]
                      )
                      llm_response = LlmResponse.create(partial_response)
                      llm_response.partial = True
                      yield llm_response
            
            # Handle usage metadata
            if "usageMetadata" in response_data:
              usage_metadata = response_data["usageMetadata"]
              
        except json.JSONDecodeError:
          # Skip malformed JSON chunks
          continue
    
    # Yield final complete response
    if accumulated_text:
      final_content = types.Content(
          role="model",
          parts=[types.Part(text=accumulated_text)]
      )
      final_response = types.GenerateContentResponse(
          candidates=[types.Candidate(content=final_content)],
          usage_metadata=usage_metadata
      )
      llm_response = LlmResponse.create(final_response)
      llm_response.partial = False
      yield llm_response

async def _parse_sse_stream(response: httpx.Response) -> AsyncGenerator[dict, None]:
  """Parse Server-Sent Events stream from Code Assist API."""
  buffered_lines = []
  async for line in response.aiter_lines():
    # Blank lines separate JSON objects in the stream
    if line == '':
      if buffered_lines:
        try:
          # Join buffered lines and parse as JSON
          json_str = '\n'.join(buffered_lines)
          data = json.loads(json_str)
          # Extract the actual response from Code Assist wrapper
          if 'response' in data:
            yield data['response']
        except json.JSONDecodeError:
          # Skip malformed JSON
          pass
        buffered_lines = []
    elif line.startswith('data: '):
      # Extract the data part and add to buffer
      data_content = line[6:].strip()
      if data_content:
        buffered_lines.append(data_content)

def _method_url(method: str) -> str:
  endpoint = os.getenv("CODE_ASSIST_ENDPOINT", CODE_ASSIST_ENDPOINT)
  return f"{endpoint}/{CODE_ASSIST_API_VERSION}:{method}"


def _build_headers(extra: Optional[dict[str, str]] = None) -> dict[str, str]:
  headers = {
      "Content-Type": "application/json",
      # Mirror Gemini CLI UA style lightly for compatibility
      "User-Agent": f"ADK-GeminiCodeAssist/{os.getenv('ADK_VERSION','0')}",
  }
  if extra:
    headers.update(extra)
  return headers


def _build_generation_config(cfg: types.GenerateContentConfig) -> dict:
  # Map a subset used by Code Assist; include keys only if set
  out: dict = {}
  # Simple scalar fields
  for key in (
      "temperature", "topP", "topK", "candidateCount", "maxOutputTokens",
      "responseLogprobs", "logprobs", "presencePenalty", "frequencyPenalty",
      "seed", "responseMimeType", "audioTimestamp",
  ):
    val = getattr(cfg, key, None)
    if val is not None:
      out[key] = val

  # Array / object fields
  if getattr(cfg, "stopSequences", None):
    out["stopSequences"] = list(cfg.stopSequences)
  if getattr(cfg, "responseModalities", None):
    out["responseModalities"] = list(cfg.responseModalities)
  if getattr(cfg, "responseSchema", None):
    out["responseSchema"] = cfg.responseSchema
  if getattr(cfg, "responseJsonSchema", None):
    out["responseJsonSchema"] = cfg.responseJsonSchema
  if getattr(cfg, "routingConfig", None):
    out["routingConfig"] = cfg.routingConfig
  if getattr(cfg, "modelSelectionConfig", None):
    out["modelSelectionConfig"] = cfg.modelSelectionConfig
  if getattr(cfg, "mediaResolution", None):
    out["mediaResolution"] = cfg.mediaResolution
  if getattr(cfg, "speechConfig", None):
    out["speechConfig"] = cfg.speechConfig
  if getattr(cfg, "thinkingConfig", None):
    out["thinkingConfig"] = cfg.thinkingConfig
  return out


def _to_jsonish(obj):
  """Recursively convert pydantic/genai objects to plain JSON-serializable types."""
  # Primitives
  if obj is None or isinstance(obj, (str, int, float, bool)):
    return obj
  # Handle bytes by converting to base64 string
  if isinstance(obj, bytes):
    import base64
    return base64.b64encode(obj).decode('utf-8')
  
  # Handle common problematic types that may contain bytes
  try:
    import json
    json.dumps(obj)
    return obj  # If it's already JSON serializable, return as-is
  except TypeError:
    pass  # Continue with conversion logic
  
  # Pydantic-like objects
  for attr in ("model_dump", "dict"):
    if hasattr(obj, attr):
      try:
        dumped = getattr(obj, attr)(by_alias=True, exclude_none=True) if attr == "model_dump" else getattr(obj, attr)()
        return _to_jsonish(dumped)
      except Exception:
        pass
  
  # Mappings
  if isinstance(obj, dict):
    return {k: _to_jsonish(v) for k, v in obj.items()}
  
  # Iterables
  if isinstance(obj, (list, tuple, set)):
    return [ _to_jsonish(v) for v in obj ]
  
  # Parts that expose text
  if hasattr(obj, "text"):
    return {"text": getattr(obj, "text")}
  
  # Enums
  if hasattr(obj, "value"):
    return obj.value
  
  # Handle dataclasses
  if hasattr(obj, "__dataclass_fields__"):
    import dataclasses
    try:
      return _to_jsonish(dataclasses.asdict(obj))
    except Exception:
      pass
  
  # Try __dict__ as fallback for complex objects
  if hasattr(obj, "__dict__"):
    try:
      result = {}
      for key, value in obj.__dict__.items():
        try:
          result[key] = _to_jsonish(value)
        except Exception:
          # Skip problematic attributes
          result[key] = str(value)
      return result
    except Exception:
      pass
  
  # Last resort: convert to string
  return str(obj)


def _content_to_json(c) -> dict:
  """Accepts ContentUnion (Content | PartsUnion | str) and returns JSON dict."""
  # String content -> user text part
  if isinstance(c, str):
    return {"role": "user", "parts": [{"text": c}]}
  # If already a dict-like content
  if isinstance(c, dict):
    return c
  # Try pydantic dump first
  try:
    return c.model_dump(by_alias=True, exclude_none=True)
  except Exception:
    # Fallback – construct minimal structure if it looks like a Content
    role = getattr(c, "role", "user")
    parts_list = []
    parts = getattr(c, "parts", None)
    if parts:
      for p in parts:
        try:
          parts_list.append(p.model_dump(by_alias=True, exclude_none=True))
        except Exception:
          parts_list.append(_to_jsonish(p))
    return {"role": role, "parts": parts_list}


class GeminiCLICodeAssist(BaseLlm):
  """LLM provider that talks to Code Assist using OAuth tokens.

  This class does not require API keys. It will use Google OAuth credentials
  from the local Gemini CLI cache (via GeminiOAuthCredentialManager).
  """

  def __init__(self, model: str, **kwargs):
    """Initializes the GeminiCLICodeAssist class.

    Args:
      model: The name of the model (e.g., "gemini_cli/gemini-2.0-flash" or "gemini-2.0-flash").
      **kwargs: Additional arguments to pass to the base class.
    """
    # Strip the gemini_cli/ prefix if present to get the actual model name
    if model.startswith("gemini_cli/"):
      model = model.replace("gemini_cli/", "")
    
    super().__init__(model=model, **kwargs)

  @classmethod
  @override
  def supported_models(cls) -> list[str]:
    """Provides the list of supported models for Code Assist API.

    Returns:
      A list of supported model patterns that the Code Assist API can handle.
      Based on the models typically supported by Gemini CLI and Code Assist.
    """
    return [
        # Gemini CLI specific prefix (similar to github_copilot/ and iflow/)
        r'gemini_cli/gemini-1\.5-flash.*',
        r'gemini_cli/gemini-1\.5-pro.*',
        r'gemini_cli/gemini-2\.0-flash.*',
        r'gemini_cli/gemini-2\.5-flash.*',
        r'gemini_cli/gemini-2\.5-pro.*',
        r'gemini_cli/gemini-embedding-001',
        r'gemini_cli/text-embedding-.*',
        # Support models without gemini_cli/ prefix for convenience (like iflow)
        r'gemini-1\.5-flash.*',
        r'gemini-1\.5-pro.*',
        r'gemini-2\.0-flash.*',
        r'gemini-2\.5-flash.*',
        r'gemini-2\.5-pro.*',
        r'gemini-embedding-001',
        r'text-embedding-.*',
    ]

  @override
  async def generate_content_async(
      self, llm_request: LlmRequest, stream: bool = False
  ) -> AsyncGenerator[LlmResponse, None]:
    # Obtain OAuth credentials
    oauth_mgr = GeminiOAuthCredentialManager()
    credentials = await oauth_mgr.get_credentials()
    if not credentials:
      raise RuntimeError("Failed to obtain OAuth credentials for Code Assist.")

    # Ensure token is fresh
    if isinstance(credentials, GoogleCredentials) and credentials.expired:
      credentials.refresh(GoogleAuthRequest())

    # Determine project: env var first; otherwise try loadCodeAssist onboarding
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    try:
      if not project:
        project = await self._get_or_setup_project(credentials)
    except Exception:
      # If unable to auto-setup, leave as None – Code Assist can still accept
      # requests for free tier users after onboarding attempt.
      pass

    # Prepare request payload following gemini-cli converter.ts
    model = llm_request.model or self.model

    # Build vertex-like request from our config/contents
    request_obj: dict = {
        "contents": [
            _content_to_json(c) for c in (llm_request.contents or [])
        ],
        "generationConfig": _build_generation_config(llm_request.config),
    }
    if llm_request.config and getattr(llm_request.config, "system_instruction", None):
      request_obj["systemInstruction"] = _content_to_json(
          llm_request.config.system_instruction)
    if getattr(llm_request.config, "safety_settings", None):
      request_obj["safetySettings"] = llm_request.config.safety_settings
    if getattr(llm_request.config, "tools", None):
      request_obj["tools"] = llm_request.config.tools
    if getattr(llm_request.config, "tool_config", None):
      request_obj["toolConfig"] = llm_request.config.tool_config

    ca_payload = _to_jsonish({
        "model": model,
        "project": project,
        "request": request_obj,
    })

    headers = _build_headers()
    headers["Authorization"] = f"Bearer {credentials.token}"

    # Execute request
    if stream:
      # Use streaming endpoint
      url = _method_url("streamGenerateContent")
      async with httpx.AsyncClient(timeout=DEFAULT_REQUEST_TIMEOUT) as client:
        async with client.stream(
            "POST", 
            url, 
            headers=headers, 
            json=ca_payload,
            params={"alt": "sse"}
        ) as resp:
          if resp.status_code == HTTP_UNAUTHORIZED and isinstance(credentials, GoogleCredentials):
            # Try a single refresh and retry the stream
            credentials.refresh(GoogleAuthRequest())
            headers["Authorization"] = f"Bearer {credentials.token}"
            async with client.stream(
                "POST", 
                url, 
                headers=headers, 
                json=ca_payload,
                params={"alt": "sse"}
            ) as retry_resp:
              retry_resp.raise_for_status()
              if True:
                # Use _handle_streaming_response for proper streaming behavior
                async for llm_response in _handle_streaming_response(retry_resp):
                  yield llm_response
              else:
                # Use _parse_sse_stream for raw dictionary parsing
                async for chunk_data in _parse_sse_stream(retry_resp):
                  gen_resp = types.GenerateContentResponse(**chunk_data)
                  yield LlmResponse.create(gen_resp)
          else:
            resp.raise_for_status()
            if True:
              # Use _handle_streaming_response for proper streaming behavior
              async for llm_response in _handle_streaming_response(resp):
                yield llm_response
            else:
              # Use _parse_sse_stream for raw dictionary parsing
              async for chunk_data in _parse_sse_stream(resp):
                gen_resp = types.GenerateContentResponse(**chunk_data)
                yield LlmResponse.create(gen_resp)
    else:
      # Use non-streaming endpoint
      url = _method_url("generateContent")
      async with httpx.AsyncClient(timeout=DEFAULT_REQUEST_TIMEOUT) as client:
        resp = await client.post(url, headers=headers, json=ca_payload)
        if resp.status_code == HTTP_UNAUTHORIZED and isinstance(credentials, GoogleCredentials):
          # Try a single refresh
          credentials.refresh(GoogleAuthRequest())
          headers["Authorization"] = f"Bearer {credentials.token}"
          resp = await client.post(url, headers=headers, json=ca_payload)
        resp.raise_for_status()
        data = resp.json()

      # Convert Code Assist response to google.genai GenerateContentResponse
      inres = (data or {}).get("response") or {}
      gen_resp = types.GenerateContentResponse(**inres)
      yield LlmResponse.create(gen_resp)

  async def _get_or_setup_project(self, credentials: GoogleCredentials) -> Optional[str]:
    """Try to fetch or create a managed project via Code Assist APIs.

    Mirrors gemini-cli setup.ts logic at a high level.
    Returns a project id if available; otherwise None.
    """
    headers = _build_headers()
    headers["Authorization"] = f"Bearer {credentials.token}"

    async with httpx.AsyncClient(timeout=PROJECT_SETUP_TIMEOUT) as client:
      # loadCodeAssist
      url = _method_url("loadCodeAssist")
      payload = {
          "cloudaicompanionProject": None,
          "metadata": {
              "ideType": "IDE_UNSPECIFIED",
              "platform": "PLATFORM_UNSPECIFIED",
              "pluginType": "GEMINI",
          },
      }
      resp = await client.post(url, headers=headers, json=payload)
      if resp.status_code == HTTP_UNAUTHORIZED:
        credentials.refresh(GoogleAuthRequest())
        headers["Authorization"] = f"Bearer {credentials.token}"
        resp = await client.post(url, headers=headers, json=payload)
      resp.raise_for_status()
      data = resp.json() or {}

      project = data.get("cloudaicompanionProject")
      if data.get("currentTier"):
        # current tier already set
        if project:
          return project
        # If no project in response, cannot infer – require env
        return None

      # No current tier – try onboarding
      tier_list = (data.get("allowedTiers") or [])
      tier_id = None
      for t in tier_list:
        if t.get("isDefault"):
          tier_id = t.get("id")
          break
      tier_id = tier_id or FREE_TIER_ID

      onboard_payload = {
          "tierId": tier_id,
          "cloudaicompanionProject": None if tier_id == FREE_TIER_ID else os.getenv("GOOGLE_CLOUD_PROJECT"),
          "metadata": {
              "ideType": "IDE_UNSPECIFIED",
              "platform": "PLATFORM_UNSPECIFIED",
              "pluginType": "GEMINI",
          },
      }
      op_url = _method_url("onboardUser")
      lro = await client.post(op_url, headers=headers, json=onboard_payload)
      lro.raise_for_status()
      lro_data = lro.json() or {}
      # Poll until done
      start = time.time()
      while not lro_data.get("done") and time.time() - start < LRO_POLL_TIMEOUT:
        await asyncio.sleep(LRO_POLL_INTERVAL)
        lro = await client.post(op_url, headers=headers, json=onboard_payload)
        lro.raise_for_status()
        lro_data = lro.json() or {}

      response = (lro_data or {}).get("response") or {}
      ca_project = (response.get("cloudaicompanionProject") or {}).get("id")
      return ca_project
