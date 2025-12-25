# Test Anti-Patterns and Troubleshooting Guide

## Overview

This document consolidates all common anti-patterns, mistakes, and troubleshooting solutions from Simics device model testing. It serves as a quick reference for avoiding common pitfalls and debugging test failures.

**Use this document when:**
- Encountering test failures or errors
- Starting a new test suite to avoid common mistakes
- Code review - checking for anti-patterns
- Training new team members on testing best practices

## Table of Contents

1. [Critical Anti-Patterns](#critical-anti-patterns)
2. [Test File Location Issues](#test-file-location-issues)
3. [Configuration Errors](#configuration-errors)
4. [Register Access Problems](#register-access-problems)
5. [Fake Object Issues](#fake-object-issues)
6. [DMA and Memory Problems](#dma-and-memory-problems)
7. [Timing and Event Issues](#timing-and-event-issues)
8. [Troubleshooting Quick Reference](#troubleshooting-quick-reference)

---

## Critical Anti-Patterns

### ⚠️ Top 5 Most Common Mistakes

These are the most frequent errors that break tests:

#### 1. ❌ Wrong Test Location

```bash
# ❌ WRONG - underscore directory
simics_project/modules/device/test/s-test.py

# ✅ CORRECT - hyphen directory
simics-project/modules/device/test/s-test.py
```

**Impact:** Test-runner will not find your tests  
**Error:** "No such test suite"  
**Fix:** Rename directory from `simics_project` to `simics-project`

**See:** [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md) for detailed location requirements

#### 2. ❌ Clock Frequency Set After Instantiation

```python
# ❌ WRONG - freq_mhz set after SIM_add_configuration
clk = simics.pre_conf_object('clk', 'clock')
simics.SIM_add_configuration([clk], None)
conf.clk.freq_mhz = 10  # ❌ TOO LATE!

# ✅ CORRECT - freq_mhz set before SIM_add_configuration
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 10  # ✅ Set on pre-conf object
simics.SIM_add_configuration([clk], None)
```

**Impact:** Timing behavior will be incorrect or undefined  
**Error:** "Attribute 'freq_mhz' is required" or timing failures  
**Fix:** Always set `clk.freq_mhz` on pre-conf object BEFORE `SIM_add_configuration()`

**See:** [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md) for clock configuration details

#### 3. ❌ Missing .bank. Namespace

```python
# ❌ WRONG - missing .bank.
regs = dev_util.bank_regs(device.regs)

# ✅ CORRECT - include .bank.
regs = dev_util.bank_regs(device.bank.regs)
```

**Impact:** AttributeError on bank access  
**Error:** "'conf_object' object has no attribute 'regs'"  
**Fix:** Always use `device.bank.<bank_name>`

**See:** [03_Test_Register_Access](03_Test_Register_Access.md) for register access patterns

#### 4. ❌ Returning Pre-Conf Object

```python
# ❌ WRONG - returning pre_conf_object
def create_config():
    dev = simics.pre_conf_object('dut', 'device')
    simics.SIM_add_configuration([dev], None)
    return dev  # ❌ Wrong object type

# ✅ CORRECT - returning conf_object
def create_config():
    dev = simics.pre_conf_object('dut', 'device')
    simics.SIM_add_configuration([dev], None)
    return conf.dut  # ✅ Use conf.<name>
```

**Impact:** Cannot access device registers or attributes  
**Error:** "'pre_conf_object' has no attribute 'bank'"  
**Fix:** Return `conf.<name>` from `create_config()`, NOT the pre-conf object

**See:** [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md) for pre-conf vs conf objects

#### 5. ❌ Not Wrapping Bank with dev_util.bank_regs()

```python
# ❌ WRONG - direct bank access
wdt = dut.bank.wdt_regs
wdt.WDOGLOAD.write(0x10)  # ❌ No write() method

# ✅ CORRECT - wrap with dev_util.bank_regs()
wdt = dev_util.bank_regs(dut.bank.wdt_regs)
wdt.WDOGLOAD.write(0x10)  # ✅ Works!
```

**Impact:** AttributeError when trying to read/write registers  
**Error:** "'bank_object' has no attribute 'write'"  
**Fix:** Always wrap banks with `dev_util.bank_regs()` before accessing registers

**See:** [03_Test_Register_Access](03_Test_Register_Access.md) for bank access requirements

---

## Test File Location Issues

### Anti-Pattern: Using Underscore in Project Directory

**See:** [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md)

**Problem:** Using `simics_project/` instead of `simics-project/`

**Why it's wrong:**
- Simics expects hyphenated directory names
- Test-runner only discovers tests in correct locations
- Python package convention vs Simics project convention

**Fix:**
```bash
mv simics_project simics-project
```

### Anti-Pattern: Missing SUITEINFO File

**Problem:** No SUITEINFO file in test directory

**Impact:** Test-runner doesn't recognize directory as test suite

**Fix:**
```bash
cd simics-project/modules/device/test
touch SUITEINFO
```

### Anti-Pattern: Defining Test Functions But Not Calling Them

```python
# ❌ WRONG - function defined but never called
def test_interrupts():
    (dut, pic) = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.trigger_irq.write(0x1)
    stest.expect_equal(pic.raised, 1, "Interrupt not raised")
# File ends - test NEVER runs! Silent failure

# ✅ CORRECT - call the function
def test_interrupts():
    (dut, pic) = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.trigger_irq.write(0x1)
    stest.expect_equal(pic.raised, 1, "Interrupt not raised")

test_interrupts()  # ✅ Actually execute the test
```

**Impact:** Silent failure - test appears to pass but didn't run

---

## Configuration Errors

### Anti-Pattern: Setting Attributes After Instantiation

**See:** [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md)

```python
# ❌ WRONG - configure after SIM_add_configuration
dev = simics.pre_conf_object('dev', 'device')
clk = simics.pre_conf_object('clk', 'clock')
simics.SIM_add_configuration([dev, clk], None)

conf.clk.freq_mhz = 100  # ❌ Too late
conf.dev.queue = conf.clk  # ❌ Too late

# ✅ CORRECT - configure before SIM_add_configuration
dev = simics.pre_conf_object('dev', 'device')
clk = simics.pre_conf_object('clk', 'clock')

clk.freq_mhz = 100  # ✅ Set on pre-conf object
dev.queue = clk     # ✅ Set on pre-conf object

simics.SIM_add_configuration([dev, clk], None)
```

### Anti-Pattern: Missing Queue Assignment

```python
# ❌ WRONG - no queue assigned to time-dependent device
dev = simics.pre_conf_object('dev', 'timer_device')
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100
# Missing: dev.queue = clk

# ✅ CORRECT - assign queue for time-dependent devices
dev = simics.pre_conf_object('dev', 'timer_device')
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100
dev.queue = clk  # ✅ Required for timers/events
```

**Impact:** "Queue not set" error, events don't fire

---

## Register Access Problems

### Anti-Pattern: Guessing Bank Names

**See:** [03_Test_Register_Access](03_Test_Register_Access.md)

```python
# ❌ WRONG - guessing/scanning for bank names
for name in ['reg_if', 'regif', 'regs', 'registers']:
    try:
        regs = dev_util.bank_regs(getattr(device.bank, name))
        break
    except:
        pass

# ✅ CORRECT - read DML for exact bank name
# From DML: bank regs { ... }
regs = dev_util.bank_regs(device.bank.regs)
```

**Correct workflow:**
1. Read `<device>.dml` file
2. Find `bank <bank_name> { ... }` declaration
3. Use exact bank name in test: `device.bank.<bank_name>`

### Anti-Pattern: Testing Without Assertions

```python
# ❌ WRONG - no verification
regs.CONTROL.write(0x5)
value = regs.CONTROL.read()
print(f"Value: {value}")  # ❌ No assertion - can't detect failures

# ✅ CORRECT - use assertions to verify
regs.CONTROL.write(0x5)
value = regs.CONTROL.read()
stest.expect_equal(value, 0x5, "CONTROL register mismatch")
```

**Impact:** False positives - test "passes" but doesn't verify behavior

---

## Fake Object Issues

### Anti-Pattern: Missing Fake Objects for Connect Blocks

**See:** [04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md)

```python
# DML has:
# connect pic { interface signal; }
# connect reset { interface reset_signal; }

# ❌ WRONG - only creating one fake
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
dev.pic = fake_pic
# Missing: fake reset object

# ✅ CORRECT - create fakes for ALL connect blocks
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
fake_reset = simics.pre_conf_object('fake_reset', 'FakeReset')

dev.pic = fake_pic
dev.reset = fake_reset
```

**Impact:** Segmentation fault (core dumped)

**Fix:**
1. Read DML for all `connect <name>` blocks
2. Create fake object for each
3. Connect all fakes to device before instantiation

### Anti-Pattern: Wrong Interface Method Names

```python
# DML calls:
# pic.signal.signal_raise();

# ❌ WRONG - method name mismatch
class FakePic(pyobj.ConfObject):
    class signal(pyobj.Interface):
        def raise_signal(self):  # ❌ Wrong name
            self._up.raised.val += 1

# ✅ CORRECT - match DML call exactly
class FakePic(pyobj.ConfObject):
    class signal(pyobj.Interface):
        def signal_raise(self):  # ✅ Matches DML
            self._up.raised.val += 1
```

**Impact:** Interface method never called, fake object state doesn't update

---

## DMA and Memory Problems

### Anti-Pattern: Not Connecting Memory to Device

**See:** [05_Test_DMA_Memory](05_Test_DMA_Memory.md)

```python
# ❌ WRONG - memory created but not connected
mem = dev_util.Memory()
# Missing: dev.phys_mem = mem.obj

# ✅ CORRECT - connect memory to device
mem = dev_util.Memory()
dev.phys_mem = mem.obj  # ✅ Required for device memory access
```

**Impact:** DMA operations fail silently, no data transfer occurs

### Anti-Pattern: Not Waiting for DMA Completion

```python
# ❌ WRONG - checking result immediately
regs.DMA_START.write(0x1)
result = mem.read(dst_addr, size)  # ❌ DMA not complete yet

# ✅ CORRECT - wait for completion
regs.DMA_START.write(0x1)
simics.SIM_continue(1000)  # ✅ Wait for DMA to complete
result = mem.read(dst_addr, size)
```

**Impact:** Test fails even though DMA works correctly

### Anti-Pattern: Not Clearing Destination Memory

```python
# ❌ WRONG - destination may have stale data
mem.write(src_addr, test_data)
# Missing: clear destination
regs.DMA_START.write(0x1)
simics.SIM_continue(1000)
result = mem.read(dst_addr, size)
# Can't tell if DMA worked or data was already there!

# ✅ CORRECT - clear destination before DMA
mem.write(src_addr, test_data)
mem.write(dst_addr, [0] * size)  # ✅ Clear destination
regs.DMA_START.write(0x1)
simics.SIM_continue(1000)
result = mem.read(dst_addr, size)
```

**Impact:** Tests pass even if DMA doesn't work

---

## Timing and Event Issues

### Anti-Pattern: Missing Clock Configuration

**See:** [06_Test_Events_Timing](06_Test_Events_Timing.md)

```python
# ❌ WRONG - no clock frequency or queue
dev = simics.pre_conf_object('dev', 'timer_device')
clk = simics.pre_conf_object('clk', 'clock')
# Missing: clk.freq_mhz = 100
# Missing: dev.queue = clk

# ✅ CORRECT - configure clock and queue
dev = simics.pre_conf_object('dev', 'timer_device')
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100  # ✅ Set frequency
dev.queue = clk     # ✅ Assign queue
```

**Impact:** "Queue not set" error, events don't fire, timers don't work

### Anti-Pattern: Insufficient Wait Time

```python
# ❌ WRONG - not waiting long enough
regs.TIMER_VALUE.write(1000)
regs.TIMER_START.write(0x1)
simics.SIM_continue(100)  # ❌ Only 100 cycles, need 1000

# ✅ CORRECT - wait sufficient time
regs.TIMER_VALUE.write(1000)
regs.TIMER_START.write(0x1)
simics.SIM_continue(1000)  # ✅ Wait full duration
```

**Impact:** Legitimate timer behavior fails test

---

## Troubleshooting Quick Reference

### Error: "No such test suite"

**Symptoms:**
```bash
$ ./bin/test-runner --suite modules/device/test
Error: No such test suite: modules/device/test
```

**Fixes:**
1. Check for underscore directory: `ls -la | grep simics`
   - Should show `simics-project`, not `simics_project`
   - Fix: `mv simics_project simics-project`

2. Check for SUITEINFO file: `ls modules/device/test/SUITEINFO`
   - Fix: `touch simics-project/modules/device/test/SUITEINFO`

3. Check working directory: `pwd` should end with `/simics-project`
   - Fix: `cd simics-project`

### Error: "'conf_object' object has no attribute 'regs'"

**Fix:** Always include `.bank.` namespace
```python
regs = dev_util.bank_regs(device.bank.regs)  # Not device.regs
```

### Error: "'bank_object' has no attribute 'write'"

**Fix:** Always wrap with `dev_util.bank_regs()`
```python
wdt = dev_util.bank_regs(dut.bank.wdt_regs)  # Wrap with dev_util.bank_regs()
wdt.WDOGLOAD.write(0x10)
```

### Error: "Attribute 'freq_mhz' is required"

**Fix:** Set freq_mhz BEFORE SIM_add_configuration
```python
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100  # BEFORE instantiation
simics.SIM_add_configuration([clk], None)
```

### Error: "Queue not set"

**Fix:** Assign queue for time-dependent devices
```python
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100
dev.queue = clk  # Required for events/timers
```

### Error: Segmentation fault (core dumped)

**Fix:** Create fakes for ALL connect blocks in DML
```python
# Check DML for all: connect <name> { ... }
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
fake_reset = simics.pre_conf_object('fake_reset', 'FakeReset')

dev.pic = fake_pic
dev.reset = fake_reset
```

### Error: Timer/Event Never Fires

**Debugging checklist:**
```python
# 1. Verify clock frequency is set
clk.freq_mhz = 100  # BEFORE SIM_add_configuration

# 2. Verify queue is assigned
dev.queue = clk

# 3. Verify timer is enabled
stest.expect_equal(regs.TIMER_CONTROL.read() & 0x1, 1, "Timer not enabled")

# 4. Verify fake PIC is connected
dev.pic = fake_pic

# 5. Wait sufficient time
simics.SIM_continue(timeout_value + 100)  # Add margin
```

### Error: Test Passes But Shouldn't

**Common causes:**

1. **Test function not called**
   ```python
   def test_feature():
       # test code
   test_feature()  # ✅ Must call it!
   ```

2. **No assertions**
   ```python
   regs.CONTROL.write(0x5)
   value = regs.CONTROL.read()
   stest.expect_equal(value, 0x5, "Mismatch")  # ✅ Assert!
   ```

---

## Best Practices Summary

### ✅ Always DO:

1. **Test Location**: Use `simics-project/` (hyphen), tests in `modules/<device>/test/`
2. **Clock Setup**: Set `clk.freq_mhz` BEFORE `SIM_add_configuration()`
3. **Return conf_object**: Return `conf.<name>` from `create_config()`, NOT pre-conf objects
4. **Bank Access**: Use `dev_util.bank_regs(device.bank.<bank_name>)`, read DML for exact name
5. **Call Test Functions**: If you wrap test code in a function, MUST call it at the end
6. **Fake Objects**: Create fakes for ALL DML connect blocks
7. **Assertions**: Always use `stest.expect_equal()` to verify behavior
8. **Wait for Async**: Use `simics.SIM_continue()` to wait for DMA, timers, events
9. **Read DML First**: Get exact bank/register/field names from DML source
10. **Clear Memory**: Clear destination before DMA tests

### ❌ Never DO:

1. **Don't** use `simics_project/` (underscore)
2. **Don't** set attributes after `SIM_add_configuration()`
3. **Don't** access banks without `dev_util.bank_regs()`
4. **Don't** guess bank/register names - read DML
5. **Don't** return pre-conf objects from `create_config()`
6. **Don't** forget to call test functions
7. **Don't** test without assertions
8. **Don't** forget fake objects for connect blocks
9. **Don't** forget to wait for async operations
10. **Don't** assume - verify intermediate states

---

## Related Documents

For detailed examples and comprehensive coverage:

- **[01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md)** - Location and naming requirements, SUITEINFO, test patterns
- **[02_Test_Configuration_Setup](02_Test_Configuration_Setup.md)** - Device configuration, clocks, memory mapping, common.py template
- **[03_Test_Register_Access](03_Test_Register_Access.md)** - Register and field access patterns, bank_regs usage
- **[04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md)** - Creating fake objects, interface implementation
- **[05_Test_DMA_Memory](05_Test_DMA_Memory.md)** - DMA testing, memory verification, descriptor-based DMA
- **[06_Test_Events_Timing](06_Test_Events_Timing.md)** - Timer testing, event verification, timing assertions

---

**Document Status**: ✅ Complete  
**Created From**: Consolidated anti-patterns and troubleshooting from documents 01-06  
**Last Updated**: December 24, 2025  
**Purpose**: Quick reference for debugging test failures and avoiding common mistakes
