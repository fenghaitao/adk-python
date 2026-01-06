# Project Context

## Purpose
This project is a Simics device model development environment focused on creating functional simulation models for embedded systems hardware. The primary goal is to develop accurate, high-performance Simics device models using DML (Device Modeling Language) to enable virtual platform development for hardware-software co-design and testing. The initial focus is on implementing an ARM PrimeCell-compatible watchdog timer (WDT) device model that can be integrated into QSP-x86 and other platform configurations.

## Tech Stack
- **Simics Base**: Version 7.57.0 - Complete virtual platform simulation environment
- **DML 1.4**: Device Modeling Language for creating functional device models
- **Python**: Test automation, build scripts, and validation frameworks
- **IP-XACT**: XML-based register and interface specifications for hardware design
- **APB4 Bus Interface**: Advanced Peripheral Bus v4 for device connectivity
- **APB4**: AMBA 4 Peripheral Bus interface for register access
- **XML**: IP-XACT register definitions and component specifications
- **Make/CMake**: Build system integration for Simics modules
- **Git**: Version control for device model source code

## Project Conventions

### Code Style
- **DML 1.4**: Use proper session state management for checkpoint/restore compatibility
- **Register Access**: Follow standard read/write handler patterns with appropriate side effect handling
- **Event Management**: Implement event-based timing rather than cycle-accurate updates (avoid performance penalties)
- **Signal Interfaces**: Use proper signal connection patterns for interrupt and reset signals
- **Module Structure**: Keep device implementations in single .dml file with separate -registers.dml auto-generated files
- **File Names**: Use descriptive names matching device functionality (e.g., wdt.dml, wdt-registers.dml)
- **Documentation**: Include comprehensive comments explaining device behavior and register side effects

### Architecture Patterns
- **Functional Modeling**: Focus on functional correctness over cycle-accurate behavior for optimal simulation performance
- **Register Abstraction**: Implement all device registers with proper address decoding and access control
- **State Machine Modeling**: Use DML events and state variables to model device operational states
- **Protection Mechanisms**: Implement lock registers and access control as specified in hardware documentation
- **Integration Test Mode**: Support special test modes as defined in device specifications
- **Modular Design**: Separate register definitions from functional behavior while maintaining single file structure
- **Signal Routing**: Use standard APB and interrupt signal patterns for platform integration

### Testing Strategy
- **Test-Driven Development**: Write failing tests first, then implement functionality to pass tests
- **Register Testing**: Validate all register read/write operations with expected reset values and side effects
- **State Transition Testing**: Verify device state changes and state machine behavior
- **Integration Testing**: Test device behavior in complete platform context
- **Functional Validation**: Test complete watchdog functionality including interrupt and reset generation
- **Edge Case Testing**: Validate boundary conditions, overflow, and special operational modes
- **Lock/Protection Testing**: Verify register lock mechanisms prevent unauthorized access

### Git Workflow
- **Feature Branches**: Use descriptive branch names with format `feature/device-name-description`
- **Commit Messages**: Follow format "Implement/Register/Update [component] for [functionality]"
- **Change Tracking**: Use OpenSpec changes directory for tracking design decisions and requirements
- **Spec Integration**: Link implementation commits to specification requirements in specs/ directory
- **Module Organization**: Keep each device implementation in dedicated modules/[device-name]/ directory

## Domain Context
- **Simics Simulation**: Virtual platform simulators that model complete systems including processors, memory, and peripherals
- **DML Device Models**: Functional models that simulate hardware behavior without cycle-accurate timing
- **Watchdog Timers**: Critical safety devices that reset systems if not periodically "fed" by software
- **ARM PrimeCell**: ARM's family of peripheral IP cores with standardized interfaces and identification
- **APB Interface**: Low-cost, low-latency bus for connecting peripheral devices to system controllers
- **Platform Integration**: Device models must work within Simics platform frameworks and connect to interrupt controllers
- **Functional vs. Cycle-Accurate**: Prioritize functional correctness for development velocity over detailed timing accuracy
- **Checkpoint/Restore**: Simics capability to save/restore simulation state without needing to model this explicitly

## Important Constraints
- **Performance**: Avoid cycle-accurate modeling patterns that cause exponential slowdown (use events, not continuous updates)
- **Register Protection**: Must implement lock register mechanism with magic value 0x1ACCE551 as specified
- **Interrupt Behavior**: Must follow ARM PrimeCell specification for single-bit interrupt status and clearing behavior
- **Reset Handling**: Support dual reset domains (APB and working clock) with proper reset value assignments
- **Timing**: Functional timing only - no specific clock frequency requirements, but must maintain correct logical behavior
- **Compatibility**: Maintain compatibility with Simics 7.x APIs and DML 1.4 language features
- **ID Registers**: Must implement fixed peripheral/PrimeCell identification registers with specified values

## External Dependencies
- **Simics Platform**: Complete Simics Base 7.57.0 installation with DML compiler
- **ARM PrimeCell Specifications**: Reference documentation for WDT register maps and behavior
- **APB4 Bus Specification**: For register interface compatibility
- **QSP-x86 Platform**: Target platform for device integration and testing
- **Python Simics API**: For test automation and validation scripts
- **IP-XACT Tools**: For register specification validation and documentation
