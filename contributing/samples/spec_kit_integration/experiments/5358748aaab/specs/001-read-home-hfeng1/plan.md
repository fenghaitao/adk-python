---
description: "Implementation plan template for feature development"
---

# Implementation Plan: Simics Watchdog Timer Model

**Branch**: `001-read-home-hfeng1` | **Date**: 2024-12-19 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-read-home-hfeng1/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api, simics=hardware device)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code, `ADK.md` for adk, or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
This plan outlines the development of a Simics watchdog timer model, a hardware device that monitors system health and triggers interrupts or resets when the system fails to respond within a specified time interval. The technical approach involves creating a DML 1.4 device model with memory-mapped registers that implement the specified watchdog functionality.

## Technical Context
**Language/Version**: DML 1.4
**Primary Dependencies**: Simics API
**Storage**: N/A
**Testing**: Simics test scripts
**Target Platform**: Simics 7.57.0
**Project Type**: simics
**Performance Goals**: Functional accuracy
**Constraints**: Software-visible behavior
**Scale/Scope**: Register complexity with 15+ registers

**Simics-Specific Context** (if Project Type = simics):
**Simics Version**: 7.57.0
**Required Packages**: Simics-Base 7.57.0, QSP-x86 7.38.0, and related packages
**Available Platforms**: QSP-x86 (qsp-x86-public-7)
**MCP Server**: simics-mcp-server integration available with 22+ tools for project automation, device modeling and documentation access
**Device Type**: Peripheral watchdog timer controller
**Hardware Interfaces**: Memory-mapped registers, interrupts, reset signals

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Based on the Simics Model Development Constitution:

1. **Device-First Development** ✅ - The watchdog timer will be implemented as a standalone DML device model
2. **Interface-First Architecture** ✅ - Register map and external interfaces are clearly defined in the specification
3. **Test-First Development** ✅ - Test scenarios are defined in the feature specification, and we'll implement TDD approach
4. **Specification-Driven Implementation** ✅ - Implementation will strictly follow the hardware specification provided
5. **Integration Testing Focus** ✅ - The model will be designed for integration with other Simics components
6. **Observability and Transparency** ✅ - All device states will be inspectable through Simics debugging capabilities
7. **Versioning and Evolution** ✅ - Will follow MAJOR.MINOR.BUILD versioning format
8. **Simplicity and Incremental Development** ✅ - Will start with basic functionality and add complexity only when needed
9. **Simics Excellence** ✅ - Will follow DML coding standards and Simics best practices

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

## Repository Structure
repo-root/
├── simics-project/              # ← Source code (implementation)
│   └── modules/device-name/
│       ├── device-name.dml      # Main device implementation
│       ├── registers.dml        # Register definitions and mappings (optional)
│       ├── interfaces.dml       # Device interface implementations (optional)
│       ├── sub-feature.dml      # Device sub-feature modules (optional)
│       ├── module_load.py       # Simics module load action definitions
│       ├── CMakeLists.txt       # CMake file
│       └── test/
│           ├── CMakeLists.txt   # CMake file
│           ├── SUITEINFO        # Test timeout and tags
│           ├── s-device-name.py # tests implementation
│           ├── test_name_common.py # test configuration and device instance creation
│           └── README
│
└── specs/                       # ← Documentation artifacts only
    └── [###-feature-name]/
        ├── plan.md              # This file (/plan command output)
        ├── research.md          # Phase 0 output (/plan command)
        ├── data-model.md        # Phase 1 output (/plan command)
        ├── quickstart.md        # Phase 1 output (/plan command)
        ├── contracts/           # Phase 1 output (/plan command)
        └── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)

**Structure Decision**: Simics device project structure will be created using MCP tools during Phase 3.1 Setup.

**For Simics projects**: The structure above shows the template that will be generated AT REPOSITORY ROOT (not in specs/ folder). The actual project structure will be created by the simics-mcp-server's MCP tools during task execution (Phase 3.1 Setup):
- `create_simics_project(project_path="./simics-project")` creates the base project structure at repo root
- `add_dml_device_skeleton(project_path="./simics-project", device_name=DEVICE_NAME)` adds device-specific modeling files

**IMPORTANT**: Simics projects must be created at repository root to separate source code from documentation. The specs/ folder contains only documentation artifacts (plan.md, tasks.md, etc.), while the simics-project/ folder at repo root contains the actual implementation.

