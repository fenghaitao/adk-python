# DML Anti-Patterns: What NOT to Do

## Overview

This document lists critical anti-patterns and mistakes to avoid when writing DML device models. These patterns lead to poor performance, incorrect behavior, or compilation failures.

## CRITICAL Anti-Pattern 1: Using DML Keywords as Object References

**⚠️ CRITICAL COMPILATION ERROR - CAUSES BUILD FAILURE**

### The Problem

**NEVER use `bank`, `register`, or `field` keywords as object references in DML code.**

These are **declaration keywords** ONLY - they declare the structure, but are NOT used to reference instances.

```dml
// ❌ WRONG - Using keywords as object references:
bank regs {
    register CONTROL {
        field ENABLE @ [0] { }
        
        method write_register() {
            // ❌ ALL THESE ARE WRONG:
            local uint8 val1 = this.field.ENABLE.val;           // Error: reference to unknown object 'CONTROL.field'
            local uint8 val2 = this.register.CONTROL.val;       // Error: reference to unknown object 'CONTROL.register'
            local uint8 val3 = dev.bank.regs.val;               // Error: reference to unknown object 'device.bank'
            local uint8 val4 = this.bank.regs.val;              // Error: reference to unknown object 'CONTROL.bank'
        }
    }
}

// ❌ WRONG - Using 'bank' as reference at device level:
method device_method() {
    local uint32 load = dev.bank.regs.LOAD.val;  // ❌ Error!
}
```

### Compilation Errors You'll See

```
error: reference to unknown object 'CONTROL.field'
error: reference to unknown object 'register'
error: reference to unknown object 'device.bank'
error: reference to unknown object 'this.bank'
```

### The CORRECT Way - Direct Name References

**Rule: Reference objects by their DECLARED NAMES ONLY, never by keywords.**

```dml
// ✅ CORRECT - Direct name references:
bank regs {
    register CONTROL {
        field ENABLE @ [0] { }
        
        method write_register() {
            // ✅ CORRECT: Reference field by name directly
            local uint8 enable_val = this.ENABLE.val;  // From register scope
            
            // ✅ CORRECT: Reference register from bank scope
            local uint8 ctrl_val = regs.CONTROL.val; // `regs` is the bank name here, not a keyword
        }
    }
    
    register LOAD { }

    // ✅ CORRECT - Reference from one register to another:
    register VALUE {
        method read_register() -> (uint64) {
            // Reference sibling register by name
            return regs.LOAD.val; // `regs` is the bank name here, not a keyword
        }
    }
}

// ✅ CORRECT - Device-level reference to bank/register:
method device_method() {
    // Reference bank by its NAME, not by keyword 'bank'
    local uint32 load = regs.LOAD.val; // `regs` is the bank name defined as above, not a keyword
}
```

### Understanding DML Scope Rules

**Read `openspec-memories/07_DML_Register_Access_Scope.md` for complete details.**

| Context | Access Pattern | Example |
|---------|----------------|---------|
| **Inside field** | `this.<field_name>` | `this.ENABLE.val` |
| **Inside register** | `this.<field_name>` | `this.ENABLE.val` (field access) |
| **Inside register** | `<bank_name>.<register_name>` | `regs.LOAD.val` (sibling register) |
| **Inside bank** | `this.<register_name>` | `this.CONTROL.val` |
| **Device level** | `<bank_name>.<register_name>` | `regs.LOAD.val` |

### Key Rules

1. ✅ **DO**: Use declared names (`regs`, `CONTROL`, `ENABLE`)
2. ❌ **DON'T**: Use keywords (`bank`, `register`, `field`) as references
3. ❌ **DON'T**: Use `dev.bank.<anything>` or `this.bank.<anything>`
4. ❌ **DON'T**: Use `this.register.<anything>` or `this.field.<anything>`
5. ✅ **DO**: Read `07_DML_Register_Access_Scope.md` for all scope patterns

### Why This Matters

- **`bank`**, **`register`**, **`field`** are **declaration keywords**, not namespace identifiers
- DML compiler doesn't create a `.bank` or `.register` or `.field` namespace
- Using these keywords causes immediate compilation failure
- This is a fundamental DML syntax rule, not a style preference

---

