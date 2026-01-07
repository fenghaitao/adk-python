# WDT Device Implementation Specification Delta

## ADDED Requirements

### Requirement: Watchdog Timer Core Functionality
The watchdog timer device SHALL be implemented as a 32-bit decrementing counter that counts down from the value stored in the WDOGLOAD register using event-based timing and lazy evaluation patterns.

#### Scenario: Counter Decrement Pattern
- **WHEN** WDOGCONTROL.INTEN is set to 1
- **THEN** the counter SHALL decrement using Simics event mechanism (NOT cycle-by-cycle updates)
- **AND** counter reads SHALL use lazy evaluation to calculate remaining value from saved start_time and start_value
- **AND** the implementation SHALL avoid Anti-Pattern #1 (clock signal modeling causing 100-1000x performance degradation)

#### Scenario: Counter Value Calculation
- **WHEN** software reads WDOGVALUE register
- **THEN** device SHALL calculate current value as: start_value - ((SIM_cycle_count() - start_time) / divider)
- **AND** calculation SHALL occur on-demand (lazy evaluation pattern)
- **AND** result SHALL handle underflow to 0 gracefully

### Requirement: Timer Event Scheduling and Management
The timer SHALL use Simics event objects to schedule timeout actions at counter expiration, with proper event cancellation and rescheduling when timer state changes.

#### Scenario: Event Scheduling on Timer Start
- **WHEN** WDOGCONTROL.INTEN transitions from 0 to 1
- **THEN** device SHALL post a timeout event scheduled for WDOGLOAD cycles in the future
- **AND** event handler SHALL be invoked when counter reaches 0
- **AND** implementation SHALL check event.posted() before posting new events to avoid multiple pending events

#### Scenario: Event Cancellation on Timer Stop
- **WHEN** WDOGCONTROL.INTEN transitions from 1 to 0
- **THEN** device SHALL cancel any pending timeout event using event.remove()
- **AND** counter value SHALL be preserved by updating counter_start_value before cancellation
- **AND** no timeout actions SHALL occur after timer disabled

#### Scenario: Event Rescheduling on Counter Reload
- **WHEN** software writes to WDOGLOAD while timer is running
- **THEN** device SHALL cancel existing timeout event
- **AND** device SHALL post new timeout event with updated WDOGLOAD value
- **AND** counter_start_time and counter_start_value SHALL be updated to current simulation time and new load value

### Requirement: Interrupt Generation on First Timeout
When the counter reaches zero for the first time with WDOGCONTROL.INTEN enabled, the device SHALL assert the wdogint interrupt signal (rising edge), set WDOGRIS[0] to 1, reload the counter from WDOGLOAD, and reschedule the timeout event.

#### Scenario: First Timeout Actions
- **WHEN** timeout event fires AND interrupt_pending flag is false
- **THEN** device SHALL set WDOGRIS bit 0 to 1
- **AND** device SHALL assert wdogint interrupt signal via signal_raise()
- **AND** device SHALL set interrupt_pending flag to true
- **AND** device SHALL reload counter: counter_start_value = WDOGLOAD.val, counter_start_time = SIM_cycle_count()
- **AND** if INTEN still set, device SHALL reschedule timeout event with WDOGLOAD value

#### Scenario: Interrupt Signal Behavior
- **WHEN** first timeout occurs
- **THEN** wdogint signal SHALL remain asserted (high) until software writes to WDOGINTCLR
- **AND** WDOGRIS[0] SHALL remain 1 until WDOGINTCLR write
- **AND** WDOGMIS[0] SHALL reflect (WDOGRIS[0] & INTEN) bitwise AND

### Requirement: Interrupt Clear Operation
Writing any value to the WDOGINTCLR register SHALL clear WDOGRIS[0], deassert the wdogint interrupt signal, clear the interrupt_pending flag, reload the counter from WDOGLOAD, and reschedule the timeout event if timer is still enabled.

