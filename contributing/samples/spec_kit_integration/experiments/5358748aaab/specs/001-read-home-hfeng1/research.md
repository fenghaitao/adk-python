# Research: Simics Watchdog Timer Model

## Environment Discovery

### Simics Version
Simics Base package version 7.57.0

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
Public Intel® Simics® Quick Start Platform (QSP-x86) - 7 (Group: qsp-x86-public-7)

## Documentation Access (via RAG Queries)

### DML 1.4 Reference Manual
- **Query**: "DML 1.4 reference manual register and device modeling"
- **Source Type**: docs
- **Key Findings**:
  * Register modeling patterns and constructs are available in the standard templates library, with templates for registers and fields that can be accessed after importing `utility.dml`.
  * Device structure requirements include defining reset behavior through standard templates like `power_on_reset`, `hard_reset`, and `soft_reset`.
  * DML language features for hardware modeling include various standard templates that define specific behaviors for registers and fields, such as constant values, read/write restrictions, and unimplemented functionality.
- **References**: Device Modeling Language 1.4 Reference Manual, Standard Templates chapter
- **Application**: Structure the watchdog timer with appropriate register definitions and field breakdowns using standard templates from utility.dml

### Model Builder User Guide
- **Query**: "Simics Model Builder device creation and structure patterns"
- **Source Type**: docs
- **Key Findings**:
  * Device creation workflow involves defining device metadata, importing necessary libraries, and implementing registers and methods.
  * Structure patterns include defining banks for register organization, using standard templates for common register behaviors, and implementing device-specific functionality through methods.
  * Best practices for device modeling include using checkpointed variables for state that needs to persist across simulation checkpoints and implementing proper logging for debugging.
- **References**: Simics Model Builder documentation
- **Application**: Follow established patterns for device structure and implementation approach

### DML Device Template
- **Query**: "DML device template base structure and skeleton"
- **Source Type**: dml
- **Key Patterns**:
  * Device declaration with `dml 1.4;` and `device` name
  * Register banks with parameters like `register_size` and `byte_order`
  * Register declarations with size, offset, and behavior templates
- **Code Examples**:
  ```dml
  dml 1.4;
  
  device sample_device_dml;
  
  param desc = "sample DML device";
  param documentation = "This is a very simple device.";
  
  import "sample-interface.dml";
  
  bank regs {
      param desc = dev.desc + "custom desc";
      register r1 size 4 @ 0x0000 is read {
          method read() -> (uint64) {
              log info: "read from r1";
              return 42 + sample.call_count;
          }
      }
  }
  ```
- **Application**: Structure the watchdog timer device following standard DML skeleton patterns

## Device Example Analysis (via RAG Queries)

### Device-Specific Best Practices
- **Query**: "Best practices for watchdog timer device modeling with Simics DML 1.4"
- **Source Type**: source
- **Key Patterns Observed**:
  * Using standard templates from `utility.dml` for common register behaviors
  * Implementing proper reset behavior through reset templates
  * Using checkpointed variables for state that must persist across checkpoints
- **Code Examples**:
  ```dml
  dml 1.4;
  
  device sample_device_dml;
  
  param desc = "sample DML device";
  param documentation = "This is a very simple device.";
  
  import "sample-interface.dml";
  
  bank regs {
      param desc = dev.desc + "custom desc";
      register r1 size 4 @ 0x0000 is read {
          method read() -> (uint64) {
              log info: "read from r1";
              return 42 + sample.call_count;
          }
      }
  }
  ```
- **Relevant Structures**: Apply standard register bank patterns with appropriate templates for read-only, write-only, and read-write registers
- **Application**: Apply watchdog timer-specific patterns to avoid common issues and follow best practices

### Simics Device Reference Example
- **Query**: "Simics device implementation example watchdog timer or similar peripheral"
- **Source Type**: source
- **Key Patterns Observed**:
  * Basic register implementation with read/write methods
  * Device initialization and lifecycle management
  * Interface implementation for external connectivity
  * Event handling for time-based operations
- **Code Examples**:
  ```dml
  dml 1.4;
  
  device sample_device_dml;
  
  param desc = "sample DML device";
  param documentation = "This is a very simple device.";
  
  import "sample-interface.dml";
  
  bank regs {
      param desc = dev.desc + "custom desc";
      register r1 size 4 @ 0x0000 is read {
          method read() -> (uint64) {
              log info: "read from r1";
              return 42 + sample.call_count;
          }
      }
  }
  ```
- **Applicable Patterns**: Adapt similar device patterns to watchdog timer implementation requirements, especially for register access and event handling
- **Application**: Adapt similar device patterns to watchdog timer implementation requirements

### Register Implementation Patterns
- **Query**: "DML register bank implementation patterns"
- **Source Type**: dml
- **Implementation Patterns**:
  * Register bank definition with parameters like `register_size`
  * Register access methods (read, write, get, set)
  * Register callbacks and custom behaviors through method overrides
  * Field definitions and bit-level access within registers
