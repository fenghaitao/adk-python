## ADDED Requirements

### Requirement: Timer Counter SHALL Decrement from LOAD Value
The device SHALL implement a 32-bit decrementing counter that starts counting from the value stored in the LOAD register.

#### Scenario: Counter Initialization
- **WHEN** INTEN bit transitions from 0 to 1
- **THEN** counter SHALL be loaded with WDOGLOAD register value
- **AND** counter SHALL begin decrementing

#### Scenario: Counter Read
- **WHEN** WDOGVALUE register is read
- **THEN** device SHALL return current counter value calculated using lazy evaluation
- **AND** calculation SHALL account for elapsed cycles since counter start

### Requirement: Timer SHALL Apply Clock Divider to Decrement Rate
The timer SHALL decrement at a rate determined by the clock divider specified in CONTROL[4:2].

#### Scenario: Clock Divider Configuration
- **WHEN** step_value field is set to 000 (÷1)
- **THEN** timer SHALL decrement once per clock cycle
- **WHEN** step_value field is set to 001 (÷2)
- **THEN** timer SHALL decrement once every 2 clock cycles
- **WHEN** step_value field is set to 010 (÷4)
- **THEN** timer SHALL decrement once every 4 clock cycles
- **WHEN** step_value field is set to 011 (÷8)
- **THEN** timer SHALL decrement once every 8 clock cycles
- **WHEN** step_value field is set to 100 (÷16)
- **THEN** timer SHALL decrement once every 16 clock cycles

#### Scenario: Invalid Divider Values
- **WHEN** step_value field is set to 101-111
- **THEN** values SHALL be treated as invalid

### Requirement: Timer SHALL Reload Counter at Zero
The timer SHALL reload with the value in LOAD when it reaches zero.

#### Scenario: Counter Reload
- **WHEN** counter reaches zero
- **THEN** counter SHALL reload from WDOGLOAD register
- **AND** timer SHALL continue decrementing if INTEN=1

### Requirement: Timer SHALL Continue After Zero When INTEN=0
The timer SHALL continue decrementing after reaching zero if INTEN is not set.

#### Scenario: Timer Disabled Mode
- **WHEN** INTEN=0 and counter reaches zero
- **THEN** timer SHALL reload and continue
- **AND** no interrupt SHALL be generated

### Requirement: Device SHALL Assert Interrupt When Counter Reaches Zero
When the counter reaches zero and INTEN=1, the device SHALL assert the interrupt signal.

#### Scenario: Interrupt Generation
- **WHEN** counter reaches zero and INTEN=1
- **THEN** WDOGRIS[0] SHALL be set to 1
- **AND** interrupt output signal SHALL be asserted

### Requirement: Interrupt Signal SHALL Remain Asserted Until Cleared
The interrupt signal SHALL remain asserted until cleared by writing to INTCLR.

#### Scenario: Interrupt Persistence
- **WHEN** interrupt is asserted
- **THEN** interrupt signal SHALL remain high
- **AND** WDOGRIS[0] SHALL remain 1
- **UNTIL** WDOGINTCLR register is written

### Requirement: Device SHALL Generate Reset on Second Timeout
If the counter reaches zero again while interrupt is asserted and RESEN=1, the device SHALL assert the reset signal.

#### Scenario: Reset Generation
- **WHEN** counter reaches zero for second consecutive time
- **AND** interrupt is still asserted (WDOGRIS[0]=1)
- **AND** RESEN=1
- **THEN** reset output signal SHALL be asserted

#### Scenario: No Reset When RESEN=0
- **WHEN** counter reaches zero for second consecutive time
- **AND** RESEN=0
- **THEN** reset signal SHALL NOT be asserted

### Requirement: Reset Signal SHALL Persist Until System Reset
The reset signal SHALL remain asserted until a system reset occurs.

#### Scenario: Reset Signal Persistence
- **WHEN** reset signal is asserted
- **THEN** reset SHALL remain asserted
- **UNTIL** system reset occurs

### Requirement: INTCLR Write SHALL Clear Interrupt and Reload Counter
Writing any value to INTCLR SHALL clear the interrupt and reload the counter from LOAD.

#### Scenario: Interrupt Clear
- **WHEN** any value is written to WDOGINTCLR
- **THEN** WDOGRIS[0] SHALL be cleared to 0
- **AND** WDOGMIS[0] SHALL be cleared to 0
- **AND** interrupt output SHALL be deasserted
- **AND** counter SHALL reload from WDOGLOAD
- **AND** timeout event SHALL be rescheduled

### Requirement: All Registers SHALL Be Write-Protected When Locked
All registers except LOCK SHALL be write-protected when locked.

#### Scenario: Write Protection
- **WHEN** device is locked (WDOGLOCK read returns 0x1)
- **THEN** writes to WDOGLOAD SHALL be ignored
- **AND** writes to WDOGCONTROL SHALL be ignored
- **AND** writes to WDOGINTCLR SHALL be ignored

### Requirement: VALUE Register SHALL Always Be Readable
VALUE register SHALL always be readable regardless of lock status.