#### Scenario: Interrupt Clear Sequence
- **WHEN** software writes any value to WDOGINTCLR register
- **THEN** device SHALL set WDOGRIS register value to 0
- **AND** device SHALL deassert wdogint interrupt signal via signal_lower()
- **AND** device SHALL clear interrupt_pending flag to false
- **AND** device SHALL reload counter: counter_start_value = WDOGLOAD.val, counter_start_time = SIM_cycle_count()
- **AND** if INTEN=1, device SHALL reschedule timeout event

#### Scenario: Interrupt Clear Bypasses Lock Protection
- **WHEN** device is locked (WDOGLOCK != 0) AND software writes to WDOGINTCLR
- **THEN** interrupt clear operation SHALL succeed regardless of lock state
- **AND** all interrupt clear actions SHALL execute normally

### Requirement: Reset Generation on Second Timeout
If the counter reaches zero for a second time while the interrupt is still asserted (WDOGRIS[0]=1, interrupt_pending=true) and WDOGCONTROL.RESEN is enabled, the device SHALL assert the wdogres reset signal.

#### Scenario: Second Timeout with Reset Enabled
- **WHEN** timeout event fires AND interrupt_pending flag is true AND WDOGCONTROL.RESEN=1
- **THEN** device SHALL assert wdogres reset signal via signal_raise()
- **AND** device SHALL log reset generation event
- **AND** wdogres signal SHALL remain asserted until system reset completes

#### Scenario: Second Timeout without Reset Enabled
- **WHEN** timeout event fires AND interrupt_pending flag is true AND WDOGCONTROL.RESEN=0
- **THEN** device SHALL NOT assert wdogres reset signal
- **AND** device SHALL continue interrupt-only mode (reload counter and reschedule)
- **AND** interrupt SHALL continue to assert on each subsequent timeout until cleared

### Requirement: WDOGLOAD Register Side-Effects
The WDOGLOAD register SHALL support read and write operations with write side-effect of immediately reloading the counter value, subject to lock protection.

#### Scenario: WDOGLOAD Write Reloads Counter
- **WHEN** software writes value V to WDOGLOAD AND device is unlocked (WDOGLOCK=0)
- **THEN** register value SHALL update to V via default() write
- **AND** counter_start_value SHALL update to V
- **AND** counter_start_time SHALL update to current SIM_cycle_count()
- **AND** if timer running (INTEN=1), timeout event SHALL be cancelled and rescheduled with new value

#### Scenario: WDOGLOAD Write When Locked
- **WHEN** software writes to WDOGLOAD AND device is locked (WDOGLOCK != 0)
- **THEN** write operation SHALL be ignored (return early without calling default())
- **AND** register value SHALL remain unchanged
- **AND** counter state SHALL remain unchanged

### Requirement: WDOGVALUE Register Lazy Evaluation
The WDOGVALUE register SHALL support read-only operations returning the current counter value calculated on-demand using lazy evaluation from saved base values.

#### Scenario: WDOGVALUE Read Calculates Current Value
- **WHEN** software reads WDOGVALUE register
- **THEN** device SHALL calculate elapsed_cycles = (SIM_cycle_count() - counter_start_time)
- **AND** device SHALL calculate remaining_value = counter_start_value - elapsed_cycles
- **AND** if remaining_value < 0, device SHALL return 0 (handle underflow)
- **AND** calculated value SHALL be returned (NOT stored register value)

#### Scenario: WDOGVALUE Write Ignored
- **WHEN** software attempts write to WDOGVALUE register
- **THEN** write SHALL be ignored (read-only register)
- **AND** no side-effects SHALL occur

### Requirement: WDOGCONTROL Register Timer Control
The WDOGCONTROL register SHALL support read and write operations with write side-effects controlling timer enable/disable (INTEN bit) and reset enable (RESEN bit), subject to lock protection.

#### Scenario: INTEN Bit Starts Timer
- **WHEN** software writes WDOGCONTROL with INTEN transitioning from 0 to 1 AND device unlocked
- **THEN** register value SHALL update via default()
- **AND** counter_start_value SHALL be set to WDOGLOAD.val
- **AND** counter_start_time SHALL be set to SIM_cycle_count()
- **AND** timeout event SHALL be posted with counter_start_value cycles delay

