# © 2010 Intel Corporation

import simics

# Extend this function if your device requires any additional attributes to be
# set. It is often sensible to make additional arguments to this function
# optional, and let the function create mock objects if needed.
def create_watchdog_timer(name = None):
    '''Create a new watchdog_timer object'''
    watchdog_timer = simics.pre_conf_object(name, 'watchdog_timer')
    simics.SIM_add_configuration([watchdog_timer], None)
    return simics.SIM_get_object(watchdog_timer.name)
