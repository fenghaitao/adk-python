---
name: "openspec-apply"
displayName: "OpenSpec Apply"
description: "Complete OpenSpec apply workflow for Simics DML device implementation with domain knowledge and build/test tools"
keywords: ["openspec", "apply", "simics", "dml", "device-modeling", "hardware-simulation", "python-tests", "register-access", "timer-devices", "watchdog", "uart"]
author: "ADK Team"
---

# OpenSpec Apply Power

This power provides complete OpenSpec apply workflow execution for Simics DML device implementation, including domain knowledge and build/test tools.

## What This Power Provides

1. **OpenSpec Workflow** - Complete apply phase execution following `openspec/AGENTS.md`
2. **Knowledge Base** - DML and test documentation in `openspec-memories/`
3. **Build & Test Tools** - MCP tools: `build_simics_project`, `run_simics_test`

## Scope

- This power handles the OpenSpec Apply phase for Simics device implementations
- Implement DML device code and tests based on approved proposals
- Keep the scope tight and changes minimal unless explicitly expanded

## Guardrails

- Favor straightforward, minimal implementations first and add complexity only when requested or clearly required
- Keep changes tightly scoped to the requested outcome
- Identify any vague or ambiguous details and ask necessary follow-up questions before editing files

## CRITICAL: Execution Steps (FOLLOW THIS SEQUENCE)

You MUST execute these steps in EXACT order. Do NOT skip any step or jump ahead.

**STEP 1: Read OpenSpec Workflow Documentation (DO THIS FIRST)**
- IMMEDIATELY read `openspec/AGENTS.md` before doing anything else
- This provides the complete OpenSpec workflow conventions and directory structure
- Focus on the "Implementing Changes" section for apply phase guidance

**STEP 2: Load Context and Implement**
- Follow "Stage 2: Implementing Changes" workflow from openspec/AGENTS.md
- Use Simics-Specific Implementation Guidance below for device patterns and hardware specs
- Follow TDD approach: tests first, then DML implementation
- Build iteratively using these Simics MCP tools:
  - `build_simics_project(/absolute/path/to/workspace/simics-project, <device-name>)` - Build DML code after each change
  - **If MCP tool fails**, use bash: `cd /absolute/path/to/workspace/simics-project && make <device-name>`
- When encountering build failures:
  - Check `openspec-memories/05_DML_Troubleshooting.md`
  - Verify register scope patterns (device/bank/register level)

**STEP 2.5: Implementation Completeness Check (MANDATORY BEFORE TESTING)**

Before running tests, verify you've implemented BEHAVIOR, not just structure:

**Checklist:**
1. Timer/Watchdog devices: Countdown logic with `after` or event posting implemented?
2. Interrupt devices: Interrupt signal raising/lowering implemented?
3. Register side-effects: Write operations trigger actual behavior (not just storage)?
4. Review `changes/<id>/tasks.md`: All functional requirements implemented?

**Red Flag Detection:**
- If all tests fail with identical errors across 2+ runs → Missing functionality, not test issues
- If build succeeds but no behavior → Implemented structure without logic

**Action if Red Flag:** Stop testing, implement missing functionality first.

**STEP 3: Test and Validate Quality**
- Run tests using: `run_simics_test(/absolute/path/to/workspace/simics-project, <device-name>)`
  - **If MCP tool fails**, use bash: `cd /absolute/path/to/workspace/simics-project && ./bin/test-runner`
- When encountering test failures:
  - Check troubleshooting table in `openspec-memories/00_Test_Best_Practices_Index.md`
  - Verify implementation completeness (return to STEP 2.5)

**STEP 4: Report Status**
- Build MUST succeed without warnings
- Report test results (partial passing is acceptable):
  - For failing tests: explain why they fail and what's needed to fix them
  - Distinguish between: missing functionality vs incorrect implementation vs test issues
- Confirm no anti-patterns introduced (check against Universal DML Constraints below)
- Update tasks.md to reflect completed vs remaining work

## Memory Loading Protocol (CRITICAL - for token-efficient knowledge loading)

1. **MANDATORY**: Read BOTH index files FIRST before any other memory documents:
   - MUST read `openspec-memories/00_DML_Best_Practices_Index.md` (for DML implementation guidance)
   - MUST read `openspec-memories/00_Test_Best_Practices_Index.md` (for test creation guidance)
   - These provide the roadmap for selecting additional documents

2. Use the indices' "I want to..." or "For Specific Tasks" sections to identify which 1-2 additional documents are relevant to your current task

3. Load ONLY the specific documents needed (avoid loading all documents - be token-efficient)

