# Simple test to debug timer behavior

import dev_util
import simics
import conf
import stest
import wdt_common

def simple_timer_test():
    """Simple test to debug timer behavior"""
    devs = wdt_common.create_config()
    dev = devs[0]
    pic_int = devs[1]
    pic_res = devs[2]
    
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    print("=== Simple Timer Test ===")
    
    # Run initial cycles
    simics.SIM_continue(50)
    print(f"After initial 50 cycles: cycle_count = {simics.SIM_cycle_count(dev)}")
    
    # Set load value
    regs.WDOGLOAD.write(1000)
    print(f"WDOGLOAD set to 1000")
    
    # Check initial WDOGVALUE
    initial_value = regs.WDOGVALUE.read()
    print(f"Initial WDOGVALUE: {initial_value}")
    
    # Enable timer
    regs.WDOGCONTROL.write(0x1)
    print(f"Timer enabled, cycle_count = {simics.SIM_cycle_count(dev)}")
    
    # Check WDOGVALUE immediately after enable
    after_enable = regs.WDOGVALUE.read()
    print(f"WDOGVALUE after enable: {after_enable}")
    
    # Run 100 cycles
    simics.SIM_continue(100)
    print(f"After 100 more cycles: cycle_count = {simics.SIM_cycle_count(dev)}")
    
    # Check WDOGVALUE after cycles
    after_cycles = regs.WDOGVALUE.read()
    print(f"WDOGVALUE after 100 cycles: {after_cycles}")
    
    # Check if timer is still enabled
    control_val = regs.WDOGCONTROL.read()
    print(f"WDOGCONTROL value: 0x{control_val:x}")
    
    print("=== End Simple Timer Test ===")

if __name__ == "__main__":
    simple_timer_test()
