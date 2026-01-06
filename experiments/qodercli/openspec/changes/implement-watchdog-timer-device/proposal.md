# Change: Implement Watchdog Timer Device

## Context
- **Primary Spec**: specs/001-user-input-read/spec.md (105 functional requirements: FUNC-001 to FUNC-020, REG-001 to REG-012, BEHAV-001 to BEHAV-009, TEST-001 to TEST-009)
- **Existing Code**: simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated registers)
- **Key Memory Docs**: 
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid timer performance pitfalls)
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (lazy evaluation and event-based patterns)

## Why
Enable functional watchdog timer device by implementing behavior specified in specs/001-user-input-read/spec.md. This provides a working watchdog timer for Simics platform simulation with timer countdown, interrupt generation, reset output, and lock protection mechanisms.

## What Changes
- Implement register side-effects in wdt.dml (LOAD, VALUE, CONTROL, INTCLR, LOCK registers)
- Implement lazy evaluation pattern for timer counter calculation (avoid cycle-by-cycle updates)
- Implement event-based timeout mechanism for interrupt and reset generation
- Implement clock divider logic for configurable timer rates
- Implement lock protection mechanism for register access control
- Add test cases in simics-project/modules/wdt/test/ to validate all functional requirements

## Impact
- Affected specs: 001-user-input-read
- Affected code:
  - Modified: simics-project/modules/wdt/wdt.dml (implement USER-TODO side-effects and timer logic)
  - Added: simics-project/modules/wdt/test/s-*.py (test cases for timer, interrupt, reset, lock functionality)
