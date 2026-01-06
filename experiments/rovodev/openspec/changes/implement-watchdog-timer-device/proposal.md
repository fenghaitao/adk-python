# Change: Implement Watchdog Timer Device

## Context
- **Primary Spec**: specs/001-tmp-hfeng1-demo/spec.md (90 functional requirements: FUNC-001 to FUNC-019, REG-001 to REG-009, BEHAV-001 to BEHAV-006, TEST-001 to TEST-008)
- **Existing Code**: simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated register structure and USER-TODO placeholders)
- **Key Memory Docs**: 
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid timer anti-patterns that cause 100-1000x performance degradation)
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (timer implementation patterns using event-based timing and lazy evaluation)
  - openspec-memories/06_DML_Common_Patterns.md (register side-effect patterns for lock protection and interrupt handling)

## Why
Enable functional watchdog timer device by implementing behavior specified in specs/001-tmp-hfeng1-demo/spec.md. The device is an ARM PrimeCell compatible 32-bit decrementing counter with configurable timeout periods, interrupt generation, reset functionality, and lock protection mechanism.

## What Changes
- Implement register side-effects in wdt.dml for all USER-TODO placeholders
- Implement timer countdown logic using event-based timing (lazy evaluation pattern)
- Implement lock protection mechanism (WDOGLOCK register)
- Implement interrupt generation and clearing logic
- Implement reset generation on second timeout
- Implement clock divider functionality
- Implement integration test mode
- Add comprehensive test cases to validate all functional requirements

## Impact
- Affected specs: 001-tmp-hfeng1-demo
- Affected code:
  - Modified: simics-project/modules/wdt/wdt.dml (implement USER-TODO side-effects and timer logic)
  - Added: simics-project/modules/wdt/test/s-wdt-timer.py (timer and interrupt tests)
  - Added: simics-project/modules/wdt/test/s-wdt-lock.py (lock protection tests)
  - Added: simics-project/modules/wdt/test/s-wdt-integration.py (integration test mode)