## Phase 0: Outline & Research

### Step 0.1: Identify Research Needs
Extract unknowns from Technical Context above:
- None remaining - all technical context has been resolved

### Step 0.2: Execute Discovery MCP Tools (Simics Projects)

**MANDATORY for Simics projects - Execute these tools immediately**:

1. **Environment Discovery** (MANDATORY):
   - Execute `get_simics_version()` → resolve Simics Version NEEDS CLARIFICATION
   - Execute `list_installed_packages()` → resolve Required Packages NEEDS CLARIFICATION
   - Execute `list_simics_platforms()` → resolve Available Platforms NEEDS CLARIFICATION

2. **Documentation Access via RAG** (MANDATORY):
   - Execute `perform_rag_query("DML 1.4 reference manual register and device modeling", source_type="docs", match_count=5)` → get DML 1.4 language reference excerpts
   - Execute `perform_rag_query("Simics Model Builder device creation and structure patterns", source_type="docs", match_count=5)` → get device modeling patterns
   - Execute `perform_rag_query("DML device template base structure and skeleton", source_type="dml", match_count=5)` → get base device structure patterns

3. **Device Example Analysis via RAG** (MANDATORY - use RAG queries for targeted examples):
   - Execute `perform_rag_query("Best practices for watchdog timer device modeling with Simics DML 1.4", source_type="source", match_count=5)` → get device-specific patterns and best practices
   - Execute `perform_rag_query("Simics device implementation example watchdog timer or similar peripheral", source_type="source", match_count=5)` → get Simics device patterns as reference
   - Execute `perform_rag_query("DML register bank implementation patterns", source_type="dml", match_count=5)` → get register implementation patterns and best practices

4. **Test Example Analysis via RAG** (MANDATORY - use RAG queries for test patterns):
   - Execute `perform_rag_query("Simics Python test patterns and examples", source_type="python", match_count=5)` → get Python test case patterns and structures
   - Execute `perform_rag_query("Simics device testing best practices", source_type="source", match_count=5)` → get device testing approaches and validation strategies

5. **Additional RAG Documentation Search** (recommended - query knowledge gaps):
   - **Review Functional Requirements**: Examine the "Functional Requirements" section in the feature spec (`specs/[###-feature-name]/spec.md`)
   - **Identify Knowledge Gaps**: For each functional requirement, determine what knowledge is NOT covered by the 8 mandatory queries above
   - **Execute Targeted Queries**: Use `perform_rag_query(query, source_type, match_count)` for each knowledge gap:
     * **Requirement-Specific Queries**: Query for specific hardware features, interfaces, or behaviors mentioned in requirements
     * **Pattern Queries**: Search for implementation patterns for specific device capabilities (e.g., "DMA implementation patterns", "interrupt handling in DML")
     * **Integration Queries**: Search for examples of devices with similar integration requirements (e.g., "PCI device configuration space", "memory-mapped I/O patterns")
   - **Source Type Selection**:
     * `source_type="dml"` for DML device modeling examples specific to requirements
     * `source_type="python"` for Python test case patterns for specific behaviors
     * `source_type="source"` for combined DML and test examples
     * `source_type="docs"` for general Simics documentation on specific topics
     * `source_type="all"` for comprehensive search across all sources
   - **Best Practices**: Use `match_count=5` for focused results; increase to 10 for complex requirements
   - **Document Rationale**: In research.md, document why each additional query was needed and which requirement(s) it addresses

**CRITICAL**: DO NOT execute implementation tools (`create_simics_project()`, `add_dml_device_skeleton()`, `build_simics_project()`) - those belong in Phase 3 (Implementation).

### Step 0.3: Parse MCP Tool and RAG Query Outputs

