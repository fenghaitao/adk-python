# Research: Simics Watchdog Timer Device Implementation

## DML Learning Prerequisites (Simics Projects Only)

**⚠️ CRITICAL FOR SIMICS PROJECTS**: Two comprehensive DML learning documents must be studied in the tasks phase before writing any DML code:

1. `.specify/memory/DML_Device_Development_Best_Practices.md` - Patterns and pitfalls
2. `.specify/memory/DML_grammar.md` - Complete DML 1.4 language specification

**During /plan Phase**:
- ✅ Execute RAG queries for device patterns and examples
- ✅ Document RAG results in research.md
- ❌ DO NOT read the DML learning documents yet (they will be studied in tasks phase)

**In Tasks Phase**: Mandatory tasks T013-T014 will require complete study of these documents with comprehensive note-taking in research.md before any implementation

## Environment Discovery

### Simics Version
{
  "package_name": "Simics-Base",
  "package_number": "1000",
  "package_version": "7.57.0"
}

### Installed Packages
| Package Name | Package Number | Package Version |
|-------------|----------------|-----------------|
| Simics-Base | 1000 | 7.57.0 |
| SystemC-Library | 1013 | 7.17.0 |
| Crypto-Engine | 1030 | 7.14.0 |
| GDB | 1031 | 7.9.0 |
| Python | 1033 | 7.13.0 |
| RISC-V-CPU | 2050 | 7.21.0 |
| RISC-V-Simple | 2053 | 7.12.0 |
| QSP-x86 | 2096 | 7.38.0 |
| Training | 6010 | 7.0.0-pre.11 |
| Docea-Base | 7801 | 7.0.0-pre.5 |
| QSP-CPU | 8112 | 7.14.0 |
| QSP-ISIM | 8144 | 7.0.0-pre.2 |

### Available Platforms
Available Remote Manifests
No entries
Available Local Manifests
 Name                                                      Group            
 Public Intel® Simics® Quick Start Platform (QSP-x86) - 7  qsp-x86-public-7 


## Documentation Access (via RAG Queries)

### DML 1.4 Reference Manual
- **Query**: "DML 1.4 reference manual register and device modeling"
- **Source Type**: docs
- **Key Findings**:
  * Key differences between DML 1.2 and DML 1.4 syntax including inline method calls, return value declarations, and object array syntax
  * Built-in templates that are automatically instantiated for different object types (register, device, etc.)
  * Template inheritance patterns and how to properly override template parameters
- **References**: DML 1.4 Reference Manual, Changes from DML 1.2 to DML 1.4
- **Application**: Structure the watchdog timer with appropriate register definitions and field breakdowns following DML 1.4 syntax
- **Note**: This provides initial context; detailed grammar rules from DML_grammar.md will be studied in tasks phase

### Model Builder User Guide
- **Query**: "Simics Model Builder device creation and structure patterns"
- **Source Type**: docs
- **Key Findings**:
  * Standard functionality in DML is implemented in templates with built-in templates for each object type
  * Interface templates specify programming interfaces and often require explicit instantiation
  * Template hierarchy for parameter override behavior with strict rules for determining which declarations take precedence
- **References**: Device Modeling Language 1.4 Reference Manual, Libraries and Built-ins
- **Application**: Follow established patterns for device structure and implementation approach
- **Note**: This provides architectural context; detailed best practices from DML_Device_Development_Best_Practices.md will be studied in tasks phase

### DML Device Template
- **Query**: "DML device template base structure and skeleton"
- **Source Type**: dml
- **Key Patterns**:
  * Device declaration with dml 1.4; and device name
  * Register banks with parameters (register_size, byte_order)
  * Register declarations with size, offset, and behavior templates
  * Field declarations with @ bit range syntax
  * Session variable declarations for checkpointed state