## CRITICAL Anti-Pattern 2: Clock Signal Modeling & Cycle-Accurate Updates

**⚠️ MOST COMMON MISTAKE - NEVER DO THIS**

### The Problem

**NEVER model clock signals or update counters every cycle in Simics DML.**

```dml
// ❌ FORBIDDEN - Clock signal modeling:
port timer_clk {
    implement signal {
        method signal_raise() {
            timer_counter--;  // ❌ CATASTROPHIC! Called MILLIONS of times/second
        }
    }
}

// ❌ FORBIDDEN - Cycle-accurate updates:
event timer_tick is simple_cycle_event {
    method event() {
        timer_counter.val++;
        this.post(1);  // ❌ WRONG! Updates every cycle
    }
}
```

### Why This is CATASTROPHIC

1. **Performance**: 100-1000x slower - methods called MILLIONS of times per second
2. **Wrong Paradigm**: Simics = Transaction-Level Modeling (TLM), NOT Register-Transfer Level (RTL)
3. **Software Visibility**: Software NEVER sees clock edges - only register values
4. **Breaks Lazy Evaluation**: Forces expensive cycle-by-cycle updates instead of on-demand calculation

### The CORRECT Alternative - Lazy Evaluation Pattern

```dml
saved cycles_t start_time;
saved uint64 start_value;

register COUNTER {
    method read_register() -> (uint64) {
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t elapsed = now - start_time;
        return start_value - cast(elapsed, uint64);  // Calculate on-demand, not every cycle
    }
}
```

### Detection Rules

If you see ANY of these patterns, it's WRONG:
- `port` implementing `signal` interface for clock/timing purposes
- Timer/timing counter decrements or increments inside `signal_raise()` or `signal_lower()` methods
- `event` posting to itself every cycle (e.g., `this.post(1)`)
- Any cycle-by-cycle timer state updates in event handlers
- Timer register value updates triggered by clock edges

---

## CRITICAL Anti-Pattern 3: Calling Interface Methods on Connect Objects in init() or post_init()

### The Problem

**NEVER call interface methods on connect objects in device initialization methods.**

```dml
// ❌ FORBIDDEN - Calling interface methods in init():
connect interrupt_out {
    interface signal;
}

connect reset_out {
    interface signal;
}

method init() {
    load_value = 0xffffffff;
    control_value = 0;
    
    // ❌ WRONG! Causes segmentation fault
    interrupt_out.signal.signal_lower();
    reset_out.signal.signal_lower();
}

method post_init() {
    // ❌ WRONG! Connections not established yet
    interrupt_out.signal.signal_lower();
}
```

### Runtime Error

```
Segmentation fault (SIGSEGV) in main thread
#0  in _DML_M_init
The simulation state has been corrupted. Simulation cannot continue.
```

### Why This CAUSES SEGFAULT

1. **Connection Timing**: Connect objects are wired up AFTER `init()` and `post_init()` complete
2. **Null Reference**: Interface methods are called on uninitialized/null connect objects
3. **Default State**: All Simics signals are created in the LOWERED state by default - no initialization needed
4. **Crash Risk**: Calling interface methods before connections are established causes immediate segmentation fault

### The CORRECT Alternative - No Manual Signal Initialization Needed

```dml
// ✅ CORRECT - Don't initialize signals in init()
connect interrupt_out {
    interface signal;
}

connect reset_out {
    interface signal;
}

method init() {
    load_value = 0xffffffff;
    control_value = 0;
    // ✅ Do NOT call signal_lower() - signals default to low
}

// ✅ CORRECT - Drive signals during runtime, not init
register CONTROL {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        
        if (enable_bit.val) {
            interrupt_out.signal.signal_raise();  // ✅ OK at runtime
        } else {
            interrupt_out.signal.signal_lower();  // ✅ OK at runtime
        }
    }
}
```

### Key Facts About Simics Signals

1. **Default State**: All signals are created in the LOWERED state automatically
2. **No Init Needed**: Never need to call `signal_lower()` in `init()` or `post_init()`
3. **Runtime Only**: Only call interface methods during normal device operation (register access, events, etc.)
4. **Connection Order**: Connections are established by test configuration AFTER device initialization

### Detection Rules