Extract key information from MCP tool JSON and RAG query responses:
- **get_simics_version()** → Extract Simics version for Technical Context
- **list_installed_packages()** → Extract package list for Technical Context
- **list_simics_platforms()** → Extract platform list for Technical Context
- **RAG queries for documentation** → Extract key patterns, best practices, and reference information
- **RAG queries for device examples** → Extract pattern insights, code structures, and architecture approaches
  * **CRITICAL**: Extract and include actual code examples from RAG results:
    - Parse the JSON response `results[].content` field to locate code snippets
    - Look for code patterns: lines containing `dml 1.4;`, `device`, `bank`, `register`, `field`, `method`, etc.
    - Extract 10-20 lines of actual DML code per example (not just descriptions)
    - Format as markdown code blocks with ```dml fencing
    - Example: If RAG returns "device contraption; bank regs { register r0 ... }", extract and format it as a proper code block
    - DO NOT write descriptions like "Sample timer device with counter" - show the actual code
- **RAG queries for test patterns** → Extract test structures, validation approaches, and Python test examples
  * **CRITICAL**: Extract and include actual Python test code snippets:
    - Parse the JSON response `results[].content` field to locate Python test code
    - Look for Python patterns: `def test_`, `simics.SIM_create_object()`, `dev_util.Register_LE()`, `stest.expect_equal()`
    - Extract 10-20 lines of actual Python test code per example (not just descriptions)
    - Format as markdown code blocks with ```python fencing
    - Example: If RAG returns test code with device creation and assertions, extract and format the actual Python code
    - DO NOT write descriptions like "Tests that create devices" - show the actual test code
- **Additional RAG searches** → Extract code examples, implementation patterns, and design recommendations

### Step 0.4: Create research.md File

**MANDATORY**: Create `[SPECS_DIR]/research.md` with this exact structure:

