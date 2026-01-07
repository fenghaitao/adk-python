# Change: Implement ARM PrimeCell SP805 Watchdog Timer Device

## Why

Enable functional watchdog timer device by implementing register side-effects and device behavior specified in openspec/project.md. The DML skeleton with auto-generated register structure exists at simics-project/modules/wdt/ with USER-TODO placeholders that need implementation.

## What Changes

- **Modified**: simics-project/modules/wdt/wdt.dml - Implement USER-TODO register side-effects for WDOGLOAD, WDOGVALUE, WDOGCONTROL, WDOGINTCLR, WDOGRIS, WDOGMIS, WDOGLOCK, WDOGITCR, WDOGITOP
- **Modified**: simics-project/modules/wdt/wdt.dml - Add timer countdown logic with lazy evaluation and event-based timeout
- **Modified**: simics-project/modules/wdt/wdt.dml - Implement interrupt (WDOGINT) and reset (WDOGRES) signal outputs
- **Modified**: simics-project/modules/wdt/wdt.dml - Add lock protection mechanism with magic unlock value 0x1ACCE551
- **Modified**: simics-project/modules/wdt/wdt.dml - Implement integration test mode for direct output control
- **Added**: simics-project/modules/wdt/test/s-basic-timer.py - Basic timer countdown and interrupt tests
- **Added**: simics-project/modules/wdt/test/s-reset-generation.py - Reset generation on second timeout tests
- **Added**: simics-project/modules/wdt/test/s-lock-protection.py - Lock mechanism and register protection tests
- **Added**: simics-project/modules/wdt/test/s-integration-test.py - Integration test mode and output control tests
- **Added**: simics-project/modules/wdt/test/s-edge-cases.py - Edge case and error condition tests

## Impact

- **Affected specs**: wdt (ARM PrimeCell SP805 Watchdog Timer)
- **Affected code**: 
  - simics-project/modules/wdt/wdt.dml (9 register implementations + timer logic + interrupt/reset handling)
  - simics-project/modules/wdt/test/*.py (5 new test files with 25+ test scenarios)
- **Dependencies**: None - self-contained device implementation
- **Breaking changes**: None - initial implementation

## Context

- **Primary Spec:** openspec/project.md (69 implementation requirements: FUNC-001 to FUNC-009, REG-001 to REG-010, BEHAV-001 to BEHAV-010, SIM-001 to SIM-010, INTF-001 to INTF-005, plus 25 test scenarios TEST-001 to TEST-025)
- **Secondary Hardware Spec:** wdt.md, simics-wdt-spec.md (ARM PrimeCell SP805 compatible specification with register details and operational model)
- **Existing Code:** simics-project/modules/wdt/wdt.dml (DML skeleton with auto-generated register structure and USER-TODO placeholders), simics-project/modules/wdt/wdt-registers.dml (auto-generated, DO NOT EDIT)
- **Key Memory Docs:**
  - memories/02_DML_Anti_Patterns.md (CRITICAL: avoid clock signal modeling causing 100-1000x performance degradation, SIM_cycle_count() in init() causing crashes, and incomplete timer implementation)
  - memories/04_DML_Timing_Timer_Modeling.md (timer countdown with lazy evaluation, event-based timeout, interrupt generation patterns)
  - memories/008-code-examples/008_timer.md (synopsys-apb-wdt watchdog timer implementation with countdown and interrupt support)
  - memories/06_DML_Common_Patterns.md (interrupt device patterns and register side-effect implementation)
  - memories/03_Test_Register_Access.md (register testing with dev_util.bank_regs patterns)
  - memories/04_Test_Device_Outputs.md (fake object pattern for testing interrupts and signals)
  - memories/06_Test_Events_Timing.md (timer event testing with time advancement)

## Implementation Approach

### Core Principles (from Anti-Patterns)
1. ✅ Use lazy evaluation for counter reads (calculate from saved base values, NOT cycle-by-cycle updates)
2. ✅ Use event-based timeout mechanism (post events for timeout actions, cancel on disable)
3. ❌ NEVER model clock signals with cycle-accurate updates (causes 100-1000x slowdown)
4. ❌ NEVER call SIM_cycle_count() in init() or post_init() (causes runtime crashes)
5. ✅ Implement BOTH lazy evaluation AND event mechanism (incomplete timer anti-pattern)

### Device State Variables (saved for checkpointing)
- `counter_start_time` - Simulation time when counter started (uint64)
- `counter_start_value` - Counter value at start time (uint32)
- `interrupt_pending` - Interrupt asserted flag for second timeout detection (bool)
- `locked` - Lock protection state (bool)

### Timer Implementation Pattern
- **Counter Read**: Calculate remaining value = start_value - (elapsed_cycles / divider) using SIM_cycle_count()
- **Counter Write**: Update start_time and start_value, cancel/reschedule event
- **Timeout Event**: Set WDOGRIS[0]=1, assert WDOGINT, reload counter, reschedule if INTEN still set
- **Second Timeout**: If interrupt_pending && RESEN, assert WDOGRES reset signal

### Register Side-Effects Summary
- WDOGLOAD write → Reload counter immediately, restart timer if running
- WDOGVALUE read → Return calculated current value (lazy evaluation)
- WDOGCONTROL write → Start/stop timer based on INTEN, enable/disable reset on RESEN
- WDOGINTCLR write → Clear WDOGRIS[0], deassert WDOGINT, reload counter, clear interrupt_pending
- WDOGRIS read → Return interrupt status (set by timeout event, cleared by WDOGINTCLR)
- WDOGMIS read → Return (WDOGRIS[0] & WDOGCONTROL.INTEN)
- WDOGLOCK write → Set/clear lock protection (0x1ACCE551 unlocks, any other value locks)
- WDOGITCR write → Enter/exit integration test mode (suspends normal operation)
- WDOGITOP write → Direct control of WDOGINT/WDOGRES outputs when in test mode

### Test Strategy
- Use fake PIC object to capture interrupt signals
- Use fake reset controller to capture reset signals  
- Advance simulation time with SIM_continue(cycles) to trigger timeouts
- Verify register values and signal states with stest.expect_equal()
- Configure device with clock (freq_mhz) and queue before tests
