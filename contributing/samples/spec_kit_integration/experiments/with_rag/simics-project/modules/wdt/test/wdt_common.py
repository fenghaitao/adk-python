# © 2010 Intel Corporation

import simics

# Extend this function if your device requires any additional attributes to be
# set. It is often sensible to make additional arguments to this function
# optional, and let the function create mock objects if needed.
def create_wdt(name = None):
    '''Create a new wdt object'''
    wdt = simics.pre_conf_object(name, 'wdt')
    wdt.irq_level = 0  # Set the required irq_level attribute
    
    # Create a clock for the queue attribute
    clock = simics.pre_conf_object('clock', 'clock')
    clock.freq_mhz = 1000  # 1 GHz clock
    wdt.queue = clock
    
    simics.SIM_add_configuration([clock, wdt], None)
    return simics.SIM_get_object(wdt.name)