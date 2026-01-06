## 1. DML Implementation

- [ ] 1.1 Implement WDOGLOAD register side-effects (wdt.dml)
  - [ ] 1.1.1 Write: Store reload value when unlocked (FUNC-001, REG-001)
  - [ ] 1.1.2 Write: Block writes when locked (FUNC-011, BEHAV-007)
  - [ ] 1.1.3 Read: Return stored reload value
  - [ ] 1.1.4 Pattern: Use write protection check from openspec-memories/06_DML_Common_Patterns.md

- [ ] 1.2 Implement WDOGVALUE register with lazy evaluation (wdt.dml)
  - [ ] 1.2.1 Read: Calculate current counter value based on elapsed cycles (FUNC-001, FUNC-002)
  - [ ] 1.2.2 Use lazy evaluation pattern to avoid cycle-by-cycle updates
  - [ ] 1.2.3 Apply clock divider from WDOGCONTROL[4:2] to elapsed cycles (FUNC-014)
  - [ ] 1.2.4 Return saved value when timer disabled (INTEN=0)
  - [ ] 1.2.5 Anti-Pattern: NEVER use clock signal modeling (see openspec-memories/02_DML_Anti_Patterns.md)
  - [ ] 1.2.6 Pattern: Use lazy counter evaluation from openspec-memories/04_DML_Timing_Timer_Modeling.md

- [ ] 1.3 Implement WDOGCONTROL register side-effects (wdt.dml)
  - [ ] 1.3.1 INTEN bit write: Start/stop timer and schedule timeout event (FUNC-005, BEHAV-001)
  - [ ] 1.3.2 INTEN 0→1 transition: Reload counter from LOAD and start timer
  - [ ] 1.3.3 RESEN bit write: Enable/disable reset generation (FUNC-007)
  - [ ] 1.3.4 step_value field write: Configure clock divider (FUNC-014)
  - [ ] 1.3.5 Write protection: Block writes when locked (FUNC-011)

- [ ] 1.4 Implement WDOGINTCLR register side-effects (wdt.dml)
  - [ ] 1.4.1 Write: Clear interrupt status in WDOGRIS and WDOGMIS (FUNC-009, BEHAV-005)
  - [ ] 1.4.2 Write: Reload counter from LOAD and reschedule timeout event
  - [ ] 1.4.3 Write: Deassert interrupt output signal (BEHAV-006)
  - [ ] 1.4.4 Write protection: Block writes when locked

- [ ] 1.5 Implement WDOGLOCK register side-effects (wdt.dml)
  - [ ] 1.5.1 Write 0x1ACCE551: Unlock register access (REG-010)
  - [ ] 1.5.2 Write other value: Lock register access (REG-011)
  - [ ] 1.5.3 Read: Return 0x0 when unlocked, 0x1 when locked (REG-012)
  - [ ] 1.5.4 LOCK register itself always accessible (FUNC-013)

- [ ] 1.6 Implement timeout event mechanism (wdt.dml)
  - [ ] 1.6.1 Create simple_cycle_event for timeout handling
  - [ ] 1.6.2 Event handler: Set WDOGRIS[0] when counter reaches zero (BEHAV-002)
  - [ ] 1.6.3 Event handler: Generate interrupt when INTEN=1 (FUNC-005, BEHAV-003)
  - [ ] 1.6.4 Event handler: Generate reset on second timeout when RESEN=1 (FUNC-007)
  - [ ] 1.6.5 Event handler: Auto-reload counter and reschedule event (FUNC-003)
  - [ ] 1.6.6 Anti-Pattern: NEVER call SIM_cycle_count in init() (see openspec-memories/02_DML_Anti_Patterns.md)
  - [ ] 1.6.7 Pattern: Use event-based timeout from openspec-memories/04_DML_Timing_Timer_Modeling.md

- [ ] 1.7 Implement interrupt and reset output signals (wdt.dml)
  - [ ] 1.7.1 Assert interrupt when WDOGMIS[0]=1 (BEHAV-003)
  - [ ] 1.7.2 Deassert interrupt when INTCLR written (BEHAV-006)
  - [ ] 1.7.3 Assert reset on second timeout with RESEN=1 (FUNC-008, BEHAV-009)
  - [ ] 1.7.4 Keep reset asserted until system reset (FUNC-008)

- [ ] 1.8 Add session state management (wdt.dml)
  - [ ] 1.8.1 Mark timer state variables as 'saved' for checkpointing
  - [ ] 1.8.2 Save start_time, start_value, lock_status, interrupt_status, reset_status

## 2. Test Implementation

- [ ] 2.1 Implement basic timer functionality tests (test/s-basic-timer.py)
  - [ ] 2.1.1 Test timer countdown from LOAD value (TEST-001, FUNC-001)
  - [ ] 2.1.2 Test timer reload at zero (TEST-002, FUNC-003)
  - [ ] 2.1.3 Test timer disabled when INTEN=0 (BEHAV-001)
  - [ ] 2.1.4 Test counter wrapping behavior (BEHAV-006)
  - [ ] 2.1.5 Setup: Use clock configuration from openspec-memories/02_Test_Configuration_Setup.md

- [ ] 2.2 Implement interrupt generation tests (test/s-interrupt.py)
  - [ ] 2.2.1 Test interrupt assertion on timeout (TEST-003, FUNC-005)
  - [ ] 2.2.2 Test interrupt clearing with INTCLR (TEST-004, FUNC-009)
  - [ ] 2.2.3 Test WDOGRIS and WDOGMIS status registers (BEHAV-002, BEHAV-005)
  - [ ] 2.2.4 Test interrupt signal remains asserted until cleared (FUNC-006)

- [ ] 2.3 Implement reset generation tests (test/s-reset.py)
  - [ ] 2.3.1 Test reset assertion on second timeout (TEST-003, FUNC-007)
  - [ ] 2.3.2 Test reset requires RESEN=1 (BEHAV-003)
  - [ ] 2.3.3 Test reset signal persistence (FUNC-008, BEHAV-009)
  - [ ] 2.3.4 Test no reset when RESEN=0 (BEHAV-003)

- [ ] 2.4 Implement lock protection tests (test/s-lock.py)
  - [ ] 2.4.1 Test lock/unlock with magic value (TEST-005, REG-010, REG-011)
  - [ ] 2.4.2 Test register write protection when locked (FUNC-011, BEHAV-007)
  - [ ] 2.4.3 Test LOCK status read (TEST-006, REG-012)
  - [ ] 2.4.4 Test VALUE always readable when locked (FUNC-012)
  - [ ] 2.4.5 Test LOCK register always accessible (FUNC-013)

- [ ] 2.5 Implement clock divider tests (test/s-clock-divider.py)
  - [ ] 2.5.1 Test all valid divider settings (TEST-007, FUNC-014)
  - [ ] 2.5.2 Test divider affects timer decrement rate
  - [ ] 2.5.3 Test invalid divider values (FUNC-015)

- [ ] 2.6 Verify all tests pass
  - [ ] 2.6.1 Run all test files and confirm zero failures
  - [ ] 2.6.2 Verify coverage of all FUNC, REG, BEHAV, TEST requirements
