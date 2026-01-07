# Implementation Tasks for Watchdog Timer Device

## 1. Device State and Helper Methods

- [ ] 1.1 Add device state variables (wdt.dml, before bank declaration)
  - [ ] 1.1.1 Add `saved uint64 counter_start_time` - Simulation time when counter started
  - [ ] 1.1.2 Add `saved uint32 counter_start_value` - Counter value when started
  - [ ] 1.1.3 Add `saved bool interrupt_pending` - Interrupt asserted flag for second timeout tracking
  - [ ] 1.1.4 Add `saved bool locked` - Lock protection state
  - [ ] 1.1.5 Add `saved bool test_mode` - Integration test mode active flag
  - [ ] 1.1.6 Reference: memories/04_DML_Timing_Timer_Modeling.md for saved variable patterns

- [ ] 1.2 Add event object for timeout handling (wdt.dml, before bank declaration)
  - [ ] 1.2.1 Declare: `event timeout_event is simple_cycle_event`
  - [ ] 1.2.2 Implement `method timeout_event.callback()` to handle timeout actions
  - [ ] 1.2.3 Pattern: Check `timeout_event.posted()` before posting new events
  - [ ] 1.2.4 Pattern: Use `timeout_event.post(cycles)` to schedule, `timeout_event.remove()` to cancel
  - [ ] 1.2.5 Reference: memories/04_DML_Timing_Timer_Modeling.md lines 67-97 for event object usage

- [ ] 1.3 Add helper method: `calculate_counter_value()` (wdt.dml, device-level method)
  - [ ] 1.3.1 Calculate elapsed time: `(SIM_cycle_count() - counter_start_time)`
  - [ ] 1.3.2 Return remaining value: `counter_start_value - elapsed_cycles` (handle underflow to 0)
  - [ ] 1.3.3 Pattern: Lazy evaluation - calculate on-demand, don't update every cycle
  - [ ] 1.3.4 Anti-Pattern: NEVER call SIM_cycle_count() in init() (memories/02_DML_Anti_Patterns.md)
  - [ ] 1.3.5 Reference: memories/04_DML_Timing_Timer_Modeling.md lines 177-224 for countdown pattern

- [ ] 1.4 Add helper method: `schedule_timeout(uint32 cycles)` (wdt.dml, device-level method)
  - [ ] 1.4.1 Cancel existing event if posted: `if (timeout_event.posted()) timeout_event.remove()`
  - [ ] 1.4.2 Post new event: `timeout_event.post(cycles)`
  - [ ] 1.4.3 Log event scheduling at info level for debugging
  - [ ] 1.4.4 Reference: memories/04_DML_Timing_Timer_Modeling.md for event scheduling

- [ ] 1.5 Add helper method: `stop_timer()` (wdt.dml, device-level method)
  - [ ] 1.5.1 Cancel pending timeout event: `if (timeout_event.posted()) timeout_event.remove()`
  - [ ] 1.5.2 Preserve current counter value by updating counter_start_value
  - [ ] 1.5.3 Log timer stop at info level

## 2. Register Side-Effects Implementation

- [ ] 2.1 Implement WDOGLOAD register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.1.1 Write: Check lock protection - if locked, ignore write and return early
  - [ ] 2.1.2 Write: Update counter_start_value to written value
  - [ ] 2.1.3 Write: Update counter_start_time to current SIM_cycle_count()
  - [ ] 2.1.4 Write: If timer running (INTEN=1), reschedule timeout event with new load value
  - [ ] 2.1.5 Pattern: Immediate reload behavior per spec requirement REG-001
  - [ ] 2.1.6 Reference: memories/06_DML_Common_Patterns.md for register side-effect patterns

- [ ] 2.2 Implement WDOGVALUE register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.2.1 Read: Call calculate_counter_value() to get current counter value
  - [ ] 2.2.2 Read: Return calculated value (lazy evaluation pattern)
  - [ ] 2.2.3 Pattern: Read-only register, no write method needed
  - [ ] 2.2.4 Requirement: Covers REG-002, FUNC-004
  - [ ] 2.2.5 Reference: memories/04_DML_Timing_Timer_Modeling.md for lazy evaluation

