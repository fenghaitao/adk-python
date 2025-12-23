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

## Scope

- This power handles the OpenSpec Proposal phase for **INITIAL implementations** (skeleton → working code)
- DML skeleton already exists with auto-generated register structure and USER-TODO placeholders
- The goal is to implement the device behavior specified in the existing spec, not to add new features
- Keep the scope tight and changes minimal unless explicitly expanded

**CRITICAL**: This is for implementing what's already specified in `specs/<branch-name>/spec.md`, not for adding new requirements or features.

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

**STEP 3: Load Relevant DML Knowledge (if needed for implementation details)**
- Follow Memory Loading Protocol below to load relevant openspec-memories/ documents
- Only load 1-2 documents specific to your proposal needs (be token-efficient)
- **For timer/watchdog devices**: Read `openspec-memories/02_DML_Anti_Patterns.md` FIRST to avoid critical mistakes

**STEP 4: Create Proposal and Spec Deltas**
- Follow OpenSpec workflow from `openspec/AGENTS.md` for proposal structure and spec delta creation
- Apply Simics-specific context, scope, device patterns, and DML constraints (see Simics-Specific Implementation Guidance below)
- **Reference specific requirements from the existing spec** by ID (e.g., "Building on FUNC-014..." or "Extends TEST-004...")
- Ensure compliance with Spec Format Requirements (UPPERCASE keywords: SHALL, MUST; `#### Scenario:` sections)
- Match the style, terminology, and structure of the existing spec
- Use ADDED for new requirements, MODIFIED for changes to existing requirements (include full updated text)
- **Create tasks.md with BOTH DML implementation tasks AND test tasks** (see Task Structure Requirements below)

**STEP 5: Validate (MANDATORY)**
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

**PREREQUISITE**: You MUST have already read the existing spec file (see STEP 2 above) before using this guidance.

The user input provides the purpose (what device/feature to implement) and may include references to hardware specifications.

### Information Sources (in priority order):

1. **Primary Specification** (MANDATORY - already read in STEP 2): `specs/<branch-name>/spec.md`
   - **Authoritative source** for device requirements and behavior
   - Contains: hardware spec, operational model, existing requirements (FUNC-XXX, REG-XXX, etc.), test scenarios (TEST-XXX)
   - **Your proposal MUST**: Reference and extend this spec, not duplicate or contradict it
   - **Example references**: "Building on FUNC-014 (clock divider requirements)..." or "Extends TEST-004 to cover edge case..."

2. **Secondary Hardware Specification** (optional - if mentioned in user input):
   - Look for: "Hardware Specification: documented in `<filename>`" in user input
   - Use when: Primary spec needs clarification on hardware details
   - Contains: Comprehensive hardware details, register definitions, operational behavior

3. **DML and Test Best Practices** (optional - for implementation patterns):
   - Follow Memory Loading Protocol above to load relevant knowledge from `openspec-memories/`
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

**Why Context Matters:**
- Apply agent knows where to find detailed requirements
- Apply agent knows which memory documents to load
- Reduces apply agent search time by 60%
- Provides clear implementation context

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

## Spec Format Requirements (Prevents Validation Failures)

**CRITICAL**: Follow these rules exactly to pass validation:

1. **Requirement keywords**: MUST be UPPERCASE
   - ✅ Correct: SHALL, SHOULD, MAY, MUST, MUST NOT
   - ❌ Wrong: shall, should, may, must, must not

2. **Scenarios**: Each requirement MUST have at least one `#### Scenario:` subsection
   - ✅ Correct: `#### Scenario: Success case`
   - ❌ Wrong: `### Scenario:` or `**Scenario:**`

3. **Delta operations**: Use proper section headers
   - ✅ Correct: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`
   - ❌ Wrong: `## Added Requirements`, `## New Requirements`

4. **MODIFIED requirements**: Include complete updated text
   - Must match existing requirement name exactly (whitespace-insensitive)
   - Include ALL content (not just changes)
   - See OpenSpec workflow documentation for details

## Spec Delta Completeness Requirements (CRITICAL - Prevents Incomplete Proposals)

**CRITICAL**: Validation checks format, but you must also ensure content completeness.

When creating spec deltas from a source specification:

1. **Requirement Coverage**: Extract ALL functional requirements from source spec
   - Count requirements in source (FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX)
   - Ensure spec delta includes equivalent coverage (80%+ minimum)
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

5. **Pre-Validation Check**: Before running `openspec validate`, verify:
   ```bash
   # Count requirements in source spec
   SOURCE_REQS=$(grep -E "^\*\*(FUNC|REG|BEHAV|TEST)-" specs/<branch>/spec.md | wc -l)
   
   # Count spec delta requirements
   DELTA_REQS=$(grep -c "^### Requirement:" openspec/changes/<id>/specs/*/spec.md)
   
   # Calculate coverage
   COVERAGE=$((DELTA_REQS * 100 / SOURCE_REQS))
   
   # Ensure 80%+ coverage
   if [ $COVERAGE -lt 80 ]; then
     echo "ERROR: Only $COVERAGE% requirement coverage (need 80%+)"
     echo "Source has $SOURCE_REQS requirements, spec delta has $DELTA_REQS"
     echo "Review source spec and extract missing requirements"
     exit 1
   fi
   ```

