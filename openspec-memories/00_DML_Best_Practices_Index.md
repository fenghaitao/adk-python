# DML Best Practices - Document Index

## Overview

This is the master index for the DML Best Practices documentation. The original comprehensive guide has been split into focused, single-subject documents for easier reference and learning.

## Document Structure

The documentation is organized into 7 focused documents:

### 1. [Simics Modeling Philosophy](01_Simics_Modeling_Philosophy.md)
**Focus**: Core principles and philosophy behind Simics device modeling

**Topics Covered**:
- Transaction-Level Device Modeling (TLM)
- Simics High-Level Modeling Approach
- Why not to model unnecessary detail
- Core modeling principles summary

**When to Read**: Start here to understand the fundamental philosophy before writing any DML code.

---

### 2. [DML Anti-Patterns](02_DML_Anti_Patterns.md)
**Focus**: Critical mistakes to avoid when writing DML code

**Topics Covered**:
- Clock signal modeling (MOST COMMON MISTAKE)
- Calling timing APIs in init()/post_init()
- Incomplete timer/counter implementations
- Cycle-by-cycle updates
- Other common anti-patterns

**When to Read**: Review this before starting any new device, especially timer-related devices. Refer back when debugging performance issues.

---

### 3. [DML Basic Syntax and Structure](03_DML_Basic_Syntax.md)
**Focus**: Fundamental DML syntax, compilation, and basic programming constructs

**Topics Covered**:
- DML compilation setup and flags
- Basic DML syntax and device structure
- DML core constructs (parameters, attributes, banks, registers, interfaces, templates, methods, variables)
- File organization and naming conventions
- Documentation and logging best practices

**When to Read**: Essential reference for all DML development. Keep this handy while coding.

---

### 4. [DML Timing and Timer Modeling](04_DML_Timing_Timer_Modeling.md)
**Focus**: Comprehensive guide to timing features and timer device implementation

**Topics Covered**:
- Core timing mechanisms (`after` statement, event objects)
- Timer counter modeling patterns (lazy evaluation, HPET, countdown, watchdog, TSC, periodic, comparator)
- Complete timer device examples (relative and absolute timers)
- Timing constants and conversions
- Best practices and quick reference

**When to Read**: Essential for any device with timing behavior (timers, counters, watchdogs, periodic events).

---

### 5. [DML Troubleshooting](05_DML_Troubleshooting.md)
**Focus**: Solutions to common compilation errors, runtime issues, and development problems

**Topics Covered**:
- Compilation issues (syntax errors, missing imports, UTF-8 mode)
- Runtime issues (AttributeError, module_load.py problems)
- Testing and build issues (forgotten rebuilds)
- Common mistakes and debugging tips

**When to Read**: When you encounter errors or unexpected behavior. Use as a diagnostic checklist.

---

### 6. [DML Common Patterns and Examples](06_DML_Common_Patterns.md)
**Focus**: Practical, reusable patterns and complete examples for common device types

**Topics Covered**:
- Basic memory-mapped device
- Device with interrupts
- Complete UART example
- Simple PCI device
- When to use each pattern

**When to Read**: When starting a new device implementation. Copy and adapt these patterns to your needs.

---

### 7. [DML Register Access Scope Patterns](07_DML_Register_Access_Scope.md) **CRITICAL**
**Focus**: Register access syntax based on code context (device/bank/register level)

**Topics Covered**:
- Device-level register access (`bank.REGISTER.val`)
- Bank-level register access (`REGISTER.val`)
- Register-level access (`this.val`)
- Common "unknown identifier" errors and fixes
- Pre-build checklist for scope errors
- Real-world examples from WDT implementation

**When to Read**: **MANDATORY before ANY DML implementation**. This prevents 100% of register scope compilation errors. Review before first build.

---

## Quick Navigation Guide

### I want to...

**...start ANY DML implementation** **CRITICAL**  
→ **FIRST** read [07_DML_Register_Access_Scope.md](07_DML_Register_Access_Scope.md) to prevent scope errors

**...understand Simics modeling philosophy**  
→ Start with [01_Simics_Modeling_Philosophy.md](01_Simics_Modeling_Philosophy.md)

