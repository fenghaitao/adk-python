# Standalone timer test

import dev_util
import simics
import conf
import stest
import wdt_common

def test_timer_standalone():
    """Standalone timer test"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    print("=== Standalone Timer Test ===")
    
    # Run some initial cycles to establish baseline
    simics.SIM_continue(50)
    print(f"After initial 50 cycles: cycle_count = {simics.SIM_cycle_count(dev)}")
    
    # Set load value
    regs.WDOGLOAD.write(1000)
    print(f"WDOGLOAD set to 1000")
    
    # Enable timer (INTEN = 1)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    print(f"Timer enabled at cycle {simics.SIM_cycle_count(dev)}")
    
    # Check initial value after enable
    initial_value = regs.WDOGVALUE.read()
    print(f"Initial WDOGVALUE after enable: {initial_value}")
    stest.expect_equal(initial_value, 1000, "Counter loaded on enable")
    
    # Run some cycles and then check counter value
    simics.SIM_continue(100)
    print(f"After 100 more cycles: cycle_count = {simics.SIM_cycle_count(dev)}")
    counter_value = regs.WDOGVALUE.read()
    print(f"WDOGVALUE after 100 cycles: {counter_value}")
    stest.expect_equal(counter_value, 900, "Counter decremented after 100 cycles")
    
    print("Standalone timer test passed")

if __name__ == "__main__":
    test_timer_standalone()