#### Scenario: Read During Lock
- **WHEN** device is locked
- **AND** WDOGVALUE register is read
- **THEN** device SHALL return current counter value

### Requirement: LOCK Register SHALL Always Be Accessible
LOCK register itself SHALL always be readable and writable.

#### Scenario: LOCK Register Access
- **WHEN** device is locked
- **THEN** WDOGLOCK register SHALL be readable
- **AND** WDOGLOCK register SHALL be writable

### Requirement: LOAD Register SHALL Support Read and Write Operations
The LOAD register SHALL support read and write operations, with reset value 0xFFFFFFFF.

#### Scenario: LOAD Write
- **WHEN** value is written to WDOGLOAD
- **AND** device is unlocked
- **THEN** value SHALL be stored
- **AND** stored value SHALL be returned on subsequent reads

#### Scenario: LOAD Read
- **WHEN** WDOGLOAD register is read
- **THEN** device SHALL return stored reload value

#### Scenario: LOAD Reset Value
- **WHEN** device is reset
- **THEN** WDOGLOAD SHALL contain 0xFFFFFFFF

### Requirement: VALUE Register SHALL Provide Read-Only Access
The VALUE register SHALL support read operations only, returning current counter value.

#### Scenario: VALUE Read
- **WHEN** WDOGVALUE register is read
- **THEN** device SHALL return current counter value calculated via lazy evaluation

#### Scenario: VALUE Write Ignored
- **WHEN** write is attempted to WDOGVALUE
- **THEN** write SHALL be ignored (read-only register)

### Requirement: CONTROL Register SHALL Support Configuration
CONTROL register supports read and write operations, with reset value 0x00000000.

#### Scenario: CONTROL Write
- **WHEN** value is written to WDOGCONTROL
- **AND** device is unlocked
- **THEN** INTEN, RESEN, and step_value fields SHALL be updated
- **AND** timer behavior SHALL reflect new configuration

#### Scenario: CONTROL Read
- **WHEN** WDOGCONTROL register is read
- **THEN** device SHALL return current configuration

#### Scenario: CONTROL Reset Value
- **WHEN** device is reset
- **THEN** WDOGCONTROL SHALL contain 0x00000000

### Requirement: INTCLR Register SHALL Support Write-Only Clearing
INTCLR register supports write operations only, any write clears interrupt and reloads counter.

#### Scenario: INTCLR Write Effect
- **WHEN** any value is written to WDOGINTCLR
- **THEN** interrupt SHALL be cleared
- **AND** counter SHALL be reloaded

#### Scenario: INTCLR Read Behavior
- **WHEN** WDOGINTCLR is read
- **THEN** device SHALL return undefined or zero value (write-only register)

### Requirement: RIS Register SHALL Show Raw Interrupt Status
RIS register supports read operations, showing raw interrupt status.

#### Scenario: RIS Read
- **WHEN** WDOGRIS register is read
- **THEN** bit 0 SHALL be 1 if interrupt condition occurred
- **AND** bit 0 SHALL be 0 if no interrupt pending

### Requirement: MIS Register SHALL Show Masked Interrupt Status
MIS register supports read operations, showing masked interrupt status.

#### Scenario: MIS Read
- **WHEN** WDOGMIS register is read
- **THEN** bit 0 SHALL be (WDOGRIS[0] AND INTEN)
- **AND** reflects whether interrupt output is asserted

### Requirement: LOCK Register SHALL Support Locking Mechanism
LOCK register supports read and write operations with special locking behavior.

#### Scenario: LOCK Read Unlocked
- **WHEN** WDOGLOCK is read and device is unlocked
- **THEN** register SHALL return 0x00000000

#### Scenario: LOCK Read Locked
- **WHEN** WDOGLOCK is read and device is locked
- **THEN** register SHALL return 0x00000001

### Requirement: Writing Unlock Code SHALL Unlock Register Access
Writing unlock code to LOCK register SHALL unlock write access to protected registers.

#### Scenario: Unlock Operation
- **WHEN** 0x1ACCE551 is written to WDOGLOCK
- **THEN** device SHALL be unlocked
- **AND** subsequent WDOGLOCK reads SHALL return 0x00000000
- **AND** writes to other registers SHALL be accepted

### Requirement: Writing Other Value SHALL Lock Register Access
Writing any value other than unlock code to LOCK register SHALL lock write access.

#### Scenario: Lock Operation
- **WHEN** any value other than 0x1ACCE551 is written to WDOGLOCK
- **THEN** device SHALL be locked
- **AND** subsequent WDOGLOCK reads SHALL return 0x00000001
- **AND** writes to other registers (except LOCK) SHALL be blocked

### Requirement: Timer SHALL Not Decrement When INTEN=0
When INTEN=0, the timer shall decrement and reload at zero without generating interrupts.

#### Scenario: Disabled Timer Behavior
- **WHEN** INTEN=0
- **THEN** timer SHALL be in idle state
- **AND** counter value SHALL NOT change
- **AND** no timeout events SHALL be scheduled