#### Scenario: INTEN Bit Stops Timer
- **WHEN** software writes WDOGCONTROL with INTEN transitioning from 1 to 0 AND device unlocked
- **THEN** register value SHALL update via default()
- **AND** pending timeout event SHALL be cancelled via event.remove()
- **AND** current counter value SHALL be preserved in counter_start_value

#### Scenario: WDOGCONTROL Write When Locked
- **WHEN** software writes to WDOGCONTROL AND device is locked
- **THEN** write operation SHALL be ignored
- **AND** register value SHALL remain unchanged
- **AND** timer state SHALL remain unchanged

### Requirement: WDOGRIS Raw Interrupt Status
The WDOGRIS register SHALL be read-only returning the raw interrupt status, automatically set to 1 by timeout event handler and cleared to 0 by WDOGINTCLR write.

#### Scenario: WDOGRIS Read Returns Status
- **WHEN** software reads WDOGRIS register
- **THEN** device SHALL return current register value (bit 0 indicates interrupt status)
- **AND** no side-effects SHALL occur on read

#### Scenario: WDOGRIS Updated by Timeout Event
- **WHEN** first timeout event fires
- **THEN** WDOGRIS bit 0 SHALL be set to 1 by timeout_event.callback()
- **AND** value SHALL remain 1 until WDOGINTCLR write

#### Scenario: WDOGRIS Cleared by WDOGINTCLR
- **WHEN** software writes to WDOGINTCLR
- **THEN** WDOGRIS register value SHALL be set to 0
- **AND** subsequent reads SHALL return 0 until next timeout

### Requirement: WDOGMIS Masked Interrupt Status Calculation
The WDOGMIS register SHALL be read-only returning the calculated masked interrupt status as bitwise AND of WDOGRIS[0] and WDOGCONTROL.INTEN.

#### Scenario: WDOGMIS Calculation
- **WHEN** software reads WDOGMIS register
- **THEN** device SHALL read WDOGRIS bit 0 value
- **AND** device SHALL read WDOGCONTROL INTEN bit value
- **AND** device SHALL return (WDOGRIS[0] & INTEN) bitwise AND result

#### Scenario: WDOGMIS When Interrupt Masked
- **WHEN** WDOGRIS[0]=1 AND WDOGCONTROL.INTEN=0
- **THEN** WDOGMIS read SHALL return 0 (interrupt masked by INTEN=0)
- **AND** WDOGRIS[0] SHALL remain 1 (raw status unchanged)

### Requirement: WDOGLOCK Register Protection Mechanism
The WDOGLOCK register SHALL implement write protection by locking device when any value except 0x1ACCE551 is written, and unlocking when magic value 0x1ACCE551 is written.

#### Scenario: Lock Device
- **WHEN** software writes any value != 0x1ACCE551 to WDOGLOCK
- **THEN** locked state variable SHALL be set to true
- **AND** WDOGLOCK register value SHALL be set to 1
- **AND** subsequent WDOGLOCK reads SHALL return 1

#### Scenario: Unlock Device with Magic Value
- **WHEN** software writes 0x1ACCE551 to WDOGLOCK
- **THEN** locked state variable SHALL be set to false
- **AND** WDOGLOCK register value SHALL be set to 0
- **AND** subsequent WDOGLOCK reads SHALL return 0

#### Scenario: Lock Protection Enforced on Protected Registers
- **WHEN** device is locked (locked=true)
- **THEN** writes to WDOGLOAD SHALL be ignored
- **AND** writes to WDOGCONTROL SHALL be ignored
- **AND** writes to WDOGITCR SHALL be ignored
- **AND** writes to WDOGINTCLR SHALL succeed (bypass lock protection)
- **AND** all register reads SHALL succeed normally

