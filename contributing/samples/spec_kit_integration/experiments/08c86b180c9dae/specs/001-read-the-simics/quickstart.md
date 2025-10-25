# Quick Start: Simics Watchdog Timer Device Implementation

## Goal
Implement and validate a Simics watchdog timer device compatible with ARM PrimeCell specification that can monitor system health by generating interrupts and resets when the system fails to respond within a configured time period.

## Prerequisites
- Simics Base 7.57.0
- Required packages: simics-base, simics-qsp-x86
- Available platform: Public Intel® Simics® Quick Start Platform (QSP-x86) - 7

## Validation Steps

### Step 1: Configure Watchdog Timer with Interrupt Generation
**What to do**:
1. Create a Simics project with QSP-x86 platform
2. Add the watchdog timer device to the memory map at address 0x1000
3. Configure the timer with a short timeout period and enable interrupt generation
4. Start the timer and wait for timeout

**Expected Result**:
The watchdog timer should generate an interrupt when the countdown reaches zero.

**Success Criteria**:
- Interrupt output signal is asserted
- WDOGRIS register shows interrupt pending
- WDOGMIS register shows masked interrupt pending when INTEN=1

### Step 2: Test Lock Protection Mechanism
**What to do**:
1. Attempt to write to a protected register (e.g., WDOGCONTROL) without unlocking
2. Verify the write is rejected
3. Unlock the registers using the magic value 0x1ACCE551
4. Attempt the write operation again

**Expected Result**:
Write operations should be rejected when locked and accepted when unlocked.

**Success Criteria**:
- Register values remain unchanged when locked
- Register values update correctly when unlocked
- WDOGLOCK register reflects the current lock status

### Step 3: Validate Reset Generation on Second Timeout
**What to do**:
1. Configure the watchdog timer with reset enabled but interrupt enabled
2. Start the timer and let it timeout (generates interrupt)
3. Do not clear the interrupt
4. Let the timer timeout again

**Expected Result**:
The watchdog timer should generate a system reset on the second timeout since the interrupt was not cleared.

**Success Criteria**:
- Reset output signal is asserted on second timeout
- System reset is triggered when RESEN=1 and interrupt was not cleared

### Step 4: Verify Integration Test Mode
**What to do**:
1. Enable integration test mode using WDOGITCR register
2. Set direct control values using WDOGITOP register
3. Verify interrupt and reset outputs follow the direct control values

**Expected Result**:
In integration test mode, the outputs should be directly controlled by the test registers rather than timer behavior.

**Success Criteria**:
- Outputs follow WDOGITOP register values when test mode is enabled
- Normal timer behavior is suspended during test mode
- Outputs return to normal behavior when test mode is disabled

## Troubleshooting
- If interrupts are not generated, verify INTEN bit is set in WDOGCONTROL
- If resets are not generated, verify RESEN bit is set and interrupt was not cleared
- If register writes are rejected, ensure WDOGLOCK is unlocked with 0x1ACCE551
- If timer does not count down, verify ENABLE bit is set and clock is connected

## Next Steps
- Review the detailed register specifications in data-model.md
- Examine the register access contracts in contracts/register-access.md
- Study the interface behavior specifications in contracts/interface-behavior.md
- Run `/tasks` to generate actionable implementation tasks