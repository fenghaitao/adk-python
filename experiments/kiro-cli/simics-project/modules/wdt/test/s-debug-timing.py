# Debug test to understand timing issues

import dev_util
import simics
import conf
import stest
import wdt_common

def debug_timing():
    """Debug timing and cycle counting"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    print(f"Initial cycle count: {simics.SIM_cycle_count(dev)}")
    print(f"Initial time: {simics.SIM_time(dev)}")
    
    # Run some cycles
    simics.SIM_continue(100)
    
    print(f"After 100 steps - cycle count: {simics.SIM_cycle_count(dev)}")
    print(f"After 100 steps - time: {simics.SIM_time(dev)}")
    
    # Set load value and enable timer
    regs.WDOGLOAD.write(1000)
    print(f"After WDOGLOAD write - cycle count: {simics.SIM_cycle_count(dev)}")
    
    # Read initial counter value
    initial_value = regs.WDOGVALUE.read()
    print(f"Initial WDOGVALUE: {initial_value}")
    
    # Enable timer
    regs.WDOGCONTROL.write(0x1)
    print(f"After WDOGCONTROL write - cycle count: {simics.SIM_cycle_count(dev)}")
    
    # Read counter after enable
    after_enable = regs.WDOGVALUE.read()
    print(f"WDOGVALUE after enable: {after_enable}")
    
    # Run more cycles
    simics.SIM_continue(50)
    print(f"After 50 more steps - cycle count: {simics.SIM_cycle_count(dev)}")
    
    # Read counter after running
    after_run = regs.WDOGVALUE.read()
    print(f"WDOGVALUE after running: {after_run}")
    
    print("Debug timing test complete")

if __name__ == "__main__":
    debug_timing()
