# Watchdog Timer Device Implementation Specification

## ADDED Requirements

### Requirement: 32-bit Decrementing Counter
The watchdog timer SHALL implement a 32-bit decrementing counter that decrements from the value loaded from WDOGLOAD register.

#### Scenario: Counter initialization
- **WHEN** device is reset
- **THEN** counter value SHALL be 0xFFFFFFFF (WDOGVALUE reads 0xFFFFFFFF)

#### Scenario: Counter decrement on enable
- **WHEN** INTEN=1 and clock is running
- **THEN** counter value SHALL decrement from WDOGLOAD value at rate determined by step_value

### Requirement: Clock Divider Configuration
The timer SHALL decrement at a rate determined by the clock divider setting (step_value) in WDOGCONTROL register bits [4:2], with valid settings: ÷1 (000), ÷2 (001), ÷4 (010), ÷8 (011), ÷16 (100).

#### Scenario: Clock divider ÷1 setting
- **WHEN** step_value=000 in WDOGCONTROL[4:2]
- **THEN** counter SHALL decrement by 1 on each wclk rising edge when wclk_en=1

#### Scenario: Clock divider ÷4 setting
- **WHEN** step_value=010 in WDOGCONTROL[4:2]
- **THEN** counter SHALL decrement by 4 on each wclk rising edge when wclk_en=1

#### Scenario: Clock divider ÷16 setting
- **WHEN** step_value=100 in WDOGCONTROL[4:2]
- **THEN** counter SHALL decrement by 16 on each wclk rising edge when wclk_en=1

### Requirement: Clock-Gated Counter Decrement
The timer SHALL decrement only on rising edges of wclk when wclk_en signal is asserted (high).

#### Scenario: Clock enable signal active
- **WHEN** wclk_en=1 and wclk rising edge occurs
- **THEN** counter SHALL decrement by step_value

#### Scenario: Clock enable signal inactive
- **WHEN** wclk_en=0
- **THEN** counter SHALL NOT decrement regardless of wclk edges

### Requirement: Non-Destructive Counter Read
The timer counter value SHALL be readable at any time via the WDOGVALUE register without affecting counter operation.

#### Scenario: Counter value read while running
- **WHEN** WDOGVALUE register is read
- **THEN** current counter value SHALL be returned without affecting counter state or timing

### Requirement: First Timeout Interrupt Generation
When the counter reaches zero and INTEN=1, the device SHALL set WDOGRIS[0] to 1 and assert the wdogint output signal.

#### Scenario: Counter reaches zero with interrupts enabled
- **WHEN** counter reaches 0 AND INTEN=1
- **THEN** WDOGRIS[0] SHALL be set to 1 AND wdogint output SHALL be asserted

### Requirement: Interrupt Signal Persistence
The wdogint signal SHALL remain asserted until cleared by writing any value to WDOGINTCLR register.

#### Scenario: Interrupt remains active until serviced
- **WHEN** wdogint is asserted
- **THEN** signal SHALL remain high until any value is written to WDOGINTCLR

### Requirement: Second Timeout Reset Generation
If the counter reaches zero again while the interrupt is still asserted (WDOGRIS[0]=1) and RESEN=1, the device SHALL assert the wdogres output signal.

#### Scenario: Second timeout with reset enabled
- **WHEN** counter reaches 0 again AND WDOGRIS[0]=1 AND RESEN=1
- **THEN** wdogres output signal SHALL be asserted

#### Scenario: Second timeout with reset disabled
- **WHEN** counter reaches 0 again AND WDOGRIS[0]=1 AND RESEN=0
- **THEN** wdogres output signal SHALL NOT be asserted

### Requirement: Reset Signal Persistence
The wdogres signal SHALL remain asserted until system reset (wrst_n assertion).

#### Scenario: Reset signal cleared on system reset
- **WHEN** wrst_n is asserted (active-low reset)
- **THEN** wdogres output SHALL be de-asserted