If you see ANY of these patterns in init()/post_init(), it's WRONG and will SEGFAULT:
- Calling `.signal.signal_raise()` in `method init()` or `method post_init()`
- Calling `.signal.signal_lower()` in `method init()` or `method post_init()`
- Calling ANY interface method on ANY connect object in initialization methods
- Trying to "initialize" signal states in `init()` or `post_init()`

**Correct Pattern**: Only call interface methods during runtime (register access, event handlers, etc.), NEVER in init().

---

## CRITICAL Anti-Pattern 4: Calling SIM_cycle_count/SIM_time in init() or post_init()

### The Problem

**NEVER call SIM_cycle_count() or SIM_time() in device initialization methods.**

```dml
// ❌ FORBIDDEN - Timing APIs in init():
method init() {
    reload_value = 0xffffffff;
    start_cycle = SIM_cycle_count(dev.obj);  // ❌ WRONG! Queue not ready yet
    enabled = 0;
}

// ❌ FORBIDDEN - Timing APIs in post_init():
method post_init() {
    start_time = SIM_time(dev.obj);  // ❌ WRONG! Queue dependency not satisfied
}
```

### Runtime Error You'll See

```
*** SIM_cycle_count():/disk2/mp/builds/nightly-base.785.17418104131.1/core/src/core/common/event.c:892 
- the object 'dev' has no valid queue attribute but 'SIM_cycle_count()' requires the object to have one. 
If this assertion occurs while loading a configuration, you are probably calling 'SIM_cycle_count()' 
before the finalize phase, which is usually not allowed.
```

### Why This FAILS

1. **Queue Dependency**: `SIM_cycle_count()` and `SIM_time()` require a valid queue object
2. **Initialization Order**: Queue is assigned AFTER device object creation, not during `init()`
3. **Finalize Phase**: These APIs can only be called after the configuration finalize phase
4. **Runtime Error**: Causes assertion failure when queue is not yet configured

### The CORRECT Alternative - Initialize on First Use

```dml
saved cycles_t start_cycle = 0;  // Default value
saved bool first_use = true;

method start_timer() {
    if (first_use) {
        start_cycle = SIM_cycle_count(dev.obj);  // ✅ CORRECT! Called at runtime
        first_use = false;
    }
    // Continue timer logic
}

register CONTROL {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        if (enable_bit.val) {
            start_cycle = SIM_cycle_count(dev.obj);  // ✅ CORRECT! Queue is ready
        }
    }
}
```

### Detection Rules

If you see ANY of these patterns in init()/post_init(), it's WRONG:
- `SIM_cycle_count(dev.obj)` in `method init()` or `method post_init()`
- `SIM_time(dev.obj)` in `method init()` or `method post_init()`
- Any timing API that depends on queue in initialization methods

**Correct Pattern**: Initialize timing state on first register access or when timer is enabled, NOT in init().

---

## CRITICAL Anti-Pattern 5: Incomplete Timer/Counter Implementation

### The Problem

**Common Mistake:** Implementing lazy evaluation (counter calculation) but forgetting the event mechanism for timeout/expiry actions.

```dml
// ❌ INCOMPLETE - Has lazy evaluation but NO event mechanism:
register VALUE_REG {
    method read_register() -> (uint64) {
        // ✅ Good: Lazy evaluation calculates current counter value
        local cycles_t elapsed = SIM_cycle_count(dev.obj) - start_time;
        return initial_value - cast(elapsed, uint32);
    }
}

// ❌ PROBLEM: No event to trigger interrupt/reset when counter reaches zero!
// The counter decrements on reads, but nothing HAPPENS when it expires.
```

### Why Both Components Are Required

1. **Lazy evaluation** = Efficient calculation of current counter value (avoids cycle-by-cycle updates)
2. **Event mechanism** = Triggers interrupts/resets/actions when counter expires (functional behavior)

**Without events:** The counter decrements correctly but nothing happens when it reaches zero - no interrupt, no reset, no functional behavior!

### The CORRECT Pattern - Complete Timer Implementation

**Component 1: Lazy Evaluation** (calculate current value on-demand):
```dml
register COUNTER {
    method read_register() -> (uint64) {
        if (!enabled) return saved_value;
        local cycles_t elapsed = SIM_cycle_count(dev.obj) - start_time;
        local uint64 current = saved_value - (elapsed / step_value);
        return current;
    }
}
```

