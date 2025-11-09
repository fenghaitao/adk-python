# Simics-OpenSpec Integration Design Document

## Overview

This design document outlines the integration of Simics hardware model development capabilities into the existing OpenSpec-ADK integration. The design extends the current openspec_integration sample by adding Simics MCP (Model Context Protocol) tools, hardware device detection, and Simics-specific guidance while maintaining full compatibility with existing OpenSpec workflows for software development.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    run_openspec.sh                          │
│  (Initialization script - unchanged from base integration)  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     └─> adk run contributing/samples/openspec_integration
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          contributing/samples/openspec_integration/         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         agent.py (Enhanced OpenSpec Agent)           │  │
│  │  - Reads AGENTS.md from project directory            │  │
│  │  - Understands OpenSpec workflow                     │  │
│  │  - Detects hardware device modeling projects         │  │
│  │  - Uses Simics MCP tools for hardware projects       │  │
│  │  - Enhanced instructions for Simics development      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      openspec_tools.py (Existing Tool Wrapper)       │  │
│  │  - File operations (read_file, write_file)           │  │
│  │  - Bash command execution                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      simics_mcp_tools.py (NEW - Simics Tools)        │  │
│  │  - create_simics_mcp_toolset()                       │  │
│  │  - STDIO connection to Simics MCP server             │  │
│  │  - Graceful fallback if server unavailable           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         README.md (Enhanced Documentation)           │  │
│  │  - Simics integration section added                  │  │
│  │  - Hardware device workflow examples                 │  │
│  │  - Simics MCP server setup instructions              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Uses tools from
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Simics MCP Server (External - Port 8051)           │
│                                                             │
│  Simics Tools:                                              │
│  - get_simics_version()                                     │
│  - create_simics_project(project_name, project_path)        │
│  - add_dml_device_skeleton(project_path, device_name)       │
│  - build_simics_project(project_path, module)               │
│  - run_simics_test(project_path, suite)                     │
│  - search_packages(query)                                   │
│  - list_installed_packages()                                │
│                                                             │
│  RAG Documentation Search:                                  │
│  - perform_rag_query(query, source_type, match_count)       │
│    * source_type="dml" - Search DML documentation           │
│    * source_type="python" - Search Python API docs          │
│    * source_type="docs" - Search Simics documentation       │
│    * source_type="all" - Search everything                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow for Hardware Projects

```
User: "Create a change proposal for an ARM watchdog timer device"
      │
      ▼
OpenSpec Agent
      │
      ├─> Detect hardware keywords: "watchdog timer", "device"
      │
      ├─> Load Simics MCP toolset (if available)
      │
      ├─> Read AGENTS.md and project.md
      │
      └─> Create change proposal with:
          │
          ├─> proposal.md (explains hardware device feature)
          │
          ├─> specs/<device-name>/spec.md (hardware requirements)
          │   - Register map specifications
          │   - Interface definitions
          │   - Behavioral requirements
          │
          ├─> design.md (technical design)
          │   - DML 1.4 implementation approach
          │   - Simics project structure
          │   - Register and interface architecture
          │
          └─> tasks.md (implementation tasks)
              - T001: Verify Simics with get_simics_version()
              - T002: Create project with create_simics_project()
              - T003: Add skeleton with add_dml_device_skeleton()
              - T004: Write register tests
              - T005: Implement registers.dml
              - T006: Build with build_simics_project()
              - T007: Test with run_simics_test()
```

## Components and Interfaces

### 1. simics_mcp_tools.py (NEW)

**Purpose**: Provides Simics MCP toolset for hardware device development.

**Interface**:
```python
def create_simics_mcp_toolset() -> MCPToolset:
    """
    Create a MCP toolset for Simics operations using SSE connection.
    
    Returns:
        MCPToolset: Configured toolset with Simics MCP tools
        
    Raises:
        Exception: If Simics MCP server cannot be connected
    """
    # Create SSE connection parameters for Simics MCP server
    connection_params = SseConnectionParams(
        url="http://127.0.0.1:8051/sse",  # Simics MCP server SSE endpoint (default port)
        headers={"Accept": "text/event-stream"},
        timeout=10.0,
        sse_read_timeout=300.0
    )
    
    return MCPToolset(
        connection_params=connection_params,
        tool_filter=None  # Include all Simics tools
    )
```