### Requirement: WDOGITCR Integration Test Control
The WDOGITCR register SHALL control integration test mode, suspending normal timer operation when ITCR bit is set to 1 and resuming normal operation when cleared to 0, subject to lock protection.

#### Scenario: Enter Integration Test Mode
- **WHEN** software writes ITCR=1 to WDOGITCR AND device unlocked
- **THEN** test_mode flag SHALL be set to true
- **AND** any pending timeout event SHALL be cancelled
- **AND** normal counter operation SHALL be suspended
- **AND** WDOGITOP SHALL control output signals directly

#### Scenario: Exit Integration Test Mode
- **WHEN** software writes ITCR=0 to WDOGITCR
- **THEN** test_mode flag SHALL be set to false
- **AND** normal timer operation SHALL resume based on WDOGCONTROL.INTEN state
- **AND** if INTEN=1, timeout event SHALL be rescheduled

#### Scenario: WDOGITCR Write When Locked
- **WHEN** software writes to WDOGITCR AND device is locked
- **THEN** write operation SHALL be ignored
- **AND** test_mode state SHALL remain unchanged

### Requirement: WDOGITOP Direct Output Control in Test Mode
The WDOGITOP register SHALL provide direct control of wdogint and wdogres output signals when integration test mode is active (ITCR=1), with bit 0 controlling wdogint and bit 1 controlling wdogres.

#### Scenario: Direct Interrupt Output Control
- **WHEN** test_mode is active AND software writes WDOGITOP with bit 0 = 1
- **THEN** wdogint signal SHALL be asserted via signal_raise()
- **WHEN** test_mode is active AND software writes WDOGITOP with bit 0 = 0
- **THEN** wdogint signal SHALL be deasserted via signal_lower()

#### Scenario: Direct Reset Output Control
- **WHEN** test_mode is active AND software writes WDOGITOP with bit 1 = 1
- **THEN** wdogres signal SHALL be asserted via signal_raise()
- **WHEN** test_mode is active AND software writes WDOGITOP with bit 1 = 0
- **THEN** wdogres signal SHALL be deasserted via signal_lower()

#### Scenario: WDOGITOP Write When Test Mode Inactive
- **WHEN** test_mode is false (ITCR=0) AND software writes to WDOGITOP
- **THEN** write SHALL have no effect (return early)
- **AND** output signals SHALL remain in their normal operation state

### Requirement: Device State Variables for Checkpointing
The device SHALL declare saved state variables for timer base values, interrupt state, lock state, and test mode to support Simics checkpointing and restore.

#### Scenario: Saved Variables Declaration
- **WHEN** device is compiled
- **THEN** device SHALL declare `saved uint64 counter_start_time` variable
- **AND** device SHALL declare `saved uint32 counter_start_value` variable
- **AND** device SHALL declare `saved bool interrupt_pending` variable
- **AND** device SHALL declare `saved bool locked` variable
- **AND** device SHALL declare `saved bool test_mode` variable

#### Scenario: Checkpoint Save and Restore
- **WHEN** Simics performs checkpoint save
- **THEN** all saved variables SHALL be automatically serialized
- **WHEN** Simics performs checkpoint restore
- **THEN** all saved variables SHALL be automatically deserialized
- **AND** device state SHALL be restored correctly for continued operation

### Requirement: Timeout Event Object Declaration and Handler
The device SHALL declare a simple_cycle_event named timeout_event with a callback method that handles both first timeout (interrupt generation) and second timeout (reset generation) cases.

#### Scenario: Timeout Event Declaration
- **WHEN** device is compiled
- **THEN** device SHALL declare `event timeout_event is simple_cycle_event`
- **AND** device SHALL implement `method timeout_event.callback()` handler

#### Scenario: Timeout Event Handler First Timeout Path
- **WHEN** timeout_event.callback() is invoked AND interrupt_pending is false
- **THEN** handler SHALL execute first timeout actions (set WDOGRIS, assert interrupt, set interrupt_pending)
- **AND** handler SHALL reload counter and reschedule event