**Component 2: Event Mechanism** (trigger actions when counter expires):
```dml
// ✅ REQUIRED: Event to handle expiry/timeout
event timeout_event is simple_cycle_event {
    method event() {
        // Execute timeout actions
        raw_int = true;             // Set interrupt flag
        update_outputs();           // Drive interrupt signal
        
        // Handle auto-reload if needed
        if (auto_reload_enabled) {
            counter = reload_value;
            start_time = SIM_cycle_count(dev.obj);
            schedule_next_timeout();  // Re-post event
        }
    }
}

// Schedule event when counter is started/reloaded
method schedule_next_timeout() {
    if (timeout_event.posted())
        timeout_event.remove();
    
    if (enabled && counter > 0) {
        local cycles_t cycles_to_zero = counter * step_value;
        timeout_event.post(cycles_to_zero);
    }
}
```

**Component 3: Wire Them Together**:
```dml
register CONTROL {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        
        if (enable_bit.val) {
            counter = reload_value;
            start_time = SIM_cycle_count(dev.obj);
            schedule_next_timeout();  // ✅ Post event when enabled
        } else {
            if (timeout_event.posted())
                timeout_event.remove();  // Cancel event when disabled
        }
    }
}
```

### Detection Checklist

- ❌ **INCOMPLETE:** Has lazy counter evaluation but no `event` object → Timer never triggers actions
- ❌ **INCOMPLETE:** Has `event` object but never calls `.post()` → Event never fires
- ❌ **INCOMPLETE:** Has `.post()` but no logic in `event()` method → No actions on timeout
- ✅ **COMPLETE:** Has lazy evaluation + event object + `.post()` scheduling + timeout actions

---

## CRITICAL Anti-Pattern 6: Incorrect cast() Syntax

### The Problem

**CRITICAL MISTAKE: cast() arguments in wrong order**

```dml
// ❌ WRONG - Type first, value second (common mistake):
register LOAD_REG {
    method write_register(uint64 val, uint64 enabled_bytes, void *aux) {
        default(val, enabled_bytes, aux);
        last_counter_value = cast(uint32, val);  // ❌ WRONG! Causes "unknown identifier" error
    }
}

register VALUE_REG {
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        return cast(uint64, last_counter_value);  // ❌ WRONG! Causes "unknown identifier" error
    }
}
```

### Compilation Error

```
error: unknown identifier: 'uint32'
error: unknown identifier: 'uint64'
error: missing return statement in method with output argument
```

### Why This FAILS

The DML `cast()` function expects: **cast(value, type)** - value FIRST, type SECOND

The error message "unknown identifier: 'uint32'" occurs because DML interprets the type as a variable name when it's in the first position.

### The CORRECT Syntax

```dml
// ✅ CORRECT - Value first, type second:
register LOAD_REG {
    method write_register(uint64 val, uint64 enabled_bytes, void *aux) {
        default(val, enabled_bytes, aux);
        last_counter_value = cast(val, uint32);  // ✅ CORRECT! Value first, type second
    }
}

register VALUE_REG {
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        return cast(last_counter_value, uint64);  // ✅ CORRECT! Value first, type second
    }
}
```

### DML cast() Signature

```dml
// Correct syntax:
cast(expression, target_type)
//   ^^^^^^^^^^  ^^^^^^^^^^^
//   VALUE       TYPE
//   (first)     (second)

// Common examples:
local uint32 small = cast(large_value, uint32);
local uint64 big = cast(small_value, uint64);
local cycles_t cycles = cast(count, cycles_t);
```

### Detection Rules

- ❌ **WRONG:** `cast(uint32, value)` - Type first
- ❌ **WRONG:** `cast(uint64, value)` - Type first
- ❌ **WRONG:** `cast(int, value)` - Type first
- ✅ **CORRECT:** `cast(value, uint32)` - Value first
- ✅ **CORRECT:** `cast(value, uint64)` - Value first
- ✅ **CORRECT:** `cast(value, int)` - Value first

### Best Practice: When Unsure About DML Library Methods

