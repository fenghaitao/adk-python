# Basic Simics Test Concepts

## Overview

Only in a Simics project the device can be loaded and tested. You can use tool to create a Simics project.

If you are not in such project directory, you can write test but you cannot execute them.

1. You can use tool to add device skeleton. The testcase will be in the folder `modules/<device-name>/test`.

2. Then you can replace the `<device-name>_common.py` to your own testcase to create the devices and the interfaces that the device need to connect to.

3. For each testcase, the agent should create a py file with prefix `s-*.py` such as stest.

4. Use `./bin/test-runner --project-only <test_relative_path>` to run a specific test. Use `./bin/test-runner --project-only` to run all tests in this project.

5. Make sure you have written ALL tests required in your test plan.

## IMPORTANT NOTE

- You should check if you are in a simics project. A Simics project's directory tree is like:
```
.
├── CMakeLists.txt
├── GNUmakefile
├── PROJECT_SETUP_COMPLETE.md
├── bin
│   ├── dmlc
│   ├── mini-python
│   ├── project-setup
│   ├── setup-venv
│   ├── test-runner
│   └── ..
├── cmake-wrapper.mk
├── compiler.mk
├── config.mk
...
├── modules
│   └── ...
...
├── simics
├── targets
│   └── ...
```
- You should look up knowledge about tests by using the tools.
- Tests are written in python. Syntax is different from DML. DO NOT use DML syntax knowledge on python.


## Sample for common file

Here is an example python code in a file named `dut_common.py` which can be used to create devices to test.

```python
# Some common simics core library, from simics install path, for linux:
# it's in <simics install path>/linux64/lib/python-py3
import conf # import `conf` separately
import pyobj
from simics import (SIM_add_configuration, pre_conf_object)
from stest import untrap_log # if need to ignore warns

'''
For testing the device that that can trigger signals, we need to create a signaling object (`irq_target`) with pyobj. This is same as creating a DML device, but in python.

NOTE: You should check if the singals are correctly triggered on this signaling object when testing.
'''
class irq_target(pyobj.ConfObject):
    '''
    Create an attribute named `level` and `i` means its type is int
    '''
    class level(pyobj.SimpleAttribute(0, 'i')):
        pass

    '''
    Create an Sample Interface of a signal, when the signal raised by the device, the `level` attribute plus 1, lower then minus 1
    '''
    class signal(pyobj.Interface):
        def signal_raise(self):
            self._up.level.val += 1
        def signal_lower (self):
            self._up.level.val -= 1

'''
`create_device` is a common method by convention, it generaetes all the device objects needed by the test. Don't modify the method name of it.

You can add some params to init or set the attribute of the device, the sample here adds `cpu_freq_mhz` and `timer_freq_mhz`, both of them is to used to set the attributes in the device DML.
'''
def create_device(*, cpu_freq_mhz=1200, timer_freq_mhz=125):

    dut = pre_conf_object('dut', 'device_module_name') # create the pre_conf objects for the device module, if some attribute is required at initialization, you must set it in this method

    dut.freq_mhz = timer_freq_mhz # set some attributes

    # Assuming the device contains interface `GTIMERINTR` with `connect` key words, the interface needs to connect other interface objects, create the signal objects.
    # In this sample, assuming the `GTIMERINTR` is a attribute list so we create an object list to connect
    phy_irqs = [pre_conf_object('irq%d' % i, 'irq_target') for i in range(8)]
    dut.GTIMERINTR = phy_irqs

    # IMPORTANT: If the device doesn't connect a core object or an object with queue, you MUST create a clock for this device.
    clock = pre_conf_object('clock', 'clock')
    clock.freq_mhz = cpu_freq_mhz
    dut.queue = clock

    # All the objects must be add to the configuration after generating with `pre_conf_object`
    SIM_add_configuration([clock, dut, *phy_irqs], None)

    # return the device with the interface connected.
    return conf.dut # `conf` is not under `simics`. Just `conf`.

```

