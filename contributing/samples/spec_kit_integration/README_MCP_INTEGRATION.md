# Multiple MCP Server Integration Guide

This guide explains how to integrate multiple MCP (Model Context Protocol) servers with ADK agents, specifically showing how to add an HTTP SSE MCP server alongside the existing Simics MCP server.

## Overview

ADK supports connecting to multiple MCP servers simultaneously in a single agent. Each MCP server can provide different tools and capabilities:

- **Simics MCP Server**: Hardware simulation tools (STDIO connection)
- **HTTP SSE MCP Server**: Custom tools via HTTP Server-Sent Events
- **Spec-Kit Tools**: Basic file and bash operations

## Architecture

```
ADK Agent
├── Spec-Kit Toolset (built-in tools)
├── Simics MCP Toolset (STDIO connection)
└── HTTP SSE MCP Toolset (SSE connection)
```

## Integration Steps

### 1. Update spec_kit_tools.py

The `create_http_sse_mcp_toolset()` function has been added to connect to an HTTP SSE MCP server:

```python
def create_http_sse_mcp_toolset() -> MCPToolset:
    """Create a MCP toolset that connects to the HTTP SSE MCP server at localhost:8051."""
    connection_params = SseConnectionParams(
        url="http://127.0.0.1:8051/sse",
        headers={"Accept": "text/event-stream"},
        timeout=10.0,
        sse_read_timeout=300.0
    )
    
    return MCPToolset(
        connection_params=connection_params,
        tool_filter=None  # Include all tools
    )
```

### 2. Multiple MCP Servers in Agent

The main agent (`agent.py`) now supports multiple MCP servers with graceful fallback:

```python
# Add all available toolsets
tools = []
tools.append(create_spec_kit_toolset())

# Try to add Simics MCP toolset
try:
    tools.append(create_simics_mcp_toolset())
except Exception as e:
    print(f"Warning: Simics MCP toolset not available: {e}")

# Try to add HTTP SSE MCP toolset  
try:
    tools.append(create_http_sse_mcp_toolset())
except Exception as e:
    print(f"Warning: HTTP SSE MCP toolset not available: {e}")
```

## Connection Types

ADK supports multiple MCP connection types:

### STDIO Connection (Simics)
```python
StdioConnectionParams(
    server_params=StdioServerParameters(
        command=str(python_path),
        args=[str(server_script), "--transport", "stdio"]
    ),
    timeout=300.0
)
```

### SSE Connection (HTTP Server-Sent Events)
```python
SseConnectionParams(
    url="http://127.0.0.1:8051/sse",
    headers={"Accept": "text/event-stream"},
    timeout=10.0,
    sse_read_timeout=300.0
)
```

### Streamable HTTP Connection
```python
StreamableHTTPConnectionParams(
    url="http://127.0.0.1:8080/streamable",
    headers={"Content-Type": "application/json"},
    timeout=10.0,
    sse_read_timeout=300.0,
    terminate_on_close=True
)
```

## Usage Examples

### Basic Usage

```python
from spec_kit_tools import (
    create_simics_mcp_toolset,
    create_http_sse_mcp_toolset, 
    create_spec_kit_toolset
)

# Create agent with multiple toolsets
agent = LlmAgent(
    model='gemini-2.0-flash',
    name='multi_mcp_agent',
    tools=[
        create_spec_kit_toolset(),
        create_simics_mcp_toolset(),      # STDIO MCP
        create_http_sse_mcp_toolset(),    # HTTP SSE MCP
    ]
)
```

### Advanced Configuration

```python
# Custom tool filtering
http_sse_toolset = MCPToolset(
    connection_params=SseConnectionParams(
        url="http://127.0.0.1:8051/sse",
        headers={
            "Accept": "text/event-stream",
            "Authorization": "Bearer token123"
        }
    ),
    tool_filter=["specific_tool1", "specific_tool2"]  # Only these tools
)
```

## Testing

Run the test script to verify integration:

```bash
cd contributing/samples/spec_kit_integration
python test_http_sse_mcp.py
```

Run the multi-MCP example:

```bash
python multi_mcp_example.py
```

## Server Requirements

### HTTP SSE MCP Server

Your HTTP SSE MCP server at `http://127.0.0.1:8051/sse` should:

1. Implement the MCP protocol over Server-Sent Events
2. Accept `text/event-stream` content type
3. Provide proper MCP tool definitions
4. Handle connection timeouts appropriately

### Example Server Response

The server should respond to tool listing requests with MCP-compliant tool definitions:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "example_tool",
        "description": "An example tool",
        "inputSchema": {
          "type": "object",
          "properties": {
            "param1": {"type": "string"}
          },
          "required": ["param1"]
        }
      }
    ]
  }
}
```

## Error Handling

The integration includes robust error handling:

- **Connection failures**: Graceful fallback without breaking the agent
- **Server unavailable**: Warnings logged, agent continues with available tools
- **Tool execution errors**: Individual tool failures don't affect other toolsets
- **Timeout handling**: Configurable timeouts for different connection types

## Benefits

1. **Modularity**: Each MCP server provides specialized tools
2. **Scalability**: Easy to add new MCP servers as needed
3. **Resilience**: Agent works even if some MCP servers are unavailable
4. **Flexibility**: Different connection types for different use cases

## Troubleshooting

### Connection Issues

1. **Check server availability**:
   ```bash
   curl -H "Accept: text/event-stream" http://127.0.0.1:8051/sse
   ```

2. **Verify MCP protocol compliance**: Ensure server implements MCP correctly

3. **Check network connectivity**: Ensure no firewall blocking the connection

### Tool Discovery Issues

1. **Verify tool definitions**: Tools must have proper MCP schema
2. **Check filtering**: Ensure `tool_filter` isn't excluding needed tools
3. **Validate permissions**: MCP server must allow tool access

### Performance Issues

1. **Adjust timeouts**: Increase `timeout` and `sse_read_timeout` values
2. **Optimize tool filters**: Filter to only needed tools
3. **Monitor server load**: Ensure MCP server can handle concurrent requests

## Next Steps

1. **Add authentication**: Implement proper auth headers for secure servers
2. **Tool caching**: Cache tool definitions to improve performance  
3. **Health monitoring**: Add health checks for MCP server availability
4. **Custom protocols**: Extend to support other MCP transport mechanisms