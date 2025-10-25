# Unit tests for the watchdog timer device
import dev_util
import simics
import stest

# Test register access functionality
def test_register_access():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer0')
    
    # Test WDOGLOAD register
    load_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0000, size=4)
    load_reg.write(0x12345678)
    stest.expect_equal(load_reg.read(), 0x12345678)
    
    # Test WDOGVALUE register (read-only)
    value_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0004, size=4)
    initial_value = value_reg.read()
    stest.expect_true(isinstance(initial_value, int))
    
    # Test WDOGCONTROL register
    control_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0008, size=4)
    control_reg.write(0x00000007)  # Enable all bits
    stest.expect_equal(control_reg.read(), 0x00000007)
    
    # Test WDOGLOCK register
    lock_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0C00, size=4)
    lock_reg.write(0x1ACCE551)  # Unlock
    stest.expect_equal(lock_reg.read(), 0x1ACCE551)
    lock_reg.write(0x00000001)  # Lock
    stest.expect_equal(lock_reg.read(), 0x00000001)
    
    print("Register access tests passed")

# Test lock mechanism
def test_lock_mechanism():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer1')
    
    # Test that registers are locked by default
    lock_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0C00, size=4)
    stest.expect_equal(lock_reg.read(), 0x00000001)  # Should be locked by default
    
    # Test that we can't write to protected registers when locked
    control_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0008, size=4)
    original_value = control_reg.read()
    
    # Try to write to control register while locked (but with a valid value)
    control_reg.write(0x00000005)  # Try to change to a different valid value
    # The value should remain unchanged
    stest.expect_equal(control_reg.read(), original_value)
    
    # Unlock the registers
    lock_reg.write(0x1ACCE551)
    stest.expect_equal(lock_reg.read(), 0x1ACCE551)
    
    # Now we should be able to write to protected registers
    control_reg.write(0x00000005)
    stest.expect_equal(control_reg.read(), 0x00000005)
    
    print("Lock mechanism tests passed")

# Test interrupt generation
def test_interrupt_generation():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer2')
    
    # Configure for interrupt generation
    load_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0000, size=4)
    control_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0008, size=4)
    ris_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0010, size=4)
    mis_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0014, size=4)
    
    # Set a small load value
    load_reg.write(0x0000000A)  # 10 cycles
    
    # Enable timer and interrupt
    control_reg.write(0x00000005)  # Enable timer (bit 0) and interrupt (bit 2)
    
    # Check that interrupt is not yet pending
    stest.expect_equal(ris_reg.read(), 0x00000000)
    stest.expect_equal(mis_reg.read(), 0x00000000)
    
    print("Interrupt generation tests passed")

# Test integration test mode
def test_integration_test_mode():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer3')
    
    # Test integration test control register
    itcr_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0F00, size=4)
    itop_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0F04, size=4)
    
    # Enable integration test mode
    itcr_reg.write(0x00000001)
    stest.expect_equal(itcr_reg.read(), 0x00000001)
    
    # Set integration test output
    itop_reg.write(0x00000003)  # Set both interrupt and reset outputs
    stest.expect_equal(itop_reg.read(), 0x00000003)
    
    print("Integration test mode tests passed")

# Test ID registers
def test_id_registers():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer4')
    
    # Test Peripheral ID registers
    periph_id0 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FE0, size=4)
    periph_id1 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FE4, size=4)
    periph_id2 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FE8, size=4)
    periph_id3 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FEC, size=4)
    
    stest.expect_equal(periph_id0.read(), 0x00000024)
    stest.expect_equal(periph_id1.read(), 0x000000B8)
    stest.expect_equal(periph_id2.read(), 0x0000001B)
    stest.expect_equal(periph_id3.read(), 0x00000000)
    
    # Test PrimeCell ID registers
    primecell_id0 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FF0, size=4)
    primecell_id1 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FF4, size=4)
    primecell_id2 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FF8, size=4)
    primecell_id3 = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0FFC, size=4)
    
    stest.expect_equal(primecell_id0.read(), 0x0000000D)
    stest.expect_equal(primecell_id1.read(), 0x000000F0)
    stest.expect_equal(primecell_id2.read(), 0x00000005)
    stest.expect_equal(primecell_id3.read(), 0x000000B1)
    
    print("ID register tests passed")

# Run all tests
def run_all_tests():
    test_register_access()
    test_lock_mechanism()
    test_interrupt_generation()
    test_integration_test_mode()
    test_id_registers()
    print("All unit tests completed successfully")

# Execute the tests
run_all_tests()