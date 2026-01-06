# Lock Protection Tests
# Tests the lock mechanism that prevents unauthorized modification

import dev_util
import simics
import conf
import stest
import wdt_common

def test_unlock_with_magic_value():
    """Test unlock with magic value 0x1ACCE551 (TEST-005)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Device starts unlocked
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "Device starts unlocked")
    
    # Lock the device first
    regs.WDOGLOCK.write(0x12345678)  # Any non-magic value
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1, "Device locked")
    
    # Unlock with magic value
    regs.WDOGLOCK.write(0x1ACCE551)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "Device unlocked with magic value")
    
    print("Unlock with magic value test passed")

def test_lock_with_non_magic_values():
    """Test lock with non-magic values (TEST-006)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Test various non-magic values
    test_values = [0x0, 0x12345678, 0xFFFFFFFF, 0xDEADBEEF, 0x1ACCE550, 0x1ACCE552]
    
    for val in test_values:
        # Start unlocked
        regs.WDOGLOCK.write(0x1ACCE551)
        stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "Device unlocked")
        
        # Lock with non-magic value
        regs.WDOGLOCK.write(val)
        stest.expect_equal(regs.WDOGLOCK.read(), 0x1, f"Device locked with value 0x{val:08x}")
    
    print("Lock with non-magic values test passed")

def test_write_protection_when_locked():
    """Test write protection when locked (TEST-007)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Set initial values when unlocked
    regs.WDOGLOAD.write(0x12345678)
    regs.WDOGCONTROL.write(0x5)  # INTEN=1, RESEN=1
    
    # Verify values are set
    stest.expect_equal(regs.WDOGLOAD.read(), 0x12345678, "WDOGLOAD set when unlocked")
    stest.expect_equal(regs.WDOGCONTROL.read() & 0x3, 0x1, "WDOGCONTROL set when unlocked")
    
    # Lock the device
    regs.WDOGLOCK.write(0xDEADBEEF)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1, "Device locked")
    
    # Try to modify registers - should be ignored
    regs.WDOGLOAD.write(0xABCDEF00)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x12345678, "WDOGLOAD write ignored when locked")
    
    regs.WDOGCONTROL.write(0x0)
    stest.expect_equal(regs.WDOGCONTROL.read() & 0x3, 0x1, "WDOGCONTROL write ignored when locked")
    
    # Test WDOGINTCLR is also protected
    old_ris = regs.WDOGRIS.read()
    regs.WDOGINTCLR.write(0x1)
    stest.expect_equal(regs.WDOGRIS.read(), old_ris, "WDOGINTCLR write ignored when locked")
    
    # Test WDOGITCR is also protected
    regs.WDOGITCR.write(0x1)
    stest.expect_equal(regs.WDOGITCR.read(), 0x0, "WDOGITCR write ignored when locked")
    
    # Test WDOGITOP is also protected
    regs.WDOGITOP.write(0x3)
    # WDOGITOP is write-only, but the write should be ignored
    
    print("Write protection when locked test passed")

def test_wdoglock_always_writable():
    """Test WDOGLOCK register always writable (TEST-008)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Lock the device
    regs.WDOGLOCK.write(0x12345678)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1, "Device locked")
    
    # WDOGLOCK should still be writable even when locked
    regs.WDOGLOCK.write(0x1ACCE551)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "WDOGLOCK writable when device locked")
    
    # Lock again
    regs.WDOGLOCK.write(0xABCDEF00)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1, "Can lock again")
    
    # Unlock again
    regs.WDOGLOCK.write(0x1ACCE551)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "Can unlock again")
    
    print("WDOGLOCK always writable test passed")

def test_lock_status_read_values():
    """Verify lock status read values (0x0 unlocked, 0x1 locked)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Test multiple lock/unlock cycles
    for i in range(5):
        # Unlock
        regs.WDOGLOCK.write(0x1ACCE551)
        stest.expect_equal(regs.WDOGLOCK.read(), 0x0, f"Cycle {i}: unlocked reads 0x0")
        
        # Lock
        regs.WDOGLOCK.write(0x12345678 + i)
        stest.expect_equal(regs.WDOGLOCK.read(), 0x1, f"Cycle {i}: locked reads 0x1")
    
    print("Lock status read values test passed")

def test_register_access_after_unlock():
    """Test that registers become writable after unlock"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Lock the device
    regs.WDOGLOCK.write(0x12345678)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1, "Device locked")
    
    # Try to write - should be ignored
    regs.WDOGLOAD.write(0xDEADBEEF)
    stest.expect_equal(regs.WDOGLOAD.read(), 0xFFFFFFFF, "Write ignored when locked")
    
    # Unlock
    regs.WDOGLOCK.write(0x1ACCE551)
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "Device unlocked")
    
    # Now write should work
    regs.WDOGLOAD.write(0xDEADBEEF)
    stest.expect_equal(regs.WDOGLOAD.read(), 0xDEADBEEF, "Write works after unlock")
    
    print("Register access after unlock test passed")

# Run all tests
if __name__ == "__main__":
    test_unlock_with_magic_value()
    test_lock_with_non_magic_values()
    test_write_protection_when_locked()
    test_wdoglock_always_writable()
    test_lock_status_read_values()
    test_register_access_after_unlock()
    print("All lock protection tests passed!")
