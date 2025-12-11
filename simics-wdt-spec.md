# Simics Watchdog Timer Device Implementation Specification

## Feature Description

Create a comprehensive Simics watchdog timer device implementation with the following requirements:

## Core Functionality

- Implement 32-bit watchdog timer compatible with ARM PrimeCell specification from wdt.md
- Support all 21 registers including control, data, status, lock, integration test, and ID registers
- Enable configurable timeout periods with 5 clock divider settings (÷1, ÷2, ÷4, ÷8, ÷16)
- Generate edge-triggered interrupt on first timeout and system reset on second timeout
- Include lock protection mechanism with magic unlock value 0x1ACCE551
- Support integration test mode for direct signal control

## Technical Implementation

- Use DML 1.4 syntax with proper device template and signal interfaces
- Implement functional model - precise cycle-accurate timing NOT required, base clock frequency NOT needed
- Checkpoint/restore NOT required - Simics handles register state automatically
- Use APB bus interface for register access - specific APB signal connections are implementation details
- Provide interrupt and reset signal outputs with platform routing
- Include comprehensive logging for debugging and monitoring

## Integration & Testing

- Map to QSP-x86 platform memory space at base address 0x1000
- Memory address range: 0x1000 - 0x1FFF (4KB address space)
- Register offsets from base address as specified in register map
- Connect edge-triggered interrupt signal to platform interrupt controller - specific routing is implementation detail
- Connect reset signal to platform reset controller
- Provide comprehensive test suites covering all functionality
- Follow TDD approach with failing tests initially

## Modeling Scope

**Include in specification:**
- Register map and bit fields
- Device behavior and state transitions
- Interrupt and reset conditions
- Lock protection mechanism

**Do NOT include in specification (implementation details):**
- Base clock frequency (functional model, not cycle-accurate)
- Specific APB signal connections (handled by DML implementation)
- Interrupt controller routing details (platform-specific)
- Checkpoint/restore implementation (Simics automatic)

## Performance & Compatibility

- Achieve minimal simulation overhead for real-time performance
- Maintain compatibility with Simics 7.x and DML 1.4 standards
- Support both 32-bit and 64-bit simulation environments
- Follow Simics device development best practices

## Quality Requirements

- Implement input validation and error handling
- Ensure deterministic timeout behavior
- Support observability through status registers
- Enable security through register lock protection