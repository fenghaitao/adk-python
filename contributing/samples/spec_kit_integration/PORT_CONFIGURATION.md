# MCP Server Port Configuration

## Overview
The Spec-Kit integration now supports configurable MCP server ports, which is particularly useful for WSL2 environments where the default port (8051) may have socket binding issues.

## Changes Made

### 1. `start_mcp_servers.sh`
- **Added port parameter**: Script now accepts an optional port argument
- **Default**: 8051
- **Validation**: Port must be between 1024-65535
- **Usage**: `./start_mcp_servers.sh [PORT]`

**Examples:**
```bash
# Default port
./start_mcp_servers.sh

# Custom port
./start_mcp_servers.sh 8052
```

### 2. `run_spec_kit_phased.sh`
- **Added `--port` option**: Accepts port number via command line
- **Environment variable**: Exports `MCP_PORT` for child processes
- **Default**: 8051
- **Validation**: Port must be between 1024-65535

**Examples:**
```bash
# Default port
./run_spec_kit_phased.sh myproject "Create REST API"

# Custom port
./run_spec_kit_phased.sh myproject "Create REST API" --port 8052

# With model and custom port
./run_spec_kit_phased.sh myproject "Create REST API" --model github_copilot/claude-sonnet-4.5 --port 8052
```

### 3. `spec_kit_tools.py`
- **Updated `create_simics_mcp_toolset()`**: Now accepts optional `port` parameter
- **Environment variable support**: Reads from `MCP_PORT` if not provided
- **Backward compatible**: All existing code continues to work without changes

**Function signature:**
```python
def create_simics_mcp_toolset(port: Optional[int] = None) -> MCPToolset:
    """Create a MCP toolset that connects to the simics-mcp-server.
    
    Args:
        port: MCP server port. If not provided, reads from MCP_PORT 
              environment variable or defaults to 8051.
    """
```

## Port Resolution Order

The port is determined in the following order:

1. **Explicit parameter** (if calling `create_simics_mcp_toolset(port=8052)`)
2. **Environment variable** `MCP_PORT`
3. **Default value** `8051`

## Environment Variable Flow

```
run_spec_kit_phased.sh --port 8052
    ↓
export MCP_PORT=8052
    ↓
start_mcp_servers.sh 8052
    ↓
Python agents inherit MCP_PORT
    ↓
create_simics_mcp_toolset() reads MCP_PORT
    ↓
Connects to http://127.0.0.1:8052/sse
```

## WSL2 Considerations

### Why Custom Ports Are Needed
WSL2 has known networking issues:
- Slower socket cleanup after server shutdown
- "Address already in use" errors even when `lsof` shows nothing
- IPv4/IPv6 dual-stack conflicts with `0.0.0.0` binding

### Solutions
1. **Use a different port**: `--port 8052`
2. **Bind to 127.0.0.1**: Already configured in `run_server_sse.py`
3. **Wait between restarts**: 5-10 seconds for socket cleanup

### Recommended Workflow for WSL2
```bash
# Stop any existing servers
./contributing/samples/spec_kit_integration/simics-mcp-server/stop_mcp_servers.sh

# Wait for socket cleanup
sleep 5

# Start with custom port
./run_spec_kit_phased.sh myproject "Create REST API" --port 8052
```

## Testing

### Test port configuration
```bash
# Test start_mcp_servers.sh
cd contributing/samples/spec_kit_integration/simics-mcp-server
./start_mcp_servers.sh 8052

# Verify server is running
lsof -i :8052

# Stop server
./stop_mcp_servers.sh
```

### Test full workflow
```bash
# Run with custom port
./run_spec_kit_phased.sh test_project "Create a simple API" --port 8052

# Check environment variable is set
echo $MCP_PORT  # Should show 8052
```

## Backward Compatibility

All existing code continues to work without modifications:
- Scripts without `--port` use default 8051
- Python code calling `create_simics_mcp_toolset()` without arguments uses default
- Environment variable `MCP_PORT` is optional

## Troubleshooting

### Port already in use
```bash
# Check what's using the port
lsof -i :8051

# Use a different port
./run_spec_kit_phased.sh myproject --port 8052
```

### Connection refused
```bash
# Verify MCP server is running
lsof -i :8052

# Check server logs
tail -f contributing/samples/spec_kit_integration/simics-mcp-server/*.log
```

### Environment variable not set
```bash
# Manually set if needed
export MCP_PORT=8052

# Then run agents
adk run adk_specify_agent
```

## Files Modified

1. `contributing/samples/spec_kit_integration/simics-mcp-server/start_mcp_servers.sh`
2. `run_spec_kit_phased.sh`
3. `contributing/samples/spec_kit_integration/spec_kit_tools.py`

## Related Documentation

- `contributing/samples/spec_kit_integration/simics-mcp-server/START_MCP_SERVERS_USAGE.md`
- WSL2 networking issues: https://github.com/microsoft/WSL/issues