**Design Rationale**:
- Uses SSE (Server-Sent Events) transport for HTTP-based communication
- Connects to Simics MCP server on port 8051 (default port)
- Provides long timeout for Simics operations (build, test can be slow)
- Follows the same pattern as spec_kit_integration's HTTP SSE MCP toolset
- Simpler than STDIO - no need to manage server process lifecycle

### 2. agent.py (ENHANCED)

**Purpose**: Enhanced OpenSpec agent with Simics hardware device modeling support.

**Key Changes**:

#### Hardware Detection Function
```python
def detect_hardware_project(text: str) -> bool:
    """
    Detect if the project involves hardware device modeling.
    
    Args:
        text: Feature description or project context
        
    Returns:
        bool: True if hardware device modeling is detected
    """
    hardware_keywords = [
        # Hardware terms
        "processor", "cpu", "gpu", "fpga", "microcontroller", "embedded",
        # Simulation terms
        "simulation", "modeling", "hardware validation", "device model",
        # Architecture terms
        "x86", "arm", "risc-v", "mips", "sparc",
        # Hardware components
        "pci", "usb", "memory controller", "peripheral", "watchdog timer",
        "network controller", "storage device", "interrupt controller",
        # Development terms
        "firmware", "bios", "bootloader", "dml", "register map",
        "hardware interface", "device driver"
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in hardware_keywords)
```

#### Enhanced System Instruction
```python
instruction = """
You are an OpenSpec agent that helps with spec-driven development for both 
software and hardware projects.

## OpenSpec Workflow

1. **Proposal**: Create change proposals in openspec/changes/
2. **Review**: Iterate on specs and tasks until approved
3. **Implement**: Execute tasks following the plan
4. **Archive**: Merge completed changes into openspec/specs/

## Hardware Device Modeling with Simics

**REQUIREMENTS**: Simics 7.x and DML 1.4 are required for hardware device modeling.

When working on hardware device models (detected by keywords like "processor", 
"device", "register", "DML", etc.), you have access to Simics MCP tools:

### Simics Project Structure
```
project_root/
├── modules/
│   └── <device-name>/
│       ├── <device-name>.dml      # Main device implementation
│       ├── registers.dml          # Register definitions
│       ├── interfaces.dml         # External interfaces
│       ├── utility.dml            # Common utilities
│       └── test/
│           ├── test_registers.py  # Register tests
│           ├── test_interfaces.py # Interface tests
│           └── s-<device-name>.py # Main test script
```

### Simics MCP Tools Available

**Project Management:**
- `get_simics_version()` - Verify Simics installation
- `create_simics_project(project_name, project_path)` - Create project structure
- `add_dml_device_skeleton(project_path, device_name)` - Add device template

**Build & Test:**
- `build_simics_project(project_path, module=None)` - Build device module
- `run_simics_test(project_path, suite=None)` - Run test suites

**Package Management:**
- `search_packages(query)` - Search available Simics packages
- `list_installed_packages()` - List installed packages

**Documentation Search (RAG):**
- `perform_rag_query(query, source_type, match_count)` - Search Simics documentation
  - `source_type="dml"` - Search DML 1.4 documentation and examples
  - `source_type="python"` - Search Simics Python API documentation
  - `source_type="docs"` - Search general Simics documentation
  - `source_type="all"` - Search all available sources

### Hardware Device Workflow

1. **Research Phase**: Use `perform_rag_query()` to search DML documentation and examples
2. **Specification Phase**: Define register map, interfaces, and behavior
3. **Setup Phase**: Use `create_simics_project()` and `add_dml_device_skeleton()`
4. **TDD Phase**: Write tests for registers and interfaces first
5. **Implementation Phase**: Implement DML files (registers.dml, interfaces.dml, device.dml)
   - Use `perform_rag_query(source_type="dml")` for DML syntax questions
   - Use `perform_rag_query(source_type="python")` for Python API questions
6. **Validation Phase**: Use `build_simics_project()` and `run_simics_test()`
7. **Integration Phase**: Test device in full system context

### DML 1.4 Best Practices (Required)

**IMPORTANT**: All device models MUST use DML 1.4 syntax. DML 1.2 is not supported.

- **Software-Visible Behavior**: Model only externally observable functionality
- **Register Accuracy**: All registers must match hardware specification exactly
- **Side Effects**: Implement in `write_register()` and `read_register()` methods
- **Attributes**: Use for internal state and checkpointing
- **Interfaces**: Implement in `connect` blocks for device communication
- **Events**: Use for asynchronous behavior and timing
- **DML 1.4 Syntax**: Use modern DML 1.4 constructs (not legacy DML 1.2)

## Available Tools

**File Operations:**
- read_file(file_path): Read file contents
- write_file(file_path, content, overwrite): Write files
- bash_command(command, working_directory, timeout): Execute commands

**Simics Tools (for hardware projects):**
- All Simics MCP tools listed above

**Documentation Search (for hardware projects):**
- perform_rag_query(query, source_type, match_count): Search Simics documentation
  - Use this tool when you need DML syntax examples
  - Use this tool when you need Python API documentation
  - Use this tool when you need Simics best practices
  - Example: `perform_rag_query("DML register definition syntax", source_type="dml")`

## Best Practices

- Always read AGENTS.md first to understand project context
- Use spec deltas (ADDED, MODIFIED, REMOVED) for changes
- For hardware projects, include register maps and interface definitions in specs
- Follow test-driven development: tests before implementation
- Validate specs before implementation
- Use Simics MCP tools for automated project setup and validation
"""
```

