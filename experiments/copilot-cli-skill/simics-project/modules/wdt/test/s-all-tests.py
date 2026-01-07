#!/usr/bin/env python3
"""
Comprehensive WDT Test Suite Runner
Runs all test suites and reports results
"""

import simics
import sys

def run_test_suite(test_name, test_func):
    """Run a test suite and catch exceptions"""
    try:
        print(f"\n{'='*70}")
        print(f"Running: {test_name}")
        print(f"{'='*70}")
        test_func()
        print(f"✓ {test_name} PASSED")
        return True
    except Exception as e:
        print(f"✗ {test_name} FAILED: {e}")
        return False

def main():
    """Run all test suites"""
    results = []
    
    # Import test modules
    import sys
    sys.path.insert(0, 'modules/wdt/test')
    
    # Test suite 1: Basic tests
    import importlib
    s_basic = importlib.import_module('s-basic')
    results.append(run_test_suite("Basic Tests (s-basic.py)", s_basic.test_basic))
    
    # Test suite 2: Countdown timer
    s_countdown = importlib.import_module('s-countdown-timer')
    results.append(run_test_suite("Countdown Timer Tests (s-countdown-timer.py)", 
                                  s_countdown.test_countdown_timer))
    
    # Test suite 3: Interrupt generation
    s_interrupt = importlib.import_module('s-interrupt-generation')
    results.append(run_test_suite("Interrupt Generation Tests (s-interrupt-generation.py)", 
                                  s_interrupt.test_interrupt_generation_suite))
    
    # Test suite 4: Reset generation
    s_reset = importlib.import_module('s-reset-generation')
    results.append(run_test_suite("Reset Generation Tests (s-reset-generation.py)", 
                                  s_reset.test_reset_generation_suite))
    
    # Test suite 5: Lock protection
    s_lock = importlib.import_module('s-lock-protection')
    results.append(run_test_suite("Lock Protection Tests (s-lock-protection.py)", 
                                  s_lock.test_lock_protection_suite))
    
    # Test suite 6: Integration test mode
    s_itm = importlib.import_module('s-integration-test-mode')
    results.append(run_test_suite("Integration Test Mode Tests (s-integration-test-mode.py)", 
                                  s_itm.test_integration_test_mode_suite))
    
    # Test suite 7: Edge cases
    s_edge = importlib.import_module('s-edge-cases')
    results.append(run_test_suite("Edge Cases Tests (s-edge-cases.py)", 
                                  s_edge.test_edge_cases_suite))
    
    # Print summary
    print(f"\n{'='*70}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*70}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓✓✓ ALL TEST SUITES PASSED ✓✓✓\n")
        return 0
    else:
        print(f"\n✗✗✗ {total - passed} TEST SUITE(S) FAILED ✗✗✗\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