```markdown
# Research: [FEATURE_NAME]

## Environment Discovery

### Simics Version
[Document output from get_simics_version() - include version number]

### Installed Packages
[Document output from list_installed_packages() - format as table with package details]

| Package Name | Package Number | Package Version |
|-------------|----------------|-----------------|
| [package-1-name] | [package-1-number] | [package-1-version] |
| [package-2-name] | [package-2-number] | [package-2-version] |
| [additional packages...] | [...] | [...] |

### Available Platforms
[Document output from list_simics_platforms() - list available simulation platforms]

## Documentation Access (via RAG Queries)

### DML 1.4 Reference Manual
[Document findings from RAG query: "DML 1.4 reference manual register and device modeling"]
- **Query**: "DML 1.4 reference manual register and device modeling"
- **Source Type**: docs
- **Key Findings**:
  * [Finding 1 with relevant excerpt: Register modeling patterns and constructs]
  * [Finding 2 with relevant excerpt: Device structure requirements and organization]
  * [Finding 3 with relevant excerpt: DML language features for hardware modeling]
  * [Additional findings as discovered from RAG results]
- **References**: [List any specific manual sections or topics found]
- **Application**: Structure the [DEVICE_NAME] with appropriate register definitions and field breakdowns

### Model Builder User Guide
[Document findings from RAG query: "Simics Model Builder device creation and structure patterns"]
- **Query**: "Simics Model Builder device creation and structure patterns"
- **Source Type**: docs
- **Key Findings**:
  * [Finding 1 with relevant excerpt: Device creation workflow and build process]
  * [Finding 2 with relevant excerpt: Structure patterns and organization]
  * [Finding 3 with relevant excerpt: Best practices for device modeling]
  * [Finding 4 with relevant excerpt: Example device structures (e.g., DS12887, AM79C960, etc.)]
- **References**: [List relevant guide sections and chapters]
- **Application**: Follow established patterns for device structure and implementation approach

### DML Device Template
[Document findings from RAG query: "DML device template base structure and skeleton"]
- **Query**: "DML device template base structure and skeleton"
- **Source Type**: dml
- **Key Patterns**:
  * [Pattern 1: Device declaration with dml 1.4; and device name]
  * [Pattern 2: Register banks with parameters (register_size, byte_order)]
  * [Pattern 3: Register declarations with size, offset, and behavior templates]
  * [Additional patterns discovered from RAG results]
- **Code Examples**:
  * [code example 1]
  * [code example 2]
- **Application**: Structure the [DEVICE_NAME] device following standard DML skeleton patterns

## Device Example Analysis (via RAG Queries)

### Device-Specific Best Practices
[Document findings from RAG query: "Best practices for [DEVICE_NAME] device modeling with Simics DML 1.4"]
- **Query**: "Best practices for [DEVICE_NAME] device modeling with Simics DML 1.4"
- **Source Type**: source
- **Key Patterns Observed**:
  * [Pattern 1: Device-specific implementation approach and architecture]
  * [Pattern 2: Recommended architecture for this device type]
  * [Pattern 3: Common pitfalls to avoid and solutions]
  * [Pattern 4: Performance or accuracy considerations]
- **Code Examples**:
  * [code example 1]
  * [code example 2]
- **Relevant Structures**: [Describe patterns directly applicable to [DEVICE_NAME]]
- **Application**: Apply [DEVICE_NAME]-specific patterns to avoid common issues and follow best practices

### Simics Device Reference Example
[Document findings from RAG query: "Simics device implementation example [DEVICE_NAME] or similar peripheral"]
- **Query**: "Simics device implementation example [DEVICE_NAME] or similar peripheral"
- **Source Type**: source
- **Key Patterns Observed**:
  * [Pattern 1: Basic register implementation and organization]
  * [Pattern 2: Device initialization and lifecycle]
  * [Pattern 3: Interface implementation (e.g., io_memory, signal, port, connect)]
  * [Pattern 4: Event handling and timing mechanisms]
- **Code Examples**:
  * [code example 1]
  * [code example 2]
- **Applicable Patterns**: [Which patterns apply to [DEVICE_NAME] and how to adapt them]
- **Application**: Adapt similar device patterns to [DEVICE_NAME] implementation requirements

### Register Implementation Patterns
[Document findings from RAG query: "DML register bank implementation patterns"]
- **Query**: "DML register bank implementation patterns"
- **Source Type**: dml
- **Implementation Patterns**:
  * [Pattern 1: Register bank definition with parameters]
  * [Pattern 2: Register access methods (read, write, get, set)]
  * [Pattern 3: Register callbacks and custom behaviors]
  * [Pattern 4: Field definitions and bit-level access]
- **Code Examples**:
  * [code example 1]
  * [code example 2]
- **Application**: Implement [DEVICE_NAME] register bank following standard patterns with appropriate customization

## Test Example Analysis (via RAG Queries)

### Simics Python Test Patterns
[Document findings from RAG query: "Simics Python test patterns and examples"]
- **Query**: "Simics Python test patterns and examples"
- **Source Type**: python
- **Key Test Patterns Observed**:
  * [Pattern 1: Test suite structure and organization]
  * [Pattern 2: Device instance creation using simics.SIM_create_object()]
  * [Pattern 3: Register access testing using dev_util.Register_LE()]
  * [Pattern 4: Assertions and validation using stest.expect_equal()]
- **Code Examples**:
  * [test code example 1]
  * [test code example 2]
- **Test Framework**: [Document testing framework and utilities used (e.g., stest, dev_util, simics modules)]
- **Application**: Structure tests for [DEVICE_NAME] following established test patterns and conventions

### Device Testing Best Practices
[Document findings from RAG query: "Simics device testing best practices"]
- **Query**: "Simics device testing best practices"
- **Source Type**: source
- **Best Practices Identified**:
  * [Practice 1: Test coverage strategies and completeness criteria]
  * [Practice 2: Validation approaches for device behavior verification]
  * [Practice 3: Error condition testing and edge case handling]
  * [Practice 4: Performance testing and regression detection]
- **Code Examples**:
  * [test code example 1]
  * [test code example 2]
- **Applicable Practices**: [Which practices apply to [DEVICE_NAME] testing and how to implement them]
- **Application**: Apply comprehensive testing practices to ensure [DEVICE_NAME] correctness and reliability

## Additional Research (Requirement-Driven RAG Queries)

[Document additional RAG queries executed to address specific functional requirements not covered by mandatory queries]

### Additional Query #9: [Query Focus - tied to specific requirement]
[Document findings from additional RAG query addressing a knowledge gap]
- **Query**: "[exact query string used]"
- **Source Type**: [dml/python/source/docs/all]
- **Match Count**: [number]
- **Requirement Addressed**: [Reference specific functional requirement from spec.md that necessitated this query]
- **Knowledge Gap**: [What wasn't covered by mandatory queries 1-8]
- **Key Findings**:
  * [Finding 1: Specific pattern, feature, or approach discovered]
  * [Finding 2: Implementation detail or best practice]
  * [Finding 3: Integration or interface pattern]
  * [Additional findings as relevant]
- **Code Examples**:
  * [code example 1 - 10-20 lines of actual DML/Python code]
  * [code example 2 - showing specific pattern or feature]
- **Application**: [How these findings will be applied to [DEVICE_NAME] implementation]

### Additional Query #10: [Query Focus - tied to specific requirement]
[Repeat structure above for each additional query]
- **Query**: "[exact query string]"
- **Source Type**: [type]
- **Match Count**: [number]
- **Requirement Addressed**: [Reference specific functional requirement]
- **Knowledge Gap**: [What knowledge was needed]
- **Key Findings**: [...]
- **Code Examples**: [...]
- **Application**: [...]

[Continue with Additional Query #11, #12, etc. as needed based on functional requirements]

## Architecture Decisions

[For each NEEDS CLARIFICATION in Technical Context, create an entry:]

### Decision: [What was decided - e.g., "Use register bank template"]
- **Rationale**: [Why this choice - based on MCP tool and RAG findings and examples]
- **Alternatives Considered**: [What else was evaluated]
- **Source**: [Which MCP tool, RAG query (Search #) informed this decision]
- **Impact**: [How this affects implementation]

## RAG Search Results Summary

[Quick reference table for all RAG queries executed - verify all 8 MANDATORY searches completed, plus any additional requirement-driven queries]

| # | Query Focus | Source Type | Match Count | Status | Reference Section |
|---|-------------|-------------|-------------|--------|-------------------|
| 1 | DML 1.4 Reference Manual | docs | 5 | ✅ | Documentation Access |
| 2 | Model Builder Patterns | docs | 5 | ✅ | Documentation Access |
| 3 | DML Device Template | dml | 5 | ✅ | Documentation Access |
| 4 | Device-Specific Best Practices | source | 5 | ✅ | Device Example Analysis |
| 5 | Simics Device Reference | source | 5 | ✅ | Device Example Analysis |
| 6 | Register Implementation | dml | 5 | ✅ | Device Example Analysis |
| 7 | Python Test Patterns | python | 5 | ✅ | Test Example Analysis |
| 8 | Device Testing Best Practices | source | 5 | ✅ | Test Example Analysis |
| 9+ | [Additional Query - specify requirement addressed] | [type] | [N] | ✅ | Additional Research |

**Note**: Queries 9+ are requirement-driven queries executed to address specific knowledge gaps identified from the "Functional Requirements" section in spec.md. Each additional query should document which requirement it addresses and what knowledge gap it fills.

## Implementation Strategy

[Document overall approach based on research findings]

### Device Architecture
[High-level architecture based on examples and patterns]

### Register Design Approach
[Strategy for register implementation]

### Test Strategy
[Approach for testing based on example test patterns]

### Next Steps
[What Phase 1 should focus on based on research]
```

