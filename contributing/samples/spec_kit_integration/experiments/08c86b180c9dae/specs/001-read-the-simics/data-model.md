# Data Model: Simics Watchdog Timer Device Implementation

## Registers (Simics Projects)

### Register: WDOGLOAD
- **Offset**: 0x0000
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0xFFFFFFFF
- **Purpose**: Load register that holds the initial countdown value for the watchdog timer
- **Fields**: 
  * [31:0] LOAD_VALUE - Initial countdown value

### Register: WDOGVALUE
- **Offset**: 0x0004
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0xFFFFFFFF
- **Purpose**: Current value register that reflects the current countdown value of the watchdog timer
- **Fields**: 
  * [31:0] CURRENT_VALUE - Current countdown value

### Register: WDOGCONTROL
- **Offset**: 0x0008
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000000
- **Purpose**: Control register that enables/disables timer functions and sets operational parameters
- **Fields**: 
  * [0] ENABLE - Enable the watchdog timer (0=disabled, 1=enabled)
  * [1] RESEN - Enable reset generation (0=disabled, 1=enabled)
  * [2] INTEN - Enable interrupt generation (0=disabled, 1=enabled)
  * [4:3] DIVSEL - Clock divider selection (00=÷1, 01=÷2, 10=÷4, 11=÷8, with additional ÷16 support)

### Register: WDOGINTCLR
- **Offset**: 0x000C
- **Size**: 32 bits
- **Access**: WO
- **Reset Value**: 0x00000000
- **Purpose**: Interrupt clear register that clears interrupt status when written to
- **Fields**: 
  * [0] INTCLR - Clear interrupt status (write any value to clear)

### Register: WDOGRIS
- **Offset**: 0x0010
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Raw interrupt status register that indicates interrupt status
- **Fields**: 
  * [0] RIS - Raw interrupt status (0=no interrupt, 1=interrupt pending)

### Register: WDOGMIS
- **Offset**: 0x0014
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Masked interrupt status register that indicates masked interrupt status
- **Fields**: 
  * [0] MIS - Masked interrupt status (0=no masked interrupt, 1=masked interrupt pending)

### Register: WDOGLOCK
- **Offset**: 0x0C00
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000001
- **Purpose**: Lock register that prevents unauthorized writes to other registers using a magic unlock value
- **Fields**: 
  * [31:0] LOCK_VALUE - Lock value (0x1ACCE551=unlocked, any other value=locked)

### Register: WDOGITCR
- **Offset**: 0x0F00
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000000
- **Purpose**: Integration test control register for direct signal control
- **Fields**: 
  * [0] INTEG_TEST_EN - Integration test enable (0=normal mode, 1=test mode)

### Register: WDOGITOP
- **Offset**: 0x0F04
- **Size**: 32 bits
- **Access**: RW
- **Reset Value**: 0x00000000
- **Purpose**: Integration test output set register for direct signal control
- **Fields**: 
  * [0] INTEG_TEST_OUT - Integration test output control

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
  * [3:0] REVISION - Revision number

### Register: WDOGPERIPHID2
- **Offset**: 0x0FE8
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x0000001B
- **Purpose**: Peripheral identification register 2
- **Fields**: 
  * [7:4] REVISION - Revision number (continued)
  * [3:0] CONFIGURATION - Configuration options

### Register: WDOGPERIPHID3
- **Offset**: 0x0FEC
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 3
- **Fields**: 
  * [7:0] CUSTOMER_MODIFIED - Customer modified bits

### Register: WDOGPERIPHID4
- **Offset**: 0x0FD0
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000004
- **Purpose**: Peripheral identification register 4
- **Fields**: 
  * [7:4] CONTINUATION_CODE - Continuation code
  * [3:0] SIZE - Size indicator

### Register: WDOGPERIPHID5
- **Offset**: 0x0FD4
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 5
- **Fields**: 
  * [7:0] RESERVED - Reserved bits

### Register: WDOGPERIPHID6
- **Offset**: 0x0FD8
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 6
- **Fields**: 
  * [7:0] RESERVED - Reserved bits

### Register: WDOGPERIPHID7
- **Offset**: 0x0FDC
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000000
- **Purpose**: Peripheral identification register 7
- **Fields**: 
  * [7:0] RESERVED - Reserved bits

### Register: WDOGPCELLID0
- **Offset**: 0x0FF0
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x0000000D
- **Purpose**: PrimeCell identification register 0
- **Fields**: 
  * [7:0] PRIMECELL_ID_0 - Bits 7:0 of PrimeCell ID

### Register: WDOGPCELLID1
- **Offset**: 0x0FF4
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x000000F0
- **Purpose**: PrimeCell identification register 1
- **Fields**: 
  * [7:0] PRIMECELL_ID_1 - Bits 15:8 of PrimeCell ID

### Register: WDOGPCELLID2
- **Offset**: 0x0FF8
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x00000005
- **Purpose**: PrimeCell identification register 2
- **Fields**: 
  * [7:0] PRIMECELL_ID_2 - Bits 23:16 of PrimeCell ID

### Register: WDOGPCELLID3
- **Offset**: 0x0FFC
- **Size**: 32 bits
- **Access**: RO
- **Reset Value**: 0x000000B1
- **Purpose**: PrimeCell identification register 3
- **Fields**: 
  * [7:0] PRIMECELL_ID_3 - Bits 31:24 of PrimeCell ID

## Device State (Simics Projects)

### State Variable: countdown_value
- **Type**: uint64
- **Purpose**: Tracks the current countdown value for the watchdog timer
- **Persistence**: checkpointed

### State Variable: interrupt_status
- **Type**: bool
- **Purpose**: Tracks whether an interrupt is currently pending
- **Persistence**: checkpointed

### State Variable: reset_status
- **Type**: bool
- **Purpose**: Tracks whether a reset condition has been triggered
- **Persistence**: checkpointed

### State Variable: lock_status
- **Type**: bool
- **Purpose**: Tracks whether the device registers are currently locked
- **Persistence**: checkpointed

### State Variable: timer_enabled
- **Type**: bool
- **Purpose**: Tracks whether the watchdog timer is currently enabled
- **Persistence**: checkpointed

### State Variable: clock_divider
- **Type**: uint32
- **Purpose**: Tracks the current clock divider setting
- **Persistence**: checkpointed

## Interfaces (Simics Projects)

### Interface: interrupt_output
- **Type**: signal
- **Methods**: signal_raise(), signal_lower()
- **Purpose**: Output interface for generating interrupt signals to the system

### Interface: reset_output
- **Type**: signal
- **Methods**: signal_raise(), signal_lower()
- **Purpose**: Output interface for generating reset signals to the system

### Interface: clock_input
- **Type**: clock
- **Methods**: cycle_callback()
- **Purpose**: Input interface for receiving clock signals to drive the timer