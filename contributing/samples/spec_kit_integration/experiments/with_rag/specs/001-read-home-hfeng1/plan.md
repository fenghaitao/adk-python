---
description: "Implementation plan template for feature development"
---

# Implementation Plan: Simics Watchdog Timer Model

**Branch**: `001-read-home-hfeng1` | **Date**: 2024-05-24 | **Spec**: /specs/001-read-home-hfeng1/spec.md
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
Implementation of a Simics watchdog timer model that provides a 32-bit decrementing timer with configurable time interval, interrupt and reset generation capabilities, register protection mechanisms, and integration test support. The implementation follows device-first development principles using DML 1.4.

## Technical Context
**Language/Version**: DML 1.4
**Primary Dependencies**: Simics API, Python 7.13.0
**Storage**: N/A
**Testing**: Simics test scripts
**Target Platform**: Simics 7.57.0
**Project Type**: simics
**Performance Goals**: Functional accuracy
**Constraints**: Software-visible behavior
**Scale/Scope**: Register-based peripheral device with 32-bit timer

**Simics-Specific Context** (if Project Type = simics):
**Simics Version**: Simics Base 7.57.0
**Required Packages**: simics-base, Python
**Available Platforms**: QSP-x86 7.38.0
**MCP Server**: simics-mcp-server integration available with 22+ tools for project automation, device modeling and documentation access
**Device Type**: Peripheral watchdog timer
**Hardware Interfaces**: Memory-mapped registers, interrupts, reset signals

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

All constitutional principles have been followed:
- Device-First Development: Creating a standalone watchdog timer device model
- Interface-First Architecture: Well-defined register interfaces and signal connections
- Test-First Development: Planning for comprehensive test coverage before implementation
- Specification-Driven Implementation: Strictly following the hardware specification
- Integration Testing Focus: Planning for device-to-device communication testing
- Observability and Transparency: Ensuring device state is inspectable
- Simplicity and Incremental Development: Starting with core functionality
- Simics Excellence: Following DML coding standards and best practices

## Project Structure