#### Tool Loading Logic
```python
class OpenSpecAgent(LlmAgent):
    """OpenSpec agent with optional Simics support (includes RAG)."""
    
    def __init__(self, **kwargs):
        # Start with base tools
        tools = []
        tools.append(create_openspec_toolset())
        
        # Try to add Simics MCP tools (includes both Simics and RAG tools)
        try:
            from .simics_mcp_tools import create_simics_mcp_toolset
            tools.append(create_simics_mcp_toolset())
            print("✓ Simics MCP tools loaded successfully (includes RAG documentation search)")
        except Exception as e:
            print(f"ℹ Simics MCP tools not available: {e}")
            print("  (Software projects will work normally)")
        
        kwargs["tools"] = tools
        
        super().__init__(
            name="openspec_agent",
            model=get_openspec_model(),
            instruction=instruction,
            description="OpenSpec agent for spec-driven development (software and hardware)",
            **kwargs
        )
```

### 3. README.md (ENHANCED)

**New Section to Add**: "Simics Hardware Device Modeling"

```markdown
## Simics Hardware Device Modeling

The OpenSpec integration supports hardware device modeling using Simics and DML 1.4.

### Prerequisites for Simics Projects

1. **Simics Installation**: Valid Simics 7.x installation (required)
2. **DML Version**: DML 1.4 language support (required)
3. **Simics MCP Server**: Located in `contributing/samples/openspec_integration/simics-mcp-server/`
4. **Python Environment**: Same environment used for ADK

### Simics Workflow Example

#### 1. Create Hardware Device Change Proposal

```
You: I want to create an ARM watchdog timer device model with timeout and reset functionality.
     Please create an OpenSpec change proposal for this Simics device.

Agent: I'll create an OpenSpec change proposal for the watchdog timer device.
       *Detects hardware keywords: "watchdog timer", "device model"*
       *Creates openspec/changes/add-watchdog-timer/ with:*
       - proposal.md: Explains the watchdog timer feature
       - specs/watchdog-timer/spec.md: Hardware requirements with register map
       - design.md: DML implementation approach and Simics project structure
       - tasks.md: Implementation tasks using Simics MCP tools