**If you don't know the correct syntax for a DML library method:**

1. **Use MCP RAG tool** to search for examples:
   ```
   perform_rag_query("DML cast function syntax example")
   perform_rag_query("how to use cast in DML")
   perform_rag_query("DML type conversion")
   ```

2. **Search in existing DML code** for working examples
3. **Check DML documentation** for the correct function signature

**Never guess the syntax** - incorrect DML library method calls cause cryptic compilation errors that are hard to debug.

---

## Additional Anti-Patterns

### Anti-Pattern 6: Using `this.obj` Instead of `dev.obj` with Timing APIs

```dml
// ❌ DON'T: Use this.obj with SIM_cycle_count() or SIM_time()
register COUNTER {
    method read_register() -> (uint64) {
        local cycles_t now = SIM_cycle_count(this.obj);  // ❌ WRONG! `this` refer to the register, not device
        local cycles_t elapsed = now - start_time;
        return start_value - cast(elapsed, uint64);
    }
}

bank regs {
    method some_method() {
        local double time = SIM_time(this.obj);  // ❌ WRONG! this refers to the bank, not device
    }
}

// ✅ DO: Always use dev.obj for timing APIs
register COUNTER {
    method read_register() -> (uint64) {
        local cycles_t now = SIM_cycle_count(dev.obj);  // ✅ CORRECT! Always device context
        local cycles_t elapsed = now - start_time;
        return start_value - cast(elapsed, uint64);
    }
}

bank regs {
    method some_method() {
        local double time = SIM_time(dev.obj);  // ✅ CORRECT! Device context
    }
}
```

**Why this matters:**
- `this` is a dynamic pointer - could refer to device, bank, register, or field depending on context
- `SIM_cycle_count()` and `SIM_time()` expect the **device object**, not a register/bank/field object
- Using `this.obj` inside a register/bank/field method passes the wrong object type
- `dev.obj` always refers to the device object, ensuring correct context
- Most timing operations need device-level queue context, not register/field context

**Rule:** Always use `dev.obj` with `SIM_cycle_count()`, `SIM_time()`, and other Simics timing APIs.

### Anti-Pattern 7: Calling Timing APIs Without Required Parameters

**⚠️ CRITICAL COMPILATION ERROR - CAUSES BUILD FAILURE**

**NEVER call Simics timing APIs without required parameters.**

Many Simics timing APIs require a device object parameter - they CANNOT be called with empty parentheses.

```dml
// ❌ DON'T: Call timing APIs without parameters
register COUNTER {
    method read_register() -> (uint64) {
        local cycles_t now = SIM_cycle_count();     // ❌ WRONG! Missing required parameter
        local double time = SIM_time();             // ❌ WRONG! Missing required parameter
        return cast(now, uint64);
    }
}

method device_method() {
    local cycles_t cycles = SIM_cycle_count();      // ❌ WRONG! Missing dev.obj parameter
    local double current_time = SIM_time();         // ❌ WRONG! Missing dev.obj parameter
}

// ✅ DO: Always provide dev.obj as the parameter
register COUNTER {
    method read_register() -> (uint64) {
        local cycles_t now = SIM_cycle_count(dev.obj);   // ✅ CORRECT! Device object provided
        local double time = SIM_time(dev.obj);           // ✅ CORRECT! Device object provided
        return cast(now, uint64);
    }
}

method device_method() {
    local cycles_t cycles = SIM_cycle_count(dev.obj);    // ✅ CORRECT!
    local double current_time = SIM_time(dev.obj);       // ✅ CORRECT!
}
```

### Compilation Errors You'll See

```
error: too few arguments to function 'SIM_cycle_count'
error: too few arguments to function 'SIM_time'
error: expected 1 argument, got 0
```

### Common Timing APIs That Require Parameters

**All these APIs require `dev.obj` as parameter:**
- `SIM_cycle_count(dev.obj)` - Get current cycle count
- `SIM_time(dev.obj)` - Get current simulation time
- `SIM_stacked_post(dev.obj, callback, data)` - Post event to queue
- `SIM_event_find_next_cycle(dev.obj, callback)` - Find next scheduled event

### Why This Matters

