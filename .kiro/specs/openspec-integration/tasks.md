# Implementation Plan

## 1. Create OpenSpec Integration Sample Directory Structure

- [ ] 1.1 Create `contributing/samples/openspec_integration/` directory
  - Create the base directory for the OpenSpec integration sample
  - _Requirements: 2.1_

- [ ] 1.2 Create `__init__.py` file in openspec_integration directory
  - Add empty `__init__.py` to make it a Python package
  - _Requirements: 2.2_

## 2. Implement OpenSpec Tools Module

- [ ] 2.1 Create `openspec_tools.py` with tool wrapper function
  - Import `create_spec_kit_toolset` from spec_kit_integration
  - Implement `create_openspec_toolset()` function that returns the spec_kit toolset
  - Add docstring explaining tool reuse strategy
  - _Requirements: 4.1, 4.2, 4.3_

## 3. Implement OpenSpec Root Agent

- [ ] 3.1 Create `agent.py` with OpenSpecAgent class
  - Define `OpenSpecAgent` class inheriting from `LlmAgent`
  - Implement `__init__` method with OpenSpec-specific system instruction
  - Include OpenSpec workflow explanation in instruction
  - Include OpenSpec directory structure explanation in instruction
  - Include OpenSpec command reference in instruction
  - Include best practices guidance in instruction
  - Load tools using `create_openspec_toolset()`
  - _Requirements: 2.2, 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 3.2 Add model configuration helper function
  - Implement `get_openspec_model()` function
  - Read from `OPENSPEC_MODEL` environment variable
  - Default to `iflow/Qwen3-Coder` if not set
  - _Requirements: 2.2_

- [ ] 3.3 Create root_agent instance
  - Instantiate `OpenSpecAgent` as `root_agent`
  - Export `root_agent` for ADK to discover
  - _Requirements: 2.2_

## 4. Create run_openspec.sh Script

- [ ] 4.1 Create `run_openspec.sh` at repository root
  - Add shebang and script header with usage documentation
  - Add color definitions for output formatting
  - _Requirements: 1.1, 1.7_

- [ ] 4.2 Implement prerequisite checks
  - Check for OpenSpec CLI (TypeScript) or uvx (Python port)
  - Check for ADK virtual environment at `.venv`
  - Check for openspec_integration directory
  - Display helpful error messages with installation instructions
  - Exit with code 1 if prerequisites not met
  - _Requirements: 1.6, 4.4, 4.5_

- [ ] 4.3 Implement project initialization logic
  - Parse command-line arguments for project name and initial prompt
  - Default project name to `adk_openspec_project` if not provided
  - Remove existing project directory if it exists (with warning)
  - Execute `openspec init <project_name> --tools adk` command
  - Handle both TypeScript CLI and Python port (uvx) execution
  - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.8_

- [ ] 4.4 Implement ADK agent execution
  - Change to project directory after initialization
  - Run ADK agent with openspec_integration path
  - Support interactive mode (no initial prompt)
  - Support non-interactive mode (with initial prompt piped to agent)
  - _Requirements: 1.7, 1.8_

- [ ] 4.5 Make script executable
  - Set executable permissions on `run_openspec.sh`
  - Test script execution with both modes
  - _Requirements: 1.1_

## 5. Create Comprehensive Documentation

- [ ] 5.1 Create README.md with overview section
  - Explain what OpenSpec is and its purpose
  - Explain why use OpenSpec with ADK
  - Highlight key differences from spec-kit integration
  - _Requirements: 5.1, 5.2_

- [ ] 5.2 Document prerequisites and installation
  - List OpenSpec CLI installation options (TypeScript and Python)
  - List ADK installation requirements
  - List Python version requirements
  - Provide installation commands for each prerequisite
  - _Requirements: 5.1, 5.5_

- [ ] 5.3 Document quick start guide
  - Explain how to use `run_openspec.sh` script
  - Provide example commands for both interactive and non-interactive modes
  - Show expected output and directory structure after initialization
  - _Requirements: 5.1, 5.2_

