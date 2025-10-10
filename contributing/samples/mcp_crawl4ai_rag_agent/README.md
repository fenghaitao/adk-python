This agent connects to an mcp-crawl4ai-rag MCP server and exposes its tools to the agent as a chatbot.

Usage

1) Start or point to a running mcp-crawl4ai-rag server.
   - SSE (default): export MCP_CRAWL4AI_RAG_URL="http://127.0.0.1:8051/sse"
   - Streamable HTTP (optional): set MCP_CRAWL4AI_RAG_PROTOCOL=streamable_http and MCP_CRAWL4AI_RAG_URL accordingly.
   - Optional headers (e.g., auth): export MCP_CRAWL4AI_RAG_HEADERS='{"Authorization": "Bearer ..."}'

2) Run the agent using ADK Runner. For example, via the CLI or your app that loads root_agent from this module.

Notes
- The agent uses MCP SSE by default. To use Streamable HTTP instead, set MCP_CRAWL4AI_RAG_PROTOCOL=streamable_http.
- The agent filters tools to allow crawl and query operations and excludes knowledge graph-related tools.
