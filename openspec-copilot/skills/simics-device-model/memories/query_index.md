# OpenSpec Memories - Query Index

## Overview

This index provides a quick reference guide for all documentation in the memories directory. Each entry includes a short description, document name, and typical queries that would benefit from referencing that document.

---

# SIMICS MODELING DOCUMENTS

## DML Best Practices Documents (Modeling)

| Description | Document Name | Possible Queries |
|-------------|---------------|------------------|
| **Master index** for all DML best practices documents with navigation and reading order recommendations | `00_DML_Best_Practices_Index.md` | "What DML documents are available?", "Where should I start learning DML?", "What's the recommended reading order?", "Show me the DML documentation structure" |
| **Core philosophy** behind Simics device modeling, explaining transaction-level modeling (TLM) and lazy evaluation principles | `01_Simics_Modeling_Philosophy.md` | "What is transaction-level modeling?", "Why use lazy evaluation?", "What's the Simics modeling philosophy?", "Should I model clock signals?", "What level of detail should I model?" |
| **Critical mistakes** to avoid in DML, including clock signal modeling, init() timing issues, and incomplete timer implementations | `02_DML_Anti_Patterns.md` | "What are DML anti-patterns?", "Why shouldn't I model clock signals?", "Can I call SIM_cycle_count in init()?", "Common DML mistakes", "Why is my timer not working?" |
| **Basic DML syntax** including device structure, registers, banks, interfaces, and core language constructs | `03_DML_Basic_Syntax.md` | "How do I declare a device?", "What's the syntax for registers?", "How do I use interfaces?", "DML basic syntax examples", "How to define methods?" |
| **Comprehensive timing guide** covering events, timers, counters, and timing-related patterns | `04_DML_Timing_Timer_Modeling.md` | "How do I implement a timer?", "What are event objects?", "How to use after statement?", "Timer countdown pattern", "How to model a watchdog timer?" |
| **Troubleshooting guide** for compilation errors, runtime issues, and common development problems | `05_DML_Troubleshooting.md` | "Why won't my DML compile?", "UTF-8 mode error", "Unknown template device", "Module load errors", "How to debug DML compilation?" |
| **Common device patterns** including interrupt devices, UART, PCI devices with complete examples | `06_DML_Common_Patterns.md` | "Device with interrupts example", "UART implementation", "PCI device template", "Common device patterns", "How to implement a basic device?" |
| **Register access scope** patterns explaining correct syntax based on code context (device/bank/register level) | `07_DML_Register_Access_Scope.md` | "How to access registers?", "Unknown identifier error", "Register scope syntax", "bank.REGISTER vs this.val", "Why can't I access my register?" |
| **Comprehensive guide** combining all DML best practices in a single document | `DML_Best_Practices.md` | "Complete DML guide", "All DML best practices", "DML full documentation", "Everything about DML" |

## Code Examples (Modeling)

| Description | Document Name | Possible Queries |
|-------------|---------------|------------------|
| **Overview and navigation** for all code examples with 9 device categories from production Simics devices | `008-code-examples/000_overview.md` | "Code examples overview", "What device examples are available?", "Production device categories", "Real DML code structure" |
| **DMA device examples** including synopsys-ahb-dmac with descriptor-based DMA patterns | `008-code-examples/001_dma.md` | "DMA implementation", "How to implement DMA?", "Descriptor-based DMA", "AHB DMAC example", "DMA controller patterns" |
| **Interrupt controller examples** including RISC-V CLINT with timer and software interrupts | `008-code-examples/002_interrupt_controller.md` | "Interrupt controller", "RISC-V CLINT", "How to implement interrupt controller?", "Software interrupts", "Timer interrupts" |
| **MMU device examples** including ARM MMU-600 (SMMUv3) and MMU-500 (SMMUv2) with address translation | `008-code-examples/003_mmu.md` | "MMU implementation", "SMMU examples", "ARM MMU", "Address translation", "Memory protection unit" |
| **PCIe device examples** with multiple capabilities, endpoint wrapper, and educational samples | `008-code-examples/004_pcie.md` | "PCIe implementation", "PCI device example", "PCIe endpoint", "PCI capabilities", "How to implement PCIe?" |
| **TRNG device example** - Synopsys True Random Number Generator implementing NIST SP800-90C | `008-code-examples/005_trng.md` | "Random number generator", "TRNG implementation", "NIST SP800-90C", "Hardware RNG", "Synopsys TRNG" |
| **I2C device examples** including synopsys-apb-i2c controller/target and I2C bus link | `008-code-examples/006_i2c.md` | "I2C implementation", "I2C controller", "I2C target", "I2C bus", "How to implement I2C?" |
| **I3C device examples** including synopsys-mipi-i3c controller implementing MIPI I3C specification | `008-code-examples/007_i3c.md` | "I3C implementation", "MIPI I3C", "I3C controller", "I3C bus", "How to implement I3C?" |
| **Timer device examples** including synopsys-apb-timers, watchdog, ARM timers with countdown patterns | `008-code-examples/008_timer.md` | "Timer implementation", "Watchdog timer", "ARM timer", "Timer countdown", "How to implement timer?", "APB timer" |
| **UART device examples** including synopsys-apb-uart and ARM PL011 with FIFOs, DMA, and interrupts | `008-code-examples/009_uart.md` | "UART implementation", "Serial port", "UART with FIFO", "PL011 UART", "How to implement UART?" |

