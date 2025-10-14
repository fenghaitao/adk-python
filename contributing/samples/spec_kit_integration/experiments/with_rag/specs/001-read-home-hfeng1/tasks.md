# Tasks: Simics Watchdog Timer Model

**Input**: Design documents from `/specs/001-read-home-hfeng1/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Extract: tech stack (DML 1.4), libraries (Simics API, Python), structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Register access contract → contract test task
   → research.md: Extract decisions → setup tasks
   → quickstart.md: Extract user stories → integration tests
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have model tasks?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Simics**: `./simics-project/modules/wdt/`, `./simics-project/modules/wdt/test/` at repository root

## Phase 3.1: Setup
- [x] T001 Verify simics-mcp-server connection and Simics installation using `get_simics_version()`
- [x] T002 Create Simics project structure using `create_simics_project(project_path="./simics-project")`
- [x] T003 Add device skeleton using `add_dml_device_skeleton(project_path="./simics-project", device_name="wdt")`
- [x] T004 [P] Verify project structure and build system using `build_simics_project(project_path="./simics-project", module="wdt")`
- [x] T005 **MANDATORY**: Access DML 1.4 reference documentation using `get_simics_dml_1_4_reference_manual()`
- [x] T006 **MANDATORY**: Access Model Builder User Guide using `get_simics_model_builder_user_guide()`
- [x] T007 **MANDATORY**: Retrieve DML template using `get_simics_dml_template()` for base device structure patterns
- [x] T008 **MANDATORY**: Retrieve I2C device example using `get_simics_device_example_i2c()` for reference patterns
- [x] T009 **MANDATORY**: Retrieve DS12887 device example using `get_simics_device_example_ds12887()` for advanced patterns
- [x] T010 **RAG SEARCH**: Use `perform_rag_query("DML device implementation patterns", source_type="source", match_count=5)` for additional examples
- [x] T011 **RAG SEARCH**: Use `perform_rag_query("Simics register modeling", source_type="dml", match_count=5)` for register-specific guidance
- [x] T012 **CRITICAL**: Study and document the retrieved documentation, examples, DML template, and RAG search results before proceeding to test or implementation phases
- [x] T013 **VALIDATION**: Verify that documentation, examples, and RAG searches have been successfully retrieved and analyzed

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T014 [P] Register access test in simics-project/modules/wdt/test/s-registers.py (use python_test_samples_path from device examples and RAG results for patterns)
- [x] T015 [P] Timer behavior test in simics-project/modules/wdt/test/s-timer.py
- [x] T016 [P] Interrupt and reset generation test in simics-project/modules/wdt/test/s-interrupt-reset.py
- [x] T017 [P] Register protection test in simics-project/modules/wdt/test/s-protection.py
- [x] T018 [P] Integration test mode test in simics-project/modules/wdt/test/s-integration.py
- [x] T019 [P] Set up and validate test environment using `run_simics_test(project_path="./simics-project", suite="modules/wdt/test")`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T020 [P] Register definitions in simics-project/modules/wdt/registers.dml
- [x] T021 [P] Interface declarations in simics-project/modules/wdt/interfaces.dml
- [x] T022 [P] Utility methods in simics-project/modules/wdt/utility.dml
- [x] T023 [P] Build device module using `build_simics_project(project_path="./simics-project", module="wdt")`
- [x] T024 Main device structure in simics-project/modules/wdt/wdt.dml
- [x] T025 **RAG SEARCH**: Use `perform_rag_query("device state management Simics", source_type="source", match_count=5)` for state handling patterns
- [x] T026 Register read/write logic implementation
- [x] T027 Device state management and attributes
- [x] T028 Error handling and logging for device operations
- [x] T029 [P] Incremental build validation using `build_simics_project(project_path="./simics-project", module="wdt")`

## Phase 3.4: Integration
- [x] T030 **RAG SEARCH**: Use `perform_rag_query("Simics device interface integration", source_type="docs", match_count=5)` for integration patterns
- [x] T031 Connect device to memory interface using transact() methods
- [x] T032 Implement interrupt line connections and events
- [x] T033 Add external port communications and protocols
- [x] T034 Integrate with Simics checkpointing and state management
- [x] T035 [P] Validate integration with `build_simics_project(project_path="./simics-project")`
- [x] T036 [P] Run comprehensive tests using `run_simics_test(project_path="./simics-project", suite="modules/wdt/test")`

## Phase 3.5: Polish
- [ ] T037 [P] Unit tests for validation in tests/unit/test_validation.py
- [ ] T038 Performance tests (<200ms)
- [ ] T039 [P] Update docs/api.md
- [ ] T040 Remove duplication
- [ ] T041 Run manual-testing.md

## Dependencies
- Tests (T014-T019) before implementation (T020-T029)
- T020-T022 blocks T024
- T024 blocks T026-T028
- T029 before T031-T036
- Implementation before polish (T037-T041)

### Simics Dependencies
- MCP server connection (T001) before project creation (T002)
- Project structure (T002) before device skeleton (T003)
- Device skeleton (T003) before build validation (T004)
- Build validation (T004) before documentation access (T005-T009)
- Documentation access (T005-T009) before RAG searches (T010-T011)
- RAG searches (T010-T011) before study phase (T012)
- Documentation study (T012) before validation (T013)
- Validation (T013) before test RAG search (T014)
- Test RAG search (T014) before register tests (T015-T019)
- Register tests (T015-T019) before implementation RAG searches (T020, T025)
- Implementation RAG searches before actual implementation (T020-T029)
- Device implementation (T020-T029) before integration RAG search (T030)
- Integration RAG search (T030) before integration tasks (T031-T036)
- Integration validation (T035-T036) before polish tasks

## Parallel Example
```
# Launch T014-T018 together:
Task: "Register access test in simics-project/modules/wdt/test/s-registers.py"
Task: "Timer behavior test in simics-project/modules/wdt/test/s-timer.py"
Task: "Interrupt and reset generation test in simics-project/modules/wdt/test/s-interrupt-reset.py"
Task: "Register protection test in simics-project/modules/wdt/test/s-protection.py"
Task: "Integration test mode test in simics-project/modules/wdt/test/s-integration.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - Register access contract → register test task [P]
   - Each register → implementation task
   - **Simics**: Each register interface → register test task [P]
   