4. CRITICAL ANTI-PATTERN PREVENTION:
   - For timer/counter/watchdog devices: MUST read `openspec-memories/02_DML_Anti_Patterns.md` FIRST before any DML implementation
     - Anti-Pattern #1 (clock signal modeling) causes 100-1000x performance degradation
     - Anti-Pattern #2 (SIM_cycle_count in init) causes runtime crashes
     - Anti-Pattern #3 (incomplete timer) causes non-functional devices
     - Reading anti-patterns first prevents generating "obvious but wrong" code that needs fixing

   - For test creation: MUST read `openspec-memories/01_Test_File_Location_Requirements.md` FIRST before creating any test files
     - Wrong location causes test-runner failures
     - Wrong patterns cause test functions not to execute

## Test Configuration Requirements (CRITICAL)

When implementing timer/watchdog devices, test configuration MUST include clock setup:

**Required in `test/<device>_common.py`:**

```python
import conf

def create_<device>():
    # Create clock with frequency
    clk = conf.sim.create_object("clock", "clk", [["freq_mhz", 100]])
    
    # Create device
    dev = conf.sim.create_object("<device>", "dev", [])
    
    # CRITICAL: Assign clock's queue to device
    dev.queue = clk
    
    return dev
```

**Why This Matters:**
- Timer devices use `SIM_cycle_count()` which requires a valid queue
- Without clock/queue setup, tests fail with: "object has no valid queue attribute"
- This is Anti-Pattern #2 from `openspec-memories/02_DML_Anti_Patterns.md`

**Pre-Test Checklist:**
- [ ] Clock created with `freq_mhz` parameter
- [ ] Device's `queue` attribute assigned to clock
- [ ] Test configuration loaded before device operations

**Reference**: See `openspec-memories/02_Test_Configuration_Setup.md` for complete examples

## Signal Interface Safety (CRITICAL)

When implementing signal interfaces (interrupt, reset, etc.), ALWAYS add NULL checks:

**Pattern for DML signal interfaces:**

```dml
connect wdogint {
    interface signal;
    
    method signal_raise() {
        // CRITICAL: Check if signal is connected before calling
        if (this.obj != NULL) {
            this.signal.signal_raise();
        }
    }
    
    method signal_lower() {
        // CRITICAL: Check if signal is connected before calling
        if (this.obj != NULL) {
            this.signal.signal_lower();
        }
    }
}
```

**Why This Matters:**
- Signal interfaces may not be connected in test configurations
- Calling signal methods on unconnected interfaces causes segmentation faults
- NULL checks prevent crashes while allowing tests to run

**Anti-Pattern (causes segfault):**
```dml
method signal_raise() {
    this.signal.signal_raise();  // ❌ No NULL check - crashes if not connected
}
```

**When to Use:**
- ALL signal interface implementations (interrupt, reset, DMA, etc.)
- Before ANY call to `this.signal.*` methods
- In both `signal_raise()` and `signal_lower()` methods

   - For test configuration helpers (wdt_common.py, etc.): MUST read `openspec-memories/02_Test_Configuration_Setup.md` FIRST
     - Missing clock setup causes "object has no valid queue attribute" runtime crashes
     - Must set clk.freq_mhz BEFORE instantiation
     - Must assign dev.queue = clk for all timing-based devices
     - Wrong pattern causes SIM_cycle_count() and timing functions to fail

5. Quick reference for task-specific loading:
   
   **DML Implementation Tasks:**
   - **ANY DML implementation** → MUST read `openspec-memories/07_DML_Register_Access_Scope.md` FIRST (prevents 100% of scope errors)
   - Timer/watchdog devices → `openspec-memories/02_DML_Anti_Patterns.md` + `openspec-memories/04_DML_Timing_Timer_Modeling.md`
   - Register side-effects → `openspec-memories/06_DML_Common_Patterns.md`
   - Compilation errors → `openspec-memories/05_DML_Troubleshooting.md`
   - New to DML → `openspec-memories/01_Simics_Modeling_Philosophy.md` + `openspec-memories/03_DML_Basic_Syntax.md`
   
   **Test Creation Tasks:**
   - Creating first tests → `openspec-memories/01_Test_File_Location_Requirements.md` + `openspec-memories/02_Test_Configuration_Setup.md`
   - Creating test configuration helpers (e.g., wdt_common.py, device_common.py) → `openspec-memories/02_Test_Configuration_Setup.md` (CRITICAL for clock/queue setup)
   - Register testing → `openspec-memories/03_Test_Register_Access.md`
   - Timer testing → `openspec-memories/06_Test_Events_Timing.md`
   - Test errors → Use troubleshooting table in `openspec-memories/00_Test_Best_Practices_Index.md`

## Simics-Specific Implementation Guidance

When implementing changes, your primary context sources are:

1. **Proposal Context** (PRIMARY - read these first):
   - `changes/<id>/proposal.md` - What's being built and why
   - `changes/<id>/tasks.md` - Implementation checklist
   - `changes/<id>/design.md` - Technical decisions (if exists)

