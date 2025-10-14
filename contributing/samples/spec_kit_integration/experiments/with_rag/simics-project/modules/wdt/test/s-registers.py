# © 2024 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.

# Test the WDT register access functions

import stest
import dev_util
import conf
import wdt_common

# Create an instance of the device to test
dev = wdt_common.create_wdt()

# Test WDOGLOAD register read/write
def test_wdogload():
    print("Testing WDOGLOAD register")
    
    # Test writing a value
    test_value = 0x12345678
    dev.bank.regs.wdogload = test_value
    stest.expect_equal(dev.bank.regs.wdogload, test_value)
    
    # Test writing zero
    dev.bank.regs.wdogload = 0
    stest.expect_equal(dev.bank.regs.wdogload, 0)
    
    # Test writing maximum value
    dev.bank.regs.wdogload = 0xFFFFFFFF
    stest.expect_equal(dev.bank.regs.wdogload, 0xFFFFFFFF)

# Test WDOGVALUE register read-only
def test_wdogvalue():
    print("Testing WDOGVALUE register")
    
    # Set load value first
    dev.bank.regs.wdogload = 0x1000
    stest.expect_equal(dev.bank.regs.wdogvalue, 0x1000)
    
    # Try to write (should not change)
    try:
        dev.bank.regs.wdogvalue = 0x12345678
        # If we get here, the write succeeded, which is incorrect
        stest.expect_equal(dev.bank.regs.wdogvalue, 0x1000)  # Should still be original value
    except:
        # Write failed as expected
        pass

# Test WDOGCONTROL register read/write
def test_wdogcontrol():
    print("Testing WDOGCONTROL register")
    
    # Test initial value
    initial_value = dev.bank.regs.wdogcontrol
    print(f"Initial WDOGCONTROL value: 0x{initial_value:08x}")
    
    # Test setting interrupt enable
    dev.bank.regs.wdogcontrol = 0x1  # int_en = 1
    stest.expect_equal(dev.bank.regs.wdogcontrol & 0x1, 0x1)
    
    # Test setting reset enable
    dev.bank.regs.wdogcontrol = 0x2  # res_en = 1
    stest.expect_equal(dev.bank.regs.wdogcontrol & 0x2, 0x2)
    
    # Test setting both
    dev.bank.regs.wdogcontrol = 0x3  # int_en = 1, res_en = 1
    stest.expect_equal(dev.bank.regs.wdogcontrol, 0x3)

# Test WDOGINTCLR register write-only
def test_wdogintclr():
    print("Testing WDOGINTCLR register")
    
    # Writing any value should clear interrupt (implementation will be added later)
    dev.bank.regs.wdogintclr = 0x0
    dev.bank.regs.wdogintclr = 0x1
    dev.bank.regs.wdogintclr = 0xFFFFFFFF

# Test WDOGRIS register read-only
def test_wdogris():
    print("Testing WDOGRIS register")
    
    # Test initial value
    initial_value = dev.bank.regs.wdogris
    print(f"Initial WDOGRIS value: 0x{initial_value:08x}")
    
    # Try to write (should not change)
    try:
        dev.bank.regs.wdogris = 0x1
        # If we get here, the write succeeded, which is incorrect
        stest.expect_equal(dev.bank.regs.wdogris, initial_value)  # Should still be original value
    except:
        # Write failed as expected
        pass

# Test WDOGMIS register read-only
def test_wdogmis():
    print("Testing WDOGMIS register")
    
    # Test initial value
    initial_value = dev.bank.regs.wdogmis
    print(f"Initial WDOGMIS value: 0x{initial_value:08x}")
    
    # Try to write (should not change)
    try:
        dev.bank.regs.wdogmis = 0x1
        # If we get here, the write succeeded, which is incorrect
        stest.expect_equal(dev.bank.regs.wdogmis, initial_value)  # Should still be original value
    except:
        # Write failed as expected
        pass

# Test WDOGLOCK register read/write
def test_wdoglock():
    print("Testing WDOGLOCK register")
    
    # Test initial state (should be locked)
    initial_locked = dev.bank.regs.wdoglock
    print(f"Initial WDOGLOCK value: 0x{initial_locked:08x}")
    
    # Test unlocking
    unlock_key = 0x1ACCE551
    dev.bank.regs.wdoglock = unlock_key
    
    # Test that registers can now be written (if unlocked)
    # This will be fully tested when we implement the lock functionality
    
    # Test locking again
    dev.bank.regs.wdoglock = 0x0
    
# Test integration test registers
def test_integration_registers():
    print("Testing integration test registers")
    
    # Test WDOGITCR
    initial_itcr = dev.bank.regs.wdogitcr
    print(f"Initial WDOGITCR value: 0x{initial_itcr:08x}")
    
    # Try to write
    dev.bank.regs.wdogitcr = 0x1
    
    # Test WDOGITOP write-only
    try:
        dev.bank.regs.wdogitop = 0x3  # int_output = 1, res_output = 1
    except:
        # Write might fail if not implemented yet
        pass

# Run all tests
test_wdogload()
test_wdogvalue()
test_wdogcontrol()
test_wdogintclr()
test_wdogris()
test_wdogmis()
test_wdoglock()
test_integration_registers()

print("All register tests completed.")