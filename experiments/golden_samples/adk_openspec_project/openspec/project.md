# Project Context

## Purpose
This project implements a Simics device model for an ARM PrimeCell-compatible Watchdog Timer (WDT) device. The purpose is to provide a functional simulation model that enables testing and development of embedded software systems that interact with watchdog timer functionality. The model simulates hardware behavior for embedded systems design and validation.

## Tech Stack
- **Simics 7.57.0**: Intel Simics System-level simulator for virtual development and testing
- **DML 1.4**: Device Modeling Language for creating Simics device models
- **Python 3.x**: Test framework and automation (stest, simics API)
- **APB Bus Interface**: Advanced Peripheral Bus for register access
- **ARM PrimeCell Compatible Design**: Following ARM PrimeCell watchdog timer specification
- **IP-XACT**: For register generation and device specification
- **Makefile/CMake**: Build system integration

## Project Conventions

### Code Style
- DML 1.4 syntax with proper device template structure
- Use session variables for checkpointing and state management
- Event-based timing using `.post(cycles)` for scheduling (avoid cycle-accurate updates)
- Follow ARM PrimeCell register naming conventions
- Proper indentation and comments in DML code
- All import statements must be preserved (auto-generated during build)
- Use descriptive method names: `read_register`, `write_register`, `signal_raise`, `signal_lower`

### Architecture Patterns
- **Register-based Interface**: All device interaction via memory-mapped registers
- **Functional Modeling**: Focus on register behavior rather than cycle-accurate timing
- **Signal Interface**: Use Simics signal interfaces for interrupt and reset outputs
- **Modular Design**: Separate register definitions from functional implementation
- **Lock Protection**: Implement WDOGLOCK register with magic unlock value 0x1ACCE551
- **Integration Test Mode**: Support for direct signal control during testing

### Testing Strategy
- **Test-Driven Development**: Write failing tests first, then implement functionality
- **Register-level Tests**: Verify all 21 registers according to specification
- **Functional Behavior Tests**: Test interrupt generation, reset conditions, and lock protection
- **Integration Tests**: Validate platform connectivity and signal routing
- **Python-based Testing**: Use simics, dev_util, and stest modules for test validation
- **Simics Testing Framework**: Follow Simics test suite conventions

### Git Workflow
- **Feature Branches**: Create dedicated branches for new device implementations
- **Commit Messages**: Use descriptive messages following conventional commits pattern
- **Change IDs**: Use OpenSpec change ID format (NNN-descriptive-title) for tracking
- **Spec-first Development**: Document requirements before implementation
- **Incremental Changes**: Small, focused commits that deliver user-visible progress

## Domain Context
- **Watchdog Timer Functionality**: 32-bit decrementing counter with configurable timeout
- **ARM PrimeCell Specification**: Compatible with ARM PrimeCell watchdog IP
- **Embedded Systems Integration**: Device connects to APB bus with interrupt and reset signals
- **Platform Simulation**: Designed for QSP-x86 and other Simics platforms
- **Safety Mechanisms**: Lock protection prevents malicious register access
- **Interrupt Management**: Edge-triggered interrupt on first timeout, reset on second
- **Clock Domain Handling**: Separate work clock (wclk) and bus clock domains

## Important Constraints
- **Preserve Import Statements**: Never remove auto-generated import statements
- **Functional vs Cycle-Accurate**: Use functional timing models, avoid cycle-accurate behavior
- **Memory Mapping**: Fixed address range 0x1000-0x1FFF for register access
- **Signal Interfaces**: APB bus interface with specific signal connections (wclk, wrst_n, wdogint, wdogres)
- **Register Locking**: Magic value 0x1ACCE551 required to unlock register writes
- **Simulation Performance**: Prioritize real-time simulation performance over detailed timing
- **Checkpoint/Restore**: Rely on Simics automatic state management

## External Dependencies
- **Simics Base Package**: Core simulator functionality
- **Simics Device Utilities**: dev_util module for register access
- **Simics Testing Framework**: stest module for test validation
- **Platform Integration**: QSP-x86 or other target platforms for device instantiation
- **APB Bus Protocol**: Standard ARM bus interface for register access
- **Signal Routing**: Platform-specific routing for interrupt and reset signals