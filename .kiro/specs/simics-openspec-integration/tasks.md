# Implementation Plan

## 1. Reuse Simics MCP Tools from spec-kit Integration

- [ ] 1.1 Review existing Simics MCP toolset in spec_kit_integration
  - Read `contributing/samples/spec_kit_integration/spec_kit_tools.py`
  - Identify `create_simics_mcp_toolset()` function implementation
  - Verify it uses SSE connection on port 8051
  - Understand error handling approach
  - _Requirements: 1.1, 1.2, 1.3, 12.1_

- [ ] 1.2 Create `simics_mcp_tools.py` in openspec_integration directory
  - Import or copy `create_simics_mcp_toolset()` from spec_kit_integration
  - Ensure SSE connection uses `http://127.0.0.1:8051/sse`
  - Maintain same timeout configuration (10s connection, 300s read)
  - Add docstring explaining Simics MCP integration for OpenSpec
  - Add reference to spec_kit_integration as source
  - _Requirements: 1.1, 1.2, 1.3, 12.1, 12.6_

- [ ] 1.3 Verify error handling for Simics MCP server unavailability
  - Ensure clear exception is raised if connection fails
  - Include helpful error message with server setup instructions
  - Test graceful fallback behavior
  - _Requirements: 1.9_

## 2. Verify RAG Tool Integration

- [ ] 2.1 Verify RAG tool is included in Simics MCP toolset
  - Confirm `perform_rag_query` is in the tool_filter list in spec_kit_integration
  - Understand that RAG and Simics tools come from same MCP server (port 8051)
  - Note: No separate rag_tools.py needed - RAG is part of Simics MCP toolset
  - _Requirements: 11.1, 11.2, 11.3_

- [ ] 2.2 Update design documentation to reflect unified MCP server
  - Clarify that Simics MCP server provides both Simics tools AND RAG tools
  - Remove references to separate RAG MCP server on port 8050
  - Update architecture diagrams to show single MCP server
  - _Requirements: 11.1, 11.2_

## 3. Enhance OpenSpec Agent with Hardware Detection

- [ ] 3.1 Add hardware detection function to `agent.py`
  - Implement `detect_hardware_project(text: str) -> bool` function
  - Include hardware keywords: processor, CPU, GPU, FPGA, microcontroller, embedded
  - Include simulation keywords: simulation, modeling, hardware validation, device model
  - Include architecture keywords: x86, ARM, RISC-V, MIPS, SPARC
  - Include component keywords: PCI, USB, memory controller, peripheral, watchdog timer
  - Include development keywords: firmware, BIOS, bootloader, DML, register map
  - Use case-insensitive matching
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

## 4. Update Agent System Instructions

- [ ] 4.1 Add Simics hardware modeling section to agent instruction
  - Explain Simics 7.x and DML 1.4 requirements (mandatory)
  - Describe Simics project structure with modules/ directory
  - List available Simics MCP tools with descriptions
  - Explain hardware device workflow (research → spec → setup → TDD → implement → validate)
  - Include DML 1.4 best practices
  - Emphasize software-visible behavior focus
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 10.1, 10.2, 10.3, 10.4_

- [ ] 4.2 Add RAG documentation search section to agent instruction
  - Explain `perform_rag_query()` tool and its parameters
  - Describe source_type options: dml, python, docs, all
  - Provide examples of when to use RAG tool
  - Explain how to use RAG during research and implementation phases
  - _Requirements: 11.4, 11.5, 11.6, 11.7, 11.8_

- [ ] 4.3 Update tool availability section in agent instruction
  - List file operations tools
  - List Simics MCP tools (for hardware projects)
  - List RAG documentation search tools (for hardware projects)
  - Explain graceful degradation when tools unavailable
  - _Requirements: 3.4_

## 5. Implement Tool Loading Logic in Agent

