# Simics Model Test Best Practices - Master Index

## Overview

This is the master index for Simics device model testing documentation. The content has been organized into focused, independent documents to make learning and reference easier.

## Document Organization

Each document focuses on a single testing subject without mixing contexts:

### Core Documents

| Document | Focus | When to Read |
|----------|-------|--------------|
| [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md) | ⚠️ **CRITICAL** - Where to create test files, test patterns | **READ FIRST** - Before creating any test |
| [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md) | Device configuration, clocks, memory mapping, common.py template | Setting up test environment |
| [03_Test_Register_Access](03_Test_Register_Access.md) | Register and field testing patterns | Testing device registers |
| [04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md) | Mocking interfaces and dependencies | Isolating device under test |
| [05_Test_DMA_Memory](05_Test_DMA_Memory.md) | DMA and memory testing | Testing DMA operations |
| [06_Test_Events_Timing](06_Test_Events_Timing.md) | Time-dependent behavior testing | Testing timers and events |

## Quick Navigation

### For First-Time Test Writers

**Recommended Reading Order:**
1. Start with [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md) - **CRITICAL** to avoid location errors
2. Read [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md) - Learn minimal config and common.py patterns
3. Read [03_Test_Register_Access](03_Test_Register_Access.md) - Basic register testing
4. Reference others as needed (04, 05, 06) for specific features

### For Specific Testing Tasks

- **Creating test files?** → [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md)
- **Configuring device?** → [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md)
- **Testing registers?** → [03_Test_Register_Access](03_Test_Register_Access.md)
- **Need to mock interfaces?** → [04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md)
- **Testing DMA?** → [05_Test_DMA_Memory](05_Test_DMA_Memory.md)
- **Testing timers?** → [06_Test_Events_Timing](06_Test_Events_Timing.md)
- **Need common.py template?** → [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md) (see "Complete common.py Template" section)

### For Troubleshooting

Common issues and solutions:

| Problem | Document to Check |
|---------|-------------------|
| Test files not found by test-runner | [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md) |
| "Queue not set" error | [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md) |
| Segfault on test run | [04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md) |
| Register access errors | [03_Test_Register_Access](03_Test_Register_Access.md) |
| Events don't fire | [06_Test_Events_Timing](06_Test_Events_Timing.md) |
| DMA verification fails | [05_Test_DMA_Memory](05_Test_DMA_Memory.md) |
| Test functions not executing | [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md) (see "s-*.py Test Files" section) |

## Document Dependencies

```
01_Test_File_Location_Requirements (standalone - no dependencies)
    ↓
02_Test_Configuration_Setup (requires understanding of file location)
    ↓
03_Test_Register_Access (builds on configuration)
    ↓
04_Test_Fake_Objects_Mocking (uses configuration patterns)
05_Test_DMA_Memory (uses configuration + register access)
06_Test_Events_Timing (uses configuration + register access)
```

## Best Practices Summary

### Essential Rules (Read These First)

1. ✅ **Test Location**: Tests MUST be in `simics-project/modules/<device>/test/`
2. ✅ **Clock Setup**: Set `clk.freq_mhz` BEFORE `SIM_add_configuration()`
3. ✅ **Return conf_object**: Return `conf.<name>` from `create_config()`, NOT pre-conf objects
4. ✅ **Bank Access**: Use `dev_util.bank_regs(device.bank.<bank_name>)`, read DML for exact name
5. ✅ **Call Test Functions**: If you wrap test code in a function, MUST call it at the end

### Common Anti-Patterns to Avoid

- ❌ Creating tests in `simics_project/` (underscore) instead of `simics-project/` (hyphen)
- ❌ Setting clock frequency after `SIM_add_configuration()`
- ❌ Missing `.bank.` namespace when accessing registers
- ❌ Scanning/discovering bank names dynamically instead of reading DML
- ❌ Defining test functions but forgetting to call them

## Document Status

- **Extracted From**: Test_Best_Practices.md
- **Split Date**: December 12, 2025
- **Total Documents**: 6 focused documents + this index
- **Tested With**: Simics 7.57.0, Simics Model Builder

## Using This Documentation

1. **Start here** for navigation and overview
2. **Follow recommended reading order** for first-time users
3. **Jump to specific topics** using quick navigation
4. **Use troubleshooting table** when encountering errors
5. **Reference individual documents** for deep dives into specific testing areas

---

## Memory Loading Protocol for AI Agents

This section provides token-efficient loading strategies for AI agents implementing Python test code for Simics devices.

### Core Protocol

1. **ALWAYS read this index file FIRST** - It provides the roadmap for all test implementation tasks
2. **Use task-specific guidance below** to identify which 1-2 additional documents are relevant
3. **Load ONLY the specific documents needed** - Avoid loading all documents to preserve token budget
4. **These documents use Python syntax**: `def`, `regs.REG.read()`, `stest.expect_equal()`, `conf.obj`, etc.

### Task-Specific Document Loading

#### For Creating First Test Files (CRITICAL)
**Load in this order:**
1. `01_Test_File_Location_Requirements.md` (MANDATORY - prevents test location errors)
   - **Why**: Wrong location causes tests to not be found by test-runner
   - **Prevents**: Tests in `simics_project/` instead of `simics-project/`, missing `test/` directory
