## ADDED Requirements

### Requirement: Interrupt Generation on Timeout
When the counter reaches zero and INTEN=1 in WDOGCONTROL, device SHALL assert the wdogint interrupt signal.

#### Scenario: Interrupt on First Timeout
- **WHEN** counter reaches zero and INTEN=1
- **THEN** wdogint signal SHALL be asserted
- **AND** raw interrupt status SHALL be set

#### Scenario: No Interrupt When Disabled
- **WHEN** counter reaches zero and INTEN=0
- **THEN** wdogint signal SHALL NOT be asserted
- **AND** raw interrupt status SHALL remain clear

### Requirement: Raw Interrupt Status Register
The WDOGRIS register SHALL support read operations only and reflect raw interrupt status.

#### Scenario: Raw Status Set on Timeout
- **WHEN** counter reaches zero and INTEN=1
- **THEN** WDOGRIS[0] SHALL be set to 1
- **AND** raw interrupt status SHALL be readable

#### Scenario: Raw Status Clear on Interrupt Clear
- **WHEN** WDOGINTCLR register is written
- **THEN** WDOGRIS[0] SHALL be cleared to 0
- **AND** raw interrupt status SHALL be updated

### Requirement: Masked Interrupt Status Register
The WDOGMIS register SHALL support read operations only and show masked interrupt status.

#### Scenario: Masked Status Calculation
- **WHEN** WDOGMIS register is read
- **THEN** MIS[0] SHALL equal (WDOGRIS[0] & WDOGCONTROL[0])
- **AND** masked status SHALL reflect interrupt enable state

#### Scenario: Masked Status When Interrupt Disabled
- **WHEN** INTEN=0 in WDOGCONTROL
- **THEN** WDOGMIS[0] SHALL be 0 regardless of raw status
- **AND** no interrupt SHALL be signaled

### Requirement: Interrupt Clear Register
The WDOGINTCLR register SHALL support write operations only for clearing interrupts.

#### Scenario: Interrupt Clear on Write
- **WHEN** any value is written to WDOGINTCLR
- **THEN** interrupt signal SHALL be cleared
- **AND** WDOGRIS[0] SHALL be set to 0
- **AND** counter SHALL reload from WDOGLOAD

#### Scenario: Counter Reload on Clear
- **WHEN** WDOGINTCLR is written
- **THEN** counter SHALL reload from WDOGLOAD register
- **AND** timer operation SHALL continue if INTEN=1

### Requirement: Interrupt Signal Output
The device SHALL provide wdogint signal output for interrupt signaling.

#### Scenario: Signal Assertion
- **WHEN** WDOGMIS[0] becomes 1
- **THEN** wdogint signal SHALL be asserted
- **AND** signal SHALL remain asserted until cleared

#### Scenario: Signal Deassertion
- **WHEN** WDOGMIS[0] becomes 0
- **THEN** wdogint signal SHALL be deasserted
- **AND** interrupt condition SHALL be resolved

### Requirement: Interrupt Persistence
The interrupt signal SHALL remain asserted until explicitly cleared.

#### Scenario: Interrupt Remains Until Clear
- **WHEN** interrupt is generated and not cleared
- **THEN** wdogint signal SHALL remain asserted
- **AND** WDOGRIS[0] SHALL remain 1
- **AND** WDOGMIS[0] SHALL remain 1 if INTEN=1

#### Scenario: Interrupt Clear Resets State
- **WHEN** WDOGINTCLR is written
- **THEN** all interrupt status SHALL be cleared
- **AND** wdogint signal SHALL be deasserted

### Requirement: Interrupt Enable Control
The INTEN bit SHALL control interrupt generation and masking.

#### Scenario: Interrupt Enable Effect
- **WHEN** INTEN=1 and raw interrupt status is set
- **THEN** wdogint signal SHALL be asserted
- **AND** WDOGMIS[0] SHALL be 1

#### Scenario: Interrupt Disable Effect
- **WHEN** INTEN=0
- **THEN** wdogint signal SHALL be deasserted
- **AND** WDOGMIS[0] SHALL be 0 regardless of raw status

### Requirement: Interrupt Status Coordination
Interrupt status registers SHALL coordinate with timer core capability events.

#### Scenario: Timer Event Triggers Status Update
- **WHEN** timer core capability signals timeout event
- **THEN** interrupt status SHALL be updated appropriately
- **AND** interrupt signal SHALL be driven based on enable state

#### Scenario: Status Clear Coordinates with Timer
- **WHEN** interrupt is cleared via WDOGINTCLR
- **THEN** timer core capability SHALL be notified for counter reload
- **AND** timer operation SHALL continue seamlessly
