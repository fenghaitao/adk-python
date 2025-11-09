# Requirements Document

## Introduction

This specification defines the integration of Simics hardware model development capabilities into the existing OpenSpec-ADK integration. The goal is to enable developers to use OpenSpec's spec-driven development workflow for creating Simics device models written in DML 1.4, while leveraging Simics MCP (Model Context Protocol) tools for project automation, building, and testing.

## Glossary

- **Simics**: A full-system simulator for embedded and hardware development (version 7.x required)
- **DML**: Device Modeling Language - Simics' domain-specific language for hardware device models (version 1.4 required)
- **MCP**: Model Context Protocol - A standard for connecting AI agents to external tools
- **Simics MCP Server**: An MCP server providing tools for Simics project management, building, and testing
- **OpenSpec**: A spec-driven development tool that manages specifications and change proposals
- **OpenSpec Agent**: The ADK agent that orchestrates OpenSpec workflows
- **Change Proposal**: An OpenSpec concept representing a proposed feature with specs, tasks, and design
- **Hardware Device Model**: A software simulation of a hardware device (e.g., watchdog timer, network controller)
- **Register Map**: The memory-mapped registers that define a hardware device's software interface

## Requirements

### Requirement 1: Simics MCP Tools Integration

**User Story:** As a hardware developer, I want the OpenSpec agent to have access to Simics MCP tools, so that I can automate Simics project creation, building, and testing within the OpenSpec workflow.

#### Acceptance Criteria

1. THE OpenSpec Agent SHALL integrate the Simics MCP toolset alongside existing file operation tools
2. THE Integration SHALL use SSE (Server-Sent Events) connection parameters to communicate with the Simics MCP server
3. THE Integration SHALL connect to the Simics MCP server at `http://127.0.0.1:8051/sse` (default port)
4. THE Agent SHALL have access to `get_simics_version()` tool for verifying Simics installation
5. THE Agent SHALL have access to `create_simics_project()` tool for creating Simics project structures
6. THE Agent SHALL have access to `add_dml_device_skeleton()` tool for generating DML device templates
7. THE Agent SHALL have access to `build_simics_project()` tool for compiling DML device modules
8. THE Agent SHALL have access to `run_simics_test()` tool for executing Simics test suites
9. THE Agent SHALL gracefully handle cases where Simics MCP server is unavailable

### Requirement 2: Hardware Device Detection

**User Story:** As a hardware developer, I want the OpenSpec agent to automatically detect when I'm working on a Simics hardware device model, so that it can provide appropriate guidance and use Simics-specific tools.

#### Acceptance Criteria

1. THE Agent SHALL detect hardware device modeling projects based on keywords in feature descriptions
2. THE Detection SHALL recognize hardware terms including "processor", "CPU", "GPU", "FPGA", "microcontroller", "embedded"
3. THE Detection SHALL recognize simulation terms including "simulation", "modeling", "hardware validation", "device model"
4. THE Detection SHALL recognize architecture terms including "x86", "ARM", "RISC-V", "MIPS", "SPARC"
5. THE Detection SHALL recognize hardware components including "PCI", "USB", "memory controller", "peripheral", "watchdog timer"
6. THE Detection SHALL recognize development terms including "firmware", "BIOS", "bootloader", "DML", "register map"
7. WHEN hardware device modeling is detected, THE Agent SHALL suggest using Simics MCP tools in change proposals

### Requirement 3: Enhanced Agent Instructions for Simics

**User Story:** As a hardware developer, I want the OpenSpec agent to understand Simics development workflows, so that it can guide me through creating proper hardware device specifications and implementations.

#### Acceptance Criteria

1. THE Agent System Instruction SHALL include a section explaining Simics hardware device modeling
2. THE Instruction SHALL describe the DML 1.4 language and its purpose
3. THE Instruction SHALL explain the typical structure of a Simics device model project
4. THE Instruction SHALL provide guidance on when to use Simics MCP tools during development
5. THE Instruction SHALL explain the relationship between hardware specifications and DML implementations
6. THE Instruction SHALL emphasize software-visible behavior focus for device modeling
7. THE Instruction SHALL recommend test-driven development for hardware device models

### Requirement 4: Simics Project Structure Support

**User Story:** As a hardware developer, I want change proposals for Simics devices to follow the standard Simics project structure, so that my projects are compatible with Simics tooling and conventions.

#### Acceptance Criteria

1. THE Agent SHALL recommend the standard Simics project structure for hardware device change proposals
2. THE Project Structure SHALL include a `modules/` directory at the project root
3. THE Project Structure SHALL include a `modules/<device-name>/` directory for each device
4. THE Project Structure SHALL include DML files: `<device-name>.dml`, `registers.dml`, `interfaces.dml`, `utility.dml`
5. THE Project Structure SHALL include a `test/` directory within the device module
6. THE Project Structure SHALL include test files: `test_registers.py`, `test_interfaces.py`, `s-<device-name>.py`
7. THE Agent SHALL explain this structure in change proposal design documents

### Requirement 5: Simics-Specific Task Generation

**User Story:** As a hardware developer, I want task lists for Simics device models to include appropriate setup, implementation, and testing tasks using Simics MCP tools, so that I have a clear implementation roadmap.

#### Acceptance Criteria

1. THE Agent SHALL generate Simics-specific tasks when hardware device modeling is detected
2. THE Task List SHALL include a setup phase using `create_simics_project()` and `add_dml_device_skeleton()` tools
3. THE Task List SHALL include build validation tasks using `build_simics_project()` tool
4. THE Task List SHALL include test execution tasks using `run_simics_test()` tool
5. THE Task List SHALL follow test-driven development ordering: setup → tests → implementation → validation
6. THE Task List SHALL include tasks for register definitions, interface implementations, and device logic
7. THE Task List SHALL reference specific DML files and test files in task descriptions

