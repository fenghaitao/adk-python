#!/usr/bin/env python3
"""
Interrupt Generation Tests (TEST-004, TEST-005, TEST-006)
Tests interrupt generation on timeout, interrupt clear, and masked status
"""

import simics
import stest
import dev_util
import wdt_common

def test_interrupt_generation(dev, fake_pic_int):
    """TEST-004: Verify interrupt generation on first timeout"""
    print("\n=== TEST-004: Interrupt Generation ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Write small load value and enable
    regs.WDOGLOAD.write(20)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    
    # Wait for timeout
    simics.SIM_continue(30)
    
    # Check interrupt status registers
    ris = regs.WDOGRIS.read()
    stest.expect_equal(ris & 0x1, 1, "WDOGRIS[0] should be 1 after timeout")
    
    mis = regs.WDOGMIS.read()
    stest.expect_equal(mis & 0x1, 1, "WDOGMIS[0] should be 1 (masked interrupt)")
    
    # Check interrupt signal raised
    stest.expect_true(fake_pic_int.raised > 0,
                     f"Interrupt signal should be raised, count={fake_pic_int.raised}")
    
    print(f"[PASS] Interrupt generated: WDOGRIS={ris:#x}, WDOGMIS={mis:#x}, signal_count={fake_pic_int.raised}")

def test_interrupt_clear(dev, fake_pic_int):
    """TEST-005: Verify interrupt clear operation"""
    print("\n=== TEST-005: Interrupt Clear ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Trigger interrupt
    regs.WDOGLOAD.write(25)
    regs.WDOGCONTROL.write(0x1)
    simics.SIM_continue(35)
    
    # Verify interrupt set
    ris_before = regs.WDOGRIS.read()
    stest.expect_equal(ris_before & 0x1, 1, "Interrupt should be set before clear")
    
    raised_before = fake_pic_int.raised
    
    # Clear interrupt
    regs.WDOGINTCLR.write(1)
    
    # Verify interrupt cleared
    ris_after = regs.WDOGRIS.read()
    stest.expect_equal(ris_after & 0x1, 0, "WDOGRIS[0] should be 0 after clear")
    
    mis_after = regs.WDOGMIS.read()
    stest.expect_equal(mis_after & 0x1, 0, "WDOGMIS[0] should be 0 after clear")
    
    # Check counter reloaded
    counter_value = regs.WDOGVALUE.read()
    load_value = regs.WDOGLOAD.read()
    stest.expect_equal(counter_value, load_value,
                      f"Counter should reload to WDOGLOAD: counter={counter_value}, load={load_value}")
    
    # Signal should be lowered
    raised_after = fake_pic_int.raised
    stest.expect_equal(raised_after, raised_before - 1,
                      f"Signal should be lowered: before={raised_before}, after={raised_after}")
    
    print(f"[PASS] Interrupt cleared: WDOGRIS={ris_after:#x}, counter reloaded to {counter_value}")

def test_masked_interrupt_status(dev):
    """TEST-006: Verify WDOGMIS reflects masked interrupt status"""
    print("\n=== TEST-006: Masked Interrupt Status ===")
    regs = dev_util.bank_regs(dev.bank.wdt_map)
    
    # Setup: Trigger interrupt with INTEN=1
    regs.WDOGLOAD.write(15)
    regs.WDOGCONTROL.write(0x1)  # INTEN=1
    simics.SIM_continue(25)
    
    # Check both registers with INTEN=1
    ris = regs.WDOGRIS.read()
    mis_enabled = regs.WDOGMIS.read()
    stest.expect_equal(ris & 0x1, 1, "WDOGRIS[0] should be 1")
    stest.expect_equal(mis_enabled & 0x1, 1, "WDOGMIS[0] should be 1 when INTEN=1")
    
    # Disable interrupt (INTEN=0) without clearing WDOGRIS
    regs.WDOGCONTROL.write(0x0)  # INTEN=0
    
    # WDOGRIS should still be 1, but WDOGMIS should be 0
    ris_after = regs.WDOGRIS.read()
    mis_disabled = regs.WDOGMIS.read()
    stest.expect_equal(ris_after & 0x1, 1, "WDOGRIS[0] should still be 1")
    stest.expect_equal(mis_disabled & 0x1, 0, "WDOGMIS[0] should be 0 when INTEN=0")
    
    print(f"[PASS] Masked interrupt status correct: INTEN=1 -> MIS={mis_enabled:#x}, INTEN=0 -> MIS={mis_disabled:#x}")

def test_interrupt_generation_suite():
    """Main test entry point"""
    # Create device configuration
    devs = wdt_common.create_config()
    dev = devs[0]
    fake_pic_int = devs[1]
    
    # Run tests
    test_interrupt_generation(dev, fake_pic_int)
    test_interrupt_clear(dev, fake_pic_int)
    test_masked_interrupt_status(dev)
    
    print("\n=== ALL INTERRUPT GENERATION TESTS PASSED ===\n")

if __name__ == "__main__":
    test_interrupt_generation_suite()
