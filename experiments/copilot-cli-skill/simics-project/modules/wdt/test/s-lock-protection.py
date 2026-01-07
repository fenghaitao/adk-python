#!/usr/bin/env python3
"""
Lock Protection Tests (TEST-010, TEST-011, TEST-012)
Tests lock mechanism, unlock with magic value, and WDOGINTCLR bypass
"""

import simics
import stest
import dev_util
import wdt_common

def test_lock_prevents_writes(dev):
    """TEST-010: Verify lock protection prevents register writes"""
    print("\n=== TEST-010: Lock Prevents Writes ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Set initial values
    regs.WDOGLOAD.write(100)
    regs.WDOGCONTROL.write(0x0)
    
    # Lock device (write non-magic value)
    regs.WDOGLOCK.write(1)
    lock_status = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status, 1, "WDOGLOCK should read as 1 when locked")
    
    # Attempt to write protected registers
    load_before = regs.WDOGLOAD.read()
    ctrl_before = regs.WDOGCONTROL.read()
    
    regs.WDOGLOAD.write(500)
    regs.WDOGCONTROL.write(0x3)
    
    # Verify writes were ignored
    load_after = regs.WDOGLOAD.read()
    ctrl_after = regs.WDOGCONTROL.read()
    
    stest.expect_equal(load_after, load_before,
                      f"WDOGLOAD write should be ignored when locked: before={load_before}, after={load_after}")
    stest.expect_equal(ctrl_after, ctrl_before,
                      f"WDOGCONTROL write should be ignored when locked: before={ctrl_before}, after={ctrl_after}")
    
    print(f"[PASS] Lock prevents writes: WDOGLOAD={load_after}, WDOGCONTROL={ctrl_after}")

def test_unlock_with_magic_value(dev):
    """TEST-011: Verify unlock with magic value"""
    print("\n=== TEST-011: Unlock with Magic Value ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Lock device
    regs.WDOGLOCK.write(1)
    stest.expect_equal(regs.WDOGLOCK.read(), 1, "Device should be locked")
    
    # Unlock with magic value 0x1ACCE551
    regs.WDOGLOCK.write(0x1ACCE551)
    lock_status = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status, 0, "WDOGLOCK should read as 0 when unlocked")
    
    # Now writes should succeed
    regs.WDOGLOAD.write(500)
    load_value = regs.WDOGLOAD.read()
    stest.expect_equal(load_value, 500, "WDOGLOAD write should succeed when unlocked")
    
    print(f"[PASS] Device unlocked with magic value, WDOGLOAD write succeeded: {load_value}")

def test_wdogintclr_works_when_locked(dev, fake_pic_int):
    """TEST-012: Verify WDOGINTCLR works regardless of lock state"""
    print("\n=== TEST-012: WDOGINTCLR Works When Locked ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Trigger interrupt while unlocked
    regs.WDOGLOAD.write(20)
    regs.WDOGCONTROL.write(0x1)
    simics.SIM_continue(30)
    
    # Verify interrupt set
    ris_before = regs.WDOGRIS.read()
    stest.expect_equal(ris_before & 0x1, 1, "Interrupt should be set")
    
    raised_before = fake_pic_int.raised
    
    # Lock device
    regs.WDOGLOCK.write(1)
    stest.expect_equal(regs.WDOGLOCK.read(), 1, "Device should be locked")
    
    # Clear interrupt while locked - should work
    regs.WDOGINTCLR.write(1)
    
    # Verify interrupt cleared
    ris_after = regs.WDOGRIS.read()
    stest.expect_equal(ris_after & 0x1, 0, "WDOGRIS[0] should be 0 after clear (even when locked)")
    
    # Signal should be lowered
    raised_after = fake_pic_int.raised
    stest.expect_equal(raised_after, raised_before - 1,
                      f"Signal should be lowered: before={raised_before}, after={raised_after}")
    
    # Counter should be reloaded
    counter_value = regs.WDOGVALUE.read()
    load_value = regs.WDOGLOAD.read()
    stest.expect_equal(counter_value, load_value,
                      f"Counter should reload even when locked: counter={counter_value}, load={load_value}")
    
    print(f"[PASS] WDOGINTCLR works when locked: interrupt cleared, counter reloaded to {counter_value}")

def test_lock_protection_suite():
    """Main test entry point"""
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    
    # Run tests
    test_lock_prevents_writes(dev)
    test_unlock_with_magic_value(dev)
    test_wdogintclr_works_when_locked(dev, fake_pic_int)
    
    print("\n=== ALL LOCK PROTECTION TESTS PASSED ===\n")

if __name__ == "__main__":
    test_lock_protection_suite()
