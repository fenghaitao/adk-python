# DML Anti-Patterns: What NOT to Do

## Overview

This document lists critical anti-patterns and mistakes to avoid when writing DML device models. These patterns lead to poor performance, incorrect behavior, or compilation failures.

## CRITICAL Anti-Pattern 1: Clock Signal Modeling & Cycle-Accurate Updates

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

## CRITICAL Anti-Pattern 2: Calling Interface Methods on Connect Objects in init() or post_init()

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

## CRITICAL Anti-Pattern 3: Calling SIM_cycle_count/SIM_time in init() or post_init()

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

### Why This FAILS

1. **Queue Dependency**: `SIM_cycle_count()` and `SIM_time()` require a valid queue object
2. **Initialization Order**: Queue is assigned AFTER device object creation, not during `init()`
3. **Runtime Error**: Causes crashes or undefined behavior when queue is not yet configured

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

## CRITICAL Anti-Pattern 4: Incomplete Timer/Counter Implementation

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

## CRITICAL Anti-Pattern 5: Incorrect cast() Syntax

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

### Anti-Pattern 6: Updating Counters Every Cycle

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

### Anti-Pattern 7: Using `after` with Stack-Allocated Data

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

### Anti-Pattern 8: Forgetting to Cancel Events

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

### Anti-Pattern 9: Mixing Time Units

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

### Anti-Pattern 10: Checkpointing Calculated Values

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

1. **NEVER** model clock signals or update counters every cycle
2. **NEVER** call interface methods on connect objects in `init()` or `post_init()` - causes SEGFAULT
3. **REMEMBER** all Simics signals default to LOWERED state - no manual initialization needed
4. **NEVER** call `SIM_cycle_count()` or `SIM_time()` in `init()` or `post_init()`
5. **ALWAYS** implement both lazy evaluation AND event mechanisms for timers
6. **ALWAYS** use correct `cast()` syntax: `cast(value, type)` - value FIRST, type SECOND
7. **ALWAYS** use MCP RAG tool when unsure about DML library method syntax
8. **ALWAYS** cancel pending events before posting new ones
9. **ALWAYS** use explicit time unit conversions
10. **ALWAYS** checkpoint base values, not calculated values
11. **NEVER** use `after` with stack-allocated data
12. **ALWAYS** use lazy evaluation instead of cycle-by-cycle updates

---

**Document Status**: ✅ Complete  
**Extracted From**: DML_Best_Practices.md  
**Last Updated**: December 25, 2025
