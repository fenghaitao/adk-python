# Change: Implement Watchdog Timer Device

## Context
- **Primary Spec**: specs/001-read-the-simics/spec.md (96 functional requirements: FUNC-001 to FUNC-032, REG-001 to REG-010, BEHAV-001 to BEHAV-010, TEST-001 to TEST-010)
- **Existing Code**: simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated registers)
- **Key Memory Docs**: 
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (timer implementation patterns)
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid performance pitfalls)

## Why
Enable functional watchdog timer device by implementing behavior specified in specs/001-read-the-simics/spec.md. The existing spec defines a complete ARM PrimeCell watchdog timer with 32-bit decrementing counter, interrupt generation, reset capability, and lock protection mechanism.

## What Changes
- Implement register side-effects in wdt.dml for WDOGCONTROL, WDOGINTCLR, WDOGLOCK, WDOGITCR, and WDOGITOP registers
- Implement watchdog timer behavior logic using lazy evaluation and event-based timeout handling
- Add interrupt and reset signal generation on timeout conditions
- Add test cases to validate all functional requirements

## Impact
- Affected specs: 001-read-the-simics
- Affected code:
  - Modified: simics-project/modules/wdt/wdt.dml (implement USER-TODO side-effects)
  - Added: simics-project/modules/wdt/test/s-*.py (test cases)
