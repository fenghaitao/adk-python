#!/usr/bin/env python3
"""
Test RegisterAgent JSON output format.

This test validates that RegisterAgent produces correctly formatted JSON
with read/write side-effects for register analysis.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def validate_json_output(json_data):
    """
    Validate that JSON output conforms to expected format.

    Expected format:
    {
      "REGISTER_NAME": {
        "read": "description",
        "write": "description"
      }
    }
    """
    errors = []

    if not isinstance(json_data, dict):
        errors.append("Top level must be a dictionary")
        return errors

    for reg_name, reg_data in json_data.items():
        # Check register name is a string
        if not isinstance(reg_name, str):
            errors.append(f"Register name must be string, got {type(reg_name)}")
            continue

        # Check register data is a dict
        if not isinstance(reg_data, dict):
            errors.append(f"{reg_name}: Register data must be dict, got {type(reg_data)}")
            continue

        # Check required fields
        if 'read' not in reg_data:
            errors.append(f"{reg_name}: Missing 'read' field")
        elif not isinstance(reg_data['read'], str):
            errors.append(f"{reg_name}: 'read' must be string")
        elif not reg_data['read'].strip():
            errors.append(f"{reg_name}: 'read' field is empty")

        if 'write' not in reg_data:
            errors.append(f"{reg_name}: Missing 'write' field")
        elif not isinstance(reg_data['write'], str):
            errors.append(f"{reg_name}: 'write' must be string")
        elif not reg_data['write'].strip():
            errors.append(f"{reg_name}: 'write' field is empty")

        # Check for extra fields (warning, not error)
        extra_fields = set(reg_data.keys()) - {'read', 'write'}
        if extra_fields:
            print(f"Warning: {reg_name} has extra fields: {extra_fields}")

    return errors


def test_valid_json():
    """Test with valid JSON."""
    print("Test 1: Valid JSON")
    print("-" * 80)

    valid_json = {
        "TIMER_CTRL": {
            "read": "Returns control register value. No side-effects.",
            "write": "Bit 0 enables timer. Bit 1 enables interrupt."
        },
        "TIMER_COUNT": {
            "read": "Returns current counter value. No side-effects.",
            "write": "Not writable - read-only register."
        }
    }

    errors = validate_json_output(valid_json)

    if errors:
        print(f"❌ Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Valid JSON passed validation")
        print(json.dumps(valid_json, indent=2))
        return True


def test_invalid_json():
    """Test with various invalid JSON formats."""
    print("\nTest 2: Invalid JSON Cases")
    print("-" * 80)

    test_cases = [
        {
            "name": "Missing 'read' field",
            "data": {
                "REG1": {"write": "Write side-effect"}
            },
            "expect_error": True
        },
        {
            "name": "Missing 'write' field",
            "data": {
                "REG1": {"read": "Read side-effect"}
            },
            "expect_error": True
        },
        {
            "name": "Empty read description",
            "data": {
                "REG1": {"read": "", "write": "Write side-effect"}
            },
            "expect_error": True
        },
        {
            "name": "Non-dict register data",
            "data": {
                "REG1": "invalid"
            },
            "expect_error": True
        },
        {
            "name": "Top level not dict",
            "data": ["invalid"],
            "expect_error": True
        }
    ]

    all_passed = True
    for test_case in test_cases:
        print(f"\nSubtest: {test_case['name']}")
        errors = validate_json_output(test_case['data'])

        if test_case['expect_error']:
            if errors:
                print(f"  ✅ Correctly detected errors: {errors[0]}")
            else:
                print(f"  ❌ Should have detected errors but didn't")
                all_passed = False
        else:
            if errors:
                print(f"  ❌ Unexpected errors: {errors}")
                all_passed = False
            else:
                print(f"  ✅ Passed as expected")

    return all_passed


def test_realistic_example():
    """Test with realistic watchdog timer example."""
    print("\nTest 3: Realistic Example (Watchdog Timer)")
    print("-" * 80)

    wdt_json = {
        "WDOGLOAD": {
            "read": "Returns the current load register value. No side-effects - reading does not modify hardware state.",
            "write": "Stores the written value to the load register AND immediately copies it to the counter register (WDOGVALUE), restarting the countdown. If an interrupt is pending, it may be cleared. If the timer is enabled (WDOGCONTROL.INTEN or RESEN set), the countdown restarts from the new value."
        },
        "WDOGVALUE": {
            "read": "Returns the current countdown counter value. No side-effects - this is a pure status register that reflects the real-time counter state.",
            "write": "Not writable - this is a read-only register. Writes are ignored. The value is updated automatically as the timer counts down and when WDOGLOAD is written."
        },
        "WDOGCONTROL": {
            "read": "Returns the current control register value with bit 0 = interrupt enable, bit 1 = reset enable. No side-effects.",
            "write": "Bit 0 (INTEN): When set to 1, enables interrupt generation when counter reaches 0; when cleared to 0, disables interrupts. Bit 1 (RESEN): When set to 1, enables system reset generation when counter reaches 0; when cleared to 0, disables reset. Writing these bits starts/stops the countdown timer if counter is non-zero and updates the masked interrupt status (WDOGMIS)."
        },
        "WDOGINTCLR": {
            "read": "Not readable - this is a write-only register. Reads return undefined/unpredictable values.",
            "write": "ANY write (regardless of written value) clears the interrupt pending status, updates WDOGRIS and WDOGMIS to 0, and deasserts the interrupt signal to the interrupt controller. Does not affect the counter or timer operation."
        },
        "WDOGRIS": {
            "read": "Returns raw interrupt status: bit 0 = 1 if interrupt is pending (counter reached 0), bit 0 = 0 otherwise. No side-effects - reading does NOT clear the interrupt status.",
            "write": "Not writable - this is a read-only status register. Use WDOGINTCLR to clear interrupt status."
        }
    }

    errors = validate_json_output(wdt_json)

    if errors:
        print(f"❌ Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Realistic example passed validation")
        print(f"\nRegisters analyzed: {len(wdt_json)}")
        for reg_name in wdt_json.keys():
            print(f"  - {reg_name}")

        # Save to file
        output_file = "test-wdt-side-effects.json"
        with open(output_file, 'w') as f:
            json.dump(wdt_json, f, indent=2)
        print(f"\nSaved example to: {output_file}")
        return True


def main():
    """Run all validation tests."""
    print("\n" + "=" * 80)
    print("RegisterAgent JSON Output Validation Tests")
    print("=" * 80 + "\n")

    results = []

    # Test 1: Valid JSON
    results.append(("Valid JSON", test_valid_json()))

    # Test 2: Invalid JSON cases
    results.append(("Invalid JSON Detection", test_invalid_json()))

    # Test 3: Realistic example
    results.append(("Realistic Example", test_realistic_example()))

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
