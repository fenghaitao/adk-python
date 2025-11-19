# Spec Deltas for Watchdog Load Register Implementation

## ADDED Requirements

### Requirement: WDOGLOAD Register Implementation
The watchdog device SHALL implement the WDOGLOAD register at address 0x00 with the following characteristics:
- Size: 32-bit
- Type: Read/Write (RW)
- Reset value: 0xFFFFFFFF
- Description: Watchdog decrement timer reload value

#### Scenario: WDOGLOAD Register Basic Access
When the WDOGLOAD register is accessed,
- Upon read, it SHALL return the current load value used for reloading the watchdog counter
- Upon write, it SHALL update the load value and reload the current counter value
- The register SHALL respect the WDOGLOCK register state and be writable only when unlocked

### Requirement: WDOGLOAD Reset Value
The WDOGLOAD register SHALL reset to 0xFFFFFFFF upon device reset.

#### Scenario: WDOGLOAD Reset Behavior
When the watchdog device is reset,
- The WDOGLOAD register value SHALL be set to 0xFFFFFFFF

### Requirement: WDOGLOAD Field Definition
The WDOGLOAD register SHALL contain a single field:
- wdog_load: bits [31:0] - Watchdog decrement timer reload value
- This field SHALL be writable when the watchdog is unlocked
- This field SHALL update the counter reload value when written

#### Scenario: WDOGLOAD Field Access
When writing to the wdog_load field,
- The entire 32-bit value SHALL be stored as the reload value
- The watchdog counter SHALL be immediately reloaded with this value
- The counter operation SHALL continue with the new reload value

### Requirement: WDOGLOAD Lock Protection
The WDOGLOAD register SHALL respect the watchdog lock mechanism and be write-protected when locked.

#### Scenario: WDOGLOAD Access When Locked
When attempting to write to WDOGLOAD while the watchdog is locked,
- The write operation SHALL be ignored
- The register value SHALL remain unchanged
- A warning message MAY be logged indicating the access violation

## MODIFIED Requirements

## REMOVED Requirements