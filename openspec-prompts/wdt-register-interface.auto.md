# Watchdog Timer Register Interface - Complete OpenSpec Workflow (Autonomous)

**AUTONOMOUS EXECUTION**: Complete all phases from proposal creation through archiving without waiting for approval.

Please implement the watchdog timer register interface following the complete OpenSpec workflow from start to finish. Follow the autonomous execution rules in your instruction - do not stop for approval between phases.

## Context

I have a comprehensive watchdog timer specification from spec-kit that includes detailed register definitions and behavior. I want to extract and organize the register interface aspects into a proper OpenSpec specification, implement it, and archive it.

## IMPORTANT - Path Discovery (Do This First)

Before starting, discover the actual paths in this project:

```bash
# 1. Get current git branch (spec directory is named specs/<git-branch-name>/)
git branch --show-current

# 2. Find the device name
ls simics-project/modules/

# 3. Verify the spec file exists
ls specs/<git-branch-name>/spec.md
```

**Use these discovered values throughout the workflow:**
- Spec file: `specs/<git-branch-name>/spec.md`
- Device directory: `simics-project/modules/<device_name>/`
- DML files: `simics-project/modules/<device_name>/<device_name>.dml`
- Tests: `simics-project/modules/<device_name>/test/`

## What to Implement

Create an OpenSpec change proposal `add-<device_name>-register-interface` that:

1. **Extracts register interface requirements** from the existing comprehensive spec
2. **Creates focused specification** for register behavior, access patterns, and validation  
3. **Defines clear requirements** for DML implementation of register map
4. **Includes lock mechanism** and security aspects
5. **Implements the DML code** for all registers
6. **Creates comprehensive tests** for register access and lock mechanism
7. **Archives the completed change**

## What to Leverage from Existing Spec

Extract these sections from `specs/<git-branch-name>/spec.md`:
- Register Map with all registers (WDOGLOAD, WDOGVALUE, WDOGCONTROL, etc.)
- Detailed register behavior descriptions with offsets
- Lock mechanism with magic value 0x1ACCE551
- Register access patterns and validation rules
- Reset values and field definitions

## Expected Workflow

You should autonomously complete all these phases:

1. **Assess current state** - Discover paths, read specs, constitution, best practices
2. **Create change proposal** - Use OpenSpec workflow to create proposal.md, tasks.md, and spec delta
3. **Implement the change** - Write DML code and tests, mark tasks as complete
4. **Archive the change** - Run `openspec archive` command
5. **Provide final status** - Report success or known issues with next steps

## Critical Requirements for Implementation

### Files to Edit
- **ONLY** edit these files (replace `<device_name>` with discovered device):
  - DML register definitions: `simics-project/modules/<device_name>/<device_name>-registers.dml`
  - DML main device: `simics-project/modules/<device_name>/<device_name>.dml`
  - Python unit tests: `simics-project/modules/<device_name>/test/*.py`

### ABSOLUTE REQUIREMENTS
- Keep ALL import statements intact - NEVER remove:
  - `import "<device_name>-glue.dml";` (auto-generated during build)
  - `import "<device_name>-dia.dml";` (defines register interface)
  - `import "simics/devs/signal.dml";` (defines signal interfaces)

### FORBIDDEN ACTIONS
❌ Removing or commenting out ANY import statements
❌ Creating new .dml files (<device_name>-data-model.dml, <device_name>-glue.dml)
❌ Modifying config/XML/Makefiles
❌ Editing auto-generated files (<device_name>-dia.dml, <device_name>-glue.dml)
❌ Stopping after proposal creation - MUST complete all phases
❌ Stopping after implementation - MUST archive
❌ Asking for permission mid-workflow - EXECUTE AUTONOMOUSLY

### DML Implementation Requirements
- Use proper DML 1.4 syntax
- Implement register read/write handlers with side effects
- Follow patterns from `.specify/memory/DML_Device_Development_Best_Practices.md`
- Implement lock mechanism state management
- Add proper error handling for locked register access

### Python Test Requirements
- **MUST READ**: `.specify/memory/DML_Device_Development_Best_Practices.md` (Section: Python Test File Structure)
- One test function per file (pattern: `s-<feature>.py`)
- Configure clock queue for device: `device.queue = clk`
- Use proper register access patterns: `bank = dev_util.bank_regs(device.bank.BANK_NAME)`
- Use assertions: `stest.expect_equal(actual, expected, "msg")`

## Execution Instructions

**DO NOT WAIT FOR APPROVAL - Execute all four phases autonomously:**

1. ✅ Create the complete change proposal (Phase 1)
2. ✅ Implement all tasks (Phase 2)
3. ✅ Archive the completed change (Phase 3)
4. ✅ Provide final status report (Phase 4)

**When you're done**, you should have:
- ✅ Empty `openspec/changes/` directory (change moved to archive)
- ✅ Populated `openspec/changes/archive/add-<device_name>-register-interface/`
- ✅ Working DML implementation in `simics-project/modules/<device_name>/<device_name>-registers.dml` and `<device_name>.dml`
- ✅ Complete test suite in `simics-project/modules/<device_name>/test/`
- ✅ Successful build (`gmake <device_name>` passes)
- ✅ Test results (passing or documented failures)
- ✅ Git commit with the implementation
- ✅ Final status report with next steps

**Start now and complete all phases without stopping.**