### Step 0.5: Update Technical Context in plan.md

**MANDATORY**: Replace ALL "NEEDS CLARIFICATION" placeholders in the Technical Context section with actual discovered values:

- **Simics Version**: Replace with actual version from `get_simics_version()`
- **Required Packages**: Replace with list from `list_installed_packages()`
- **Available Platforms**: Replace with list from `list_simics_platforms()`
- Any other NEEDS CLARIFICATION items resolved through research

### Step 0.6: Update Progress Tracking in plan.md

**MANDATORY**: Update the Progress Tracking section at the end of plan.md. Mark these checkboxes:

```markdown
**Phase Status**:
- [x] Phase 0: Research complete (/plan command)

**Simics Discovery MCP Tool Status** (if Project Type = simics):
- [x] `get_simics_version()` executed and documented (MANDATORY)
- [x] `list_installed_packages()` executed and documented (MANDATORY)
- [x] `list_simics_platforms()` executed and documented (MANDATORY)
- [x] MCP tool outputs incorporated into research.md

**RAG Documentation Search Status** (if Project Type = simics):
- [x] `perform_rag_query()` used for DML 1.4 reference documentation (source_type="docs")
- [x] `perform_rag_query()` used for Model Builder patterns (source_type="docs")
- [x] `perform_rag_query()` used for DML device templates (source_type="dml")
- [x] `perform_rag_query()` used for device-specific best practices (source_type="source")
- [x] `perform_rag_query()` used for register implementation patterns (source_type="dml")
- [x] `perform_rag_query()` used for Python test patterns (source_type="python")
- [x] `perform_rag_query()` used for device testing best practices (source_type="source")
- [x] RAG search results documented in research.md

**RAG Quality Verification** (if Project Type = simics):
- [x] All 8 MANDATORY RAG queries executed and documented in research.md
- [x] Code examples extracted and included in relevant sections
- [x] Key findings documented with excerpts and references
- [x] Application guidance provided for [DEVICE_NAME] implementation
- [x] Any additional queries (9+) documented with justification in research.md
- [x] RAG Search Results Summary table completed with status checkmarks
```

