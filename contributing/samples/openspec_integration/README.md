# OpenSpec Integration for ADK

This sample demonstrates how to integrate [OpenSpec](https://github.com/Fission-AI/OpenSpec) with the Agent Development Kit (ADK) for spec-driven development. OpenSpec provides a lightweight workflow that aligns humans and AI coding assistants by establishing clear specifications before any code is written.

## Overview

### What is OpenSpec?

OpenSpec is an AI-native system for spec-driven development that helps teams:
- Agree on specifications before implementation
- Track changes explicitly through structured proposals
- Maintain a clear separation between current truth (specs) and proposed changes
- Archive completed work for auditable history

### Why Use OpenSpec with ADK?

Combining OpenSpec with ADK provides:
- **Structured Development**: Follow a proven workflow (proposal → review → implement → archive)
- **AI-Assisted Specification**: Let ADK agents help create and refine specifications
- **Explicit Change Tracking**: All updates are tracked as deltas (ADDED/MODIFIED/REMOVED)
- **Team Collaboration**: Multiple developers can work on different changes simultaneously

### Key Differences from spec-kit Integration

While both samples demonstrate spec-driven development, they serve different use cases:

**OpenSpec** (this sample):
- Two-folder model: `specs/` (truth) + `changes/` (proposals)
- Explicit delta format for tracking changes
- Archive workflow for completed changes
- Better for **brownfield/evolving projects** (1→n)
- Ideal when modifying existing behavior or touching multiple specs

**spec-kit**:
- Single folder per feature with all artifacts
- Phased workflow (constitution → specify → plan → tasks → implement)
- Better for **greenfield/0→1 projects**
- More prescriptive structure with detailed templates

## Prerequisites

### Required Software

1. **OpenSpec CLI** - Choose one installation method:

   **Option 1: TypeScript CLI** (requires Node.js >= 20.19.0)
   ```bash
   npm install -g @fission-ai/openspec@latest
   ```

   **Option 2: Python Port** (requires uv)
   ```bash
   # Install uv first
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # OpenSpec will be available via uvx
   uvx openspec --version
   ```

2. **ADK (Agent Development Kit)**
   ```bash
   # Clone the repository
   git clone https://github.com/google/adk-python.git
   cd adk-python
   
   # Create virtual environment and install
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

## Quick Start

### Using the Convenience Script

The easiest way to get started is using the `run_openspec.sh` script:

```bash
# Default mode - automatically helps populate project.md
./run_openspec.sh

# Custom project name (still uses default prompt to populate project.md)
./run_openspec.sh my_project

# Pure interactive mode without default prompt
./run_openspec.sh my_project --interactive

# Custom prompt instead of default
./run_openspec.sh my_project "Create a user authentication feature"

# Save session for later resuming
./run_openspec.sh my_project --save-session

# Interactive mode with session saving
./run_openspec.sh my_project --interactive --save-session

# Resume from saved session
./run_openspec.sh my_project --resume

# Use specific model
./run_openspec.sh my_project --model iflow/qwen3-coder-plus --save-session
```

**Default Behavior**: When no initial prompt is provided (and `--interactive` is not used), the script automatically sends:
> "Please read openspec/project.md and help me fill it out with details about my project, tech stack, and conventions"

This helps you establish project context before creating change proposals.

**Interactive Mode**: Use `--interactive` to skip the default prompt and start in pure interactive mode where you can type your own queries.

The script will:
1. Check for OpenSpec CLI and ADK installation
2. Initialize an OpenSpec project with the specified name
3. Create the OpenSpec directory structure
4. Launch the ADK agent in the project directory
5. Optionally save session for resuming later

### Manual Initialization

If you prefer manual setup:

```bash
# 1. Initialize OpenSpec project
openspec init my_project --tools none
cd my_project

# 2. Run ADK agent with OpenSpec integration
adk run ../contributing/samples/openspec_integration
```

### Expected Output

After initialization, your project will have this structure:

```
my_project/
├── AGENTS.md                    # Workflow instructions for AI agents
├── openspec/
│   ├── project.md              # Project context and conventions
│   ├── specs/                  # Current specifications (source of truth)
│   ├── changes/                # Active change proposals
│   │   └── archive/            # Archived (completed) changes
```

## OpenSpec Workflow

### 1. Create a Change Proposal

Start by asking the agent to create a change proposal:

```
You: I want to add user authentication with email/password login.
     Please create an OpenSpec change proposal for this feature.

Agent: I'll create an OpenSpec change proposal for user authentication.
       *Creates openspec/changes/add-user-auth/ with proposal.md, tasks.md, and spec deltas*
```

The agent will create:
- `proposal.md`: Explains why and what changes
- `tasks.md`: Implementation checklist
- `specs/<feature>/spec.md`: Spec deltas (ADDED/MODIFIED/REMOVED)

### 2. Review and Refine

Iterate on the specifications until they're clear:

```
You: Can you add acceptance criteria for password reset functionality?

Agent: I'll update the spec delta with password reset scenarios.
       *Edits openspec/changes/add-user-auth/specs/auth/spec.md*
```

Validate the specs:

```
You: Please validate the change proposal

Agent: *Runs: openspec validate add-user-auth*
       ✓ All specs are valid and properly formatted
```

### 3. Implement Tasks

Once specs are approved, start implementation:

```
You: The specs look good. Let's implement this change.

Agent: I'll work through the tasks in the add-user-auth change.
       *Implements tasks from openspec/changes/add-user-auth/tasks.md*
       *Marks tasks complete: Task 1.1 ✓, Task 1.2 ✓, Task 2.1 ✓...*
```

### 4. Archive Completed Changes

After implementation is complete:

```
You: Please archive the change

Agent: I'll archive the add-user-auth change.
       *Runs: openspec archive add-user-auth --yes*
       ✓ Change archived successfully. Specs updated. Ready for the next feature!
```

Or run the command yourself:
```bash
openspec archive add-user-auth --yes
```

## Agent Capabilities

### Understanding OpenSpec Structure

The agent understands the OpenSpec directory layout and can:
- Navigate between specs/ (truth) and changes/ (proposals)
- Identify active vs. archived changes
- Read and interpret AGENTS.md for project-specific conventions

### Reading and Interpreting Specs

The agent can:
- Parse spec deltas with ADDED, MODIFIED, REMOVED markers
- Understand requirement hierarchies and scenarios
- Validate spec formatting and structure
- Cross-reference requirements in tasks

### Executing OpenSpec Commands

The agent can execute OpenSpec CLI commands:
- `openspec list`: List active changes
- `openspec show <change>`: Display change details
- `openspec validate <change>`: Check spec formatting
- `openspec archive <change>`: Archive completed work

### Best Practices Guidance

The agent provides guidance on:
- When to create new change proposals vs. modifying existing ones
- How to write clear, testable requirements
- Proper use of spec delta markers
- Task breakdown and dependency management

## Examples

### Example 1: Creating a Simple Feature

```
You: Create a change proposal for adding a search feature to the product catalog

Agent: I'll create an OpenSpec change proposal for product search.

*Agent creates openspec/changes/add-product-search/ with:*
- proposal.md: Explains the need for search functionality
- tasks.md: Breaks down implementation into tasks
- specs/catalog/spec.md: Adds search requirements as ADDED deltas
```

### Example 2: Working with Spec Deltas

```markdown
# Delta for Catalog

## ADDED Requirements

### Requirement: Product Search
The system SHALL provide search functionality for the product catalog.

#### Scenario: Search by keyword
- WHEN a user enters a search keyword
- THEN the system SHALL return matching products
- AND results SHALL be ranked by relevance

#### Scenario: Empty search results
- WHEN a search returns no results
- THEN the system SHALL display a helpful message
- AND suggest alternative search terms
```

### Example 3: Managing Multiple Changes

```
You: List all active changes

Agent: *Runs: openspec list*

Active changes:
- add-product-search (3 tasks, 2 specs)
- improve-checkout-flow (5 tasks, 1 spec)
- add-user-reviews (8 tasks, 3 specs)
```

### Example 4: Archiving Workflow

```
You: Show me the details of the add-product-search change

Agent: *Runs: openspec show add-product-search*

Change: add-product-search
Proposal: Add search functionality to product catalog
Tasks: 3 total (3 completed)
Spec Deltas:
  - catalog/spec.md (2 ADDED requirements)

You: Archive this change

Agent: *Runs: openspec archive add-product-search --yes*
✓ Archived to openspec/changes/archive/add-product-search
✓ Updated openspec/specs/catalog/spec.md with new requirements
```

## Troubleshooting

### OpenSpec CLI Not Found

**Error**: `OpenSpec CLI not found`

**Solution**:
1. Install OpenSpec using one of the methods in [Prerequisites](#prerequisites)
2. Verify installation:
   ```bash
   openspec --version  # TypeScript CLI
   # or
   uvx openspec --version  # Python port
   ```
3. Ensure the CLI is in your PATH

### ADK Virtual Environment Not Found

**Error**: `ADK virtual environment not found at .venv`

**Solution**:
1. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install ADK:
   ```bash
   pip install -e .
   ```

### Directory Structure Problems

**Error**: `AGENTS.md not found` or `Invalid openspec/ structure`

**Solution**:
1. Ensure you're in a directory initialized with OpenSpec:
   ```bash
   ls -la  # Should show AGENTS.md and openspec/ directory
   ```
2. If not initialized, run:
   ```bash
   openspec init .
   ```

### Agent Confusion About Workflow

**Issue**: Agent doesn't understand OpenSpec commands or workflow

**Solution**:
1. Ensure the agent reads AGENTS.md first:
   ```
   You: Please read the AGENTS.md file and explain the OpenSpec workflow
   ```
2. Provide explicit instructions:
   ```
   You: Follow the OpenSpec workflow: proposal → review → implement → archive
   ```
3. Reference specific OpenSpec commands:
   ```
   You: Run 'openspec list' to show active changes
   ```

## Advanced Usage

### Custom Model Configuration

Override the default model using the `--model` flag:

```bash
./run_openspec.sh my_project --model iflow/qwen3-coder-plus
./run_openspec.sh my_project --model github_copilot/claude-sonnet-4
```

Or use an environment variable:

```bash
export OPENSPEC_MODEL="gemini-2.0-flash-exp"
./run_openspec.sh my_project
```

### Session Management

Save and resume your work sessions:

```bash
# Save session while working
./run_openspec.sh my_project --save-session

# Resume from saved session
./run_openspec.sh my_project --resume

# Resume with different model
./run_openspec.sh my_project --resume --model github_copilot/claude-sonnet-4
```

Session files are saved in:
- `adk_openspec_agent/PROJECT_NAME_openspec.session.json` - Raw session data
- `adk_openspec_agent/PROJECT_NAME_openspec.session.txt` - Human-readable dump

### Integration with CI/CD

Use OpenSpec validation in your CI pipeline:

```yaml
# .github/workflows/validate-specs.yml
name: Validate OpenSpec Changes

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install OpenSpec
        run: npm install -g @fission-ai/openspec@latest
      - name: Validate all changes
        run: |
          for change in openspec/changes/*/; do
            openspec validate $(basename $change)
          done
```

### Team Collaboration Patterns

**Pattern 1: Feature Branches**
```bash
# Developer A works on authentication
git checkout -b feature/auth
openspec init . --tools none
# Create change proposal for auth
# Implement and archive

# Developer B works on search (different branch)
git checkout -b feature/search
openspec init . --tools none
# Create change proposal for search
# Implement and archive
```

**Pattern 2: Shared Specs**
```bash
# Team maintains shared specs in main branch
# Developers create change proposals in feature branches
# After review, changes are archived and merged to main
```

**Pattern 3: Spec Review Process**
```bash
# 1. Create change proposal
openspec init my-feature

# 2. Push for review
git add openspec/changes/my-feature
git commit -m "feat: add my-feature spec proposal"
git push origin feature/my-feature

# 3. Team reviews spec deltas in PR
# 4. After approval, implement and archive
# 5. Merge to main with updated specs
```

## Simics Hardware Device Modeling

The OpenSpec integration supports hardware device modeling using Simics and DML 1.4.

### Prerequisites for Simics Projects

1. **Simics Installation**: Valid Simics 7.x installation (required)
2. **DML Version**: DML 1.4 language support (required)
3. **Simics MCP Server**: Running on `http://127.0.0.1:8051/sse`
4. **Python Environment**: Same environment used for ADK

### Simics MCP Server Setup

The Simics MCP server must be running before using hardware device features.

**Start the Server:**
```bash
# Assuming simics-mcp-server is in a sibling directory or accessible
cd path/to/simics-mcp-server
python src/simics_mcp_server/server.py --transport sse --port 8051
```

**Verify Connection:**
The agent will automatically attempt to connect when started. You'll see:
```
✓ Simics MCP tools loaded successfully (includes RAG documentation search)
```

If the server is not available:
```
ℹ Simics MCP tools not available: [connection error]
  (Software projects will work normally)
```

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

#### 4. Using RAG Documentation Search

During implementation, use the RAG tool to search Simics documentation:

```
You: How do I define a register in DML 1.4?

Agent: Let me search the DML documentation for you.
       *Uses: perform_rag_query("register definition syntax", source_type="dml")*
       
       In DML 1.4, you define registers using the `register` keyword...
```

```
You: How do I implement a read callback for a register?

Agent: *Uses: perform_rag_query("register read callback", source_type="dml")*
       
       You can implement a read callback using the `read` method...
```

#### 5. Archive Completed Device

```
You: The watchdog timer device is complete and tested. Please archive the change.

Agent: I'll archive the add-watchdog-timer change.
       *Runs: openspec archive add-watchdog-timer --yes*
       ✓ Device implementation archived
       ✓ Specs updated in openspec/specs/watchdog-timer/
       ✓ Ready for the next hardware device!
```

### Simics Project Structure

Hardware device projects follow the standard Simics structure:

```
project_root/
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

### Troubleshooting Simics Integration

**Issue**: Simics MCP tools not available

**Solution**:
1. Verify Simics 7.x is installed and in PATH
2. Check that Simics MCP server is running on port 8051
3. Ensure Python environment has required dependencies
4. Software projects will work normally without Simics tools

**Issue**: Device build fails

**Solution**:
1. Check DML syntax errors in device files
2. Verify register definitions match specification
3. Use `build_simics_project()` to see detailed error messages
4. Use `perform_rag_query(source_type="dml")` to search for DML syntax examples

**Issue**: Tests fail

**Solution**:
1. Verify test expectations match device behavior
2. Check register read/write operations
3. Use Simics logging to debug device behavior
4. Run individual test suites to isolate issues

**Issue**: Simics 7.x or DML 1.4 not available

**Solution**:
1. Simics 7.x is required (not optional) for hardware device modeling
2. DML 1.4 is required (not optional) - DML 1.2 is not supported
3. Verify Simics version using `get_simics_version()` tool
4. Upgrade Simics installation if using older version

### RAG Documentation Search

The Simics MCP server provides RAG (Retrieval-Augmented Generation) documentation search:

**Search DML Documentation:**
```python
perform_rag_query("register definition syntax", source_type="dml")
```

**Search Python API Documentation:**
```python
perform_rag_query("create simulation object", source_type="python")
```

**Search General Simics Documentation:**
```python
perform_rag_query("checkpoint management", source_type="docs")
```

**Search All Sources:**
```python
perform_rag_query("device modeling best practices", source_type="all")
```

## Related Resources

- [OpenSpec Documentation](https://github.com/Fission-AI/OpenSpec)
- [ADK Documentation](https://github.com/google/adk-python)
- [spec-kit Integration](../spec_kit_integration/) - Alternative approach for greenfield projects
- [AGENTS.md Convention](https://agents.md/) - Universal AI agent instructions
- [Simics Documentation](https://www.intel.com/content/www/us/en/developer/articles/tool/simics-simulator.html) - Intel Simics simulator

## License

This sample is part of the ADK project and is licensed under the Apache License 2.0.
