# Spec Delta: Implement Watchdog Timer Device

This spec delta extracts and formalizes requirements from specs/001-tmp-hfeng1-demo/spec.md for implementation.

## ADDED Requirements

### Requirement: Timer Counter SHALL Decrement When Enabled
The watchdog timer SHALL be a 32-bit decrementing counter that decrements when INTEN is enabled and wclk_en is high.

#### Scenario: Timer Enabled and Counting
- **WHEN** INTEN bit in WDOGCONTROL is set to 1 AND wclk_en signal is high
- **THEN** the counter SHALL decrement from the WDOGLOAD value
- **AND** WDOGVALUE register SHALL reflect the current decremented value

#### Scenario: Timer Disabled
- **WHEN** INTEN bit in WDOGCONTROL is set to 0
- **THEN** the counter SHALL NOT decrement
- **AND** WDOGVALUE register SHALL remain unchanged

### Requirement: Clock Divider SHALL Control Decrement Rate
The timer SHALL decrement at a rate determined by the step_value field in WDOGCONTROL[4:2] register.

#### Scenario: Clock Divider Configuration
- **WHEN** step_value field is set to a valid value (000-100)
- **THEN** the timer SHALL decrement at the corresponding rate:
  - 000: Divide by 1 (base rate)
  - 001: Divide by 2 (half speed)
  - 010: Divide by 4 (quarter speed)
  - 011: Divide by 8 (1/8 speed)
  - 100: Divide by 16 (1/16 speed)

#### Scenario: Invalid Divider Values
- **WHEN** step_value field is set to 101-111
- **THEN** the behavior SHALL be undefined or treated as invalid

### Requirement: Timer SHALL Reload on Enable Transition
The timer SHALL reload with the value from WDOGLOAD when enabled after previously being disabled.

#### Scenario: Enable Timer After Disabled
- **WHEN** INTEN bit transitions from 0 to 1 in WDOGCONTROL
- **THEN** the counter SHALL reload from WDOGLOAD register value
- **AND** counting SHALL begin from the reloaded value

#### Scenario: Counter Already Running
- **WHEN** INTEN bit is already 1 and WDOGLOAD is written
- **THEN** the counter SHALL continue from current value
- **AND** the new WDOGLOAD value SHALL be used on next reload

### Requirement: WDOGVALUE Register SHALL Return Current Counter Value
The WDOGVALUE register SHALL always return the current value of the decrementing counter.

#### Scenario: Read Current Counter Value
- **WHEN** WDOGVALUE register is read
- **THEN** the current counter value SHALL be returned
- **AND** no side effects SHALL occur

#### Scenario: Counter Value Calculation
- **WHEN** counter is actively decrementing
- **THEN** WDOGVALUE SHALL reflect elapsed time since last update using lazy evaluation

### Requirement: Interrupt SHALL Assert on Counter Zero
When counter reaches zero and INTEN=1, device SHALL assert wdogint signal and set interrupt status registers.

#### Scenario: Interrupt Generation
- **WHEN** counter reaches zero AND INTEN bit is 1
- **THEN** wdogint signal SHALL be asserted
- **AND** WDOGRIS[0] SHALL be set to 1
- **AND** WDOGMIS[0] SHALL be set to 1

#### Scenario: No Interrupt When Disabled
- **WHEN** counter reaches zero AND INTEN bit is 0
- **THEN** wdogint signal SHALL NOT be asserted
- **AND** WDOGRIS[0] SHALL remain 0

### Requirement: Reset SHALL Assert on Second Timeout
When interrupt is asserted and timer reaches zero again without being cleared, device SHALL assert wdogres signal if RESEN=1.

#### Scenario: Reset Generation on Second Timeout
- **WHEN** counter reaches zero with interrupt already pending AND RESEN bit is 1
- **THEN** wdogres signal SHALL be asserted
- **AND** reset signal SHALL remain asserted until system reset

#### Scenario: No Reset When RESEN Disabled
- **WHEN** counter reaches zero with interrupt already pending AND RESEN bit is 0
- **THEN** wdogres signal SHALL NOT be asserted

### Requirement: WDOGINTCLR Write SHALL Clear Interrupt and Reload Counter
Writing to WDOGINTCLR register SHALL clear the interrupt flag and reload the counter from WDOGLOAD.

