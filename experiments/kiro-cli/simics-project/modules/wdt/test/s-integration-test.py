# Integration Test Mode Tests
# Tests WDOGITCR and WDOGITOP registers for direct signal control

import dev_util
import simics
import conf
import stest
import wdt_common

def test_wdogitcr_enable_disable():
    """Test WDOGITCR enable/disable test mode (TEST-019)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Initially not in test mode
    stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x0, "Not in test mode initially")
    
    # Enable test mode
    regs.WDOGITCR.write(0x1)
    stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x1, "Test mode enabled")
    
    # Disable test mode
    regs.WDOGITCR.write(0x0)
    stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x0, "Test mode disabled")
    
    # Test multiple enable/disable cycles
    for i in range(3):
        regs.WDOGITCR.write(0x1)
        stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x1, f"Cycle {i}: test mode enabled")
        
        regs.WDOGITCR.write(0x0)
        stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x0, f"Cycle {i}: test mode disabled")
    
    print("WDOGITCR enable/disable test passed")

def test_wdogitop_direct_interrupt_control():
    """Test WDOGITOP direct control of wdogint (TEST-020)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Enable test mode
    regs.WDOGITCR.write(0x1)
    
    # Initially no signals
    stest.expect_equal(pic_int.raised, 0, "No interrupt initially")
    
    # Set interrupt via WDOGITOP (bit 1)
    regs.WDOGITOP.write(0x2)  # WDOGINT_VAL = 1
    stest.expect_equal(pic_int.raised, 1, "Interrupt raised via WDOGITOP")
    
    # Clear interrupt via WDOGITOP
    regs.WDOGITOP.write(0x0)  # WDOGINT_VAL = 0
    stest.expect_equal(pic_int.raised, 0, "Interrupt cleared via WDOGITOP")
    
    # Test multiple toggles
    for i in range(3):
        regs.WDOGITOP.write(0x2)
        stest.expect_equal(pic_int.raised, 1, f"Cycle {i}: interrupt set")
        
        regs.WDOGITOP.write(0x0)
        stest.expect_equal(pic_int.raised, 0, f"Cycle {i}: interrupt cleared")
    
    print("WDOGITOP direct interrupt control test passed")

def test_wdogitop_direct_reset_control():
    """Test WDOGITOP direct control of wdogres (TEST-021)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Enable test mode
    regs.WDOGITCR.write(0x1)
    
    # Initially no reset
    stest.expect_equal(pic_res.raised, 0, "No reset initially")
    
    # Set reset via WDOGITOP (bit 0)
    regs.WDOGITOP.write(0x1)  # WDOGRES_VAL = 1
    stest.expect_equal(pic_res.raised, 1, "Reset raised via WDOGITOP")
    
    # Clear reset via WDOGITOP
    regs.WDOGITOP.write(0x0)  # WDOGRES_VAL = 0
    stest.expect_equal(pic_res.raised, 0, "Reset cleared via WDOGITOP")
    
    # Test multiple toggles
    for i in range(3):
        regs.WDOGITOP.write(0x1)
        stest.expect_equal(pic_res.raised, 1, f"Cycle {i}: reset set")
        
        regs.WDOGITOP.write(0x0)
        stest.expect_equal(pic_res.raised, 0, f"Cycle {i}: reset cleared")
    
    print("WDOGITOP direct reset control test passed")

def test_wdogitop_combined_control():
    """Test WDOGITOP control of both signals simultaneously"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Enable test mode
    regs.WDOGITCR.write(0x1)
    
    # Test all combinations
    test_cases = [
        (0x0, 0, 0),  # Both off
        (0x1, 0, 1),  # Reset only
        (0x2, 1, 0),  # Interrupt only
        (0x3, 1, 1),  # Both on
    ]
    
    for val, exp_int, exp_res in test_cases:
        regs.WDOGITOP.write(val)
        stest.expect_equal(pic_int.raised, exp_int, f"Value 0x{val:x}: interrupt = {exp_int}")
        stest.expect_equal(pic_res.raised, exp_res, f"Value 0x{val:x}: reset = {exp_res}")
    
    print("WDOGITOP combined control test passed")