### Requirement: Interrupt Suppression When Disabled
When INTEN=0, the timer SHALL not generate interrupts even if the counter reaches zero.

#### Scenario: Counter reaches zero with interrupts disabled
- **WHEN** counter reaches 0 AND INTEN=0
- **THEN** WDOGRIS[0] SHALL remain 0 AND wdogint SHALL remain de-asserted

### Requirement: Reset Generation Gating
When RESEN=0, the device SHALL not assert wdogres even if the counter reaches zero while interrupt is pending.

#### Scenario: Second timeout with RESEN disabled
- **WHEN** counter reaches 0 second time AND WDOGRIS[0]=1 AND RESEN=0
- **THEN** wdogres SHALL NOT be asserted

### Requirement: Lock Protection Mechanism
All registers except WDOGLOCK SHALL be write-protected when the device is locked (WDOGLOCK register does not contain the unlock value 0x1ACCE551).

#### Scenario: Protected register writes when locked
- **WHEN** device is locked (WDOGLOCK != 0x1ACCE551) AND write to WDOGLOAD/WDOGCONTROL/WDOGINTCLR/WDOGITCR/WDOGITOP attempted
- **THEN** write SHALL be silently ignored

#### Scenario: Read operations when locked
- **WHEN** device is locked
- **THEN** read operations from all registers SHALL succeed

### Requirement: Device Unlock
Writing 0x1ACCE551 to WDOGLOCK SHALL unlock the device and enable write access to protected registers.

#### Scenario: Unlock with magic value
- **WHEN** 0x1ACCE551 is written to WDOGLOCK
- **THEN** device SHALL be unlocked AND writes to protected registers SHALL succeed

### Requirement: Device Lock
Writing any value other than 0x1ACCE551 to WDOGLOCK SHALL lock the device and disable write access to protected registers.

#### Scenario: Lock with non-magic value
- **WHEN** any value other than 0x1ACCE551 is written to WDOGLOCK
- **THEN** device SHALL be locked AND writes to protected registers SHALL be ignored

### Requirement: Lock Status Read-Back
Reading WDOGLOCK SHALL return 0x00000000 when unlocked or 0x00000001 when locked.

#### Scenario: Read lock status when unlocked
- **WHEN** WDOGLOCK is read AND device is unlocked
- **THEN** value 0x00000000 SHALL be returned

#### Scenario: Read lock status when locked
- **WHEN** WDOGLOCK is read AND device is locked
- **THEN** value 0x00000001 SHALL be returned

### Requirement: Unlocked Reset State
The device SHALL initialize in the unlocked state after reset (WDOGLOCK = 0x00000000).

#### Scenario: Device state after reset
- **WHEN** device is reset (wrst_n or prst_n asserted)
- **THEN** device SHALL be unlocked AND WDOGLOCK SHALL read 0x00000000

### Requirement: Interrupt Clear and Counter Reload
Writing any value to WDOGINTCLR SHALL reload the counter from WDOGLOAD and clear the interrupt status.

#### Scenario: Interrupt clear operation
- **WHEN** any value is written to WDOGINTCLR
- **THEN** (1) WDOGRIS[0] SHALL be cleared to 0, (2) wdogint SHALL be de-asserted, (3) counter SHALL reload from WDOGLOAD, (4) counter SHALL resume counting

### Requirement: Counter Reload on Enable Transition
When INTEN transitions from 0 to 1 in WDOGCONTROL register, the counter SHALL reload from WDOGLOAD.

#### Scenario: Enable timer from disabled state
- **WHEN** INTEN transitions from 0 to 1 in WDOGCONTROL write
- **THEN** counter SHALL reload from current WDOGLOAD value AND start counting

### Requirement: Automatic Counter Reload on Timeout
When the counter reaches zero with INTEN=1, the counter SHALL automatically reload from WDOGLOAD after generating the interrupt.

