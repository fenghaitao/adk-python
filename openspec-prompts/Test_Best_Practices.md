# Simics Model Test Best Practices

## Overview

This document provides comprehensive best practices for writing Python-based tests for Simics device models. Testing is a critical part of device model development in Simics Model Builder, helping ensure correctness, catch regressions early, and maintain code quality throughout the development lifecycle.

## ❌ CRITICAL: Test File Location Requirements

### ✅ CORRECT Test Location

**ALL test files MUST be created in the Simics project test directory:**

```
simics-project/                    # ✅ Correct: hyphen (Simics project)
└── modules/<device>/test/
    ├── SUITEINFO
    ├── README
    ├── common.py                  # ✅ Shared configuration
    ├── s-<feature1>.py            # ✅ Individual test files
    ├── s-<feature2>.py
    └── CMakeLists.txt
```

### ❌ FORBIDDEN Test Locations

**NEVER create these directory structures:**

```
simics_project/                    # ❌ FORBIDDEN: underscore (Python package)
simics_project/modules/
simics_project/__init__.py         # ❌ NO Python package markers
simics_project/modules/<device>/test/  # ❌ WRONG location!

test/                              # ❌ FORBIDDEN: project root
<device>_test/                     # ❌ FORBIDDEN: standalone test dir
```

### Why This Matters

1. **Simics Test Execution Model**: Tests run within Simics runtime environment
2. **Official Method**: `./bin/test-runner` is the standard way to run test suites
3. **Real Simics Imports**: Tests import actual Simics APIs (simics, dev_util, stest)
4. **Build Integration**: CMakeLists.txt in test/ directory integrates with Simics build
5. **Correct Location Critical**: Tests must be in `simics-project/modules/<device>/test/` for test-runner to find them

### Running Tests

```bash
# ✅ RECOMMENDED: Run via Simics test-runner (official method)
cd simics-project
./bin/test-runner --suite modules/<device>/test

# ✅ ALSO OK: Run as standalone test (for quick testing)
cd simics-project
./simics -no-gui -no-win -batch-mode modules/<device>/test/s-test.py
```

### Validation After Test Creation

```bash
# Verify tests in correct location
ls -1 simics-project/modules/*/test/s-*.py | wc -l  # Should be > 0

# Check no forbidden directories exist
if [ -d simics_project ]; then
    echo "❌ ERROR: Forbidden simics_project/ directory found!"
    echo "Tests must be in simics-project/ not simics_project/"
    exit 1
fi
```

## Structure of a Simics Device Model Test

### Test Suite Organization

A test suite for a Simics module is located in the `test/` directory within the module's source. The typical structure includes:

```
module-name/
├── test/
│   ├── SUITEINFO          # Marks directory as test suite (can be empty)
│   ├── README             # Human-readable description of test suite
│   ├── tests.py           # Optional: custom test generation logic
│   ├── common.py          # Shared definitions and helper functions
│   ├── s-test1.py         # Individual test file (auto-discovered)
│   ├── s-test2.py         # Individual test file
│   └── s-test3.py         # Individual test file
```

### Key Files

- **SUITEINFO**: Required file that identifies the directory as a test suite. Usually empty but can contain configuration parameters.

- **README**: Optional documentation describing the test suite, coverage, and any known omissions.

- **tests.py**: Optional file for custom test generation. If absent, the test system automatically creates a test for every `s-*.py` file.

- **s-*.py**: Test files following this naming pattern are automatically discovered and run in separate Simics processes.

- **common.py**: Shared code including configuration setup, fake object definitions, and helper functions.

## Core Testing Concepts & Patterns

### 1. Configuration and Simulation Control

Proper configuration is essential for Simics tests. The goal is to create a **minimal configuration** containing only the device under test and necessary support objects (clock, memory).

#### Minimal Configuration Pattern