## DML Language Reference (Modeling)

| Description | Document Name | Possible Queries |
|-------------|---------------|------------------|
| **Overview and navigation** for all 22 DML 1.4 reference documents with document structure guide | `003-DML-Language/000_overview.md` | "DML documentation overview", "What DML reference docs exist?", "DML 1.4 language guide", "Where to start with DML reference?" |
| **Lexical structure** - character encoding, reserved words, identifiers, literals, and basic syntax | `003-DML-Language/001_lexical-structure.md` | "DML lexical structure", "Reserved words", "DML identifiers", "Character encoding", "String literals in DML" |
| **Module system** - import directives, idempotent imports, and module hierarchy semantics | `003-DML-Language/002_module-system.md` | "DML module system", "How to import files?", "DML imports", "Module hierarchy", "Idempotent imports" |
| **Source file structure** - device declaration, version declaration, and file organization | `003-DML-Language/003_source-file-structure.md` | "DML file structure", "Device declaration", "Version declaration", "How to organize DML files?" |
| **Pragmas** - compiler directives including COVERITY and other pragma syntax | `003-DML-Language/004_pragmas.md` | "DML pragmas", "Compiler directives", "COVERITY pragma", "How to use pragmas?" |
| **Object model** - device objects, member objects, methods, parameters, and object hierarchy | `003-DML-Language/005_object-model.md` | "DML object model", "Device objects", "Member objects", "Object hierarchy", "What are DML objects?" |
| **Register banks and registers** - fundamental memory-mapped I/O modeling constructs | `003-DML-Language/006_registers.md` | "DML registers", "Register banks", "How to define registers?", "Memory-mapped I/O", "Register fields" |
| **Templates** - code reuse mechanism with template definition and instantiation | `003-DML-Language/007_templates.md` | "DML templates", "Template syntax", "How to use templates?", "Template inheritance", "Reusable code patterns" |
| **Parameters detailed** - typed and untyped parameters with declarations and default values | `003-DML-Language/008_parameters-detailed.md` | "DML parameters", "Parameter syntax", "Typed parameters", "Parameter defaults", "How to declare parameters?" |
| **Data types** - type system including integers, bitfields, arrays, structs, and type conversions | `003-DML-Language/009_data-types.md` | "DML data types", "Type system", "Integer types", "Bitfields", "Struct declarations", "Type conversions" |
| **Methods** - function declarations with input/output parameters, exception handling, and return values | `003-DML-Language/010_methods.md` | "DML methods", "Function syntax", "Method parameters", "Return values", "Exception handling in DML" |
| **Session variables** - runtime storage for arbitrary values without checkpointing | `003-DML-Language/011_session-variables.md` | "Session variables", "Runtime storage", "Non-checkpointed variables", "How to declare session variables?" |
| **Saved variables** - checkpointed variables that automatically create attributes | `003-DML-Language/012_saved-variables.md` | "Saved variables", "Checkpointed variables", "State persistence", "How to save device state?" |
| **Hook declarations** - suspended computations with message passing and FIFO semantics | `003-DML-Language/013_hook-declarations.md` | "DML hooks", "Hook syntax", "Suspended computations", "Message passing", "After statement hooks" |
| **Object declarations** - general syntax for declaring objects with templates and descriptions | `003-DML-Language/014_object-declarations.md` | "Object declarations", "How to declare objects?", "Object syntax", "Template inheritance", "Object types" |
| **Conditional objects** - conditionally including/excluding object declarations based on boolean expressions | `003-DML-Language/015_conditional-objects.md` | "Conditional objects", "Conditional declarations", "#if statements", "How to conditionally include objects?" |
| **In each declarations** - applying patterns to groups of objects using template matching | `003-DML-Language/016_in-each-declarations.md` | "In each syntax", "Pattern application", "Template matching", "How to apply patterns to objects?" |
| **Global declarations** - top-level declarations including imports, constants, typedefs, and externs | `003-DML-Language/017_global-declarations.md` | "Global declarations", "Import statements", "Constants", "Typedef declarations", "Extern declarations" |
| **Resolution of overrides** - detailed rules for handling multiple definitions of parameters and methods | `003-DML-Language/018_resolution-of-overrides.md` | "Override resolution", "Parameter overrides", "Method overrides", "Template ranking", "How are overrides resolved?" |
| **Comparison to C/C++** - DML's extended subset of ISO C with C++ extensions and differences | `003-DML-Language/019_comparison-to-c-cpp.md` | "DML vs C", "C++ extensions in DML", "Language differences", "ISO C subset", "What C features are in DML?" |
| **Method statements** - all available statements including assignments, control flow, and DML-specific statements | `003-DML-Language/020_method-statements.md` | "DML statements", "Assignment statements", "Control flow", "Log statements", "After statements", "Try/throw" |
| **Expressions** - operators, precedence, bit-slicing, new/delete, and DML-specific expressions | `003-DML-Language/021_expressions.md` | "DML expressions", "Operators", "Bit-slicing", "New/delete operators", "Expression syntax", "Operator precedence" |