#### Scenario: First timeout auto-reload
- **WHEN** counter reaches 0 AND INTEN=1
- **THEN** interrupt SHALL be generated AND counter SHALL automatically reload from WDOGLOAD AND continue counting

### Requirement: Deferred Reload Value Update
Changes to WDOGLOAD register SHALL not immediately affect the current counter value; new load value takes effect on next reload event.

#### Scenario: Update reload value while counter running
- **WHEN** WDOGLOAD is written while counter is running
- **THEN** current counter SHALL continue with existing value AND new value SHALL apply on next reload event

### Requirement: Integration Test Mode Entry
When WDOGITCR[0]=1, the device SHALL enter integration test mode and suspend normal counter operation.

#### Scenario: Enter integration test mode
- **WHEN** 1 is written to WDOGITCR[0]
- **THEN** device SHALL enter integration test mode AND counter operation SHALL be suspended

### Requirement: Integration Test Interrupt Control
In integration test mode, writing to WDOGITOP[1] SHALL directly control the wdogint output signal.

#### Scenario: Direct interrupt control in test mode
- **WHEN** WDOGITCR[0]=1 AND WDOGITOP[1] is written
- **THEN** wdogint output SHALL directly reflect WDOGITOP[1] value

### Requirement: Integration Test Reset Control
In integration test mode, writing to WDOGITOP[0] SHALL directly control the wdogres output signal.

#### Scenario: Direct reset control in test mode
- **WHEN** WDOGITCR[0]=1 AND WDOGITOP[0] is written
- **THEN** wdogres output SHALL directly reflect WDOGITOP[0] value

### Requirement: Normal Mode Operation
When WDOGITCR[0]=0, the device SHALL operate in normal mode and WDOGITOP register SHALL have no effect on outputs.

#### Scenario: Test mode disabled
- **WHEN** WDOGITCR[0]=0
- **THEN** device SHALL operate in normal counter mode AND WDOGITOP writes SHALL have no effect on outputs

### Requirement: Integration Test Mode Lock Protection
Integration test mode control registers (WDOGITCR, WDOGITOP) SHALL be write-protected when device is locked.

#### Scenario: Test mode access when locked
- **WHEN** device is locked AND writes to WDOGITCR or WDOGITOP attempted
- **THEN** writes SHALL be silently ignored

### Requirement: PrimeCell Peripheral Identification Registers
The device SHALL implement PrimeCell peripheral identification registers (WDOGPERIPHID0-7) with fixed read-only values.

#### Scenario: Read peripheral ID registers
- **WHEN** WDOGPERIPHID0-7 registers are read
- **THEN** fixed identification values SHALL be returned per ARM PrimeCell specification

### Requirement: PrimeCell Component Identification Registers
The device SHALL implement PrimeCell component identification registers (WDOGPCELLID0-3) with fixed read-only values.

#### Scenario: Read component ID registers
- **WHEN** WDOGPCELLID0-3 registers are read
- **THEN** fixed values 0x0D, 0xF0, 0x05, 0xB1 SHALL be returned for registers 0-3 respectively

### Requirement: Peripheral ID Encoding
Peripheral ID registers SHALL encode: part number=0x024, JEP106 ID code, revision number, and other identification fields per ARM PrimeCell specification.

#### Scenario: Verify peripheral identification encoding
- **WHEN** peripheral ID registers are read
- **THEN** part number 0x024 SHALL be encoded in appropriate register bits

### Requirement: Component ID Fixed Values
Component ID registers SHALL return the fixed values: 0x0D, 0xF0, 0x05, 0xB1 for registers 0-3 respectively.

#### Scenario: Read all component ID registers
- **WHEN** WDOGPCELLID0-3 are read
- **THEN** values SHALL be 0x0D (ID0), 0xF0 (ID1), 0x05 (ID2), 0xB1 (ID3)

### Requirement: Working Clock Domain Reset
Assertion of wrst_n (active-low) SHALL asynchronously reset the wclk clock domain logic including counter state and interrupt status.

