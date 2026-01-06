import dev_util
import simics
import conf
import stest
import wdt_common

def test_reset_on_second_timeout():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 100
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x3)
    
    initial_reset = pic_res.raised
    stest.expect_equal(initial_reset, 0, "Reset should not be raised initially")
    
    simics.SIM_continue(150)
    
    after_first_timeout_reset = pic_res.raised
    stest.expect_equal(after_first_timeout_reset, 0, "Reset should not be raised after first timeout")
    
    after_first_timeout_int = pic_int.raised
    stest.expect_equal(after_first_timeout_int, 1, "Interrupt should be raised after first timeout")
    
    simics.SIM_continue(150)
    
    after_second_timeout_reset = pic_res.raised
    stest.expect_equal(after_second_timeout_reset, 1, "Reset should be raised after second timeout")
    
    print("Reset on second timeout test passed!")

def test_no_reset_when_resen_disabled():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 100
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x1)
    
    simics.SIM_continue(150)
    
    after_first_timeout_int = pic_int.raised
    stest.expect_equal(after_first_timeout_int, 1, "Interrupt should be raised after first timeout")
    
    simics.SIM_continue(150)
    
    after_second_timeout_reset = pic_res.raised
    stest.expect_equal(after_second_timeout_reset, 0, "Reset should NOT be raised when RESEN=0")
    
    print("No reset when RESEN disabled test passed!")

def test_reset_persistence():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 100
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x3)
    
    simics.SIM_continue(250)
    
    after_second_timeout_reset = pic_res.raised
    stest.expect_equal(after_second_timeout_reset, 1, "Reset should be raised after second timeout")
    
    simics.SIM_continue(500)
    
    reset_after_delay = pic_res.raised
    stest.expect_equal(reset_after_delay, 1, "Reset should remain asserted")
    
    print("Reset persistence test passed!")

if __name__ == "__main__":
    test_reset_on_second_timeout()
    test_no_reset_when_resen_disabled()
    test_reset_persistence()
