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

"""Gemini LLM with CLI-compatible authentication."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import sys
from functools import cached_property
from typing import AsyncGenerator, Optional, TYPE_CHECKING

from google.genai import Client
from google.genai import types
from google.genai.types import FinishReason
from google.auth.compute_engine import Credentials as ComputeCredentials
from typing_extensions import override

from .. import version
from ..auth.gemini_auth_types import AuthType, GeminiAuthConfig
from ..auth.gemini_auth_validator import GeminiAuthValidator
from ..auth.gemini_oauth_client import GeminiOAuthCredentialManager
from ..utils.context_utils import Aclosing
from ..utils.variant_utils import GoogleLLMVariant
from .base_llm import BaseLlm
from .base_llm_connection import BaseLlmConnection
from .gemini_llm_connection import GeminiLlmConnection
from .llm_response import LlmResponse

if TYPE_CHECKING:
    from .llm_request import LlmRequest

logger = logging.getLogger('google_adk.' + __name__)

_NEW_LINE = '\n'
_EXCLUDED_PART_FIELD = {'inline_data': {'data'}}
_AGENT_ENGINE_TELEMETRY_TAG = 'remote_reasoning_engine'
_AGENT_ENGINE_TELEMETRY_ENV_VARIABLE_NAME = 'GOOGLE_CLOUD_AGENT_ENGINE_ID'


class GeminiCLI(BaseLlm):
    """Gemini model with CLI-compatible authentication.
    
    This class provides access to Gemini models using the same authentication
    methods as the Gemini CLI, including OAuth, API keys, and Cloud Shell.
    
    Attributes:
        model: The name of the Gemini model.
        auth_type: The authentication type to use.
        no_browser: Whether to suppress browser launch for OAuth.
    """
    
    model: str = 'gemini-2.5-flash'
    auth_type: Optional[AuthType] = None
    no_browser: bool = False
    retry_options: Optional[types.HttpRetryOptions] = None
    
    def __init__(
        self,
        model: str = 'gemini-2.5-flash',
        auth_type: Optional[AuthType] = None,
        no_browser: bool = False,
        retry_options: Optional[types.HttpRetryOptions] = None,
        **kwargs
    ):
        """Initialize the Gemini CLI model.
        
        Args:
            model: The name of the Gemini model.
            auth_type: The authentication type to use. If None, will be auto-detected.
            no_browser: Whether to suppress browser launch for OAuth.
            retry_options: HTTP retry options for the client.
            **kwargs: Additional arguments passed to the base class.
        """
        super().__init__(**kwargs)
        self.model = model
        self.auth_type = auth_type or GeminiAuthValidator.get_default_auth_type()
        self.no_browser = no_browser or bool(os.environ.get('NO_BROWSER'))
        self.retry_options = retry_options
        
        # Validate authentication method
        error = GeminiAuthValidator.validate_auth_method(self.auth_type)
        if error:
            raise ValueError(f"Authentication validation failed: {error}")
            
        self._auth_config = GeminiAuthConfig(
            **GeminiAuthValidator.create_auth_config_from_env(self.auth_type)
        )
        self._oauth_manager: Optional[GeminiOAuthCredentialManager] = None
        
    @classmethod
    @override
    def supported_models(cls) -> list[str]:
        """Provides the list of supported models.
        
        Returns:
            A list of supported models.
        """
        return [
            r'gemini-.*',
            # model optimizer pattern
            r'model-optimizer-.*',
            # fine-tuned vertex endpoint pattern
            r'projects\/.+\/locations\/.+\/endpoints\/.+',
            # vertex gemini long name
            r'projects\/.+\/locations\/.+\/publishers\/google\/models\/gemini.+',
        ]
        
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        """Sends a request to the Gemini model.
        
        Args:
            llm_request: LlmRequest, the request to send to the Gemini model.
            stream: bool = False, whether to do streaming call.
            
        Yields:
            LlmResponse: The model response.
        """
        await self._preprocess_request(llm_request)
        self._maybe_append_user_content(llm_request)
        logger.info(
            'Sending out request, model: %s, backend: %s, stream: %s',
            llm_request.model,
            self._api_backend,
            stream,
        )
        logger.debug(self._build_request_log(llm_request))
        
        # Always add tracking headers to custom headers
        if llm_request.config:
            if not llm_request.config.http_options:
                llm_request.config.http_options = types.HttpOptions()
            llm_request.config.http_options.headers = self._merge_tracking_headers(
                llm_request.config.http_options.headers
            )
            
        client = await self._get_authenticated_client()
        
        if stream:
            responses = await client.aio.models.generate_content_stream(
                model=llm_request.model,
                contents=llm_request.contents,
                config=llm_request.config,
            )
            response = None
            thought_text = ''
            text = ''
            usage_metadata = None
            
            async with Aclosing(responses) as agen:
                async for response in agen:
                    logger.debug(self._build_response_log(response))
                    llm_response = LlmResponse.create(response)
                    usage_metadata = llm_response.usage_metadata
                    if (
                        llm_response.content
                        and llm_response.content.parts
                        and llm_response.content.parts[0].text
                    ):
                        part0 = llm_response.content.parts[0]
                        if part0.thought:
                            thought_text += part0.text
                        else:
                            text += part0.text
                        llm_response.partial = True
                    elif (thought_text or text) and (
                        not llm_response.content
                        or not llm_response.content.parts
                        or not llm_response.content.parts[0].inline_data
                    ):
                        parts = []
                        if thought_text:
                            parts.append(types.Part(text=thought_text, thought=True))
                        if text:
                            parts.append(types.Part.from_text(text=text))
                        yield LlmResponse(
                            content=types.ModelContent(parts=parts),
                            usage_metadata=llm_response.usage_metadata,
                        )
                        thought_text = ''
                        text = ''
                    yield llm_response
                    
            # Generate an aggregated content at the end
            if (text or thought_text) and response and response.candidates:
                parts = []
                if thought_text:
                    parts.append(types.Part(text=thought_text, thought=True))
                if text:
                    parts.append(types.Part.from_text(text=text))
                yield LlmResponse(
                    content=types.ModelContent(parts=parts),
                    error_code=None
                    if response.candidates[0].finish_reason == FinishReason.STOP
                    else response.candidates[0].finish_reason,
                    error_message=None
                    if response.candidates[0].finish_reason == FinishReason.STOP
                    else response.candidates[0].finish_message,
                    usage_metadata=usage_metadata,
                )
        else:
            response = await client.aio.models.generate_content(
                model=llm_request.model,
                contents=llm_request.contents,
                config=llm_request.config,
            )
            logger.info('Response received from the model.')
            logger.debug(self._build_response_log(response))
            yield LlmResponse.create(response)
            
    async def _get_authenticated_client(self) -> Client:
        """Get an authenticated client based on the auth type."""
        if self._auth_config.is_oauth or self._auth_config.is_cloud_shell:
            return await self._get_oauth_client()
        else:
            return self._get_api_key_client()
            
    async def _get_oauth_client(self) -> Client:
        """Get a client authenticated with OAuth or Cloud Shell."""
        if self._auth_config.is_cloud_shell:
            # For Cloud Shell, use compute engine credentials
            credentials = ComputeCredentials()
            return Client(
                http_options=types.HttpOptions(
                    headers=self._tracking_headers,
                    retry_options=self.retry_options,
                ),
                credentials=credentials,
                vertexai=True,
            )
        else:
            # For OAuth, use the OAuth credential manager
            if not self._oauth_manager:
                self._oauth_manager = GeminiOAuthCredentialManager()
                
            credentials = await self._oauth_manager.get_credentials()
            
            # Create client with OAuth credentials
            # OAuth credentials work with Vertex AI, need project and location
            import os
            project = os.environ.get('GOOGLE_CLOUD_PROJECT')
            location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
            
            if not project:
                # Try to get project from gcloud config
                try:
                    import subprocess
                    result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                          capture_output=True, text=True, check=True)
                    project = result.stdout.strip()
                except:
                    # Default project for OAuth
                    project = 'gemini-oauth-project'
            
            return Client(
                http_options=types.HttpOptions(
                    headers=self._tracking_headers,
                    retry_options=self.retry_options,
                ),
                credentials=credentials,
                vertexai=True,  # OAuth credentials work with Vertex AI
                project=project,
                location=location,
            )
        
    def _get_api_key_client(self) -> Client:
        """Get a client authenticated with API key."""
        return Client(
            api_key=self._auth_config.api_key,
            vertexai=self._auth_config.is_vertex_ai,
            http_options=types.HttpOptions(
                headers=self._tracking_headers,
                retry_options=self.retry_options,
            )
        )
        
    @cached_property
    def api_client(self) -> Client:
        """Provides the api client.
        
        Note: This is a synchronous property for compatibility.
        For OAuth authentication, use _get_authenticated_client() instead.
        
        Returns:
            The api client.
        """
        if self._auth_config.is_oauth or self._auth_config.is_cloud_shell:
            # For OAuth, we need async authentication, so return a basic client
            # The actual authenticated client will be created in generate_content_async
            return Client(
                http_options=types.HttpOptions(
                    headers=self._tracking_headers,
                    retry_options=self.retry_options,
                )
            )
        else:
            return self._get_api_key_client()
            
    @cached_property
    def _api_backend(self) -> GoogleLLMVariant:
        return (
            GoogleLLMVariant.VERTEX_AI
            if self._auth_config.is_vertex_ai or self._auth_config.is_oauth or self._auth_config.is_cloud_shell
            else GoogleLLMVariant.GEMINI_API
        )
        
    @cached_property
    def _tracking_headers(self) -> dict[str, str]:
        framework_label = f'google-adk/{version.__version__}'
        if os.environ.get(_AGENT_ENGINE_TELEMETRY_ENV_VARIABLE_NAME):
            framework_label = f'{framework_label}+{_AGENT_ENGINE_TELEMETRY_TAG}'
        language_label = 'gl-python/' + sys.version.split()[0]
        version_header_value = f'{framework_label} {language_label}'
        tracking_headers = {
            'x-goog-api-client': version_header_value,
            'user-agent': version_header_value,
        }
        return tracking_headers
        
    @cached_property
    def _live_api_version(self) -> str:
        if self._api_backend == GoogleLLMVariant.VERTEX_AI:
            return 'v1beta1'
        else:
            return 'v1alpha'
            
    @cached_property
    def _live_api_client(self) -> Client:
        return Client(
            http_options=types.HttpOptions(
                headers=self._tracking_headers, 
                api_version=self._live_api_version
            )
        )
        
    @contextlib.asynccontextmanager
    async def connect(self, llm_request: LlmRequest) -> BaseLlmConnection:
        """Connects to the Gemini model and returns an llm connection.
        
        Args:
            llm_request: LlmRequest, the request to send to the Gemini model.
            
        Yields:
            BaseLlmConnection, the connection to the Gemini model.
        """
        # Add tracking headers and set api_version
        if (
            llm_request.live_connect_config
            and llm_request.live_connect_config.http_options
        ):
            if not llm_request.live_connect_config.http_options.headers:
                llm_request.live_connect_config.http_options.headers = {}
            llm_request.live_connect_config.http_options.headers.update(
                self._tracking_headers
            )
            llm_request.live_connect_config.http_options.api_version = (
                self._live_api_version
            )
            
        llm_request.live_connect_config.system_instruction = types.Content(
            role='system',
            parts=[
                types.Part.from_text(text=llm_request.config.system_instruction)
            ],
        )
        llm_request.live_connect_config.tools = llm_request.config.tools
        logger.info('Connecting to live with llm_request:%s', llm_request)
        
        client = await self._get_authenticated_client()
        async with client.aio.live.connect(
            model=llm_request.model, config=llm_request.live_connect_config
        ) as live_session:
            yield GeminiLlmConnection(live_session)
            
    async def _preprocess_request(self, llm_request: LlmRequest) -> None:
        """Preprocess the request based on the API backend."""
        if self._api_backend == GoogleLLMVariant.GEMINI_API:
            # Using API key from Google AI Studio doesn't support labels
            if llm_request.config:
                llm_request.config.labels = None
                
            if llm_request.contents:
                for content in llm_request.contents:
                    if not content.parts:
                        continue
                    for part in content.parts:
                        self._remove_display_name_if_present(part.inline_data)
                        self._remove_display_name_if_present(part.file_data)
                        
        # Initialize config if needed
        if llm_request.config and llm_request.config.tools:
            # Check if computer use is configured
            for tool in llm_request.config.tools:
                if (
                    isinstance(tool, (types.Tool, types.ToolDict))
                    and hasattr(tool, 'computer_use')
                    and tool.computer_use
                ):
                    llm_request.config.system_instruction = None
                    await self._adapt_computer_use_tool(llm_request)
                    
    async def _adapt_computer_use_tool(self, llm_request: LlmRequest) -> None:
        """Adapt the google computer use predefined functions to the adk computer use toolset."""
        from ..tools.computer_use.computer_use_toolset import ComputerUseToolset
        
        async def convert_wait_to_wait_5_seconds(wait_func):
            async def wait_5_seconds():
                return await wait_func(5)
            return wait_5_seconds
            
        await ComputerUseToolset.adapt_computer_use_tool(
            'wait', convert_wait_to_wait_5_seconds, llm_request
        )
        
    def _merge_tracking_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Merge tracking headers to the given headers."""
        headers = headers or {}
        for key, tracking_header_value in self._tracking_headers.items():
            custom_value = headers.get(key, None)
            if not custom_value:
                headers[key] = tracking_header_value
                continue
                
            # Merge tracking headers with existing headers and avoid duplicates
            value_parts = tracking_header_value.split(' ')
            for custom_value_part in custom_value.split(' '):
                if custom_value_part not in value_parts:
                    value_parts.append(custom_value_part)
            headers[key] = ' '.join(value_parts)
        return headers
        
    def _remove_display_name_if_present(self, data_obj) -> None:
        """Sets display_name to None for the Gemini API (non-Vertex) backend."""
        if data_obj and hasattr(data_obj, 'display_name') and data_obj.display_name:
            data_obj.display_name = None
            
    def _build_request_log(self, req: LlmRequest) -> str:
        """Build a log string for the request."""
        function_decls = (
            req.config.tools[0].function_declarations if req.config.tools else []
        )
        function_logs = (
            [
                f'{func_decl.name}: {func_decl.parameters}'
                for func_decl in function_decls
            ]
            if function_decls
            else []
        )
        contents_logs = [
            str(content) for content in req.contents
        ]
        
        return f"""
LLM Request:
-----------------------------------------------------------
System Instruction:
{req.config.system_instruction if req.config else None}
-----------------------------------------------------------
Contents:
{_NEW_LINE.join(contents_logs)}
-----------------------------------------------------------
Functions:
{_NEW_LINE.join(function_logs)}
-----------------------------------------------------------
"""
        
    def _build_response_log(self, resp: types.GenerateContentResponse) -> str:
        """Build a log string for the response."""
        function_calls_text = []
        if function_calls := resp.function_calls:
            for func_call in function_calls:
                function_calls_text.append(
                    f'name: {func_call.name}, args: {func_call.args}'
                )
        return f"""
LLM Response:
-----------------------------------------------------------
Text:
{resp.text}
-----------------------------------------------------------
Function calls:
{_NEW_LINE.join(function_calls_text)}
-----------------------------------------------------------
"""