```

#### 2. Review Hardware Specifications

The spec delta will include hardware-specific requirements:

```markdown
# Delta for Watchdog Timer

## ADDED Requirements

### Requirement: Watchdog Timer Control Register
The device SHALL provide a 32-bit control register at offset 0x00.

#### Scenario: Enable watchdog
- WHEN software writes 1 to bit 0 of the control register
- THEN the watchdog timer SHALL start counting
- AND the device SHALL generate an interrupt on first timeout

### Requirement: Watchdog Timer Load Register
The device SHALL provide a 32-bit load register at offset 0x04.

#### Scenario: Set timeout value
- WHEN software writes a value to the load register
- THEN the watchdog timer SHALL use that value as the timeout period
- AND the value SHALL be decremented each clock cycle when enabled
```

#### 3. Implement Using Simics MCP Tools

The tasks.md will include Simics-specific tasks:

```markdown
# Implementation Tasks

## 1. Setup Phase
- [ ] 1.1 Verify Simics installation using `get_simics_version()`
- [ ] 1.2 Create project structure using `create_simics_project(project_name="watchdog-timer", project_path=".")`
- [ ] 1.3 Add device skeleton using `add_dml_device_skeleton(project_path=".", device_name="watchdog-timer")`

## 2. Test-Driven Development
- [ ] 2.1 Write register access tests in modules/watchdog-timer/test/test_registers.py
- [ ] 2.2 Write timeout behavior tests in modules/watchdog-timer/test/test_timeout.py
- [ ] 2.3 Write interrupt tests in modules/watchdog-timer/test/test_interrupts.py

## 3. Implementation
- [ ] 3.1 Implement register definitions in modules/watchdog-timer/registers.dml
- [ ] 3.2 Implement timer logic in modules/watchdog-timer/watchdog-timer.dml
- [ ] 3.3 Build device module using `build_simics_project(project_path=".", module="watchdog-timer")`

## 4. Validation
- [ ] 4.1 Run register tests using `run_simics_test(project_path=".", suite="test_registers")`
- [ ] 4.2 Run full test suite using `run_simics_test(project_path=".", suite="all")`
```

#### 4. Archive Completed Device

```
You: The watchdog timer device is complete and tested. Please archive the change.

Agent: I'll archive the add-watchdog-timer change.
       *Runs: openspec archive add-watchdog-timer --yes*
       ✓ Device implementation archived
       ✓ Specs updated in openspec/specs/watchdog-timer/
       ✓ Ready for the next hardware device!
```

### Simics MCP Server Setup

The Simics MCP server is located in the `simics-mcp-server/` subdirectory and must be started before using hardware device features.

**Start the Server:**
```bash
cd contributing/samples/openspec_integration/simics-mcp-server
python src/simics_mcp_server/server.py --transport sse --port 8051
```

**Or use the startup script:**
```bash
cd contributing/samples/openspec_integration
./start_simics_mcp_server.sh
```

**Verify Simics Installation:**
```python
# The agent will automatically verify Simics using:
get_simics_version()
```

**Stop the Server:**
```bash
./stop_simics_mcp_server.sh
```

### Troubleshooting Simics Integration

**Issue**: Simics MCP tools not available

**Solution**:
1. Verify Simics is installed and in PATH
2. Check that simics-mcp-server directory exists
3. Ensure Python environment has required dependencies
4. Software projects will work normally without Simics tools

**Issue**: Device build fails

**Solution**:
1. Check DML syntax errors in device files
2. Verify register definitions match specification
3. Use `build_simics_project()` to see detailed error messages
4. Review Simics documentation for DML 1.4 syntax

**Issue**: Tests fail

**Solution**:
1. Verify test expectations match device behavior
2. Check register read/write operations
3. Use Simics logging to debug device behavior
4. Run individual test suites to isolate issues
```

## Data Models

### Simics Project Directory Structure

