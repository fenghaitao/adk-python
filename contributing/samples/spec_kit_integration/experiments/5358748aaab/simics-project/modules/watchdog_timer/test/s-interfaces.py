# Tests for watchdog timer interface behavior
# Copyright (c) 2024 Intel Corporation

import stest
import dev_util
import simics

# Create device instance with interfaces
def create_watchdog_device():
    # Delete any existing objects with the same names
    try:
        simics.SIM_delete_object(simics.SIM_get_object("wdt"))
    except:
        pass
    try:
        simics.SIM_delete_object(simics.SIM_get_object("clk_en"))
    except:
        pass
    try:
        simics.SIM_delete_object(simics.SIM_get_object("rst_in"))
    except:
        pass
    
    # Create the watchdog timer device
    wdt = simics.SIM_create_object("watchdog_timer", "wdt", [])
    
    # Create clock enable signal
    clk_en = simics.pre_conf_object("clk_en", "signal")
    simics.SIM_add_configuration([clk_en], None)
    clk_en_obj = simics.SIM_get_object("clk_en")
    wdt.wclk_en = clk_en_obj
    
    # Create reset input signal
    rst_in = simics.pre_conf_object("rst_in", "signal")
    simics.SIM_add_configuration([rst_in], None)
    rst_in_obj = simics.SIM_get_object("rst_in")
    wdt.wrst_n = rst_in_obj
    
    return wdt, clk_en_obj, rst_in_obj

# Test clock enable interface
def test_clock_enable_interface():
    wdt, clk_en, rst_in = create_watchdog_device()
    
    # Initially clock should be disabled
    clk_en.signal_lower()
    
    # Enable the clock
    clk_en.signal_raise()
    
    # Disable the clock
    clk_en.signal_lower()

# Test reset input interface
def test_reset_input_interface():
    wdt, clk_en, rst_in = create_watchdog_device()
    
    # Assert reset (active low)
    rst_in.signal_lower()
    
    # Deassert reset
    rst_in.signal_raise()

# Run all tests
test_clock_enable_interface()
test_reset_input_interface()

print("All interface behavior tests passed!")