### Step 0.7: Validation Checkpoint

**MANDATORY**: Before proceeding to Phase 1, verify:
- [x] research.md file exists at `[SPECS_DIR]/research.md`
- [x] Technical Context in plan.md has NO "NEEDS CLARIFICATION" text
- [x] Progress Tracking shows Phase 0 marked complete

Use bash commands to verify:
```bash
ls -la [SPECS_DIR]/research.md
grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md
```

### Step 0.8: Announce Phase Completion

Explicitly state in your response:
```
✅ Phase 0 (Research) complete. Proceeding to Phase 1 (Design).

**Phase 0 Summary**:
- MCP tools executed: 3
- RAG searches performed: 8
- NEEDS CLARIFICATION resolved: 3
- research.md created: ✅
- Technical Context updated: ✅
```

**Output**: research.md with all NEEDS CLARIFICATION resolved, MCP tool outputs, and RAG documentation search results documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete, Phase 0 validated*

### Step 1.1: Create data-model.md

**MANDATORY**: Create `[SPECS_DIR]/data-model.md` documenting the data structures:

**For Software Projects**:
- Entity name, fields, relationships
- Validation rules from requirements
- State transitions if applicable

**For Simics Projects**:
- Register definitions (address, size, access type, reset value)
- Device state variables and attributes
- Interface specifications
- Memory-mapped regions

Use this structure:
```markdown
# Data Model: [FEATURE_NAME]

## Registers (Simics Projects)

### Register: [REGISTER_NAME]
- **Offset**: [hex address]
- **Size**: [bits]
- **Access**: [RO/WO/RW]
- **Reset Value**: [hex value]
- **Purpose**: [description]
- **Fields**: [bit fields if applicable]

## Device State (Simics Projects)

### State Variable: [NAME]
- **Type**: [type]
- **Purpose**: [description]
- **Persistence**: [checkpointed/transient]

## Interfaces (Simics Projects)

### Interface: [INTERFACE_NAME]
- **Type**: [Simics interface type]
- **Methods**: [list methods]
- **Purpose**: [description]
```

### Step 1.2: Create contracts/ directory

**MANDATORY**: Create `[SPECS_DIR]/contracts/` directory with contract specifications:

**For Software Projects**:
- API contracts (REST/GraphQL endpoints)
- Request/response schemas
- Error codes and messages

**For Simics Projects**:
- Register access contracts (read/write behavior)
- Interface behavior specifications
- Memory transaction patterns

Create files like:
- `contracts/register-access.md` - Register read/write specifications
- `contracts/interface-behavior.md` - Interface method contracts

### Step 1.3: Generate contract tests (planning only)

**Note**: Don't create test files yet - just plan them in contracts/

**For Simics Projects**: Document expected register read/write behavior tests:
- Reference device test patterns from research.md Device Example Analysis section
- Use test patterns discovered via `perform_rag_query()` for [DEVICE_NAME] and similar devices
- Extract test structure patterns from RAG search results (simple and complex device references)

### Step 1.4: Extract test scenarios from user stories

Identify integration test scenarios:
- Each user story → integration test scenario
- Quickstart validation steps

**For Simics Projects**: Device operational workflow tests

### Step 1.5: Create quickstart.md

**MANDATORY**: Create `[SPECS_DIR]/quickstart.md` with user validation guide:

**CRITICAL RULES for quickstart.md**:
- ❌ DO NOT use MCP tool syntax (no `create_simics_project()` calls)
- ❌ DO NOT assume implementation details (no specific register names until implemented)
- ✅ DO use generic descriptions ("Create Simics project", "Build device module")
- ✅ DO focus on Simics CLI commands users will actually run
- ✅ DO use placeholders: `[DEVICE_NAME]`, `[REGISTER_NAME]` for unknowns
- ✅ DO include validation criteria: "What constitutes success for each step?"

