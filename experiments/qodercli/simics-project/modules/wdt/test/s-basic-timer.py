import dev_util
import simics
import conf
import stest
import wdt_common

def test_basic_timer_countdown():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 1000
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x1)
    
    initial_value = regs.WDOGVALUE.read()
    stest.expect_equal(initial_value, load_value, "Counter should start at load value")
    
    simics.SIM_continue(500)
    
    value_after_500 = regs.WDOGVALUE.read()
    stest.expect_true(value_after_500 < initial_value, "Counter should have decremented")
    stest.expect_true(value_after_500 > 0, "Counter should not have reached zero yet")
    
    print(f"Initial value: {initial_value}, after 500 cycles: {value_after_500}")
    print("Basic timer countdown test passed!")

def test_timer_reload():
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
    
    ris_status = regs.WDOGRIS.read()
    stest.expect_equal(ris_status & 0x1, 1, "RIS should be set after timeout")
    
    value_after_timeout = regs.WDOGVALUE.read()
    stest.expect_true(value_after_timeout < load_value, "Counter should have reloaded and started counting down again")
    
    print("Timer reload test passed!")

def test_timer_disabled():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 1000
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x0)
    
    initial_value = regs.WDOGVALUE.read()
    
    simics.SIM_continue(500)
    
    value_after_500 = regs.WDOGVALUE.read()
    stest.expect_equal(value_after_500, initial_value, "Counter should not change when INTEN=0")
    
    print("Timer disabled test passed!")

def test_clock_divider():
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    regs.WDOGLOCK.write(0x1ACCE551)
    
    load_value = 1000
    regs.WDOGLOAD.write(load_value)
    
    regs.WDOGCONTROL.write(0x5)
    
    initial_value = regs.WDOGVALUE.read()
    
    simics.SIM_continue(100)
    
    value_after_100 = regs.WDOGVALUE.read()
    expected_decrement = 100 / 2
    actual_decrement = initial_value - value_after_100
    stest.expect_true(abs(actual_decrement - expected_decrement) < 5, 
                     f"Divider ÷2: expected ~{expected_decrement}, got {actual_decrement}")
    
    print("Clock divider test passed!")

if __name__ == "__main__":
    test_basic_timer_countdown()
    test_timer_reload()
    test_timer_disabled()
    test_clock_divider()