- **Queue context**: Timing APIs need to know which device's event queue to use
- **Not global functions**: Unlike some languages, these APIs are not global - they operate on specific device instances
- **Device object required**: The `dev.obj` parameter provides the Simics object handle for the device
- **Runtime state**: The device object carries runtime state needed for timing operations

### Common Mistake Pattern

Agents sometimes assume timing APIs are global functions like in other simulation frameworks:

```dml
// ❌ WRONG - Treating as global function (common in other frameworks):
local cycles_t now = SIM_cycle_count();     // Missing device context
local double time = SIM_time();             // Missing device context

// ✅ CORRECT - Simics requires device context:
local cycles_t now = SIM_cycle_count(dev.obj);   // Device context provided
local double time = SIM_time(dev.obj);           // Device context provided
```

**Rule:** All Simics timing and event APIs require `dev.obj` as the first parameter. Never call them with empty parentheses.

### Anti-Pattern 8: Adding Prefixes/Suffixes to Register and Field Names

```dml
// DML declarations:
bank regs {
    register CONTROL {
        field ENABLE @ [0] { }
    }
    register STATUS { }
}

// ❌ DON'T: Add prefixes or suffixes to declared names
method device_method() {
    // ❌ WRONG - Adding "_r" suffix to register name:
    local uint32 ctrl = regs.CONTROL_r.val;     // Error: reference to unknown object 'regs.CONTROL_r'
    local uint32 stat = regs.STATUS_r.val;      // Error: reference to unknown object 'regs.STATUS_r'
    
    // ❌ WRONG - Adding "field_" prefix to field name:
    local uint8 en = regs.CONTROL.field_ENABLE.val;  // Error: reference to unknown object 'CONTROL.field_ENABLE'
    
    // ❌ WRONG - Adding "reg_" prefix to register name:
    local uint32 ctrl2 = regs.reg_CONTROL.val;  // Error: reference to unknown object 'regs.reg_CONTROL'
}

// ✅ DO: Use EXACT declared names without modifications
method device_method() {
    // ✅ CORRECT - Use exact name as declared:
    local uint32 ctrl = regs.CONTROL.val;       // ✅ Matches declaration
    local uint32 stat = regs.STATUS.val;        // ✅ Matches declaration
    
    // ✅ CORRECT - Use exact field name:
    local uint8 en = regs.CONTROL.ENABLE.val;   // ✅ Matches declaration
}
```

### Compilation Errors You'll See

```
error: reference to unknown object 'regs.CONTROL_r'
error: reference to unknown object 'CONTROL.field_ENABLE'
error: reference to unknown object 'regs.reg_CONTROL'
```

**Why this matters:**
- DML compiler looks for **EXACT** names as declared in `bank`, `register`, and `field` statements
- Adding any prefix (`field_`, `reg_`, `bank_`) or suffix (`_r`, `_f`) creates a non-existent identifier
- These are not namespaces or type indicators - use the declared name verbatim
- **Read `openspec-memories/07_DML_Register_Access_Scope.md` for correct scope patterns**

**Rule:** Use register and field names EXACTLY as declared, with no prefixes or suffixes.

### Anti-Pattern 9: Using Incorrect Type Names

```dml
// ❌ DON'T: Use non-existent DML type names
method calculate_time() {
    local real64 time_value = 1.5;      // ❌ WRONG! 'real64' doesn't exist in DML
    local float64 result = time_value * 2.0;  // ❌ WRONG! 'float64' doesn't exist
    local boolean flag = true;          // ❌ WRONG! Use 'bool', not 'boolean'
    local string name = "device";       // ❌ WRONG! DML has no 'string' type
}

// ✅ DO: Use correct DML type names
method calculate_time() {
    local double time_value = 1.5;      // ✅ CORRECT! Use 'double' for floating-point
    local double result = time_value * 2.0;  // ✅ CORRECT!
    local bool flag = true;             // ✅ CORRECT! Use 'bool'
    local char *name = "device";        // ✅ CORRECT! Use 'char *' for strings
}
```

### Compilation Error You'll See

```
error: unknown type: 'real64'
error: unknown type: 'float64'
error: unknown type: 'boolean'
error: unknown type: 'string'
```

### Valid DML 1.4 Type Names