- **Code Examples**:
  ```dml
  dml 1.4;
  
  device sample_timer_device;
  param desc = "sample timer device";
  param documentation = "This is the <class>sample_timer_device</class> "
                            + "class, an example of how timer devices "
                            + "can be written in Simics.";
  
  import "utility.dml";
  import "simics/devs/signal.dml";
  
  connect irq_dev is signal_connect {
      param documentation = "Device an interrupt should be forwarded to "
                                + "(interrupt controller)";
  }
  
  bank regs {
      param register_size = 2;
      param byte_order = "big-endian";
      param use_io_memory = false;
  
      // Records the time when the counter register was started.
      saved cycles_t counter_start_time;
      // Records the start value of the counter register.
      saved cycles_t counter_start_value;
  
      register counter   @ 0x0 "Counter register";
      register reference @ 0x2 "Reference counter register";
      register step      @ 0x4
          "Counter is incremented every STEP clock cycles. 0 means stopped.";
      register config    @ 0x6 "Configuration register" {
          field clear_on_match @ [1]
              "If 1, counter is cleared when counter matches reference.";
          field interrupt_enable @ [0]
              "If 1, interrupt is enabled.";
      }
  }
  ```
- **Application**: Structure the watchdog timer device following standard DML skeleton patterns

## Device Example Analysis (via RAG Queries)

### Device-Specific Best Practices
- **Query**: "Best practices for watchdog timer device modeling with Simics DML 1.4"
- **Source Type**: source
- **Key Patterns Observed**:
  * Use of saved variables for checkpointed state (counter_start_time, counter_start_value)
  * Register-specific method implementations (get, read, write) for custom behavior
  * Event posting with after statements for timer-based functionality
  * Connect interfaces for interrupt signaling to other devices
  * Proper use of cancel_after() to manage pending events
- **Code Examples**:
  ```dml
  bank regs {
      register counter is (get, read, write) {
          param configuration = "none";
  
          method write(uint64 value) {
              counter_start_value = value;
              restart();
          }
  
          method get() -> (uint64) {
              if (step.val == 0) {
                  return counter_start_value;
              }
  
              local cycles_t now = SIM_cycle_count(dev.obj);
              return (now - counter_start_time) / step.val
                  + counter_start_value;
          }
  
          method read() -> (uint64) {
              return get();
          }
  
          method restart() {
              counter_start_time = SIM_cycle_count(dev.obj);
              update_event();
          }
  
          method on_match() {
              log info, 4: "Counter matches reference";
  
              if (regs.config.clear_on_match.val) {
                  regs.counter.write(0);
              }
  
              if (regs.config.interrupt_enable.val) {
                  log info, 4: "Raising interrupt";
  
                  irq_dev.set_level(1);
                  irq_dev.set_level(0);
              }
          }
  
          method update_event() {
              cancel_after();
  
              if (step.val == 0)
                  return;
  
              local cycles_t now = SIM_cycle_count(dev.obj);
              local cycles_t cycles_left =
                  (reference.val - counter_start_value) * step.val
                  - (now - counter_start_time);
              after cycles_left cycles: on_match();
          }
      }
  }
  ```
- **Relevant Structures**: Timer-based event handling and interrupt signaling patterns applicable to watchdog functionality
- **Application**: Apply timer device patterns to implement watchdog timeout and interrupt generation

### Simics Device Reference Example
- **Query**: "Simics device implementation example watchdog timer or similar peripheral"
- **Source Type**: source
- **Key Patterns Observed**:
  * Register banks with specific register_size and byte_order parameters
  * Register arrays with index parameters for multiple similar registers
  * Field definitions with bit-level access for configuration registers
  * Connect interfaces for signal and interrupt handling
  * Event-based timing mechanisms with after statements
- **Code Examples**:
  ```dml
  bank regs {
      param register_size = 2;
      param byte_order = "big-endian";
      param use_io_memory = false;
  
      // Records the time when the counter register was started.
      saved cycles_t counter_start_time;
      // Records the start value of the counter register.
      saved cycles_t counter_start_value;
  
      register counter   @ 0x0 "Counter register";
      register reference @ 0x2 "Reference counter register";
      register step      @ 0x4
          "Counter is incremented every STEP clock cycles. 0 means stopped.";
      register config    @ 0x6 "Configuration register" {
          field clear_on_match @ [1]
              "If 1, counter is cleared when counter matches reference.";
          field interrupt_enable @ [0]
              "If 1, interrupt is enabled.";
      }
  }
  ```
