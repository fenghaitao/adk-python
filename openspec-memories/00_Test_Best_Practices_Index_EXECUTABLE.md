# Simics Test Best Practices - Executable Index

**Purpose**: This executable index contains copy-paste ready test patterns that enable you to write working Simics tests without reading other documents. Use this for 80% of common test cases. Read detailed documents only when you need deeper understanding.

**Generated from**: Session learnings (Watchdog Timer testing, December 2024)

---

## ⚡ CRITICAL PATTERNS (Copy These First)

### Pattern 1: Device Creation with Clock ⭐ PREVENTS "Queue not set" ERRORS

```python
import simics
import conf

def create_wdt(name='test_wdt'):
    """Create watchdog timer device with clock."""
    # 1. Create pre-conf objects
    wdt = simics.pre_conf_object(name, 'wdt')
    clk = simics.pre_conf_object(name + '_clk', 'clock')
    
    # 2. ⚠️ CRITICAL: Set freq_mhz BEFORE instantiation!
    clk.freq_mhz = 100  # Must be set on pre-conf object
    
    # 3. ⚠️ CRITICAL: Assign queue for timing devices
    wdt.queue = clk  # Required for devices with events/timers
    
    # 4. Instantiate objects
    simics.SIM_add_configuration([wdt, clk], None)
    
    # 5. ⚠️ CRITICAL: Return conf object, NOT pre-conf!
    return simics.SIM_get_object(name)  # or conf.test_wdt
```

**Why Each Step Matters**:
- `clk.freq_mhz` MUST be set BEFORE `SIM_add_configuration()`
- `wdt.queue = clk` required for any device with timing behavior
- Return `conf.<name>` or `SIM_get_object(name)`, NOT the pre-conf object

---

### Pattern 2: Register Access ⭐ PREVENTS AttributeError

```python
import dev_util
import stest

# ❌ WRONG - Direct bank access (missing dev_util.bank_regs wrapper)
def test_wrong():
    dev = create_wdt()
    wdt = dev.bank.WatchdogRegisters  # ❌ Raw bank object, no read/write methods
    wdt.WDOGLOAD.write(0x1000)  # ❌ AttributeError: no write() method

# ✅ CORRECT - Use dev_util.bank_regs() wrapper
def test_correct():
    dev = create_wdt()
    
    # ⚠️ CRITICAL: ALWAYS wrap with dev_util.bank_regs()
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)  # ✅ Provides read/write API
    
    # Now you can use convenient methods
    regs.WDOGLOAD.write(0x1000)  # ✅ Works!
    value = regs.WDOGLOAD.read()  # ✅ Works!
    stest.expect_equal(value, 0x1000, "WDOGLOAD mismatch")
```

**Critical Rules**:
- ALWAYS use `dev_util.bank_regs(dev.bank.<BankName>)`
- NEVER access `dev.bank.<BankName>` directly
- Bank name must match DML exactly (read DML file to find it)
- Must include `.bank.` namespace: `dev.bank.BankName`, not `dev.BankName`

---

### Pattern 3: Test Organization ⭐ PREVENTS AttributeError

```python
import simics
import stest
import dev_util

# ✅ CORRECT - Use print() for test sections
def test_watchdog():
    dev = create_wdt()
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    print("TEST-001: Basic register access")
    regs.WDOGLOAD.write(0x1000)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x1000, "WDOGLOAD write failed")
    
    print("TEST-002: Lock protection")
    regs.WDOGLOCK.write(0x1ACCE551)  # Unlock
    regs.WDOGLOAD.write(0x2000)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x2000, "Write after unlock failed")
    
    print("TEST-003: Counter countdown")
    regs.WDOGCONTROL.write(0x1)  # Enable
    simics.SIM_continue(100)  # Run 100 cycles
    # Verify counter decremented

# ❌ WRONG - Don't use (doesn't exist)
def test_wrong():
    # stest.start_branch("TEST-001")  # ❌ AttributeError: no start_branch!
    # stest.end_branch()  # ❌ AttributeError: no end_branch!
    pass
```

**Test Framework Limitations**:
- ✅ Use `print()` for test section headers
- ✅ Use `stest.expect_equal()`, `stest.expect_true()` for assertions
- ❌ DON'T use `stest.start_branch()` (doesn't exist)
- ❌ DON'T use `stest.end_branch()` (doesn't exist)

---

### Pattern 4: Simulation Control

```python
import simics

def test_timing():
    dev = create_wdt()
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Advance simulation time
    simics.SIM_continue(100)  # Run 100 cycles
    
    # Check elapsed cycles
    start = simics.SIM_cycle_count(dev)
    simics.SIM_continue(100)
    elapsed = simics.SIM_cycle_count(dev) - start
    stest.expect_equal(elapsed, 100, "Cycle count mismatch")
    
    # Run until specific time
    simics.SIM_continue_seconds(0.001)  # Run 1ms
```

