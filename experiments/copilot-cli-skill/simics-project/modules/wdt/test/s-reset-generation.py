#!/usr/bin/env python3
"""
Reset Generation Tests (TEST-007, TEST-008, TEST-009)
Tests reset signal generation on second timeout and prevention mechanisms
"""

import simics
import stest
import dev_util
import wdt_common

def test_reset_on_second_timeout(dev, fake_pic_res):
    """TEST-007: Verify reset generation on second timeout"""
    print("\n=== TEST-007: Reset on Second Timeout ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Enable timer with reset enabled
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1
    
    # Wait for first timeout (interrupt generated)
    simics.SIM_continue(60)
    
    ris = regs.WDOGRIS.read()
    stest.expect_equal(ris & 0x1, 1, "Interrupt should be set after first timeout")
    
    # Do NOT clear interrupt - wait for second timeout
    simics.SIM_continue(60)
    
    # Check reset signal asserted
    stest.expect_true(fake_pic_res.raised > 0,
                     f"Reset signal should be asserted, count={fake_pic_res.raised}")
    
    print(f"[PASS] Reset generated on second timeout: reset_signal_count={fake_pic_res.raised}")

def test_no_reset_when_resen_disabled(dev, fake_pic_res):
    """TEST-008: Verify no reset when RESEN=0"""
    print("\n=== TEST-008: No Reset When RESEN=0 ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Enable timer with reset DISABLED
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1, RESEN=0
    
    # Wait for first timeout
    simics.SIM_continue(60)
    
    ris = regs.WDOGRIS.read()
    stest.expect_equal(ris & 0x1, 1, "Interrupt should be set after first timeout")
    
    reset_count_before = fake_pic_res.raised
    
    # Wait for second timeout
    simics.SIM_continue(60)
    
    # Reset signal should NOT be asserted
    reset_count_after = fake_pic_res.raised
    stest.expect_equal(reset_count_after, reset_count_before,
                      f"Reset signal should not be asserted when RESEN=0: before={reset_count_before}, after={reset_count_after}")
    
    print(f"[PASS] No reset generated when RESEN=0")

def test_reset_prevented_by_interrupt_clear(dev, fake_pic_res):
    """TEST-009: Verify reset prevented by interrupt clear"""
    print("\n=== TEST-009: Reset Prevented by Interrupt Clear ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Enable timer with reset enabled
    regs.WDOGLOAD.write(30)
    regs.WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1
    
    # Wait for first timeout
    simics.SIM_continue(40)
    
    ris = regs.WDOGRIS.read()
    stest.expect_equal(ris & 0x1, 1, "Interrupt should be set after first timeout")
    
    reset_count_before = fake_pic_res.raised
    
    # Clear interrupt BEFORE second timeout
    regs.WDOGINTCLR.write(1)
    
    # Wait for what would have been second timeout
    simics.SIM_continue(40)
    
    # Reset signal should NOT be asserted because interrupt was cleared
    reset_count_after = fake_pic_res.raised
    stest.expect_equal(reset_count_after, reset_count_before,
                      f"Reset should be prevented by interrupt clear: before={reset_count_before}, after={reset_count_after}")
    
    print(f"[PASS] Reset prevented by clearing interrupt before second timeout")

def test_reset_generation_suite():
    """Main test entry point"""
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    fake_pic_res = devs[2]
    
    # Run tests
    test_reset_on_second_timeout(dev, fake_pic_res)
    test_no_reset_when_resen_disabled(dev, fake_pic_res)
    test_reset_prevented_by_interrupt_clear(dev, fake_pic_res)
    
    print("\n=== ALL RESET GENERATION TESTS PASSED ===\n")

if __name__ == "__main__":
    test_reset_generation_suite()