```python
import simics
import conf
import dev_util
import stest

# ⚠️ WORKAROUND: Disable spec-viol log failures (if needed)
# Some Simics internal spec violations may not relate to your device logic
# Temporarily untrap them to focus on actual test failures
stest.untrap_log('spec-viol')  # Optional: Use only if spec-viol logs block testing

def create_test_config():
    # 1. Create pre-conf objects
    dev = simics.pre_conf_object('dev', 'my_device')
    clk = simics.pre_conf_object('clk', 'clock')
    mem = simics.pre_conf_object('mem', 'memory-space')
    mem.map = []
    # Map bank to memory space [0x1000, 0x2000]
    # Bank name 'regs' comes from DML: "bank regs { ... }" (use actual name from your DML)
    mem.map += [0x1000, #base address
                dev.bank.regs, # Use exact bank name from DML file
                0, # function
                0, # offset
                0x1000]
    
    # 2. Configure attributes BEFORE SIM_add_configuration
    clk.freq_mhz = 10  # ⚠️ CRITICAL: MUST set freq_mhz BEFORE SIM_add_configuration!
    dev.queue = conf.clk  # REQUIRED: Set queue for time-dependent objects
    
    # 3. Add configuration
    simics.SIM_add_configuration([dev, clk, mem], None)
    
    return (conf.dev, conf.clk, conf.mem)
```

**❌ CRITICAL: create_config() MUST Return conf_object, NOT pre_conf_object**

A common mistake is returning pre-configuration objects from `create_config()`. Pre-conf objects are **ONLY** for configuration setup and **CANNOT** be used in test scripts.

```python
# ❌ WRONG - Returning pre_conf_object (unusable in tests):
def create_config():
    dev = simics.pre_conf_object('dut1', 'dut_class')
    clk = simics.pre_conf_object('clk', 'clock')
    clk.freq_mhz = 1
    dev.queue = clk
    simics.SIM_add_configuration([dev, clk], None)
    
    return (dev, clk)  # ❌ WRONG! Returning pre_conf_object

# Later in test:
(dut, clk) = create_config()
regs = dev_util.bank_regs(dut.bank.regs)  # ❌ FAILS! dut is pre_conf_object, not conf_object

# ✅ CORRECT - Returning conf_object via conf.<device_name>:
def create_config():
    dev = simics.pre_conf_object('dut1', 'dut_class')
    clk = simics.pre_conf_object('clk', 'clock')
    clk.freq_mhz = 1
    dev.queue = clk
    simics.SIM_add_configuration([dev, clk], None)
    
    return (conf.dut1, conf.clk)  # ✅ CORRECT! Returning conf_object

# Later in test:
(dut, clk) = create_config()
regs = dev_util.bank_regs(dut.bank.regs)  # ✅ WORKS! dut is conf_object
```

**Why This Matters:**
- `simics.pre_conf_object()` returns a **pre-configuration object** used ONLY for setup
- After `SIM_add_configuration()`, the actual **configuration object** is available via `conf.<object_name>`
- Pre-conf objects have limited API and cannot be used for register access, simulation control, etc.
- **ALWAYS return `conf.<object_name>`**, not the pre-conf object variable

**Pattern: Return conf_object, not pre_conf_object**
```python
def create_config():
    # Step 1: Create pre-conf objects with names
    dev = simics.pre_conf_object('device_name', 'class')  # Note the name 'device_name'
    
    # Step 2: Configure and instantiate
    simics.SIM_add_configuration([dev], None)
    
    # Step 3: Return conf_object using the name from step 1
    return conf.device_name  # ✅ Use conf.<name>, NOT the pre-conf variable 'dev'
```

**❌ CRITICAL: Clock freq_mhz MUST Be Set Before SIM_add_configuration()**

```python
# ❌ WRONG - Setting freq_mhz AFTER object creation:
clk = simics.pre_conf_object('clk', 'clock')
simics.SIM_add_configuration([dev, clk], None)  # ❌ freq_mhz not set yet!
conf.clk.freq_mhz = 10  # ❌ TOO LATE! Object already instantiated

# ✅ CORRECT - Setting freq_mhz BEFORE object creation:
clk = simics.pre_conf_object('clk', 'clock')
clk.freq_mhz = 10  # ✅ Set on pre-conf object BEFORE SIM_add_configuration
simics.SIM_add_configuration([dev, clk], None)  # ✅ Now freq_mhz is configured
```

