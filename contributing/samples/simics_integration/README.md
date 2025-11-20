# Simics Integration Agent

This agent demonstrates how to integrate ADK with Simics hardware development tools for device modeling and hardware specification work.

## Features

- **Simics Project Setup**: Automatically creates Simics project structure
- **DML Device Skeleton Creation**: Generates device skeleton files for hardware modeling
- **DDM XML Integration**: Processes Device Data Model XML specifications
- **Hardware Specification Support**: Works with hardware specification documents

## Prerequisites

1. **Simics MCP Server**: The Simics MCP server must be running
2. **Spec Kit Integration**: Requires the spec_kit_integration sample with MCP tools
3. **Environment Setup**: Proper environment variables configured

## Usage

### Quick Start

```bash
# From the ADK root directory
export DDM_XML="path/to/your/device.xml"
export SPEC_FILE="path/to/your/specification.md"  
export DEVICE_NAME="your_device_name"
export MCP_PORT="8051"

python -m contributing.samples.simics_integration.main
```

### With WDT Defaults

If you have `wdt.xml`, `wdt.md` in your project directory:

```bash
# The agent will automatically detect and use WDT files
python -m contributing.samples.simics_integration.main
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DDM_XML` | Path to DDM XML file | None |
| `SPEC_FILE` | Path to specification file | None |
| `DEVICE_NAME` | Device name for skeleton creation | `wdt` |
| `MCP_PORT` | Port for Simics MCP server | `8051` |

## Agent Capabilities

The agent can help you with:

### 1. Project Setup
- Create complete Simics project structure
- Set up build configuration
- Initialize development environment

### 2. Device Development
- Generate DML device skeleton files
- Create device-specific templates
- Set up register mappings based on DDM XML

### 3. Hardware Specification
- Parse DDM XML specifications
- Map hardware registers to DML code
- Generate documentation from specifications

## Example Interactions

### Setting up a new hardware project:

```
User: "I need to create a new Simics project for my WDT device"

Agent: I'll help you set up a Simics project for WDT device development. Let me:
1. Create the Simics project structure
2. Add a DML device skeleton for the WDT device
3. Set up the development environment

[Agent uses create_simics_project and add_dml_device_skeleton tools]
```

### Working with DDM specifications:

```
User: "How do I implement the registers defined in my DDM XML?"

Agent: Based on your DDM XML specification, I can see the following registers:
- [Lists registers from DDM_XML content]
- I'll help you create the DML implementation...

[Agent provides specific guidance based on DDM content]
```

## Integration with run_openspec.sh

This agent is designed to work with the enhanced `run_openspec.sh` script:

```bash
# The script automatically exports environment variables and starts the agent
./run_openspec.sh myproject --ddm_xml wdt.xml --spec wdt.md --device wdt
```

## Development Workflow

1. **Prepare specifications**: Have your DDM XML and specification files ready
2. **Start MCP server**: Ensure Simics MCP server is running on the configured port
3. **Set environment**: Configure DDM_XML, SPEC_FILE, DEVICE_NAME variables
4. **Run agent**: Execute the agent to get interactive hardware development assistance
5. **Follow guidance**: Use agent recommendations for DML device implementation

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DDM XML       │    │   Simics Agent   │    │  Simics MCP     │
│   Spec Files    │───▶│   (ADK)          │───▶│  Server         │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   User           │    │  Simics Project │
                       │   Interaction    │    │  & DML Files    │
                       └──────────────────┘    └─────────────────┘
```

## Troubleshooting

### MCP Server Not Available
- Ensure the Simics MCP server is running on the specified port
- Check that `spec_kit_integration` sample is properly set up
- Verify MCP_PORT environment variable is correct

### File Not Found Errors  
- Check DDM_XML and SPEC_FILE paths are correct
- Ensure files are readable by the agent
- Verify working directory is correct

### Tool Execution Failures
- Confirm Simics tools are properly installed
- Check project directory permissions
- Verify device name is valid for Simics

## Related Samples

- `spec_kit_integration` - Provides the underlying MCP tools
- `openspec_integration` - Similar agent for OpenSpec workflow
- `mcp_stdio_server_agent` - Basic MCP integration example