# Change: Implement Complex Watchdog Timer Device

## Context
- **Primary Spec**: specs/001-home-hfeng1-demo/spec.md (105 functional requirements: FUNC-001 to FUNC-027, REG-001 to REG-010, BEHAV-001 to BEHAV-010, TEST-001 to TEST-010)
- **Existing Code**: simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated registers)
- **Key Memory Docs**: 
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid performance pitfalls in timer implementation)
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (timer implementation patterns with lazy evaluation and event mechanisms)
  - openspec-memories/06_DML_Common_Patterns.md (register side-effect patterns and interrupt handling)

## Why
Enable functional complex watchdog timer device by implementing behavior specified in specs/001-home-hfeng1-demo/spec.md. The device provides system reset functionality if software fails to periodically refresh the timer, following ARM PrimeCell specification with 32-bit decrementing counter, configurable clock dividers, interrupt/reset generation, lock protection, and integration test mode.

## What Changes
- Implement register side-effects in wdt.dml across 5 functional capabilities
- Implement device behavior logic (timer core, interrupt control, reset control, lock protection, integration test)
- Add comprehensive test cases to validate all functionality
- Use multi-capability decomposition for independent implementation and testing

## Impact
- Affected specs: 001-home-hfeng1-demo (5 capabilities: timer-core, interrupt-control, reset-control, lock-protection, integration-test)
- Affected code:
  - Modified: simics-project/modules/wdt/wdt.dml (implement USER-TODO side-effects across all capabilities)
  - Added: simics-project/modules/wdt/test/s-*.py (comprehensive test cases for each capability)

## Capability Decomposition

This complex device (105 requirements) is decomposed into 5 independent capabilities:

1. **timer-core**: Basic 32-bit decrementing counter with clock divider support
2. **interrupt-control**: Interrupt generation, status management, and clearing
3. **reset-control**: Reset generation on second timeout and watchdog behavior
4. **lock-protection**: Lock mechanism preventing unauthorized register modifications
5. **integration-test**: Integration test mode for direct signal control

Each capability has its own spec delta and can be implemented/tested independently.