## Sample for Test cases
### Sample test case
```python
import dut_common
import simics

import dev_util # use the bank_regs to access the register
import stest # stest is used to evaluate the test result

cpu_freq = 2000*1000*1000
timer_freq = 100*1000*1000

def reset(dut):
    # ... dut reset logics ...

# Test the register access. It's a general test for almost all the model
def test_register_access(dut):
    reset(dut) # reset the dut in the beginning is always a good habit.

    # test register with dml register name, for dut.bank.regs, the 'regs' means that the model has the bank named 'regs'
    regs = dev_util.bank_regs(dut.bank.regs)

    # NOTE you MUST use read() and write() to manipulate registers.
    regs.CNTFRQ.write(timer_freq)
    # then read the CNTFRQ register with read method
    stest.expect_equal(regs.CNTFRQ.read(), timer_freq)

# This is a functional testcase example. You should check the functionality with respect to the spec.
def test_timer_clock(dut):
    reset(dut)

    regs = dev_util.bank_regs(dut.bank.regs)

    clk = simics.SIM_object_clock(dut) # get the `clock` of current device
    cycle_iface = simics.SIM_get_interface(clk, 'cycle') # get the `cycle` interface implemented by the `clk` device
    current_cpu_cycle_count = cycle_iface.get_cycle_count()

    freq_ratio = cpu_freq / timer_freq
    # Read the `CNTPCT` registers
    stest.expect_equal(regs.CNTPCT.read(), int(current_cpu_cycle_count/freq_ratio))

    # SIM_continue to run for 10000 cycles.
    simics.SIM_continue(10000)
    # or use cli command:
    # cli.run_command('run-cycles 10000')

    # check the `CNTPCT` registers again
    stest.expect_equal(regs.CNTPCT.read(),
                 int((current_cpu_cycle_count+10000)/freq_ratio))

def run(dut):
    # Test for 50 times
    for i in range(50):
        test_register_access(dut)
        test_timer_clock(dut)

if __name__ == '__main__':
    run(dut_common.create_device())

```

# attrtype

## Type Definition Rules
- **Simple types**: Single letters represent basic types:
  - `i` = int
  - `f` = float
  - `s` = string
  - `b` = bool
  - `d` = data
  - `o` = object
  - `D` = dictionary
  - `n` = nil
  - `a` = any
- **Multiple types**: Use `|` operator for OR logic (e.g., `s|o` = string OR object)
- **Lists**: Defined with square brackets `[ ]` in three ways:
  - **Fixed elements**: `[iffsb]` = exactly 5 elements (int, float, float, string, bool)
  - **Variable arbitrary**: 
    - `[i*]` = zero or more integers
    - `[i+]` = one or more integers
  - **Size specifier**: 
    - `[i{1:4}]` = 1 to 4 integers

## Operator Precedence
- `|` has higher precedence than juxtaposition in lists
- `[i|si|s]` = two-element list where each element is integer OR string
- Use commas for clarity (ignored): `[i|s,i|s]`

## Complex Type Examples
- `"[s*]|s"` = string OR list of strings (possibly empty)

## Limitations and Workarounds
- Complex variable-size lists: Type strings cannot describe lists with mixed variable elements (e.g., one object + variable integers)
- Fallback options:
  - Use `a` type and implement custom type checking in `set()` function
  - Restructure attribute (e.g., use sub-lists: `[o[i+]]`)
  - Split into multiple simpler attributes

# Info and Status
- In `module_load.py`, you should implement working `info` and `status` commands for your device. Example:
```python
# .. other things omitted ..
def get_info(obj):
    return [ (None,
              [ ("System Frequency (MHz)", obj.sys_mhz),
                # ..
            ]) ]
cli.new_info_command("device_name", get_info)
def get_status(obj):
    try:
        ctrl = obj.regs_CTRL
    return [ (None,[ ("CTRL Register", "0x%08x" % ctrl),
             ("Device State", [ ("State 1", some_thing),])])]
cli.new_status_command("device_name", get_status)
```

# Modeling with Python (pyobj)

## The pyobj Python Module and ConfObject Class

- Import `pyobj` module for Simics Python device development
- Contains `ConfObject` base class for all Python devices
- Device auto-registers as Simics class with `info`/`status` commands
- In `pyobj`, nested classes define attributes/interfaces/ports/events; they are NOT per-instance. Simics instantiates them automatically when the ConfObject is created.
- Access Simics `conf_object_t` via `obj` member

### ConfObject Class Basic Methods

- `_initialize(self)`: Called during object instantiation; set values before attributes/interfaces defined; always call `super()._initialize()`
- `_finalize(self)`: Called after all attributes set
- `_pre_delete()`: Called before object deletion

### ConfObject Class Parameters