- **Applicable Patterns**: Timer counter implementation, interrupt signaling, and register field definitions for configuration
- **Application**: Adapt timer device patterns to watchdog timer implementation requirements

### Register Implementation Patterns
- **Query**: "DML register bank implementation patterns"
- **Source Type**: dml
- **Implementation Patterns**:
  * Register declarations with address offsets (@) and descriptive names
  * Field definitions with bit ranges (@ [msb:lsb]) for bit-level access
  * Register method implementations (read, write, get, set) for custom behavior
  * Register groups for organizing related registers
  * Parameter inheritance for register defaults
- **Code Examples**:
  ```dml
  bank regs {
      register config    @ 0x6 "Configuration register" {
          field clear_on_match @ [1]
              "If 1, counter is cleared when counter matches reference.";
          field interrupt_enable @ [0]
              "If 1, interrupt is enabled.";
      }
  }
  
  bank regs {
      register counter is (get, read, write) {
          method write(uint64 value) {
              counter_start_value = value;
              restart();
          }
  
          method get() -> (uint64) {
              // Implementation
          }
  
          method read() -> (uint64) {
              return get();
          }
      }
  }
  ```
- **Application**: Implement watchdog timer register bank following standard patterns with appropriate customization

## Test Example Analysis (via RAG Queries)

### Simics Python Test Patterns
- **Query**: "Simics Python test patterns and examples"
- **Source Type**: python
- **Key Test Patterns Observed**:
  * Use of dev_util.Register_LE for register access testing
  * stest.expect_equal for assertion-based validation
  * simics.SIM_create_object for device instance creation
  * Register read/write operations for functional testing
  * Attribute access for backing register values
- **Code Examples**:
  ```python
  import dev_util
  import simics
  import stest
  
  # Create the python device.
  py_dev = simics.SIM_create_object('empty_device_confclass',
                                    'empty_dev_confclass')
  
  # Add register definition for the device's register.
  register = dev_util.Register_LE(py_dev.bank.regs, 0, size = 1)
  
  # Test the register.
  a = register.read()
  register.write(a + 1)
  b = register.read()
  stest.expect_equal(b, a + 1)
  
  # Also test the 'r1' attribute which backs the register.
  stest.expect_equal(py_dev.r1, b)
  c = b + 1
  py_dev.r1 = c
  stest.expect_equal(py_dev.r1, c)
  stest.expect_equal(register.read(), c)
  ```
- **Test Framework**: stest, dev_util, simics modules for testing infrastructure
- **Application**: Structure tests for watchdog timer following established test patterns and conventions

### Device Testing Best Practices
- **Query**: "Simics device testing best practices"
- **Source Type**: source
- **Best Practices Identified**:
  * Register read/write testing with dev_util.Register_LE
  * Value validation using stest.expect_equal assertions
  * Attribute access testing for backing register values
  * Functional behavior testing through register operations
  * Error condition testing for edge cases
- **Code Examples**:
  ```python
  import dev_util
  import simics
  import stest
  
  # Create the python device.
  py_dev = simics.SIM_create_object('empty_device_confclass',
                                    'empty_dev_confclass')
  
  # Add register definition for the device's register.
  register = dev_util.Register_LE(py_dev.bank.regs, 0, size = 1)
  
  # Test the register.
  a = register.read()
  register.write(a + 1)
  b = register.read()
  stest.expect_equal(b, a + 1)
  ```
- **Applicable Practices**: Register access testing, value validation, and functional behavior verification
- **Application**: Apply comprehensive testing practices to ensure watchdog timer correctness and reliability

## Additional Research (Requirement-Driven RAG Queries)

