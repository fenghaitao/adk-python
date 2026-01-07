# Watchdog Timer (WDT) Device Specification

## 1. Device Overview

### 1.1 Device Identity
- **Device Name**: Watchdog Timer (WDT)
- **Device Type/Category**: Timer/Counter
- **Base Address**: 0x1000
- **Address Range**: 0x1000 - 0x1FFF (4KB address space)
- **Version Information**: Compatible with ARM PrimeCell SP805 Watchdog Timer
- **Vendor Information**: ARM PrimeCell specification compatible

### 1.2 Device Purpose
The Watchdog Timer is a 32-bit decrementing counter that provides system reliability by generating interrupts and reset signals when software fails to periodically refresh the counter. It supports configurable timeout periods, lock protection, and integration test modes.

## 2. Register Map

### 2.1 Register Map Overview Table

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x000  | WDOGLOAD      | RW   | 32    | 0xFFFFFFFF  | Load register - sets counter value |
| 0x004  | WDOGVALUE     | RO   | 32    | 0xFFFFFFFF  | Current counter value |
| 0x008  | WDOGCONTROL   | RW   | 32    | 0x00000000  | Control register - interrupt/reset enable |
| 0x00C  | WDOGINTCLR    | WO   | 32    | N/A         | Interrupt clear register |
| 0x010  | WDOGRIS       | RO   | 32    | 0x00000000  | Raw interrupt status |
| 0x014  | WDOGMIS       | RO   | 32    | 0x00000000  | Masked interrupt status |
| 0xC00  | WDOGLOCK      | RW   | 32    | 0x00000000  | Lock register - protects against accidental writes |
| 0xF00  | WDOGITCR      | RW   | 32    | 0x00000000  | Integration test control |
| 0xF04  | WDOGITOP      | WO   | 32    | N/A         | Integration test output set |
| 0xFE0  | WDOGPeriphID0 | RO   | 32    | 0x00000005  | Peripheral ID register 0 |
| 0xFE4  | WDOGPeriphID1 | RO   | 32    | 0x00000018  | Peripheral ID register 1 |
| 0xFE8  | WDOGPeriphID2 | RO   | 32    | 0x00000018  | Peripheral ID register 2 |
| 0xFEC  | WDOGPeriphID3 | RO   | 32    | 0x00000000  | Peripheral ID register 3 |
| 0xFF0  | WDOGPCellID0  | RO   | 32    | 0x0000000D  | PrimeCell ID register 0 |
| 0xFF4  | WDOGPCellID1  | RO   | 32    | 0x000000F0  | PrimeCell ID register 1 |
| 0xFF8  | WDOGPCellID2  | RO   | 32    | 0x00000005  | PrimeCell ID register 2 |
| 0xFFC  | WDOGPCellID3  | RO   | 32    | 0x000000B1  | PrimeCell ID register 3 |

### 2.2 Detailed Register Descriptions (Side-Effect Registers Only)

#### WDOGLOAD (Offset: 0x000, RW, Reset: 0xFFFFFFFF)

Load value for the watchdog counter. Writing to this register reloads the counter with the written value.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:0      | LOAD       | RW   | 0xFFFFFFFF | Counter load value |

**Write Side-Effects**:
- Trigger: Write any value to WDOGLOAD
- Action: Counter (WDOGVALUE) is immediately reloaded with written value
- Dependencies: Register write only succeeds when WDOGLOCK is unlocked (contains value != 0x1)
- Observable: WDOGVALUE register reads back the new load value

**Read Side-Effects**: None - returns last written value

#### WDOGVALUE (Offset: 0x004, RO, Reset: 0xFFFFFFFF)

Current counter value register. Provides read-only access to the current countdown value.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:0      | VALUE      | RO   | 0xFFFFFFFF | Current counter value |

**Read Side-Effects**: None - returns current counter value
**Write Side-Effects**: Writes are ignored

**Counter Behavior**:
- Decrements automatically when WDOGCONTROL.INTEN = 1
- Decrement rate determined by simulation event timing (functional model)
- When reaches 0: WDOGRIS.WDOGRIS is set to 1, interrupt is asserted
- Reloaded from WDOGLOAD when counter reaches 0

#### WDOGCONTROL (Offset: 0x008, RW, Reset: 0x00000000)

Control register for interrupt and reset enable.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:2      | Reserved   | RO   | 0     | Reserved, read as zero |
| 1         | RESEN      | RW   | 0     | Reset enable. 1=enabled, 0=disabled |
| 0         | INTEN      | RW   | 0     | Interrupt enable. 1=enabled, 0=disabled |

**Write Side-Effects**:

**INTEN bit (bit 0)**:
- Trigger: Write 1 to INTEN (0→1 transition)
- Action: Watchdog timer starts counting down from WDOGLOAD value
- Dependencies: Counter starts immediately after write
- Observable: WDOGVALUE begins decrementing

**RESEN bit (bit 1)**:
- Trigger: Write 1 to RESEN
- Action: Enables reset generation on second timeout (when counter reaches 0 while interrupt is still asserted)
- Dependencies: Requires INTEN = 1 for timer operation
- Observable: Reset signal asserted when counter expires twice without interrupt clear

**Read Side-Effects**: None - returns current control register value

#### WDOGINTCLR (Offset: 0x00C, WO, Reset: N/A)

Interrupt clear register. Any write to this register clears the watchdog interrupt.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:0      | INTCLR     | WO   | N/A   | Interrupt clear - any write clears interrupt |