### Requirement 6: Documentation and Examples

**User Story:** As a hardware developer new to using OpenSpec with Simics, I want clear documentation and examples, so that I can quickly understand how to develop Simics device models using the OpenSpec workflow.

#### Acceptance Criteria

1. THE Sample SHALL include an updated README.md with Simics integration documentation
2. THE README SHALL explain how Simics MCP tools integrate with OpenSpec workflows
3. THE README SHALL provide an example of creating a Simics device model change proposal
4. THE README SHALL document the Simics project structure and file organization
5. THE README SHALL include troubleshooting guidance for Simics-specific issues
6. THE README SHALL reference the Simics MCP server setup and configuration
7. THE README SHALL provide examples of typical Simics device modeling tasks

### Requirement 7: Simics MCP Server Configuration

**User Story:** As a developer, I want clear instructions for setting up the Simics MCP server, so that the OpenSpec agent can access Simics tools.

#### Acceptance Criteria

1. THE Documentation SHALL explain how to locate the Simics MCP server implementation
2. THE Documentation SHALL provide instructions for starting the Simics MCP server with SSE transport
3. THE Documentation SHALL specify the SSE endpoint URL (`http://127.0.0.1:8051/sse`) used for communication
4. THE Documentation SHALL provide a startup script for launching the Simics MCP server
5. THE Documentation SHALL explain the required Simics installation and environment setup
6. THE Documentation SHALL provide troubleshooting steps for connection issues
7. THE Documentation SHALL reference the Simics MCP server's available tools and their parameters

### Requirement 8: Example Simics Device Workflow

**User Story:** As a hardware developer, I want a complete example of developing a Simics device using OpenSpec, so that I can see the full workflow in action.

#### Acceptance Criteria

1. THE Documentation SHALL include a complete example of creating a watchdog timer device
2. THE Example SHALL show the initial change proposal creation with hardware specifications
3. THE Example SHALL demonstrate spec delta format for hardware device requirements
4. THE Example SHALL show the task list with Simics MCP tool calls
5. THE Example SHALL demonstrate the implementation workflow using OpenSpec commands
6. THE Example SHALL show how to validate and test the device implementation
7. THE Example SHALL demonstrate archiving the completed change

### Requirement 9: Compatibility with Existing OpenSpec Integration

**User Story:** As a developer, I want the Simics integration to work seamlessly with the existing OpenSpec integration, so that I can use OpenSpec for both software and hardware projects without conflicts.

#### Acceptance Criteria

1. THE Simics Integration SHALL extend the existing openspec_integration sample without breaking changes
2. THE Integration SHALL maintain compatibility with non-Simics OpenSpec workflows
3. THE Integration SHALL use the same agent architecture and tool patterns as the base integration
4. THE Integration SHALL follow ADK sample conventions and structure
5. THE Integration SHALL not interfere with other ADK samples
6. THE Integration SHALL support both software and hardware projects in the same OpenSpec repository

### Requirement 10: Simics Version and DML Language Requirements

**User Story:** As a hardware developer, I want the integration to enforce Simics 7.x and DML 1.4 requirements, so that device models use modern, supported tooling.

#### Acceptance Criteria

1. THE Documentation SHALL explicitly state that Simics 7.x is required (not optional)
2. THE Documentation SHALL explicitly state that DML 1.4 is required (not optional)
3. THE Agent Instructions SHALL emphasize using DML 1.4 syntax only
4. THE Agent Instructions SHALL warn against using legacy DML 1.2 constructs
5. THE Agent SHALL verify Simics version using `get_simics_version()` tool before creating projects
6. THE Error Messages SHALL clearly indicate when Simics 7.x is not detected
7. THE Examples SHALL use only DML 1.4 syntax and Simics 7.x features

### Requirement 11: RAG Documentation Search Integration

**User Story:** As a hardware developer, I want the OpenSpec agent to search Simics documentation during development, so that I can get accurate DML syntax examples and API references.

#### Acceptance Criteria

1. THE OpenSpec Agent SHALL integrate the RAG MCP toolset for documentation search
2. THE Integration SHALL use SSE connection to the RAG MCP server
3. THE Agent SHALL have access to `perform_rag_query()` tool for searching documentation
4. THE Tool SHALL support `source_type="dml"` for DML 1.4 documentation search
5. THE Tool SHALL support `source_type="python"` for Simics Python API documentation search
6. THE Tool SHALL support `source_type="docs"` for general Simics documentation search
7. THE Tool SHALL support `source_type="all"` for searching all available sources
8. THE Agent Instructions SHALL explain when and how to use the RAG tool
9. THE Agent SHALL gracefully handle cases where RAG MCP server is unavailable

### Requirement 12: Tool Reuse and Code Organization

**User Story:** As a maintainer, I want the Simics integration to reuse existing code where appropriate, so that the codebase remains maintainable and consistent.

#### Acceptance Criteria

1. THE Integration SHALL reuse the existing `openspec_tools.py` module for file operations
2. THE Integration SHALL create a new `simics_mcp_tools.py` module for Simics-specific tooling
3. THE Integration SHALL update `agent.py` to conditionally load Simics MCP tools
4. THE Integration SHALL follow the same error handling patterns as the base integration
5. THE Integration SHALL use the same model configuration approach as the base integration
6. THE Integration SHALL maintain clear separation between OpenSpec tools and Simics tools
