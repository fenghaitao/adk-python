# Implementation Tasks

## 1. Counter and Timing Infrastructure (wdt.dml)

- [ ] 1.1 Implement lazy evaluation counter infrastructure
  - [ ] 1.1.1 Add saved session variables: `counter_start_time` (cycles_t), `counter_start_value` (uint32), `is_locked` (bool)
  - [ ] 1.1.2 Initialize timing state on first counter enable (not in init() - see Anti-Pattern #2)
  - [ ] 1.1.3 Implement step_value decoding logic (÷1, ÷2, ÷4, ÷8, ÷16) per FUNC-002
  - [ ] 1.1.4 Calculate effective counter decrement rate based on step_value and elapsed cycles
  - [ ] 1.1.5 Pattern reference: openspec-memories/04_DML_Timing_Timer_Modeling.md (Lazy Counter Evaluation section)
  
- [ ] 1.2 Implement event-based timeout mechanism
  - [ ] 1.2.1 Create `timeout_event` using `simple_cycle_event` template for counter expiry
  - [ ] 1.2.2 Implement `timeout_event.event()` method to handle counter reaching zero (set WDOGRIS, assert wdogint)
  - [ ] 1.2.3 Implement `schedule_timeout_event()` method to calculate cycles until zero and post event
  - [ ] 1.2.4 Implement `cancel_timeout_event()` method for interrupt clear and disable scenarios
  - [ ] 1.2.5 Anti-Pattern check: Do NOT use `this.post(1)` for cycle-by-cycle updates (see Anti-Pattern #1)

## 2. Register Side-Effects Implementation (wdt.dml)

- [ ] 2.1 Implement WDOGVALUE register (read-only counter value)
  - [ ] 2.1.1 `read_register()`: Calculate current counter value using lazy evaluation (elapsed cycles / step_value)
  - [ ] 2.1.2 Handle INTEN=0 case: Return frozen counter_start_value per BEHAV-001
  - [ ] 2.1.3 Handle counter underflow: Return 0 if calculated value would be negative
  - [ ] 2.1.4 Covers: FUNC-001, FUNC-004, REG-002

- [ ] 2.2 Implement WDOGLOAD register (reload value)
  - [ ] 2.2.1 `write_register()`: Check lock state first; return if locked per FUNC-011
  - [ ] 2.2.2 Update reload value stored in register (call default())
  - [ ] 2.2.3 Do NOT reload counter immediately per FUNC-019, BEHAV-004
  - [ ] 2.2.4 `read_register()`: Return current reload value (no side-effects)
  - [ ] 2.2.5 Covers: FUNC-019, REG-001, REG-012

- [ ] 2.3 Implement WDOGCONTROL register (enable, divider, interrupt/reset control)
  - [ ] 2.3.1 `write_register()`: Check lock state first; return if locked per FUNC-011
  - [ ] 2.3.2 Detect INTEN bit 0→1 transition: Reload counter from WDOGLOAD, restart timing, schedule timeout event per FUNC-017
  - [ ] 2.3.3 Detect INTEN bit 1→0 transition: Cancel timeout event, preserve counter value per FUNC-009, BEHAV-001
  - [ ] 2.3.4 Handle step_value change: Recalculate and reschedule timeout event if counter running per FUNC-002
  - [ ] 2.3.5 RESEN bit: Store for use in second timeout condition per FUNC-007, FUNC-010
  - [ ] 2.3.6 Covers: FUNC-002, FUNC-009, FUNC-010, FUNC-017, REG-003, BEHAV-001

- [ ] 2.4 Implement WDOGINTCLR register (interrupt clear)
  - [ ] 2.4.1 `write_register()`: Check lock state first; return if locked per FUNC-011
  - [ ] 2.4.2 Clear WDOGRIS[0] bit to 0 per FUNC-016
  - [ ] 2.4.3 De-assert wdogint output signal per FUNC-016
  - [ ] 2.4.4 Reload counter from WDOGLOAD register value per FUNC-016
  - [ ] 2.4.5 Restart counter timing state (new counter_start_time = SIM_cycle_count)
  - [ ] 2.4.6 Reschedule timeout event for new countdown period
  - [ ] 2.4.7 Covers: FUNC-006, FUNC-016, REG-004

- [ ] 2.5 Implement WDOGRIS register (raw interrupt status)
  - [ ] 2.5.1 `read_register()`: Return bit[0] reflecting raw interrupt state (set when counter reaches zero with INTEN=1)
  - [ ] 2.5.2 Bit is set by timeout_event, cleared by WDOGINTCLR write or INTEN 0→1 transition
  - [ ] 2.5.3 Covers: FUNC-005, REG-005, BEHAV-002

- [ ] 2.6 Implement WDOGMIS register (masked interrupt status)
  - [ ] 2.6.1 `read_register()`: Calculate and return (WDOGRIS[0] AND WDOGCONTROL[INTEN]) per REG-006
  - [ ] 2.6.2 This value drives wdogint signal output
  - [ ] 2.6.3 Covers: REG-006

- [ ] 2.7 Implement WDOGLOCK register (lock protection)
  - [ ] 2.7.1 `write_register()`: Check if value == 0x1ACCE551 (unlock magic value) per FUNC-012
  - [ ] 2.7.2 If magic value: Set is_locked = false (unlock device)
  - [ ] 2.7.3 If any other value: Set is_locked = true (lock device) per FUNC-013
  - [ ] 2.7.4 `read_register()`: Return 0x00000000 if unlocked, 0x00000001 if locked per FUNC-014
  - [ ] 2.7.5 Covers: FUNC-011, FUNC-012, FUNC-013, FUNC-014, FUNC-015, REG-007, BEHAV-006

## 3. Second Timeout and Reset Signal (wdt.dml)

- [ ] 3.1 Implement second timeout detection
  - [ ] 3.1.1 In timeout_event: Check if WDOGRIS[0] already set (first timeout already occurred)
  - [ ] 3.1.2 If WDOGRIS[0]=1 AND RESEN=1: Assert wdogres output signal per FUNC-007
  - [ ] 3.1.3 If WDOGRIS[0]=0: Set WDOGRIS[0]=1, assert wdogint, reload counter, reschedule event per FUNC-005, FUNC-018
  - [ ] 3.1.4 wdogres remains asserted until system reset per FUNC-008
  - [ ] 3.1.5 Covers: FUNC-007, FUNC-008, FUNC-018, BEHAV-008

## 4. Integration Test Mode (wdt.dml)

- [ ] 4.1 Implement WDOGITCR register (test mode enable)
  - [ ] 4.1.1 `write_register()`: Check lock state first; return if locked per FUNC-024
  - [ ] 4.1.2 If bit[0]=1: Enter integration test mode, cancel timeout event, freeze counter per FUNC-020, BEHAV-007
  - [ ] 4.1.3 If bit[0]=0: Exit integration test mode, resume normal counter operation per FUNC-023
  - [ ] 4.1.4 Covers: FUNC-020, FUNC-023, FUNC-024, REG-008, BEHAV-007

- [ ] 4.2 Implement WDOGITOP register (test mode output control)
  - [ ] 4.2.1 `write_register()`: Check lock state first; return if locked per FUNC-024
  - [ ] 4.2.2 Check if WDOGITCR[0]=1 (integration test mode active)
  - [ ] 4.2.3 If active: Directly control wdogint from bit[1] per FUNC-021
  - [ ] 4.2.4 If active: Directly control wdogres from bit[0] per FUNC-022
  - [ ] 4.2.5 If not active: Ignore write per FUNC-023
  - [ ] 4.2.6 Covers: FUNC-021, FUNC-022, FUNC-023, FUNC-024, REG-009

## 5. Signal Outputs Implementation (wdt.dml)

- [ ] 5.1 Implement wdogint interrupt signal output
  - [ ] 5.1.1 Add signal port: `port wdogint { implement signal; }`
  - [ ] 5.1.2 Assert signal in timeout_event when first timeout occurs
  - [ ] 5.1.3 De-assert signal when WDOGINTCLR written or INTEN 0→1 transition
  - [ ] 5.1.4 In integration test mode: Controlled by WDOGITOP[1]
  - [ ] 5.1.5 Covers: FUNC-005, FUNC-006, FUNC-021

- [ ] 5.2 Implement wdogres reset signal output
  - [ ] 5.2.1 Add signal port: `port wdogres { implement signal; }`
  - [ ] 5.2.2 Assert signal in timeout_event when second timeout occurs with RESEN=1
  - [ ] 5.2.3 De-assert only on system reset (hard reset method)
  - [ ] 5.2.4 In integration test mode: Controlled by WDOGITOP[0]
  - [ ] 5.2.5 Covers: FUNC-007, FUNC-008, FUNC-022, FUNC-032

## 6. Basic Functionality Tests (test/s-basic-operation.py)

- [ ] 6.1 Implement test configuration setup (common.py)
  - [ ] 6.1.1 Create minimal device configuration with clock setup (CRITICAL: set clk.freq_mhz BEFORE SIM_add_configuration)
  - [ ] 6.1.2 Set queue on device object (CRITICAL: prevents "Queue not set" errors)
  - [ ] 6.1.3 Import dev_util for register bank access
  - [ ] 6.1.4 Pattern reference: openspec-memories/02_Test_Configuration_Setup.md (Complete common.py Template section)

- [ ] 6.2 Implement initialization test
  - [ ] 6.2.1 Verify all registers have correct reset values (WDOGLOAD=0xFFFFFFFF, WDOGVALUE=0xFFFFFFFF, WDOGCONTROL=0x00000000, etc.)
  - [ ] 6.2.2 Verify device is unlocked after reset (WDOGLOCK reads 0x00000000)
  - [ ] 6.2.3 Verify wdogint and wdogres signals de-asserted
  - [ ] 6.2.4 Covers: TEST-001 (initialization), FUNC-015, FUNC-031, FUNC-032

- [ ] 6.3 Implement basic countdown test
  - [ ] 6.3.1 Configure WDOGLOAD with small test value (e.g., 1000)
  - [ ] 6.3.2 Enable timer by writing INTEN=1 to WDOGCONTROL
  - [ ] 6.3.3 Read WDOGVALUE multiple times, verify decrementing behavior
  - [ ] 6.3.4 Verify counter decrements at rate determined by step_value
  - [ ] 6.3.5 Covers: TEST-001 (basic countdown), FUNC-001, FUNC-002, FUNC-003, FUNC-004

- [ ] 6.4 Implement interrupt generation test
  - [ ] 6.4.1 Configure small WDOGLOAD value, enable INTEN=1
  - [ ] 6.4.2 Advance simulation time to reach timeout
  - [ ] 6.4.3 Verify WDOGRIS[0]=1, WDOGMIS[0]=1, wdogint asserted
  - [ ] 6.4.4 Write to WDOGINTCLR, verify interrupt cleared and counter reloaded
  - [ ] 6.4.5 Covers: TEST-001 (interrupt), FUNC-005, FUNC-006, FUNC-016

- [ ] 6.5 Implement INTEN=0 behavior test
  - [ ] 6.5.1 Start counter with INTEN=1
  - [ ] 6.5.2 Clear INTEN to 0, verify counter preserves value (no decrement)
  - [ ] 6.5.3 Let time pass beyond timeout, verify no interrupt generated
  - [ ] 6.5.4 Covers: TEST-001, FUNC-009, BEHAV-001

## 7. Reset Generation Tests (test/s-reset-generation.py)

- [ ] 7.1 Implement complete watchdog sequence test
  - [ ] 7.1.1 Configure WDOGLOAD, enable INTEN=1, RESEN=1
  - [ ] 7.1.2 Let counter reach first timeout: verify WDOGRIS[0]=1, wdogint asserted
  - [ ] 7.1.3 Do NOT clear interrupt (simulate software failure)
  - [ ] 7.1.4 Let counter reach second timeout: verify wdogres asserted
  - [ ] 7.1.5 Verify both wdogint and wdogres asserted simultaneously
  - [ ] 7.1.6 Covers: TEST-002, FUNC-007, FUNC-008, BEHAV-008

- [ ] 7.2 Implement RESEN=0 test
  - [ ] 7.2.1 Configure WDOGLOAD, enable INTEN=1, RESEN=0
  - [ ] 7.2.2 Let counter reach first timeout, verify interrupt
  - [ ] 7.2.3 Let counter reach second timeout, verify wdogres NOT asserted
  - [ ] 7.2.4 Covers: TEST-002, FUNC-010

## 8. Lock Mechanism Tests (test/s-lock-mechanism.py)

- [ ] 8.1 Implement lock protection test
  - [ ] 8.1.1 Write non-magic value to WDOGLOCK, verify locked (reads 0x00000001)
  - [ ] 8.1.2 Attempt writes to WDOGLOAD, WDOGCONTROL, WDOGINTCLR: verify silently ignored
  - [ ] 8.1.3 Verify reads still work from all registers
  - [ ] 8.1.4 Covers: TEST-003, FUNC-011, FUNC-013, FUNC-014, REG-012, BEHAV-006

- [ ] 8.2 Implement unlock test
  - [ ] 8.2.1 Lock device, then write 0x1ACCE551 to WDOGLOCK
  - [ ] 8.2.2 Verify unlocked (WDOGLOCK reads 0x00000000)
  - [ ] 8.2.3 Verify writes to protected registers now succeed
  - [ ] 8.2.4 Covers: TEST-003, FUNC-012, FUNC-014

- [ ] 8.3 Implement lock persistence test
  - [ ] 8.3.1 Start timer with INTEN=1, lock device
  - [ ] 8.3.2 Let timer generate interrupt
  - [ ] 8.3.3 Verify interrupt state survives lock (WDOGRIS[0] still set)
  - [ ] 8.3.4 Verify cannot clear interrupt while locked (WDOGINTCLR ignored)
  - [ ] 8.3.5 Covers: TEST-003, BEHAV-009

## 9. Clock Divider Tests (test/s-clock-divider.py)

- [ ] 9.1 Implement step_value divider test
  - [ ] 9.1.1 Test each valid step_value: 000 (÷1), 001 (÷2), 010 (÷4), 011 (÷8), 100 (÷16)
  - [ ] 9.1.2 For each divider: Configure known WDOGLOAD, measure actual timeout period
  - [ ] 9.1.3 Verify timeout period matches expected (WDOGLOAD / step_value / clock_freq)
  - [ ] 9.1.4 Verify counter decrement rate matches step_value
  - [ ] 9.1.5 Covers: TEST-004, TEST-007, FUNC-002, BEHAV-003

- [ ] 9.2 Implement boundary condition tests
  - [ ] 9.2.1 Test WDOGLOAD = 0x00000001 (minimum value): verify immediate timeout
  - [ ] 9.2.2 Test WDOGLOAD = 0xFFFFFFFF (maximum value): verify very long timeout
  - [ ] 9.2.3 Test counter value at exact zero transition
  - [ ] 9.2.4 Covers: TEST-008

## 10. Integration Test Mode Tests (test/s-integration-test-mode.py)

- [ ] 10.1 Implement test mode entry/exit test
  - [ ] 10.1.1 Start normal counter operation, verify countdown
  - [ ] 10.1.2 Write 1 to WDOGITCR[0], verify counter freezes
  - [ ] 10.1.3 Write 0 to WDOGITCR[0], verify counter resumes
  - [ ] 10.1.4 Covers: TEST-005, FUNC-020, FUNC-023, BEHAV-007

- [ ] 10.2 Implement direct output control test
  - [ ] 10.2.1 Enter integration test mode (WDOGITCR[0]=1)
  - [ ] 10.2.2 Write to WDOGITOP[1], verify direct control of wdogint signal
  - [ ] 10.2.3 Write to WDOGITOP[0], verify direct control of wdogres signal
  - [ ] 10.2.4 Verify normal timeout mechanism bypassed (counter does not affect outputs)
  - [ ] 10.2.5 Covers: TEST-005, FUNC-021, FUNC-022

- [ ] 10.3 Implement test mode lock protection test
  - [ ] 10.3.1 Lock device, attempt to write WDOGITCR and WDOGITOP
  - [ ] 10.3.2 Verify writes ignored (device remains in normal mode)
  - [ ] 10.3.3 Covers: TEST-005, FUNC-024

## 11. Counter Reload Tests (test/s-basic-operation.py - additional)

- [ ] 11.1 Implement reload trigger tests
  - [ ] 11.1.1 Test reload on WDOGINTCLR write: Verify counter resets to WDOGLOAD value
  - [ ] 11.1.2 Test reload on INTEN 0→1 transition: Configure new WDOGLOAD, toggle INTEN, verify reload
  - [ ] 11.1.3 Test automatic reload on first timeout: Let counter reach zero, verify auto-reload from WDOGLOAD
  - [ ] 11.1.4 Covers: TEST-006, FUNC-016, FUNC-017, FUNC-018

- [ ] 11.2 Implement WDOGLOAD update timing test
  - [ ] 11.2.1 Start counter with WDOGLOAD=1000
  - [ ] 11.2.2 While counter running, write new value (2000) to WDOGLOAD
  - [ ] 11.2.3 Verify counter continues from original value (1000)
  - [ ] 11.2.4 Clear interrupt to reload, verify counter now uses new value (2000)
  - [ ] 11.2.5 Covers: TEST-006, FUNC-019, BEHAV-004

## 12. Register Read-Back Tests (test/s-basic-operation.py - additional)

- [ ] 12.1 Implement register read-back test
  - [ ] 12.1.1 Write known values to WDOGLOAD, WDOGCONTROL, read back and verify
  - [ ] 12.1.2 Verify WDOGVALUE returns live counter value (not stored register value)
  - [ ] 12.1.3 Verify WDOGMIS correctly reflects (WDOGRIS[0] AND INTEN)
  - [ ] 12.1.4 Verify WDOGLOCK read-back reflects lock state
  - [ ] 12.1.5 Covers: TEST-010

## 13. Build and Validation

- [ ] 13.1 Build device module
  - [ ] 13.1.1 Navigate to simics-project/ directory
  - [ ] 13.1.2 Run `make` to compile wdt.dml
  - [ ] 13.1.3 Fix any compilation errors (check openspec-memories/05_DML_Troubleshooting.md)
  - [ ] 13.1.4 Verify no register scope errors (see openspec-memories/07_DML_Register_Access_Scope.md)

- [ ] 13.2 Run test suite
  - [ ] 13.2.1 Run all test files: `./test/s-basic-operation.py`, `./test/s-reset-generation.py`, etc.
  - [ ] 13.2.2 Verify all tests pass
  - [ ] 13.2.3 Fix any test failures or runtime errors

- [ ] 13.3 Validate against spec
  - [ ] 13.3.1 Review spec requirements coverage: All 65 requirements implemented
  - [ ] 13.3.2 Cross-check anti-patterns: No clock signal modeling, no SIM_cycle_count in init(), complete timer implementation
  - [ ] 13.3.3 Verify test coverage: All TEST-001 through TEST-010 scenarios covered
