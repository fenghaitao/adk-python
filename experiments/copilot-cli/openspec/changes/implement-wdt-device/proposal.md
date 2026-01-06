# Change: Implement Simics Watchdog Timer Device

## Why

Enable functional watchdog timer device by implementing register side-effects, counter logic, and timeout behavior as specified in specs/001-read-the-simics/spec.md. DML skeleton exists with auto-generated register structure and USER-TODO placeholders requiring implementation.

## What Changes

- **Modified**: `simics-project/modules/wdt/wdt.dml` - Implement USER-TODO register side-effects for all functional registers (WDOGLOAD, WDOGVALUE, WDOGCONTROL, WDOGINTCLR, WDOGRIS, WDOGMIS, WDOGLOCK, WDOGITCR, WDOGITOP)
- **Added**: `simics-project/modules/wdt/test/s-basic-operation.py` - Basic watchdog timer functionality tests
- **Added**: `simics-project/modules/wdt/test/s-reset-generation.py` - Complete watchdog sequence with reset signal tests
- **Added**: `simics-project/modules/wdt/test/s-lock-mechanism.py` - Lock protection mechanism tests
- **Added**: `simics-project/modules/wdt/test/s-clock-divider.py` - Clock divider and timeout period tests
- **Added**: `simics-project/modules/wdt/test/s-integration-test-mode.py` - Integration test mode tests
- **Added**: `simics-project/modules/wdt/test/common.py` - Shared test configuration and helper functions

## Impact

- **Affected specs**: wdt-implementation (new capability)
- **Affected code**: 
  - `simics-project/modules/wdt/wdt.dml` (register side-effects implementation)
  - `simics-project/modules/wdt/test/*.py` (new test files)
- **Implementation approach**: 
  - Use lazy evaluation pattern for counter (calculate on-demand, not cycle-by-cycle)
  - Use event-based timing for timeout callbacks (avoid Anti-Pattern #1)
  - Initialize timing state on first use, not in init() (avoid Anti-Pattern #2)
  - Implement both lazy evaluation AND event mechanism (avoid Anti-Pattern #3)

## Context

- **Primary Spec**: specs/001-read-the-simics/spec.md (65 functional requirements: FUNC-001 to FUNC-032, REG-001 to REG-013, BEHAV-001 to BEHAV-010, TEST-001 to TEST-010)
- **Secondary Hardware Spec**: wdt.md (Chinese hardware documentation with detailed register descriptions)
- **Existing Code**: simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated registers and USER-TODO placeholders)
- **Key Memory Docs**: 
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid clock signal modeling, SIM_cycle_count in init, incomplete timer implementations)
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (lazy evaluation + event-based timeout patterns)
  - openspec-memories/06_DML_Common_Patterns.md (register side-effect patterns)
  - openspec-memories/07_DML_Register_Access_Scope.md (MANDATORY: prevent register scope errors)
  - openspec-memories/02_Test_Configuration_Setup.md (CRITICAL: clock/queue setup patterns)
