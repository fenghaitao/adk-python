## ADDED Requirements

### Requirement: 32-bit Decrementing Counter
The watchdog timer SHALL be a 32-bit decrementing counter that starts counting from the value in WDOGLOAD register.

#### Scenario: Counter Initialization
- **WHEN** WDOGLOAD register is written with value 0x1000
- **THEN** counter SHALL be initialized to 0x1000
- **AND** counter SHALL be ready for countdown operation

#### Scenario: Counter Decrement Operation
- **WHEN** timer is enabled and running
- **THEN** counter value SHALL decrement based on clock divider setting
- **AND** current value SHALL be readable via WDOGVALUE register

### Requirement: Clock Divider Configuration
The timer SHALL decrement at a rate determined by the clock divider specified in WDOGCONTROL[4:2] step_value field.

#### Scenario: Clock Divider ÷1 Setting
- **WHEN** step_value field is set to 0b000
- **THEN** timer SHALL decrement at full clock rate (÷1)

#### Scenario: Clock Divider ÷2 Setting
- **WHEN** step_value field is set to 0b001
- **THEN** timer SHALL decrement at half clock rate (÷2)

#### Scenario: Clock Divider ÷4 Setting
- **WHEN** step_value field is set to 0b010
- **THEN** timer SHALL decrement at quarter clock rate (÷4)

#### Scenario: Clock Divider ÷8 Setting
- **WHEN** step_value field is set to 0b011
- **THEN** timer SHALL decrement at eighth clock rate (÷8)

#### Scenario: Clock Divider ÷16 Setting
- **WHEN** step_value field is set to 0b100
- **THEN** timer SHALL decrement at sixteenth clock rate (÷16)

### Requirement: Timer Enable Control
The timer SHALL be controlled by the INTEN bit in WDOGCONTROL register.

#### Scenario: Timer Enable Transition
- **WHEN** INTEN bit transitions from 0 to 1
- **THEN** timer SHALL reload counter from WDOGLOAD register
- **AND** timer SHALL begin decrementing operation

#### Scenario: Timer Disable Transition
- **WHEN** INTEN bit transitions from 1 to 0
- **THEN** timer SHALL stop decrementing
- **AND** counter value SHALL be preserved

### Requirement: Counter Reload Functionality
The timer SHALL reload with the value in WDOGLOAD when specific conditions are met.

#### Scenario: Reload on Enable
- **WHEN** INTEN transitions from 0 to 1
- **THEN** counter SHALL reload from WDOGLOAD register
- **AND** countdown SHALL begin from new value

#### Scenario: Reload on Zero Reach
- **WHEN** counter reaches zero during normal operation
- **THEN** counter SHALL reload from WDOGLOAD register
- **AND** countdown SHALL continue from reload value

### Requirement: WDOGLOAD Register Access
The WDOGLOAD register SHALL support read and write operations with reset value 0xFFFFFFFF.

#### Scenario: WDOGLOAD Write Operation
- **WHEN** value is written to WDOGLOAD register
- **THEN** value SHALL be stored in the register
- **AND** value SHALL be available for counter reload operations

#### Scenario: WDOGLOAD Read Operation
- **WHEN** WDOGLOAD register is read
- **THEN** current stored reload value SHALL be returned

### Requirement: WDOGVALUE Register Access
The WDOGVALUE register SHALL support read operations only, returning current counter value.

#### Scenario: WDOGVALUE Read When Enabled
- **WHEN** WDOGVALUE register is read and timer is enabled
- **THEN** current calculated counter value SHALL be returned
- **AND** value SHALL reflect elapsed time since last reload

#### Scenario: WDOGVALUE Read When Disabled
- **WHEN** WDOGVALUE register is read and timer is disabled
- **THEN** last saved counter value SHALL be returned

### Requirement: WDOGCONTROL Register Fields
The WDOGCONTROL register SHALL implement INTEN, RESEN, and step_value fields with reset value 0x00.

#### Scenario: INTEN Field Access
- **WHEN** INTEN bit [0] is written
- **THEN** timer enable state SHALL be updated
- **AND** appropriate timer actions SHALL be triggered

#### Scenario: RESEN Field Access
- **WHEN** RESEN bit [1] is written
- **THEN** reset enable setting SHALL be stored
- **AND** setting SHALL be available to reset control capability

#### Scenario: step_value Field Access
- **WHEN** step_value bits [4:2] are written with valid value (0-4)
- **THEN** clock divider setting SHALL be updated
- **AND** timer decrement rate SHALL be adjusted accordingly

### Requirement: Lazy Counter Evaluation
The timer SHALL use lazy evaluation to calculate current counter value without cycle-by-cycle updates.

#### Scenario: Efficient Counter Calculation
- **WHEN** WDOGVALUE register is read
- **THEN** current value SHALL be calculated based on elapsed time
- **AND** calculation SHALL use saved start time and start value
- **AND** no cycle-by-cycle counter updates SHALL occur

### Requirement: Event-Based Timeout Handling
The timer SHALL use event mechanism to handle counter expiry and timeout actions.

#### Scenario: Timeout Event Scheduling
- **WHEN** timer is enabled with valid counter value
- **THEN** timeout event SHALL be scheduled for counter expiry time
- **AND** event SHALL account for clock divider setting

#### Scenario: Timeout Event Cancellation
- **WHEN** timer is disabled or reconfigured
- **THEN** any pending timeout events SHALL be cancelled
- **AND** new events SHALL be scheduled as appropriate
