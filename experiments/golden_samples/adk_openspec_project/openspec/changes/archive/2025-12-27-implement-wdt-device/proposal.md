# Change: Implement Watchdog Timer (WDT) Device - Initial Implementation

## Why
Enable functional Simics watchdog timer device by implementing the register side-effects and device behavior specified in the hardware specifications. Currently we have a DML skeleton with auto-generated registers but need to implement the actual timer logic, interrupt/reset generation, lock protection, and other behavioral requirements.

## What Changes
- Modified: simics-project/modules/wdt/wdt.dml (implement register side-effects and timer functionality)
- Added: simics-project/modules/wdt/test/s-basic-operation.py (basic watchdog functionality tests)
- Added: simics-project/modules/wdt/test/s-interrupt-reset.py (interrupt and reset behavior tests)
- Added: simics-project/modules/wdt/test/s-lock-protection.py (lock protection tests)
- Added: simics-project/modules/wdt/test/s-integration-test-mode.py (integration test mode tests)

## Impact
- Affected specs: specs/001-nfs-site-disks/spec.md (watchdog timer functionality requirements)
- Affected code: simics-project/modules/wdt/ (DML implementation, test cases)
- Primary Memory Docs: 
  - openspec-memories/04_DML_Timing_Timer_Modeling.md (timer implementation patterns)
  - openspec-memories/02_DML_Anti_Patterns.md (CRITICAL: avoid performance pitfalls in timer implementation)
  - openspec-memories/07_DML_Register_Access_Scope.md (register access patterns)
  - openspec-memories/06_DML_Common_Patterns.md (register side-effect patterns)