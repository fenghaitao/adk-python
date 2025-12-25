---
name: "openspec-propose"
displayName: "OpenSpec Propose"
description: "Create OpenSpec proposals for Simics DML device implementations with domain knowledge and validation"
keywords: ["openspec", "propose", "proposal", "simics", "dml", "device-modeling", "hardware-simulation", "specification", "requirements"]
author: "ADK Team"
---

# OpenSpec Propose Power

This power provides complete OpenSpec proposal creation workflow for Simics DML device implementations, including domain knowledge and validation tools.

## What This Power Provides

1. **OpenSpec Workflow** - Complete proposal phase execution following `openspec/AGENTS.md`
2. **Knowledge Base** - DML and test documentation in `openspec-memories/`
3. **Validation Tools** - OpenSpec CLI commands for proposal validation

## Available Steering Files

- **multi-capability-proposals** - Guide for decomposing complex devices (50+ requirements) into multiple capabilities with separate spec deltas

## Quick Reference

**For simple devices (<50 requirements)**:
1. Read `openspec/AGENTS.md` for OpenSpec workflow
2. Read `specs/<branch-name>/spec.md` completely
3. Create proposal.md, tasks.md, and single spec delta
4. Run `openspec validate --strict`

**For complex devices (50+ requirements)**:
1. Read `openspec/AGENTS.md` for OpenSpec workflow
2. Read `specs/<branch-name>/spec.md` completely
3. Read **multi-capability-proposals** steering file
4. Decompose into multiple capabilities (e.g., timer-core, interrupt-control, lock-protection)
5. **Create separate spec delta directory for each capability** (not a single spec delta)
6. Create design.md documenting capability interactions and implementation order
7. Run `openspec validate --strict` for each capability

**Key difference**: Complex devices use **multiple spec delta directories** (one per capability) instead of a single spec delta, enabling independent implementation and testing of each capability.

**Common device patterns**:
- Timer/watchdog → Load `02_DML_Anti_Patterns.md` FIRST (prevents critical mistakes)
- Register device → Load `06_DML_Common_Patterns.md`
- New to DML → Load `01_Simics_Modeling_Philosophy.md`
- Test setup → Load `02_Test_Configuration_Setup.md`

## Scope

This power handles the OpenSpec Proposal phase for **INITIAL implementations** (skeleton → working code):

- **Input**: DML skeleton with auto-generated register structure and USER-TODO placeholders
- **Source of Truth**: Existing specification at `specs/<branch-name>/spec.md`
- **Goal**: Create proposal to implement the device behavior already defined in the spec
- **Scope Boundary**: Implement what's specified, don't invent new functionality beyond the spec

**What "INITIAL implementation" means**:
- The spec already exists with requirements (FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX)
- The DML skeleton exists but has no functional behavior (USER-TODO placeholders)
- Your proposal extracts requirements from the spec into spec deltas
- Your proposal creates tasks to implement those requirements in DML
- You're **not adding new requirements** to the spec, you're **implementing existing requirements**

**Example**: If spec says "FUNC-005: Device SHALL generate interrupt on timeout", your proposal:
- ✅ Extracts this as spec delta requirement
- ✅ Creates task "Implement interrupt generation on timeout"
- ❌ Does NOT add new requirement like "Device SHALL support multiple interrupt priorities" (not in spec)

## Guardrails

- Favor straightforward, minimal implementations first and add complexity only when requested or clearly required
- Keep changes tightly scoped to the requested outcome
- Identify any vague or ambiguous details and ask necessary follow-up questions before editing files

## Pre-Flight Checklist (Complete Before Creating ANY Proposal)

**MANDATORY**: Verify you have completed ALL items below before creating a proposal.

- [ ] Read `openspec/AGENTS.md` completely
- [ ] Execute `find specs -name "spec.md" -type f` to locate the spec file
- [ ] Read the ENTIRE existing spec file at `specs/<branch-name>/spec.md`
- [ ] Identify existing requirements (FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX) related to your proposal
- [ ] Identify existing test scenarios (TEST-001, TEST-002, etc.) related to your proposal
- [ ] Understand the device's register map and operational model from the spec
- [ ] Load relevant DML knowledge from openspec-memories/ (if needed for implementation details)

**⚠️ STOP: If you cannot check ALL boxes above, complete the missing steps before proceeding.**