**Write Side-Effects**:
- Trigger: Any write to WDOGINTCLR (value doesn't matter)
- Action: Clears WDOGRIS.WDOGRIS bit, deasserts wdogint interrupt signal, reloads counter from WDOGLOAD
- Dependencies: None - always succeeds
- Observable: WDOGRIS.WDOGRIS reads as 0, wdogint signal goes low, WDOGVALUE reloaded

**Read Side-Effects**: Read returns undefined value

#### WDOGRIS (Offset: 0x010, RO, Reset: 0x00000000)

Raw interrupt status register.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:1      | Reserved   | RO   | 0     | Reserved, read as zero |
| 0         | WDOGRIS    | RO   | 0     | Raw interrupt status. 1=interrupt pending, 0=no interrupt |

**Read Side-Effects**: None - returns current raw interrupt status
**Write Side-Effects**: Writes are ignored

**Automatic Updates**:
- Set to 1 when counter reaches 0 and INTEN = 1
- Cleared to 0 when software writes to WDOGINTCLR

#### WDOGMIS (Offset: 0x014, RO, Reset: 0x00000000)

Masked interrupt status register. Shows the bitwise AND of WDOGRIS and WDOGCONTROL.INTEN.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:1      | Reserved   | RO   | 0     | Reserved, read as zero |
| 0         | WDOGMIS    | RO   | 0     | Masked interrupt status = WDOGRIS[0] AND INTEN |

**Read Side-Effects**: None - returns (WDOGRIS & INTEN)
**Write Side-Effects**: Writes are ignored

#### WDOGLOCK (Offset: 0xC00, RW, Reset: 0x00000000)

Lock register to prevent accidental modification of watchdog registers.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:0      | LOCK       | RW   | 0x00000000 | Lock status. 0=unlocked, 1=locked, 0x1ACCE551=unlock |

**Write Side-Effects**:

**Write 0x1ACCE551 (Unlock)**:
- Trigger: Write magic value 0x1ACCE551 to WDOGLOCK
- Action: Register lock is cleared, WDOGLOCK reads as 0x00000000
- Dependencies: None
- Observable: WDOGLOCK reads as 0, WDOGLOAD/WDOGCONTROL/WDOGITCR become writable

**Write any other value**:
- Trigger: Write value != 0x1ACCE551 to WDOGLOCK
- Action: Register lock is set, WDOGLOCK reads as 0x00000001
- Dependencies: None
- Observable: WDOGLOCK reads as 1, writes to WDOGLOAD/WDOGCONTROL/WDOGITCR are ignored

**Read Side-Effects**: None - returns 0 (unlocked) or 1 (locked)

**Lock Protection Scope**:
When locked (WDOGLOCK != 0):
- WDOGLOAD writes are ignored
- WDOGCONTROL writes are ignored
- WDOGITCR writes are ignored
- WDOGINTCLR writes still succeed (interrupt clear always works)
- WDOGLOCK itself can still be written

#### WDOGITCR (Offset: 0xF00, RW, Reset: 0x00000000)

Integration test control register. Enables integration test mode for direct control of output signals.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:1      | Reserved   | RO   | 0     | Reserved, read as zero |
| 0         | ITCR       | RW   | 0     | Integration test enable. 1=test mode, 0=normal mode |

**Write Side-Effects**:
- Trigger: Write 1 to ITCR (0→1 transition)
- Action: Device enters integration test mode; WDOGITOP controls output signals directly
- Dependencies: Register write only succeeds when WDOGLOCK is unlocked
- Observable: Normal counter operation suspended, outputs controlled by WDOGITOP

**Read Side-Effects**: None - returns current test mode status

#### WDOGITOP (Offset: 0xF04, WO, Reset: N/A)

Integration test output set register. In integration test mode, directly controls output signals.

| Bit Range | Field Name | Type | Reset | Description |
|-----------|------------|------|-------|-------------|
| 31:2      | Reserved   | WO   | N/A   | Reserved |
| 1         | WDOGRES    | WO   | N/A   | Reset output. 1=assert reset, 0=deassert reset |
| 0         | WDOGINT    | WO   | N/A   | Interrupt output. 1=assert interrupt, 0=deassert interrupt |

**Write Side-Effects**:
- Trigger: Write to WDOGITOP when WDOGITCR.ITCR = 1
- Action: Directly sets wdogint and wdogres output signals
- Dependencies: Requires WDOGITCR.ITCR = 1 (test mode enabled)
- Observable: Output signals immediately reflect written values

**Read Side-Effects**: Read returns undefined value

## 3. External Interfaces & Signals

### 3.1 Clock Signals

**PCLK** (APB clock):
- Direction: Input
- Description: APB bus clock for register access
- [NEEDS CLARIFICATION: Clock frequency not specified - functional model does not require specific frequency]

**WDOGCLK** (Watchdog clock):
- Direction: Input  
- Description: Clock source for watchdog counter decrementation
- [NEEDS CLARIFICATION: Clock frequency not specified - functional model uses event-based timing instead of cycle-accurate clock]

**WDOGCLKEN** (Watchdog clock enable):
- Direction: Input
- Description: Clock enable signal for WDOGCLK (not modeled in functional implementation)

### 3.2 Reset Signals

**PRESETn** (APB reset):
- Direction: Input
- Type: Asynchronous
- Polarity: Active-low
- Description: Resets all registers to default values

### 3.3 Interrupt Signals

**WDOGINT** (Watchdog interrupt):
- Direction: Output
- Type: Edge-triggered (rising edge)
- Polarity: Active-high
- Assertion Condition: Counter reaches 0 and WDOGCONTROL.INTEN = 1
- Deassertion Condition: Software writes to WDOGINTCLR
- Description: Interrupt signal indicating first timeout event

### 3.4 Reset Output Signals

**WDOGRES** (Watchdog reset output):
- Direction: Output
- Type: Level-triggered
- Polarity: Active-high
- Assertion Condition: Counter reaches 0 for second time while WDOGINT is still asserted and WDOGCONTROL.RESEN = 1
- Deassertion Condition: System reset or WDOGINTCLR write before second timeout
- Description: System reset signal indicating watchdog timeout failure

### 3.5 Bus Interface

**APB Interface**:
- Protocol: AMBA 3 APB (Advanced Peripheral Bus)
- Data Width: 32 bits
- Address Width: 12 bits (4KB address space)
- Control Signals: PSEL, PENABLE, PWRITE, PADDR, PWDATA, PRDATA, PREADY, PSLVERR

## 4. Register Side-Effects & Behaviors

### 4.1 Counter Operation Behaviors

**Counter Decrement**:
```
Trigger: WDOGCONTROL.INTEN = 1
Action: Counter automatically decrements from WDOGLOAD value
Dependencies: None
Observable: WDOGVALUE decreases over time
Simics Note: Use event mechanism to schedule periodic decrements
```

**Counter Reload on Write**:
```
Trigger: Write to WDOGLOAD register
Action: WDOGVALUE immediately updated to new WDOGLOAD value
Dependencies: WDOGLOCK must be unlocked (value = 0)
Observable: WDOGVALUE reads back new load value
Simics Note: Cancel existing timer event, restart with new value
```

**Counter Reload on Interrupt Clear**:
```
Trigger: Write to WDOGINTCLR
Action: Counter reloaded from WDOGLOAD, interrupt cleared
Dependencies: None (always succeeds regardless of lock state)
Observable: WDOGVALUE = WDOGLOAD, WDOGRIS[0] = 0, wdogint deasserted
Simics Note: Reschedule timer event, clear interrupt state
```

### 4.2 Interrupt Generation Behaviors

**First Timeout (Interrupt Assertion)**:
```
Trigger: WDOGVALUE decrements to 0 and INTEN = 1
Action: Set WDOGRIS[0] = 1, assert wdogint signal (rising edge), reload counter from WDOGLOAD
Dependencies: WDOGCONTROL.INTEN = 1
Observable: WDOGRIS[0] = 1, WDOGMIS[0] = 1 (if INTEN=1), wdogint pin high, WDOGVALUE = WDOGLOAD
Simics Note: Set interrupt port, schedule next countdown event
```

**Interrupt Clear**:
```
Trigger: Write any value to WDOGINTCLR
Action: Clear WDOGRIS[0], deassert wdogint, reload counter
Dependencies: None
Observable: WDOGRIS[0] = 0, WDOGMIS[0] = 0, wdogint pin low, WDOGVALUE = WDOGLOAD
Simics Note: Clear interrupt port, cancel reset pending state
```

### 4.3 Reset Generation Behaviors

**Second Timeout (Reset Assertion)**:
```
Trigger: WDOGVALUE decrements to 0 while WDOGRIS[0] = 1 (interrupt not cleared) and RESEN = 1
Action: Assert wdogres signal (level high)
Dependencies: WDOGCONTROL.RESEN = 1, WDOGRIS[0] = 1 (interrupt still pending)
Observable: wdogres pin high, system reset initiated
Simics Note: Set reset output port
```

### 4.4 Lock Protection Behaviors

**Lock Enable**:
```
Trigger: Write any value != 0x1ACCE551 to WDOGLOCK
Action: Set lock state, WDOGLOCK reads as 1, protected registers become read-only
Dependencies: None
Observable: WDOGLOCK = 1, writes to WDOGLOAD/WDOGCONTROL/WDOGITCR ignored
Simics Note: Set lock flag variable
```

**Lock Disable (Unlock)**:
```
Trigger: Write 0x1ACCE551 to WDOGLOCK
Action: Clear lock state, WDOGLOCK reads as 0, protected registers become writable
Dependencies: None
Observable: WDOGLOCK = 0, writes to WDOGLOAD/WDOGCONTROL/WDOGITCR succeed
Simics Note: Clear lock flag variable
```

### 4.5 Integration Test Behaviors

**Enter Test Mode**:
```
Trigger: Write 1 to WDOGITCR.ITCR when WDOGLOCK = 0
Action: Normal counter operation suspended, WDOGITOP controls outputs
Dependencies: WDOGLOCK = 0 (unlocked)
Observable: WDOGITCR[0] = 1, counter stops, outputs controlled by WDOGITOP
Simics Note: Set test mode flag, cancel timer events
```

**Test Output Control**:
```
Trigger: Write to WDOGITOP when WDOGITCR.ITCR = 1
Action: WDOGITOP[0] directly controls wdogint, WDOGITOP[1] controls wdogres
Dependencies: WDOGITCR.ITCR = 1 (test mode active)
Observable: wdogint = WDOGITOP[0], wdogres = WDOGITOP[1]
Simics Note: Set output port values from register bits
```

## 5. Device Operational Model

### 5.1 Device States

#### State: IDLE
- **Entry Conditions**: After reset (PRESETn asserted) or WDOGCONTROL.INTEN = 0
- **Observable Indicators**: WDOGCONTROL.INTEN = 0, WDOGVALUE static, WDOGRIS[0] = 0, wdogint low
- **Active Behaviors**: No counter operation, all register values preserved, no interrupts or resets
- **Exit Conditions**: Write INTEN = 1 to WDOGCONTROL
- **Simics Implementation Note**: state variable = STATE_IDLE, no active timer events

#### State: COUNTING
- **Entry Conditions**: Write INTEN = 1 to WDOGCONTROL with WDOGLOCK = 0
- **Observable Indicators**: WDOGCONTROL.INTEN = 1, WDOGVALUE decrements, WDOGRIS[0] = 0, wdogint low
- **Active Behaviors**: Counter decrements from WDOGLOAD value toward 0, no interrupt asserted yet
- **Exit Conditions**: Counter reaches 0 (→ INTERRUPT_PENDING), or INTEN cleared (→ IDLE)
- **Simics Implementation Note**: state variable = STATE_COUNTING, timer event scheduled for next decrement

#### State: INTERRUPT_PENDING
- **Entry Conditions**: Counter reaches 0 from COUNTING state while INTEN = 1
- **Observable Indicators**: WDOGRIS[0] = 1, WDOGMIS[0] = 1, wdogint asserted high, WDOGVALUE = WDOGLOAD
- **Active Behaviors**: Counter reloaded and continues counting, interrupt signal asserted, reset pending if RESEN = 1
- **Exit Conditions**: Write to WDOGINTCLR (→ COUNTING), or counter reaches 0 again with RESEN=1 (→ RESET_ASSERTED), or INTEN cleared (→ IDLE)
- **Simics Implementation Note**: state variable = STATE_INTERRUPT_PENDING, interrupt port set, timer continues

#### State: RESET_ASSERTED
- **Entry Conditions**: Counter reaches 0 from INTERRUPT_PENDING state while RESEN = 1 and interrupt not cleared
- **Observable Indicators**: WDOGRIS[0] = 1, wdogint high, wdogres asserted high
- **Active Behaviors**: Reset signal asserted, system reset in progress
- **Exit Conditions**: System reset completes, PRESETn asserted (→ IDLE)
- **Simics Implementation Note**: state variable = STATE_RESET_ASSERTED, reset port set

#### State: INTEGRATION_TEST
- **Entry Conditions**: Write ITCR = 1 to WDOGITCR when WDOGLOCK = 0
- **Observable Indicators**: WDOGITCR[0] = 1, counter stopped, outputs controlled by WDOGITOP
- **Active Behaviors**: Normal operation suspended, WDOGITOP directly controls wdogint and wdogres outputs
- **Exit Conditions**: Write ITCR = 0 to WDOGITCR (→ IDLE or COUNTING depending on INTEN)
- **Simics Implementation Note**: state variable = STATE_TEST_MODE, timer events cancelled

#### State: LOCKED
- **Entry Conditions**: Write any value != 0x1ACCE551 to WDOGLOCK
- **Observable Indicators**: WDOGLOCK reads as 1, writes to WDOGLOAD/WDOGCONTROL/WDOGITCR ignored
- **Active Behaviors**: Lock protection active, counter continues operation if already running, protected registers read-only
- **Exit Conditions**: Write 0x1ACCE551 to WDOGLOCK (returns to previous operational state)
- **Simics Implementation Note**: lock flag set, register write checks lock status
- **Note**: LOCKED is a protection state that overlays other operational states

### 5.2 State Transitions

```
IDLE → COUNTING: Write WDOGCONTROL.INTEN = 1
- Register writes: WDOGCONTROL[0] = 1
- Hardware events: Counter starts decrementing from WDOGLOAD
- Observable change: WDOGVALUE begins decreasing, WDOGCONTROL.INTEN = 1

COUNTING → INTERRUPT_PENDING: Counter reaches 0
- Register writes: None (automatic hardware event)
- Hardware events: Counter = 0, interrupt logic activates
- Observable change: WDOGRIS[0] = 1, wdogint rises, WDOGVALUE reloaded to WDOGLOAD

INTERRUPT_PENDING → COUNTING: Write to WDOGINTCLR
- Register writes: Any write to WDOGINTCLR register
- Hardware events: Interrupt cleared, counter reloaded
- Observable change: WDOGRIS[0] = 0, wdogint falls, WDOGVALUE = WDOGLOAD

INTERRUPT_PENDING → RESET_ASSERTED: Counter reaches 0 with RESEN=1
- Register writes: None (automatic hardware event)
- Hardware events: Second timeout while interrupt pending
- Observable change: wdogres asserts high

COUNTING/INTERRUPT_PENDING → IDLE: Write WDOGCONTROL.INTEN = 0
- Register writes: WDOGCONTROL[0] = 0
- Hardware events: Counter stops
- Observable change: WDOGVALUE static, WDOGCONTROL.INTEN = 0

Any State → INTEGRATION_TEST: Write WDOGITCR.ITCR = 1 (if unlocked)
- Register writes: WDOGITCR[0] = 1
- Hardware events: Normal operation suspended
- Observable change: WDOGITCR[0] = 1, outputs controlled by WDOGITOP

INTEGRATION_TEST → IDLE/COUNTING: Write WDOGITCR.ITCR = 0
- Register writes: WDOGITCR[0] = 0
- Hardware events: Resume normal operation
- Observable change: Returns to state based on WDOGCONTROL.INTEN value

Any State ⇄ LOCKED: WDOGLOCK writes
- Register writes: WDOGLOCK = any value except 0x1ACCE551 (lock), WDOGLOCK = 0x1ACCE551 (unlock)
- Hardware events: Lock protection activated/deactivated
- Observable change: WDOGLOCK reads as 1 (locked) or 0 (unlocked)
```

### 5.3 SW/HW Interaction Flows

#### Flow: Basic Watchdog Timer Operation with Interrupt

**State Transition**: IDLE → COUNTING → INTERRUPT_PENDING → COUNTING → ...

| Step | Software Actions | Hardware Responses | Observable State |
|------|------------------|-------------------|------------------|
| 1    | Write 1000 to WDOGLOAD | Value stored in load register | WDOGLOAD=1000, WDOGVALUE=1000 |
| 2    | Write INTEN=1 to WDOGCONTROL | Counter starts decrementing | WDOGVALUE=1000, STATUS: COUNTING |
| 3    | Wait (polling or interrupt-driven) | Counter decrements 1000→999→...→1 | WDOGVALUE decreasing |
| 4    | Counter reaches 0 | IRQ asserted, WDOGRIS[0]=1, counter reloaded | wdogint=HIGH, WDOGRIS=1, WDOGVALUE=1000 |
| 5    | Read WDOGRIS to check status | Returns 0x00000001 | WDOGRIS[0]=1 confirms interrupt |
| 6    | Write 1 to WDOGINTCLR | IRQ cleared, counter reloaded | wdogint=LOW, WDOGRIS=0, WDOGVALUE=1000 |
| 7    | Loop back to Step 3 | Counter continues from WDOGLOAD | STATUS: COUNTING |

#### Flow: Watchdog Timer with Reset Generation

**State Transition**: IDLE → COUNTING → INTERRUPT_PENDING → RESET_ASSERTED

| Step | Software Actions | Hardware Responses | Observable State |
|------|------------------|-------------------|------------------|
| 1    | Write 100 to WDOGLOAD | Value stored | WDOGLOAD=100, WDOGVALUE=100 |
| 2    | Write INTEN=1, RESEN=1 to WDOGCONTROL | Counter starts, reset enabled | WDOGVALUE=100, STATUS: COUNTING |
| 3    | Wait without servicing | Counter decrements to 0 | WDOGVALUE decreasing to 0 |
| 4    | First timeout (counter=0) | IRQ asserted, counter reloaded | wdogint=HIGH, WDOGRIS=1, WDOGVALUE=100, STATUS: INTERRUPT_PENDING |
| 5    | Software fails to clear interrupt | Counter continues decrementing | WDOGVALUE decreasing, wdogint still HIGH |
| 6    | Second timeout (counter=0 again) | Reset asserted | wdogres=HIGH, system reset, STATUS: RESET_ASSERTED |
| 7    | System reset executes | Device returns to IDLE state | All registers reset to default values |

#### Flow: Lock Protection Mechanism

**State Transition**: IDLE → LOCKED → IDLE (with protection active/inactive)

| Step | Software Actions | Hardware Responses | Observable State |
|------|------------------|-------------------|------------------|
| 1    | Read WDOGLOCK | Returns 0 (unlocked) | WDOGLOCK=0 (unlocked state) |
| 2    | Write 500 to WDOGLOAD | Write succeeds | WDOGLOAD=500, WDOGVALUE=500 |
| 3    | Write 0x00000001 to WDOGLOCK | Lock activated | WDOGLOCK reads as 1 (locked) |
| 4    | Attempt write 1000 to WDOGLOAD | Write ignored (protected) | WDOGLOAD=500 (unchanged) |
| 5    | Attempt write INTEN=1 to WDOGCONTROL | Write ignored (protected) | WDOGCONTROL=0 (unchanged) |
| 6    | Write 0x1ACCE551 to WDOGLOCK | Lock cleared | WDOGLOCK reads as 0 (unlocked) |
| 7    | Write 1000 to WDOGLOAD | Write succeeds | WDOGLOAD=1000 |
| 8    | Write INTEN=1 to WDOGCONTROL | Write succeeds, counter starts | WDOGCONTROL.INTEN=1, STATUS: COUNTING |

#### Flow: Integration Test Mode

**State Transition**: IDLE → INTEGRATION_TEST → IDLE

| Step | Software Actions | Hardware Responses | Observable State |
|------|------------------|-------------------|------------------|
| 1    | Write 0x1ACCE551 to WDOGLOCK | Unlock device | WDOGLOCK=0 |
| 2    | Write ITCR=1 to WDOGITCR | Enter test mode | WDOGITCR[0]=1, normal operation suspended |
| 3    | Write 0x1 to WDOGITOP | Set wdogint=1, wdogres=0 | wdogint=HIGH, wdogres=LOW |
| 4    | Read interrupt pin status | Verify interrupt asserted | wdogint=HIGH (test) |
| 5    | Write 0x2 to WDOGITOP | Set wdogint=0, wdogres=1 | wdogint=LOW, wdogres=HIGH |
| 6    | Read reset pin status | Verify reset asserted | wdogres=HIGH (test) |
| 7    | Write 0x0 to WDOGITOP | Clear both outputs | wdogint=LOW, wdogres=LOW |
| 8    | Write ITCR=0 to WDOGITCR | Exit test mode | WDOGITCR[0]=0, resume normal operation |

#### Flow: Counter Reload During Operation

**State Transition**: COUNTING → COUNTING (with value update)

| Step | Software Actions | Hardware Responses | Observable State |
|------|------------------|-------------------|------------------|
| 1    | Write 10000 to WDOGLOAD | Initial load value set | WDOGLOAD=10000, WDOGVALUE=10000 |
| 2    | Write INTEN=1 to WDOGCONTROL | Counter starts | STATUS: COUNTING |
| 3    | Wait (counter decrements to ~5000) | Counter decrements | WDOGVALUE≈5000 |
| 4    | Write 8000 to WDOGLOAD | Counter immediately reloaded | WDOGVALUE=8000 (immediate reload) |
| 5    | Continue waiting | Counter decrements from new value | WDOGVALUE decreasing from 8000 |

## 6. Simics Implementation Requirements

### 6.1 Timer Functionality Requirements

**FUNC-001**: The watchdog timer shall be implemented as a 32-bit decrementing counter that counts down from the value in WDOGLOAD register.

**FUNC-002**: The timer shall decrement using Simics event mechanism (functional model, not cycle-accurate) at a rate suitable for simulation performance.

**FUNC-003**: When the counter reaches zero for the first time, the device shall reload the counter from WDOGLOAD and continue counting.

**FUNC-004**: The counter value shall be readable at any time through the WDOGVALUE register without affecting counter operation.

### 6.2 Interrupt and Reset Requirements

**FUNC-005**: When counter reaches zero and WDOGCONTROL.INTEN=1, the device shall assert the wdogint interrupt signal (rising edge) and set WDOGRIS[0] to 1.

**FUNC-006**: The interrupt signal shall remain asserted until software writes to WDOGINTCLR register.

**FUNC-007**: If counter reaches zero again while interrupt is still asserted (WDOGRIS[0]=1) and WDOGCONTROL.RESEN=1, the device shall assert wdogres reset signal.

**FUNC-008**: Writing to WDOGINTCLR shall clear WDOGRIS[0], deassert wdogint, and reload counter from WDOGLOAD.

**FUNC-009**: The WDOGMIS register shall reflect the bitwise AND of WDOGRIS[0] and WDOGCONTROL.INTEN.

### 6.3 Register Access Requirements

**REG-001**: WDOGLOAD register shall support read and write operations; writes shall immediately reload the counter value.

**REG-002**: WDOGVALUE register shall support read operations only and return the current counter value.

**REG-003**: WDOGCONTROL register shall support read and write operations for INTEN (bit 0) and RESEN (bit 1) fields.

**REG-004**: WDOGINTCLR register shall be write-only; any write value shall trigger interrupt clear operation.

**REG-005**: WDOGRIS and WDOGMIS registers shall be read-only status registers.

**REG-006**: WDOGLOCK register shall support read and write operations with special unlock value 0x1ACCE551.

**REG-007**: WDOGITCR and WDOGITOP registers shall support integration test mode operations.

**REG-008**: Peripheral ID and PrimeCell ID registers shall be read-only with fixed identification values.

**REG-009**: All registers shall reset to their specified reset values when PRESETn is asserted.

**REG-010**: Register writes shall follow 32-bit alignment; unaligned accesses behavior is implementation-defined.

### 6.4 Lock Protection Requirements

**BEHAV-001**: When WDOGLOCK register contains any value except 0 (locked state), writes to WDOGLOAD, WDOGCONTROL, and WDOGITCR registers shall be ignored.

**BEHAV-002**: Writing 0x1ACCE551 to WDOGLOCK shall unlock the device; WDOGLOCK shall read back as 0x00000000.

**BEHAV-003**: Writing any value other than 0x1ACCE551 to WDOGLOCK shall lock the device; WDOGLOCK shall read back as 0x00000001.

**BEHAV-004**: Lock protection shall not affect WDOGINTCLR operation; interrupt clear shall succeed regardless of lock state.

**BEHAV-005**: Lock protection shall not affect read operations; all registers shall remain readable when locked.

### 6.5 Behavioral Requirements

**BEHAV-006**: When WDOGCONTROL.INTEN=0, the timer shall not operate; counter shall remain at current value.

**BEHAV-007**: When WDOGCONTROL.INTEN transitions from 0 to 1, counter operation shall begin immediately.

**BEHAV-008**: When WDOGCONTROL.INTEN transitions from 1 to 0, counter operation shall stop; counter value shall be preserved.

**BEHAV-009**: When WDOGCONTROL.RESEN=0, second timeout shall not generate reset signal; only interrupt behavior applies.

**BEHAV-010**: Integration test mode (WDOGITCR.ITCR=1) shall suspend normal counter operation and allow direct output control via WDOGITOP.

### 6.6 Simics-Specific Requirements

**SIM-001**: Device shall be implemented as DML 1.4 device model targeting Simics 7.x.

**SIM-002**: Timer decrement shall be implemented using Simics event mechanism (post_event/cancel_event).

**SIM-003**: Device shall expose simple_interrupt port named "wdogint" for interrupt signal output.

**SIM-004**: Device shall expose simple_interrupt port named "wdogres" for reset signal output.

**SIM-005**: Device shall implement APB register bank with 4KB address space (0x000 - 0xFFF).

**SIM-006**: Register access shall use DML register template with appropriate read/write methods.

**SIM-007**: Device shall support checkpointing through Simics standard register state saving (automatic).

**SIM-008**: Device shall include comprehensive logging using log_info, log_error for debugging.

**SIM-009**: Device shall expose attributes for runtime configuration if needed (base address mapping handled by platform).

**SIM-010**: Implementation shall follow Simics device modeling best practices (functional model, event-driven timing).

### 6.7 Integration Requirements

**INTF-001**: Device shall be instantiated in QSP-x86 platform configuration at base address 0x1000.

**INTF-002**: Device memory map shall occupy 4KB address space from 0x1000 to 0x1FFF.

**INTF-003**: Interrupt signal (wdogint) shall be routed to platform interrupt controller with appropriate IRQ number.

**INTF-004**: Reset signal (wdogres) shall be routed to platform reset controller to trigger system reset.

**INTF-005**: Device shall be accessible via APB bus interface for register read/write operations.

## 7. Verification Scenarios

### 7.1 Basic Timer Operation Tests

**TEST-001**: Verify basic timer countdown functionality
- **Setup**: Write value 100 to WDOGLOAD, write INTEN=1 to WDOGCONTROL
- **Action**: Step simulation, poll WDOGVALUE register periodically
- **Expected**: WDOGVALUE decrements from 100 toward 0, interrupt generated when reaches 0
- **Pass Criteria**: Counter decrements correctly, WDOGRIS[0]=1 at timeout, wdogint asserted

**TEST-002**: Verify counter reload on timeout
- **Setup**: Write value 50 to WDOGLOAD, enable timer with INTEN=1
- **Action**: Wait for counter to reach 0, observe WDOGVALUE after timeout
- **Expected**: After first timeout, WDOGVALUE reloaded to 50 and continues counting
- **Pass Criteria**: WDOGVALUE=50 immediately after timeout, counter continues decrementing

**TEST-003**: Verify WDOGLOAD write reloads counter immediately
- **Setup**: Write 1000 to WDOGLOAD, enable timer, wait for counter to reach ~500
- **Action**: Write 2000 to WDOGLOAD while timer running
- **Expected**: WDOGVALUE immediately changes to 2000, continues from new value
- **Pass Criteria**: WDOGVALUE=2000 after write, counter decrements from 2000

### 7.2 Interrupt Generation and Clearing Tests

**TEST-004**: Verify interrupt generation on first timeout
- **Setup**: Write 20 to WDOGLOAD, write INTEN=1 to WDOGCONTROL
- **Action**: Wait for counter to reach 0, read WDOGRIS register
- **Expected**: WDOGRIS[0]=1, WDOGMIS[0]=1, wdogint signal asserted
- **Pass Criteria**: Interrupt status registers set, interrupt port asserted

**TEST-005**: Verify interrupt clear operation
- **Setup**: Trigger interrupt by allowing timeout (from TEST-004)
- **Action**: Write any value to WDOGINTCLR, read WDOGRIS
- **Expected**: WDOGRIS[0]=0, WDOGMIS[0]=0, wdogint signal deasserted, counter reloaded
- **Pass Criteria**: Interrupt cleared, counter reset to WDOGLOAD value

**TEST-006**: Verify WDOGMIS reflects masked interrupt status
- **Setup**: Trigger interrupt, read WDOGMIS with INTEN=1, then clear INTEN
- **Action**: Read WDOGMIS with INTEN=0 while WDOGRIS[0]=1
- **Expected**: WDOGMIS[0]=1 when INTEN=1, WDOGMIS[0]=0 when INTEN=0 (even if WDOGRIS[0]=1)
- **Pass Criteria**: WDOGMIS correctly shows (WDOGRIS & INTEN)

### 7.3 Reset Generation Tests

**TEST-007**: Verify reset generation on second timeout
- **Setup**: Write 50 to WDOGLOAD, write INTEN=1, RESEN=1 to WDOGCONTROL
- **Action**: Allow first timeout (interrupt generated), do NOT clear interrupt, wait for second timeout
- **Expected**: After second timeout, wdogres signal asserted
- **Pass Criteria**: Reset signal asserted after second timeout with interrupt pending

**TEST-008**: Verify no reset when RESEN=0
- **Setup**: Write 50 to WDOGLOAD, write INTEN=1, RESEN=0 to WDOGCONTROL
- **Action**: Allow first timeout, do NOT clear interrupt, wait for second timeout
- **Expected**: Interrupt continues to assert on each timeout, no reset signal
- **Pass Criteria**: wdogres remains deasserted even after multiple timeouts

**TEST-009**: Verify reset prevented by interrupt clear
- **Setup**: Write 30 to WDOGLOAD, write INTEN=1, RESEN=1 to WDOGCONTROL
- **Action**: Allow first timeout (interrupt generated), write to WDOGINTCLR before second timeout
- **Expected**: Reset signal not asserted because interrupt cleared before second timeout
- **Pass Criteria**: wdogres remains deasserted after interrupt clear

### 7.4 Lock Protection Tests

**TEST-010**: Verify lock protection prevents register writes
- **Setup**: Write non-magic value (e.g., 1) to WDOGLOCK
- **Action**: Attempt writes to WDOGLOAD and WDOGCONTROL
- **Expected**: Writes ignored, registers retain previous values, WDOGLOCK reads as 1
- **Pass Criteria**: Protected register writes have no effect when locked

**TEST-011**: Verify unlock with magic value
- **Setup**: Lock device (WDOGLOCK=1), then write 0x1ACCE551 to WDOGLOCK
- **Action**: Write 500 to WDOGLOAD
- **Expected**: WDOGLOCK reads as 0, WDOGLOAD write succeeds
- **Pass Criteria**: Device unlocked, register writes succeed

**TEST-012**: Verify WDOGINTCLR works regardless of lock state
- **Setup**: Lock device, trigger interrupt
- **Action**: Write to WDOGINTCLR while locked
- **Expected**: Interrupt cleared successfully even when locked
- **Pass Criteria**: WDOGRIS[0]=0, wdogint deasserted, counter reloaded

### 7.5 Integration Test Mode Tests

**TEST-013**: Verify integration test mode entry
- **Setup**: Unlock device, write ITCR=1 to WDOGITCR
- **Action**: Start counter (INTEN=1), verify no automatic operation
- **Expected**: Counter does not decrement, normal operation suspended, WDOGITCR[0]=1
- **Pass Criteria**: Counter static in test mode

**TEST-014**: Verify direct output control in test mode
- **Setup**: Enter test mode (ITCR=1), write 0x1 to WDOGITOP
- **Action**: Read interrupt signal status
- **Expected**: wdogint asserted (WDOGITOP[0]=1), wdogres deasserted (WDOGITOP[1]=0)
- **Pass Criteria**: Output signals match WDOGITOP bit values

**TEST-015**: Verify test mode exit resumes normal operation
- **Setup**: In test mode, write ITCR=0 to WDOGITCR
- **Action**: Write INTEN=1, observe counter
- **Expected**: Normal countdown operation resumes
- **Pass Criteria**: Counter decrements normally after exiting test mode

### 7.6 Edge Case and Error Handling Tests

**TEST-016**: Verify behavior with INTEN=0
- **Setup**: Write 100 to WDOGLOAD, write INTEN=0 to WDOGCONTROL
- **Action**: Step simulation, read WDOGVALUE
- **Expected**: Counter remains static at 100, no timeout, no interrupt
- **Pass Criteria**: WDOGVALUE unchanged, no timer activity

**TEST-017**: Verify maximum counter value handling
- **Setup**: Write 0xFFFFFFFF to WDOGLOAD, enable timer
- **Action**: Verify counter decrements from maximum value
- **Expected**: Counter correctly handles 32-bit maximum value
- **Pass Criteria**: Counter decrements from 0xFFFFFFFF without overflow issues

**TEST-018**: Verify zero load value handling
- **Setup**: Write 0 to WDOGLOAD, enable timer
- **Action**: Observe timeout behavior
- **Expected**: Immediate timeout (counter=0), interrupt generated immediately
- **Pass Criteria**: Interrupt asserted immediately or on first event cycle

**TEST-019**: Verify register read-only enforcement
- **Setup**: Attempt writes to WDOGVALUE, WDOGRIS, WDOGMIS
- **Action**: Write arbitrary values, read back registers
- **Expected**: Writes ignored, registers return actual status values
- **Pass Criteria**: Read-only registers cannot be modified by writes

**TEST-020**: Verify peripheral/PrimeCell ID registers
- **Setup**: Read all ID registers (WDOGPeriphID0-3, WDOGPCellID0-3)
- **Action**: Compare against expected values
- **Expected**: ID registers return correct ARM PrimeCell identification values
- **Pass Criteria**: All ID registers match specification

### 7.7 State Transition Tests

**TEST-021**: Verify IDLE → COUNTING transition
- **Setup**: Device in IDLE (INTEN=0)
- **Action**: Write INTEN=1 to WDOGCONTROL
- **Expected**: Timer immediately begins counting down
- **Pass Criteria**: WDOGVALUE begins decrementing

**TEST-022**: Verify COUNTING → INTERRUPT_PENDING transition
- **Setup**: Timer counting with small WDOGLOAD value
- **Action**: Wait for timeout
- **Expected**: Transition to INTERRUPT_PENDING state, WDOGRIS[0]=1
- **Pass Criteria**: Interrupt asserted, state transition observable

**TEST-023**: Verify INTERRUPT_PENDING → RESET_ASSERTED transition
- **Setup**: In INTERRUPT_PENDING state with RESEN=1
- **Action**: Wait for second timeout without clearing interrupt
- **Expected**: Reset signal asserted, state transition to RESET_ASSERTED
- **Pass Criteria**: wdogres asserted on second timeout

### 7.8 Performance and Stress Tests

**TEST-024**: Verify rapid register access
- **Setup**: Enable timer
- **Action**: Perform rapid consecutive reads/writes to various registers
- **Expected**: All accesses complete correctly without race conditions
- **Pass Criteria**: No data corruption, all operations execute correctly

**TEST-025**: Verify long-duration countdown
- **Setup**: Write large value (0x10000000) to WDOGLOAD, enable timer
- **Action**: Fast-forward simulation to timeout
- **Expected**: Counter correctly decrements over extended period
- **Pass Criteria**: Timeout occurs at expected simulation time

## 8. Clarification Notes

The following aspects require clarification or are noted as implementation-specific:

1. **Clock Frequency**: [NEEDS CLARIFICATION] Exact WDOGCLK frequency not specified. Functional model uses event-based timing with configurable decrement rate suitable for simulation performance.
- For functional simulation purposes, we will implement the timer using Simics event mechanism, and ignore the clock rating.

2. **Clock Divider Settings**: Specification mentions 5 clock divider settings (÷1, ÷2, ÷4, ÷8, ÷16) but no register field for divider configuration found. [NEEDS CLARIFICATION: Is divider controlled via undocumented register field, or is this a fixed configuration?]
- by default we will assume ÷1 (no division) for functional model, and default clock frequency is 100MHz.

3. **Unaligned Access**: APB specification supports 32-bit aligned access. Behavior for unaligned reads/writes is implementation-defined. [NEEDS CLARIFICATION: Should unaligned access return error or allow byte/halfword access?]
- We support unaligned access by allowing byte/halfword accesses through the byte_enabled parameter in registers read_register/write_register methods.

4. **Reset Signal Duration**: Specification does not define how long wdogres remains asserted. [NEEDS CLARIFICATION: Reset pulse duration, or held until system reset completes?]
- We will assume wdogres remains asserted until system reset is completed (PRESETn asserted).

5. **Integration Test Constraints**: WDOGITOP register bit definitions for test mode outputs may have additional reserved bits. [NEEDS CLARIFICATION: Complete bit field definition for WDOGITOP?]
- We will assume only bits 0 and 1 are defined for wdogint and wdogres control, other bits reserved.

6. **APB Error Response**: Should device assert PSLVERR for invalid accesses (locked writes, write to RO registers)? [NEEDS CLARIFICATION: APB error signaling policy?]
- We will not assert PSLVERR for locked writes or writes to RO registers; such writes will be silently ignored.

7. **Counter Value on Disable**: When INTEN transitions 1→0, should counter value be preserved or reset? Current spec implies preservation. [NEEDS CLARIFICATION: Confirm counter behavior on disable?]
- We will preserve counter value when INTEN is cleared.

8. **Multiple Pending Interrupts**: If interrupt is not cleared and counter reaches 0 multiple times before reset, does each timeout generate new interrupt edge? [NEEDS CLARIFICATION: Interrupt re-assertion behavior?]
- We will assume interrupt is not re-asserted until cleared. We should assert reset in second timeout if interrupt asserted during first timout is not cleared.
