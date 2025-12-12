# DML Best Practices - Document Index

## Overview

This is the master index for the DML Best Practices documentation. The original comprehensive guide has been split into focused, single-subject documents for easier reference and learning.

## Document Structure

The documentation is organized into 6 focused documents:

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

## Quick Navigation Guide

### I want to...

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

**...build a specific device type**  
→ Use templates from [06_DML_Common_Patterns.md](06_DML_Common_Patterns.md)

---

## Recommended Reading Order

### For Beginners:
1. **01_Simics_Modeling_Philosophy.md** - Understand the "why"
2. **02_DML_Anti_Patterns.md** - Learn what NOT to do
3. **03_DML_Basic_Syntax.md** - Learn the language
4. **06_DML_Common_Patterns.md** - Practice with examples
5. **05_DML_Troubleshooting.md** - Keep handy for issues

### For Timer/Counter Devices:
1. **01_Simics_Modeling_Philosophy.md** - Understand lazy evaluation principle
2. **02_DML_Anti_Patterns.md** - **CRITICAL**: Read anti-patterns 1, 2, and 3
3. **04_DML_Timing_Timer_Modeling.md** - Complete guide and examples
4. **05_DML_Troubleshooting.md** - For debugging

### For Quick Reference:
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

**Document Status**: ✅ Complete  
**Last Updated**: December 11, 2025  
**Total Documents**: 6 focused guides + this index