- [ ] 2.3 Implement WDOGCONTROL register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.3.1 Write: Check lock protection - if locked, ignore write and return early
  - [ ] 2.3.2 Write: Extract INTEN (bit 0) and RESEN (bit 1) from written value
  - [ ] 2.3.3 Write: If INTEN transitions 0→1, start timer by calling schedule_timeout()
  - [ ] 2.3.4 Write: If INTEN transitions 1→0, stop timer by calling stop_timer()
  - [ ] 2.3.5 Write: Update register value via default() after processing
  - [ ] 2.3.6 Requirements: Covers REG-003, BEHAV-006, BEHAV-007, BEHAV-008
  - [ ] 2.3.7 Reference: memories/06_DML_Common_Patterns.md for control register patterns

- [ ] 2.4 Implement WDOGINTCLR register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.4.1 Write: Clear WDOGRIS register value (set to 0)
  - [ ] 2.4.2 Write: Deassert wdogint interrupt signal via port
  - [ ] 2.4.3 Write: Clear interrupt_pending flag
  - [ ] 2.4.4 Write: Reload counter from WDOGLOAD (reset start_time and start_value)
  - [ ] 2.4.5 Write: Reschedule timeout event if timer still enabled (INTEN=1)
  - [ ] 2.4.6 Note: Always succeeds regardless of lock state per BEHAV-004
  - [ ] 2.4.7 Requirements: Covers REG-004, FUNC-008
  - [ ] 2.4.8 Reference: memories/06_DML_Common_Patterns.md for write-to-clear patterns

- [ ] 2.5 Implement WDOGRIS register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.5.1 Read: Return current register value (set by timeout_event, cleared by WDOGINTCLR)
  - [ ] 2.5.2 Pattern: Read-only status register, updated by timeout event handler
  - [ ] 2.5.3 Requirement: Covers REG-005, FUNC-005
  - [ ] 2.5.4 Note: Value automatically updated by timeout_event.callback()

- [ ] 2.6 Implement WDOGMIS register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.6.1 Read: Get WDOGRIS bit 0 value
  - [ ] 2.6.2 Read: Get WDOGCONTROL INTEN bit value
  - [ ] 2.6.3 Read: Return bitwise AND (WDOGRIS[0] & INTEN)
  - [ ] 2.6.4 Pattern: Calculated read-only value per spec
  - [ ] 2.6.5 Requirement: Covers REG-005, FUNC-009

- [ ] 2.7 Implement WDOGLOCK register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.7.1 Write: If value == 0x1ACCE551, set locked = false (unlock)
  - [ ] 2.7.2 Write: If value != 0x1ACCE551, set locked = true (lock)
  - [ ] 2.7.3 Write: Update register value: 0 if unlocked, 1 if locked
  - [ ] 2.7.4 Read: Return 0 if unlocked, 1 if locked (from saved locked state)
  - [ ] 2.7.5 Pattern: Magic unlock value mechanism per spec
  - [ ] 2.7.6 Requirements: Covers REG-006, BEHAV-001, BEHAV-002, BEHAV-003
  - [ ] 2.7.7 Reference: memories/006-DML-Common-Patterns.md for lock mechanisms

- [ ] 2.8 Implement WDOGITCR register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.8.1 Write: Check lock protection - if locked, ignore write and return early
  - [ ] 2.8.2 Write: Extract ITCR bit (bit 0) from written value
  - [ ] 2.8.3 Write: If ITCR=1, enter test mode: set test_mode flag, cancel timer events
  - [ ] 2.8.4 Write: If ITCR=0, exit test mode: clear test_mode flag, resume normal operation
  - [ ] 2.8.5 Write: Update register value via default()
  - [ ] 2.8.6 Requirement: Covers REG-007, BEHAV-010
  - [ ] 2.8.7 Reference: openspec/project.md Section 4.5 for integration test behavior

