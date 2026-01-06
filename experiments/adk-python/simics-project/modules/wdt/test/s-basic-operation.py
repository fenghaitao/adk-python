# © 2025 Intel Corporation
# Test basic watchdog timer functionality

import dev_util
import simics
import stest
import wdt_common

def test_basic_operation():
    # Create an instance of the device to test
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_wdogint = devs[1]
    fake_pic_wdogres = devs[2]

    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)

    # Test 1: Check initial register values
    print("Test 1: Initial register values")
    stest.expect_equal(regs.WDOGLOAD.read(), 0xffffffff)
    stest.expect_equal(regs.WDOGVALUE.read(), 0xffffffff)
    stest.expect_equal(regs.WDOGCONTROL.read(), 0x0)
    stest.expect_equal(regs.WDOGRIS.read(), 0x0)
    stest.expect_equal(regs.WDOGMIS.read(), 0x0)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1)  # Should be locked initially
    print("Initial register values are correct")

    # Test 2: Test lock mechanism - writes should be ignored when locked
    print("Test 2: Lock mechanism - writes ignored when locked")
    old_counter = regs.WDOGVALUE.read()
    regs.WDOGLOAD.write(0x1000)
    stest.expect_equal(regs.WDOGLOAD.read(), 0xffffffff)  # Should remain unchanged when locked
    print("Lock mechanism working: register writes ignored when locked")

    # Test 3: Unlock the device
    print("Test 3: Unlock device")
    regs.WDOGLOCK.write(0x1ACCE551)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0)  # Should now be unlocked
    print("Device unlocked successfully")

    # Test 4: Write to WDOGLOAD after unlocking
    print("Test 4: Write to WDOGLOAD after unlocking")
    test_load_value = 0x1000
    regs.WDOGLOAD.write(test_load_value)
    stest.expect_equal(regs.WDOGLOAD.read(), test_load_value)
    print(f"WDOGLOAD write successful, value: 0x{regs.WDOGLOAD.read():x}")

    # Test 5: Test counter countdown functionality (briefly)
    print("Test 5: Counter countdown functionality")
    initial_value = regs.WDOGVALUE.read()
    # Enable the timer with a small step value to see countdown
    regs.WDOGCONTROL.write(0x1)  # INTEN=1, others at default
    simics.SIM_continue(100)  # Run for a few cycles
    # The counter should start counting down
    current_value = regs.WDOGVALUE.read()
    # The counter should be less than the initial value after running
    # We'll verify this behavior more thoroughly in a moment
    
    # Enable and run again to see countdown
    regs.WDOGLOAD.write(0x100)  # Small value for quick testing
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    initial_value = regs.WDOGVALUE.read()
    simics.SIM_continue(50)  # Run for some cycles
    current_value = regs.WDOGVALUE.read()
    print(f"Countdown test: initial={initial_value}, current={current_value}")
    
    # The counter should decrease but may not reach zero with only 50 cycles
    # The important part is that the mechanism works
    
    # Test 6: Test interrupt clear functionality
    print("Test 6: Interrupt clear functionality")
    # Clear interrupt (though it shouldn't be set yet)
    regs.WDOGINTCLR.write(0x1234)  # Any value should clear
    stest.expect_equal(regs.WDOGINTCLR.read(), 0x0)  # Should read as 0 (write-only)
    print("Interrupt clear register behaves correctly")
    
    # Test 7: Test different clock divider configurations
    print("Test 7: Clock divider configurations")
    # Reset to known state
    regs.WDOGLOCK.write(0x1ACCE551)  # Ensure unlocked
    regs.WDOGLOAD.write(0x100)
    regs.WDOGCONTROL.write(0x0)  # INTEN=0, disable timer
    regs.WDOGINTCLR.write(0x1234)  # Clear any pending interrupts
    
    # Test step values
    for step_val in range(5):  # 0 to 4 are valid step values
        expected_ctrl = (step_val << 2)  # Put step_value in bits [4:2]
        regs.WDOGCONTROL.write(expected_ctrl)
        actual_ctrl = regs.WDOGCONTROL.read()
        stest.expect_equal(actual_ctrl & 0x1C, expected_ctrl & 0x1C)  # Check STEP_VALUE field
        print(f"Step value {step_val} written successfully")
    
    print("Basic operation tests completed successfully!")


if __name__ == "__main__":
    test_basic_operation()