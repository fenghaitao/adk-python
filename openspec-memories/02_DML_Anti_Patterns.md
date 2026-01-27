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

## CRITICAL Anti-Pattern 2: Calling SIM_cycle_count/SIM_time in init() or post_init()

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

## CRITICAL Anti-Pattern 3: Incomplete Timer/Counter Implementation

### The Problem

**Common Mistake:** Implementing lazy evaluation (counter calculation) but forgetting the event mechanism for timeout/expiry actions.

```dml
// ❌ INCOMPLETE - Has lazy evaluation but NO event mechanism:
register WDOGVALUE {
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

**Component 1: Device Frequency Configuration** (REQUIRED for time-based events):
```dml
// ✅ REQUIRED: Define device operating frequency
// This makes the device self-contained and independent of external clock signals
constant DEVICE_FREQ_HZ = 12.0e+6;  // 12 MHz (example - use hardware spec value)

// Optional: Make frequency configurable via attribute
attribute freq_mhz is (double_attr, init) {
    param documentation = "Timer device frequency in MHz";
    param configuration = "optional";
    method init() {
        val = 12.0;  // Default to 12 MHz
    }
}

// ✅ Helper method: Convert cycles to simulation time
method cycles_to_time(uint64 cycles) -> (double) {
    return cast(cycles, double) / DEVICE_FREQ_HZ;
}
```

**Component 2: Lazy Evaluation** (calculate current value on-demand):
```dml
register COUNTER {
    method read_register() -> (uint64) {
        if (!enabled) return saved_value;
        
        // Calculate elapsed time since start
        local double elapsed_time = SIM_time(dev.obj) - start_time;
        local uint64 elapsed_cycles = cast(elapsed_time * DEVICE_FREQ_HZ, uint64);
        local uint64 current = saved_value - (elapsed_cycles / step_value);
        return current;
    }
}
```

**Component 3: Event Mechanism** (trigger actions when counter expires):
```dml
// ✅ CORRECT: Use simple_time_event (self-contained, no external clock dependency)
event timeout_event is simple_time_event {
    method event() {
        // Execute timeout actions
        raw_int = true;             // Set interrupt flag
        update_outputs();           // Drive interrupt signal
        
        // Handle auto-reload if needed
        if (auto_reload_enabled) {
            counter = reload_value;
            start_time = SIM_time(dev.obj);
            schedule_next_timeout();  // Re-post event
        }
    }
}

// Schedule event when counter is started/reloaded
method schedule_next_timeout() {
    if (timeout_event.posted())
        timeout_event.remove();
    
    if (enabled && counter > 0) {
        // Convert timer cycles to simulation time
        local double timeout_seconds = cycles_to_time(counter * step_value);
        timeout_event.post(timeout_seconds);
    }
}
```

**Component 4: Wire Them Together**:
```dml
register CONTROL {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        
        if (enable_bit.val) {
            counter = reload_value;
            start_time = SIM_time(dev.obj);  // Use SIM_time for time-based events
            schedule_next_timeout();         // ✅ Post event when enabled
        } else {
            if (timeout_event.posted())
                timeout_event.remove();      // Cancel event when disabled
        }
    }
}
```

### Why simple_time_event Is Better Than simple_cycle_event

**❌ AVOID: `simple_cycle_event`** - Requires clock frequency to match device frequency:
```dml
// Problem: Clock frequency must match device frequency exactly
event timeout_event is simple_cycle_event {
    method event() { /* ... */ }
}

// Scheduling in cycles - assumes external clock runs at device frequency
timeout_event.post(cycles);  // FRAGILE: Only correct if clock.freq_mhz == device freq

// In test configuration, you MUST:
// 1. Create clock with EXACT device frequency: clk.freq_mhz = 12.0  # Must match!
// 2. Assign queue: dev.queue = clk
// 3. If frequencies mismatch, timing calculations are wrong
```

**✅ PREFER: `simple_time_event`** - Device frequency independent of clock frequency:
```dml
// Solution: Device defines own frequency, converts internally
constant DEVICE_FREQ_HZ = 12.0e+6;  // Device-specific frequency

event timeout_event is simple_time_event {
    method event() { /* ... */ }
}

// Scheduling in simulation time - clock can be any frequency
local double timeout = cast(cycles, double) / DEVICE_FREQ_HZ;
timeout_event.post(timeout);  // ROBUST: Works regardless of clock frequency

// In test configuration, you still need:
// 1. Create clock: clk.freq_mhz = <any value>  # Can be different from device!
// 2. Assign queue: dev.queue = clk
// 3. Device converts time using its own frequency - no mismatch possible
```

**Key Differences:**

| Aspect | `simple_cycle_event` (❌ Avoid) | `simple_time_event` (✅ Prefer) |
|--------|--------------------------------|-------------------------------|
| **Clock Setup** | Required (clock + queue) | Required (clock + queue) |
| **Frequency Coupling** | Clock freq MUST match device freq | Clock freq can be anything |
| **Robustness** | Fragile - breaks if frequencies mismatch | Robust - device converts internally |
| **Test Complexity** | Must ensure freq matching | Clock freq doesn't matter |
| **Use Case** | Only when device uses exact CPU/bus cycles | Timer/watchdog with own oscillator (95% of cases) |

**Both templates require clock/queue setup**, but the critical difference is:
- **`simple_cycle_event`**: Cycle count depends on external clock frequency → tight coupling, fragile
- **`simple_time_event`**: Device converts time using own frequency → loose coupling, robust

**When to use each:**
- **Use `simple_time_event`**: Timer/watchdog devices with their own oscillator frequency (most cases)
- **Use `simple_cycle_event`**: Only for devices explicitly using CPU/bus cycle counts (rare)
```

### Detection Checklist

- ❌ **INCOMPLETE:** Has lazy counter evaluation but no `event` object → Timer never triggers actions
- ❌ **INCOMPLETE:** Has `event` object but never calls `.post()` → Event never fires
- ❌ **INCOMPLETE:** Has `.post()` but no logic in `event()` method → No actions on timeout
- ❌ **WRONG TEMPLATE:** Uses `simple_cycle_event` without external clock dependency justification → Use `simple_time_event`
- ❌ **MISSING FREQUENCY:** Uses `simple_time_event` but no device frequency defined → Add `constant` or `attribute` for frequency
- ✅ **COMPLETE:** Has device frequency + lazy evaluation + `simple_time_event` + `.post()` scheduling + timeout actions

---

## Additional Anti-Patterns

### Anti-Pattern 4: Updating Counters Every Cycle

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

### Anti-Pattern 5: Using `after` with Stack-Allocated Data

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

### Anti-Pattern 6: Forgetting to Cancel Events

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

### Anti-Pattern 7: Mixing Time Units

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

### Anti-Pattern 8: Checkpointing Calculated Values

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
2. **NEVER** call `SIM_cycle_count()` or `SIM_time()` in `init()` or `post_init()`
3. **ALWAYS** implement both lazy evaluation AND event mechanisms for timers
4. **ALWAYS** cancel pending events before posting new ones
5. **ALWAYS** use explicit time unit conversions
6. **ALWAYS** checkpoint base values, not calculated values
7. **NEVER** use `after` with stack-allocated data
8. **ALWAYS** use lazy evaluation instead of cycle-by-cycle updates

---

**Document Status**: ✅ Complete  
**Extracted From**: DML_Best_Practices.md  
**Last Updated**: December 11, 2025