### Additional Query #9: ARM PrimeCell watchdog timer register behaviors and interrupt generation
- **Query**: "ARM PrimeCell watchdog timer register behaviors and interrupt generation"
- **Source Type**: source
- **Match Count**: 5
- **Requirement Addressed**: FR-001 (32-bit watchdog timer compatible with ARM PrimeCell specification), FR-004 (interrupt on first timeout and system reset on second timeout)
- **Knowledge Gap**: Understanding of ARM PrimeCell watchdog timer register behaviors and interrupt generation mechanisms
- **Key Findings**:
  * Timer devices use events for periodic or timeout behavior with after statements
  * Interrupt generation requires connect interfaces to signal other devices
  * Register fields control interrupt enable/disable functionality
  * Status registers track interrupt and reset conditions
- **Code Examples**:
  ```dml
  register reg_c {
      field IRQF[7] is (clear_on_read) "Interrupt Request Flag";
      field PF[6]   is (clear_on_read) "Periodic Interrupt Flag";
      field AF[5]   is (clear_on_read) "Alarm Flag";
      field UF[4]   is (clear_on_read) "Update-Ended Flag";
      method before_read(memop) {
          // Implementation for updating interrupt flags
      }
      method after_read(memop) {
          call $update_interrupt();
      }
  }
  
  method update_interrupt() {
      // Implementation for updating interrupt signals
  }
  ```
- **Application**: Implement interrupt generation and status tracking following ARM PrimeCell patterns

### Additional Query #10: Watchdog timer device register map and behavior DML implementation
- **Query**: "watchdog timer device register map and behavior DML implementation"
- **Source Type**: dml
- **Match Count**: 5
- **Requirement Addressed**: FR-002 (21 registers including control, data, status, lock, integration test, and ID registers), FR-005 (lock protection mechanism with magic unlock value)
- **Knowledge Gap**: Specific register map implementation patterns for watchdog timers
- **Key Findings**:
  * Timer devices implement register-specific behaviors through method overrides
  * Configuration registers use fields for bit-level access to control parameters
  * Lock mechanisms use special registers with magic values for protection
  * Integration test registers provide direct signal control for testing
- **Code Examples**:
  ```dml
  bank regs {
      register counter   @ 0x0 "Counter register";
      register reference @ 0x2 "Reference counter register";
      register step      @ 0x4
          "Counter is incremented every STEP clock cycles. 0 means stopped.";
      register config    @ 0x6 "Configuration register" {
          field clear_on_match @ [1]
              "If 1, counter is cleared when counter matches reference.";
          field interrupt_enable @ [0]
              "If 1, interrupt is enabled.";
      }
  }
  ```
- **Application**: Implement comprehensive register map with appropriate field definitions and behaviors

## DML Best Practices Study Notes

### Device Structure and Syntax
- **Device Declaration**: Device declarations in DML 1.4 are single lines without braces, e.g., `device my_device;`
- **No Braces After Device**: Unlike older versions, DML 1.4 does not use braces after device declarations
- **Parameters Placement**: Parameters go at the top level, not inside device blocks
- **Required Imports**: Always include `import "simics/device-api.dml";` for devices

### Memory-Mapped Device Implementation
- **Bank Declaration**: Use `bank` to define memory-mapped regions with parameters like `function` (base address) and `register_size`
- **Register Definition**: Registers are defined with `@` offset, size, and optional descriptions
- **Field Definitions**: Use `field` with `@ [msb:lsb]` notation for bit-level access to register bits

### Common Patterns
- **Interrupt Handling**: Use `connect` declarations for interrupt interfaces and call `signal_raise()`/`signal_lower()` methods
- **Timer Implementation**: Use `event` declarations and `after` statements for timing functionality
- **State Management**: Use `saved` variables for checkpointed state that persists across simulation saves/loads

