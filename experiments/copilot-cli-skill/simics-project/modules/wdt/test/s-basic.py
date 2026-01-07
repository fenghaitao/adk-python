#!/usr/bin/env python3
"""
Basic watchdog timer tests
Tests timer countdown, interrupt generation, and basic operations
"""

import simics
import stest
import dev_util
import wdt_common

# Test: Basic timer countdown and interrupt
def test_basic_countdown(dev, fake_pic_int, fake_pic_res):
    """Test that timer counts down and generates interrupt"""
    # Get register bank
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Write load value
    regs.WDOGLOAD.write(100)
    
    # Enable timer (INTEN=1)
    regs.WDOGCONTROL.write(0x1)
    
    # Advance simulation partway through countdown
    simics.SIM_continue(50)
    
    # Check counter has decremented
    value = regs.WDOGVALUE.read()
    stest.expect_true(value < 100 and value > 0, 
                     f"Counter should be between 0 and 100, got {value}")
    
    # Advance past timeout
    simics.SIM_continue(60)
    
    # Check interrupt generated
    ris = regs.WDOGRIS.read()
    stest.expect_equal(ris & 0x1, 1, "WDOGRIS[0] should be 1 after timeout")
    
    # Check interrupt signal raised
    stest.expect_true(fake_pic_int.raised > 0, 
                     f"Interrupt should be raised, count={fake_pic_int.raised}")
    
    print("[PASS] Basic countdown test")

# Test: Interrupt clear
def test_interrupt_clear(dev):
    """Test that WDOGINTCLR clears interrupt"""
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: trigger interrupt
    regs.WDOGLOAD.write(20)
    regs.WDOGCONTROL.write(0x1)
    simics.SIM_continue(30)
    
    # Verify interrupt set
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 1, "Interrupt should be set")
    
    # Clear interrupt
    regs.WDOGINTCLR.write(1)
    
    # Verify interrupt cleared
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0, "Interrupt should be cleared")
    
    print("[PASS] Interrupt clear test")

# Test: Lock protection
def test_lock_protection(dev):
    """Test that lock mechanism protects registers"""
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Lock device
    regs.WDOGLOCK.write(1)
    stest.expect_equal(regs.WDOGLOCK.read(), 1, "Device should be locked")
    
    # Try to write WDOGLOAD (should be ignored)
    old_value = regs.WDOGLOAD.read()
    regs.WDOGLOAD.write(500)
    value = regs.WDOGLOAD.read()
    stest.expect_equal(value, old_value, f"Write should be ignored when locked")
    
    # Unlock with magic value
    regs.WDOGLOCK.write(0x1ACCE551)
    stest.expect_equal(regs.WDOGLOCK.read(), 0, "Device should be unlocked")
    
    # Now write should succeed
    regs.WDOGLOAD.write(500)
    stest.expect_equal(regs.WDOGLOAD.read(), 500, "Write should succeed when unlocked")
    
    print("[PASS] Lock protection test")

# Main test runner
def test_basic():
    """Main test entry point"""
    # Create device configuration using wdt_common
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    fake_pic_res = devs[2]
    
    # Run tests
    test_basic_countdown(dev, fake_pic_int, fake_pic_res)
    test_interrupt_clear(dev)
    test_lock_protection(dev)
    
    print("\n=== ALL BASIC TESTS PASSED ===\n")

# Entry point for test runner
if __name__ == "__main__":
    test_basic()