#### Scenario: Timeout Event Handler Second Timeout Path
- **WHEN** timeout_event.callback() is invoked AND interrupt_pending is true
- **THEN** if RESEN=1, handler SHALL assert wdogres reset signal
- **AND** if RESEN=0, handler SHALL continue interrupt-only mode

#### Scenario: Timeout Event Handler Test Mode Check
- **WHEN** timeout_event.callback() is invoked AND test_mode is true
- **THEN** handler SHALL return early without executing timeout actions
- **AND** normal timeout behavior SHALL be suspended

### Requirement: WDOGINT Interrupt Output Signal
The device SHALL declare a connect output port named WDOGINT implementing the signal interface for edge-triggered interrupt signal output.

#### Scenario: WDOGINT Signal Declaration
- **WHEN** device is compiled
- **THEN** device SHALL declare `connect WDOGINT { interface signal; }`
- **AND** port SHALL support signal_raise() and signal_lower() methods

#### Scenario: WDOGINT Assert on Timeout
- **WHEN** first timeout occurs
- **THEN** device SHALL call WDOGINT.signal.signal_raise() to assert interrupt (rising edge)
- **AND** signal SHALL remain asserted until WDOGINTCLR write

#### Scenario: WDOGINT Deassert on Interrupt Clear
- **WHEN** software writes to WDOGINTCLR
- **THEN** device SHALL call WDOGINT.signal.signal_lower() to deassert interrupt
- **AND** signal SHALL remain low until next timeout

### Requirement: WDOGRES Reset Output Signal
The device SHALL declare a connect output port named WDOGRES implementing the signal interface for level-triggered reset signal output.

#### Scenario: WDOGRES Signal Declaration
- **WHEN** device is compiled
- **THEN** device SHALL declare `connect WDOGRES { interface signal; }`
- **AND** port SHALL support signal_raise() and signal_lower() methods

#### Scenario: WDOGRES Assert on Second Timeout
- **WHEN** second timeout occurs with RESEN=1
- **THEN** device SHALL call WDOGRES.signal.signal_raise() to assert reset (level high)
- **AND** signal SHALL remain asserted until system reset completes

#### Scenario: WDOGRES Control in Test Mode
- **WHEN** test_mode active AND WDOGITOP bit 1 = 1
- **THEN** device SHALL call WDOGRES.signal.signal_raise()
- **WHEN** test_mode active AND WDOGITOP bit 1 = 0
- **THEN** device SHALL call WDOGRES.signal.signal_lower()

### Requirement: Anti-Pattern Prevention - No Clock Signal Modeling
The device implementation SHALL NOT implement cycle-accurate clock signal modeling with events posting to themselves every cycle, to avoid 100-1000x performance degradation.

#### Scenario: Lazy Evaluation Instead of Cycle-Accurate Updates
- **WHEN** implementing counter decrement
- **THEN** device SHALL use lazy evaluation pattern (calculate on read)
- **AND** device SHALL NOT use `this.post(1)` pattern posting events every cycle
- **AND** device SHALL NOT implement PCLK/WDOGCLK port handlers that update counter every cycle

#### Scenario: Event-Based Timeout Only
- **WHEN** timer is enabled
- **THEN** device SHALL post ONE event scheduled for counter expiration time
- **AND** device SHALL NOT post intermediate events for every cycle
- **AND** timeout event SHALL only fire when counter reaches 0

### Requirement: Anti-Pattern Prevention - No SIM_cycle_count in Init
The device implementation SHALL NOT call SIM_cycle_count() or SIM_time() in init() or post_init() methods, to avoid runtime crashes from uninitialized queue object.

#### Scenario: Timing State Initialization on First Access
- **WHEN** device initializes via init() or post_init()
- **THEN** device SHALL NOT call SIM_cycle_count() or SIM_time()
- **AND** counter_start_time and counter_start_value SHALL be initialized to 0 or appropriate defaults