Use this structure:
```markdown
# Quick Start: [FEATURE_NAME]

## Goal
[One sentence: What will users accomplish by following this guide?]

## Prerequisites
[Environment requirements from research.md - actual versions/packages found]
- Simics Base [version from research.md]
- Required packages: [list from research.md]

## Validation Steps

### Step 1: [First User Story Validation]
**What to do**:
[Conceptual steps - no specific implementation commands]

**Expected Result**:
[What should happen]

**Success Criteria**:
[How to verify it worked - observable behavior]

### Step 2: [Second User Story Validation]
**What to do**:
[Reference that implementation will create the necessary files]

**Expected Result**:
[What should happen]

**Success Criteria**:
[How to verify it worked]

## Troubleshooting
[Common failure modes and how to debug them]

## Next Steps
[References to contracts/, data-model.md, and tasks.md]
```

### Step 1.6: Update agent context file

**MANDATORY**: Run the agent context update script:

```bash
.specify/scripts/bash/update-agent-context.sh adk
```

**IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.

This updates the agent-specific file (e.g., `ADK.md` for ADK agent) with:
- New technologies from current plan
- Preserved manual additions between markers
- Updated recent changes (keep last 3)
- Kept under 150 lines for token efficiency

### Step 1.7: Update Progress Tracking in plan.md

**MANDATORY**: Update the Progress Tracking section in plan.md. Mark these checkboxes:

```markdown
**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)

**Gate Status**:
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
```

### Step 1.8: Re-evaluate Constitution Check

After completing design artifacts, re-check constitutional compliance:
- Review data-model.md against constitution principles
- Verify design doesn't introduce violations
- If new violations: Document in Complexity Tracking section
- If violations cannot be justified: Refactor design and return to Step 1.1

### Step 1.9: Validation Checkpoint

**MANDATORY**: Before proceeding, verify all Phase 1 deliverables exist:

```bash
ls -la [SPECS_DIR]/data-model.md
ls -la [SPECS_DIR]/quickstart.md
ls -la [SPECS_DIR]/contracts/
ls -la ADK.md  # or agent-specific file
```

Checklist:
- [x] data-model.md file exists and contains register/entity definitions
- [x] contracts/ directory exists with contract specifications
- [x] quickstart.md file exists with user validation steps
- [x] Agent context file updated (ADK.md or equivalent)
- [x] Progress Tracking shows Phase 1 marked complete
- [x] Constitution check passed (no new violations)

### Step 1.10: Announce Phase Completion

Explicitly state in your response:
```
✅ Phase 1 (Design) complete. Ready for /tasks command.

**Phase 1 Summary**:
- data-model.md created: ✅
- contracts/ created: ✅
- quickstart.md created: ✅
- Agent context updated: ✅
- Constitutional compliance: ✅
```

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific context file (e.g., ADK.md)

   **Quickstart.md Structure**:
   ```markdown
   # Quick Start: [FEATURE_NAME]

   ## Goal
   [One sentence: What will users accomplish by following this guide?]

   ## Prerequisites
   [Environment requirements from research.md - actual versions/packages found]

   ## Validation Steps
   ### Step 1: [First User Story Validation]
   [What to do]
   **Expected Result**: [What should happen]
   **Success Criteria**: [How to verify it worked]

   ### Step 2: [Second User Story Validation]
   [What to do - no implementation details, reference tasks that will create them]
   **Expected Result**: [What should happen]
   **Success Criteria**: [How to verify it worked]

   ## Troubleshooting
   [Common failure modes and how to debug them]

   ## Next Steps
   [References to contracts/, data-model.md, and tasks.md]
   ```

6. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh adk`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each contract → contract test task [P]
- Each entity → model creation task [P]
- Each user story → integration test task
- Implementation tasks to make tests pass
- **Simics projects**: Include implementation MCP tool tasks:
  - **Setup tasks**: `create_simics_project()`, `add_dml_device_skeleton()`
  - **Build tasks**: `build_simics_project()`
  - **Test tasks**: `run_simics_test()`
  - **Note**: Discovery MCP tools (`get_simics_version`, `list_installed_packages`) already executed in /plan phase

**Ordering Strategy**:
- TDD order: Tests before implementation
- Dependency order: Models before services before UI
- Mark [P] for parallel execution (independent files)

**Estimated Output**: 25-30 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Completion Validation (MANDATORY)

Before reporting /plan command completion, the agent MUST verify ALL these conditions:

### Phase 0 Verification Checklist
Run these checks to verify Phase 0 is complete:

```bash
# Verify research.md exists
ls -la [SPECS_DIR]/research.md

