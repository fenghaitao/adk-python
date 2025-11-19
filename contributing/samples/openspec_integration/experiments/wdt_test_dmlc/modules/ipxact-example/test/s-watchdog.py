# INTEL CONFIDENTIAL

# © 2024 Intel Corporation
#
# This software and the related documents are Intel copyrighted materials, and
# your use of them is governed by the express license under which they were
# provided to you ("License"). Unless the License provides otherwise, you may
# not use, modify, copy, publish, distribute, disclose or transmit this software
# or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.

"""
Watchdog Timer Side Effects Test
This script demonstrates all the side effects implemented in ipxact-example.dml
"""

import dev_util
import stest

print("=" * 70)
print("Watchdog Timer Side Effects Test")
print("=" * 70)
print()

# Create the watchdog device
wdt = SIM_create_object('ipxact_example', 'wdt')
bank = dev_util.bank_regs(wdt.bank.watchdog_memap)

# Get register handles
WDOGLOAD = bank.WDOGLOAD
WDOGVALUE = bank.WDOGVALUE
WDOGCONTROL = bank.WDOGCONTROL
WDOGINTCLR = bank.WDOGINTCLR
WDOGLOCK = bank.WDOGLOCK

print("Created watchdog device: wdt")
print()

# TEST 1: Initial Register Values
print("TEST 1: Initial Register Values")
print("-" * 70)

# Check WDOGVALUE initial value (should be 0xFFFFFFFF per DML)
value = WDOGVALUE.read()
print(f"WDOGVALUE = 0x{value:08x} (expected 0xFFFFFFFF)")
stest.expect_equal(value, 0xFFFFFFFF)

# Check WDOGCONTROL initial value (should be 0x0)
control = WDOGCONTROL.read()
print(f"WDOGCONTROL = 0x{control:08x} (expected 0x00000000)")
stest.expect_equal(control, 0x0)

# Check WDOGLOCK initial value (should be 1 = locked)
lock = WDOGLOCK.read()
print(f"WDOGLOCK = {lock} (expected 1 = locked)")
stest.expect_equal(lock, 1)

print("✓ PASS: Initial values correct")
print()

# TEST 2: Unlock Side Effect
print("TEST 2: Unlock Side Effect")
print("-" * 70)

print("Writing unlock key 0x1ACCE551 to WDOGLOCK...")
WDOGLOCK.write(0x1ACCE551)

# Read back - should now be 0 (unlocked)
lock = WDOGLOCK.read()
print(f"WDOGLOCK = {lock} (expected 0 = unlocked)")
stest.expect_equal(lock, 0)

print("✓ PASS: Unlock side effect working (wdt_unlocked = true)")
print()

# TEST 3: Load Counter Value
print("TEST 3: Load Counter Value")
print("-" * 70)

print("Writing 0x00001000 to WDOGLOAD...")
WDOGLOAD.write(0x1000)

load_val = WDOGLOAD.read()
print(f"WDOGLOAD = 0x{load_val:08x}")
stest.expect_equal(load_val, 0x1000)

# WDOGVALUE should also be updated to the load value
value = WDOGVALUE.read()
print(f"WDOGVALUE = 0x{value:08x} (should match WDOGLOAD)")
stest.expect_equal(value, 0x1000)

print("✓ PASS: Load value written and counter updated")
print()

# TEST 4: Enable Timer Side Effect
print("TEST 4: Enable Timer Side Effect")
print("-" * 70)

print("Setting INTEN bit (bit 0) in WDOGCONTROL...")
WDOGCONTROL.write(0x01)

control = WDOGCONTROL.read()
print(f"WDOGCONTROL = 0x{control:08x}")
stest.expect_equal(control & 0x1, 0x1)

print("✓ PASS: Timer enabled (wdt_enabled=true, timer event posted)")
print()

# TEST 5: Counter Decrement Side Effect
print("TEST 5: Counter Decrement Side Effect")
print("-" * 70)

print("Reading counter before time advance...")
counter_before = WDOGVALUE.read()
print(f"WDOGVALUE before = 0x{counter_before:08x}")

print("Advancing simulation time by 1000 cycles...")
SIM_continue(1000)

print("Reading counter after time advance...")
counter_after = WDOGVALUE.read()
print(f"WDOGVALUE after  = 0x{counter_after:08x}")

# The counter should have decremented
stest.expect_true(counter_after < counter_before,
                  "Counter should have decremented")