- `_class_desc`: Short device description for help/GUI
- `_do_not_init`: Set to `object()` to prevent class registration (base classes only)
- `register()`: Manually register a subclass

### ConfObject Class Example
```python
import simics
import pyobj
class foo(pyobj.ConfObject):
    """Long documentation for class."""
    _class_desc = 'short description <50 chars, lowercase, no dot'
    def _initialize(self):
        super()._initialize()
        self.my_val = 4711
    
    class woot(pyobj.SimpleAttribute(0, 'i|n')):
        """A four-letter attribute"""

    class signal(pyobj.Interface):
        def signal_raise(self): self.val = True
        def signal_lower(self): self.val = False
        def _initialize(self): self.val = False
```

## Attributes

- Create attributes by defining classes inheriting `pyobj.Attribute` inside ConfObject class.
- Required methods: `_initialize()`
- Optional methods: `getter()`, `setter()` (omit to prevent read or write)
- Parameters: `attrattr` (optional/required/pseudo), `attrtype` (type string)
```python
class foo(pyobj.ConfObject):
    # .. omitted ..
    
    class wee(pyobj.Attribute):
        """Attribute documentation."""
        attrattr = simics.Sim_Attr_Pseudo # `Sim_Attr_Optional` by default
        attrtype = 'i'
        def _initialize(self):
            self.val = 4711
        def getter(self):
            return self.val
        def setter(self, val):
            self.val = val
```

- **Simple attributes**: Use `pyobj.SimpleAttribute(default_value, attrtype, attrattr=Sim_Attr_Optional)`. Attribute value will be automatically stored in the `val` parameter.
- No need to use `val` for instantiated conf object.
```python
class foo(pyobj.ConfObject):
    # .. omitted ..

    class woot(pyobj.SimpleAttribute(0, 'i|n')):
        """Simple attribute with default value 0"""

# ... omitted ...
foo_instance = simics.pre_conf_object('foo_instance', 'foo')
foo_instance.woot = 1 # No need to use `.val` here.
```

## Class Attributes

- Use `pyobj.ClassAttribute` for class-level attributes
- Store value in `val` member
- Use `@classmethod` decorators
```python
# other pyobj stuffs omitted ...
class wee(pyobj.ClassAttribute):
    """Class attribute documentation."""
    attrtype = 'i'
    val = 4711
    @classmethod
    def getter(cls): return cls.val
    @classmethod
    def setter(cls, val): cls.val = val
```

## The _up Member

- Access containing class from nested classes using `_up`
- Example accessing device field from attribute:
```python
class foo(pyobj.ConfObject):
    def _initialize(self):
        self.my_val = 4711
    
    class lost(pyobj.Attribute):
        def getter(self):
            return self._up.my_val  # Access field of the parent class `foo`.
```

## Interfaces

- Implementing interface by defining classes inheriting `pyobj.Interface`
- Interface name taken from class name
- Example:
```python
class signal(pyobj.Interface):
    def signal_raise(self): self.val = True
    def signal_lower(self): self.val = False
    def _initialize(self): self.val = False
```

- **Port interfaces**: Place `pyobj.Interface` classes inside `pyobj.Port` class
- **Access interfaces**: Use `obj.iface.interface_name.method()`
```python
val = conf.phys_mem.iface.memory_space.read(conf.cpu0, 0x1234, 4, 0) # accessing `memory_space` interface's read method.
```

## Port Objects

- Use for multiple implementations of same interface
- Define port objects as classes inheriting `pyobj.PortObject`
- Example:
```python
class myclass(pyobj.ConfObject):
    # Define the port object 'myobj.port.RESET'
    class RESET(pyobj.PortObject):
        class signal(pyobj.Interface):
            def signal_raise(self):
                print("signal_raise")
    
    # Define the port object 'myobj.bus_clock' as a 'cycle-counter' class, which inplemented multiple interfaces and attributes including `frequency`.
    class bus_clock(pyobj.PortObject):
        namespace = ""
        classname = "cycle-counter"
    
    def _initialize(self):
        super()._initialize()
        simics.SIM_set_attribute_default(self.obj.bus_clock, "frequency", 1E6) # setting `cycle-counter.frequency`
```

## Events

- Create events by defining classes inheriting `pyobj.Event`
- **Required method**: `callback(data)` - called when event triggers