#### Scenario: Working clock domain reset
- **WHEN** wrst_n is asserted (active-low)
- **THEN** counter state, WDOGRIS, and interrupt logic SHALL be reset

### Requirement: APB Clock Domain Reset
Assertion of prst_n (active-low) SHALL asynchronously reset the APB bus interface logic.

#### Scenario: APB clock domain reset
- **WHEN** prst_n is asserted (active-low)
- **THEN** APB bus interface logic SHALL be reset

### Requirement: Register Reset Values
After reset, all registers SHALL return to their documented reset values.

#### Scenario: All registers at reset values
- **WHEN** device is reset
- **THEN** WDOGLOAD=0xFFFFFFFF, WDOGVALUE=0xFFFFFFFF, WDOGCONTROL=0x00000000, WDOGRIS=0x0, WDOGMIS=0x0, WDOGLOCK=0x00000000, WDOGITCR=0x0

### Requirement: Reset Signal Cleared on System Reset
The wdogres output signal SHALL be cleared to 0 upon system reset.

#### Scenario: Reset output cleared
- **WHEN** system reset occurs (wrst_n assertion)
- **THEN** wdogres output SHALL be cleared to 0

### Requirement: WDOGLOAD Register Access
WDOGLOAD register SHALL support read and write operations with 32-bit width and reset value 0xFFFFFFFF.

#### Scenario: Read and write WDOGLOAD
- **WHEN** WDOGLOAD is written with value V
- **THEN** subsequent reads SHALL return V (if device unlocked)

#### Scenario: WDOGLOAD reset value
- **WHEN** device is reset
- **THEN** WDOGLOAD SHALL read 0xFFFFFFFF

### Requirement: WDOGVALUE Read-Only Register
WDOGVALUE register SHALL support read operations only; write operations SHALL be ignored.

#### Scenario: WDOGVALUE write ignored
- **WHEN** write to WDOGVALUE attempted
- **THEN** write SHALL be ignored AND counter value SHALL remain unchanged

### Requirement: WDOGCONTROL Register Access
WDOGCONTROL register SHALL support read and write operations with bits [31:5] reserved (read as 0).

#### Scenario: Read WDOGCONTROL reserved bits
- **WHEN** WDOGCONTROL is read
- **THEN** bits [31:5] SHALL read as 0

#### Scenario: Write WDOGCONTROL
- **WHEN** WDOGCONTROL is written
- **THEN** bits [4:0] SHALL be updated (if device unlocked)

### Requirement: WDOGINTCLR Write-Only Register
WDOGINTCLR register SHALL be write-only; any write value SHALL trigger interrupt clear and counter reload.

#### Scenario: Write any value to WDOGINTCLR
- **WHEN** any value (including 0x00000000) is written to WDOGINTCLR
- **THEN** interrupt SHALL be cleared AND counter SHALL reload

### Requirement: WDOGRIS Read-Only Status Register
WDOGRIS register SHALL be read-only with only bit [0] valid; write operations SHALL be ignored.

#### Scenario: WDOGRIS write ignored
- **WHEN** write to WDOGRIS attempted
- **THEN** write SHALL be ignored AND interrupt status SHALL remain unchanged

#### Scenario: WDOGRIS bit[0] validity
- **WHEN** WDOGRIS is read
- **THEN** only bit [0] SHALL be valid; bits [31:1] are reserved

### Requirement: WDOGMIS Masked Interrupt Status
WDOGMIS register SHALL be read-only and SHALL always reflect (WDOGRIS[0] AND WDOGCONTROL[INTEN]).

#### Scenario: WDOGMIS calculation
- **WHEN** WDOGMIS is read
- **THEN** bit[0] SHALL equal (WDOGRIS[0] AND WDOGCONTROL[INTEN])

### Requirement: WDOGLOCK Always Writable
WDOGLOCK register SHALL support read and write operations and SHALL not be affected by lock state.