6. **Completeness Criteria**:
   - Source has 96 requirements → Spec delta should have 75-90 requirements (not 5)
   - Source has 15 test scenarios → Spec delta should cover all 15
   - If source has 800+ lines → Spec delta should be 200-400 lines (not 73)

**Quality Checklist**: See `openspec-memories/10_Proposal_Quality_Checklist.md` for automated quality checks.

## Task Structure Requirements (CRITICAL for Apply Agent)

**MANDATORY**: Every proposal MUST include BOTH implementation and test tasks.

### Required Task Structure:

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

### Task Guidelines:

- **DML Tasks**: Modify `simics-project/modules/<device>/<device>.dml` to implement USER-TODO placeholders
- **Test Tasks**: Add `simics-project/modules/<device>/test/s-*.py` files to validate behavior
- **Actionable**: Each task must be specific enough to implement without guessing
- **Referenced**: Tasks must reference specific requirements (FUNC-XXX, REG-XXX, etc.)
- **Ordered**: DML implementation first, then tests
- **Sub-tasks**: Use numbered sub-tasks (1.1, 1.2, etc.) for clarity

## Task Decomposition Requirements (CRITICAL - Ensures Actionable Tasks)

Tasks must be SPECIFIC and ACTIONABLE with clear sub-tasks:

**BAD (too vague):**
```markdown
- [ ] 1.1 Implement register side-effects in wdt.dml
```

**GOOD (specific and actionable):**
```markdown
- [ ] 1.1 Implement WDOGCONTROL register side-effects (wdt.dml)
  - [ ] 1.1.1 INTEN bit write: Reload counter from WDOGLOAD on 0→1 transition
  - [ ] 1.1.2 RESEN bit write: Enable/disable reset output generation
  - [ ] 1.1.3 step_value[4:2] write: Set clock divider (000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16)
  - [ ] 1.1.4 Pattern: Use event-based timing (see openspec-memories/04_DML_Timing_Timer_Modeling.md)
  - [ ] 1.1.5 Anti-Pattern: NEVER model clock signal directly (causes 100-1000x slowdown)
  
- [ ] 1.2 Implement WDOGINTCLR register side-effects (wdt.dml)
  - [ ] 1.2.1 Any write: Clear WDOGRIS[0] and WDOGMIS[0]
  - [ ] 1.2.2 Any write: Deassert wdogint signal
  - [ ] 1.2.3 Any write: Reload counter from WDOGLOAD
  
- [ ] 1.3 Implement WDOGLOCK register side-effects (wdt.dml)
  - [ ] 1.3.1 Write 0x1ACCE551: Unlock other registers for write access
  - [ ] 1.3.2 Write any other value: Lock other registers from write access
  - [ ] 1.3.3 Read: Return 0x0 if unlocked, 0x1 if locked
```

**Task Quality Checklist:**
- [ ] Each register with side-effects has dedicated sub-task
- [ ] Each sub-task specifies exact behavior (not "implement side-effects")
- [ ] Each sub-task references specific memory document
- [ ] Anti-patterns explicitly called out with consequences
- [ ] DML patterns specified (event-based, lazy evaluation, etc.)
- [ ] Test tasks specify which TEST-XXX scenarios to cover
- [ ] Minimum 3-5 sub-tasks per main task

### Apply Agent Handoff Checklist:

- **Detailed Tasks**: All tasks in tasks.md are actionable and specific with clear sub-tasks
- **Both DML and Tests**: Include BOTH implementation tasks AND test tasks
- **Implementation Guidance**: Tasks reference specific DML patterns and anti-patterns to avoid
- **Complete Spec Deltas**: Include sufficient detail for implementation without guessing
- **Clean Validation**: Validation passes completely before handoff
- **Clear Context**: Change ID is descriptive enough for apply agent to understand context

## Knowledge Base Location

All Simics DML development documentation is in your project at:

```
openspec-memories/
├── 00_DML_Best_Practices_Index.md      # START HERE for DML
├── 00_Test_Best_Practices_Index.md     # START HERE for tests
├── 01_Simics_Modeling_Philosophy.md
├── 02_DML_Anti_Patterns.md             # CRITICAL: Read before timer/watchdog
├── 03_DML_Basic_Syntax.md
├── 04_DML_Timing_Timer_Modeling.md
├── 05_DML_Troubleshooting.md
├── 06_DML_Common_Patterns.md
├── 07_DML_Register_Access_Scope.md
├── 01_Test_File_Location_Requirements.md
├── 02_Test_Configuration_Setup.md
├── 03_Test_Register_Access.md
├── 04_Test_Device_Outputs.md
├── 05_Test_DMA_Memory.md
└── 06_Test_Events_Timing.md
```

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