### Event Posting
- Use `post(clock, data, <duration>)` method
- Duration options: `seconds=X`, `cycles=X`, `steps=X`
```python
ev.post(a_clock, some_data, seconds=4.711)
ev.post(a_clock, some_data, cycles=4711)
ev.post(a_clock, some_data, steps=4711)
```

### Event Cancellation
- `cancel_time(clock, match_fun)` or `cancel_step(clock, match_fun)`
- `match_fun`: optional function to filter which events to cancel

### Optional Event Methods
- **`destroy(data)`**: Called when event removed without triggering.
- **`get_value(data)`/`set_value(val)`**: Checkpoint conversion
- **`describe(data)`**: Human-readable description for print-event-queue
- **`flags`**: Set to `Sim_EC_Notsaved` to skip checkpointing

### Event Examples
```python
class foo(pyobj.ConfObject):
    class ev1(pyobj.Event):
        def callback(self, data):
            pass # do something
    
    class ev2(pyobj.Event):
        def callback(self, data):
            pass # do something
        def get_value(self, data):
            return str(data)
        def set_value(self, val):
            return int(val)
        def describe(self, data):
            return 'ev2 with %s' % data
    
    class ev3(pyobj.Event):
        flags = simics.Sim_EC_Notsaved # no `get_value` and `set_value` allowed for `Sim_EC_Notsaved`
        def callback(self, data):
            self._up.do_this_third_thing(data) # do something
```

# Writing Model Tests

## Test Overview
- Write functional tests for device models using Python.
- Use libraries: `dev_util`, `pyobj`, `stest`.
- Focus on testing the model under test (MUT) without dependencies on the surrounding system.
- Utilize clock objects for models dependent on timing.
- Provide real `image` objects when large data structures are needed.

### Anatomy of a Test Suite
- `SUITEINFO`: Indicates a test suite, can be empty.
- `README.txt`: Optional, human-readable description.
- `tests.py`: Optional, generates tests.
- `s-*.py`: Contains each test to be run individually.
  
### Configuration
- Use:
  ```python
  my_dev = pre_conf_object('dev', 'my_dev_class_name')
  my_dev.attr1 = 'foo'
  my_dev.attr2 = 4711
  SIM_add_configuration([my_dev], None)
  my_dev = conf.my_dev
  ```
- Fake objects for dependencies (e.g., interrupt controllers):
  ```python
  import pyobj
  class FakePic(pyobj.ConfObject):
    class raised(pyobj.SimpleAttribute(0, 'i')):
        '''An attribute to store the signal state'''

    class signal(pyobj.Interface):
        def signal_raise(self):
            self._up.raised.val += 1
        def signal_lower(self):
            self._up.raised.val -= 1
  ```
- Configure the model to connect to fake objects:
  ```python
  fake_pic = pre_conf_object('fake_pic', 'FakePic')
  my_dev = pre_conf_object('dev', 'my_dev_class_name')
  my_dev.pic = fake_pic
  SIM_add_configuration([my_dev, fake_pic], None)
  my_dev = conf.my_dev
  fake_pic = conf.fake_pic
  ```
- Some collaborators cannot be faked in Python (e.g. interfaces using non-wrappable C types). In such cases, write a small DML device to translate between that interface and a Python-wrappable one, then use `pyobj` to fake the wrappable interface in tests.


### Accessing Device Registers from Tests
- Use `dev_util.bank_regs(...)`:
  ```python
  import dev_util
  from stest import expect_equal
  
  my_device = pre_conf_object('dev', 'my_device_class')
  SIM_add_configuration([my_device], None)
  regs = dev_util.bank_regs(conf.dev.bank.regs)
  
  regs.r1.write(0xdeadbeef)
  expect_equal(regs.r1.read(), 0xdeadbeef)
  
  regs.r2.write(dev_util.READ, ctrl=0xA, counter=2)
  expect_equal(regs.r2.field.status.read(), 1)
  expect_equal(regs.r2.field.flags.read(), 0x42)
  ```
