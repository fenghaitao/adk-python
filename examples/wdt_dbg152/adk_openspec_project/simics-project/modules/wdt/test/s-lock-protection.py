# © 2025 Intel Corporation
# Test watchdog timer lock protection functionality

import dev_util
import simics
import stest
import wdt_common

def test_lock_protection():
    # Create an instance of the device to test
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_wdogint = devs[1]
    fake_pic_wdogres = devs[2]

    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)

    # Test 1: Verify device is locked by default
    print("Test 1: Device is locked by default")
    initial_lock_status = regs.WDOGLOCK.read()
    stest.expect_equal(initial_lock_status, 0x1)  # Should be locked initially
    print(f"Initial lock status: 0x{initial_lock_status:x}")

    # Test 2: Test lock register unlock mechanism (write 0x1ACCE551)
    print("Test 2: Unlock mechanism with 0x1ACCE551")
    unlock_code = 0x1ACCE551
    regs.WDOGLOCK.write(unlock_code)
    unlock_status = regs.WDOGLOCK.read()
    print(f"After writing unlock code, lock status: 0x{unlock_status:x}")
    stest.expect_equal(unlock_status, 0x0)  # Should be unlocked
    print("Device successfully unlocked with correct code")

    # Test 3: Write to registers when unlocked
    print("Test 3: Register access when unlocked")
    test_value = 0x12345678
    regs.WDOGLOAD.write(test_value)
    read_value = regs.WDOGLOAD.read()
    stest.expect_equal(read_value, test_value)
    print(f"Register write/read successful when unlocked: wrote 0x{test_value:x}, read 0x{read_value:x}")

    # Test 4: Test lock register lock mechanism (write other values)
    print("Test 4: Lock mechanism with other values")
    # First unlock again
    regs.WDOGLOCK.write(0x1ACCE551)  # Unlock
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0)  # Should be unlocked
    
    # Now lock with a different value
    lock_code = 0x12345678  # Any value other than unlock code
    regs.WDOGLOCK.write(lock_code)
    lock_status = regs.WDOGLOCK.read()
    print(f"After writing lock code {hex(lock_code)}, lock status: 0x{lock_status:x}")
    stest.expect_equal(lock_status, 0x1)  # Should be locked
    print("Device successfully locked with incorrect code")

    # Test 5: Test that writes to registers are blocked when locked
    print("Test 5: Register writes blocked when locked")
    original_load_value = regs.WDOGLOAD.read()
    print(f"Original WDOGLOAD value when locked: 0x{original_load_value:x}")
    
    # Attempt to write to register when locked
    new_test_value = 0xABCDEF00
    regs.WDOGLOAD.write(new_test_value)
    read_after_locked = regs.WDOGLOAD.read()
    print(f"Attempted to write 0x{new_test_value:x}, actual value: 0x{read_after_locked:x}")
    
    # Value should remain unchanged when locked
    stest.expect_equal(read_after_locked, original_load_value)
    print("Register writes correctly blocked when device is locked")

    # Test 6: Test that WDOGVALUE register is readable when locked
    print("Test 6: WDOGVALUE readable when locked")
    wdogvalue_locked = regs.WDOGVALUE.read()
    print(f"WDOGVALUE readable when locked: 0x{wdogvalue_locked:x}")
    # This should work - the spec says WDOGVALUE is readable regardless of lock status
    print("WDOGVALUE register is readable when locked (as expected)")

    # Test 7: Test that identification registers are readable when locked
    print("Test 7: ID registers readable when locked")
    periph_id0 = regs.WDOGPERIPHID0.read()
    periph_id1 = regs.WDOGPERIPHID1.read()
    periph_id2 = regs.WDOGPERIPHID2.read()
    pcell_id0 = regs.WDOGPCELLID0.read()
    
    print(f"PERIPHID0: 0x{periph_id0:x}, expected: 0x24")
    print(f"PERIPHID1: 0x{periph_id1:x}, expected: 0xb8")  
    print(f"PERIPHID2: 0x{periph_id2:x}, expected: 0x1b")
    print(f"PCELLID0: 0x{pcell_id0:x}, expected: 0xd")
    
    # Verify expected ID register values
    stest.expect_equal(periph_id0 & 0xFF, 0x24)  # PERIPHID0 should be 0x24
    stest.expect_equal(periph_id1 & 0xFF, 0xB8)  # PERIPHID1 should be 0xB8
    stest.expect_equal(periph_id2 & 0xFF, 0x1B)  # PERIPHID2 should be 0x1B
    stest.expect_equal(pcell_id0 & 0xFF, 0x0D)   # PCELLID0 should be 0x0D
    print("ID registers readable when locked (as expected)")

    # Test 8: Test that WDOGLOCK register itself remains writable when locked
    print("Test 8: WDOGLOCK register remains writable when locked")
    # We're currently in locked state, write unlock code
    regs.WDOGLOCK.write(0x1ACCE551)
    unlock_status_after = regs.WDOGLOCK.read()
    print(f"After writing unlock code while locked, status: 0x{unlock_status_after:x}")
    stest.expect_equal(unlock_status_after, 0x0)  # Should now be unlocked
    print("WDOGLOCK register writable even when device is locked")

    # Test 9: Test that other registers become writable after unlocking
    print("Test 9: Other registers writable after unlocking")
    # We're unlocked now, change WDOGLOAD
    test_value_unlocked = 0xCAFEBABE
    regs.WDOGLOCK.write(0x1ACCE551)  # Ensure unlocked
    regs.WDOGLOAD.write(test_value_unlocked)
    read_unlocked = regs.WDOGLOAD.read()
    stest.expect_equal(read_unlocked, test_value_unlocked)
    print(f"Register writable after unlock: 0x{read_unlocked:x}")

    # Test 10: Lock again and verify protection still works
    print("Test 10: Verify protection after re-locking")
    regs.WDOGLOCK.write(0xDEADBEEF)  # Lock with different value
    stest.expect_equal(regs.WDOGLOCK.read(), 0x1)  # Should be locked
    
    original_when_locked = regs.WDOGLOAD.read()
    regs.WDOGLOAD.write(0x11111111)  # Try to write when locked
    after_write_locked = regs.WDOGLOAD.read()
    stest.expect_equal(after_write_locked, original_when_locked)
    print("Protection working correctly after re-locking")

    print("Lock protection tests completed successfully!")


if __name__ == "__main__":
    test_lock_protection()