# Performance tests for the watchdog timer device
import dev_util
import simics
import time

# Test register access performance
def test_register_access_performance():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer_perf')
    
    # Test WDOGLOAD register access performance
    load_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0000, size=4)
    
    # Measure read performance
    start_time = time.time()
    for i in range(10000):
        value = load_reg.read()
    read_time = time.time() - start_time
    
    # Measure write performance
    start_time = time.time()
    for i in range(10000):
        load_reg.write(i & 0xFFFFFFFF)
    write_time = time.time() - start_time
    
    print(f"Register read performance: {read_time:.4f} seconds for 10000 reads ({read_time/10000*1000:.4f} ms per read)")
    print(f"Register write performance: {write_time:.4f} seconds for 10000 writes ({write_time/10000*1000:.4f} ms per write)")
    
    # Check that performance is within acceptable limits (< 200ms for 10000 operations)
    assert read_time < 0.2, f"Read performance too slow: {read_time:.4f} seconds"
    assert write_time < 0.2, f"Write performance too slow: {write_time:.4f} seconds"
    
    print("Register access performance tests passed")

# Test control register performance
def test_control_register_performance():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer_perf2')
    
    # Test WDOGCONTROL register access performance
    control_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0008, size=4)
    
    # Measure read performance
    start_time = time.time()
    for i in range(10000):
        value = control_reg.read()
    read_time = time.time() - start_time
    
    # Measure write performance
    start_time = time.time()
    for i in range(10000):
        control_reg.write((i & 0x1F) | 0x1F)  # Use valid control values
    write_time = time.time() - start_time
    
    print(f"Control register read performance: {read_time:.4f} seconds for 10000 reads ({read_time/10000*1000:.4f} ms per read)")
    print(f"Control register write performance: {write_time:.4f} seconds for 10000 writes ({write_time/10000*1000:.4f} ms per write)")
    
    # Check that performance is within acceptable limits (< 200ms for 10000 operations)
    assert read_time < 0.2, f"Control register read performance too slow: {read_time:.4f} seconds"
    assert write_time < 0.2, f"Control register write performance too slow: {write_time:.4f} seconds"
    
    print("Control register performance tests passed")

# Test lock register performance
def test_lock_register_performance():
    # Create the watchdog timer device
    watchdog_dev = simics.SIM_create_object('watchdog_timer', 'watchdog_timer_perf3')
    
    # Test WDOGLOCK register access performance
    lock_reg = dev_util.Register_LE(watchdog_dev.bank.regs, 0x0C00, size=4)
    
    # Measure read performance
    start_time = time.time()
    for i in range(10000):
        value = lock_reg.read()
    read_time = time.time() - start_time
    
    # Measure write performance (alternating between lock and unlock)
    start_time = time.time()
    for i in range(10000):
        if i % 2 == 0:
            lock_reg.write(0x1ACCE551)  # Unlock
        else:
            lock_reg.write(0x00000001)  # Lock
    write_time = time.time() - start_time
    
    print(f"Lock register read performance: {read_time:.4f} seconds for 10000 reads ({read_time/10000*1000:.4f} ms per read)")
    print(f"Lock register write performance: {write_time:.4f} seconds for 10000 writes ({write_time/10000*1000:.4f} ms per write)")
    
    # Check that performance is within acceptable limits (< 200ms for 10000 operations)
    assert read_time < 0.2, f"Lock register read performance too slow: {read_time:.4f} seconds"
    assert write_time < 0.2, f"Lock register write performance too slow: {write_time:.4f} seconds"
    
    print("Lock register performance tests passed")

# Run all performance tests
def run_all_performance_tests():
    test_register_access_performance()
    test_control_register_performance()
    test_lock_register_performance()
    print("All performance tests completed successfully")

# Execute the tests
if __name__ == "__main__":
    run_all_performance_tests()