---

### Pattern 5: Complete Test Template

```python
#!/usr/bin/env python3
"""Test suite for watchdog timer device."""

import dev_util
import simics
import stest

def create_wdt(name='test_wdt'):
    """Create watchdog timer with clock."""
    wdt = simics.pre_conf_object(name, 'wdt')
    clk = simics.pre_conf_object(name + '_clk', 'clock')
    
    # CRITICAL: Set freq_mhz BEFORE instantiation
    clk.freq_mhz = 100
    wdt.queue = clk
    
    simics.SIM_add_configuration([wdt, clk], None)
    return simics.SIM_get_object(name)

def test_basic_register_access():
    """Test basic register read/write."""
    print("TEST-001: Basic register access")
    
    dev = create_wdt()
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Test write and read
    regs.WDOGLOAD.write(0x1000)
    value = regs.WDOGLOAD.read()
    stest.expect_equal(value, 0x1000, "WDOGLOAD write/read failed")
    
    print("  ✓ Basic register access passed")

def test_lock_protection():
    """Test lock protection mechanism."""
    print("TEST-002: Lock protection")
    
    dev = create_wdt()
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Unlock with magic value
    regs.WDOGLOCK.write(0x1ACCE551)
    regs.WDOGLOAD.write(0x2000)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x2000, "Write after unlock failed")
    
    # Lock again
    regs.WDOGLOCK.write(0x0)
    regs.WDOGLOAD.write(0x3000)
    stest.expect_equal(regs.WDOGLOAD.read(), 0x2000, "Write after lock should be ignored")
    
    print("  ✓ Lock protection passed")

def test_counter_countdown():
    """Test counter countdown behavior."""
    print("TEST-003: Counter countdown")
    
    dev = create_wdt()
    regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
    
    # Load counter and enable
    regs.WDOGLOAD.write(0x1000)
    initial = regs.WDOGVALUE.read()
    
    regs.WDOGCONTROL.write(0x1)  # Enable
    simics.SIM_continue(100)  # Run 100 cycles
    
    final = regs.WDOGVALUE.read()
    stest.expect_true(final < initial, "Counter should decrement")
    
    print("  ✓ Counter countdown passed")

# Run all tests
test_basic_register_access()
test_lock_protection()
test_counter_countdown()

print("\n✅ All tests passed!")
```

---

## 📊 Quick Decision Trees

### "I need to create a test device"

```
Checklist:
├─ ✅ Create pre-conf objects (device + clock)
├─ ✅ Set clk.freq_mhz BEFORE SIM_add_configuration
├─ ✅ Set dev.queue = clk for timing devices
├─ ✅ Call SIM_add_configuration([dev, clk], None)
└─ ✅ Return conf.<name> or SIM_get_object(name)
```

### "I need to access registers"

```
Steps:
├─ 1. Read DML file to find bank name (e.g., "WatchdogRegisters")
├─ 2. Get device: dev = create_device()
├─ 3. Wrap bank: regs = dev_util.bank_regs(dev.bank.BankName)
└─ 4. Access: regs.REGISTER.write(value) / regs.REGISTER.read()
```

### "I got an error"

```
Error message:
├─ AttributeError: 'Bank_Registers' → Use dev_util.bank_regs(), not Bank_Registers
├─ AttributeError: 'start_branch' → Use print() instead
├─ "Queue not set" → Set clk.freq_mhz and dev.queue = clk
├─ AttributeError on pre-conf object → Return conf.<name>, not pre-conf
└─ "unknown bank" → Check .bank. namespace: dev.bank.Name
```

---

## 🚫 Common Anti-Patterns

### Anti-Pattern 1: Wrong API Name

```python
# ❌ WRONG
regs = dev_util.Bank_Registers(dev, 'WatchdogRegisters')  # No such function!

# ✅ CORRECT
regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)
```

### Anti-Pattern 2: Missing .bank. Namespace

```python
# ❌ WRONG
regs = dev_util.bank_regs(dev.WatchdogRegisters)  # Missing .bank.

# ✅ CORRECT
regs = dev_util.bank_regs(dev.bank.WatchdogRegisters)  # Include .bank.
```

### Anti-Pattern 3: Clock Setup After Instantiation

```python
# ❌ WRONG
def create_device():
    clk = simics.pre_conf_object('clk', 'clock')
    simics.SIM_add_configuration([clk], None)  # ❌ freq_mhz not set!
    conf.clk.freq_mhz = 100  # ❌ Too late!
    return conf.clk

# ✅ CORRECT
def create_device():
    clk = simics.pre_conf_object('clk', 'clock')
    clk.freq_mhz = 100  # ✅ Set BEFORE instantiation
    simics.SIM_add_configuration([clk], None)
    return conf.clk
```

