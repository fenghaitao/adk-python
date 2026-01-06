# Interrupt and Reset Tests
# Tests interrupt clearing, counter reload, and reset generation

import dev_util
import simics
import conf
import stest
import wdt_common

def test_interrupt_clear_with_wdogintclr():
    """Test interrupt clear with WDOGINTCLR write (TEST-014)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Set up timeout to generate interrupt
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Wait for timeout
    simics.SIM_continue(60)
    
    # Verify interrupt is set
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x1, "Raw interrupt status set")
    stest.expect_equal(regs.WDOGMIS.read() & 0x1, 0x1, "Masked interrupt status set")
    stest.expect_equal(pic_int.raised, 1, "Interrupt signal raised")
    
    # Clear interrupt
    regs.WDOGINTCLR.write(0x12345678)  # Any value should work
    
    # Verify interrupt is cleared
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x0, "Raw interrupt status cleared")
    stest.expect_equal(regs.WDOGMIS.read() & 0x1, 0x0, "Masked interrupt status cleared")
    stest.expect_equal(pic_int.raised, 0, "Interrupt signal lowered")
    
    print("Interrupt clear with WDOGINTCLR test passed")

def test_counter_reload_on_interrupt_clear():
    """Test counter reload on interrupt clear (TEST-015)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Set load value and enable
    load_value = 1000
    regs.WDOGLOAD.write(load_value)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Let counter run down partially
    simics.SIM_continue(200)
    partial_value = regs.WDOGVALUE.read()
    stest.expect_true(partial_value < load_value, "Counter decremented")
    
    # Generate interrupt by waiting for timeout
    simics.SIM_continue(load_value)
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x1, "Interrupt generated")
    
    # Counter should be reloaded after timeout
    stest.expect_equal(regs.WDOGVALUE.read(), load_value, "Counter reloaded after timeout")
    
    # Let it run down again
    simics.SIM_continue(300)
    partial_value2 = regs.WDOGVALUE.read()
    stest.expect_true(partial_value2 < load_value, "Counter decremented again")
    
    # Clear interrupt - should reload counter
    regs.WDOGINTCLR.write(0x1)
    stest.expect_equal(regs.WDOGVALUE.read(), load_value, "Counter reloaded on interrupt clear")
    
    print("Counter reload on interrupt clear test passed")

def test_reset_generation_on_second_timeout():
    """Test reset generation on second timeout (TEST-016)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Enable both interrupt and reset
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1
    
    # Wait for first timeout (interrupt)
    simics.SIM_continue(60)
    stest.expect_equal(pic_int.raised, 1, "First timeout generates interrupt")
    stest.expect_equal(pic_res.raised, 0, "No reset on first timeout")
    
    # Wait for second timeout (reset) - don't clear interrupt
    simics.SIM_continue(60)
    stest.expect_equal(pic_res.raised, 1, "Second timeout generates reset")
    stest.expect_equal(pic_int.raised, 1, "Interrupt still asserted")
    
    print("Reset generation on second timeout test passed")

def test_reset_signal_persistence():
    """Test reset signal persistence until system reset (TEST-017)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Generate reset
    regs.WDOGLOAD.write(30)
    regs.WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1
    
    # Wait for both timeouts
    simics.SIM_continue(40)  # First timeout
    simics.SIM_continue(40)  # Second timeout
    
    stest.expect_equal(pic_res.raised, 1, "Reset signal asserted")
    
    # Try various operations - reset should remain asserted
    regs.WDOGINTCLR.write(0x1)
    stest.expect_equal(pic_res.raised, 1, "Reset persists after interrupt clear")
    
    regs.WDOGCONTROL.write(0x0)  # Disable timer
    stest.expect_equal(pic_res.raised, 1, "Reset persists after timer disable")
    
    regs.WDOGLOAD.write(1000)
    stest.expect_equal(pic_res.raised, 1, "Reset persists after load write")
    
    # Only device reset should clear it (tested in reset method)
    
    print("Reset signal persistence test passed")

def test_resen_bit_control():
    """Test RESEN bit control of reset generation (TEST-018)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Test with RESEN=0 (reset disabled)
    regs.WDOGLOAD.write(40)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1, RESEN=0
    
    # Wait for both timeouts
    simics.SIM_continue(50)  # First timeout
    stest.expect_equal(pic_int.raised, 1, "Interrupt generated")
    stest.expect_equal(pic_res.raised, 0, "No reset when RESEN=0")
    
    simics.SIM_continue(50)  # Second timeout
    stest.expect_equal(pic_res.raised, 0, "Still no reset on second timeout when RESEN=0")
    
    # Reset for next test
    regs.WDOGINTCLR.write(0x1)
    stest.expect_equal(pic_int.raised, 0, "Interrupt cleared")
    
    # Test with RESEN=1 (reset enabled)
    regs.WDOGLOAD.write(40)
    regs.WDOGCONTROL.write(0x3)  # INTEN=1, RESEN=1
    
    # Wait for both timeouts
    simics.SIM_continue(50)  # First timeout
    stest.expect_equal(pic_int.raised, 1, "Interrupt generated")
    stest.expect_equal(pic_res.raised, 0, "No reset on first timeout")
    
    simics.SIM_continue(50)  # Second timeout
    stest.expect_equal(pic_res.raised, 1, "Reset generated on second timeout when RESEN=1")
    
    print("RESEN bit control test passed")

def test_multiple_wdogintclr_writes():
    """Test multiple WDOGINTCLR writes (TEST-027)"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Generate interrupt
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    simics.SIM_continue(60)
    
    stest.expect_equal(pic_int.raised, 1, "Interrupt generated")
    
    # Clear interrupt multiple times
    for i in range(5):
        regs.WDOGINTCLR.write(i)
        stest.expect_equal(pic_int.raised, 0, f"Interrupt cleared on write {i}")
        stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x0, f"RIS cleared on write {i}")
        
        # Each clear should reload the counter
        stest.expect_equal(regs.WDOGVALUE.read(), 50, f"Counter reloaded on write {i}")
    
    print("Multiple WDOGINTCLR writes test passed")

def test_interrupt_without_enable():
    """Test that no interrupt occurs when INTEN=0"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Set load value but don't enable interrupt
    regs.WDOGLOAD.write(50)
    regs.WDOGCONTROL.write(0x0)  # INTEN=0
    
    # Wait for what would be timeout
    simics.SIM_continue(100)
    
    # No interrupt should occur
    stest.expect_equal(pic_int.raised, 0, "No interrupt when INTEN=0")
    stest.expect_equal(regs.WDOGRIS.read() & 0x1, 0x0, "No raw interrupt when INTEN=0")
    stest.expect_equal(regs.WDOGMIS.read() & 0x1, 0x0, "No masked interrupt when INTEN=0")
    
    print("Interrupt without enable test passed")

# Run all tests
if __name__ == "__main__":
    test_interrupt_clear_with_wdogintclr()
    test_counter_reload_on_interrupt_clear()
    test_reset_generation_on_second_timeout()
    test_reset_signal_persistence()
    test_resen_bit_control()
    test_multiple_wdogintclr_writes()
    test_interrupt_without_enable()
    print("All interrupt and reset tests passed!")
