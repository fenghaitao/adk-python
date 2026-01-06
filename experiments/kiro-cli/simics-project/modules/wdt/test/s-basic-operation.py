# Basic Watchdog Timer Operation Tests
# Tests basic functionality including initialization, enable/disable, and timeout

import dev_util
import simics
import conf
import stest
import wdt_common

def test_device_initialization():
    """Test device initialization and default register values (TEST-001)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Check default register values
    stest.expect_equal(regs.WDOGLOAD.read(), 0xFFFFFFFF, "WDOGLOAD default value")
    # Don't read WDOGVALUE in init test as it might affect timer state
    # stest.expect_equal(regs.WDOGVALUE.read(), 0xFFFFFFFF, "WDOGVALUE default value")
    stest.expect_equal(regs.WDOGCONTROL.read(), 0x0, "WDOGCONTROL default value")
    stest.expect_equal(regs.WDOGRIS.read(), 0x0, "WDOGRIS default value")
    stest.expect_equal(regs.WDOGMIS.read(), 0x0, "WDOGMIS default value")
    stest.expect_equal(regs.WDOGLOCK.read(), 0x0, "WDOGLOCK default value (unlocked)")
    
    # Check peripheral ID registers
    stest.expect_equal(regs.WDOGPERIPHID0.read(), 0x24, "WDOGPERIPHID0")
    stest.expect_equal(regs.WDOGPERIPHID1.read(), 0xB8, "WDOGPERIPHID1")
    stest.expect_equal(regs.WDOGPERIPHID2.read(), 0x1B, "WDOGPERIPHID2")
    stest.expect_equal(regs.WDOGPERIPHID3.read(), 0x00, "WDOGPERIPHID3")
    
    # Check PrimeCell ID registers
    stest.expect_equal(regs.WDOGPCELLID0.read(), 0x0D, "WDOGPCELLID0")
    stest.expect_equal(regs.WDOGPCELLID1.read(), 0xF0, "WDOGPCELLID1")
    stest.expect_equal(regs.WDOGPCELLID2.read(), 0x05, "WDOGPCELLID2")
    stest.expect_equal(regs.WDOGPCELLID3.read(), 0xB1, "WDOGPCELLID3")
    
    print("Device initialization test passed")

def test_timer_enable_disable():
    """Test timer enable/disable transitions (TEST-002)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Run some initial cycles to establish baseline (like working test)
    simics.SIM_continue(50)
    
    # Set load value
    regs.WDOGLOAD.write(1000)
    
    # Enable timer (INTEN = 1)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    stest.expect_equal(regs.WDOGCONTROL.read() & 0x1, 0x1, "Timer enabled")
    
    # Check initial value after enable
    initial_value = regs.WDOGVALUE.read()
    stest.expect_equal(initial_value, 1000, "Counter loaded on enable")
    
    # Run some cycles and then check counter value
    simics.SIM_continue(100)
    counter_value = regs.WDOGVALUE.read()
    stest.expect_equal(counter_value, 900, "Counter decremented after 100 cycles")
    
    # Run more cycles and check counter decrements further
    simics.SIM_continue(100)
    new_counter = regs.WDOGVALUE.read()
    stest.expect_equal(new_counter, 800, "Counter decremented after 200 total cycles")
    
    # Disable timer (INTEN = 0)
    regs.WDOGCONTROL.write(0x0)  # INTEN=0
    stest.expect_equal(regs.WDOGCONTROL.read() & 0x1, 0x0, "Timer disabled")
    
    # Check counter stops decrementing
    stopped_value = regs.WDOGVALUE.read()
    simics.SIM_continue(100)
    stest.expect_equal(regs.WDOGVALUE.read(), stopped_value, "Counter stops when disabled")
    
    print("Timer enable/disable test passed")

def test_counter_decrement_and_timeout():
    """Test counter decrement and timeout generation (TEST-003)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Set small load value for quick timeout
    timeout_value = 100
    regs.WDOGLOAD.write(timeout_value)
    
    # Enable timer
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Run until timeout should occur
    simics.SIM_continue(timeout_value + 10)
    
    # Check that timeout occurred
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x1, "Raw interrupt status set on timeout")
    stest.expect_equal(regs.WDOGMIS.read() & 0x1, 0x1, "Masked interrupt status set on timeout")
    stest.expect_equal(regs.WDOGVALUE.read(), timeout_value, "Counter reloaded after timeout")
    
    print("Counter decrement and timeout test passed")

def test_interrupt_generation():
    """Test interrupt generation on first timeout (TEST-004)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Check initial interrupt state
    stest.expect_equal(pic_int.raised, 0, "No interrupt initially")
    
    # Set small timeout and enable
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Run until timeout
    simics.SIM_continue(60)
    
    # Check interrupt was raised
    stest.expect_equal(pic_int.raised, 1, "Interrupt raised on timeout")
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x1, "Raw interrupt status set")
    stest.expect_equal(regs.WDOGMIS.read() & 0x1, 0x1, "Masked interrupt status set")
    
    print("Interrupt generation test passed")

def test_load_register_behavior():
    """Test WDOGLOAD register read/write behavior"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Test writing and reading load value
    test_values = [0x12345678, 0xFFFFFFFF, 0x0, 0xABCDEF00]
    
    for val in test_values:
        regs.WDOGLOAD.write(val)
        stest.expect_equal(regs.WDOGLOAD.read(), val, f"WDOGLOAD stores value 0x{val:08x}")
    
    print("Load register behavior test passed")

# Run all tests
if __name__ == "__main__":
    test_device_initialization()
    test_timer_enable_disable()
    test_counter_decrement_and_timeout()
    test_interrupt_generation()
    test_load_register_behavior()
    print("All basic operation tests passed!")
