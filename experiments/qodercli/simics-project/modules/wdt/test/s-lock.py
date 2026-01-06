import dev_util
import simics
import conf
import stest
import wdt_common

def test_lock_unlock():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    lock_status = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status, 0, "Device should be unlocked initially")
    
    regs.WDOGLOCK.write(0x12345678)
    
    lock_status_after_lock = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status_after_lock, 1, "Device should be locked after writing non-magic value")
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    lock_status_after_unlock = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status_after_unlock, 0, "Device should be unlocked after writing magic value")
    
    print("Lock/unlock test passed!")

def test_write_protection_when_locked():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    initial_load = 0xAABBCCDD
    regs.WDOGLOAD.write(initial_load)
    
    load_after_write = regs.WDOGLOAD.read()
    stest.expect_equal(load_after_write, initial_load, "LOAD should be writable when unlocked")
    
    regs.WDOGLOCK.write(0x0)
    
    regs.WDOGLOAD.write(0x11223344)
    
    load_after_locked_write = regs.WDOGLOAD.read()
    stest.expect_equal(load_after_locked_write, initial_load, "LOAD should not change when locked")
    
    regs.WDOGCONTROL.write(0x7)
    
    control_after_locked_write = regs.WDOGCONTROL.read()
    stest.expect_equal(control_after_locked_write, 0x0, "CONTROL should not change when locked")
    
    print("Write protection when locked test passed!")

def test_value_readable_when_locked():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 1000
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x1)
    
    regs.WDOGLOCK.write(0x0)
    
    value_when_locked = regs.WDOGVALUE.read()
    stest.expect_true(value_when_locked > 0, "VALUE should be readable when locked")
    
    print("VALUE readable when locked test passed!")

def test_lock_always_accessible():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x0)
    
    lock_status = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status, 1, "LOCK should be readable when locked")
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    lock_status_after_unlock = regs.WDOGLOCK.read()
    stest.expect_equal(lock_status_after_unlock, 0, "LOCK should be writable when locked (to unlock)")
    
    print("LOCK always accessible test passed!")

if __name__ == "__main__":
    test_lock_unlock()
    test_write_protection_when_locked()
    test_value_readable_when_locked()
    test_lock_always_accessible()