### Best Practices
- **File Organization**: Organize code with clear structure: imports, device declaration, parameters, banks, registers, methods
- **Naming Conventions**: Use lowercase_with_underscores for device names, register names, and parameters
- **Documentation**: Always include meaningful descriptions for devices, registers, and parameters
- **Error Handling**: Implement proper error checking in methods with appropriate logging
- **Logging**: Use appropriate log levels (info, warning, error) for different types of messages

### Compilation Requirements
- **Compiler Flags**: Use correct flags: `--simics-api=6 -I ../linux64/bin/dml/api/6/1.4 -I ../linux64/bin/dml/1.4`
- **UTF-8 Mode**: Ensure Python runs in UTF-8 mode with `export PYTHONUTF8=1`
- **Include Paths**: Both API and builtins directories must be included in the include paths

## DML Grammar Study Notes

### Language Structure
- **Version**: DML 1.4 is a declarative language with imperative elements for device modeling
- **Type System**: Static typing with C-like type declarations
- **Compilation**: Compiles to C code that interfaces with Simics API

### Key Elements
- **Keywords**: Includes device-specific keywords like `register`, `field`, `bank`, `connect`, `event`, etc.
- **Operators**: Standard arithmetic, bitwise, logical, and comparison operators with C-like precedence
- **Literals**: Integer (decimal, hex, binary), floating point, string, character, and boolean literals

### Grammar Structure
- **Top-Level**: Device declaration followed by statements
- **Object Declarations**: Registers, fields, banks, groups, ports, attributes, connections, interfaces, events
- **Data Declarations**: Session variables (runtime), saved variables (checkpointed), parameters (compile-time/runtime)
- **Method Declarations**: With support for return values, exception handling, and various qualifiers

### Object Hierarchy
- **Device Root**: All objects are children of the device
- **Bank as Container**: Banks contain registers and groups
- **Register Fields**: Fields are children of registers for bit-level access

### Template System
- **Inheritance**: Objects can inherit from templates using `is` clauses
- **Multiple Inheritance**: Supported with proper parameter override rules
- **Shared Methods**: Can be defined in templates and overridden

### Expressions and Statements
- **Expression Types**: Rich set of expressions including literals, identifiers, operators, function calls, and type operations
- **Statement Types**: Compound, expression, declaration, control flow (if, while, for, switch), exception handling (try/catch)
- **Special Statements**: DML-specific statements like `log`, `assert`, `after` (for events)

### Type System
- **C Compatibility**: Uses C-compatible types with extensions
- **Special Types**: Sequence types, hook types, layout types, bitfields types
- **Type Operations**: Cast, typeof, sizeoftype, new, delete

## Architecture Decisions

### Decision: Use DML 1.4 for device implementation
- **Rationale**: DML 1.4 is the current standard for Simics device modeling with better syntax and features than DML 1.2
- **Alternatives Considered**: DML 1.2, but it's deprecated and lacks modern features
- **Source**: get_simics_version() and documentation access RAG queries
- **Impact**: Implementation will follow DML 1.4 syntax and patterns

### Decision: Implement timer-based event handling for watchdog functionality
- **Rationale**: Timer devices in Simics use event posting with after statements for timing behavior
- **Alternatives Considered**: Direct cycle counting, but event-based approach is standard
- **Source**: Device example analysis RAG queries
- **Impact**: Watchdog will use after statements for timeout detection

### Decision: Use register fields for bit-level access to control registers
- **Rationale**: Register field definitions with @ bit range syntax provide clean access to individual control bits
- **Alternatives Considered**: Bit manipulation in methods, but fields are more maintainable
- **Source**: Register implementation patterns RAG queries
- **Impact**: Control registers will use field definitions for configuration bits

## Implementation Results

### Device Implementation Summary
The watchdog timer device has been successfully implemented as a DML 1.4 device with the following features:

