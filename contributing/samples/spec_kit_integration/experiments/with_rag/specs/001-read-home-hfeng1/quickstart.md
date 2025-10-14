# Quick Start: Simics Watchdog Timer Model

## Goal
This guide will help you validate that the Simics Watchdog Timer model is correctly implemented and functioning as specified, generating interrupts and resets based on timer timeouts.

## Prerequisites
- Simics Base 7.57.0 or later
- Python 7.13.0 or later
- QSP-x86 7.38.0 platform or compatible simulation target
- Completed implementation of the watchdog timer device model

## Validation Steps

### Step 1: Basic Timer Interrupt Generation
Configure the watchdog timer to generate an interrupt when it times out.

**What to do**:
1. Create a Simics configuration with the watchdog timer device
2. Set the WDOGLOAD register to a known value (e.g., 1000)
3. Enable interrupt generation by setting the int_en bit in WDOGCONTROL
4. Start the timer and wait for it to count down to zero

**Expected Result**: 
- An interrupt signal (wdogint) should be generated when the counter reaches zero
- The WDOGRIS register should indicate a raw interrupt status
- The WDOGMIS register should indicate a masked interrupt status (if interrupts enabled)

**Success Criteria**: 
- WDOGRIS register shows interrupt pending
- WDOGMIS register shows interrupt pending (when int_en = 1)
- Interrupt signal is asserted in the simulation

### Step 2: Timer Reset Generation
Configure the watchdog timer to generate a reset on the second timeout.

**What to do**:
1. Configure the watchdog timer with interrupt and reset enabled
2. Allow the timer to timeout once (interrupt should be generated)
3. Do not clear the interrupt
4. Allow the timer to timeout a second time

**Expected Result**:
- A reset signal (wdogres) should be generated on the second timeout
- The system should be reset as a result of the reset signal

**Success Criteria**:
- WDOGRESET signal is asserted in the simulation
- System state is reset as expected

### Step 3: Register Protection Mechanism
Verify that the register lock mechanism protects registers from unauthorized access.

**What to do**:
1. Ensure the watchdog timer is in the locked state (default)
2. Attempt to write to a protected register (e.g., WDOGLOAD)
3. Unlock the registers by writing the unlock key to WDOGLOCK
4. Successfully write to the previously protected register

**Expected Result**:
- Write attempts to protected registers should be ignored when locked
- Write attempts should succeed when unlocked
- Registers should be protected again after re-locking

**Success Criteria**:
- Protected register writes fail when locked (return error or are ignored)
- Protected register writes succeed when unlocked
- WDOGLOCK register correctly reports lock status

### Step 4: Integration Test Mode
Verify that the integration test mode allows direct control of output signals.

**What to do**:
1. Enable integration test mode by writing to WDOGITCR
2. Set the interrupt output directly using WDOGITOP
3. Set the reset output directly using WDOGITOP

**Expected Result**:
- Direct control of output signals should be possible in test mode
- Normal timer operation should be suspended during test mode

**Success Criteria**:
- Interrupt and reset signals can be directly controlled via registers
- Timer counting is suspended during integration test mode

## Troubleshooting
- **Timer not generating interrupts**: Check that interrupt enable bit is set in WDOGCONTROL and that the timer is properly configured
- **Timer not generating resets**: Verify that both interrupt and reset enable bits are set, and that an interrupt occurred without being cleared
- **Register protection not working**: Ensure the lock mechanism is properly implemented and that WDOGLOCK register functions correctly
- **Integration test mode not working**: Verify that WDOGITCR and WDOGITOP registers are correctly implemented

## Next Steps
- Review the detailed register specifications in data-model.md
- Examine the API contracts in the contracts/ directory
- Execute the comprehensive test suite referenced in tasks.md
- Integrate the watchdog timer with other system components for full system testing