# Register Access Contracts

## WDOGLOAD Register (0x0000)
- **Read Access**: Returns the current load value
- **Write Access**: Updates the load value when the timer is not running or when properly unlocked
- **Constraints**: Only writable when WDOGLOCK is unlocked with 0x1ACCE551

## WDOGVALUE Register (0x0004)
- **Read Access**: Returns the current countdown value
- **Write Access**: Not permitted (read-only register)
- **Behavior**: Value decrements based on clock divider settings when timer is enabled

## WDOGCONTROL Register (0x0008)
- **Read Access**: Returns current control settings
- **Write Access**: Updates control settings
- **Constraints**: Only writable when WDOGLOCK is unlocked with 0x1ACCE551
- **Fields**:
  * ENABLE [0]: 0=disable timer, 1=enable timer
  * RESEN [1]: 0=disable reset, 1=enable reset on second timeout
  * INTEN [2]: 0=disable interrupt, 1=enable interrupt on first timeout
  * DIVSEL [4:3]: Clock divider selection (00=÷1, 01=÷2, 10=÷4, 11=÷8)

## WDOGINTCLR Register (0x000C)
- **Read Access**: Not permitted (write-only register)
- **Write Access**: Clears interrupt status when any value is written
- **Behavior**: Writing any value clears the interrupt status and WDOGRIS register

## WDOGRIS Register (0x0010)
- **Read Access**: Returns raw interrupt status
- **Write Access**: Not permitted (read-only register)
- **Behavior**: 1 indicates interrupt is pending, 0 indicates no interrupt

## WDOGMIS Register (0x0014)
- **Read Access**: Returns masked interrupt status
- **Write Access**: Not permitted (read-only register)
- **Behavior**: 1 indicates masked interrupt is pending (INTEN=1 and interrupt condition met), 0 otherwise

## WDOGLOCK Register (0x0C00)
- **Read Access**: Returns current lock status
- **Write Access**: Updates lock status
- **Behavior**: 
  * Writing 0x1ACCE551 unlocks the registers
  * Writing any other value locks the registers
  * Reset value is 0x00000001 (locked)

## WDOGITCR Register (0x0F00)
- **Read Access**: Returns integration test control status
- **Write Access**: Updates integration test control
- **Constraints**: Only writable when WDOGLOCK is unlocked with 0x1ACCE551
- **Behavior**: Enables integration test mode when set to 1

## WDOGITOP Register (0x0F04)
- **Read Access**: Returns integration test output settings
- **Write Access**: Updates integration test output
- **Constraints**: Only writable when WDOGLOCK is unlocked with 0x1ACCE551 and WDOGITCR=1
- **Behavior**: Controls direct output signals in integration test mode

## Peripheral ID Registers (0x0FE0-0x0FEC, 0x0FD0-0x0FDC)
- **Read Access**: Returns fixed identification values
- **Write Access**: Not permitted (read-only registers)
- **Behavior**: Fixed values for device identification

## PrimeCell ID Registers (0x0FF0-0x0FFC)
- **Read Access**: Returns fixed identification values
- **Write Access**: Not permitted (read-only registers)
- **Behavior**: Fixed values for PrimeCell identification