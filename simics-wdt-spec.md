# Simics Watchdog Timer Device Implementation Specification

## Feature Description

Create a comprehensive Simics watchdog timer device implementation with the following requirements:

## Core Functionality

- Implement 32-bit watchdog timer compatible with ARM PrimeCell specification from wdt.md
- Support all 21 registers including control, data, status, lock, integration test, and ID registers
- Enable configurable timeout periods with 5 clock divider settings (÷1, ÷2, ÷4, ÷8, ÷16)
- Generate interrupt on first timeout and system reset on second timeout
- Include lock protection mechanism with magic unlock value 0x1ACCE551
- Support integration test mode for direct signal control

## Technical Implementation

- Use DML 1.4 syntax with proper device template and signal interfaces
- Implement cycle-based timing using SIM_cycle_count() API
- Support device state persistence for checkpoint/restore functionality
- Provide interrupt and reset signal outputs with platform routing
- Include comprehensive logging for debugging and monitoring

## Integration & Testing

- Map to QSP-x86 platform memory space at address 0x1000
- Connect signals to platform interrupt and reset controllers
- Provide comprehensive test suites covering all functionality
- Follow TDD approach with failing tests initially

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