#### Scenario: WDOGLOCK writable when locked
- **WHEN** device is locked
- **THEN** WDOGLOCK itself SHALL still be writable

### Requirement: WDOGITCR Register Access and Protection
WDOGITCR register SHALL support read and write operations with only bit [0] valid; write-protected when locked.

#### Scenario: WDOGITCR locked write protection
- **WHEN** device is locked AND write to WDOGITCR attempted
- **THEN** write SHALL be ignored

#### Scenario: WDOGITCR bit validity
- **WHEN** WDOGITCR is read
- **THEN** only bit [0] SHALL be valid; bits [31:1] are reserved

### Requirement: WDOGITOP Write-Only Test Output Register
WDOGITOP register SHALL be write-only with only bits [1:0] valid; read operations return undefined value.

#### Scenario: WDOGITOP bit validity
- **WHEN** WDOGITOP is written
- **THEN** only bits [1:0] SHALL affect output signals; bits [31:2] are ignored

### Requirement: Peripheral Identification Registers Read-Only
All peripheral identification registers (WDOGPERIPHID0-7) SHALL be read-only with fixed values.

#### Scenario: Peripheral ID write ignored
- **WHEN** write to any WDOGPERIPHID register attempted
- **THEN** write SHALL be ignored AND register value SHALL remain unchanged

### Requirement: PrimeCell Identification Registers Read-Only
All PrimeCell identification registers (WDOGPCELLID0-3) SHALL be read-only with fixed values.

#### Scenario: PrimeCell ID write ignored
- **WHEN** write to any WDOGPCELLID register attempted
- **THEN** write SHALL be ignored AND register value SHALL remain unchanged

### Requirement: Silent Lock Write Rejection
Writes to locked registers SHALL be silently ignored (no bus error response).

#### Scenario: Locked register write behavior
- **WHEN** device is locked AND write to protected register attempted
- **THEN** write SHALL be ignored silently without generating bus error

### Requirement: Counter Preservation When Disabled
When INTEN=0, the timer SHALL not decrement and SHALL preserve its current counter value.

#### Scenario: Disabled counter preservation
- **WHEN** INTEN=0 AND time advances
- **THEN** counter value SHALL remain unchanged (frozen at current value)

### Requirement: Same-Cycle Interrupt Status Update
When INTEN=1 and the timer reaches zero, WDOGRIS[0] SHALL be set to 1 on the same clock cycle.

#### Scenario: Synchronous interrupt status
- **WHEN** counter reaches 0 on clock cycle N
- **THEN** WDOGRIS[0] SHALL be set to 1 on same clock cycle N

### Requirement: Step-Value Counter Decrement
The counter SHALL decrement by step_value on each wclk rising edge when wclk_en=1 and INTEN=1.

#### Scenario: Decrement by step_value
- **WHEN** wclk rising edge occurs AND wclk_en=1 AND INTEN=1
- **THEN** counter SHALL decrement by step_value (not by 1)

### Requirement: Running Counter Reload Deferral
Writing to WDOGLOAD while counter is running SHALL not immediately affect counter; new value applies on next reload.

#### Scenario: Deferred reload value application
- **WHEN** WDOGLOAD is updated while counter is decrementing
- **THEN** current countdown SHALL continue with old value AND new value SHALL apply on next reload event

### Requirement: Irregular Clock Enable Timing Accuracy
The device SHALL maintain accurate countdown timing based on wclk_en signal even with irregular clock enable patterns.

#### Scenario: Irregular clock enable pattern
- **WHEN** wclk_en has irregular on/off pattern
- **THEN** counter SHALL decrement accurately counting only cycles where wclk_en=1

### Requirement: Lock State Persistence
Lock state SHALL persist across register accesses until explicitly unlocked via WDOGLOCK register.

#### Scenario: Lock persistence
- **WHEN** device is locked AND multiple register operations performed
- **THEN** lock state SHALL persist until 0x1ACCE551 written to WDOGLOCK

