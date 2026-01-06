# Project Context

## Purpose
This project implements a Simics watchdog timer device model based on the ARM PrimeCell watchdog specification. The goal is to create a complete, tested device implementation compatible with Simics 7.x that can be integrated into QSP-x86 platform simulations.

## Tech Stack
- **Simics 7.x** - Virtual platform simulation framework
- **DML 1.4** - Device Modeling Language for device implementation
- **Python** - Test automation and scripting
- **C/C++** - Core Simics infrastructure
- **Git** - Version control
- **OpenSpec** - Specification-driven development workflow

## Project Conventions

### Code Style
- **DML Code**: Follow DML 1.4 syntax standards
  - Use descriptive register and field names matching hardware spec
  - Implement proper read/write access controls per register type
  - Include comprehensive logging with appropriate log levels
  - Use bank templates for memory-mapped registers
  
- **Naming Conventions**:
  - Register names: UPPERCASE with underscores (e.g., `WDOGLOAD`, `WDOGCONTROL`)
  - Register fields: lowercase with underscores (e.g., `wdog_load`, `step_value`)
  - Signals: lowercase descriptive names (e.g., `wdogint`, `wdogres`)
  - Methods: lowercase with underscores (e.g., `update_counter`, `trigger_interrupt`)

- **Documentation**:
  - Document all registers with address, width, access type, reset value
  - Include functional descriptions for complex behaviors
  - Reference original hardware spec sections where applicable

### Architecture Patterns
- **Device Model Architecture**:
  - Use DML device template as base
  - Implement register bank for memory-mapped registers
  - Separate interface definitions for signals (interrupt, reset)
  - Functional modeling approach (not cycle-accurate timing)
  
- **Register Organization**:
  - Control registers (LOAD, VALUE, CONTROL, INTCLR, RIS, MIS)
  - Lock protection mechanism (LOCK register at 0xC00)
  - Integration test registers (ITCR, ITOP at 0xF00)
  - Peripheral ID registers (PERIPHID0-7 at 0xFD0-0xFDC and 0xFE0-0xFEC)
  - PrimeCell ID registers (PCELLID0-3 at 0xFF0-0xFFC)

- **Counter Mechanism**:
  - 32-bit down-counter with configurable step values (÷1, ÷2, ÷4, ÷8, ÷16)
  - Functional model using Simics event system
  - Reload from WDOGLOAD on enable or interrupt clear
  - Two-stage timeout: interrupt on first timeout, reset on second

### Testing Strategy
- **Test-Driven Development (TDD)**:
  - Write failing tests first before implementation
  - Test each register independently for read/write behavior
  - Test all operational modes and state transitions
  
- **Test Coverage**:
  - Register access tests (read/write, locked/unlocked states)
  - Counter operation tests (countdown, reload, timeout)
  - Interrupt generation and clearing
  - Reset signal generation
  - Lock protection mechanism
  - Integration test mode
  - Edge cases and error conditions

- **Test Framework**:
  - Python-based test suites using Simics scripting API
  - Automated test execution and validation
  - Clear test naming and documentation

### Git Workflow
- **Branch Strategy**:
  - `master` - Stable baseline
  - Feature branches named after change-id (e.g., `001-read-the-simics`)
  - Create branch per OpenSpec change proposal
  
- **Commit Conventions**:
  - Prefix with capability/area: `specify:`, `implement:`, `test:`
  - Clear, descriptive commit messages
  - Reference change-id in commit message when applicable
  - Example: "specify: watchdog-timer - Add hardware specification and register definitions"

## Domain Context

### Hardware Specification Knowledge
The watchdog timer is an ARM PrimeCell compliant peripheral with the following characteristics:

- **Purpose**: Provides system watchdog functionality with configurable timeout periods
- **Key Features**:
  - 32-bit down-counter with programmable reload value
  - Configurable step values for different clock frequencies (1GHz to 62.5MHz)
  - Dual-stage timeout: interrupt warning followed by system reset
  - Lock register protection against rogue software
  - Integration test mode for signal verification
  - Standard ARM PrimeCell identification registers