```
<project_name>/
├── AGENTS.md                           # OpenSpec workflow instructions
├── openspec/
│   ├── project.md                      # Project context
│   ├── specs/                          # Current specifications
│   │   └── <device-name>/
│   │       └── spec.md                 # Device specification
│   └── changes/                        # Change proposals
│       └── add-<device-name>/
│           ├── proposal.md             # Change proposal
│           ├── design.md               # Technical design
│           ├── tasks.md                # Implementation tasks
│           └── specs/
│               └── <device-name>/
│                   └── spec.md         # Spec delta
├── modules/                            # Simics device modules
│   └── <device-name>/
│       ├── <device-name>.dml           # Main device
│       ├── registers.dml               # Register definitions
│       ├── interfaces.dml              # External interfaces
│       ├── utility.dml                 # Utilities
│       └── test/
│           ├── test_registers.py       # Register tests
│           ├── test_interfaces.py      # Interface tests
│           └── s-<device-name>.py      # Main test script
└── Makefile                            # Simics build configuration
```

### Hardware Specification Format

Hardware device specs include additional sections:

```markdown
# Watchdog Timer Device Specification

## Hardware Overview
- **Device Type**: Watchdog Timer
- **Architecture**: ARM PrimeCell compatible
- **Bus Interface**: APB (Advanced Peripheral Bus)
- **Address Space**: 4KB (0x1000 - 0x1FFF)

## Register Map

| Offset | Name    | Access | Description              |
|--------|---------|--------|--------------------------|
| 0x00   | WDTCTRL | RW     | Control register         |
| 0x04   | WDTLOAD | RW     | Load/timeout value       |
| 0x08   | WDTVAL  | RO     | Current counter value    |
| 0x0C   | WDTSTAT | RW1C   | Status register          |

## Register Definitions

### WDTCTRL - Control Register (Offset 0x00)

| Bits  | Name   | Access | Reset | Description           |
|-------|--------|--------|-------|-----------------------|
| 31:2  | -      | -      | 0     | Reserved              |
| 1     | RESEN  | RW     | 0     | Reset enable          |
| 0     | INTEN  | RW     | 0     | Interrupt enable      |

## Behavioral Requirements

### Requirement: Watchdog Enable
WHEN software writes 1 to WDTCTRL.INTEN, THE device SHALL start decrementing WDTVAL.

### Requirement: Timeout Interrupt
WHEN WDTVAL reaches 0 AND WDTCTRL.INTEN is 1, THE device SHALL generate an interrupt.

### Requirement: Timeout Reset
WHEN WDTVAL reaches 0 a second time AND WDTCTRL.RESEN is 1, THE device SHALL assert reset signal.
```

## Error Handling

### Simics MCP Server Connection Errors

**Scenario**: Simics MCP server not available

**Handling**:
1. Agent prints informational message: "Simics MCP tools not available"
2. Agent continues with file operation tools only
3. Software projects work normally
4. Hardware projects can still be specified, but implementation requires manual Simics setup

**User Guidance**:
- Check Simics installation
- Verify simics-mcp-server directory exists
- Review server logs for connection issues

### DML Build Errors

**Scenario**: Device build fails with syntax errors

**Handling**:
1. `build_simics_project()` returns detailed error messages
2. Agent suggests reviewing DML syntax
3. Agent recommends checking register definitions
4. Agent provides links to DML 1.4 documentation

### Test Execution Errors

**Scenario**: Simics tests fail

**Handling**:
1. `run_simics_test()` returns test failure details
2. Agent suggests reviewing test expectations
3. Agent recommends checking device behavior
4. Agent provides debugging guidance

## Testing Strategy

### Unit Tests

**Test Coverage**:
1. **simics_mcp_tools.py**:
   - Test toolset creation
   - Verify STDIO connection parameters
   - Test graceful failure when server unavailable

2. **agent.py**:
   - Test hardware detection function with various keywords
   - Verify tool loading with and without Simics MCP server
   - Test instruction content includes Simics guidance

### Integration Tests

**Test Scenarios**:
1. **Software Project Workflow**:
   - Create change proposal for software feature
   - Verify no Simics tools used
   - Validate normal OpenSpec workflow

