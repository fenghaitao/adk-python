# Project Context

## Purpose
This project is a Simics device model development environment focused on creating high-fidelity virtual hardware models for embedded systems. The primary purpose is to implement device models compatible with Intel Simics simulation platform, starting with a watchdog timer (WDT) device compatible with ARM PrimeCell specification. The project uses OpenSpec methodology to manage specification, implementation, and validation of device models.

## Tech Stack
- **Simics Device Modeling Language (DML) 1.4**: Primary language for implementing device models
- **Python 3.x**: For test infrastructure, automation, and validation scripts
- **APB4 (Advanced Peripheral Bus 4)**: Standard bus interface for device communication
- **ARM PrimeCell Watchdog Timer Specification**: Reference hardware specification
- **IP-XACT**: Register definition format and XML-based IP description
- **CMake/Make**: Build system for Simics modules
- **Simics Python API**: For test automation and device interaction

## Project Conventions

### Code Style
- DML 1.4 syntax following Simics best practices
- Event-based timing models (no cycle-accurate updates to avoid performance issues)
- Session state management for checkpoint/restore capability
- Use of `SIM_cycle_count` for lazy evaluation timing calculations
- Import statements preserved (never removed as they're auto-generated)
- Register read/write methods implemented with proper side effects

### Architecture Patterns
- **Separation of Register Definition and Implementation**: Split across `<device>-registers.dml` and `<device>.dml` files
- **Signal Interface Pattern**: Use `port` for input signals and `connect` for output signals
- **Bank-based Register Organization**: Group related registers in memory banks
- **Event-driven Architecture**: Use DML events for timer/counter operations
- **Lazy Evaluation**: Calculate timer values on-demand rather than continuous updates

### Testing Strategy
- **TDD Approach**: Write tests first, then implement device functionality
- **Comprehensive Register Tests**: Validate all 21 watchdog registers for read/write behavior
- **Behavioral Tests**: Verify timer countdown, interrupt generation, and reset behavior
- **Integration Tests**: Validate platform connectivity and signal routing
- **Simics Python API Testing**: Use `dev_util.bank_regs`, `simics.SIM_continue`, and `stest.expect_equal`
- **Fake PIC Implementation**: Simulate interrupt controllers and peripheral interfaces

### Git Workflow
- **Feature Branches**: Create branches for each device implementation (e.g., `feature/wdt-implementation`)
- **Change-based Commits**: Use OpenSpec changes to track specification deltas
- **Automated Validation**: Run build and test suite before merging
- **Commit Conventions**: Follow OpenSpec change model with clear change IDs

## Domain Context
- **Simics Simulation Environment**: High-fidelity virtual platform for embedded system development
- **Watchdog Timer Functionality**: 32-bit countdown timer with interrupt and reset generation
- **ARM PrimeCell Compatibility**: Follows ARM's PrimeCell watchdog specification
- **Lock Protection**: Magic unlock value 0x1ACCE551 to protect against errant software writes
- **Integration Test Mode**: Special mode for direct signal control during testing
- **APB Bus Interface**: Standard peripheral bus interface for register access

## Important Constraints
- **Performance**: Avoid cycle-accurate timer implementations that cause 100-1000x slowdown
- **Functional Model**: Focus on accuracy of behavior, not precise timing simulation
- **No Base Clock Required**: Functional model approach, not cycle-accurate simulation
- **Memory Mapping**: Fixed address range (0x1000-0x1FFF) for compatibility
- **Auto-generated Files**: Do not modify `<device>-registers.dml` and `<device>-glue.dml` files

## External Dependencies
- **Intel Simics Platform**: Core simulation environment and APIs
- **Simics Base Package**: Required for DML compilation and execution
- **Device Utility Libraries**: `dev_util` for register access patterns
- **Test Framework**: `stest` for assertion-based testing
- **Simics C/C++ Libraries**: Underlying implementation libraries
