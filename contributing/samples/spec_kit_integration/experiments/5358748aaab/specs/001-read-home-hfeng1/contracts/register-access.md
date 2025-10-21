# Register Access Contracts

## WDOGLOAD Register Access Contract

### Read Behavior
- When read, returns the current load value
- Access type: Read-Write
- Size: 32 bits
- Reset value: 0x00000000

### Write Behavior
- When written, updates the load value used when the timer restarts
- Access type: Read-Write
- Size: 32 bits
- Writing has no effect on the current countdown value

## WDOGVALUE Register Access Contract

### Read Behavior
- When read, returns the current countdown value
- Access type: Read-Only
- Size: 32 bits
- Value decreases on each clock tick when the timer is enabled

### Write Behavior
- Writes are ignored
- Access type: Read-Only
- Size: 32 bits

## WDOGCONTROL Register Access Contract

### Read Behavior
- When read, returns the current control register value
- Access type: Read-Write
- Size: 32 bits
- Bit 0 (INTEN): Interrupt enable status
- Bit 1 (RESEN): Reset enable status

### Write Behavior
- When written, updates the control register bits
- Access type: Read-Write
- Size: 32 bits
- Bit 0 (INTEN): Set to 1 to enable interrupt generation
- Bit 1 (RESEN): Set to 1 to enable reset generation

## WDOGINTCLR Register Access Contract

### Read Behavior
- Reads return undefined value
- Access type: Write-Only
- Size: 32 bits

### Write Behavior
- When written, clears the interrupt pending status
- Access type: Write-Only
- Size: 32 bits
- Any write value clears the interrupt

## WDOGRIS Register Access Contract

### Read Behavior
- When read, returns the raw interrupt status
- Access type: Read-Only
- Size: 32 bits
- Bit 0 (RIS): 1 = interrupt pending, 0 = no interrupt pending

### Write Behavior
- Writes are ignored
- Access type: Read-Only
- Size: 32 bits

## WDOGMIS Register Access Contract

### Read Behavior
- When read, returns the masked interrupt status
- Access type: Read-Only
- Size: 32 bits
- Bit 0 (MIS): 1 = interrupt enabled and pending, 0 = interrupt not enabled or not pending

### Write Behavior
- Writes are ignored
- Access type: Read-Only
- Size: 32 bits

## WDOGLOCK Register Access Contract

### Read Behavior
- When read, returns the current lock status
- Access type: Read-Write
- Size: 32 bits
- Value 0x00000000 = unlocked, any other value = locked

### Write Behavior
- When written, updates the lock status
- Access type: Read-Write
- Size: 32 bits
- Write 0x1ACCE551 to unlock registers
- Write any other value to lock registers

## WDOGITCR Register Access Contract

### Read Behavior
- When read, returns the integration test control register value
- Access type: Read-Write
- Size: 32 bits
- Bit 0 (INTEG_TEST_EN): 1 = integration test mode enabled, 0 = normal mode

### Write Behavior
- When written, updates the integration test control register
- Access type: Read-Write
- Size: 32 bits
- Bit 0 (INTEG_TEST_EN): Set to 1 to enable integration test mode

## WDOGITOP Register Access Contract

### Read Behavior
- Reads return undefined value
- Access type: Write-Only
- Size: 32 bits

### Write Behavior
- When written, controls the integration test outputs
- Access type: Write-Only
- Size: 32 bits
- Bit 0: Controls interrupt output in test mode
- Bit 1: Controls reset output in test mode

## Identification Registers Access Contract

### Read Behavior
- All identification registers are read-only
- Return fixed values for device identification
- Access type: Read-Only
- Size: 32 bits each

### Write Behavior
- Writes are ignored for all identification registers
- Access type: Read-Only
- Size: 32 bits each