- When verifying the correct endianness, offsets and bit-to-field mapping, use `dev_util.Register_LE` / `Register_BE` plus `Bitfield_LE` / `Bitfield_BE` and define these explicitly in the test. Any mismatch between test and model will cause failures.
```python
import dev_util
from stest import expect_equal
my_device = pre_conf_object('dev', 'my_device_class')
SIM_add_configuration([my_device], None)
r1 = dev_util.Register_LE(conf.dev.bank.regs, # bank
                          0x0,                # offset in bank
                          size=4)
r2 = dev_util.Register_LE(
        dev.bank.regs, 0x4, size=4,
        bitfield = dev_util.Bitfield_LE(
             ctrl=(31,24),      # Bits 31-24
             flags=(23,5),      # Bits 23-5
             counter=(4,1),     # Bits 4-1
             status=0           # Bit 0
         )
      )
# Writing and reading the entire register r1
r1.write(0xdeadbeef)
expect_equal(r1.read(), 0xdeadbeef)

# No "just writing a field". A read-modify-write behavior is implied: reading the full register value, set the field values, then write it back.
r2.write(ctrl = 0xA, counter = 2)

# Field reads are *full register reads* that extract field values for convenience
expect_equal(r2.status, 1)
expect_equal(r2.flags, 0x42)

# Access to a single field (implicit read-modify-write accesses)
r2.flags = 0x66
r2.status = 0
```

### Responding to Memory Accesses from Models
- Use `dev_util.Memory` and `dev_util.Layout` classes for testing DMA transfers:
  ```python
  import dev_util
  from stest import expect_equal, expect_different
  mem = dev_util.Memory()
  dma_dev = pre_conf_object('dev', 'my_dev_class')
  dma_dev.phys_mem = mem.obj
  SIM_add_configuration([dma_dev], None)
  
  desc = dev_util.Layout_LE(
      mem, 0x1234,
      {'reg1': (0, 2), 'reg2': (2, 2), 'reg3': (4, 4),
       'reg4': (8, 2, dev_util.Bitfield_BE({'f1': (15, 8), 'f2': (7, 0)})) }) # {'reg-name' : (offset, size, bitfield)}
  desc.reg1 = 0xffff
  desc.reg2 = 0xabab
  desc.reg3 = 0xdeadbeef
  desc.reg4.write(0, f1=5, f2=27)
  # Fill memory
  mem.write(0xabab, tuple(i for i in xrange(256)))
  ```
- `dev_util.Memory` can track writes and raises an exception on reads from uninitialized addresses.
- You cannot read/write a single field of an uninitialized register: either write the whole register first, or do a `reg.write(default, field=val)` style write so a full value exists before field updates.


### Calling Interfaces on Devices
- Call interfaces directly:
  ```python
  # .. omit imports
  dev = pre_conf_object('dev', 'my_dev_class')
  SIM_add_configuration([dev], None)
  dev = conf.dev
  
  dev.iface.signal.signal_raise()
  dev.port.reset.iface.signal.signal_raise()
  dev.port.reset.iface.signal.signal_lower()
  dev.iface.signal.signal_lower()
  ```

### Working with Transactions
- Create and send transactions:
  ```python
  import simics
  
  dev = pre_conf_object('dev', 'my_dev_class')
  SIM_add_configuration([dev], None)
  dev = conf.dev
  SIM_load_module('extended-id-atom')
  
  txn = simics.transaction_t(size=4, write=True, value_le=0xdeadbeef, extended_id=3000)
  exc = simics.SIM_issue_transaction(dev.bank.regs, txn, 0x420)
  ```
- To verify transactions sent *from* the device (e.g. custom atoms), you can insert a small `pyobj.ConfObject` in the path that:
  - implements the `transaction` interface,
  - records fields (like `txn.extended_id`) into a `SimpleAttribute`,
  - then forwards the transaction to a `dev_util.Memory` object.
  - Tests can then assert both memory contents and the last seen atom value.
```python
# ... omit imports ...
# load the module that defines the custom atom
SIM_load_module('example_module')

# Create a simple device class that can inspect transactions and forward them
class txn_checker(pyobj.ConfObject):
    class last_extended_id(pyobj.SimpleAttribute(0, 'i')):
        '''An attribute to store the last seen extended id'''

    # The transaction interface
    class transaction(pyobj.Interface):
        def issue(self, txn, addr):
            self._up.last_extended_id.val = txn.extended_id
            return self._up.to_mem.val.iface.transaction.issue(txn, addr)

    class to_mem(pyobj.SimpleAttribute(None, 'o', simics.Sim_Attr_Optional)):
        '''Connect to the memory space'''
```

### General Test Good Practices
- Use subtests for independent features
- Factor out common test code
- Group related small tests to optimize runtime
- Ensure clarity on what is tested and reasoning behind the design
- When testing system with events, make sure the delay is within your expectation. A margin of 50% is reasonable to add since possible timing variations