- [ ] 2.9 Implement WDOGITOP register side-effects (wdt.dml, bank wdt_map)
  - [ ] 2.9.1 Write: Check if test_mode active, if not active return early (no effect)
  - [ ] 2.9.2 Write: Extract WDOGINT bit (bit 0) and WDOGRES bit (bit 1)
  - [ ] 2.9.3 Write: If WDOGINT=1, assert wdogint signal; if 0, deassert
  - [ ] 2.9.4 Write: If WDOGRES=1, assert wdogres signal; if 0, deassert
  - [ ] 2.9.5 Pattern: Direct output control in test mode only
  - [ ] 2.9.6 Requirement: Covers REG-007, BEHAV-010
  - [ ] 2.9.7 Reference: openspec/project.md Section 5.3 Flow: Integration Test Mode

## 3. Timeout Event Handler Implementation

- [ ] 3.1 Implement timeout_event.callback() method (wdt.dml, device level)
  - [ ] 3.1.1 Check if in test mode - if yes, return early (no automatic timeout in test mode)
  - [ ] 3.1.2 Check if interrupt already pending - this is second timeout case
  - [ ] 3.1.3 First timeout path (interrupt_pending == false):
    - [ ] 3.1.3.1 Set WDOGRIS bit 0 to 1 (interrupt status)
    - [ ] 3.1.3.2 Assert wdogint interrupt signal via port
    - [ ] 3.1.3.3 Set interrupt_pending flag to true
    - [ ] 3.1.3.4 Reload counter: counter_start_value = WDOGLOAD.val, counter_start_time = SIM_cycle_count()
    - [ ] 3.1.3.5 If INTEN still set, reschedule timeout event with WDOGLOAD value
    - [ ] 3.1.3.6 Log first timeout at info level
  - [ ] 3.1.4 Second timeout path (interrupt_pending == true):
    - [ ] 3.1.4.1 Check if RESEN bit set in WDOGCONTROL
    - [ ] 3.1.4.2 If RESEN=1, assert wdogres reset signal via port
    - [ ] 3.1.4.3 Log reset generation at info level
    - [ ] 3.1.4.4 If RESEN=0, continue interrupt-only mode (reload and reschedule)
  - [ ] 3.1.5 Requirements: Covers FUNC-003, FUNC-005, FUNC-006, FUNC-007
  - [ ] 3.1.6 Reference: memories/04_DML_Timing_Timer_Modeling.md lines 400-413 for interrupt generation
  - [ ] 3.1.7 Anti-Pattern: Avoid incomplete timer implementation (memories/02_DML_Anti_Patterns.md)

## 4. Signal Port Implementation

- [ ] 4.1 Implement WDOGINT output signal (wdt.dml, connect declaration)
  - [ ] 4.1.1 Declare: `connect WDOGINT { interface signal; }`
  - [ ] 4.1.2 Use signal_raise() to assert interrupt (rising edge)
  - [ ] 4.1.3 Use signal_lower() to deassert interrupt
  - [ ] 4.1.4 Requirement: Covers SIM-003, INTF-003
  - [ ] 4.1.5 Reference: memories/06_DML_Common_Patterns.md for interrupt device patterns

- [ ] 4.2 Implement WDOGRES output signal (wdt.dml, connect declaration)
  - [ ] 4.2.1 Declare: `connect WDOGRES { interface signal; }`
  - [ ] 4.2.2 Use signal_raise() to assert reset (level high)
  - [ ] 4.2.3 Use signal_lower() to deassert reset
  - [ ] 4.2.4 Requirement: Covers SIM-004, INTF-004
  - [ ] 4.2.5 Reference: memories/06_DML_Common_Patterns.md for signal output patterns

- [ ] 4.3 Remove unused clock signal ports (wdt.dml)
  - [ ] 4.3.1 Remove PCLK, WDOGCLK, WDOGCLKEN port declarations (not needed for functional model)
  - [ ] 4.3.2 Remove PRESETn port declaration (reset handled by Simics automatically)
  - [ ] 4.3.3 Anti-Pattern: DO NOT implement cycle-accurate clock signal handling (memories/02_DML_Anti_Patterns.md)

