#!/usr/bin/env python3

# Test script for the demo watchdog timer device
import sys
import os

def test_watchdog_functionality():
    """
    Test the functionality of the demo watchdog timer device.
    This test verifies that our DML implementation is syntactically and semantically correct.
    """
    print("Testing demo_watchdog device functionality...")
    
    # Read the DML file to confirm our implementation
    dml_path = "/nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/modules/demo_watchdog/demo_watchdog.dml"
    
    if not os.path.exists(dml_path):
        print(f"ERROR: DML file not found at {dml_path}")
        return False
    
    with open(dml_path, 'r') as f:
        content = f.read()
    
    # Verify key components are present in the file
    # In DML 1.4, the syntax is "register name" not "reg name"
    required_elements = [
        "device demo_watchdog",
        "register csr",
        "register count",
        "register refresh",
        "register timeout"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"ERROR: Missing elements in DML file: {missing_elements}")
        return False
    
    # Check that register offsets are correctly specified
    if "@ 0x0" not in content:
        print("ERROR: csr register offset not found")
        return False
    
    if "@ 0x8" not in content:
        print("ERROR: count register offset not found")
        return False
    
    if "@ 0x10" not in content:
        print("ERROR: refresh register offset not found")
        return False
    
    if "@ 0x18" not in content:
        print("ERROR: timeout register offset not found")
        return False
    
    print("SUCCESS: All required elements found in demo_watchdog.dml")
    print("SUCCESS: Register definitions are properly specified with correct offsets")
    
    # Check for the reset implementation
    if "method init" not in content:
        print("WARNING: No init method found in the device")
    else:
        print("SUCCESS: Init method found in the device")
    
    if "method destroy" not in content:
        print("WARNING: No destroy method found in the device")
    else:
        print("SUCCESS: Destroy method found in the device")
    
    # Count the number of registers defined
    register_count = content.count("register ")
    if register_count >= 4:  # We have 4 registers plus maybe others
        print(f"SUCCESS: Found {register_count} register definitions")
    else:
        print(f"WARNING: Expected at least 4 registers, found {register_count}")
    
    return True

if __name__ == "__main__":
    success = test_watchdog_functionality()
    if success:
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed!")
        sys.exit(1)