- [ ] 5.4 Document OpenSpec workflow
  - Explain the proposal → review → implement → archive workflow
  - Provide examples of creating change proposals
  - Provide examples of reviewing and iterating on specs
  - Provide examples of implementing tasks
  - Provide examples of archiving completed changes
  - _Requirements: 5.2, 5.3_

- [ ] 5.5 Document agent capabilities
  - Explain how the agent understands OpenSpec structure
  - Explain how the agent reads and interprets specs
  - Explain how the agent executes OpenSpec commands
  - Provide best practices for working with the agent
  - _Requirements: 5.2, 5.3_

- [ ] 5.6 Add troubleshooting section
  - Document common issues and solutions
  - Add guidance for "OpenSpec CLI not found" error
  - Add guidance for directory structure problems
  - Add guidance for agent confusion about workflow
  - _Requirements: 5.1, 5.4_

- [ ] 5.7 Add advanced usage section
  - Document custom model configuration via environment variable
  - Provide examples of integration patterns
  - Suggest team collaboration workflows
  - _Requirements: 5.1_

## 6. Ensure Compatibility and Integration

- [ ] 6.1 Verify imports and dependencies
  - Test that openspec_tools.py correctly imports from spec_kit_integration
  - Test that agent.py correctly imports ADK components
  - Verify no circular dependencies exist
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 6.2 Test with ADK framework
  - Run `adk run contributing/samples/openspec_integration` to verify agent loads
  - Test that agent responds to basic queries
  - Test that agent can read files using tools
  - Test that agent can execute bash commands using tools
  - _Requirements: 6.2, 6.4, 6.5_

- [ ] 6.3 Verify non-interference with other samples
  - Ensure openspec_integration doesn't modify spec_kit_integration
  - Ensure openspec_integration doesn't modify other samples
  - Verify sample follows ADK conventions
  - _Requirements: 6.1, 6.2, 6.3_

## 7. End-to-End Testing

- [ ] 7.1 Test complete workflow with TypeScript CLI
  - Run `./run_openspec.sh test_project_ts` to initialize project
  - Verify openspec directory structure is created correctly
  - Verify AGENTS.md file is created
  - Verify agent starts and responds to queries
  - Test creating a simple change proposal via agent
  - Test reading and validating specs via agent
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 7.2 Test complete workflow with Python port
  - Run `./run_openspec.sh test_project_py` with Python port
  - Verify identical directory structure is created
  - Verify agent behavior is consistent with TypeScript CLI
  - _Requirements: 1.6_

- [ ] 7.3 Test non-interactive mode
  - Run `./run_openspec.sh test_project_prompt "Create a user authentication feature"`
  - Verify agent receives and processes the initial prompt
  - Verify agent creates appropriate OpenSpec artifacts
  - _Requirements: 1.8_

- [ ] 7.4 Test error handling
  - Test script behavior when OpenSpec CLI is not installed
  - Test script behavior when ADK venv is not found
  - Test agent behavior when AGENTS.md is missing
  - Verify error messages are clear and actionable
  - _Requirements: 4.4, 4.5_

## 8. Documentation Review and Polish

- [ ] 8.1 Review README.md for completeness
  - Verify all sections are present and accurate
  - Check for typos and formatting issues
  - Ensure code examples are correct and tested
  - Verify links and references are valid
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 8.2 Review agent system instruction
  - Verify instruction is clear and comprehensive
  - Check that all OpenSpec concepts are explained
  - Ensure workflow steps are accurate
  - Verify command examples are correct
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8.3 Add inline code comments
  - Add docstrings to all functions and classes
  - Add comments explaining non-obvious logic
  - Follow Google Python style guide for comments
  - _Requirements: 2.2, 3.1_

- [ ] 8.4 Update repository-level documentation
  - Add openspec_integration to samples list in main README (if applicable)
  - Update AGENTS.md or CONTRIBUTING.md to mention OpenSpec integration
  - _Requirements: 6.1_
