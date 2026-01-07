#!/usr/bin/env python3
"""
Countdown Timer Tests (TEST-001, TEST-002, TEST-003)
Tests basic counter decrement, value persistence when disabled, and reload behavior
"""

import simics
import stest
import dev_util
import wdt_common

def test_counter_decrement(dev):
    """TEST-001: Verify counter decrements when enabled"""
    print("\n=== TEST-001: Counter Decrement ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Write load value and enable timer
    regs.WDOGLOAD.write(1000)
    initial_value = regs.WDOGVALUE.read()
    stest.expect_equal(initial_value, 1000, "Initial counter value should equal WDOGLOAD")
    
    # Enable timer
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Advance simulation
    simics.SIM_continue(100)
    
    # Check counter decremented
    value_after = regs.WDOGVALUE.read()
    stest.expect_true(value_after < initial_value, 
                     f"Counter should decrement: initial={initial_value}, after={value_after}")
    stest.expect_true(value_after > 0, f"Counter should not reach zero yet: {value_after}")
    
    print(f"[PASS] Counter decremented from {initial_value} to {value_after}")

def test_counter_disabled_persistence(dev):
    """TEST-002: Verify counter value persists when INTEN=0"""
    print("\n=== TEST-002: Counter Disabled Persistence ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Enable timer and let it count
    regs.WDOGLOAD.write(500)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    simics.SIM_continue(50)
    
    # Save current value and disable
    value_before_disable = regs.WDOGVALUE.read()
    regs.WDOGCONTROL.write(0x0)  # INTEN=0
    
    # Advance simulation - counter should not change
    simics.SIM_continue(100)
    
    value_after_disable = regs.WDOGVALUE.read()
    stest.expect_equal(value_after_disable, value_before_disable,
                      f"Counter should not change when disabled: before={value_before_disable}, after={value_after_disable}")
    
    print(f"[PASS] Counter value persisted at {value_after_disable} when disabled")

def test_wdogload_reload(dev):
    """TEST-003: Verify WDOGLOAD write reloads counter immediately"""
    print("\n=== TEST-003: WDOGLOAD Reload ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Enable timer and let it count down
    regs.WDOGLOAD.write(1000)
    regs.WDOGCONTROL.write(0x1)
    simics.SIM_continue(500)
    
    # Counter should be around 500
    value_mid = regs.WDOGVALUE.read()
    stest.expect_true(value_mid < 1000 and value_mid > 0,
                     f"Counter should be mid-countdown: {value_mid}")
    
    # Write new load value
    regs.WDOGLOAD.write(2000)
    
    # Counter should immediately reload
    value_reloaded = regs.WDOGVALUE.read()
    stest.expect_equal(value_reloaded, 2000,
                      f"Counter should immediately reload to 2000, got {value_reloaded}")
    
    # Continue and verify counting from new value
    simics.SIM_continue(100)
    value_after = regs.WDOGVALUE.read()
    stest.expect_true(value_after < 2000 and value_after > 1800,
                     f"Counter should count from 2000: got {value_after}")
    
    print(f"[PASS] Counter reloaded from {value_mid} to {value_reloaded}, now at {value_after}")

def test_countdown_timer():
    """Main test entry point"""
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    
    # Run tests
    test_counter_decrement(dev)
    test_counter_disabled_persistence(dev)
    test_wdogload_reload(dev)
    
    print("\n=== ALL COUNTDOWN TIMER TESTS PASSED ===\n")

if __name__ == "__main__":
    test_countdown_timer()