- [ ] 5.1 Update `OpenSpecAgent.__init__()` to load Simics MCP tools
  - Import `create_simics_mcp_toolset` from simics_mcp_tools
  - Wrap in try-except for graceful fallback
  - Print success message mentioning both Simics and RAG tools when loaded
  - Print informational message when tools unavailable
  - Note: Single toolset provides BOTH Simics tools AND RAG documentation search
  - _Requirements: 1.1, 1.9, 11.1, 11.9_

- [ ] 5.2 Update agent description to mention hardware support
  - Change description to "OpenSpec agent for spec-driven development (software and hardware)"
  - _Requirements: 3.1_

## 6. Verify and Document Server Startup Scripts

- [ ] 6.1 Verify existing server startup scripts in simics-mcp-server repo
  - Confirm start script exists and works with SSE transport on port 8051
  - Confirm stop script exists and properly shuts down server
  - Test scripts to ensure they work correctly
  - Note: These scripts already exist in simics-mcp-server repo
  - _Requirements: 7.2, 7.4_

- [ ] 6.2 Create convenience wrapper scripts in openspec_integration (optional)
  - Create `start_simics_mcp_server.sh` that calls simics-mcp-server's start script
  - Create `stop_simics_mcp_server.sh` that calls simics-mcp-server's stop script
  - Add path resolution to locate simics-mcp-server directory
  - Only needed if simpler interface is desired
  - _Requirements: 7.2_

## 7. Enhance README Documentation

- [ ] 7.1 Add "Simics Hardware Device Modeling" section to README
  - Explain Simics 7.x and DML 1.4 requirements
  - List prerequisites for Simics projects
  - Provide Simics workflow example with watchdog timer
  - Show example change proposal for hardware device
  - Show example spec delta with register map
  - Show example tasks with Simics MCP tool calls
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 10.1, 10.2, 10.7_

- [ ] 7.2 Add "RAG Documentation Search" subsection
  - Explain perform_rag_query tool and source types
  - Provide examples of searching DML documentation
  - Provide examples of searching Python API documentation
  - Show how to use RAG during implementation
  - _Requirements: 6.3, 11.4, 11.5, 11.6, 11.7_

- [ ] 7.3 Add "Simics MCP Server Setup" subsection
  - Explain how to start Simics MCP server
  - Clarify that this server provides BOTH Simics tools AND RAG documentation search
  - Provide server startup commands
  - Reference startup scripts
  - Explain port configuration (8051)
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 7.5 Add "Troubleshooting Simics Integration" subsection
  - Document "Simics MCP tools not available" issue and solution
  - Document "Device build fails" issue and solution
  - Document "Tests fail" issue and solution
  - Document version requirement issues (Simics 7.x, DML 1.4)
  - _Requirements: 6.5, 7.5, 7.6, 10.6_

## 8. Create Example Watchdog Timer Workflow Documentation

- [ ] 8.1 Document complete watchdog timer example in README
  - Show initial change proposal creation
  - Show hardware specification with register map
  - Show spec delta format for hardware requirements
  - Show task list with Simics MCP tool calls
  - Show implementation workflow steps
  - Show validation and testing steps
  - Show archiving completed change
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ] 8.2 Include RAG usage in watchdog timer example
  - Show using perform_rag_query for DML syntax
  - Show using perform_rag_query for register implementation patterns
  - Show using perform_rag_query for testing examples
  - _Requirements: 8.3, 8.5_

## 9. Ensure Compatibility and Non-Breaking Changes

- [ ] 9.1 Verify software projects work without Simics tools
  - Test creating software change proposal
  - Verify no Simics tools are used
  - Verify normal OpenSpec workflow continues
  - _Requirements: 9.1, 9.2, 9.3_

- [ ] 9.2 Verify hardware projects work with Simics tools
  - Test creating hardware device change proposal
  - Verify hardware detection triggers
  - Verify Simics MCP tools are available
  - Verify RAG tools are available
  - _Requirements: 9.1, 9.6_

- [ ] 9.3 Verify MCP server requirement for hardware projects
  - Test agent startup without Simics MCP server running
  - Verify clear error message is displayed for hardware projects
  - Verify software projects still work without MCP server
  - Document that MCP server is REQUIRED for hardware device modeling
  - Document that MCP server is OPTIONAL for software projects
  - _Requirements: 1.9, 11.9_

