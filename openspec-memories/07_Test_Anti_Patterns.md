# Test Anti-Patterns

## Overview

This document consolidates common anti-patterns and mistakes in Simics device model testing. Each anti-pattern shows the wrong approach, explains why it's problematic, and demonstrates the correct solution.

**Use this document for:**
- Code review - identifying problematic patterns
- Learning correct testing practices
- Avoiding common mistakes when writing new tests

## Table of Contents

1. [Test Structure Anti-Patterns](#test-structure-anti-patterns)
2. [Attribute Access Anti-Patterns](#attribute-access-anti-patterns)
3. [Register Access Anti-Patterns](#register-access-anti-patterns)
4. [Timing Anti-Patterns](#timing-anti-patterns)
5. [Fake Object Anti-Patterns](#fake-object-anti-patterns)
6. [Configuration Anti-Patterns](#configuration-anti-patterns)
7. [Test Location Anti-Patterns](#test-location-anti-patterns)
8. [DMA and Memory Anti-Patterns](#dma-and-memory-anti-patterns)

---

## Test Structure Anti-Patterns

**Reference:** General test organization best practices

### ❌ Defining Test Functions Without Calling Them

```python
# ❌ WRONG - function defined but never called
def test_interrupts():
    (dut, pic) = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.trigger_irq.write(0x1)
    stest.expect_equal(pic.raised, 1, "Interrupt not raised")
# File ends - test NEVER runs!

# ✅ CORRECT - call the function
def test_interrupts():
    (dut, pic) = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.trigger_irq.write(0x1)
    stest.expect_equal(pic.raised, 1, "Interrupt not raised")

test_interrupts()  # ✅ Execute the test
```

**Why it's wrong:** Silent failure - test appears to pass but never executed

### ❌ Multiple Test Functions in Single File

```python
# ❌ WRONG - multiple tests in one file
def test_basic_operations():
    dut = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.CONTROL.write(0x1)
    stest.expect_equal(regs.STATUS.read(), 0x1)

def test_advanced_operations():
    dut = create_config()  # ❌ Duplicate object name!
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.CONTROL.write(0x2)

test_basic_operations()
test_advanced_operations()  # Error: simics.SimExc_General: Duplicate object name

# ✅ CORRECT - one test per file
# File: s-basic-operations.py
def test_basic_operations():
    dut = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.CONTROL.write(0x1)
    stest.expect_equal(regs.STATUS.read(), 0x1)

test_basic_operations()

# File: s-advanced-operations.py
def test_advanced_operations():
    dut = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)
    regs.CONTROL.write(0x2)

test_advanced_operations()
```

**Why it's wrong:** Multiple test functions calling `create_config()` create duplicate object names in the same Simics session, causing "Duplicate object name" errors. Each test should be in its own file with its own configuration.

---

## Attribute Access Anti-Patterns

**Reference:** [04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md)

### ❌ Incorrect Attribute Access for conf_object and pyobj

```python
# ❌ WRONG - using .val outside pyobj class
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
simics.SIM_add_configuration([fake_pic], None)
signal_raised_cnt = conf.fake_pic.raised.val  # ❌ Wrong!
stest.expect_equal(signal_raised_cnt, 0)

# ✅ CORRECT - no .val outside pyobj class
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
simics.SIM_add_configuration([fake_pic], None)
signal_raised_cnt = conf.fake_pic.raised  # ✅ Direct access
stest.expect_equal(signal_raised_cnt, 0)

# ❌ WRONG - missing .val inside pyobj class
class FakePic(pyobj.ConfObject):
    class raised(pyobj.SimpleAttribute(0, 'i')): pass
    
    class signal(pyobj.Interface):
        def signal_raise(self):
            self._up.raised += 1  # ❌ Wrong! Need .val

# ✅ CORRECT - use .val inside pyobj class
class FakePic(pyobj.ConfObject):
    class raised(pyobj.SimpleAttribute(0, 'i')): pass
    
    class signal(pyobj.Interface):
        def signal_raise(self):
            self._up.raised.val += 1  # ✅ Use .val
            
        def signal_lower(self):
            self._up.raised.val -= 1  # ✅ Use .val
```

**Why it's wrong:** Attribute access rules differ by context:
- **Outside pyobj class** (in test code): Access `conf_object.attribute` directly without `.val`
- **Inside pyobj class** (class methods): Access `self._up.attribute.val` with `.val` suffix

This distinction is critical - mixing them causes AttributeError or incorrect behavior.

---

## Register Access Anti-Patterns

**Reference:** [03_Test_Register_Access](03_Test_Register_Access.md)

### ❌ Missing .bank. Namespace

```python
# ❌ WRONG
regs = dev_util.bank_regs(device.regs)

# ✅ CORRECT
regs = dev_util.bank_regs(device.bank.regs)
```

**Why it's wrong:** Banks are always accessed via `device.bank.<bank_name>` namespace

### ❌ Not Wrapping Banks with dev_util.bank_regs()

```python
# ❌ WRONG - direct bank access
wdt = dut.bank.wdt_regs
wdt.WDOGLOAD.write(0x10)  # No write() method!

# ✅ CORRECT - wrap with dev_util.bank_regs()
wdt = dev_util.bank_regs(dut.bank.wdt_regs)
wdt.WDOGLOAD.write(0x10)  # Works!
```

**Why it's wrong:** Raw bank objects lack convenient read/write methods; must wrap with `dev_util.bank_regs()`

### ❌ Guessing or Scanning for Bank Names

```python
# ❌ WRONG - defensive scanning
for name in ['reg_if', 'regif', 'regs', 'registers']:
    try:
        regs = dev_util.bank_regs(getattr(device.bank, name))
        break
    except:
        pass

# ✅ CORRECT - read DML for exact name
# From DML: bank regs { ... }
regs = dev_util.bank_regs(device.bank.regs)
```

**Why it's wrong:** Bank names are explicit in DML; scanning adds unnecessary complexity and fragility

---

## Timing Anti-Patterns

**Reference:** [06_Test_Events_Timing](06_Test_Events_Timing.md)

### ❌ Insufficient Wait Time

```python
# ❌ WRONG - not waiting long enough
regs.TIMER_VALUE.write(1000)
regs.TIMER_START.write(0x1)
simics.SIM_continue(100)  # Only 100 cycles!

# ✅ CORRECT - wait full duration
regs.TIMER_VALUE.write(1000)
regs.TIMER_START.write(0x1)
simics.SIM_continue(1000)  # Full 1000 cycles
```

**Why it's wrong:** Async operations need time to complete; checking too early sees incomplete state

---

## Fake Object Anti-Patterns

**Reference:** [04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md)

### ❌ Missing Fake Objects for Connect Blocks

```python
# DML has: connect pic { ... } and connect reset { ... }

# ❌ WRONG - incomplete fakes
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
dev.pic = fake_pic
# Missing: fake reset

# ✅ CORRECT - fake for each connect block
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
fake_reset = simics.pre_conf_object('fake_reset', 'FakeReset')
dev.pic = fake_pic
dev.reset = fake_reset
```

**Why it's wrong:** Missing fake objects cause segfaults when device tries to access them

### ❌ Wrong Interface Method Names

```python
# DML calls: pic.signal.signal_raise();

# ❌ WRONG - name mismatch
class FakePic(pyobj.ConfObject):
    class signal(pyobj.Interface):
        def raise_signal(self):  # ❌ Doesn't match DML
            self._up.raised.val += 1

# ✅ CORRECT - exact match
class FakePic(pyobj.ConfObject):
    class signal(pyobj.Interface):
        def signal_raise(self):  # ✅ Matches DML
            self._up.raised.val += 1
```

**Why it's wrong:** Interface method names must exactly match DML calls

---

## Configuration Anti-Patterns

**Reference:** [02_Test_Configuration_Setup](02_Test_Configuration_Setup.md)

### ❌ Setting Attributes After Instantiation

```python
# ❌ WRONG - configure after SIM_add_configuration
dev = simics.pre_conf_object('dev', 'device')
clk = simics.pre_conf_object('clk', 'clock')
simics.SIM_add_configuration([dev, clk], None)
conf.clk.freq_mhz = 100  # ❌ Too late
conf.dev.queue = conf.clk

# ✅ CORRECT - configure before SIM_add_configuration
dev = simics.pre_conf_object('dev', 'device')
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100  # ✅ Before instantiation
simics.SIM_add_configuration([dev, clk], None)
dev.queue = clk
```

**Why it's wrong:** Required attributes must be set on pre-conf objects before instantiation

### ❌ Returning Pre-Conf Object Instead of Conf Object

```python
# ❌ WRONG
def create_config():
    dev = simics.pre_conf_object('dut', 'device')
    simics.SIM_add_configuration([dev], None)
    return dev  # ❌ Returns pre-conf object

# ✅ CORRECT
def create_config():
    dev = simics.pre_conf_object('dut', 'device')
    simics.SIM_add_configuration([dev], None)
    return conf.dut  # ✅ Returns conf object
```

**Why it's wrong:** Pre-conf objects lack full API; must return conf objects for register access

---

## Test Location Anti-Patterns

**Reference:** [01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md)

### ❌ Using Underscore Instead of Hyphen in Project Directory

```bash
# ❌ WRONG
simics_project/modules/device/test/s-test.py

# ✅ CORRECT
simics-project/modules/device/test/s-test.py
```

**Why it's wrong:** Simics test-runner only discovers tests in `simics-project/` (hyphen), not `simics_project/` (underscore)

### ❌ Missing SUITEINFO File

```bash
# ❌ WRONG - no SUITEINFO marker
simics-project/modules/device/test/
├── s-basic.py
└── s-advanced.py

# ✅ CORRECT - includes SUITEINFO
simics-project/modules/device/test/
├── SUITEINFO
├── s-basic.py
└── s-advanced.py
```

**Why it's wrong:** Test-runner requires SUITEINFO file to recognize directory as a test suite

---

## DMA and Memory Anti-Patterns

**Reference:** [05_Test_DMA_Memory](05_Test_DMA_Memory.md)

### ❌ Not Connecting Memory to Device

```python
# ❌ WRONG
mem = dev_util.Memory()
# Missing: dev.phys_mem = mem.obj

# ✅ CORRECT
mem = dev_util.Memory()
dev.phys_mem = mem.obj
```

**Why it's wrong:** Device needs memory reference to perform DMA operations

### ❌ Not Waiting for Async Operations

```python
# ❌ WRONG - immediate check
regs.DMA_START.write(0x1)
result = mem.read(dst_addr, size)  # Too soon!

# ✅ CORRECT - wait for completion
regs.DMA_START.write(0x1)
simics.SIM_continue(1000)
result = mem.read(dst_addr, size)
```

**Why it's wrong:** DMA is asynchronous; must wait with `SIM_continue()` for completion

### ❌ Not Clearing Destination Before Testing

```python
# ❌ WRONG - can't verify DMA actually worked
mem.write(src_addr, test_data)
regs.DMA_START.write(0x1)
simics.SIM_continue(1000)
result = mem.read(dst_addr, size)  # Might have stale data!

# ✅ CORRECT - clear to ensure DMA writes
mem.write(src_addr, test_data)
mem.write(dst_addr, [0] * size)  # Clear first
regs.DMA_START.write(0x1)
simics.SIM_continue(1000)
result = mem.read(dst_addr, size)
```

**Why it's wrong:** Can't distinguish successful transfer from pre-existing data; causes false positives

---

## Summary: Top 10 Anti-Patterns to Avoid

1. ❌ **Multiple test functions per file**: One test per file to avoid "Duplicate object name" errors
2. ❌ **Uncalled test functions**: If you define test functions, call them!
3. ❌ **Wrong .val usage**: Use `.val` inside pyobj class methods, NOT outside in test code
4. ❌ **Missing .bank. namespace**: Always use `device.bank.<bank_name>`
5. ❌ **No dev_util.bank_regs() wrapper**: Always wrap banks for register access
6. ❌ **Wrong directory name**: Use `simics-project/` not `simics_project/`
7. ❌ **Late attribute configuration**: Set attributes BEFORE `SIM_add_configuration()`
8. ❌ **Returning pre-conf objects**: Return `conf.<name>` from `create_config()`
9. ❌ **Missing fake objects**: Create fakes for ALL DML connect blocks
10. ❌ **Not waiting for async**: Use `SIM_continue()` for DMA, timers, events

---

## Related Documents

For detailed examples and correct patterns, see:

- **[01_Test_File_Location_Requirements](01_Test_File_Location_Requirements.md)** - Location and naming requirements
- **[02_Test_Configuration_Setup](02_Test_Configuration_Setup.md)** - Device configuration patterns
- **[03_Test_Register_Access](03_Test_Register_Access.md)** - Register access patterns
- **[04_Test_Fake_Objects_Mocking](04_Test_Fake_Objects_Mocking.md)** - Fake object creation
- **[05_Test_DMA_Memory](05_Test_DMA_Memory.md)** - DMA testing patterns
- **[06_Test_Events_Timing](06_Test_Events_Timing.md)** - Timing and event patterns

---

**Document Status**: ✅ Complete  
**Created From**: Consolidated anti-patterns from documents 01-06  
**Last Updated**: December 25, 2025  
**Purpose**: Quick reference for avoiding common testing mistakes
