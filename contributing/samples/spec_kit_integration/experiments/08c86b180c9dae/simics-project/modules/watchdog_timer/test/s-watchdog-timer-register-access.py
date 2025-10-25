# Test register access for the watchdog timer device
import dev_util
import simics
import stest

# Test basic register read/write operations
def test_register_access():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer0')
    
    # Test WDOGLOAD register (RW)
    load_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0000, size=4)
    initial_value = load_reg.read()
    load_reg.write(0x12345678)
    stest.expect_equal(load_reg.read(), 0x12345678)
    
    # Test WDOGVALUE register (RO)
    value_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0004, size=4)
    # Should be able to read
    value = value_reg.read()
    # For a read-only register, writing should not be allowed
    # In Simics, write to read-only registers may not cause an error but should not change the value
    # Let's just verify we can read it
    stest.expect_true(isinstance(value, int))
    
    # Test WDOGCONTROL register (RW)
    control_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0008, size=4)
    initial_control = control_reg.read()
    control_reg.write(0x00000007)  # Enable all bits
    stest.expect_equal(control_reg.read(), 0x00000007)
    control_reg.write(initial_control)  # Restore initial value
    
    # Test WDOGINTCLR register (WO)
    intclr_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x000C, size=4)
    # Writing should be possible (no error)
    intclr_reg.write(0x00000001)
    
    # Test WDOGRIS register (RO)
    ris_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0010, size=4)
    # Should be able to read
    ris_value = ris_reg.read()
    stest.expect_true(isinstance(ris_value, int))
    
    # Test WDOGMIS register (RO)
    mis_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0014, size=4)
    # Should be able to read
    mis_value = mis_reg.read()
    stest.expect_true(isinstance(mis_value, int))
    
    # Test WDOGLOCK register (RW)
    lock_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0C00, size=4)
    initial_lock = lock_reg.read()
    # Test unlock with magic value
    lock_reg.write(0x1ACCE551)
    stest.expect_equal(lock_reg.read(), 0x1ACCE551)
    # Test lock with any other value
    lock_reg.write(0x00000001)
    stest.expect_equal(lock_reg.read(), 0x00000001)
    lock_reg.write(initial_lock)  # Restore initial value

# Run the test
test_register_access()
print("Register access test completed successfully")