- [ ] 9.4 Verify no interference with other ADK samples
  - Check that openspec_integration changes don't affect spec_kit_integration
  - Check that openspec_integration changes don't affect other samples
  - Verify ADK conventions are followed
  - _Requirements: 9.4, 9.5_

## 10. Testing and Validation

- [ ] 10.1 Create unit tests for simics_mcp_tools.py
  - Test toolset creation with valid server
  - Test error handling when server unavailable
  - Test connection parameters are correct
  - _Requirements: 1.1, 1.2, 1.3, 1.9_

- [ ] 10.2 Create unit tests for RAG tool availability
  - Test that perform_rag_query is available in Simics MCP toolset
  - Test RAG query with different source_type parameters
  - Test error handling when server unavailable
  - _Requirements: 11.1, 11.2, 11.3, 11.9_

- [ ] 10.3 Create unit tests for hardware detection
  - Test detection with various hardware keywords
  - Test detection with software keywords (should return false)
  - Test case-insensitive matching
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 10.4 Create integration test for software project workflow
  - Initialize OpenSpec project
  - Create software change proposal
  - Verify no Simics tools used
  - Verify normal workflow completes
  - _Requirements: 9.1, 9.2_

- [ ] 10.5 Create integration test for hardware project workflow
  - Initialize OpenSpec project
  - Create hardware device change proposal (e.g., watchdog timer)
  - Verify hardware detection works
  - Verify Simics MCP tools are suggested in tasks
  - Verify RAG tools are suggested for research
  - Verify Simics project structure in design
  - _Requirements: 2.7, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 10.6 Create end-to-end test with MCP server
  - Start Simics MCP server (provides both Simics and RAG tools)
  - Create hardware device change proposal
  - Verify tools are loaded successfully
  - Verify perform_rag_query works
  - Verify Simics MCP tools work
  - Stop MCP server
  - _Requirements: 1.4, 1.5, 1.6, 1.7, 1.8, 11.3, 11.4, 11.5, 11.6, 11.7_

## 11. Code Quality and Documentation

- [ ] 11.1 Add docstrings to all new functions
  - Document simics_mcp_tools.py functions
  - Document hardware detection function
  - Follow Google Python style guide
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [ ] 11.2 Add inline comments for complex logic
  - Comment hardware keyword lists
  - Comment tool loading try-except blocks
  - Comment connection parameter configurations
  - _Requirements: 12.4_

- [ ] 11.3 Update type hints for all functions
  - Add return type hints
  - Add parameter type hints
  - Use proper imports from typing module
  - _Requirements: 12.4_

- [ ] 11.4 Run linting and formatting
  - Run pylint on new modules
  - Run black formatter
  - Fix any style issues
  - _Requirements: 12.4_

## 12. Final Integration and Verification

- [ ] 12.1 Test complete workflow end-to-end
  - Start Simics MCP server (provides both Simics and RAG tools)
  - Run run_openspec.sh script
  - Create hardware device change proposal
  - Verify all tools available (Simics + RAG)
  - Create software change proposal
  - Verify appropriate tools used
  - Stop MCP server
  - _Requirements: 9.1, 9.2, 9.3, 9.6_

- [ ] 12.2 Verify documentation completeness
  - Check README has all required sections
  - Verify examples are accurate and tested
  - Check troubleshooting covers common issues
  - Verify links and references are valid
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ] 12.3 Create summary documentation
  - Document what was added to openspec_integration
  - Explain benefits of Simics integration
  - Provide quick start guide for hardware developers
  - Reference related samples (spec_kit_integration)
  - _Requirements: 6.1, 6.2, 6.7_

- [ ] 12.4 Update main ADK documentation
  - Add openspec_integration with Simics to samples list
  - Update AGENTS.md or CONTRIBUTING.md if needed
  - Reference Simics hardware modeling capabilities
  - _Requirements: 9.4, 9.5_
