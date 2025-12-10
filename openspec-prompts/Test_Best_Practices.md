# Simics Model Test Best Practices

## Overview

This document provides comprehensive best practices for writing Python-based tests for Simics device models. Testing is a critical part of device model development in Simics Model Builder, helping ensure correctness, catch regressions early, and maintain code quality throughout the development lifecycle.

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

def create_test_config():
    # 1. Create pre-conf objects
    dev = simics.pre_conf_object('dev', 'my_device')
    clk = simics.pre_conf_object('clk', 'clock')
    mem = simics.pre_conf_object('mem', 'memory-space')
    mem.map = []
    # map dev.bank.regs to memory space [0x1000, 0x2000]
    mem.map += [0x1000, #base address
                dev.bank.regs, # object
                0, # function
                0, # offset
                0x1000]
    
    # 2. Configure attributes
    clk.freq_mhz = 1000
    dev.queue = conf.clk  # REQUIRED: Set queue for time-dependent objects
    
    # 3. Add configuration
    simics.SIM_add_configuration([dev, clk, mem], None)
    
    return (conf.dev, conf.clk, conf.mem)
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

#### Using `bank_regs` (Recommended)

The `bank_regs` utility creates a proxy for easy read/write access to registers and fields.

```python
# Create proxy
regs = dev_util.bank_regs(conf.dev.bank.regs)

# Full register access
regs.control.write(0xdeadbeef)
stest.expect_equal(regs.control.read(), 0xdeadbeef)

# Field access (Read-Modify-Write)
regs.status.write(dev_util.READ, enable=1, mode=3)
stest.expect_equal(regs.status.field.enable.read(), 1)
```

#### Using `Register_LE/BE` (Specific Layouts)

Use `Register_LE` (Little Endian) or `Register_BE` (Big Endian) when you need to test specific offsets or endianness behavior explicitly.

```python
# Define register at specific offset
control = dev_util.Register_LE(
    conf.dev.bank.regs, 0x00, size=4,
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
regs = dev_util.bank_regs(dut.bank.regs)

# 2. Test Register Access
regs.load.write(0x5)
stest.expect_equal(regs.timer_value.read(), 0x5, "TimeValue register mismatch while loading new timer configuration")
regs.control.write(0x1)
stest.expect_equal(regs.control.read(), 0x1, "Control register mismatch")

# 3. Test Side Effects
regs.trigger_irq.write(1)
stest.expect_equal(pic.raised, 1, "Interrupt not raised")

# 4. Test Timing
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
or

```python
import simics
import dev_util
import stest
from common import create_config

def test_feature():
    # 1. Setup
    (dut, pic) = create_config()
    regs = dev_util.bank_regs(dut.bank.regs)

    # 2. Test Register Access
    regs.load.write(0x5)
    stest.expect_equal(regs.timer_value.read(), 0x5, "TimeValue register mismatch while loading new timer configuration")
    regs.control.write(0x1)
    stest.expect_equal(regs.control.read(), 0x1, "Control register mismatch")

    '''
    More test content ...
    '''

if __name__ == "__main__":
    test_feature()
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
- **Clock configuration is mandatory** for time-based devices in unit tests
- Create and assign clocks **before** posting any time events
- Test time-dependent behavior explicitly with `SIM_continue()`
- **Use Fake Objects (Section 3)** to mock signal interfaces when DML uses `connect` blocks
- Use `dev_util.bank_regs()` for clean register access
- Follow the `s-<feature>.py` naming convention

### 5. **Quick Troubleshooting Checklist**:
- Queue not set error → Create clock: `device.queue = clk`
- Segmentfault on test → Add Fake Objects (Section 3) for `connect` interfaces
- Events don't fire → Check clock frequency and time advancement

## Conclusion

Effective testing is essential for reliable device models. By following these best practices—using minimal configurations, leveraging fake objects, and structuring tests logically—you can ensure robust and maintainable device models.