## CRITICAL: Execution Steps (FOLLOW THIS SEQUENCE)

You MUST execute these steps in EXACT order. Do NOT skip any step or jump ahead.

**STEP 1: Read OpenSpec Workflow Documentation (DO THIS FIRST)**
- IMMEDIATELY read `openspec/AGENTS.md` before doing anything else
- This provides the complete OpenSpec proposal creation workflow
- Focus on the "Creating Change Proposals" section for structure and requirements

**STEP 2: Locate and Read Existing Spec (MANDATORY - DO NOT SKIP)**

Execute this command to find the spec:
```bash
find specs -name "spec.md" -type f
```

Then read the ENTIRE spec file at `specs/<branch-name>/spec.md` and understand:
- **Existing requirements**: FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX
- **Test scenarios**: TEST-001, TEST-002, etc. (what's already covered)
- **Register map**: Device registers, offsets, access types, reset values
- **Operational model**: Device states, transitions, SW/HW interaction flows
- **Terminology**: Naming conventions and structure used in the spec

**⚠️ CRITICAL**: Your proposal MUST reference and build upon this existing spec, not duplicate or contradict it.

**❌ FAILURE TO READ THE SPEC WILL RESULT IN INVALID PROPOSALS**

**STEP 2.5: Evaluate Device Complexity IMMEDIATELY (DO THIS BEFORE LOADING DML KNOWLEDGE)**

**⚠️ STOP: Before loading ANY DML knowledge, you MUST determine device complexity.**

**Check if this is a complex device:**
- User request mentions "complex" device
- OR spec has 50+ requirements - count using grep tool:
  ```
  grep(pattern=\*\*(FUNC|REG|BEHAV|TEST)-\d+\*\*, path=specs/<branch-name>/spec.md)
  ```
- OR device has distinct functional subsystems (e.g., timer + interrupt + lock + test-mode)

**If complex device detected (50+ requirements):**
1. **IMMEDIATELY read the multi-capability-proposals steering file**:
   - The steering file is available in this power: `multi-capability-proposals.md`
   - Use available tools to read steering files from the openspec-propose power
2. Follow the guidance to decompose into multiple capabilities
3. Create separate spec delta directories for each capability
4. Create design.md documenting capability interactions

**If simple device (<50 requirements):**
- Proceed to STEP 3 to load DML knowledge
- Create single spec delta

**⚠️ DO NOT LOAD DML KNOWLEDGE UNTIL YOU COMPLETE THIS STEP**

**STEP 3: Load Relevant DML Knowledge (if needed for implementation details)**
- Follow Memory Loading Protocol below to load relevant openspec-memories/ documents
- Only load 1-2 documents specific to your proposal needs (be token-efficient)
- **For timer/watchdog devices**: Read `openspec-memories/02_DML_Anti_Patterns.md` FIRST to avoid critical mistakes

**STEP 4: Create Proposal and Spec Deltas**

Follow OpenSpec workflow from `openspec/AGENTS.md` for proposal structure and spec delta creation.

**Spec Format Requirements (CRITICAL):**
- ALL requirement keywords MUST be UPPERCASE: "SHALL", "SHOULD", "MAY", "MUST", "MUST NOT"
- NEVER use lowercase: "shall", "should", "may", "must", "must not"
- Each requirement MUST have at least one `#### Scenario:` subsection
- Format: `## ADDED Requirements` or `## MODIFIED Requirements` or `## REMOVED Requirements`

**Additional Guidance:**
- Simics-specific context, scope, device patterns, and DML constraints (see Simics-Specific Implementation Guidance below)
- **Reference specific requirements from the existing spec** by ID (e.g., "Building on FUNC-014..." or "Extends TEST-004...")
- Match the style, terminology, and structure of the existing spec
- Use ADDED for new requirements, MODIFIED for changes to existing requirements (include full updated text)
- **Ensure complete requirement coverage** (see Spec Delta Completeness Requirements below for coverage criteria)
- **Create tasks.md with BOTH DML implementation tasks AND test tasks** (see Task Structure Requirements and Task Decomposition Requirements below)

**STEP 5: Validate (MANDATORY)**
- Verify proposal meets Apply Agent Handoff criteria below (detailed tasks, comprehensive testing, implementation guidance, complete spec deltas, clear context)
- Verify spec delta completeness using criteria in Spec Delta Completeness Requirements below
- Execute: `openspec validate <change-id> --strict` as specified in OpenSpec workflow
- Fix ALL validation errors before proceeding

**STEP 6: Return Result**
- Confirm proposal created successfully with change_id and summary

## Memory Loading Protocol (Token-Efficient Knowledge Loading)

**Purpose**: Load only the DML/test knowledge needed for your specific proposal. The spec file (STEP 2) provides device requirements; memory docs provide implementation patterns.

### Loading Strategy:

1. **Start with index files** (if you need DML implementation guidance):
   - `openspec-memories/00_DML_Best_Practices_Index.md` - DML implementation roadmap
   - `openspec-memories/00_Test_Best_Practices_Index.md` - Test creation roadmap
   - Use "I want to..." sections to identify which 1-2 additional documents to load

2. **Load ONLY specific documents needed** (avoid loading all documents):
   - Be token-efficient: load 1-2 targeted documents maximum
   - Use the index to guide your selection

3. **⚠️ CRITICAL ANTI-PATTERN PREVENTION**:
   - **Timer/counter/watchdog devices**: MUST read `openspec-memories/02_DML_Anti_Patterns.md` FIRST
     - Anti-Pattern #1 (clock signal modeling) → 100-1000x performance degradation
     - Anti-Pattern #2 (SIM_cycle_count in init) → runtime crashes
     - Anti-Pattern #3 (incomplete timer) → non-functional devices
   - Reading anti-patterns first prevents proposing "obvious but wrong" implementations

### Quick Reference by Proposal Type:

| Proposal Type | Required Reading |
|---------------|------------------|
| Timer/watchdog | `02_DML_Anti_Patterns.md` + `04_DML_Timing_Timer_Modeling.md` |
| Register device | `01_Simics_Modeling_Philosophy.md` + `06_DML_Common_Patterns.md` |
| New to DML | `01_Simics_Modeling_Philosophy.md` + `03_DML_Basic_Syntax.md` |
| Test configuration | `02_Test_Configuration_Setup.md` (CRITICAL for clock/queue setup) |

## Simics-Specific Implementation Guidance

The user input provides the purpose (what device/feature to implement) and may include references to hardware specifications.

### Information Sources (in priority order):

1. **Primary Specification** (see STEP 2): `specs/<branch-name>/spec.md`
   - **Authoritative source** for device requirements and behavior
   - Contains: hardware spec, operational model, existing requirements (FUNC-XXX, REG-XXX, etc.), test scenarios (TEST-XXX)
   - **Your proposal MUST**: Reference and extend this spec, not duplicate or contradict it
   - **Example references**: "Building on FUNC-014 (clock divider requirements)..." or "Extends TEST-004 to cover edge case..."

2. **Secondary Hardware Specification** (optional - if mentioned in user input):
   - Look for: "Hardware Specification: documented in `<filename>`" in user input
   - Use when: Primary spec needs clarification on hardware details
   - Contains: Comprehensive hardware details, register definitions, operational behavior

3. **DML and Test Best Practices** (optional - for implementation patterns):
   - Follow Memory Loading Protocol (see above) to load relevant knowledge from `openspec-memories/`
   - Use when: You need DML syntax, patterns, or test implementation guidance

### Proposal Structure Template:

Use this structure when creating proposals for INITIAL implementations:

**proposal.md:**
```markdown
# Change: Implement <Device> Device

## Context
- **Primary Spec**: specs/<branch-name>/spec.md (X functional requirements)
- **Secondary Hardware Spec**: <filename> (if mentioned in user input)
- **Existing Code**: simics-project/modules/<device>/<device>.dml (DML skeleton with USER-TODO placeholders)
- **Key Memory Docs**: 
  - openspec-memories/<relevant-doc-1>.md (why needed)
  - openspec-memories/<relevant-doc-2>.md (why needed)

## Why
Enable functional <device> device by implementing behavior specified in 
specs/<branch-name>/spec.md.

## What Changes
- Implement register side-effects in <device>.dml
- Implement device behavior logic (timer, interrupts, etc.)
- Add test cases to validate functionality

## Impact
- Affected specs: <branch-name>
- Affected code:
  - Modified: simics-project/modules/<device>/<device>.dml (implement USER-TODO side-effects)
  - Added: simics-project/modules/<device>/test/s-*.py (test cases)
```

**Context Section Requirements (CRITICAL):**

The Context section MUST include:
- **Primary Spec**: Location and requirement count (e.g., "96 functional requirements: FUNC-001 to FUNC-025, REG-001 to REG-010, BEHAV-001 to BEHAV-007, TEST-001 to TEST-010")
- **Secondary Hardware Spec**: If mentioned in user input (e.g., "wdt.md (Chinese hardware documentation)")
- **Existing Code**: DML skeleton location (e.g., "simics-project/modules/wdt/wdt.dml")
- **Key Memory Docs**: List 2-3 relevant memory documents with brief reason for each

**Example Context Section:**
```markdown
## Context
- **Primary Spec**: specs/001-user-input-read/spec.md (96 functional requirements: FUNC-001 to FUNC-025, REG-001 to REG-010, BEHAV-001 to BEHAV-007, TEST-001 to TEST-010)
- **Secondary Hardware Spec**: wdt.md (Chinese hardware documentation with register details)
- **Existing Code**: simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated registers)
- **Key Memory Docs**: 
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (timer implementation patterns)
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid performance pitfalls)
  - openspec-memories/06_DML_Common_Patterns.md (register side-effect patterns)
```

**specs/<branch-name>/spec.md (delta):**

For INITIAL implementations, you typically use `## ADDED Requirements` to formalize what needs to be implemented from the existing spec. Only create spec deltas if you need to clarify or add missing requirements.

```markdown
## ADDED Requirements
### Requirement: [Name from existing spec]
The device SHALL [requirement text with UPPERCASE keywords].

#### Scenario: [Success case]
- **WHEN** [condition]
- **THEN** [expected result]
```

**Key Rules for INITIAL Implementations:**
- Focus on implementing what's already in the spec, not adding new features
- Reference existing requirements by ID (e.g., "Implements FUNC-014...")
- Use the same terminology and structure as the existing spec
- Spec deltas should clarify or formalize existing requirements, not add new ones

### Common Simics Device Patterns (for reference):

- Simple register device: Register read/write side-effects only
- Timer/Counter: Register side-effects + lazy evaluation + event-based countdown + interrupts
- Watchdog: Timer pattern + reset signal + lock mechanism + reload on write
- UART: Register side-effects + data buffering + TX/RX interrupts
- Interrupt controller: Multiple inputs + priority + masking + status registers

### Universal DML Constraints (apply to ALL Simics devices):

- DML 1.4 syntax only
- Event-based timing: use `after` statement or event object with `post()` method, NOT cycle-by-cycle updates
- Session state management (use `session` keyword for state variables)
- Preserve ALL auto-generated imports in <device>.dml
- NEVER edit auto-generated files: *-registers.dml
- NEVER add new .dml files or modify XML/Makefiles

## Spec Delta Completeness Requirements (CRITICAL - Prevents Incomplete Proposals)

**CRITICAL**: Validation checks format, but you must also ensure content completeness.

### Spec Delta Approach: Requirement Extraction

**Extract ALL requirements from the source spec** as separate spec delta requirements:
- Use when source spec has detailed requirements (FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX)
- Extract each requirement as a separate spec delta requirement
- Example: "WDOGLOAD Register SHALL store 32-bit reload value"
- **Benefit**: Provides complete functional guidance to apply agent

**For implementation patterns** (DML-specific "how to implement"):
- Apply agent reads `openspec-memories/` for DML patterns and anti-patterns
- No need to duplicate implementation guidance in spec deltas
- Focus spec deltas on **what to implement**, not **how to implement**

**Target Coverage**:
- Extract 70%+ of source requirements (minimum 60% for simple devices)
- All register requirements (REG-XXX)
- All functional requirements (FUNC-XXX)
- All behavioral requirements (BEHAV-XXX)
- All test scenarios (TEST-XXX)

### Requirement Coverage Requirements

When creating spec deltas from a source specification:

1. **Requirement Coverage**: Extract ALL functional requirements from source spec
   - Count requirements in source (FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX)
   - **Target 70%+ coverage** (minimum 60% for simple devices)
   - NEVER drop requirements silently
   - NEVER summarize multiple requirements into one

2. **Test Scenario Mapping**: For each test scenario in source spec (TEST-XXX):
   - Create corresponding requirement with scenarios in spec delta
   - Map test scenarios to device states and transitions
   - Include Setup/Action/Expected format from source

3. **Behavioral Requirements**: Extract ALL state machine behaviors
   - When device is enabled/disabled (e.g., BEHAV-001: "When INTEN=0, timer shall not decrement")
   - State transitions and conditions
   - Edge cases and error conditions

4. **Register Requirements**: Extract ALL register access behaviors
   - Read-only, write-only, read-write access types
   - Side-effects for each register
   - Lock protection behaviors

5. **Pre-Validation Completeness Check**: Before running `openspec validate`, verify:
   - Count requirements in source spec (grep for `FUNC-XXX`, `REG-XXX`, `BEHAV-XXX`, `TEST-XXX`)
   - Count requirements in spec delta (grep for `### Requirement:`)
   - Calculate coverage percentage: (delta_reqs / source_reqs) × 100
   - **Target**: 70%+ coverage (minimum 60% for simple devices)
   - **Line ratio**: 25-40% of source spec size for detailed specs (500+ lines)
   - If coverage is low, extract more detailed requirements from source spec

6. **Completeness Criteria**:
   - **Coverage Target**: 70%+ requirement coverage (minimum 60% for simple devices)
   - **Line Ratio Target**: 25-40% of source spec size for detailed specs (500+ lines)
   - **Quality Check**: Spec delta should extract specific functional requirements, not just implementation patterns
   
   **Examples**:
   - Source has 100 requirements → Spec delta should have 70-100 requirements
   - Source has 20 test scenarios → Spec delta should cover all 20
   - Source has 800 lines → Spec delta should be 200-320 lines
   - Source has 10 registers → Spec delta should cover all 10 register behaviors

### Example: Spec Delta Quality

**❌ BAD** (implementation pattern, not functional requirement):
```markdown
### Requirement: Timer Implementation Pattern
The device timer SHALL use lazy evaluation and event-based timing.

#### Scenario: Lazy Evaluation
- **WHEN** counter value is read
- **THEN** value SHALL be calculated based on elapsed cycles
```
**Problem**: Only tells HOW to implement (patterns), not WHAT to implement (functionality).

**✅ GOOD** (specific functional requirement):
```markdown
### Requirement: Load Register Functionality
The LOAD register SHALL store a reload value that determines timeout period.

#### Scenario: Write to LOAD Register
- **WHEN** value is written to LOAD
- **THEN** value SHALL be stored in the register
- **AND** current counter SHALL NOT be affected until next reload
```
**Why it's good**: Extracts specific functional requirement from source spec. Apply agent knows exactly what to implement. For DML patterns (HOW to implement), apply agent reads `openspec-memories/` (e.g., `04_DML_Timing_Timer_Modeling.md`, `02_DML_Anti_Patterns.md`).

## Task Requirements (CRITICAL for Apply Agent)

**MANDATORY**: Every proposal MUST include BOTH implementation and test tasks.

### Task Structure

```markdown
## 1. DML Implementation
- [ ] 1.1 Implement register side-effects in <device>.dml
- [ ] 1.2 Implement device behavior logic
- [ ] 1.3 Handle edge cases and error conditions
- [ ] 1.4 Add session state management (if needed)

## 2. Test Implementation
- [ ] 2.1 Create test file simics-project/modules/<device>/test/s-<feature>.py
- [ ] 2.2 Implement basic functionality tests
- [ ] 2.3 Implement edge case tests
- [ ] 2.4 Implement error condition tests
- [ ] 2.5 Verify all tests pass
```

### Task Quality Requirements

Tasks must be **SPECIFIC and ACTIONABLE** with clear sub-tasks:

**Quality Checklist**:
- [ ] Each register with side-effects has dedicated sub-task
- [ ] Each sub-task specifies exact behavior (not generic "implement side-effects")
- [ ] Each sub-task references specific memory document for patterns/anti-patterns
- [ ] DML patterns specified (event-based, lazy evaluation, session state)
- [ ] Test tasks specify which TEST-XXX scenarios from spec they cover
- [ ] Minimum 3-5 sub-tasks per main task

**Example - Good Task Decomposition**:
```markdown
- [ ] 1.1 Implement CONTROL register side-effects (device.dml)
  - [ ] 1.1.1 ENABLE bit write: Start/stop device operation based on 0→1 or 1→0 transition
  - [ ] 1.1.2 MODE bits write: Configure device operating mode per spec requirements
  - [ ] 1.1.3 RESET bit write: Clear device state and reinitialize to default values
  - [ ] 1.1.4 Pattern: Use appropriate DML pattern from openspec-memories/06_DML_Common_Patterns.md
  - [ ] 1.1.5 Anti-Pattern: Check openspec-memories/02_DML_Anti_Patterns.md for device-specific pitfalls
  
- [ ] 2.1 Implement basic functionality tests (test/s-basic-operation.py)
  - [ ] 2.1.1 Test device initialization and default register values (covers TEST-001)
  - [ ] 2.1.2 Test enable/disable transitions (covers TEST-002, TEST-003)
  - [ ] 2.1.3 Test mode configuration changes (covers TEST-004)
  - [ ] 2.1.4 Setup: Use patterns from openspec-memories/02_Test_Configuration_Setup.md
```

**Device-Specific Task Patterns**:

| Device Type | Key Sub-Tasks | Reference |
|-------------|---------------|-----------|
| Timer/watchdog | Counter decrement logic, interrupt generation, reload/reset behavior | `04_DML_Timing_Timer_Modeling.md` |
| UART/serial | TX/RX buffer management, baud rate config, data ready interrupts | `06_DML_Common_Patterns.md` |
| Interrupt controller | Priority handling, masking/unmasking, pending/active status | `06_DML_Common_Patterns.md` |

### Task Guidelines

- **DML Tasks**: Modify `simics-project/modules/<device>/<device>.dml` to implement USER-TODO placeholders
- **Test Tasks**: Add `simics-project/modules/<device>/test/s-*.py` files to validate behavior
- **Actionable**: Each task must be specific enough to implement without guessing
- **Referenced**: Tasks must reference specific requirements (FUNC-XXX, REG-XXX, etc.)
- **Ordered**: DML implementation first, then tests
- **Sub-tasks**: Use numbered sub-tasks (1.1, 1.2, etc.) for clarity

## Apply Agent Handoff

When creating proposals, ensure:
- **Detailed Tasks**: All tasks in tasks.md are actionable and specific with clear sub-tasks (see Task Requirements above)
- **Both DML and Tests**: Include BOTH implementation tasks AND test tasks
- **Implementation Guidance**: Tasks reference specific DML patterns and anti-patterns to avoid
- **Complete Spec Deltas**: Include sufficient detail for implementation without guessing (see Spec Delta Completeness Requirements above for coverage criteria)
- **Clean Validation**: Validation passes completely before handoff
- **Clear Context**: Change ID is descriptive enough for apply agent to understand context

## OpenSpec Commands Reference

Use these commands during the workflow:

```bash
# Essential commands
openspec list                           # List active changes
openspec show <id>                      # Display change details
openspec show <id> --json --deltas-only # Get additional context
openspec show <spec> --type spec        # Inspect spec details
openspec validate <id> --strict         # Validate proposal (MANDATORY)
```

## Quick Start Workflows

### For Creating Proposals

**Start here:** Read `openspec/AGENTS.md` first

**Common needs:**
- Timer/watchdog proposals → `openspec-memories/02_DML_Anti_Patterns.md`
- Register device proposals → `openspec-memories/06_DML_Common_Patterns.md`
- Understanding DML → `openspec-memories/01_Simics_Modeling_Philosophy.md`
- Test planning → `openspec-memories/00_Test_Best_Practices_Index.md`

### For Validation Issues

**Quick reference:** Use `openspec show <id> --json --deltas-only` to inspect details

**Common issues:**
- Lowercase keywords → Use UPPERCASE (SHALL, MUST, etc.)
- Missing scenarios → Add `#### Scenario:` subsections
- Invalid structure → Check OpenSpec workflow documentation

## Version Information

- **Simics Version**: 7.57.0
- **DML Version**: 1.4
- **API Version**: 7
- **Last Updated**: December 23, 2025

---

**Power Type**: Knowledge Base + CLI Tools  
**Dependencies**: openspec-memories/ directory in project  
**License**: Apache 2.0
