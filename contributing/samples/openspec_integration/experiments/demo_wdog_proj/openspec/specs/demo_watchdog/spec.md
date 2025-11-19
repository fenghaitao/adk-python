# demo_watchdog Specification

## Purpose
Specification created by archiving change implement-watchdog load

## Requirements

### Requirement: WDOGLOAD_Register_Implementation
The watchdog timer shall implement the WDOGLOAD register at address 0x00 to store the reload value for the decrementing counter. When the WDOGLOAD register is accessed: - On read, it shall return the current 32-bit reload value - On write, it shall update the 32-bit reload value - After reset, it shall have a default value of 0xFFFFFFFF - All 32 bits (31:0) shall be read/write accessible

#### Scenario: WDOGLOAD_Register_Read_Write

### Requirement: WDOGLOAD_Register_Reset_Value
The WDOGLOAD register shall reset to 0xFFFFFFFF. When the watchdog timer device is reset: - The WDOGLOAD register value shall be set to 0xFFFFFFFF - Subsequent reads of the register shall return 0xFFFFFFFF until modified

#### Scenario: WDOGLOAD_Register_Reset

### Requirement: WDOGLOAD_Register_Behavior
The WDOGLOAD register value shall be used to reload the watchdog counter when the counter reaches zero and interrupt is enabled, or when the interrupt clear register is written. When the watchdog counter reaches zero: - If the control register INTEN bit is set, the counter shall be reloaded from the WDOGLOAD register value - When WDOGINTCLR register is written, the counter shall be reloaded from the WDOGLOAD register value

#### Scenario: WDOGLOAD_Register_Usage

### Requirement: WDOGLOAD_Register_Access
The WDOGLOAD register shall be accessible as a 32-bit read/write register. When accessing individual bits of the WDOGLOAD register: - Bits 31:0 shall represent the wdog_load field - All bits shall be read-write accessible - Writing to the register shall update the reload value used by the counter

#### Scenario: WDOGLOAD_Register_Access_Bits