## 5. Test Implementation - Basic Timer Operation

- [ ] 5.1 Create test file: s-basic-timer.py (test/ directory)
  - [ ] 5.1.1 Setup: Configure device with clock (freq_mhz=100) and queue
  - [ ] 5.1.2 Setup: Use wdt_common.py helpers for device configuration
  - [ ] 5.1.3 Reference: memories/02_Test_Configuration_Setup.md for clock and queue setup

- [ ] 5.2 Test: Basic timer countdown (TEST-001)
  - [ ] 5.2.1 Write 100 to WDOGLOAD register
  - [ ] 5.2.2 Write INTEN=1 to WDOGCONTROL register
  - [ ] 5.2.3 Advance simulation by 50 cycles
  - [ ] 5.2.4 Read WDOGVALUE and verify ~50 remaining
  - [ ] 5.2.5 Reference: memories/03_Test_Register_Access.md for register access patterns

- [ ] 5.3 Test: Counter reload on timeout (TEST-002)
  - [ ] 5.3.1 Write 50 to WDOGLOAD, enable timer
  - [ ] 5.3.2 Advance simulation by 60 cycles (past timeout)
  - [ ] 5.3.3 Verify WDOGVALUE reloaded to 50
  - [ ] 5.3.4 Verify counter continues decrementing

- [ ] 5.4 Test: WDOGLOAD write reloads counter immediately (TEST-003)
  - [ ] 5.4.1 Write 1000 to WDOGLOAD, enable timer
  - [ ] 5.4.2 Advance simulation by 500 cycles
  - [ ] 5.4.3 Write 2000 to WDOGLOAD while timer running
  - [ ] 5.4.4 Verify WDOGVALUE immediately changes to 2000
  - [ ] 5.4.5 Verify counter decrements from new value

## 6. Test Implementation - Interrupt Generation

- [ ] 6.1 Create test file: s-interrupt-generation.py (test/ directory)
  - [ ] 6.1.1 Setup: Create fake PIC object to capture interrupt signals
  - [ ] 6.1.2 Setup: Connect fake PIC to device wdogint output
  - [ ] 6.1.3 Reference: memories/04_Test_Device_Outputs.md for fake object pattern

- [ ] 6.2 Test: Interrupt generation on first timeout (TEST-004)
  - [ ] 6.2.1 Write 20 to WDOGLOAD, write INTEN=1
  - [ ] 6.2.2 Advance simulation by 25 cycles (past timeout)
  - [ ] 6.2.3 Read WDOGRIS and verify bit 0 = 1
  - [ ] 6.2.4 Read WDOGMIS and verify bit 0 = 1
  - [ ] 6.2.5 Verify fake PIC raised count incremented

- [ ] 6.3 Test: Interrupt clear operation (TEST-005)
  - [ ] 6.3.1 Trigger interrupt (from TEST-004 setup)
  - [ ] 6.3.2 Write any value to WDOGINTCLR
  - [ ] 6.3.3 Read WDOGRIS and verify bit 0 = 0
  - [ ] 6.3.4 Read WDOGMIS and verify bit 0 = 0
  - [ ] 6.3.5 Verify counter reloaded to WDOGLOAD value

- [ ] 6.4 Test: WDOGMIS reflects masked interrupt status (TEST-006)
  - [ ] 6.4.1 Trigger interrupt, verify WDOGMIS[0]=1 with INTEN=1
  - [ ] 6.4.2 Write INTEN=0 to WDOGCONTROL (keep WDOGRIS[0]=1)
  - [ ] 6.4.3 Read WDOGMIS and verify bit 0 = 0 (masked by INTEN=0)
  - [ ] 6.4.4 Verify WDOGRIS[0] still = 1 (raw status unchanged)

## 7. Test Implementation - Reset Generation

- [ ] 7.1 Create test file: s-reset-generation.py (test/ directory)
  - [ ] 7.1.1 Setup: Create fake reset controller to capture reset signals
  - [ ] 7.1.2 Setup: Connect fake reset controller to device wdogres output
  - [ ] 7.1.3 Reference: memories/04_Test_Device_Outputs.md for fake object pattern