**Why This Matters:**
- `freq_mhz` is a **required attribute** for clock objects
- Must be set on the pre-conf object (before `SIM_add_configuration`)
- Setting it after instantiation causes errors or undefined behavior
- All time-dependent devices rely on correct clock frequency

**Pattern: All required attributes BEFORE SIM_add_configuration**
```python
# Create pre-conf objects
obj = simics.pre_conf_object('name', 'class')

# Configure ALL required attributes
obj.required_attr1 = value1
obj.required_attr2 = value2

# THEN instantiate
simics.SIM_add_configuration([obj], None)
```

#### Running the Simulation

Use `simics.SIM_continue()` to advance time. This must be called from **Global Context**.

```python
# Run for specific cycles
start = simics.SIM_cycle_count(conf.clk)
simics.SIM_continue(1000)
elapsed = simics.SIM_cycle_count(conf.clk) - start
stest.expect_equal(elapsed, 1000, "Time did not advance correctly")
```

### 2. Register Access

Testing register access is the most common task. Use `dev_util` helpers for convenience.

#### **CRITICAL: Finding Bank Names from DML**

**ALWAYS read the DML file to find the exact bank name.** Bank names in DML map directly to Python attributes:

```dml
// In <device>.dml:
bank regs {          // ← Bank name is "regs" (could be any name like reg_if, regbank, etc.)
    register CONTROL { ... }
    register STATUS { ... }
}
```

```python
# In test.py - use the EXACT bank name from DML:
regs = dev_util.bank_regs(conf.dev.bank.regs)  # ✅ Correct: matches DML "bank regs"
```

**❌ CRITICAL Anti-Pattern: Missing `.bank.` in dev_util.bank_regs()**

**ALWAYS use `device.bank.<bank_name>`, NOT `device.<bank_name>` directly!**

```python
# ❌ WRONG - Missing .bank. namespace:
regs = dev_util.bank_regs(dut.regs)  # ❌ WRONG! Missing .bank.

# ✅ CORRECT - Include .bank. namespace:
regs = dev_util.bank_regs(dut.bank.regs)  # ✅ Correct! device.bank.<bank_name>
```

**Pattern: `device.bank.<bank_name>` is ALWAYS required**
- DML: `bank regs { ... }` → Python: `device.bank.regs`
- DML: `bank reg_if { ... }` → Python: `device.bank.reg_if`

**Anti-Pattern: DO NOT scan/discover banks dynamically**

```python
# ❌ WRONG - Never write defensive discovery code:
for name in ['reg_if', 'regif', 'regs', 'bank']:  # ❌ Unnecessary complexity
    try:
        obj = getattr(dev, name)
        regs = dev_util.bank_regs(obj)
        break
    except: pass

# ✅ CORRECT - Read DML, use exact bank name:
regs = dev_util.bank_regs(conf.dev.bank.<bank_name>)  # Replace <bank_name> with actual name from DML
```

#### Using `bank_regs` (Recommended)

The `bank_regs` utility creates a proxy for easy read/write access to registers and fields.

```python
# Example: If DML defines "bank regs { ... }" (or any other name)
regs = dev_util.bank_regs(conf.dev.bank.regs)  # Use exact bank name from DML

# Full register access
regs.control.write(0xdeadbeef)
stest.expect_equal(regs.control.read(), 0xdeadbeef)

# Field access (Read-Modify-Write)
regs.status.write(dev_util.READ, enable=1, mode=3)
stest.expect_equal(regs.status.field.enable.read(), 1)
```

**Workflow:**
1. Read `<device>.dml`, find `bank <bank_name> { ... }`
2. Use `dev_util.bank_regs(conf.device.bank.<bank_name>)` with exact bank name from step 1
3. Never guess or scan - the bank name is always explicit in DML

**❌ CRITICAL Anti-Pattern: Direct Register Access via device.bank.<bank_name>**