#### Scenario: Clear Interrupt and Reload
- **WHEN** any value is written to WDOGINTCLR register
- **THEN** interrupt_pending flag SHALL be cleared
- **AND** WDOGRIS[0] and WDOGMIS[0] SHALL become 0
- **AND** wdogint signal SHALL be deasserted
- **AND** counter SHALL reload from WDOGLOAD value

#### Scenario: Clear While Counter Running
- **WHEN** WDOGINTCLR is written while counter is running
- **THEN** counter SHALL restart from WDOGLOAD value
- **AND** timer SHALL continue counting

### Requirement: WDOGMIS SHALL Return Masked Interrupt Status
The WDOGMIS register SHALL return the logical AND of WDOGRIS[0] and WDOGCONTROL[0] (INTEN bit).

#### Scenario: Masked Interrupt Status Calculation
- **WHEN** WDOGMIS register is read
- **THEN** it SHALL return (WDOGRIS[0] AND INTEN)
- **AND** this SHALL reflect the actual interrupt signal state

#### Scenario: Interrupt Masked
- **WHEN** WDOGRIS[0] is 1 AND INTEN is 0
- **THEN** WDOGMIS[0] SHALL be 0
- **AND** wdogint signal SHALL NOT be asserted

### Requirement: Register Access SHALL Use APB Bus Interface
Register access SHALL be performed via APB bus interface with proper address decoding.

#### Scenario: APB Register Read
- **WHEN** APB read transaction occurs with valid register address
- **THEN** corresponding register value SHALL be returned on prdata
- **AND** pready signal SHALL indicate transaction completion

#### Scenario: APB Register Write
- **WHEN** APB write transaction occurs with valid register address
- **THEN** register SHALL be updated with pwdata value
- **AND** any side effects SHALL be triggered

### Requirement: Write Protection SHALL Apply When Locked
All registers except WDOGLOCK SHALL be write-protected when WDOGLOCK does not contain 0x1ACCE551.

#### Scenario: Writes Blocked When Locked
- **WHEN** device is locked (WDOGLOCK != 0x1ACCE551)
- **AND** write is attempted to protected register
- **THEN** write SHALL be ignored
- **AND** register value SHALL remain unchanged

#### Scenario: WDOGLOCK Always Writable
- **WHEN** device is locked
- **AND** write is attempted to WDOGLOCK register
- **THEN** write SHALL be accepted
- **AND** lock state SHALL be updated

### Requirement: Writing Unlock Code SHALL Enable Write Access
Writing 0x1ACCE551 to WDOGLOCK SHALL enable write access to protected registers.

#### Scenario: Unlock Device
- **WHEN** 0x1ACCE551 is written to WDOGLOCK register
- **THEN** device SHALL transition to unlocked state
- **AND** subsequent writes to protected registers SHALL succeed
- **AND** reading WDOGLOCK SHALL return 0x00000000

#### Scenario: Lock Device
- **WHEN** any value other than 0x1ACCE551 is written to WDOGLOCK
- **THEN** device SHALL transition to locked state
- **AND** subsequent writes to protected registers SHALL be ignored
- **AND** reading WDOGLOCK SHALL return 0x00000001

### Requirement: WDOGVALUE Register SHALL Be Read-Only
WDOGVALUE register SHALL be read-only and return current timer value without side effects.

#### Scenario: Read Counter Value
- **WHEN** WDOGVALUE register is read
- **THEN** current counter value SHALL be returned
- **AND** no registers SHALL be modified
- **AND** no signals SHALL change state

#### Scenario: Write Attempts Ignored
- **WHEN** write is attempted to WDOGVALUE register
- **THEN** write SHALL be ignored
- **AND** counter value SHALL remain unchanged

### Requirement: Clock Divider SHALL Support Five Valid Settings
The step_value field in WDOGCONTROL SHALL control the timer decrement rate with 5 valid settings.

#### Scenario: Divider Setting Applied
- **WHEN** step_value is written to WDOGCONTROL[4:2]
- **THEN** subsequent counter decrements SHALL use the configured divider
- **AND** timeout period SHALL be (WDOGLOAD × divider_value)

#### Scenario: Proportional Timing
- **WHEN** same WDOGLOAD value is used with different dividers
- **THEN** time to reach zero SHALL be proportional to divider value
- **AND** divider=16 SHALL take 16x longer than divider=1

### Requirement: Clock Divider Setting SHALL Determine Decrement Rate
Clock divider setting SHALL determine timer decrement rate where larger values cause slower decrementing.