### Requirement: Integration Test Mode Bypass
Integration test mode SHALL completely bypass normal counter operation and interrupt generation logic.

#### Scenario: Test mode counter bypass
- **WHEN** WDOGITCR[0]=1
- **THEN** counter SHALL be frozen AND normal timeout/interrupt logic SHALL be bypassed

### Requirement: Simultaneous Signal Assertion
Simultaneous assertion of both wdogint and wdogres signals SHALL be possible (during second timeout with RESEN=1).

#### Scenario: Both signals asserted
- **WHEN** second timeout occurs with RESEN=1
- **THEN** both wdogint=1 AND wdogres=1 SHALL be asserted simultaneously

### Requirement: State Survival Across Lock Changes
Counter state and interrupt status SHALL survive changes to lock state (locking does not clear interrupt).

#### Scenario: Interrupt survives locking
- **WHEN** interrupt is pending (WDOGRIS[0]=1) AND device is locked
- **THEN** WDOGRIS[0] SHALL remain 1 AND counter state SHALL remain unchanged

### Requirement: Basic Timer Countdown and Interrupt Test
The test suite SHALL verify basic timer countdown and interrupt generation functionality.

#### Scenario: Complete basic operation test
- **WHEN** timer configured with small timeout value AND enabled
- **THEN** counter SHALL decrement to zero AND interrupt SHALL be generated

### Requirement: Complete Watchdog Sequence with Reset Test
The test suite SHALL verify complete watchdog sequence with reset generation.

#### Scenario: Full watchdog reset sequence
- **WHEN** first timeout occurs AND interrupt not cleared AND second timeout occurs
- **THEN** wdogres SHALL be asserted

### Requirement: Lock Mechanism Functionality Test
The test suite SHALL verify lock mechanism prevents unauthorized register modification.

#### Scenario: Lock protection verification
- **WHEN** device is locked AND writes to protected registers attempted
- **THEN** writes SHALL be rejected AND lock can be removed with magic value

### Requirement: Clock Divider Timeout Period Test
The test suite SHALL verify different clock divider settings produce correct timeout periods.

#### Scenario: Multiple divider settings
- **WHEN** same WDOGLOAD value used with different step_value settings
- **THEN** timeout periods SHALL be inversely proportional to step_value

### Requirement: Integration Test Mode Direct Control Test
The test suite SHALL verify integration test mode provides direct output control.

#### Scenario: Test mode output control
- **WHEN** integration test mode enabled
- **THEN** WDOGITOP SHALL directly control wdogint and wdogres outputs

### Requirement: Counter Reload Trigger Test
The test suite SHALL verify counter reload on various trigger conditions.

#### Scenario: All reload triggers
- **WHEN** INTEN 0→1 transition, WDOGINTCLR write, or timeout occurs
- **THEN** counter SHALL reload from WDOGLOAD in each case

### Requirement: Precise Decrement Behavior Test
The test suite SHALL verify precise counter decrement behavior with step_value settings.

#### Scenario: Multi-step countdown verification
- **WHEN** counter runs with specific step_value
- **THEN** each clock cycle SHALL decrement by exact step_value amount

### Requirement: Boundary Condition Behavior Test
The test suite SHALL verify correct behavior at counter boundary conditions.

#### Scenario: Counter at boundary values
- **WHEN** counter value is near 0 or at maximum
- **THEN** wraparound and reload SHALL function correctly

### Requirement: Simultaneous Signal Assertion Test
The test suite SHALL verify wdogint and wdogres can be asserted simultaneously.

#### Scenario: Both signals active
- **WHEN** second timeout with RESEN=1
- **THEN** both wdogint AND wdogres SHALL be asserted together

### Requirement: Register Read-Back Verification Test
The test suite SHALL verify all register read-back values match written values (where applicable).

#### Scenario: Register read-back
- **WHEN** values written to writable registers
- **THEN** subsequent reads SHALL return written values (for non-side-effect registers)