#### Scenario: Timing State Update on Timer Enable
- **WHEN** WDOGCONTROL.INTEN transitions 0→1 (first timer start after init)
- **THEN** device SHALL initialize counter_start_time = SIM_cycle_count()
- **AND** device SHALL initialize counter_start_value = WDOGLOAD.val
- **AND** queue object SHALL be ready for SIM_cycle_count() call

### Requirement: Complete Timer Implementation Pattern
The device SHALL implement BOTH lazy evaluation for counter reads AND event mechanism for timeout actions, to avoid incomplete timer anti-pattern.

#### Scenario: Lazy Evaluation for Counter Reads
- **WHEN** software reads WDOGVALUE register
- **THEN** device SHALL calculate current value from saved base values (lazy evaluation)
- **AND** device SHALL NOT maintain continuously updated counter variable

#### Scenario: Event Mechanism for Timeout Actions
- **WHEN** counter reaches expiration time
- **THEN** device SHALL invoke timeout_event.callback() method
- **AND** callback SHALL execute timeout actions (interrupt, reset, reload)
- **AND** callback SHALL reschedule event for next timeout if timer still enabled

#### Scenario: Event Cancellation on Timer Disable
- **WHEN** timer is disabled
- **THEN** device SHALL cancel pending event via event.remove()
- **AND** no timeout actions SHALL occur after disable

### Requirement: Clock and Queue Configuration in Tests
Test scripts SHALL configure device with clock frequency and queue assignment before executing timer-related test operations.

#### Scenario: Clock and Queue Setup
- **WHEN** test script initializes device for testing
- **THEN** script SHALL create clock object with freq_mhz attribute (e.g., clk.freq_mhz = 100)
- **AND** script SHALL assign clock queue to device (e.g., dev.queue = clk)
- **AND** device SHALL be ready for SIM_cycle_count() and event operations

#### Scenario: Time Advancement in Tests
- **WHEN** test needs to advance simulation time
- **THEN** script SHALL use simics.SIM_continue(cycles) to advance by cycle count
- **AND** device timeout events SHALL fire during time advancement

### Requirement: Fake Object Pattern for Interrupt and Reset Testing
Test scripts SHALL create fake PIC and fake reset controller objects to capture and verify interrupt and reset signal assertions from the device.

#### Scenario: Fake PIC Object for Interrupt Testing
- **WHEN** test needs to verify interrupt signal behavior
- **THEN** test SHALL create FakePic class inheriting from pyobj.ConfObject
- **AND** FakePic SHALL implement signal interface with signal_raise() and signal_lower() methods
- **AND** FakePic SHALL track raised count to verify interrupt assertions
- **AND** test SHALL connect dev.WDOGINT = fake_pic before triggering interrupts

#### Scenario: Fake Reset Controller for Reset Testing
- **WHEN** test needs to verify reset signal behavior
- **THEN** test SHALL create FakeResetController class with signal interface
- **AND** controller SHALL track reset signal assertions
- **AND** test SHALL connect dev.WDOGRES = fake_reset_controller before triggering resets

### Requirement: Register Access Pattern in Tests
Test scripts SHALL use dev_util.bank_regs() wrapper to access device registers and fields, following Simics test best practices.

#### Scenario: Bank Proxy Creation
- **WHEN** test needs to access device registers
- **THEN** test SHALL get bank proxy: `regs = dev_util.bank_regs(device.bank.wdt_map)`
- **AND** test SHALL include `.bank.` namespace in bank reference
- **AND** test SHALL always read DML file to find exact bank name

#### Scenario: Register Read and Write
- **WHEN** test accesses registers via bank proxy
- **THEN** test SHALL write registers: `regs.WDOGLOAD.write(100)`
- **AND** test SHALL read registers: `value = regs.WDOGVALUE.read()`
- **AND** test SHALL access fields: `regs.WDOGCONTROL.write(dev_util.READ, INTEN=1)`

### Requirement: Test Coverage for All Requirements
Test scripts SHALL cover all functional requirements with specific test scenarios, achieving comprehensive verification of device behavior.