#### Scenario: Faster Decrement with Smaller Divider
- **WHEN** step_value is set to 000 (÷1)
- **THEN** counter SHALL decrement at fastest rate

#### Scenario: Slower Decrement with Larger Divider
- **WHEN** step_value is set to 100 (÷16)
- **THEN** counter SHALL decrement at slowest rate
- **AND** timeout SHALL be 16x longer than ÷1 setting

### Requirement: Normal Mode SHALL Operate Timer
When WDOGITCR[0]=0, device SHALL operate in normal timer mode.

#### Scenario: Normal Timer Operation
- **WHEN** WDOGITCR[0] is 0
- **THEN** timer SHALL decrement based on WDOGCONTROL settings
- **AND** interrupts and resets SHALL be generated normally
- **AND** WDOGITOP register SHALL have no effect

### Requirement: Integration Test Mode SHALL Allow Direct Output Control
When WDOGITCR[0]=1, device SHALL enter integration test mode allowing direct control of outputs.

#### Scenario: Enter Test Mode
- **WHEN** WDOGITCR[0] is set to 1
- **THEN** device SHALL enter integration test mode
- **AND** normal timer operation SHALL be suspended
- **AND** WDOGITOP register SHALL control outputs directly

#### Scenario: Exit Test Mode
- **WHEN** WDOGITCR[0] is set to 0
- **THEN** device SHALL exit integration test mode
- **AND** normal timer operation SHALL resume

### Requirement: WDOGITOP SHALL Control Signals in Test Mode
In integration test mode, WDOGITOP register SHALL directly control wdogint and wdogres output signals.

#### Scenario: Direct Interrupt Control
- **WHEN** WDOGITCR[0]=1 AND WDOGITOP[1] is written
- **THEN** wdogint signal SHALL match WDOGITOP[1] value
- **AND** signal SHALL change immediately

#### Scenario: Direct Reset Control
- **WHEN** WDOGITCR[0]=1 AND WDOGITOP[0] is written
- **THEN** wdogres signal SHALL match WDOGITOP[0] value
- **AND** signal SHALL change immediately

### Requirement: Device SHALL Implement Peripheral ID Registers
Device SHALL implement WDOGPERIPHID0-7 registers containing ARM PrimeCell peripheral identification values.

#### Scenario: Read Peripheral ID Registers
- **WHEN** any WDOGPERIPHID register is read
- **THEN** it SHALL return the fixed identification value
- **AND** values SHALL match ARM PrimeCell specification

### Requirement: Device SHALL Implement Component ID Registers
Device SHALL implement WDOGPCELLID0-3 registers containing ARM PrimeCell component identification values.

#### Scenario: Read Component ID Registers
- **WHEN** any WDOGPCELLID register is read
- **THEN** it SHALL return the fixed identification value
- **AND** values SHALL match ARM PrimeCell specification

### Requirement: WDOGLOAD Register SHALL Support Read and Write
WDOGLOAD register SHALL support read and write operations and return the current load value.

#### Scenario: Write Load Value
- **WHEN** value is written to WDOGLOAD register (and device is unlocked)
- **THEN** the load value SHALL be stored
- **AND** subsequent reads SHALL return the written value

#### Scenario: Read Load Value
- **WHEN** WDOGLOAD register is read
- **THEN** the currently stored load value SHALL be returned

### Requirement: WDOGCONTROL Register SHALL Support Bit-Field Access
WDOGCONTROL register SHALL support read and write operations with bit-field access control.

#### Scenario: Write Control Bits
- **WHEN** value is written to WDOGCONTROL register (and device is unlocked)
- **THEN** INTEN, RESEN, and step_value fields SHALL be updated
- **AND** appropriate side effects SHALL trigger

#### Scenario: Read Control Bits
- **WHEN** WDOGCONTROL register is read
- **THEN** current values of all control bits SHALL be returned

### Requirement: WDOGINTCLR Register SHALL Be Write-Only
WDOGINTCLR register SHALL support write-only operations that trigger side effects.

#### Scenario: Write Clears Interrupt
- **WHEN** any value is written to WDOGINTCLR (and device is unlocked)
- **THEN** interrupt SHALL be cleared and counter SHALL reload

#### Scenario: Read Returns Zero
- **WHEN** WDOGINTCLR register is read
- **THEN** value 0 SHALL be returned
- **AND** no side effects SHALL occur