**NEVER access registers directly via `device.bank.<bank_name>.<register_name>`!**
**ALWAYS use `dev_util.bank_regs(device.bank.<bank_name>).<register_name>`!**

```python
# ❌ WRONG - Direct access to registers (missing dev_util.bank_regs wrapper):
def run():
    (dut, pic) = create_config()
    
    # ❌ WRONG! Direct access without dev_util.bank_regs()
    wdt = dut.bank.wdt_regs
    wdt.WDOGLOAD.write(0x10)  # ❌ FAILS! No write() method on bank object

# ✅ CORRECT - Use dev_util.bank_regs() wrapper:
def run():
    (dut, pic) = create_config()
    
    # ✅ CORRECT! Wrap with dev_util.bank_regs()
    wdt = dev_util.bank_regs(dut.bank.wdt_regs)
    wdt.WDOGLOAD.write(0x10)  # ✅ WORKS! bank_regs() provides read/write API
```

**Why This Matters:**
- `device.bank.<bank_name>` is a **raw Simics bank object** without convenient read/write methods
- `dev_util.bank_regs()` creates a **proxy wrapper** with easy `.read()` and `.write()` methods
- Direct bank access requires low-level Simics APIs and is error-prone
- **ALWAYS wrap with `dev_util.bank_regs()` for register testing**

**Pattern: ALWAYS use dev_util.bank_regs() wrapper**
```python
# Step 1: Get device from create_config()
(dut, pic) = create_config()

# Step 2: ALWAYS wrap bank with dev_util.bank_regs()
regs = dev_util.bank_regs(dut.bank.<bank_name>)  # ✅ Required wrapper

# Step 3: Now use convenient register API
regs.CONTROL.write(0x1)
value = regs.STATUS.read()
```

**Detection Rule:**
- ❌ Flag any code like: `var = device.bank.<name>` followed by `var.<register>.write()`
- ✅ Require pattern: `var = dev_util.bank_regs(device.bank.<name>)` then `var.<register>.write()`

#### Using `Register_LE/BE` (Specific Layouts)

Use `Register_LE` (Little Endian) or `Register_BE` (Big Endian) when you need to test specific offsets or endianness behavior explicitly.

```python
# Example: If DML defines "bank regs { register control @ 0x00 ... }"
control = dev_util.Register_LE(
    conf.dev.bank.regs, 0x00, size=4,  # Use exact bank name from DML
    bitfield=dev_util.Bitfield_LE({'enable': 31, 'mode': (30, 28)})
)

control.write(0x80000000)
stest.expect_equal(control.enable, 1)
```

### 3. Environment Simulation (Fakes & Interfaces)

Isolate your device by using **Fake Objects** (also called "mock objects", "signal mocks", or "mock signal interfaces") instead of real dependencies. This improves test speed and stability.

#### Fake Object Pattern

```python
import pyobj

class FakePic(pyobj.ConfObject):
    class raised(pyobj.SimpleAttribute(True, 'b')): pass
    
    class signal(pyobj.Interface):
        def signal_raise(self): self._up.raised.val = True
        def signal_lower(self): self._up.raised.val = False

# In config setup:
fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')
dev.pic = fake_pic
```

#### Interface Testing

Verify your device interacts correctly with the environment (e.g., raising interrupts).

```python
# Trigger device action
regs.control.write(1)  # Suppose this triggers interrupt

# Verify side effect on fake object
stest.expect_equal(conf.fake_pic.raised, 1, "Interrupt not raised")
```

### 4. Memory and DMA

For DMA devices, use `dev_util.Memory` to simulate system memory.

#### DMA Test Pattern

```python
# 1. Setup Memory
mem = dev_util.Memory()
dev.phys_mem = mem.obj

# 2. Prepare Data
src = 0x1000; dst = 0x2000; size = 256
data = tuple(range(size))
mem.write(src, data)

# 3. Trigger DMA
regs.dma_src.write(src)
regs.dma_dst.write(dst)
regs.dma_len.write(size)
regs.dma_cmd.write(1) # Start

# 4. Verify Result
stest.expect_equal(mem.read(dst, size), list(data), "DMA mismatch")
```