### Anti-Pattern 4: Returning Pre-Conf Object

```python
# ❌ WRONG
def create_device():
    dev = simics.pre_conf_object('dev', 'wdt')
    simics.SIM_add_configuration([dev], None)
    return dev  # ❌ Returns pre-conf object!

# ✅ CORRECT
def create_device():
    dev = simics.pre_conf_object('dev', 'wdt')
    simics.SIM_add_configuration([dev], None)
    return conf.dev  # ✅ Returns conf object
    # or: return simics.SIM_get_object('dev')
```

### Anti-Pattern 5: Using Non-Existent Test APIs

```python
# ❌ WRONG
stest.start_branch("TEST-001")  # ❌ Doesn't exist!
# ... test code ...
stest.end_branch()  # ❌ Doesn't exist!

# ✅ CORRECT
print("TEST-001: Description")  # ✅ Simple and works
# ... test code ...
```

---

## 📚 Deep Dive Documents

**Only read these if the patterns above aren't sufficient:**

### Document 1: [Test File Location Requirements](01_Test_File_Location_Requirements.md) ⚠️ CRITICAL
**When**: Before creating ANY test file  
**Topics**: Where to create tests, file naming, test patterns

### Document 2: [Test Configuration Setup](02_Test_Configuration_Setup.md)
**When**: Setting up test environment  
**Topics**: Device configuration, clocks, memory mapping, common.py template

### Document 3: [Test Register Access](03_Test_Register_Access.md)
**When**: Testing device registers  
**Topics**: Bank access, register read/write, field access, common errors

### Document 4: [Test Fake Objects/Mocking](04_Test_Fake_Objects_Mocking.md)
**When**: Isolating device under test  
**Topics**: Mocking interfaces, fake objects, dependency injection

### Document 5: [Test DMA/Memory](05_Test_DMA_Memory.md)
**When**: Testing DMA operations  
**Topics**: Memory access, DMA testing, verification patterns

### Document 6: [Test Events/Timing](06_Test_Events_Timing.md)
**When**: Testing timers and events  
**Topics**: Time-dependent behavior, event testing, timing verification

---

## 🎯 Recommended Reading Order

### For ALL Test Writers:
1. **This executable index** (you're reading it now)
2. **01_Test_File_Location_Requirements.md** (CRITICAL - where to create tests)

### For First-Time Test Writers:
1. **This executable index** (copy patterns 1, 2, 3, 5)
2. **01_Test_File_Location_Requirements.md** (file location rules)
3. **02_Test_Configuration_Setup.md** (device setup details)
4. **03_Test_Register_Access.md** (register testing details)

### For Specific Features:
- **Testing timers?** → Pattern 4 + Document 6
- **Testing DMA?** → Document 5
- **Need mocking?** → Document 4

---

## ✅ Pre-Test Checklist

Before running your first test, verify:

- [ ] Test file in correct location: `simics-project/modules/<device>/test/`
- [ ] Test file named correctly: `s-*.py` or `test-*.py`
- [ ] Clock created with `freq_mhz` set BEFORE instantiation
- [ ] Device has `queue = clk` for timing behavior
- [ ] Using `dev_util.bank_regs()` wrapper for register access
- [ ] Bank name matches DML exactly (read DML file)
- [ ] Using `.bank.` namespace: `dev.bank.BankName`
- [ ] Returning conf object, not pre-conf object
- [ ] Using `print()` for test sections, not `start_branch()`
- [ ] Test functions are actually called (not just defined)

---

## 🔍 Quick Reference Card

```python
# Device Creation
dev = simics.pre_conf_object('name', 'class')
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 100  # BEFORE instantiation!
dev.queue = clk
simics.SIM_add_configuration([dev, clk], None)
dev = conf.name  # or simics.SIM_get_object('name')

# Register Access
regs = dev_util.bank_regs(dev.bank.BankName)  # Read DML for exact name
regs.REGISTER.write(value)
value = regs.REGISTER.read()

# Field Access
regs.REGISTER.FIELD.write(value)
value = regs.REGISTER.FIELD.read()

# Simulation Control
simics.SIM_continue(cycles)
elapsed = simics.SIM_cycle_count(dev)

# Assertions
stest.expect_equal(got, expected, "message")
stest.expect_true(condition, "message")

# Test Organization
print("TEST-001: Description")
# ... test code ...
```

---

**Document Status**: Executable Index  
**Generated From**: Session learnings (Watchdog Timer testing)  
**Last Updated**: December 17, 2025  
**Coverage**: 80% of common Simics test cases

**Next Steps**: Copy the patterns you need, write your tests, then read detailed docs only if you encounter edge cases not covered here.