#### Register Implementation
- **21 Registers**: All registers as specified in the ARM PrimeCell specification
- **Register Types**: 
  - WDOGLOAD (0x0000) - Load register for initial countdown value
  - WDOGVALUE (0x0004) - Current value register (read-only)
  - WDOGCONTROL (0x0008) - Control register with enable, reset, interrupt, and divider fields
  - WDOGINTCLR (0x000C) - Interrupt clear register (write-only)
  - WDOGRIS (0x0010) - Raw interrupt status register (read-only)
  - WDOGMIS (0x0014) - Masked interrupt status register (read-only)
  - WDOGLOCK (0x0C00) - Lock register with magic unlock value 0x1ACCE551
  - WDOGITCR (0x0F00) - Integration test control register
  - WDOGITOP (0x0F04) - Integration test output set register
  - Peripheral ID registers (0x0FE0-0x0FEC, 0x0FD0-0x0FDC) - Fixed identification values
  - PrimeCell ID registers (0x0FF0-0x0FFC) - Fixed identification values

#### Key Features Implemented
- **Timer Functionality**: Countdown timer with configurable timeout periods
- **Interrupt Generation**: First timeout generates interrupt when enabled
- **Reset Generation**: Second timeout generates system reset when enabled
- **Lock Protection**: Register lock mechanism with magic unlock value
- **Integration Test Mode**: Direct signal control for testing
- **Clock Divider**: Configurable clock division (÷1, ÷2, ÷4, ÷8)
- **Checkpointing**: All state variables properly saved for simulation persistence

#### Interface Implementation
- **Interrupt Output**: Connect irq interface for interrupt signaling
- **Reset Output**: Connect reset interface for system reset signaling
- **Memory Interface**: Standard register bank memory-mapped I/O

#### Testing
- **Comprehensive Test Suite**: Multiple test files covering register access, interface behavior, and workflow
- **Unit Tests**: Performance and validation tests
- **All Tests Passing**: Complete test suite validates implementation correctness

## RAG Search Results Summary

| # | Query Focus | Source Type | Match Count | Status | Reference Section |
|---|-------------|-------------|-------------|--------|-------------------|
| 1 | DML 1.4 Reference Manual | docs | 5 | ✅ | Documentation Access |
| 2 | Model Builder Patterns | docs | 5 | ✅ | Documentation Access |
| 3 | DML Device Template | dml | 5 | ✅ | Documentation Access |
| 4 | Device-Specific Best Practices | source | 5 | ✅ | Device Example Analysis |
| 5 | Simics Device Reference | source | 5 | ✅ | Device Example Analysis |
| 6 | Register Implementation | dml | 5 | ✅ | Device Example Analysis |
| 7 | Python Test Patterns | python | 5 | ✅ | Test Example Analysis |
| 8 | Device Testing Best Practices | source | 5 | ✅ | Test Example Analysis |
| 9 | ARM PrimeCell Register Behaviors | source | 5 | ✅ | Additional Research |
| 10 | Watchdog Register Map | dml | 5 | ✅ | Additional Research |

**Note**: Queries 9+ are requirement-driven queries executed to address specific knowledge gaps identified from the "Functional Requirements" section in spec.md. Each additional query documents which requirement it addresses and what knowledge gap it fills.

## Implementation Strategy

### Device Architecture
Based on the research, the watchdog timer will be implemented as a DML 1.4 device with:
- Register bank for memory-mapped I/O access
- Timer-based event handling using after statements
- Interrupt and reset signaling through connect interfaces
- Lock protection mechanism with magic unlock value
- Integration test mode registers for direct signal control

### Register Design Approach
- Implement all 21 registers as specified in the requirements
- Use field definitions for bit-level access to control registers
- Implement appropriate read/write behaviors for each register type
- Include lock protection with magic unlock value 0x1ACCE551
- Provide integration test registers for direct signal control

### Test Strategy
- Create register access tests using dev_util.Register_LE
- Implement functional behavior tests for timeout and interrupt generation
- Test lock protection mechanism with unlock sequences
- Verify integration test mode functionality
- Validate reset behavior and interrupt clearing

### Next Steps
Phase 1 (Design) will focus on creating the data model, contracts, and quickstart guide based on this research.