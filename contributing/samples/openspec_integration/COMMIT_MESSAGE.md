# Commit Message

```
feat: Add Simics hardware device modeling to OpenSpec integration #non-breaking

Integrate Simics MCP tools into OpenSpec-ADK integration to enable
spec-driven development for hardware device models written in DML 1.4.

## Changes

### New Files
- simics_mcp_tools.py: Imports Simics MCP toolset from spec_kit_integration
- test_hardware_detection.py: Unit tests for hardware detection (20/20 passing)
- verify_simics_integration.py: Integration verification script
- SIMICS_INTEGRATION_SUMMARY.md: Detailed implementation documentation
- IMPLEMENTATION_COMPLETE.md: Verification results and usage guide

### Modified Files
- agent.py: Added hardware detection and Simics tool loading
- README.md: Added comprehensive Simics integration documentation

## Features

- **Hardware Detection**: Automatic detection of hardware projects via keywords
- **Simics MCP Tools**: Project management, build, test, and RAG documentation search
- **Graceful Degradation**: Software projects work normally without Simics server
- **Code Reuse**: Imports toolset from spec_kit_integration for consistency
- **Comprehensive Docs**: Complete workflow examples and troubleshooting

## Requirements

- Simics 7.x (required for hardware projects)
- DML 1.4 (required for hardware projects)
- Simics MCP server running on port 8051 (optional for software projects)

## Testing

- ✅ Hardware detection: 20/20 tests passing
- ✅ Agent initialization: Verified
- ✅ Tool availability: All 10 Simics tools available
- ✅ Integration: End-to-end verification successful
- ✅ Code quality: Formatted with isort and black

## Backward Compatibility

This change is non-breaking:
- Software projects work exactly as before
- Simics tools only loaded when server available
- No changes to existing OpenSpec workflows
- No impact on other ADK samples

## Usage

Software projects (unchanged):
  ./run_openspec.sh my_project

Hardware projects (requires Simics MCP server):
  # Terminal 1: Start server
  python simics-mcp-server/src/simics_mcp_server/server.py --transport sse --port 8051
  
  # Terminal 2: Run agent
  ./run_openspec.sh my_hardware_project
```