---

# SIMICS TESTING DOCUMENTS

## Test Best Practices Documents (Testing)

| Description | Document Name | Possible Queries |
|-------------|---------------|------------------|
| **Master index** for all test best practices documents with navigation and troubleshooting guide | `00_Test_Best_Practices_Index.md` | "What test documents are available?", "Where should I start with testing?", "Test documentation structure", "How to organize tests?" |
| **Critical requirements** for test file locations and naming conventions | `01_Test_File_Location_Requirements.md` | "Where do I put test files?", "Test file location", "Why can't test-runner find my tests?", "s-*.py naming convention" |
| **Device configuration** for tests including clock setup, memory mapping, and pre-conf vs conf objects | `02_Test_Configuration_Setup.md` | "How to configure device for testing?", "Clock setup in tests", "Memory mapping", "pre_conf_object vs conf_object" |
| **Register access** patterns in tests including bank_regs usage and field testing | `03_Test_Register_Access.md` | "How to access registers in tests?", "Using dev_util.bank_regs", "Field read/write", "Register testing patterns" |
| **Fake objects** for testing device outputs like interrupts and signals | `04_Test_Device_Outputs.md` | "How to test interrupts?", "Fake object pattern", "Mocking signals", "Testing device outputs" |
| **DMA and memory** testing patterns including Layout helpers | `05_Test_DMA_Memory.md` | "How to test DMA?", "Memory testing", "Descriptor-based DMA", "Using dev_util.Layout" |
| **Events and timing** testing including timer verification and time advancement | `06_Test_Events_Timing.md` | "How to test timers?", "Event verification", "Time advancement in tests", "Testing watchdog timers" |
| **Comprehensive guide** combining all test best practices in a single document | `Test_Best_Practices.md` | "Complete testing guide", "All test best practices", "Test full documentation", "Everything about Simics testing" |

---

# USAGE GUIDE

### For Beginners