#### Scenario: Basic Timer Operation Coverage
- **WHEN** test suite executes
- **THEN** tests SHALL verify basic timer countdown (TEST-001, TEST-002, TEST-003)
- **AND** tests SHALL cover interrupt generation and clearing (TEST-004, TEST-005, TEST-006)
- **AND** tests SHALL cover reset generation scenarios (TEST-007, TEST-008, TEST-009)

#### Scenario: Lock Protection and Special Modes Coverage
- **WHEN** test suite executes
- **THEN** tests SHALL verify lock protection mechanism (TEST-010, TEST-011, TEST-012)
- **AND** tests SHALL cover integration test mode (TEST-013, TEST-014, TEST-015)
- **AND** tests SHALL cover edge cases (TEST-016, TEST-017, TEST-018, TEST-019, TEST-020)

#### Scenario: State Transition Coverage
- **WHEN** test suite executes
- **THEN** tests SHALL verify IDLE→COUNTING transition (TEST-021)
- **AND** tests SHALL verify COUNTING→INTERRUPT_PENDING transition (TEST-022)
- **AND** tests SHALL verify INTERRUPT_PENDING→RESET_ASSERTED transition (TEST-023)

### Requirement: Comprehensive Logging for Debugging
The device SHALL include comprehensive logging at appropriate verbosity levels for timer operations, interrupt generation, reset assertion, and lock protection operations.

#### Scenario: Timer Operation Logging
- **WHEN** timer starts or stops
- **THEN** device SHALL log at info level with details (e.g., "Timer started with load value %d")
- **WHEN** timeout event fires
- **THEN** device SHALL log timeout occurrence at info level

#### Scenario: Interrupt and Reset Logging
- **WHEN** interrupt is asserted or deasserted
- **THEN** device SHALL log at debug level with signal state
- **WHEN** reset signal is asserted
- **THEN** device SHALL log at warning level (critical event)

#### Scenario: Lock Protection Logging
- **WHEN** device is locked or unlocked
- **THEN** device SHALL log at debug level with lock state change
- **WHEN** write attempt is blocked by lock protection
- **THEN** device SHALL log at debug level indicating ignored write

### Requirement: No Editing of Auto-Generated Files
Implementation SHALL NOT modify auto-generated register definition files, preserving IP-XACT derived structure and allowing regeneration if needed.

#### Scenario: Preserve Auto-Generated Registers File
- **WHEN** implementing device behavior
- **THEN** developer SHALL NOT edit wdt-registers.dml file
- **AND** all register bank templates and structure SHALL remain unchanged
- **AND** register side-effects SHALL be implemented in wdt.dml via bank override

#### Scenario: Preserve Auto-Generated Imports
- **WHEN** adding new functionality to wdt.dml
- **THEN** developer SHALL preserve all import statements (import "wdt-registers.dml", import "simics/devs/signal.dml")
- **AND** developer SHALL NOT add new .dml files or modules
- **AND** developer SHALL NOT modify Makefile or XML files

### Requirement: Peripheral and PrimeCell ID Register Values
The peripheral ID and PrimeCell ID registers SHALL return fixed identification values matching ARM PrimeCell SP805 specification.

#### Scenario: Peripheral ID Register Values
- **WHEN** software reads WDOGPeriphID0 register
- **THEN** device SHALL return 0x00000005
- **WHEN** software reads WDOGPeriphID1 register
- **THEN** device SHALL return 0x00000018
- **WHEN** software reads WDOGPeriphID2 register
- **THEN** device SHALL return 0x00000018
- **WHEN** software reads WDOGPeriphID3 register
- **THEN** device SHALL return 0x00000000

#### Scenario: PrimeCell ID Register Values
- **WHEN** software reads WDOGPCellID0 register
- **THEN** device SHALL return 0x0000000D
- **WHEN** software reads WDOGPCellID1 register
- **THEN** device SHALL return 0x000000F0
- **WHEN** software reads WDOGPCellID2 register
- **THEN** device SHALL return 0x00000005
- **WHEN** software reads WDOGPCellID3 register
- **THEN** device SHALL return 0x000000B1