#### Descriptors

Use `dev_util.Layout` to map Python objects to memory structures (descriptors).

```python
desc = dev_util.Layout_LE(mem, 0x1000, {
    'control': (0, 4),
    'status': (4, 4)
})
desc.control = 0x1
# ... device runs ...
stest.expect_equal(desc.status, 0x1) # Verify device updated status
```

### 5. Events and Timing

Simics uses **Event Queues** (Time, Cycle, Step) associated with clocks to manage time.

#### Event-Based Testing

To test time-dependent behavior (timers, delays):

1.  **Configure**: Set up the operation.
2.  **Wait**: Advance time using `SIM_continue()`.
3.  **Verify**: Check if the event occurred.

```python
# Start timer (1000 cycles)
regs.timer.write(1000)
regs.start.write(1)

# Advance time
simics.SIM_continue(1000)

# Verify interrupt fired
stest.expect_equal(conf.fake_pic.raised, 1, "Timer interrupt missing")
```

#### Event Best Practices
- **Transform to Time Functions**: Calculate values based on `SIM_cycle_count` instead of periodic events where possible.
- **Avoid Continuous Events**: They kill performance.
- **Cancel Events**: Clean up in `destroy()` or when disabled.

## Helper Utilities

### Custom Assertion Functions

```python
def approx_equal(got, expected, tolerance):
    """Check equality with tolerance for timing variations"""
    if abs(got - expected) > tolerance:
        raise stest.fail(f"got {got}, expected {expected}")

def expect_in_range(value, min_val, max_val, msg=""):
    """Check value is within range"""
    if not (min_val <= value <= max_val):
        raise stest.fail(
            f"{msg}: {value} not in range [{min_val}, {max_val}]"
        )
```

### Struct Helper

```python
class Struct:
    """Simple struct for organizing related values"""
    def __init__(self, **kws):
        for (k, v) in list(kws.items()):
            setattr(self, k, v)
```

## Example Test Suite Structure

Here is a complete example showing how to organize a test suite with shared code and individual tests.

**common.py** (Shared setup):
```python
import simics
import conf
import dev_util
import pyobj

# Fake object definition
class FakePic(pyobj.ConfObject):
    class raised(pyobj.SimpleAttribute(0, 'i')): pass
    class signal(pyobj.Interface):
        def signal_raise(self): self._up.raised.val += 1
        def signal_lower(self): self._up.raised.val -= 1

# Configuration helper
def create_config():
    dut = simics.pre_conf_object('test_device', 'test_class')
    clk = simics.pre_conf_object('clk', 'clock', [["freq_mhz", 100]])
    fake_pic = simics.pre_conf_object('fake_pic', 'FakePic')

    dut.queue = conf.clk
    dut.pic = conf.fake_pic
    
    simics.SIM_add_configuration([dut, clk, fake_pic], None)
    return (conf.test_device, conf.fake_pic)
```

**s-<feature>.py** (Test file):
```python
import simics
import dev_util
import stest
from common import create_config

# 1. Setup
(dut, pic) = create_config()
# 2. Get bank proxy - ALWAYS read DML first to find bank name
# Example: If DML defines "bank regs { ... }", use exact name:
regs = dev_util.bank_regs(dut.bank.regs)

# 3. Test Register Access
regs.load.write(0x5)
stest.expect_equal(regs.timer_value.read(), 0x5, "TimeValue register mismatch while loading new timer configuration")
regs.control.write(0x1)
stest.expect_equal(regs.control.read(), 0x1, "Control register mismatch")

# 4. Test Side Effects
regs.trigger_irq.write(1)
stest.expect_equal(pic.raised, 1, "Interrupt not raised")

# 5. Test Timing
int_number = pic.raised
regs.load.write(1000) # re-configure timer
regs.control.write(0x1)  # Start timer
start = simics.SIM_cycle_count(dut.queue)
simics.SIM_continue(500) # run simulation 500 cycles
stest.expect_equal(regs.timer_value.read(), 500, "Timer value mismatch after 500 cycles")
simics.SIM_continue(501) # run simulation 501 cycles
elapsed = simics.SIM_cycle_count(dut.queue) - start
stest.expect_equal(elapsed, 1001, "Time did not advance")
stest.expect_equal(pic.raised, int_number + 1, "Interrupt not raised")
stest.expect_equal(regs.timer_value.read(), 0, "Timer value should be 0 after expiry")
```
or with function wrapper (**CRITICAL - must call the function!**):

