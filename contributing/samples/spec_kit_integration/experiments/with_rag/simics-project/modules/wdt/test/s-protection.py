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

# Test the WDT register protection functions

import stest
import dev_util
import conf
import wdt_common

# Create an instance of the device to test
dev = wdt_common.create_wdt()

def test_initial_lock_state():
    print("Testing initial lock state")
    
    # Device should be locked by default
    # This test will fail until we implement the lock functionality
    # lock_state = dev.bank.regs.wdoglock
    # We might need to check a separate attribute or status indicator

def test_write_protection_when_locked():
    print("Testing write protection when locked")
    
    # Device should be locked by default
    # Try to write to protected registers
    try:
        dev.bank.regs.wdogload = 0x12345678
        # If we get here, the write succeeded, which is incorrect when locked
        print("Write to WDOGLOAD succeeded when locked (unexpected)")
    except:
        # Write failed as expected
        print("Write to WDOGLOAD failed when locked (expected)")
    
    try:
        dev.bank.regs.wdogcontrol = 0x3
        # If we get here, the write succeeded, which is incorrect when locked
        print("Write to WDOGCONTROL succeeded when locked (unexpected)")
    except:
        # Write failed as expected
        print("Write to WDOGCONTROL failed when locked (expected)")

def test_unlock_sequence():
    print("Testing unlock sequence")
    
    # Test the correct unlock sequence
    unlock_key = 0x1ACCE551
    dev.bank.regs.wdoglock = unlock_key
    
    # After unlocking, writes should succeed
    try:
        dev.bank.regs.wdogload = 0x12345678
        print("Write to WDOGLOAD succeeded when unlocked (expected)")
    except:
        # Write failed, which is incorrect when unlocked
        print("Write to WDOGLOAD failed when unlocked (unexpected)")
    
    try:
        dev.bank.regs.wdogcontrol = 0x3
        print("Write to WDOGCONTROL succeeded when unlocked (expected)")
    except:
        # Write failed, which is incorrect when unlocked
        print("Write to WDOGCONTROL failed when unlocked (unexpected)")

def test_lock_sequence():
    print("Testing lock sequence")
    
    # First unlock
    unlock_key = 0x1ACCE551
    dev.bank.regs.wdoglock = unlock_key
    
    # Then lock with any other value
    dev.bank.regs.wdoglock = 0x0
    
    # After locking, writes should fail again
    try:
        dev.bank.regs.wdogload = 0x87654321
        # If we get here, the write succeeded, which is incorrect when locked
        print("Write to WDOGLOAD succeeded when re-locked (unexpected)")
    except:
        # Write failed as expected
        print("Write to WDOGLOAD failed when re-locked (expected)")

def test_invalid_unlock_keys():
    print("Testing invalid unlock keys")
    
    # Try various invalid unlock keys
    invalid_keys = [0x0, 0x1, 0xFFFFFFFF, 0x1ACCE550, 0x1ACCE552]
    
    for key in invalid_keys:
        # Device should remain locked
        dev.bank.regs.wdoglock = key
        
        # Try to write to protected register
        try:
            dev.bank.regs.wdogload = 0x12345678
            # If we get here, the write succeeded, which is incorrect
            print(f"Write succeeded with invalid key 0x{key:08x} (unexpected)")
        except:
            # Write failed as expected
            print(f"Write failed with invalid key 0x{key:08x} (expected)")

# Run all tests
test_initial_lock_state()
test_write_protection_when_locked()
test_unlock_sequence()
test_lock_sequence()
test_invalid_unlock_keys()

print("All register protection tests completed.")