**...avoid common mistakes**  
→ Read [02_DML_Anti_Patterns.md](02_DML_Anti_Patterns.md) first

**...learn DML syntax**  
→ Study [03_DML_Basic_Syntax.md](03_DML_Basic_Syntax.md)

**...implement a timer device**  
→ Follow [04_DML_Timing_Timer_Modeling.md](04_DML_Timing_Timer_Modeling.md)

**...fix compilation/runtime errors**  
→ Check [05_DML_Troubleshooting.md](05_DML_Troubleshooting.md)

**...fix "unknown identifier" errors**  
→ Check [07_DML_Register_Access_Scope.md](07_DML_Register_Access_Scope.md)

**...build a specific device type**  
→ Use templates from [06_DML_Common_Patterns.md](06_DML_Common_Patterns.md)

---

## Recommended Reading Order

### For ALL Implementations (MANDATORY):
1. **07_DML_Register_Access_Scope.md** - **READ FIRST** to prevent scope errors

### For Beginners:
1. **07_DML_Register_Access_Scope.md** - **MANDATORY** - Prevent scope errors
2. **01_Simics_Modeling_Philosophy.md** - Understand the "why"
3. **02_DML_Anti_Patterns.md** - Learn what NOT to do
4. **03_DML_Basic_Syntax.md** - Learn the language
5. **06_DML_Common_Patterns.md** - Practice with examples
6. **05_DML_Troubleshooting.md** - Keep handy for issues

### For Timer/Counter Devices:
1. **07_DML_Register_Access_Scope.md** - **MANDATORY** - Prevent scope errors
2. **01_Simics_Modeling_Philosophy.md** - Understand lazy evaluation principle
3. **02_DML_Anti_Patterns.md** - **CRITICAL**: Read anti-patterns 1, 2, and 3
4. **04_DML_Timing_Timer_Modeling.md** - Complete guide and examples
5. **05_DML_Troubleshooting.md** - For debugging

### For Quick Reference:
- **07_DML_Register_Access_Scope.md** - Register scope quick reference (check before every build)
- **03_DML_Basic_Syntax.md** - Syntax quick reference
- **04_DML_Timing_Timer_Modeling.md** - Timing quick reference card
- **06_DML_Common_Patterns.md** - Copy-paste templates

---

## Document Maintenance

### Original Source
All documents extracted from: `DML_Best_Practices.md`

### Extraction Date
December 11, 2025

### Tested With
- Simics: 7.57.0
- DML: 1.4
- API: version 7

### Content Principles
All content is extracted **exactly** from the original best practices document. No external knowledge or common assumptions have been added. Each document contains only verified, tested information.

### Updates
When updating any document:
1. Maintain single-subject focus
2. Do not mix contexts between documents
3. Extract only from verified sources
4. Test all code examples
5. Update "Last Updated" timestamp
6. Cross-reference related documents when needed

---

## Memory Loading Protocol for AI Agents

This section provides token-efficient loading strategies for AI agents implementing DML device code.l

### Core Protocol

1. **ALWAYS read this index file FIRST** - It provides the roadmap for all DML implementation tasks
2. **Use task-specific guidance below** to identify which 1-2 additional documents are relevant
3. **Load ONLY the specific documents needed** - Avoid loading all documents to preserve token budget
4. **These documents use DML syntax** (C-like): `method`, `this.val`, `uint64`, `bank.REGISTER.val`, etc.

### Task-Specific Document Loading

#### For ANY DML Implementation (MANDATORY)
- **MUST read FIRST**: `07_DML_Register_Access_Scope.md`
- **Why**: Prevents 100% of register scope compilation errors
- **Prevents**: "unknown identifier REGISTER" errors, "REGISTER is not a member" errors

#### For Timer/Watchdog/Counter Devices (CRITICAL)
**Load in this order:**
1. `07_DML_Register_Access_Scope.md` (MANDATORY for all implementations)
2. `02_DML_Anti_Patterns.md` (CRITICAL - read anti-patterns 1, 2, and 3)
   - Anti-Pattern #1 (clock signal modeling): Causes 100-1000x performance degradation
   - Anti-Pattern #2 (SIM_cycle_count in init): Causes runtime crashes
   - Anti-Pattern #3 (incomplete timer): Causes non-functional devices
   - **Reading anti-patterns FIRST prevents generating "obvious but wrong" code**