- **Operational Flow**:
  1. Software unlocks registers (write 0x1ACCE551 to LOCK)
  2. Configure LOAD value and CONTROL register (step, INTEN, RESEN)
  3. Counter starts decrementing when INTEN is enabled
  4. First timeout triggers interrupt (wdogint) if INTEN=1
  5. Second timeout triggers reset (wdogres) if RESEN=1 and interrupt not cleared
  6. Software services watchdog by writing to INTCLR register

### Simics Platform Integration
- **Target Platform**: QSP-x86 (Quick Start Platform for x86)
- **Memory Mapping**: Device mapped at base address 0x1000, 4KB address space (0x1000-0x1FFF)
- **Bus Interface**: APB (Advanced Peripheral Bus) protocol
- **Interrupt Connection**: Edge-triggered interrupt signal to platform interrupt controller
- **Reset Connection**: Reset signal to platform reset controller

### DML Device Development
- **Modeling Approach**: Functional model, not cycle-accurate
- **Checkpoint/Restore**: Simics handles register state automatically
- **Event System**: Use Simics events for counter timeout simulation
- **Logging**: Comprehensive logging for debugging and monitoring
- **Signal Interfaces**: Define output signals for interrupt and reset

## Important Constraints

### Technical Constraints
- **DML Version**: Must use DML 1.4 syntax
- **Simics Compatibility**: Compatible with Simics 7.x
- **Functional Modeling**: No cycle-accurate timing required
- **Register Layout**: Fixed register map per ARM PrimeCell spec
- **Lock Protection**: Must implement proper write protection when locked

### Hardware Specification Constraints
- **Register Addresses**: Fixed addresses as specified in wdt.md
- **Reset Values**: All registers have specified reset values
- **Access Permissions**: Strict read/write/write-only access controls
- **Lock Magic Value**: Must use 0x1ACCE551 to unlock
- **ID Registers**: Fixed values per PrimeCell specification

### Performance Constraints
- **Minimal Overhead**: Device simulation should not significantly impact overall simulation performance
- **Real-time Suitability**: Functional model allows real-time simulation scenarios

### Behavioral Constraints
- **Deterministic Operation**: Counter behavior must be deterministic across simulation runs
- **State Consistency**: Register values must remain consistent with counter state

## External Dependencies

### Simics Framework
- **Version**: Simics 7.x
- **Core Libraries**: Base Simics device infrastructure
- **Event System**: For timer event scheduling
- **Logging System**: For debug output and tracing

### Hardware Documentation
- **Primary Reference**: `wdt.md` - Original Chinese hardware specification
- **Secondary Reference**: `simics-wdt-spec.md` - Simics implementation specification
- ARM PrimeCell watchdog documentation (implicit reference)

### OpenSpec Workflow
- **Change Management**: All changes go through OpenSpec proposal → approval → implementation
- **Specification Files**: Track current state in `openspec/specs/`
- **Change Proposals**: Draft changes in `openspec/changes/`
- **Validation**: Use `openspec validate` before implementation

### Custom Agents
- **specify**: Create functional specifications from hardware docs
- **openspec_proposal**: Create change proposals for new capabilities
- **openspec_apply**: Implement approved proposals
- **simics_project_setup**: Setup Simics project environment

## Current Project State

### Completed Work
- Initial project structure created
- Hardware specification analyzed and documented
- Functional specification created in `specs/001-read-the-simics/spec.md`
- Register definitions generated in `specs/001-read-the-simics/wdt-register.xml`

### Next Steps
- Create implementation proposal for watchdog device
- Implement DML device model
- Create test suite following TDD approach
- Integrate with QSP-x86 platform
- Validate against hardware specification

### Active Capabilities
- **watchdog-timer**: Core watchdog functionality (specified, not yet implemented)
