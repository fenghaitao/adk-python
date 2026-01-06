#!/usr/bin/env python3
# © 2025 Intel Corporation
# Test: Basic watchdog countdown and interrupt generation

import dev_util
import simics
import stest
import wdt_common

def run_all_tests():
    """Run all basic tests in sequence with single config"""
    # Create config once
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_wdogint = devs[1]
    fake_pic_wdogres = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.apb_interface)
    
    # Test 1: Initialization
    print("Test 1: Initialization")
    stest.expect_equal(regs.WDOGLOAD.read(), 0xFFFFFFFF, "WDOGLOAD reset value")
    stest.expect_equal(regs.WDOGVALUE.read(), 0xFFFFFFFF, "WDOGVALUE reset value")
    stest.expect_equal(regs.WDOGCONTROL.read(), 0x00000000, "WDOGCONTROL reset value")
    stest.expect_equal(regs.WDOGRIS.read(), 0x0, "WDOGRIS reset value")
    stest.expect_equal(regs.WDOGMIS.read(), 0x0, "WDOGMIS reset value")
    stest.expect_equal(regs.WDOGLOCK.read(), 0x00000000, "WDOGLOCK reset value (unlocked)")
    stest.expect_equal(fake_pic_wdogint.raised, 0, "wdogint de-asserted at reset")
    stest.expect_equal(fake_pic_wdogres.raised, 0, "wdogres de-asserted at reset")
    print("✓ Initialization test passed")
    
    # Test 2: Basic countdown
    print("\nTest 2: Basic countdown")
    regs.WDOGLOAD.write(1000)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1, step=÷1
    
    initial_value = regs.WDOGVALUE.read()
    stest.expect_equal(initial_value, 1000, "Counter starts at WDOGLOAD value")
    
    simics.SIM_continue(100)
    
    value_after = regs.WDOGVALUE.read()
    stest.expect_true(value_after < initial_value, "Counter decrements")
    stest.expect_equal(value_after, 900, "Counter decrements by 100 cycles")
    print("✓ Basic countdown test passed")
    
    # Test 3: Interrupt generation
    print("\nTest 3: Interrupt generation")
    # Reset by disabling and re-enabling
    regs.WDOGCONTROL.write(0x0)
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1, step=÷1
    
    simics.SIM_continue(60)
    
    stest.expect_equal(regs.WDOGRIS.read(), 0x1, "WDOGRIS[0] set on timeout")
    stest.expect_equal(regs.WDOGMIS.read(), 0x1, "WDOGMIS[0] set on timeout")
    stest.expect_equal(fake_pic_wdogint.raised, 1, "wdogint asserted")
    print("✓ Interrupt generation test passed")
    
    # Test 4: Interrupt clear
    print("\nTest 4: Interrupt clear")
    regs.WDOGINTCLR.write(0x1)
    
    stest.expect_equal(regs.WDOGRIS.read(), 0x0, "WDOGRIS cleared")
    stest.expect_equal(fake_pic_wdogint.raised, 0, "wdogint de-asserted")
    
    counter_value = regs.WDOGVALUE.read()
    stest.expect_equal(counter_value, 50, "Counter reloaded from WDOGLOAD")
    print("✓ Interrupt clear test passed")
    
    # Test 5: INTEN disable behavior
    print("\nTest 5: INTEN disable")
    # Clear any previous state
    regs.WDOGCONTROL.write(0x0)  # Ensure INTEN=0
    regs.WDOGLOAD.write(1000)
    
    # Enable and verify counter starts
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    value_at_start = regs.WDOGVALUE.read()
    print(f"  Counter at start: {value_at_start}")
    stest.expect_equal(value_at_start, 1000, "Counter starts at 1000")
    
    # Run 100 cycles
    simics.SIM_continue(100)
    value_before_disable = regs.WDOGVALUE.read()
    print(f"  Counter after 100 cycles: {value_before_disable}")
    stest.expect_equal(value_before_disable, 900, "Counter decremented to 900")
    
    # Disable timer
    regs.WDOGCONTROL.write(0x0)  # INTEN=0
    value_right_after_disable = regs.WDOGVALUE.read()
    print(f"  Counter right after disable: {value_right_after_disable}")
    
    # Run more cycles - counter should stay frozen
    simics.SIM_continue(100)
    value_after = regs.WDOGVALUE.read()
    print(f"  Counter after 100 more cycles (disabled): {value_after}")
    
    stest.expect_equal(value_after, value_before_disable, "Counter frozen when INTEN=0")
    print("✓ INTEN disable test passed")

if __name__ == "__main__":
    run_all_tests()
    print("\n✅ All basic countdown tests passed!")