### Documentation (this feature)
```
specs/001-read-home-hfeng1/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
## Repository Structure
repo-root/
├── simics-project/              # ← Source code (implementation)
│   └── modules/wdt/
│       ├── wdt.dml      # Main device implementation
│       ├── registers.dml        # Register definitions and mappings (optional)
│       ├── interfaces.dml       # Device interface implementations (optional)
│       ├── module_load.py       # Simics module load action definitions
│       ├── CMakeLists.txt       # CMake file
│       └── test/
│           ├── CMakeLists.txt   # CMake file
│           ├── SUITEINFO        # Test timeout and tags
│           ├── s-wdt.py # tests implementation
│           ├── test_wdt_common.py # test configuration and device instance creation
│           └── README
│
└── specs/                       # ← Documentation artifacts only
    └── 001-read-home-hfeng1/
        ├── plan.md              # This file (/plan command output)
        ├── research.md          # Phase 0 output (/plan command)
        ├── data-model.md        # Phase 1 output (/plan command)
        ├── quickstart.md        # Phase 1 output (/plan command)
        ├── contracts/           # Phase 1 output (/plan command)
        └── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)

**Structure Decision**: Using the Simics device project structure with the device implementation at the repository root in simics-project/modules/wdt/ and documentation in the specs folder.

**For Simics projects**: The structure above shows the template that will be generated AT REPOSITORY ROOT (not in specs/ folder). The actual project structure will be created by the simics-mcp-server's MCP tools during task execution (Phase 3.1 Setup):
- `create_simics_project(project_path="./simics-project")` creates the base project structure at repo root
- `add_dml_device_skeleton(project_path="./simics-project", device_name="wdt")` adds device-specific modeling files

**IMPORTANT**: Simics projects must be created at repository root to separate source code from documentation. The specs/ folder contains only documentation artifacts (plan.md, tasks.md, etc.), while the simics-project/ folder at repo root contains the actual implementation.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - All technical context has been resolved through MCP tool execution and RAG searches

2. **Generate and dispatch research agents**:
   ```
   Task: "Research DML 1.4 implementation patterns for watchdog timers"
   Task: "Find best practices for timer-based device modeling in Simics"
   Task: "Analyze register protection mechanisms in existing Simics devices"
   ```

   **Simics-specific research tasks**:
   ```
   Task: "MANDATORY: Execute `get_simics_version()` MCP tool to resolve environment NEEDS CLARIFICATION"
   Task: "MANDATORY: Execute `list_installed_packages()` MCP tool to resolve package dependencies NEEDS CLARIFICATION"
   Task: "IF similar implementations needed for decisions: Execute `get_simics_device_example_ds12887()` MCP tools"
   Task: "Research Simics API for memory operations and interfaces (from documentation)"
   Task: "Analyze hardware specification for register mapping requirements"
   Task: "Document architectural decisions based on MCP tool findings"
   Task: "Validate constitutional compliance for device-first development approach"
   ```

3. **Execute discovery MCP tools immediately** (for Simics projects):
   - **Environment tools**: `get_simics_version()` and `list_installed_packages()` executed
   - **Documentation tools**: `get_simics_dml_1_4_reference_manual()` and `get_simics_model_builder_user_guide()` executed
   - **Example tools**: `get_simics_device_example_ds12887()` executed
   - **RAG documentation search**: Used `perform_rag_query()` with source_type="dml" for implementation patterns
   - **DO NOT execute implementation tools**: Reserved for /implement phase
   - Include MCP tool outputs and RAG findings directly in research.md to inform design decisions
   - **Purpose**: Gather information needed for planning, not create implementation artifacts

4. **Consolidate findings** in `research.md` using format:
   - Decision: Device-First Development Approach
   - Rationale: Ensures modularity, testability, and clear hardware abstraction boundaries
   - Alternatives considered: Monolithic system modeling approach
   - **Simics projects**: Device architecture decisions, MCP tool outputs, RAG search results, and abstraction strategy documented
   - **RAG findings**: Timer implementation patterns and best practices discovered

**Output**: research.md with all NEEDS CLARIFICATION resolved, MCP tool outputs, and RAG documentation search results documented

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Watchdog Timer entity with 32-bit decrementing counter
   - Configuration Registers entity with load value, control settings, and lock status
   - Interrupt/Reset Signals entity with wdogint and wdogres output signals
   - Clock/Reset Interface entity with wclk, wclk_en, and wrst_n input signals

2. **Generate API contracts** from functional requirements:
   - Register access contracts for all watchdog timer registers
   - Interface specifications for interrupt and reset signal generation
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - Register read/write behavior tests
   - Timer countdown behavior tests
   - Interrupt and reset generation tests
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Interrupt generation on timeout
   - Reset generation on second timeout
   - Register protection mechanisms
   - Device operational workflow tests

5. **Generate quickstart.md** from user story validation:
   - Focus on device behavior validation, not implementation commands
   - Reference tasks.md for implementation steps
   - Include validation criteria for each step

6. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh adk`
   - Add only NEW tech from current plan
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

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|


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
- [x] `get_simics_dml_1_4_reference_manual()` executed (only if DML syntax was NEEDS CLARIFICATION)
- [x] `get_simics_model_builder_user_guide()` executed (only if modeling approach was NEEDS CLARIFICATION)
- [x] Device example tools executed (only if needed for architectural decisions)
- [x] MCP tool outputs incorporated into research.md
- [x] Environmental constraints documented for /implement phase
- [x] **Implementation MCP tools NOT executed** (reserved for /implement phase)

**RAG Documentation Search Status** (if Project Type = simics):
- [x] `perform_rag_query()` used for DML-specific research (source_type="dml")
- [ ] `perform_rag_query()` used for Python API research (source_type="python")
- [x] `perform_rag_query()` used for implementation patterns (source_type="source")
- [ ] `perform_rag_query()` used for architectural guidance (source_type="docs")
- [x] RAG search results documented in research.md
- [x] Code examples and patterns extracted from RAG results
- [x] Best practices identified and incorporated into design decisions

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*