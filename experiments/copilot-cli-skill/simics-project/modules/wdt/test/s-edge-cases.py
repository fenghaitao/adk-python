#!/usr/bin/env python3
"""
Edge Case Tests (TEST-016, TEST-017, TEST-018, TEST-019, TEST-020)
Tests edge cases: INTEN=0, maximum value, zero value, read-only registers, ID registers
"""

import simics
import stest
import dev_util
import wdt_common

def test_inten_disabled(dev):
    """TEST-016: Verify behavior with INTEN=0"""
    print("\n=== TEST-016: INTEN=0 Behavior ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Write load value but keep INTEN=0
    regs.WDOGLOAD.write(100)
    regs.WDOGCONTROL.write(0x0)  # INTEN=0
    
    # Save counter value
    value_before = regs.WDOGVALUE.read()
    stest.expect_equal(value_before, 100, "Counter should equal WDOGLOAD")
    
    # Advance simulation
    simics.SIM_continue(50)
    
    # Counter should remain static
    value_after = regs.WDOGVALUE.read()
    stest.expect_equal(value_after, value_before,
                      f"Counter should not change when INTEN=0: before={value_before}, after={value_after}")
    
    print(f"[PASS] Counter static when INTEN=0: {value_after}")

def test_maximum_counter_value(dev):
    """TEST-017: Verify maximum counter value handling"""
    print("\n=== TEST-017: Maximum Counter Value ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Write maximum 32-bit value
    max_value = 0xFFFFFFFF
    regs.WDOGLOAD.write(max_value)
    
    value = regs.WDOGVALUE.read()
    stest.expect_equal(value, max_value, f"Counter should accept maximum value: {value:#x}")
    
    # Enable timer
    regs.WDOGCONTROL.write(0x1)
    
    # Advance simulation
    simics.SIM_continue(100)
    
    # Counter should decrement from maximum
    value_after = regs.WDOGVALUE.read()
    stest.expect_true(value_after < max_value,
                     f"Counter should decrement from max: max={max_value:#x}, after={value_after:#x}")
    
    print(f"[PASS] Maximum counter value handled correctly: {max_value:#x} -> {value_after:#x}")

def test_zero_load_value(dev, fake_pic_int):
    """TEST-018: Verify zero load value handling"""
    print("\n=== TEST-018: Zero Load Value ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Write zero to load
    regs.WDOGLOAD.write(0)
    value = regs.WDOGVALUE.read()
    stest.expect_equal(value, 0, "Counter should be 0")
    
    int_count_before = fake_pic_int.raised
    
    # Enable timer
    regs.WDOGCONTROL.write(0x1)
    
    # Advance simulation - should timeout immediately or very quickly
    simics.SIM_continue(10)
    
    # Check interrupt generated
    ris = regs.WDOGRIS.read()
    stest.expect_equal(ris & 0x1, 1, "Interrupt should be generated for zero load value")
    
    int_count_after = fake_pic_int.raised
    stest.expect_true(int_count_after > int_count_before,
                     f"Interrupt signal should be raised: before={int_count_before}, after={int_count_after}")
    
    print(f"[PASS] Zero load value causes immediate timeout")

def test_readonly_registers(dev):
    """TEST-019: Verify register read-only enforcement"""
    print("\n=== TEST-019: Read-Only Registers ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Trigger interrupt to set WDOGRIS
    regs.WDOGLOAD.write(10)
    regs.WDOGCONTROL.write(0x1)
    simics.SIM_continue(20)
    
    # Read current values
    value_before = regs.WDOGVALUE.read()
    ris_before = regs.WDOGRIS.read()
    mis_before = regs.WDOGMIS.read()
    
    # Attempt writes to read-only registers (should be ignored)
    regs.WDOGVALUE.write(0x12345678)
    regs.WDOGRIS.write(0)
    regs.WDOGMIS.write(0)
    
    # Verify values unchanged
    value_after = regs.WDOGVALUE.read()
    ris_after = regs.WDOGRIS.read()
    mis_after = regs.WDOGMIS.read()
    
    stest.expect_equal(value_after, value_before,
                      f"WDOGVALUE should be read-only: before={value_before}, after={value_after}")
    stest.expect_equal(ris_after, ris_before,
                      f"WDOGRIS should be read-only: before={ris_before}, after={ris_after}")
    stest.expect_equal(mis_after, mis_before,
                      f"WDOGMIS should be read-only: before={mis_before}, after={mis_after}")
    
    print(f"[PASS] Read-only registers cannot be written")

def test_peripheral_id_registers(dev):
    """TEST-020: Verify peripheral/PrimeCell ID registers"""
    print("\n=== TEST-020: Peripheral ID Registers ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Read ID registers
    periphid0 = regs.WDOGPeriphID0.read()
    periphid1 = regs.WDOGPeriphID1.read()
    periphid2 = regs.WDOGPeriphID2.read()
    periphid3 = regs.WDOGPeriphID3.read()
    
    pcellid0 = regs.WDOGPCellID0.read()
    pcellid1 = regs.WDOGPCellID1.read()
    pcellid2 = regs.WDOGPCellID2.read()
    pcellid3 = regs.WDOGPCellID3.read()
    
    # Verify PrimeCell ID (should be 0xB105F00D)
    pcell_id = (pcellid3 << 24) | (pcellid2 << 16) | (pcellid1 << 8) | pcellid0
    stest.expect_equal(pcell_id, 0xB105F00D,
                      f"PrimeCell ID should be 0xB105F00D, got {pcell_id:#x}")
    
    # Verify PeriphID part number (lower 12 bits should be 0x805 for SP805)
    periph_id = (periphid3 << 24) | (periphid2 << 16) | (periphid1 << 8) | periphid0
    part_number = periph_id & 0xFFF
    stest.expect_equal(part_number, 0x805,
                      f"Part number should be 0x805, got {part_number:#x}")
    
    print(f"[PASS] ID registers correct: PrimeCell={pcell_id:#x}, PeriphID={periph_id:#x}")

def test_edge_cases_suite():
    """Main test entry point"""
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    
    # Run tests
    test_inten_disabled(dev)
    test_maximum_counter_value(dev)
    test_zero_load_value(dev, fake_pic_int)
    test_readonly_registers(dev)
    test_peripheral_id_registers(dev)
    
    print("\n=== ALL EDGE CASE TESTS PASSED ===\n")

if __name__ == "__main__":
    test_edge_cases_suite()
