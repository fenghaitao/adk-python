# Tests for watchdog timer register access
# Copyright (c) 2024 Intel Corporation

import stest
import dev_util
import simics

# Create device instance
def create_watchdog_device():
    # Delete any existing device with the same name
    try:
        simics.SIM_delete_object(simics.SIM_get_object("wdt"))
    except:
        pass
    return simics.SIM_create_object("watchdog_timer", "wdt", [])

# Test WDOGLOAD register access
def test_wdogload_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x0000, 4)
    
    # Test initial value
    stest.expect_equal(reg.read(), 0x00000000)
    
    # Test write and read back
    reg.write(0x12345678)
    stest.expect_equal(reg.read(), 0x12345678)

# Test WDOGVALUE register access (read-only)
def test_wdogvalue_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x0004, 4)
    
    # Test initial value
    stest.expect_equal(reg.read(), 0x00000000)
    
    # Test that writes are ignored (read-only)
    # We expect a spec_violation log when trying to write to a read-only register
    with stest.expect_log_mgr(log_type="spec-viol"):
        reg.write(0x12345678)
    # Value should remain unchanged
    stest.expect_equal(reg.read(), 0x00000000)

# Test WDOGCONTROL register access
def test_wdogcontrol_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x0008, 4)
    
    # Test initial value
    stest.expect_equal(reg.read(), 0x00000000)
    
    # Test write and read back
    reg.write(0x00000003)  # Enable both INTEN and RESEN
    stest.expect_equal(reg.read(), 0x00000003)

# Test WDOGINTCLR register access (write-only)
def test_wdogintclr_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x000C, 4)
    
    # Test that writes are accepted (write-only)
    reg.write(0x12345678)  # Any value should clear the interrupt

# Test WDOGRIS register access (read-only)
def test_wdogris_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x0010, 4)
    
    # Test initial value
    stest.expect_equal(reg.read(), 0x00000000)
    
    # Test that writes are ignored (read-only)
    # We expect a spec_violation log when trying to write to a read-only register
    with stest.expect_log_mgr(log_type="spec-viol"):
        reg.write(0x12345678)
    # Value should remain unchanged
    stest.expect_equal(reg.read(), 0x00000000)

# Test WDOGMIS register access (read-only)
def test_wdogmis_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x0014, 4)
    
    # Test initial value
    stest.expect_equal(reg.read(), 0x00000000)
    
    # Test that writes are ignored (read-only)
    # We expect a spec_violation log when trying to write to a read-only register
    with stest.expect_log_mgr(log_type="spec-viol"):
        reg.write(0x12345678)
    # Value should remain unchanged
    stest.expect_equal(reg.read(), 0x00000000)

# Test WDOGLOCK register access
def test_wdoglock_access():
    dev = create_watchdog_device()
    reg = dev_util.Register_LE(dev.bank.regs, 0x0C00, 4)
    
    # Test initial value (locked)
    stest.expect_equal(reg.read(), 0x00000001)
    
    # Test unlock
    reg.write(0x1ACCE551)  # Unlock sequence
    stest.expect_equal(reg.read(), 0x00000000)  # Should be unlocked
    
    # Test lock again
    reg.write(0x00000000)  # Any value other than unlock sequence should lock
    stest.expect_equal(reg.read(), 0x00000001)  # Should be locked

# Test identification registers (read-only)
def test_identification_registers():
    dev = create_watchdog_device()
    
    # Test WDOGPERIPHID0
    reg0 = dev_util.Register_LE(dev.bank.regs, 0x0FE0, 4)
    stest.expect_equal(reg0.read(), 0x00000024)
    
    # Test WDOGPERIPHID1
    reg1 = dev_util.Register_LE(dev.bank.regs, 0x0FE4, 4)
    stest.expect_equal(reg1.read(), 0x000000B8)
    
    # Test WDOGPERIPHID2
    reg2 = dev_util.Register_LE(dev.bank.regs, 0x0FE8, 4)
    stest.expect_equal(reg2.read(), 0x00000018)
    
    # Test WDOGPERIPHID3
    reg3 = dev_util.Register_LE(dev.bank.regs, 0x0FEC, 4)
    stest.expect_equal(reg3.read(), 0x00000000)
    
    # Test WDOGPCELLID0
    reg4 = dev_util.Register_LE(dev.bank.regs, 0x0FF0, 4)
    stest.expect_equal(reg4.read(), 0x0000000D)
    
    # Test WDOGPCELLID1
    reg5 = dev_util.Register_LE(dev.bank.regs, 0x0FF4, 4)
    stest.expect_equal(reg5.read(), 0x000000F0)
    
    # Test WDOGPCELLID2
    reg6 = dev_util.Register_LE(dev.bank.regs, 0x0FF8, 4)
    stest.expect_equal(reg6.read(), 0x00000005)
    
    # Test WDOGPCELLID3
    reg7 = dev_util.Register_LE(dev.bank.regs, 0x0FFC, 4)
    stest.expect_equal(reg7.read(), 0x000000B1)

# Run all tests
test_wdogload_access()
test_wdogvalue_access()
test_wdogcontrol_access()
test_wdogintclr_access()
test_wdogris_access()
test_wdogmis_access()
test_wdoglock_access()
test_identification_registers()

print("All register access tests passed!")