**Integer types:**
- `int`, `int8`, `int16`, `int32`, `int64` (signed integers)
- `uint8`, `uint16`, `uint32`, `uint64` (unsigned integers)

**Floating-point types:**
- `float` (32-bit floating-point)
- `double` (64-bit floating-point)

**Other types:**
- `bool` (boolean, NOT `boolean`)
- `char *` (C-style string, NOT `string`)
- `void` (no return value)
- `cycles_t` (Simics cycle count type)

**Common mistakes from other languages:**
- ❌ `real64` (Python/NumPy) → ✅ Use `double`
- ❌ `float64` (Go/NumPy) → ✅ Use `double`
- ❌ `boolean` (Java) → ✅ Use `bool`
- ❌ `string` (C++/Python/Java) → ✅ Use `char *`
- ❌ `long` (C/Java) → ✅ Use `int64` or `uint64`
- ❌ `short` (C/Java) → ✅ Use `int16` or `uint16`

**Rule:** Only use DML 1.4 type names. When unsure, check DML documentation or use MCP RAG tool.

### Anti-Pattern 10: Using Non-Boolean Expressions in Conditional Statements

DML requires conditional expressions in `if()`, `while()`, and `for()` to be **strictly boolean** (`bool` type). Unlike C/Python where integers can be used directly, DML does NOT allow implicit integer-to-boolean conversion.

```dml
// ❌ DON'T: Use integer/uint32 directly in conditionals
saved uint32 is_timer_active;
saved uint64 counter;
saved uint32 retry_count;

method check_timer() {
    if (is_timer_active) {              // ❌ ERROR: non-boolean condition
        // ...
    }
    
    while (counter) {                   // ❌ ERROR: non-boolean condition
        counter--;
    }
    
    for (local uint32 i = 0; i < 10; i++) {
        if (!retry_count) {             // ❌ ERROR: non-boolean condition
            break;
        }
    }
}

// ✅ DO: Use explicit comparison to create bool expression
method check_timer() {
    if (is_timer_active != 0) {         // ✅ CORRECT: Explicit comparison
        // ...
    }
    
    while (counter > 0) {               // ✅ CORRECT: Explicit comparison
        counter--;
    }
    
    for (local uint32 i = 0; i < 10; i++) {
        if (retry_count == 0) {         // ✅ CORRECT: Explicit comparison
            break;
        }
    }
}
```

### Compilation Error You'll See

```
error: non-boolean condition: 'is_timer_active' of type 'uint32'
error: non-boolean condition: 'counter' of type 'uint64'
error: non-boolean condition: 'retry_count' of type 'uint32'
```

### Correct Patterns

```dml
// if() statements
if (value != 0) { ... }         // ✅ CORRECT: Checking non-zero
if (value == 0) { ... }         // ✅ CORRECT: Checking zero

// while() loops
while (counter > 0) { ... }     // ✅ CORRECT: Explicit comparison
while (index < max) { ... }     // ✅ CORRECT: Explicit comparison

// for() loops - condition must be bool
for (local uint32 i = 0; i < 10; i++) { ... }  // ✅ CORRECT: i < 10 is bool

// For pointers (NULL checking)
if (ptr != NULL) { ... }        // ✅ CORRECT
if (ptr == NULL) { ... }        // ✅ CORRECT

// For actual booleans - can use directly
saved bool enabled;
if (enabled) { ... }            // ✅ CORRECT (enabled is bool type)
if (!enabled) { ... }           // ✅ CORRECT
while (enabled) { ... }         // ✅ CORRECT
```

**Rule:** In DML, `if()`, `while()`, and `for()` conditions ONLY accept `bool` type. Always use explicit comparisons (`== 0`, `!= 0`, `< N`, `> 0`, etc.) for integer types.

### Anti-Pattern 10: Updating Counters Every Cycle

```dml
// ❌ DON'T: Update counters every cycle
event cycle_event is simple_cycle_event {
    method event() {
        counter.val++;
        this.post(1);  // Posts every cycle - very expensive!
    }
}

// ✅ DO: Use lazy evaluation
register counter {
    saved cycles_t counter_base_time;
    saved uint64 counter_base_value;
    
    method get() -> (uint64) {
        local cycles_t now = SIM_cycle_count(dev.obj);
        return counter_base_value + (now - counter_base_time);
    }
}
```

