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

import json
import os
from typing import Optional, Dict

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPServerParams,
    SseConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

# Configuration via environment variables to support different deployments
# of the mcp-crawl4ai-rag server without changing code.
#
# Prefer Streamable HTTP if MCP_CRAWL4AI_RAG_URL is provided (default), but
# you can switch to SSE by setting MCP_CRAWL4AI_RAG_PROTOCOL=sse.

_MCP_URL: str = os.getenv("MCP_CRAWL4AI_RAG_URL", "http://127.0.0.1:8051/sse")
_MCP_PROTOCOL: str = os.getenv("MCP_CRAWL4AI_RAG_PROTOCOL", "sse").lower()
_MCP_HEADERS_RAW: Optional[str] = os.getenv("MCP_CRAWL4AI_RAG_HEADERS")

_HEADERS: Optional[Dict[str, str]] = None
if _MCP_HEADERS_RAW:
  try:
    parsed = json.loads(_MCP_HEADERS_RAW)
    if isinstance(parsed, dict):
      # Ensure all header values are strings
      _HEADERS = {str(k): str(v) for k, v in parsed.items()}
  except json.JSONDecodeError:
    # Ignore invalid JSON and proceed without custom headers
    _HEADERS = None

# Always use SSE by default; allow override via MCP_CRAWL4AI_RAG_PROTOCOL
if _MCP_PROTOCOL == "sse":
  # Ensure SSE Accept header is present
  sse_headers = {"Accept": "text/event-stream"}
  if _HEADERS:
    sse_headers.update(_HEADERS)
  _connection_params = SseConnectionParams(url=_MCP_URL, headers=sse_headers)
else:
  # Fallback: keep option to use Streamable HTTP if explicitly set
  _connection_params = StreamableHTTPServerParams(url=_MCP_URL, headers=_HEADERS)

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="mcp_crawl4ai_rag_root",
    instruction=(
        "You are a RAG chatbot assistant. Use the mcp-crawl4ai-rag tools to "
        "crawl, index, and retrieve information from the web or provided corpora. "
        "Prefer using the available tools for searching, crawling, embedding, and "
        "querying over making assumptions. Ask clarifying questions when needed."
    ),
    tools=[
        MCPToolset(
            connection_params=_connection_params,
            # Allow crawl and query tools; exclude knowledge graph related tools
            tool_filter=lambda tool, ctx=None: (
                ("crawl" in tool.name.lower() or "query" in tool.name.lower())
                and ("kg" not in tool.name.lower()
                     and "graph" not in tool.name.lower()
                     and "knowledge" not in tool.name.lower())
            ),
        )
    ],
)