2. **DML and Test Best Practices** (ESSENTIAL):
   - Follow Memory Loading Protocol above to load relevant knowledge from openspec-memories/
   - These provide implementation patterns and anti-patterns to avoid

3. **Specifications** (OPTIONAL - only if clarification needed):
   - Primary: `specs/<branch-name>/spec.md` - Use `find specs -name "spec.md" -type f` to locate
   - Secondary: Hardware specification file (if mentioned in proposal.md)
   - Use these only when proposal context needs additional clarification

### Universal DML Constraints (apply to ALL implementations)

- DML 1.4 syntax only
- Event-based timing: use `after` statement or event object with `post()` method, NOT cycle-by-cycle updates
- Session state management (use `session` keyword for state variables)
- Preserve ALL auto-generated imports in <device>.dml
- NEVER edit auto-generated files: *-registers.dml, *-glue.dml
- NEVER add new .dml files or modify XML/Makefiles

### Common Simics Device Patterns (for reference):
- Simple register device: Register read/write side-effects only
- Timer/Counter: Register side-effects + lazy evaluation + event-based countdown + interrupts
- Watchdog: Timer pattern + reset signal + lock mechanism + reload on write
- UART: Register side-effects + data buffering + TX/RX interrupts
- Interrupt controller: Multiple inputs + priority + masking + status registers

### MCP Tool Path Requirements (SSE Transport)

**ALWAYS use ABSOLUTE paths** for ALL Simics MCP tools:
- **WHY**: SSE transport MCP servers run in different process/directory context
- **NEVER use relative paths** like `"./simics-project"` or `"simics-project"` or `"../project"`
- **HOW**: Get workspace root first, then construct absolute paths

**Example workflow:**
```python
# 1. Get workspace root
workspace_root = bash_command(command="pwd")  # Returns "/home/user/workspace"

# 2. Construct absolute path
project_path = workspace_root + "/simics-project"

# 3. Use absolute path in MCP tools
build_simics_project(project_path=project_path, module="<device-name>")
run_simics_test(project_path=project_path, module="<device-name>")
```

## Knowledge Base Location

All Simics DML development documentation is in your project at:

```
openspec-memories/
├── 00_DML_Best_Practices_Index.md      # START HERE for DML
├── 00_Test_Best_Practices_Index.md     # START HERE for tests
├── 01_Simics_Modeling_Philosophy.md
├── 02_DML_Anti_Patterns.md
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

## Available MCP Servers

### simics-sse-server

**Connection:** SSE transport at `http://localhost:8056/sse`
**Authentication:** None required (local server)

**Tools:**

1. **build_simics_project** - Build DML device modules
   - Required: `project_path` (string) - Absolute path to Simics project
   - Required: `module` (string) - Module name to build
   - Returns: Build result with success/failure status

2. **run_simics_test** - Execute Python tests
   - Required: `project_path` (string) - Absolute path to Simics project
   - Optional: `module` (string) - Module name to test (if omitted, runs all tests)
   - Returns: Test results with pass/fail status

**Note**: The MCP server must be running separately. The power provides documentation access regardless of MCP server availability.

## OpenSpec Commands Reference

Use these commands during the workflow:

```bash
# Essential commands
openspec list                  # List active changes
openspec show <id>             # Display change details
openspec show <id> --json --deltas-only  # Get additional context during implementation
openspec validate <id>         # Validate changes
```

## Quick Start Workflows

### For DML Implementation

**Start here:** `openspec-memories/00_DML_Best_Practices_Index.md`

**Common needs:**
- Register scope patterns → `07_DML_Register_Access_Scope.md`
- Avoid performance issues → `02_DML_Anti_Patterns.md`
- Timer/watchdog devices → `04_DML_Timing_Timer_Modeling.md`
- Compilation errors → `05_DML_Troubleshooting.md`

### For Test Creation

**Start here:** `openspec-memories/00_Test_Best_Practices_Index.md`

**Common needs:**
- Test file location → `01_Test_File_Location_Requirements.md`
- Device configuration → `02_Test_Configuration_Setup.md`
- Register testing → `03_Test_Register_Access.md`
- Timing tests → `06_Test_Events_Timing.md`

### For Troubleshooting

**Quick reference:** `openspec-memories/05_DML_Troubleshooting.md`

**Common issues:**
- "unknown identifier" errors → Register scope patterns
- "object has no valid queue attribute" → Clock configuration
- Tests not running → File location requirements
- Timer not working → Event-based timing patterns

## Version Information

- **Simics Version**: 7.57.0
- **DML Version**: 1.4
- **API Version**: 7
- **Last Updated**: December 16, 2025

---

**Power Type**: Knowledge Base + MCP Tools  
**Dependencies**: openspec-memories/ directory in project  
**License**: Apache 2.0
