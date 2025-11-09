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
# Interactive mode (default project name: adk_openspec_project)
./run_openspec.sh

# Custom project name
./run_openspec.sh my_project

# Non-interactive mode with initial prompt
./run_openspec.sh my_project "Create a user authentication feature"
```

The script will:
1. Check for OpenSpec CLI and ADK installation
2. Initialize an OpenSpec project with the specified name
3. Create the OpenSpec directory structure
4. Launch the ADK agent in the project directory

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

Override the default model using an environment variable:

```bash
export OPENSPEC_MODEL="gemini-2.0-flash-exp"
./run_openspec.sh my_project
```

Or set it in your shell profile for persistence:

```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENSPEC_MODEL="gemini-2.0-flash-exp"
```

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

## Related Resources

- [OpenSpec Documentation](https://github.com/Fission-AI/OpenSpec)
- [ADK Documentation](https://github.com/google/adk-python)
- [spec-kit Integration](../spec_kit_integration/) - Alternative approach for greenfield projects
- [AGENTS.md Convention](https://agents.md/) - Universal AI agent instructions

## License

This sample is part of the ADK project and is licensed under the Apache License 2.0.