2. **Hardware Project Workflow**:
   - Create change proposal for hardware device
   - Verify hardware detection triggers
   - Verify Simics MCP tools are suggested
   - Validate Simics project structure in tasks

3. **Mixed Project**:
   - Software and hardware changes in same repository
   - Verify appropriate tools used for each change

### End-to-End Tests

**Test Cases**:
1. **Watchdog Timer Device**:
   - Initialize OpenSpec project
   - Create watchdog timer change proposal
   - Verify spec includes register map
   - Verify tasks include Simics MCP tool calls
   - Simulate implementation workflow
   - Validate archiving process

2. **Network Controller Device**:
   - Create network controller change proposal
   - Verify complex register map handling
   - Verify interface definitions
   - Validate multi-file DML structure

## Implementation Notes

### Simics MCP Server Setup

The Simics MCP server should be:
1. **Running as HTTP SSE server** on `http://127.0.0.1:8051/sse` (default port)
2. **Started before using the agent** for hardware projects
3. **Located in** `contributing/samples/openspec_integration/simics-mcp-server/`

The server can be started with:
```bash
cd contributing/samples/openspec_integration/simics-mcp-server
python src/simics_mcp_server/server.py --transport sse --port 8051
```

Or using a startup script:
```bash
./start_simics_mcp_server.sh
```

### Tool Loading Strategy

The agent uses a try-except pattern to load Simics tools:
```python
try:
    tools.append(create_simics_mcp_toolset())
    print("✓ Simics MCP tools loaded")
except Exception as e:
    print(f"ℹ Simics MCP tools not available: {e}")
```

This ensures:
- Software projects work without Simics
- Hardware projects get Simics tools when available
- Clear feedback about tool availability
- No breaking changes to existing workflows

### Hardware Detection Heuristics

The hardware detection function uses keyword matching:
- **Broad coverage**: Includes many hardware-related terms
- **Case-insensitive**: Works with any capitalization
- **Extensible**: Easy to add new keywords
- **Conservative**: Prefers false positives (can always use software workflow)

### Compatibility with spec-kit Integration

This integration is **independent** from spec-kit integration:
- Different workflow philosophy (OpenSpec vs. phased)
- Different agent architecture (single vs. multi-agent)
- Shared concept: Simics MCP tools for hardware development
- Can coexist in same repository without conflicts

## Benefits

### For Hardware Developers

1. **Spec-Driven Hardware Development**: Apply proven spec-driven methodology to hardware
2. **Automated Project Setup**: Use Simics MCP tools for consistent project structure
3. **Test-Driven Development**: Write tests before implementing device logic
4. **Continuous Validation**: Build and test throughout development
5. **Clear Documentation**: Specifications serve as device documentation

### For Software Developers

1. **No Impact**: Software projects work exactly as before
2. **Unified Workflow**: Same OpenSpec workflow for all projects
3. **Optional Simics**: Simics tools only loaded when needed
4. **Clear Separation**: Hardware and software changes clearly distinguished

### For Teams

1. **Mixed Projects**: Support both software and hardware in same repository
2. **Consistent Process**: Same change proposal workflow for all features
3. **Explicit Tracking**: Hardware device changes tracked like software changes
4. **Auditable History**: Complete history of device specifications and implementations

## Future Enhancements

### Phase 2: Enhanced Hardware Support

- **Register Map Visualization**: Generate diagrams from register specifications
- **DML Code Generation**: Auto-generate DML skeletons from specs
- **Compliance Checking**: Validate implementations against specifications
- **Performance Modeling**: Add timing and performance specifications

### Phase 3: Advanced Simics Integration

- **Multi-Device Systems**: Support for systems with multiple devices
- **Platform Integration**: Templates for common platform configurations
- **Checkpoint Management**: Automated checkpoint creation and testing
- **Debug Support**: Integration with Simics debugging tools

### Phase 4: Collaboration Features

- **Spec Review Workflow**: Formal review process for hardware specifications
- **Change Impact Analysis**: Analyze impact of register changes on software
- **Version Management**: Track device model versions and compatibility
- **Documentation Generation**: Auto-generate device documentation from specs