decrement = counter_before - counter_after
print(f"✓ PASS: Counter decremented by {decrement}!")
print("  (tick_watchdog() side effect is working!)")
print()

# TEST 6: Interrupt Clear Side Effect
print("TEST 6: Interrupt Clear Side Effect")
print("-" * 70)

print("Writing to WDOGINTCLR (any value clears interrupt and reloads)...")
WDOGINTCLR.write(0x12345678)

# Counter should be reloaded to the WDOGLOAD value
counter_reload = WDOGVALUE.read()
load_val = WDOGLOAD.read()
print(f"WDOGVALUE after INTCLR = 0x{counter_reload:08x}")
print(f"WDOGLOAD = 0x{load_val:08x}")
stest.expect_equal(counter_reload, load_val)

print("✓ PASS: Counter reloaded (interrupt clear side effect working!)")
print()

# TEST 7: Disable Timer Side Effect
print("TEST 7: Disable Timer Side Effect")
print("-" * 70)

print("Clearing INTEN bit to disable timer...")
WDOGCONTROL.write(0x00)

control = WDOGCONTROL.read()
print(f"WDOGCONTROL = 0x{control:08x}")
stest.expect_equal(control & 0x1, 0x0)

# After disabling, counter should not decrement
print("Reading counter before time advance...")
counter_before = WDOGVALUE.read()
print(f"WDOGVALUE before = 0x{counter_before:08x}")

print("Advancing time by 1000 cycles...")
SIM_continue(1000)

counter_after = WDOGVALUE.read()
print(f"WDOGVALUE after  = 0x{counter_after:08x}")

# Counter should be the same (not decremented)
stest.expect_equal(counter_after, counter_before,
                   "Counter should not decrement when disabled")

print("✓ PASS: Timer disabled (wdt_enabled=false, counter not decrementing)")
print()

# TEST 8: Re-enable and Verify Counter Decrements Again
print("TEST 8: Re-enable and Verify Counter Decrements Again")
print("-" * 70)

print("Re-enabling timer...")
WDOGCONTROL.write(0x01)

print("Reading counter before time advance...")
counter_before = WDOGVALUE.read()
print(f"WDOGVALUE before = 0x{counter_before:08x}")

print("Advancing time by 1000 cycles...")
SIM_continue(1000)

counter_after = WDOGVALUE.read()
print(f"WDOGVALUE after  = 0x{counter_after:08x}")

# Counter should decrement again
stest.expect_true(counter_after < counter_before,
                  "Counter should decrement after re-enabling")

print("✓ PASS: Counter decrements after re-enable")
print()

# TEST 9: Lock Side Effect
print("TEST 9: Lock Side Effect")
print("-" * 70)

print("Writing 0x0 to WDOGLOCK (not the unlock key)...")
WDOGLOCK.write(0x0)

lock = WDOGLOCK.read()
print(f"WDOGLOCK = {lock} (expected 1 = locked)")
stest.expect_equal(lock, 1)

print("✓ PASS: Re-lock side effect working (wdt_unlocked = false)")
print()

# TEST 10: Verify Writes are Blocked When Locked
print("TEST 10: Verify Writes are Blocked When Locked")
print("-" * 70)

print("Attempting to write to WDOGLOAD while locked...")
current_load = WDOGLOAD.read()
WDOGLOAD.write(0x99999999)
new_load = WDOGLOAD.read()

print(f"WDOGLOAD before = 0x{current_load:08x}")
print(f"WDOGLOAD after  = 0x{new_load:08x}")

# Load value should not change when locked
stest.expect_equal(new_load, current_load,
                   "WDOGLOAD should not change when locked")

print("✓ PASS: Writes blocked when locked")
print()

# Summary
print("=" * 70)
print("Test Summary - All Side Effects Verified:")
print("=" * 70)
print("✓ TEST 1:  Initial register values correct")
print("✓ TEST 2:  WDOGLOCK unlock side effect")
print("✓ TEST 3:  WDOGLOAD write updates counter")
print("✓ TEST 4:  WDOGCONTROL enable timer side effect")
print("✓ TEST 5:  Counter decrement side effect (timer tick)")
print("✓ TEST 6:  WDOGINTCLR reload side effect")
print("✓ TEST 7:  WDOGCONTROL disable timer side effect")
print("✓ TEST 8:  Counter decrements after re-enable")
print("✓ TEST 9:  WDOGLOCK lock side effect")
print("✓ TEST 10: Writes blocked when locked")
print()
print("All watchdog timer side effects are working correctly!")
print("=" * 70)