- [ ] 7.2 Test: Reset generation on second timeout (TEST-007)
  - [ ] 7.2.1 Write 50 to WDOGLOAD, write INTEN=1, RESEN=1
  - [ ] 7.2.2 Advance by 60 cycles (first timeout, interrupt generated)
  - [ ] 7.2.3 Do NOT write to WDOGINTCLR (leave interrupt pending)
  - [ ] 7.2.4 Advance by another 60 cycles (second timeout)
  - [ ] 7.2.5 Verify fake reset controller raised count incremented

- [ ] 7.3 Test: No reset when RESEN=0 (TEST-008)
  - [ ] 7.3.1 Write 50 to WDOGLOAD, write INTEN=1, RESEN=0
  - [ ] 7.3.2 Advance by 60 cycles (first timeout)
  - [ ] 7.3.3 Advance by another 60 cycles (second timeout)
  - [ ] 7.3.4 Verify reset signal NOT asserted
  - [ ] 7.3.5 Verify interrupt continues to assert on each timeout

- [ ] 7.4 Test: Reset prevented by interrupt clear (TEST-009)
  - [ ] 7.4.1 Write 30 to WDOGLOAD, write INTEN=1, RESEN=1
  - [ ] 7.4.2 Advance by 40 cycles (first timeout)
  - [ ] 7.4.3 Write to WDOGINTCLR before second timeout
  - [ ] 7.4.4 Advance by another 40 cycles
  - [ ] 7.4.5 Verify reset signal NOT asserted

## 8. Test Implementation - Lock Protection

- [ ] 8.1 Create test file: s-lock-protection.py (test/ directory)
  - [ ] 8.1.1 Reference: memories/03_Test_Register_Access.md for register testing patterns

- [ ] 8.2 Test: Lock protection prevents register writes (TEST-010)
  - [ ] 8.2.1 Write 1 to WDOGLOCK (lock device)
  - [ ] 8.2.2 Read WDOGLOCK and verify value = 1
  - [ ] 8.2.3 Write 500 to WDOGLOAD
  - [ ] 8.2.4 Read WDOGLOAD and verify value unchanged (write ignored)
  - [ ] 8.2.5 Write to WDOGCONTROL
  - [ ] 8.2.6 Read WDOGCONTROL and verify value unchanged

- [ ] 8.3 Test: Unlock with magic value (TEST-011)
  - [ ] 8.3.1 Write 1 to WDOGLOCK (lock device)
  - [ ] 8.3.2 Write 0x1ACCE551 to WDOGLOCK (unlock)
  - [ ] 8.3.3 Read WDOGLOCK and verify value = 0
  - [ ] 8.3.4 Write 500 to WDOGLOAD
  - [ ] 8.3.5 Read WDOGLOAD and verify value = 500 (write succeeded)

- [ ] 8.4 Test: WDOGINTCLR works regardless of lock state (TEST-012)
  - [ ] 8.4.1 Lock device, trigger interrupt
  - [ ] 8.4.2 Write to WDOGINTCLR while locked
  - [ ] 8.4.3 Verify WDOGRIS[0] = 0 (interrupt cleared)
  - [ ] 8.4.4 Verify counter reloaded

## 9. Test Implementation - Integration Test Mode

- [ ] 9.1 Create test file: s-integration-test.py (test/ directory)
  - [ ] 9.1.1 Reference: memories/04_Test_Device_Outputs.md for output signal testing

- [ ] 9.2 Test: Integration test mode entry (TEST-013)
  - [ ] 9.2.1 Write 0x1ACCE551 to WDOGLOCK (unlock)
  - [ ] 9.2.2 Write ITCR=1 to WDOGITCR
  - [ ] 9.2.3 Write INTEN=1 to WDOGCONTROL
  - [ ] 9.2.4 Advance simulation by 100 cycles
  - [ ] 9.2.5 Verify counter does NOT decrement (test mode suspends normal operation)