3. `04_DML_Timing_Timer_Modeling.md` (Complete implementation guide)

**Why this order**: Anti-patterns MUST be known before implementation to avoid generating broken code that needs extensive fixing.

#### For Register Side-Effects Implementation
- **Core**: `07_DML_Register_Access_Scope.md` (MANDATORY)
- **Patterns**: `06_DML_Common_Patterns.md` (Common device patterns)

#### For Compilation Errors
- **Scope errors** ("unknown identifier"): `07_DML_Register_Access_Scope.md`
- **Other errors**: `05_DML_Troubleshooting.md`

#### For New DML Developers
**Recommended reading order:**
1. `07_DML_Register_Access_Scope.md` (MANDATORY - prevents scope errors)
2. `01_Simics_Modeling_Philosophy.md` (Understand the "why")
3. `02_DML_Anti_Patterns.md` (Learn what NOT to do)
4. `03_DML_Basic_Syntax.md` (Learn the language)

### Anti-Pattern Prevention Strategy

**CRITICAL**: For timer/counter/watchdog devices, reading anti-patterns BEFORE implementation is essential because:

1. **Performance**: Anti-Pattern #1 (clock signal modeling) seems "obvious" but causes 100-1000x slowdown
2. **Stability**: Anti-Pattern #2 (timing APIs in init) causes immediate crashes
3. **Functionality**: Anti-Pattern #3 (incomplete timer) results in non-functional devices
4. **Prevention is cheaper than fixing**: Avoiding these patterns is far more efficient than generating broken code and then debugging it

**Strategy**: Load `02_DML_Anti_Patterns.md` FIRST (after scope guide) for any timing-related device.

### Troubleshooting Document Map

| Symptom | Document to Load |
|---------|------------------|
| "unknown identifier REGISTER" | `07_DML_Register_Access_Scope.md` |
| "REGISTER is not a member of bank" | `07_DML_Register_Access_Scope.md` |
| Device builds but runs very slowly | `02_DML_Anti_Patterns.md` (Anti-Pattern #1) |
| Runtime crash on device init | `02_DML_Anti_Patterns.md` (Anti-Pattern #2) |
| Timer doesn't count down | `02_DML_Anti_Patterns.md` (Anti-Pattern #3) + `04_DML_Timing_Timer_Modeling.md` |
| Syntax errors | `03_DML_Basic_Syntax.md` + `05_DML_Troubleshooting.md` |
| Missing imports | `05_DML_Troubleshooting.md` |

### Pre-Build Checklist (Token-Efficient Validation)

Before building, verify against this checklist (found in referenced documents):

- [ ] Register access uses correct scope (device/bank/register level) - `07_DML_Register_Access_Scope.md`
- [ ] No clock signal modeling anti-pattern - `02_DML_Anti_Patterns.md`
- [ ] No timing API calls in init/post_init - `02_DML_Anti_Patterns.md`
- [ ] Timer implementation includes interrupt logic - `02_DML_Anti_Patterns.md`

### Token Budget Optimization

**Efficient Loading Pattern:**
```
1. Load this index (00_DML_Best_Practices_Index.md) → ~2K tokens
2. Identify task from "Task-Specific Document Loading" section
3. Load 1-2 specific documents (typically 3-8K tokens each)
4. Total: ~5-15K tokens vs ~40K+ for loading all documents
```

**When to load additional documents:**
- Load on-demand when encountering specific issues
- Use troubleshooting map for error-driven loading
- Reference quick navigation sections for targeted reads

## Additional Resources

### See Also
- Simics Model Builder User's Guide
- DML 1.4 Reference Manual
- Simics API documentation

### Getting Help
1. Check troubleshooting guide first
2. Review anti-patterns document
3. Verify your code against examples
4. Use the quick reference sections

---

**Document Status**: Complete  
**Last Updated**: December 17, 2025  
**Total Documents**: 7 focused guides + this index

**Recent Updates**:
- December 17, 2025: Added "Memory Loading Protocol for AI Agents" section with token-efficient loading strategies
- December 15, 2025: Added `07_DML_Register_Access_Scope.md` based on session analysis findings
