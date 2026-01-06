# Project Context

## Purpose
This project implements Simics device models for embedded systems, specifically creating a comprehensive watchdog timer (WDT) device model compatible with ARM PrimeCell specification. The purpose is to provide accurate simulation models for embedded system verification and development, enabling engineers to test software and hardware interactions in a virtual environment.

## Tech Stack
- **Simics Base**: Intel Simics 7.57.0 for virtual platform development
- **DML 1.4**: Device Modeling Language for creating device models
- **Python 3**: For test automation and validation scripts
- **C/C++**: For complex device implementations (when needed)
- **IP-XACT**: Register specification format used for auto-generation
- **CMake/Make**: Build system integration
- **QSP-x86**: Target platform for testing and validation

## Project Conventions

### Code Style
- **DML Files**: Use DML 1.4 syntax with proper import statements preserved
- **Register Definitions**: Auto-generated from IP-XACT, never manually edited
- **Implementation Files**: `device.dml` for register behavior and device logic
- **Test Files**: Python files following stest framework with `s-` prefix
- **File Organization**: One device per module directory with dedicated test subdirectory
- **Comments**: Follow Simics documentation patterns with descriptive register and field comments

### Architecture Patterns
- **Model-View-Controller**: Device logic separated from register interface and test harness
- **Functional Modeling**: Event-based timing rather than cycle-accurate (for performance)
- **Template-Based**: Use DML templates for register bank definitions
- **Signal Interface**: Standardized port/connect patterns for interrupt/reset signals
- **APB Bus Interface**: Advanced Peripheral Bus compatible register access
- **Session State**: Use `session` variables for checkpointing when needed

### Testing Strategy
- **TDD Approach**: Tests written before implementation to validate functionality
- **Unit Tests**: Register read/write validation using dev_util.bank_regs
- **Integration Tests**: Signal behavior and device state machine validation
- **Platform Tests**: Memory mapping and interrupt routing validation
- **Stest Framework**: Use stest.expect_equal() for assertions and validation
- **Fake PIC Pattern**: Use FakePic class for interrupt controller simulation
- **Simulation Continuation**: Use simics.SIM_continue() for time-based validation

### Git Workflow
- **Feature Branches**: One change ID per feature/bug fix following openspec convention
- **Change Format**: Kebab-case, verb-led format (e.g., `add-watchdog-interrupt`, `fix-register-lock`)
- **Atomic Commits**: Each change addresses single capability or fixes specific issue
- **Validation Required**: All changes must pass `openspec validate --strict` before merge
- **Archive Process**: Changes moved to archive after implementation completion

## Domain Context
- **Watchdog Timer Functionality**: ARM PrimeCell compatible 32-bit countdown timer with interrupt and reset generation
- **Register Protection**: Magic unlock value (0x1ACCE551) for write protection of critical registers
- **Dual Timeout Behavior**: First timeout generates interrupt, second timeout generates system reset
- **Integration Test Mode**: Direct signal control for validation and testing purposes
- **APB Bus Interface**: Standard ARM Advanced Peripheral Bus protocol for register access
- **ID Registers**: Standardized peripheral and PrimeCell identification registers for system recognition
- **Clock Domains**: Separate work clock (wclk) and reset (wrst_n) for proper synchronization

## Important Constraints
- **Preserve Import Statements**: Never remove auto-generated import statements in DML files
- **Event-Based Timing**: Avoid cycle-accurate counter updates (causes 100-1000x slowdown)
- **DML 1.4 Compliance**: Maintain compatibility with Simics DML 1.4 language features
- **No Auto-Generated File Edits**: Never manually modify `<device>-registers.dml` files
- **Memory Mapping**: Fixed 4KB address space requirement (0x1000-0x1FFF) for QSP-x86 compatibility
- **Lock Protection**: Mandatory lock register mechanism to prevent unauthorized register access
- **Signal Handling**: Proper edge-triggered interrupt and reset signal implementation

## External Dependencies
- **Simics Base Package (7.57.0)**: Core simulation infrastructure
- **QSP-x86 Platform**: Target platform for device integration and testing
- **DML Builtins**: Standard DML library for device modeling functions
- **APB Protocol**: Standard ARM bus interface for register access
- **ARM PrimeCell Specification**: Watchdog timer register and behavior specification
- **Python Simics API**: Runtime access to simulation objects and control
- **STest Framework**: Simulation test validation and assertion tools