### Requirement: Raw Interrupt Status SHALL Be Set at Zero
When INTEN=1 and the timer reaches zero, the raw interrupt status shall be set to 1.

#### Scenario: RIS Update on Timeout
- **WHEN** timer reaches zero and INTEN=1
- **THEN** WDOGRIS[0] SHALL become 1
- **AND** SHALL remain 1 until WDOGINTCLR is written

### Requirement: Reset Requires Second Consecutive Timeout
When RESEN=1, INTEN=1, and the timer reaches zero for the second consecutive time without interrupt clear, the reset signal shall be asserted.

#### Scenario: Second Timeout Triggers Reset
- **WHEN** timer reaches zero first time
- **AND** interrupt is asserted (WDOGRIS[0]=1)
- **AND** INTCLR is NOT written
- **AND** timer reaches zero second time
- **AND** RESEN=1
- **THEN** reset signal SHALL be asserted

### Requirement: Interrupt Output SHALL Follow MIS Register
The interrupt output signal shall be asserted when MIS[0] is 1.

#### Scenario: Interrupt Signal Assertion
- **WHEN** WDOGMIS[0] is 1
- **THEN** interrupt output signal SHALL be asserted (high)

#### Scenario: Interrupt Signal Deassertion
- **WHEN** WDOGMIS[0] is 0
- **THEN** interrupt output signal SHALL be deasserted (low)

### Requirement: Interrupt SHALL Be Deasserted When INTCLR Written
The interrupt signal shall be deasserted when INTCLR is written, regardless of counter state.

#### Scenario: INTCLR Immediate Effect
- **WHEN** WDOGINTCLR is written
- **THEN** interrupt output SHALL be deasserted immediately
- **AND** WDOGRIS[0] and WDOGMIS[0] SHALL be cleared
- **REGARDLESS** of current counter value

### Requirement: Counter SHALL Wrap from Zero to Max
The counter shall wrap from 0x00000000 to 0xFFFFFFFF when decremented.

#### Scenario: Counter Wrap Behavior
- **WHEN** counter value is 0x00000000
- **AND** counter continues to decrement
- **THEN** next value SHALL be 0xFFFFFFFF

## ADDED Test Requirements

### Requirement: Test SHALL Verify Basic Timer Countdown
Verify basic timer countdown functionality.

#### Scenario: Timer Countdown Validation
- **GIVEN** WDOGLOAD is set to known value (e.g., 1000)
- **WHEN** INTEN is set to 1 to start timer
- **THEN** WDOGVALUE SHALL decrement over time
- **AND** decrement rate SHALL match clock divider setting

### Requirement: Test SHALL Verify Timer Reload
Verify timer reload functionality.

#### Scenario: Automatic Reload Validation
- **GIVEN** WDOGLOAD is set to known value
- **WHEN** timer counts down to zero
- **THEN** WDOGVALUE SHALL reload to WDOGLOAD value
- **AND** timer SHALL continue counting

### Requirement: Test SHALL Verify Interrupt and Reset Sequence
Verify interrupt and reset generation sequence.

#### Scenario: Full Watchdog Sequence
- **GIVEN** INTEN=1 and RESEN=1
- **WHEN** timer reaches zero first time
- **THEN** interrupt SHALL be asserted
- **WHEN** timer reaches zero second time without clearing
- **THEN** reset signal SHALL be asserted

### Requirement: Test SHALL Verify Interrupt Clearing
Verify interrupt clearing functionality.

#### Scenario: Interrupt Clear Operation
- **GIVEN** interrupt is asserted (WDOGRIS[0]=1)
- **WHEN** WDOGINTCLR is written
- **THEN** WDOGRIS[0] SHALL become 0
- **AND** interrupt output SHALL be deasserted
- **AND** counter SHALL reload from WDOGLOAD

### Requirement: Test SHALL Verify Lock Protection
Verify lock protection mechanism.

#### Scenario: Lock Protection Validation
- **WHEN** WDOGLOCK is written with 0x1ACCE551
- **THEN** registers SHALL be writable
- **WHEN** WDOGLOCK is written with any other value
- **THEN** WDOGLOAD and WDOGCONTROL writes SHALL be blocked
- **AND** WDOGVALUE reads SHALL still work
- **AND** WDOGLOCK itself SHALL remain accessible

### Requirement: Test SHALL Verify Lock Status Read
Verify lock status read functionality.

#### Scenario: Lock Status Reading
- **WHEN** device is unlocked
- **THEN** WDOGLOCK read SHALL return 0x00000000
- **WHEN** device is locked
- **THEN** WDOGLOCK read SHALL return 0x00000001

### Requirement: Test SHALL Verify Clock Divider Settings
Verify different clock divider settings.

#### Scenario: Divider Rate Validation
- **FOR EACH** valid step_value setting (000, 001, 010, 011, 100)
- **WHEN** step_value is configured
- **THEN** timer decrement rate SHALL match expected divider ratio
- **AND** timeout SHALL occur at expected cycle count