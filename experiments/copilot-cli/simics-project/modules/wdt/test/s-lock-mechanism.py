#!/usr/bin/env python3
# © 2025 Intel Corporation
# Test: Watchdog lock mechanism

import dev_util
import simics
import stest
import wdt_common

def run_lock_tests():
    """Test lock protection mechanism"""
    devs = wdt_common.create_config()
    dev = devs[0]
    regs = dev_util.bank_regs(dev.bank.apb_interface)
    
    # Test 1: Device starts unlocked
    print("Test 1: Initial unlocked state")
    stest.expect_equal(regs.WDOGLOCK.read(), 0x00000000, "Device unlocked at reset")
    
    # Verify writes work when unlocked
    regs.WDOGLOAD.write(0x12345678)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x12345678, "WDOGLOAD writable when unlocked")
    print("✓ Initial unlocked state test passed")
    
    # Test 2: Lock device
    print("\nTest 2: Lock device")
    regs.WDOGLOCK.write(0xDEADBEEF)  # Any value except magic locks
    stest.expect_equal(regs.WDOGLOCK.read(), 0x00000001, "Device locked (reads 0x1)")
    
    # Try to write protected registers - should be ignored
    regs.WDOGLOAD.write(0xABCDEF00)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x12345678, "WDOGLOAD write ignored when locked")
    
    regs.WDOGCONTROL.write(0xFF)
    stest.expect_equal(regs.WDOGCONTROL.read(), 0x00, "WDOGCONTROL write ignored when locked")
    print("✓ Lock device test passed")
    
    # Test 3: Unlock with magic value
    print("\nTest 3: Unlock device")
    regs.WDOGLOCK.write(0x1ACCE551)  # Magic unlock value
    stest.expect_equal(regs.WDOGLOCK.read(), 0x00000000, "Device unlocked (reads 0x0)")
    
    # Verify writes work again
    regs.WDOGLOAD.write(0x99999999)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x99999999, "WDOGLOAD writable after unlock")
    print("✓ Unlock device test passed")
    
    # Test 4: Lock state survives register access
    print("\nTest 4: Lock persistence")
    regs.WDOGLOCK.write(0x1)  # Lock again
    
    # Try multiple register accesses
    regs.WDOGLOAD.write(0x11111111)
    regs.WDOGCONTROL.write(0x1)
    regs.WDOGINTCLR.write(0x1)
    
    # All should be ignored
    stest.expect_equal(regs.WDOGLOAD.read(), 0x99999999, "Lock persists across accesses")
    stest.expect_equal(regs.WDOGCONTROL.read(), 0x0, "WDOGCONTROL still protected")
    print("✓ Lock persistence test passed")
    
    # Test 5: Lock does not affect interrupt state
    print("\nTest 5: Interrupt state survives lock")
    # Unlock, start timer, generate interrupt
    regs.WDOGLOCK.write(0x1ACCE551)
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x1)
    simics.SIM_continue(60)
    
    stest.expect_equal(regs.WDOGRIS.read(), 0x1, "Interrupt generated")
    
    # Lock device
    regs.WDOGLOCK.write(0x1)
    
    # Interrupt state should survive
    stest.expect_equal(regs.WDOGRIS.read(), 0x1, "Interrupt state survives lock")
    
    # But can't clear interrupt while locked
    regs.WDOGINTCLR.write(0x1)
    stest.expect_equal(regs.WDOGRIS.read(), 0x1, "Cannot clear interrupt when locked")
    print("✓ Interrupt state survives lock test passed")

if __name__ == "__main__":
    run_lock_tests()
    print("\n✅ All lock mechanism tests passed!")
