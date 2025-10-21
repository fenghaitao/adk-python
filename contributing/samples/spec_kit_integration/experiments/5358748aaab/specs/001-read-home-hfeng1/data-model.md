# Data Model: Simics Watchdog Timer Model

## Registers

### Register: WDOGLOAD
- **Offset**: 0x0000
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000000
- **Purpose**: Stores the reload value for the timer
- **Fields**: 
  * [31:0] LOAD_VALUE - The value from which the timer counts down

### Register: WDOGVALUE
- **Offset**: 0x0004
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Contains the current countdown value
- **Fields**: 
  * [31:0] CURRENT_VALUE - The current value of the countdown timer

### Register: WDOGCONTROL
- **Offset**: 0x0008
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000000
- **Purpose**: Controls timer operation including interrupt and reset enable bits
- **Fields**: 
  * [0] INTEN - Interrupt enable bit
  * [1] RESEN - Reset enable bit

### Register: WDOGINTCLR
- **Offset**: 0x000C
- **Size**: 32 bits
- **Access**: WO
- **Reset Value**: Undefined
- **Purpose**: Clears the interrupt when written
- **Fields**: 
  * [31:0] INTCLR - Writing any value clears the interrupt

### Register: WDOGRIS
- **Offset**: 0x0010
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Shows raw interrupt status
- **Fields**: 
  * [0] RIS - Raw interrupt status (1 = interrupt pending)

### Register: WDOGMIS
- **Offset**: 0x0014
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Shows masked interrupt status
- **Fields**: 
  * [0] MIS - Masked interrupt status (1 = interrupt enabled and pending)

### Register: WDOGLOCK
- **Offset**: 0x0C00
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000001
- **Purpose**: Controls write access to other registers
- **Fields**: 
  * [31:1] LOCK_VALUE - Lock value (0x1ACCE551 unlocks, any other value locks)
  * [0] LOCK_STATUS - Lock status (0 = unlocked, 1 = locked)

### Register: WDOGITCR
- **Offset**: 0x0F00
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000000
- **Purpose**: Controls integration test mode
- **Fields**: 
  * [0] INTEG_TEST_EN - Integration test mode enable

### Register: WDOGITOP
- **Offset**: 0x0F04
- **Size**: 32 bits
- **Access**: WO
- **Reset Value**: Undefined
- **Purpose**: Sets interrupt and reset outputs in test mode
- **Fields**: 
  * [0] WDOGITOP - Integration test output enable for interrupt
  * [1] WDOGTOP - Integration test output enable for reset

### Register: WDOGPERIPHID0
- **Offset**: 0x0FE0
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000024
- **Purpose**: Peripheral identification register 0
- **Fields**: 
  * [7:0] PART_NUMBER_0 - Bits 7:0 of the part number

### Register: WDOGPERIPHID1
- **Offset**: 0x0FE4
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x000000B8
- **Purpose**: Peripheral identification register 1
- **Fields**: 
  * [7:4] PART_NUMBER_1 - Bits 11:8 of the part number
  * [3:0] DESIGNER_ID_1 - Bits 11:8 of the designer ID

### Register: WDOGPERIPHID2
- **Offset**: 0x0FE8
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000018
- **Purpose**: Peripheral identification register 2
- **Fields**: 
  * [7:4] REVISION - Peripheral revision
  * [3:0] DESIGNER_ID_2 - Bits 7:4 of the designer ID

### Register: WDOGPERIPHID3
- **Offset**: 0x0FEC
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 3
- **Fields**: 
  * [7:0] CONFIGURATION - Peripheral configuration

### Register: WDOGPCELLID0
- **Offset**: 0x0FF0
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x0000000D
- **Purpose**: PrimeCell identification register 0
- **Fields**: 
  * [7:0] PRIMECELL_ID_0 - Bits 7:0 of the PrimeCell ID

### Register: WDOGPCELLID1
- **Offset**: 0x0FF4
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x000000F0
- **Purpose**: PrimeCell identification register 1
- **Fields**: 
  * [7:0] PRIMECELL_ID_1 - Bits 15:8 of the PrimeCell ID

### Register: WDOGPCELLID2
- **Offset**: 0x0FF8
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000005
- **Purpose**: PrimeCell identification register 2
- **Fields**: 
  * [7:0] PRIMECELL_ID_2 - Bits 23:16 of the PrimeCell ID

### Register: WDOGPCELLID3
- **Offset**: 0x0FFC
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x000000B1
- **Purpose**: PrimeCell identification register 3
- **Fields**: 
  * [7:0] PRIMECELL_ID_3 - Bits 31:24 of the PrimeCell ID

## Device State

### State Variable: timer_counter
- **Type**: uint64
- **Purpose**: Holds the current value of the countdown timer
- **Persistence**: checkpointed

### State Variable: interrupt_pending
- **Type**: bool
- **Purpose**: Indicates if an interrupt is pending
- **Persistence**: checkpointed

### State Variable: reset_pending
- **Type**: bool
- **Purpose**: Indicates if a reset is pending
- **Persistence**: checkpointed

### State Variable: registers_locked
- **Type**: bool
- **Purpose**: Indicates if the registers are locked from write access
- **Persistence**: checkpointed

### State Variable: integration_test_mode
- **Type**: bool
- **Purpose**: Indicates if integration test mode is enabled
- **Persistence**: checkpointed

## Interfaces

### Interface: wclk
- **Type**: clock
- **Methods**: 
  * clock_tick() - Called on each clock cycle
- **Purpose**: Working clock input for the watchdog timer

### Interface: wclk_en
- **Type**: signal
- **Methods**: 
  * signal_raise() - Enable clock
  * signal_lower() - Disable clock
- **Purpose**: Clock enable signal

### Interface: wrst_n
- **Type**: signal
- **Methods**: 
  * signal_raise() - Deassert reset
  * signal_lower() - Assert reset
- **Purpose**: Reset input signal (active low)

### Interface: wdogint
- **Type**: signal
- **Methods**: 
  * signal_raise() - Assert interrupt
  * signal_lower() - Deassert interrupt
- **Purpose**: Interrupt output signal

### Interface: wdogres
- **Type**: signal
- **Methods**: 
  * signal_raise() - Assert reset
  * signal_lower() - Deassert reset
- **Purpose**: Reset output signal