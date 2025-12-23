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
DML skeleton exists at simics-project/modules/<device>/ with auto-generated 
register structure and USER-TODO placeholders. Using specification at 
specs/<branch-name>/spec.md to implement register side-effects and device behavior.

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