### Requirement: WDOGRIS Register SHALL Show Raw Interrupt Status
WDOGRIS register SHALL support read-only operations and return the raw interrupt status.

#### Scenario: Read Raw Interrupt Status
- **WHEN** WDOGRIS register is read
- **THEN** WDOGRIS[0] SHALL reflect interrupt_pending flag
- **AND** status SHALL be independent of INTEN setting

### Requirement: WDOGMIS Register SHALL Show Masked Interrupt Status
WDOGMIS register SHALL support read-only operations and return the masked interrupt status.

#### Scenario: Read Masked Interrupt Status
- **WHEN** WDOGMIS register is read
- **THEN** WDOGMIS[0] SHALL be (WDOGRIS[0] AND INTEN)
- **AND** this SHALL match wdogint signal state

### Requirement: WDOGLOCK Register SHALL Implement Lock/Unlock Functionality
WDOGLOCK register SHALL support read and write operations with special lock/unlock functionality.

#### Scenario: Lock Status Read
- **WHEN** WDOGLOCK register is read
- **THEN** it SHALL return 0x00000000 if unlocked
- **AND** it SHALL return 0x00000001 if locked

### Requirement: WDOGITCR Register SHALL Control Test Mode
WDOGITCR register SHALL support read and write operations for test mode control.

#### Scenario: Enable Test Mode
- **WHEN** 1 is written to WDOGITCR[0] (and device is unlocked)
- **THEN** device SHALL enter integration test mode

#### Scenario: Read Test Mode Status
- **WHEN** WDOGITCR register is read
- **THEN** current test mode setting SHALL be returned

### Requirement: WDOGITOP Register SHALL Control Test Outputs
WDOGITOP register SHALL support write-only operations for direct output control in test mode.

#### Scenario: Control Test Outputs
- **WHEN** value is written to WDOGITOP (and test mode is enabled)
- **THEN** wdogint and wdogres SHALL be set to WDOGITOP[1] and WDOGITOP[0] respectively

### Requirement: Timer SHALL NOT Decrement When INTEN is Zero
When INTEN=0, timer SHALL not decrement and no interrupts SHALL be generated.

#### Scenario: Timer Disabled by INTEN
- **WHEN** INTEN bit is 0
- **THEN** counter SHALL NOT decrement
- **AND** no interrupts SHALL be generated
- **AND** WDOGRIS[0] SHALL remain 0

### Requirement: Interrupt Status SHALL Set When Counter Reaches Zero
When INTEN=1 and timer reaches zero, WDOGRIS[0] SHALL be set to 1 and wdogint signal asserted.

#### Scenario: Set Interrupt Status on Timeout
- **WHEN** counter reaches zero AND INTEN=1
- **THEN** WDOGRIS[0] SHALL be set to 1
- **AND** wdogint signal SHALL be asserted
- **AND** interrupt SHALL remain until cleared

### Requirement: Reset Signal SHALL Remain Asserted Until System Reset
When wdogres signal is asserted, it SHALL remain active until system reset occurs.

#### Scenario: Reset Signal Persistence
- **WHEN** wdogres signal is asserted due to second timeout
- **THEN** signal SHALL remain asserted
- **AND** signal SHALL only be cleared by system reset (wrst_n or prst_n)

### Requirement: Interrupt Signal SHALL Remain Until Cleared
The wdogint signal SHALL remain asserted until cleared by writing to WDOGINTCLR register.

#### Scenario: Interrupt Persistence
- **WHEN** wdogint signal is asserted
- **THEN** signal SHALL remain asserted
- **AND** signal SHALL only be cleared by WDOGINTCLR write

### Requirement: Register Writes SHALL Be Ignored When Locked
When the watchdog timer is locked, any write attempts to protected registers SHALL be ignored.

#### Scenario: Protected Register Write Blocked
- **WHEN** device is locked
- **AND** write is attempted to any register except WDOGLOCK
- **THEN** write SHALL be ignored
- **AND** register value SHALL not change

### Requirement: Timer SHALL Only Decrement When Both INTEN and Clock Enable Active
The timer SHALL only decrement when both INTEN=1 and wclk_en=1.

#### Scenario: Timer Decrements with Both Enables
- **WHEN** INTEN=1 AND wclk_en=1
- **THEN** timer SHALL decrement