```python
import simics
import dev_util
import stest
from common import create_config

def test_feature():
    # 1. Setup
    (dut, pic) = create_config()
    
    # 2. Get bank proxy - read DML to find exact bank name (e.g., "bank regs")
    regs = dev_util.bank_regs(dut.bank.regs)

    # 3. Test Register Access
    regs.load.write(0x5)
    stest.expect_equal(regs.timer_value.read(), 0x5, "TimeValue register mismatch while loading new timer configuration")
    regs.control.write(0x1)
    stest.expect_equal(regs.control.read(), 0x1, "Control register mismatch")

    '''
    More test content ...
    '''

# ❌ CRITICAL: NEVER define test_feature() or run() without calling it!
# Test code inside a function will NEVER execute unless you call the function.

if __name__ == "__main__":
    test_feature()  # ✅ REQUIRED: Actually execute the test
```

**Anti-Pattern: Defining but Not Calling Test Function**

```python
# ❌ WRONG - Test will NEVER run (silent failure):
def test_feature():
    device = simics.SIM_object_by_name('dut1', 0)
    regs = dev_util.bank_regs(device.bank.regs)
    stest.expect_equal(regs.control.read(), 0x1, "Test")
    # File ends here - test_feature() is NEVER called!

# ✅ CORRECT - Test executes:
def test_feature():
    device = simics.SIM_object_by_name('dut1', 0)
    regs = dev_util.bank_regs(device.bank.regs)
    stest.expect_equal(regs.control.read(), 0x1, "Test")

test_feature()  # ✅ Actually execute the test!

# ✅ ALSO CORRECT - Direct code (no function wrapper):
device = simics.SIM_object_by_name('dut1', 0)
regs = dev_util.bank_regs(device.bank.regs)
stest.expect_equal(regs.control.read(), 0x1, "Test")
# Executes immediately when file is imported
```

## Best Practices Checklist

### 1. Test Coverage & Organization
- **Comprehensive but Focused**: Cover implemented features; document omissions.
- **Independent Subtests**: Use separate files (`s-*.py`) for independent features.
- **Shared Code**: Put common setup in `common.py`.

### 2. Performance
- **Fast Execution**: Tests should run in seconds.
- **Minimal Config**: Only create necessary objects.
- **Use Fakes**: Avoid full system simulation dependencies.

### 3. Code Quality
- **Descriptive Names**: Clear test filenames and function names.
- **Good Error Messages**: Use `stest` assertions with helpful messages.
- **Documentation**: Explain what each test covers.

### 4. **Essential Testing Practices**:
- **ALWAYS read the DML file first** to find exact bank names (e.g., `bank regs` → use `dev.bank.regs`)
- **NEVER scan/discover banks dynamically** - bank names are explicit in DML, not runtime discoveries
- **Clock configuration is mandatory** for time-based devices in unit tests
- Create and assign clocks **before** posting any time events
- Test time-dependent behavior explicitly with `SIM_continue()`
- **Use Fake Objects (Section 3)** to mock signal interfaces when DML uses `connect` blocks
- Use `dev_util.bank_regs()` for clean register access with exact bank name from DML
- Follow the `s-<feature>.py` naming convention

### 5. **Quick Troubleshooting Checklist**:
- Queue not set error → Create clock: `device.queue = clk`
- Segmentfault on test → Add Fake Objects (Section 3) for `connect` interfaces
- Events don't fire → Check clock frequency and time advancement

## Conclusion

Effective testing is essential for reliable device models. By following these best practices—using minimal configurations, leveraging fake objects, and structuring tests logically—you can ensure robust and maintainable device models.