- [ ] 9.3 Test: Direct output control in test mode (TEST-014)
  - [ ] 9.3.1 Enter test mode (ITCR=1)
  - [ ] 9.3.2 Write 0x1 to WDOGITOP (set WDOGINT=1, WDOGRES=0)
  - [ ] 9.3.3 Verify wdogint asserted via fake PIC
  - [ ] 9.3.4 Write 0x2 to WDOGITOP (set WDOGINT=0, WDOGRES=1)
  - [ ] 9.3.5 Verify wdogres asserted via fake reset controller

- [ ] 9.4 Test: Test mode exit resumes normal operation (TEST-015)
  - [ ] 9.4.1 In test mode, write ITCR=0 to WDOGITCR
  - [ ] 9.4.2 Write INTEN=1 to WDOGCONTROL
  - [ ] 9.4.3 Advance simulation by 50 cycles
  - [ ] 9.4.4 Verify counter decrements normally

## 10. Test Implementation - Edge Cases

- [ ] 10.1 Create test file: s-edge-cases.py (test/ directory)

- [ ] 10.2 Test: Behavior with INTEN=0 (TEST-016)
  - [ ] 10.2.1 Write 100 to WDOGLOAD, write INTEN=0
  - [ ] 10.2.2 Advance simulation by 50 cycles
  - [ ] 10.2.3 Read WDOGVALUE and verify value = 100 (unchanged)

- [ ] 10.3 Test: Maximum counter value handling (TEST-017)
  - [ ] 10.3.1 Write 0xFFFFFFFF to WDOGLOAD
  - [ ] 10.3.2 Enable timer
  - [ ] 10.3.3 Advance by 1000 cycles
  - [ ] 10.3.4 Verify counter decrements correctly without overflow

- [ ] 10.4 Test: Zero load value handling (TEST-018)
  - [ ] 10.4.1 Write 0 to WDOGLOAD
  - [ ] 10.4.2 Enable timer
  - [ ] 10.4.3 Verify immediate timeout or first event cycle triggers timeout

- [ ] 10.5 Test: Register read-only enforcement (TEST-019)
  - [ ] 10.5.1 Attempt writes to WDOGVALUE, WDOGRIS, WDOGMIS
  - [ ] 10.5.2 Verify writes ignored
  - [ ] 10.5.3 Verify registers return actual status values

- [ ] 10.6 Test: Peripheral/PrimeCell ID registers (TEST-020)
  - [ ] 10.6.1 Read all ID registers (WDOGPeriphID0-3, WDOGPCellID0-3)
  - [ ] 10.6.2 Verify values match specification (0x05, 0x18, 0x18, 0x00, 0x0D, 0xF0, 0x05, 0xB1)

## 11. Documentation and Cleanup

- [ ] 11.1 Add comprehensive logging
  - [ ] 11.1.1 Log timer start/stop at info level
  - [ ] 11.1.2 Log timeout events (first and second) at info level
  - [ ] 11.1.3 Log interrupt assert/deassert at debug level
  - [ ] 11.1.4 Log reset generation at warning level
  - [ ] 11.1.5 Log lock/unlock operations at debug level

- [ ] 11.2 Verify no anti-patterns
  - [ ] 11.2.1 Confirm NO clock signal modeling with cycle-accurate updates
  - [ ] 11.2.2 Confirm NO SIM_cycle_count() calls in init() or post_init()
  - [ ] 11.2.3 Confirm BOTH lazy evaluation AND event mechanism implemented
  - [ ] 11.2.4 Reference: memories/02_DML_Anti_Patterns.md for checklist

- [ ] 11.3 Build and test
  - [ ] 11.3.1 Build device module: `make -C simics-project/modules/wdt`
  - [ ] 11.3.2 Run all tests: `make -C simics-project/modules/wdt test`
  - [ ] 11.3.3 Verify all 25+ test scenarios pass
  - [ ] 11.3.4 Fix any compilation or runtime errors

- [ ] 11.4 Update documentation
  - [ ] 11.4.1 Update README in test/ directory with test summary
  - [ ] 11.4.2 Add usage examples to module_load.py
  - [ ] 11.4.3 Verify all USER-TODO comments removed or addressed