2. **From Data Model**:
   - Watchdog Timer entity → model creation task [P]
   - Configuration Registers entity → register definitions task [P]
   - Interrupt/Reset Signals entity → interrupt implementation task [P]
   - Clock/Reset Interface entity → interface implementation task [P]
   - **Simics**: Each register group → DML file task [P]
   
3. **From User Stories**:
   - Basic timer interrupt generation → timer behavior test [P]
   - Timer reset generation → interrupt and reset test [P]
   - Register protection mechanism → protection test [P]
   - Integration test mode → integration test [P]
   - **Simics**: Each device workflow → operational test [P]

4. **Ordering**:
   - Setup → Tests → Models → Services → Endpoints → Polish
   - **Simics**: MCP Setup → Tests → Registers → Interfaces → Device → Integration → Validation → Polish
   - Dependencies block parallel execution
   - **Simics MCP Tools**: Use at each validation step for continuous integration

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests
- [x] All entities have model tasks
- [x] All tests come before implementation
- [x] Parallel tasks truly independent
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task

**Simics-Specific Validation:**
- [x] All MCP tool calls specify correct project_path
- [x] Build validation tasks after implementation changes
- [x] Test execution tasks use appropriate suite parameter
- [x] Device name consistently used across MCP tool calls
- [x] RAG searches use appropriate source_type for each phase
- [x] RAG search results documented before proceeding to implementation
- [x] match_count parameter set to 5 for all searches

## Critical MCP Tool Execution Gate
**⚠️ MANDATORY: These MCP tools MUST be executed before proceeding to Phase 3.2 (Tests)**

### Pre-Test Phase Gate Checklist:
- [x] **GATE T005**: `get_simics_dml_1_4_reference_manual()` has been successfully executed and returned valid documentation paths
- [x] **GATE T006**: `get_simics_model_builder_user_guide()` has been successfully executed and returned valid guide paths
- [x] **GATE T007**: `get_simics_dml_template()` has been successfully executed and returned valid DML template code
- [x] **GATE T008**: `get_simics_device_example_i2c()` has been successfully executed and returned valid I2C device example code
- [x] **GATE T009**: `get_simics_device_example_ds12887()` has been successfully executed and returned valid DS12887 device example code
- [x] **GATE T010**: `perform_rag_query()` executed for DML device patterns with valid results
- [x] **GATE T011**: `perform_rag_query()` executed for Simics register modeling with valid results
- [x] **GATE T012**: Retrieved documentation, examples, DML template, and RAG search results have been studied and documented for reference during implementation
- [x] **GATE T013**: Validation confirms that all MCP tools and RAG searches returned non-empty, valid content

### Execution Validation Rules:
1. **Immediate Execution**: When T005-T011 are encountered, the MCP functions and RAG searches MUST be called immediately
2. **Success Verification**: Each MCP call and RAG search must return valid content before marking task complete
3. **Documentation Required**: Results must be saved and documented for later reference
4. **python_test_samples_path Access**: Device examples must include access to test sample paths for TDD phase
5. **RAG Search Parameters**: Use appropriate source_type and match_count=5 for all searches
6. **Blocking Dependency**: No Phase 3.2+ tasks can proceed until ALL setup MCP tools and RAG searches are successfully executed

### Common Execution Failures:
- ❌ **Stating intention without execution**: "Let's call get_simics_device_example_i2c" or "Let's search with RAG" without actually invoking
- ❌ **Skipping to file operations**: Moving to task file updates instead of executing MCP calls and RAG searches
- ❌ **Assuming completion**: Marking tasks complete without verifying MCP tool and RAG execution
- ❌ **Ignoring test samples**: Not accessing python_test_samples_path from device examples
- ❌ **Wrong source_type**: Using source_type="all" when specific type (dml/python/source) would be more appropriate
- ✅ **Correct approach**: Execute MCP function/RAG search → Verify result → Access test samples → Document output → Mark complete