def test_normal_operation_suspension():
    """Test normal operation suspension in test mode (TEST-022)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Start normal timer operation
    regs.WDOGLOAD.write(100)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Let it run partially
    simics.SIM_continue(50)
    normal_value = regs.WDOGVALUE.read()
    stest.expect_true(normal_value < 100, "Timer running normally")
    
    # Enter test mode - should suspend normal operation
    regs.WDOGITCR.write(0x1)
    
    # Timer should not continue decrementing
    simics.SIM_continue(100)
    suspended_value = regs.WDOGVALUE.read()
    stest.expect_equal(suspended_value, normal_value, "Timer suspended in test mode")
    
    # Normal timeout should not occur
    stest.expect_equal(pic_int.raised, 0, "No normal timeout in test mode")
    
    print("Normal operation suspension test passed")

def test_normal_operation_resume():
    """Test normal operation resume when test mode disabled (TEST-023)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Start in test mode
    regs.WDOGITCR.write(0x1)
    regs.WDOGLOAD.write(200)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Timer should not run in test mode
    simics.SIM_continue(50)
    test_value = regs.WDOGVALUE.read()
    stest.expect_equal(test_value, 200, "Timer doesn't run in test mode")
    
    # Exit test mode - should resume normal operation
    regs.WDOGITCR.write(0x0)
    
    # Timer should now decrement
    simics.SIM_continue(50)
    resumed_value = regs.WDOGVALUE.read()
    stest.expect_true(resumed_value < test_value, "Timer resumes after test mode")
    
    # Should be able to timeout normally
    simics.SIM_continue(200)
    stest.expect_equal(pic_int.raised, 1, "Normal timeout works after test mode")
    
    print("Normal operation resume test passed")

def test_wdogitop_ignored_outside_test_mode():
    """Test WDOGITOP writes ignored when not in test mode"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Not in test mode
    stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x0, "Not in test mode")
    
    # Try to control signals via WDOGITOP - should be ignored
    regs.WDOGITOP.write(0x3)  # Try to set both signals
    stest.expect_equal(pic_int.raised, 0, "WDOGITOP ignored outside test mode (int)")
    stest.expect_equal(pic_res.raised, 0, "WDOGITOP ignored outside test mode (res)")
    
    # Multiple attempts should all be ignored
    for val in [0x1, 0x2, 0x3, 0x0]:
        regs.WDOGITOP.write(val)
        stest.expect_equal(pic_int.raised, 0, f"Value 0x{val:x} ignored (int)")
        stest.expect_equal(pic_res.raised, 0, f"Value 0x{val:x} ignored (res)")
    
    print("WDOGITOP ignored outside test mode test passed")

def test_test_mode_with_lock():
    """Test integration test mode interaction with lock"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Lock the device
    regs.WDOGLOCK.write(0x12345678)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1, "Device locked")
    
    # Try to enter test mode - should be ignored
    regs.WDOGITCR.write(0x1)
    stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x0, "Test mode blocked when locked")
    
    # Try WDOGITOP - should be ignored
    regs.WDOGITOP.write(0x3)
    stest.expect_equal(pic_int.raised, 0, "WDOGITOP blocked when locked")
    stest.expect_equal(pic_res.raised, 0, "WDOGITOP blocked when locked")
    
    # Unlock and try again
    regs.WDOGLOCK.write(0x1ACCE551)
    regs.WDOGITCR.write(0x1)
    stest.expect_equal(regs.WDOGITCR.read() & 0x1, 0x1, "Test mode works when unlocked")
    
    regs.WDOGITOP.write(0x3)
    stest.expect_equal(pic_int.raised, 1, "WDOGITOP works when unlocked")
    stest.expect_equal(pic_res.raised, 1, "WDOGITOP works when unlocked")
    
    print("Test mode with lock test passed")

# Run all tests
if __name__ == "__main__":
    test_wdogitcr_enable_disable()
    test_wdogitop_direct_interrupt_control()
    test_wdogitop_direct_reset_control()
    test_wdogitop_combined_control()
    test_normal_operation_suspension()
    test_normal_operation_resume()
    test_wdogitop_ignored_outside_test_mode()
    test_test_mode_with_lock()
    print("All integration test mode tests passed!")