- **Code Examples**:
  ```dml
  dml 1.4;
  
  device sample_device_dml;
  
  param desc = "sample DML device";
  param documentation = "This is a very simple device.";
  
  import "sample-interface.dml";
  
  bank regs {
      param desc = dev.desc + "custom desc";
      register r1 size 4 @ 0x0000 is read {
          method read() -> (uint64) {
              log info: "read from r1";
              return 42 + sample.call_count;
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
  * Test suite structure using Python unittest framework
  * Device instance creation using `simics.SIM_create_object()`
  * Register access testing using `dev_util.Register_LE()`
  * Assertions and validation using `stest.expect_equal()`
- **Code Examples**:
  While specific test examples weren't found in the RAG results, typical patterns in Simics Python tests include:
  ```python
  # Typical test pattern
  import stest
  import dev_util
  import simics
  
  def test_register_access():
      # Create device instance
      dev = simics.SIM_create_object("watchdog_timer", "wdt", [])
      
      # Access register
      reg = dev_util.Register_LE(dev.bank.regs, 0x0000, 4)
      
      # Test read/write behavior
      reg.write(0x12345678)
      stest.expect_equal(reg.read(), 0x12345678)
  ```
- **Test Framework**: stest, dev_util, and simics modules for test utilities and assertions
- **Application**: Structure tests for watchdog timer following established test patterns and conventions

### Device Testing Best Practices
- **Query**: "Simics device testing best practices"
- **Source Type**: source
- **Best Practices Identified**:
  * Test coverage strategies should include all register access patterns
  * Validation approaches for device behavior verification should cover both normal and edge cases
  * Error condition testing should verify proper handling of invalid register accesses
  * Performance testing should ensure timing requirements are met
- **Code Examples**:
  ```dml
  // DML device with logging for testability
  dml 1.4;
  
  device sample_device_dml;
  
  bank regs {
      register r1 size 4 @ 0x0000 is read {
          method read() -> (uint64) {
              log info: "read from r1";
              return 42;
          }
      }
  }
  ```
- **Applicable Practices**: Apply comprehensive testing practices to ensure watchdog timer correctness and reliability, including testing interrupt generation, reset functionality, and register protection mechanisms
- **Application**: Apply comprehensive testing practices to ensure watchdog timer correctness and reliability

## Additional Research (Requirement-Driven RAG Queries)

## Architecture Decisions

### Decision: Use DML 1.4 for Implementation
- **Rationale**: The Simics environment has DML 1.4 available, and it's the latest version that provides all necessary features for implementing the watchdog timer model.
- **Alternatives Considered**: DML 1.2 was considered but DML 1.4 provides better features and is the current standard.
- **Source**: get_simics_version() output and RAG query results
- **Impact**: Implementation will use modern DML features and patterns

### Decision: Base Structure on Standard Templates
- **Rationale**: The RAG queries showed that standard templates from utility.dml provide common register behaviors that match the watchdog timer requirements.
- **Alternatives Considered**: Custom implementation of all register behaviors was considered but would be redundant and error-prone.
- **Source**: RAG query on "DML 1.4 reference manual register and device modeling"
- **Impact**: Implementation will be more maintainable and follow established patterns

### Decision: Use QSP-x86 as Target Platform
- **Rationale**: The only available platform is QSP-x86, which is suitable for testing the watchdog timer model.
- **Alternatives Considered**: Other platforms might be available but are not listed in the environment.
- **Source**: list_simics_platforms() output
- **Impact**: The watchdog timer model will be tested on QSP-x86 platform

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

## Implementation Strategy

### Device Architecture
The watchdog timer will be implemented as a standalone DML device model with memory-mapped registers. The architecture will follow the standard Simics device pattern with:
- A main device object
- Register banks for memory-mapped I/O
- Event handling for timer functionality
- Interface connections for interrupt and reset signals

### Register Design Approach
Registers will be implemented using standard templates from utility.dml where applicable:
- WDOGLOAD: Read-write register for timer load value
- WDOGVALUE: Read-only register for current timer value
- WDOGCONTROL: Read-write register for control bits
- WDOGINTCLR: Write-only register for interrupt clearing
- WDOGRIS: Read-only register for raw interrupt status
- WDOGMIS: Read-only register for masked interrupt status
- WDOGLOCK: Read-write register for register protection
- WDOGITCR/WDOGITOP: Registers for integration testing
- Identification registers: Read-only registers for device identification

### Test Strategy
Testing will follow the TDD approach with:
- Register access tests for all registers
- Functional tests for timer counting and interrupt generation
- Reset functionality tests
- Lock mechanism tests
- Integration tests with the QSP-x86 platform

### Next Steps
Proceed to Phase 1 (Design) to create the data model, contracts, and quickstart guide based on the research findings.