## ADDED Requirements

### Requirement: Lock Register Magic Value Unlock
Writing unlock code 0x1ACCE551 to WDOGLOCK register SHALL unlock write access to protected registers.

#### Scenario: Magic Value Unlock
- **WHEN** 0x1ACCE551 is written to WDOGLOCK register
- **THEN** all protected registers SHALL become writable
- **AND** lock status SHALL be set to unlocked state

#### Scenario: Unlock Confirmation
- **WHEN** WDOGLOCK register is read after unlock
- **THEN** register SHALL return 0x00000000
- **AND** unlocked status SHALL be confirmed

### Requirement: Lock Register Non-Magic Value Lock
Writing any value other than 0x1ACCE551 to WDOGLOCK register SHALL lock write access to protected registers.

#### Scenario: Non-Magic Value Lock
- **WHEN** any value other than 0x1ACCE551 is written to WDOGLOCK
- **THEN** all protected registers SHALL become write-protected
- **AND** lock status SHALL be set to locked state

#### Scenario: Lock Confirmation
- **WHEN** WDOGLOCK register is read after lock
- **THEN** register SHALL return non-zero value
- **AND** locked status SHALL be confirmed

### Requirement: Protected Register Write Control
All registers except WDOGLOCK SHALL be write-protected when device is in locked state.

#### Scenario: Protected Registers When Locked
- **WHEN** device is in locked state
- **AND** write is attempted to WDOGLOAD, WDOGCONTROL, WDOGINTCLR, WDOGITCR, or WDOGITOP
- **THEN** write operation SHALL be ignored
- **AND** register values SHALL remain unchanged

#### Scenario: Protected Registers When Unlocked
- **WHEN** device is in unlocked state
- **AND** write is attempted to protected registers
- **THEN** write operation SHALL succeed
- **AND** register values SHALL be updated normally

### Requirement: WDOGLOCK Always Writable
The WDOGLOCK register itself SHALL always be writable regardless of current lock state.

#### Scenario: WDOGLOCK Write When Locked
- **WHEN** device is in locked state
- **AND** write is attempted to WDOGLOCK register
- **THEN** write operation SHALL succeed
- **AND** lock state SHALL be updated based on written value

#### Scenario: WDOGLOCK Write When Unlocked
- **WHEN** device is in unlocked state
- **AND** write is attempted to WDOGLOCK register
- **THEN** write operation SHALL succeed
- **AND** lock state SHALL be updated based on written value

### Requirement: Read Access Always Allowed
All register read operations SHALL be allowed regardless of lock state.

#### Scenario: Read Access When Locked
- **WHEN** device is in locked state
- **AND** read is attempted from any register
- **THEN** read operation SHALL succeed
- **AND** current register value SHALL be returned

#### Scenario: WDOGVALUE Always Readable
- **WHEN** device is in any lock state
- **AND** WDOGVALUE register is read
- **THEN** current counter value SHALL be returned
- **AND** read operation SHALL not be affected by lock

### Requirement: Lock State Persistence
Lock state SHALL persist across register operations and timer events.

#### Scenario: Lock State During Timer Operation
- **WHEN** device is locked and timer is running
- **THEN** timer operation SHALL continue normally
- **AND** lock state SHALL not affect timer functionality
- **AND** only register write protection SHALL be active

#### Scenario: Lock State During Interrupt Events
- **WHEN** device is locked and interrupt events occur
- **THEN** interrupt generation SHALL work normally
- **AND** lock state SHALL not affect interrupt functionality

### Requirement: Lock Protection Scope
Lock protection SHALL apply to functional registers but not identification registers.

#### Scenario: ID Registers Not Protected
- **WHEN** device is in locked state
- **AND** identification registers are accessed
- **THEN** read operations SHALL succeed normally
- **AND** ID registers SHALL not be affected by lock mechanism

#### Scenario: Functional Registers Protected
- **WHEN** device is in locked state
- **THEN** WDOGLOAD, WDOGCONTROL, WDOGINTCLR, WDOGITCR, WDOGITOP SHALL be write-protected
- **AND** functional behavior SHALL be preserved from unauthorized changes

### Requirement: Lock Status Indication
The WDOGLOCK register SHALL provide clear indication of current lock status.

#### Scenario: Unlocked Status Reading
- **WHEN** device is unlocked
- **AND** WDOGLOCK register is read
- **THEN** register SHALL return 0x00000000
- **AND** unlocked status SHALL be clearly indicated

#### Scenario: Locked Status Reading
- **WHEN** device is locked
- **AND** WDOGLOCK register is read
- **THEN** register SHALL return non-zero value
- **AND** locked status SHALL be clearly indicated

### Requirement: Lock Mechanism Independence
Lock protection SHALL operate independently of other device capabilities.

#### Scenario: Lock Independent of Timer State
- **WHEN** lock state changes
- **THEN** timer operation SHALL not be affected
- **AND** counter values and timing SHALL remain accurate

#### Scenario: Lock Independent of Interrupt State
- **WHEN** lock state changes
- **THEN** interrupt generation and status SHALL not be affected
- **AND** interrupt behavior SHALL remain consistent