# Verify no NEEDS CLARIFICATION remains
grep "NEEDS CLARIFICATION" [SPECS_DIR]/plan.md
```

- [x] research.md file exists and contains MCP tool outputs
- [x] Technical Context in plan.md has NO "NEEDS CLARIFICATION" text
- [x] Progress Tracking shows "Phase 0: Research complete" checked
- [x] All Simics Discovery MCP Tool Status checkboxes marked (if Simics project)
- [x] MCP tool outputs are documented in research.md with proper structure

### Phase 1 Verification Checklist
Run these checks to verify Phase 1 is complete:

```bash
# Verify all Phase 1 files exist
ls -la [SPECS_DIR]/data-model.md
ls -la [SPECS_DIR]/quickstart.md
ls -la [SPECS_DIR]/contracts/
ls -la ADK.md  # or agent-specific file
```

- [x] data-model.md file exists with register/entity definitions
- [x] contracts/ directory exists with contract specifications
- [x] quickstart.md file exists with user validation steps (NO MCP tool syntax)
- [x] Agent context file updated (ADK.md, CLAUDE.md, or equivalent)
- [x] Progress Tracking shows "Phase 1: Design complete" checked
- [x] Post-Design Constitution Check shows PASS

### Overall Completion Checklist

- [x] Both Phase 0 and Phase 1 are complete
- [x] All generated files follow their respective templates
- [x] No ERROR states in execution flow
- [x] All MANDATORY steps completed
- [x] Ready for /tasks command

## Final Report Format (MANDATORY)

After completing ALL verification checks, the agent MUST provide this exact report format:

```
✅ /plan command complete

**Branch**: [branch_name from setup script]

**Files Created**:
- ✅ plan.md (updated with resolved Technical Context and Progress Tracking)
- ✅ research.md (MCP tool outputs, device examples, architecture decisions)
- ✅ data-model.md (register definitions, device state, interfaces)
- ✅ quickstart.md (user validation guide - no MCP syntax)
- ✅ contracts/ (register access contracts, interface specifications)
- ✅ [agent-file].md (updated agent context - e.g., ADK.md, CLAUDE.md)

**Phase Status**:
- ✅ Phase 0 (Research): Complete
- ✅ Phase 1 (Design): Complete
- ⏭️  Phase 2 (Task Planning): Approach described in plan.md
- 📋 Phase 2 Execution: Ready for /tasks command

**Progress Summary**:
- Constitutional checks: [PASS/ISSUES]
- MCP tools executed: [count] tools
- RAG searches performed: [count] searches
- NEEDS CLARIFICATION resolved: [count] items
- Files generated: [count] files
- Total phases completed: 2 of 2

**Generated Artifacts**:
```
[SPECS_DIR]/
├── plan.md              # ✅ Updated
├── research.md          # ✅ Created
├── data-model.md        # ✅ Created
├── quickstart.md        # ✅ Created
└── contracts/           # ✅ Created
    ├── register-access.md
    └── interface-behavior.md
```

**Next Steps**:
1. Review the generated artifacts in `[SPECS_DIR]/`
2. Run `/tasks` to generate actionable task breakdown from design artifacts
3. The /tasks command will create tasks.md based on plan.md, data-model.md, and contracts/

**Ready For**: `/tasks` command execution
```

**CRITICAL**: Do NOT report completion until BOTH Phase 0 and Phase 1 are fully complete with all files created and verified.

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [ ] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

**Simics Discovery MCP Tool Status** (if Project Type = simics):
- [x] `get_simics_version()` executed and documented (MANDATORY)
- [x] `list_installed_packages()` executed and documented (MANDATORY)
- [x] `list_simics_platforms()` executed and documented (MANDATORY)
- [x] MCP tool outputs incorporated into research.md
- [ ] Environmental constraints documented for /implement phase
- [x] **Implementation MCP tools NOT executed** (reserved for /implement phase)

**RAG Documentation Search Status** (if Project Type = simics):
- [x] `perform_rag_query()` used for DML-specific research (source_type="dml")
- [x] `perform_rag_query()` used for Python API research (source_type="python")
- [x] `perform_rag_query()` used for implementation patterns (source_type="source")
- [x] `perform_rag_query()` used for architectural guidance (source_type="docs")
- [x] RAG search results documented in research.md
- [x] Code examples and patterns extracted from RAG results
- [x] Best practices identified and incorporated into design decisions

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*