### Anti-Pattern 11: Using `after` with Stack-Allocated Data

```dml
// ❌ DON'T: Use after with stack-allocated data
method dangerous_after() {
    local int x = 42;
    after 1.0 s: use_value(&x);  // ❌ x is stack-allocated, causes security issues
}

// ✅ DO: Use saved variables or pass by value
saved int persistent_value;

method safe_after() {
    persistent_value = 42;
    after 1.0 s: use_saved_value();  // ✅ Uses saved variable
}
```

### Anti-Pattern 12: Forgetting to Cancel Events

```dml
// ❌ DON'T: Post events without canceling previous ones
method start_timer() {
    timer_event.post(timeout);  // ❌ May have multiple events pending
}

// ✅ DO: Cancel pending events before posting new ones
method start_timer() {
    if (timer_event.posted())
        timer_event.remove();  // ✅ Cancel old event first
    timer_event.post(timeout);
}
```

### Anti-Pattern 13: Mixing Time Units

```dml
// ❌ DON'T: Mix time units without explicit conversion
local cycles_t cycles = 1000;
local double seconds = 1.0;
local double result = cycles + seconds;  // ❌ Mixing incompatible units

// ✅ DO: Use explicit conversion
method cycles_to_seconds(cycles_t cycles) -> (double) {
    return cast(cycles, double) / (clock_freq_mhz * 1e6);
}

local double result = cycles_to_seconds(cycles) + seconds;  // ✅ Proper conversion
```

### Anti-Pattern 14: Checkpointing Calculated Values

```dml
// ❌ DON'T: Checkpoint calculated values
register counter {
    param configuration = "optional";  // ❌ Wrong for calculated registers
    
    method get() -> (uint64) {
        // Calculate from other values
    }
}

// ✅ DO: Checkpoint base values, mark calculated registers as "none"
saved cycles_t counter_start_time;
saved uint64 counter_start_value;

register counter {
    param configuration = "none";  // ✅ Don't checkpoint calculated value
    
    method get() -> (uint64) {
        // Calculate from saved base values
        local cycles_t now = SIM_cycle_count(dev.obj);
        return counter_start_value + (now - counter_start_time);
    }
}
```

---

## Summary: Key Rules to Remember

1. **NEVER** use `bank`, `register`, or `field` keywords as object references - use declared names only
2. **ALWAYS** read `07_DML_Register_Access_Scope.md` to understand correct scope patterns
3. **NEVER** use `dev.bank.*` or `this.bank.*` or `this.register.*` or `this.field.*` syntax
4. **NEVER** model clock signals or update counters every cycle
5. **NEVER** call interface methods on connect objects in `init()` or `post_init()` - causes SEGFAULT
6. **REMEMBER** all Simics signals default to LOWERED state - no manual initialization needed
7. **NEVER** call `SIM_cycle_count()` or `SIM_time()` in `init()` or `post_init()`
8. **ALWAYS** implement both lazy evaluation AND event mechanisms for timers
9. **ALWAYS** use correct `cast()` syntax: `cast(value, type)` - value FIRST, type SECOND
10. **ALWAYS** use MCP RAG tool when unsure about DML library method syntax
11. **ALWAYS** use `dev.obj` with timing APIs (`SIM_cycle_count`, `SIM_time`), NEVER `this.obj`
12. **NEVER** add prefixes/suffixes to register/field names - use EXACT declared names
13. **ALWAYS** use correct DML type names (double, not real64; bool, not boolean; char*, not string)
14. **ALWAYS** use explicit comparisons in `if()`, `while()`, `for()` conditions - DML requires bool type, NOT integers (use `if (var != 0)`, `while (count > 0)`, not `if (var)`, `while (count)`)
15. **ALWAYS** cancel pending events before posting new ones
16. **ALWAYS** use explicit time unit conversions
17. **ALWAYS** checkpoint base values, not calculated values
18. **NEVER** use `after` with stack-allocated data
19. **ALWAYS** use lazy evaluation instead of cycle-by-cycle updates

---

**Document Status**: ✅ Complete  
**Extracted From**: DML_Best_Practices.md  
**Last Updated**: December 27, 2025