1. Start with `00_DML_Best_Practices_Index.md` to understand the documentation structure
2. Read `01_Simics_Modeling_Philosophy.md` to understand the "why" behind Simics modeling
3. Study `07_DML_Register_Access_Scope.md` to prevent scope errors (most common mistake)
4. Reference `03_DML_Basic_Syntax.md` for language basics
5. Use `06_DML_Common_Patterns.md` for practical examples

### For Timer/Counter Implementation

1. **MUST READ**: `02_DML_Anti_Patterns.md` - Avoid clock signal modeling and incomplete implementations
2. Follow: `04_DML_Timing_Timer_Modeling.md` - Complete timer patterns
3. Reference: `008-code-examples/008_timer.md` - Production timer examples

### For Testing

1. Start with `01_Test_File_Location_Requirements.md` (CRITICAL for correct file placement)
2. Learn configuration: `02_Test_Configuration_Setup.md`
3. Master register testing: `03_Test_Register_Access.md`
4. Add fake objects: `04_Test_Device_Outputs.md` for interrupt testing

### For Troubleshooting

| Problem | Reference Document |
|---------|-------------------|
| Compilation errors | `05_DML_Troubleshooting.md` |
| Register access errors | `07_DML_Register_Access_Scope.md` |
| Test files not found | `01_Test_File_Location_Requirements.md` |
| Timer not working | `02_DML_Anti_Patterns.md` + `04_DML_Timing_Timer_Modeling.md` |
| Unknown identifier | `07_DML_Register_Access_Scope.md` |

### For Language Reference

1. Start: `003-DML-Language/000_overview.md` for navigation
2. Specific syntax: Use focused documents (001-021) for detailed reference
3. Examples: Check `008-code-examples/` for real implementations

## Quick Search Patterns

### By Topic

- **Modeling Philosophy**: `01_Simics_Modeling_Philosophy.md`
- **Syntax & Language**: `03_DML_Basic_Syntax.md`, `003-DML-Language/`
- **Anti-Patterns**: `02_DML_Anti_Patterns.md`
- **Timing & Events**: `04_DML_Timing_Timer_Modeling.md`
- **Register Access**: `07_DML_Register_Access_Scope.md`
- **Common Patterns**: `06_DML_Common_Patterns.md`, `008-code-examples/`
- **Testing**: All `0X_Test_*.md` files
- **Troubleshooting**: `05_DML_Troubleshooting.md`

### By Device Type

- **Interrupts**: `06_DML_Common_Patterns.md`, `04_Test_Device_Outputs.md`
- **Timers**: `04_DML_Timing_Timer_Modeling.md`, `008-code-examples/008_timer.md`
- **UART**: `06_DML_Common_Patterns.md`, `008-code-examples/009_uart.md`
- **PCI**: `06_DML_Common_Patterns.md`, `008-code-examples/004_pcie.md`
- **DMA**: `008-code-examples/001_dma.md`, `05_Test_DMA_Memory.md`
- **I2C/I3C**: `008-code-examples/006_i2c.md`, `008-code-examples/007_i3c.md`

### By Error Message

- "unknown identifier" → `07_DML_Register_Access_Scope.md`
- "syntax error at device" → `05_DML_Troubleshooting.md`
- "cannot find dml-builtins" → `05_DML_Troubleshooting.md`
- "Queue not set" → `02_Test_Configuration_Setup.md`
- "No tests found" → `01_Test_File_Location_Requirements.md`

## Document Metadata

- **Total Documents**: 18 markdown files + 2 directories (003-DML-Language/, 008-code-examples/)
- **Last Updated**: December 2025
- **Tested With**: Simics 7.57.0, DML 1.4, API version 7
- **Coverage**: Complete beginner to advanced DML and testing documentation

## Related Resources

- **Full Indexes**: 
  - `00_DML_Best_Practices_Index.md` - Navigation for DML documents
  - `00_Test_Best_Practices_Index.md` - Navigation for test documents
- **Complete Guides**:
  - `DML_Best_Practices.md` - All DML content in one file
  - `Test_Best_Practices.md` - All test content in one file
- **Code Examples**: 
  - `008-code-examples/000_overview.md` - Production code navigation
  - `003-DML-Language/000_overview.md` - Language reference navigation