#### Scenario: Timer Paused by Clock Enable
- **WHEN** INTEN=1 AND wclk_en=0
- **THEN** timer SHALL NOT decrement
- **AND** counter value SHALL remain unchanged

### Requirement: Reset Signals SHALL Reset Device to Initial State
Reset signals SHALL reset the device to its initial state.

#### Scenario: Device Reset
- **WHEN** wrst_n or prst_n is asserted (low)
- **THEN** all registers SHALL return to reset values
- **AND** all output signals SHALL be deasserted
- **AND** any pending timer events SHALL be cancelled

### Requirement: Registers SHALL Return to Reset Values on Reset
When reset occurs, all registers SHALL return to their specified reset values.

#### Scenario: Register Reset Values
- **WHEN** device reset occurs
- **THEN** WDOGLOAD SHALL be 0xFFFFFFFF
- **AND** WDOGVALUE SHALL be 0xFFFFFFFF
- **AND** WDOGCONTROL SHALL be 0x00000000
- **AND** all other registers SHALL match specification reset values

### Requirement: Basic Timer Countdown SHALL Function Correctly
The system SHALL verify basic timer countdown functionality.

#### Scenario: Timer Counts Down to Zero
- **WHEN** small value (e.g., 0x100) is written to WDOGLOAD AND INTEN=1
- **THEN** counter SHALL decrement in WDOGVALUE register
- **AND** interrupt SHALL be generated when counter reaches zero

### Requirement: Interrupt and Reset Generation Sequence SHALL Work
The system SHALL verify interrupt and reset generation sequence.

#### Scenario: First Timeout Generates Interrupt
- **WHEN** timer counts to zero with INTEN=1 and RESEN=1
- **THEN** interrupt SHALL be generated (WDOGRIS=1, WDOGMIS=1)

#### Scenario: Second Timeout Generates Reset
- **WHEN** timer counts to zero again without clearing interrupt AND RESEN=1
- **THEN** reset signal SHALL be asserted (wdogres active)

### Requirement: Lock Protection Mechanism SHALL Prevent Unauthorized Writes
The system SHALL verify lock protection mechanism prevents unauthorized writes.

#### Scenario: Unlock Allows Writes
- **WHEN** 0x1ACCE551 is written to WDOGLOCK
- **THEN** writes to WDOGLOAD SHALL succeed

#### Scenario: Lock Prevents Writes
- **WHEN** device is locked (non-magic value written to WDOGLOCK)
- **THEN** writes to WDOGLOAD SHALL fail (register unchanged)

### Requirement: Clock Divider Settings SHALL Produce Proportional Timing
The system SHALL verify different clock divider settings produce proportional timing.

#### Scenario: Divider Affects Timeout Duration
- **WHEN** timer configured with same WDOGLOAD but different step_value
- **THEN** time to reach zero SHALL be proportional to divider value
- **AND** larger divider SHALL take proportionally longer

### Requirement: Integration Test Mode SHALL Allow Direct Signal Control
The system SHALL verify integration test mode functionality allows direct signal control.

#### Scenario: Test Mode Enables Direct Control
- **WHEN** WDOGITCR[0]=1 to enable test mode
- **AND** different values are written to WDOGITOP register
- **THEN** wdogint and wdogres signals SHALL be directly controlled

### Requirement: All Registers SHALL Return Correct Reset Values
The system SHALL verify all registers return correct reset values.

#### Scenario: Reset Values Match Specification
- **WHEN** device is in reset state
- **AND** all registers are read
- **THEN** all registers SHALL return expected reset values per specification

### Requirement: Interrupt Status Registers SHALL Reflect Interrupt State
The system SHALL verify interrupt status register behavior reflects interrupt state.

#### Scenario: Status Registers Updated on Interrupt
- **WHEN** timer generates interrupt
- **THEN** WDOGRIS SHALL show raw status
- **AND** WDOGMIS SHALL show masked status (WDOGRIS AND INTEN)

### Requirement: Counter Reload SHALL Function After Interrupt Clear
The system SHALL verify counter reload functionality after interrupt clear.

#### Scenario: Counter Reloads After Clear
- **WHEN** timer has interrupt pending
- **AND** WDOGINTCLR is written
- **THEN** counter SHALL reload from WDOGLOAD value
- **AND** interrupt SHALL be cleared
- **AND** timer SHALL continue counting
