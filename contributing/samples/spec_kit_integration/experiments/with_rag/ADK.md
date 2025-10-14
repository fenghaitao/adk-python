# ADK Context: Simics Watchdog Timer Implementation

## Project Overview
Implementation of a Simics watchdog timer model following device-first development principles.

## Key Technical Details

### Device Architecture
- Device name: wdt (Watchdog Timer)
- Implementation language: DML 1.4
- Register-based peripheral with memory-mapped interface
- 32-bit decrementing timer with configurable load value
- Interrupt and reset generation capabilities
- Register protection mechanism using lock register

### Register Map
Main registers:
- WDOGLOAD (0x000): 32-bit load value register
- WDOGVALUE (0x004): 32-bit current counter value (read-only)
- WDOGCONTROL (0x008): Control register with int_en and res_en bits
- WDOGINTCLR (0x00C): Interrupt clear register (write-only)
- WDOGRIS (0x010): Raw interrupt status register (read-only)
- WDOGMIS (0x014): Masked interrupt status register (read-only)
- WDOGLOCK (0xC00): Register lock/unlock control
- WDOGITCR (0xF00): Integration test control register
- WDOGITOP (0xF04): Integration test output set register

### Key Implementation Patterns
1. Timer countdown mechanism using Simics events
2. Register protection using WDOGLOCK register
3. Interrupt and reset signal generation
4. Integration test mode support
5. Device state persistence for checkpointing

### Constitutional Compliance
All implementation follows the Simics Model Development Constitution:
- Device-first development approach
- Interface-first architecture
- Test-first development methodology
- Specification-driven implementation
- Simics excellence principles

## Implementation Tasks (Will be detailed in tasks.md)
1. Create Simics project structure
2. Implement DML device model with all registers
3. Implement timer countdown logic
4. Implement interrupt and reset generation
5. Implement register protection mechanism
6. Implement integration test mode
7. Create comprehensive test suite
8. Validate against specification requirements
