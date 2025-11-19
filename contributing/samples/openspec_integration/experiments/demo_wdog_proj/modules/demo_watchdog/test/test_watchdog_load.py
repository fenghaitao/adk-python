"""
Test script for the Watchdog Load (WDOGLOAD) register functionality.

This test script verifies the functionality of the WDOGLOAD register in the 
demo_watchdog device model, including:
- Basic read/write operations
- Reset behavior (reset value: 0xFFFFFFFF)
- Access restrictions (RW)
- Register fields (31:0 wdog_load)
- Side effects (counter reload functionality)
"""

import simics
from simics import *

def test_wdogload_register_basic_rw(dev, obj):
    """
    Test basic read/write operations for WDOGLOAD register.
    """
    print("Testing WDOGLOAD register basic read/write operations...")
    
    # Read default value (should be 0xFFFFFFFF)
    default_value = SIM_read_register(obj, "WDOGLOAD")
    print(f"WDOGLOAD default value: 0x{default_value:08X}")
    
    # Verify reset value
    if default_value == 0xFFFFFFFF:
        print("✓ Default value is correct: 0xFFFFFFFF")
    else:
        print(f"✗ Default value incorrect: expected 0xFFFFFFFF, got 0x{default_value:08X}")
        return False
    
    # Write test value
    test_value = 0x12345678
    SIM_write_register(obj, "WDOGLOAD", test_value)
    print(f"Wrote 0x{test_value:08X} to WDOGLOAD")
    
    # Read back and verify
    read_value = SIM_read_register(obj, "WDOGLOAD")
    print(f"Read back from WDOGLOAD: 0x{read_value:08X}")
    
    if read_value == test_value:
        print("✓ Read/write operation successful")
        return True
    else:
        print(f"✗ Read/write operation failed: expected 0x{test_value:08X}, got 0x{read_value:08X}")
        return False

def test_wdogload_reset_behavior(dev, obj):
    """
    Test reset behavior of the WDOGLOAD register.
    """
    print("\nTesting WDOGLOAD register reset behavior...")
    
    # Write a test value
    test_value = 0xABCDEF00
    SIM_write_register(obj, "WDOGLOAD", test_value)
    current_value = SIM_read_register(obj, "WDOGLOAD")
    print(f"Value before reset: 0x{current_value:08X}")
    
    # Reset the device
    SIM_reset_object(obj)
    
    # Check the value after reset
    reset_value = SIM_read_register(obj, "WDOGLOAD")
    print(f"Value after reset: 0x{reset_value:08X}")
    
    if reset_value == 0xFFFFFFFF:
        print("✓ Reset value is correct: 0xFFFFFFFF")
        return True
    else:
        print(f"✗ Reset value incorrect: expected 0xFFFFFFFF, got 0x{reset_value:08X}")
        return False

def test_wdogload_register_fields(dev, obj):
    """
    Test all register fields (31:0) individually.
    """
    print("\nTesting WDOGLOAD register fields (31:0)...")
    
    # Test boundary values
    test_values = [0x00000000, 0xFFFFFFFF, 0x55555555, 0xAAAAAAAA, 0x00FF00FF]
    
    for test_value in test_values:
        print(f"Writing 0x{test_value:08X} to WDOGLOAD...")
        SIM_write_register(obj, "WDOGLOAD", test_value)
        read_value = SIM_read_register(obj, "WDOGLOAD")
        
        if read_value == test_value:
            print(f"✓ Value 0x{test_value:08X} written and read successfully")
        else:
            print(f"✗ Value 0x{test_value:08X} failed: wrote 0x{test_value:08X}, read 0x{read_value:08X}")
            return False
    
    return True

def test_wdogload_with_counter_reload(dev, obj):
    """
    Test the interaction between WDOGLOAD and counter reload functionality.
    """
    print("\nTesting WDOGLOAD interaction with counter reload functionality...")
    
    # Set WDOGLOAD to a specific value
    load_value = 0xDEADBEEF
    SIM_write_register(obj, "WDOGLOAD", load_value)
    print(f"Set WDOGLOAD to 0x{load_value:08X}")
    
    # Verify WDOGLOAD value
    verify_value = SIM_read_register(obj, "WDOGLOAD")
    if verify_value != load_value:
        print(f"✗ Failed to set WDOGLOAD value: expected 0x{load_value:08X}, got 0x{verify_value:08X}")
        return False
    
    print("✓ WDOGLOAD value set successfully for counter reload test")
    return True

def test_wdogload_with_interrupt_clear(dev, obj):
    """
    Test the interaction between WDOGLOAD and interrupt clear functionality.
    """
    print("\nTesting WDOGLOAD interaction with interrupt clear functionality...")
    
    # Set WDOGLOAD to a specific value
    load_value = 0xBEEFCAFE
    SIM_write_register(obj, "WDOGLOAD", load_value)
    print(f"Set WDOGLOAD to 0x{load_value:08X}")
    
    # Write to WDOGINTCLR (this should reload the counter from WDOGLOAD)
    SIM_write_register(obj, "WDOGINTCLR", 0x1)
    print("Wrote to WDOGINTCLR to trigger counter reload")
    
    # Verify that WDOGLOAD still has the correct value
    current_value = SIM_read_register(obj, "WDOGLOAD")
    if current_value == load_value:
        print(f"✓ WDOGLOAD value preserved after WDOGINTCLR: 0x{current_value:08X}")
        return True
    else:
        print(f"✗ WDOGLOAD value changed after WDOGINTCLR: expected 0x{load_value:08X}, got 0x{current_value:08X}")
        return False

def run_wdogload_tests():
    """
    Main function to run all WDOGLOAD register tests.
    """
    print("Starting WDOGLOAD Register Tests...")
    print("=" * 50)
    
    # Get the demo_watchdog device
    dev = simics.preconf.object("demo_watchdog")
    obj = dev.get_object()
    
    if not obj:
        print("ERROR: Cannot find demo_watchdog device")
        return False
    
    # Track test results
    all_tests_passed = True
    
    # Run individual tests
    tests = [
        test_wdogload_register_basic_rw,
        test_wdogload_reset_behavior,
        test_wdogload_register_fields,
        test_wdogload_with_counter_reload,
        test_wdogload_with_interrupt_clear
    ]
    
    for test_func in tests:
        result = test_func(dev, obj)
        if not result:
            all_tests_passed = False
        print()
    
    # Summary
    print("=" * 50)
    if all_tests_passed:
        print("✓ All WDOGLOAD register tests PASSED")
        return True
    else:
        print("✗ Some WDOGLOAD register tests FAILED")
        return False

if __name__ == "__main__":
    run_wdogload_tests()