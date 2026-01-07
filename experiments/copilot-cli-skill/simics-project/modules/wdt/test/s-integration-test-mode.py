#!/usr/bin/env python3
"""
Integration Test Mode Tests (TEST-013, TEST-014, TEST-015)
Tests integration test mode entry/exit and direct output control
"""

import simics
import stest
import dev_util
import wdt_common

def test_integration_test_mode_entry(dev):
    """TEST-013: Verify integration test mode entry"""
    print("\n=== TEST-013: Integration Test Mode Entry ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Unlock device (test mode requires unlock)
    regs.WDOGLOCK.write(0x1ACCE551)
    
    # Enter test mode
    regs.WDOGITCR.write(0x1)  # ITCR=1
    itcr = regs.WDOGITCR.read()
    stest.expect_equal(itcr & 0x1, 1, "WDOGITCR[0] should be 1 in test mode")
    
    # Start counter
    regs.WDOGLOAD.write(100)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Save counter value
    value_before = regs.WDOGVALUE.read()
    
    # Advance simulation - counter should NOT decrement in test mode
    simics.SIM_continue(50)
    
    value_after = regs.WDOGVALUE.read()
    stest.expect_equal(value_after, value_before,
                      f"Counter should not decrement in test mode: before={value_before}, after={value_after}")
    
    print(f"[PASS] Integration test mode entered: counter static at {value_after}")

def test_direct_output_control(dev, fake_pic_int, fake_pic_res):
    """TEST-014: Verify direct output control in test mode"""
    print("\n=== TEST-014: Direct Output Control ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Ensure in test mode
    regs.WDOGLOCK.write(0x1ACCE551)
    regs.WDOGITCR.write(0x1)
    
    # Initially, both outputs should be low (raised count = 0)
    int_count_initial = fake_pic_int.raised
    res_count_initial = fake_pic_res.raised
    
    # Set interrupt output high, reset low
    regs.WDOGITOP.write(0x1)  # WDOGINT=1, WDOGRES=0
    
    # Check interrupt asserted (raised count increases)
    int_count_after_set = fake_pic_int.raised
    stest.expect_equal(int_count_after_set, int_count_initial + 1,
                     f"Interrupt should be asserted: before={int_count_initial}, after={int_count_after_set}")
    
    # Reset is lowered from 0, so count becomes -1
    res_count_after_lower = fake_pic_res.raised
    stest.expect_equal(res_count_after_lower, res_count_initial - 1,
                      f"Reset should be lowered: before={res_count_initial}, after={res_count_after_lower}")
    
    # Set reset output high, interrupt low
    regs.WDOGITOP.write(0x2)  # WDOGINT=0, WDOGRES=1
    
    # Check interrupt lowered
    int_count_after_clear = fake_pic_int.raised
    stest.expect_equal(int_count_after_clear, int_count_after_set - 1,
                      f"Interrupt should be lowered: before={int_count_after_set}, after={int_count_after_clear}")
    
    # Check reset asserted (raised from -1 to 0)
    res_count_after_set = fake_pic_res.raised
    stest.expect_equal(res_count_after_set, res_count_after_lower + 1,
                     f"Reset should be asserted: before={res_count_after_lower}, after={res_count_after_set}")
    
    print(f"[PASS] Direct output control works: INT={int_count_after_clear}, RES={res_count_after_set}")

def test_test_mode_exit(dev):
    """TEST-015: Verify test mode exit resumes normal operation"""
    print("\n=== TEST-015: Test Mode Exit ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Enter test mode
    regs.WDOGLOCK.write(0x1ACCE551)
    regs.WDOGITCR.write(0x1)
    
    # Setup timer
    regs.WDOGLOAD.write(100)
    regs.WDOGCONTROL.write(0x1)
    
    # Verify counter static in test mode
    value_in_test = regs.WDOGVALUE.read()
    simics.SIM_continue(20)
    stest.expect_equal(regs.WDOGVALUE.read(), value_in_test,
                      "Counter should be static in test mode")
    
    # Exit test mode
    regs.WDOGITCR.write(0x0)  # ITCR=0
    itcr = regs.WDOGITCR.read()
    stest.expect_equal(itcr & 0x1, 0, "WDOGITCR[0] should be 0 after exit")
    
    # Counter should now decrement normally
    value_before = regs.WDOGVALUE.read()
    simics.SIM_continue(30)
    value_after = regs.WDOGVALUE.read()
    
    stest.expect_true(value_after < value_before,
                     f"Counter should decrement after test mode exit: before={value_before}, after={value_after}")
    
    print(f"[PASS] Normal operation resumed after test mode exit: {value_before} -> {value_after}")

def test_integration_test_mode_suite():
    """Main test entry point"""
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    fake_pic_res = devs[2]
    
    # Run tests
    test_integration_test_mode_entry(dev)
    test_direct_output_control(dev, fake_pic_int, fake_pic_res)
    test_test_mode_exit(dev)
    
    print("\n=== ALL INTEGRATION TEST MODE TESTS PASSED ===\n")

if __name__ == "__main__":
    test_integration_test_mode_suite()