2. `02_Test_Configuration_Setup.md` (Setup and configuration patterns)
   - **Why**: Incorrect setup causes runtime crashes
   - **Critical info**: Clock setup MUST happen before `SIM_add_configuration()`

#### For Creating Test Configuration Helpers (wdt_common.py, device_common.py, etc.)
- **CRITICAL**: `02_Test_Configuration_Setup.md`
- **Why**: Missing clock setup causes "object has no valid queue attribute" runtime crashes
- **Must implement**:
  - Set `clk.freq_mhz` BEFORE calling `SIM_add_configuration()`
  - Assign `dev.queue = clk` for all timing-based devices
  - Return `conf.<name>` (not pre-conf objects) from `create_config()`

#### For Register Testing
- **Core**: `03_Test_Register_Access.md`
- **Covers**: `regs.REG.read()`, `regs.REG.write()`, field access, bank namespace patterns

#### For Timer/Event Testing
- **Core**: `06_Test_Events_Timing.md`
- **Covers**: `SIM_cycle_count()`, `SIM_continue()`, event callbacks, timeout verification

#### For Interface Mocking
- **Core**: `04_Test_Fake_Objects_Mocking.md`
- **Covers**: Fake object patterns, interface implementation, segfault prevention

#### For DMA Testing
- **Core**: `05_Test_DMA_Memory.md`
- **Covers**: Memory setup, DMA verification, memory read/write patterns

### Anti-Pattern Prevention Strategy

**CRITICAL**: Reading location and configuration documents BEFORE test creation is essential because:

1. **Location errors**: Tests in wrong directory are silently ignored (no error message)
2. **Clock setup**: Wrong order causes "no valid queue" crashes that are hard to debug
3. **Test function execution**: Missing test function calls result in no tests running
4. **Prevention is cheaper than debugging**: Getting setup right first time is far more efficient than debugging cryptic runtime errors

**Strategy**: Load `01_Test_File_Location_Requirements.md` + `02_Test_Configuration_Setup.md` FIRST for any new test.

### Troubleshooting Document Map

| Symptom | Document to Load |
|---------|------------------|
| Test files not found by test-runner | `01_Test_File_Location_Requirements.md` |
| "Queue not set" / "no valid queue attribute" error | `02_Test_Configuration_Setup.md` |
| Segfault on test run | `04_Test_Fake_Objects_Mocking.md` |
| Register access errors / AttributeError | `03_Test_Register_Access.md` |
| Events don't fire / timing issues | `06_Test_Events_Timing.md` |
| DMA verification fails | `05_Test_DMA_Memory.md` |
| Test functions not executing | `01_Test_File_Location_Requirements.md` (see "s-*.py Test Files" patterns) |
| `SIM_cycle_count()` fails | `02_Test_Configuration_Setup.md` (check clock/queue setup) |

### Pre-Test-Run Checklist (Token-Efficient Validation)

Before running tests, verify against this checklist (found in referenced documents):

- [ ] Tests in `simics-project/modules/<device>/test/` directory - `01_Test_File_Location_Requirements.md`
- [ ] Test files named `s-*.py` for Simics test runner - `01_Test_File_Location_Requirements.md`
- [ ] Clock frequency set BEFORE `SIM_add_configuration()` - `02_Test_Configuration_Setup.md`
- [ ] Test functions called at end of file (if wrapped) - `01_Test_File_Location_Requirements.md`
- [ ] Bank access uses `.bank.<bank_name>` namespace - `03_Test_Register_Access.md`

### Token Budget Optimization

**Efficient Loading Pattern:**
```
1. Load this index (00_Test_Best_Practices_Index.md) → ~2K tokens
2. Identify task from "Task-Specific Document Loading" section
3. Load 1-2 specific documents (typically 3-6K tokens each)
4. Total: ~5-12K tokens vs ~25K+ for loading all documents
```

**When to load additional documents:**
- Load on-demand when encountering specific issues
- Use troubleshooting map for error-driven loading
- Reference quick navigation sections for targeted reads

### Common Test Anti-Patterns to Avoid

These are covered in detail in the referenced documents:

- ❌ Using `this.val` in Python tests (that's DML syntax, not Python)
- ❌ Using Python `def` functions in .dml files (wrong language)
- ❌ Using DML `method` declarations in .py files (wrong language)
- ❌ Consulting DML docs (`0*_DML_*.md`) when writing Python tests
- ❌ Consulting Test docs (`0*_Test_*.md`) when writing DML code
- ❌ Setting clock frequency after `SIM_add_configuration()`
- ❌ Creating tests in `simics_project/` (underscore) instead of `simics-project/` (hyphen)
- ❌ Missing `.bank.` namespace when accessing registers

---

**Document Status**: Complete  
**Last Updated**: December 17, 2025  
**Total Documents**: 6 focused guides + this index

**Recent Updates**:
- December 17, 2025: Added "Memory Loading Protocol for AI Agents" section with token-efficient loading strategies

---

**Next Steps**: If this is your first time writing Simics tests, start with [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md).
