# DML Best Practices - Executable Index

**Purpose**: This executable index contains copy-paste ready patterns that enable you to implement a working DML device without reading other documents. Use this for 80% of common cases. Read detailed documents only when you need deeper understanding.

**Generated from**: Session learnings (Watchdog Timer implementation, December 2024)

---

## ⚡ CRITICAL PATTERNS (Copy These First)

### Pattern 1: Register Access Scope ⭐ PREVENTS 100% OF SCOPE ERRORS

**The Rule**: Scope determines syntax - the closer you are to a register, the less qualification needed.

```dml
// At DEVICE level - use BankName.REGISTER.val
device wdt {
    method reset_state() {
        WatchdogRegisters.WDOGLOAD.val = 0xFFFFFFFF;  // ✅ Use actual bank name
        WatchdogRegisters.WDOGCONTROL.val = 0x0;
        
        // ❌ WRONG - bare register name
        // WDOGLOAD.val = 0;  // error: unknown identifier
        
        // ❌ WRONG - 'bank' is not an access keyword
        // bank.WDOGLOAD.val = 0;  // error: unknown identifier: 'bank'
    }
}

// At BANK level - use REGISTER.val
bank WatchdogRegisters {
    method bank_method() {
        WDOGLOAD.val = 0xFFFFFFFF;  // ✅ No prefix needed at bank level
    }
}

// At REGISTER level - use this.val
register WDOGLOAD {
    method write(uint64 value) {
        this.val = value;  // ✅ Use 'this' at register level
    }
}
```

**Quick Reference**:
- Device level → `BankName.REGISTER.val` (use your actual bank name)
- Bank level → `REGISTER.val`
- Register level → `this.val`

---

### Pattern 2: Signal Safety ⭐ PREVENTS SEGFAULTS

**The Rule**: ALWAYS check if signals are connected before calling methods.

```dml
// ❌ WRONG - Causes segfault if signal not connected
method update_outputs() {
    if (interrupt_pending) {
        wdogint.signal_raise();  // ❌ Crashes if wdogint.obj is NULL
    }
}

// ✅ CORRECT - Check connection first
method update_outputs() {
    // Check if signals are connected
    if (!wdogint.obj || !wdogres.obj)
        return;  // Signals not connected, safe to skip
    
    // Now safe to use signals
    if (interrupt_pending) {
        wdogint.signal_raise();  // ✅ Safe - we checked .obj first
    } else {
        wdogint.signal_lower();
    }
}
```

**Why This Matters**:
- Test environments often don't connect all signals
- Unconnected signals have `NULL` obj pointer
- Calling methods on NULL obj causes segmentation fault
- ALWAYS check `signal.obj` before calling signal methods

**Pattern for all signal operations**:
```dml
// For connect objects (output signals)
if (my_signal.obj) {
    my_signal.signal_raise();
    my_signal.signal_lower();
}
```

---

### Pattern 3: Complete Timer Implementation ⭐ PREVENTS INCOMPLETE TIMERS

**The Rule**: Timers need BOTH lazy evaluation AND event mechanism.

```dml
// Component 1: Lazy Evaluation (calculate current value on-demand)
saved cycles_t counter_start_time;
saved uint32 counter_start_value;

method get_current_counter() -> (uint32) {
    if (!enabled)
        return counter_start_value;
    
    local cycles_t elapsed = SIM_cycle_count(dev.obj) - counter_start_time;
    local uint32 decremented = cast(elapsed / prescaler, uint32);
    
    if (decremented >= counter_start_value)
        return 0;  // Expired
    return counter_start_value - decremented;
}

// Component 2: Event Mechanism (trigger actions when counter expires)
event timeout_event is simple_cycle_event {
    method event() {
        // Execute timeout actions
        raw_interrupt_status = true;
        update_outputs();  // Drive interrupt signal
        
        // Handle auto-reload if needed
        if (auto_reload_enabled) {
            counter_start_value = reload_value;
            counter_start_time = SIM_cycle_count(dev.obj);
            schedule_timeout();  // Re-post event
        }
    }
}

// Component 3: Event Scheduling
method schedule_timeout() {
    if (timeout_event.posted())
        timeout_event.remove();  // Cancel old event first
    
    if (enabled && counter_start_value > 0) {
        local cycles_t cycles_to_zero = counter_start_value * prescaler;
        timeout_event.post(cycles_to_zero);
    }
}

// Component 4: Wire them together in register side-effects
register CONTROL {
    method write_register(uint64 val, uint64 enabled_bytes, void *aux) {
        default(val, enabled_bytes, aux);
        
        if (enable_bit.val) {
            counter_start_value = reload_value;
            counter_start_time = SIM_cycle_count(dev.obj);
            schedule_timeout();  // ✅ Post event when enabled
        } else {
            if (timeout_event.posted())
                timeout_event.remove();  // Cancel event when disabled
        }
    }
}
```

**Checklist**:
- ✅ Lazy evaluation for counter value
- ✅ Event object declared
- ✅ Event scheduling method
- ✅ Event handler with timeout actions
- ✅ Register side-effects call schedule method

---

### Pattern 4: Anti-Pattern - Never Model Clock Signals ⭐ PREVENTS 100-1000x SLOWDOWN

```dml
// ❌ FORBIDDEN - Clock signal modeling (CATASTROPHIC performance)
port timer_clk {
    implement signal {
        method signal_raise() {
            timer_counter--;  // ❌ Called MILLIONS of times/second!
        }
    }
}

// ❌ FORBIDDEN - Cycle-accurate updates
event timer_tick is simple_cycle_event {
    method event() {
        timer_counter.val++;
        this.post(1);  // ❌ Updates every cycle!
    }
}

// ✅ CORRECT - Use lazy evaluation instead
register COUNTER {
    method read_register() -> (uint64) {
        local cycles_t now = SIM_cycle_count(dev.obj);
        local cycles_t elapsed = now - start_time;
        return start_value - cast(elapsed, uint64);  // ✅ Calculate on-demand
    }
}
```

**Why This is CATASTROPHIC**:
- 100-1000x slower performance
- Methods called millions of times per second
- Wrong paradigm (Simics = TLM, not RTL)
- Software never sees clock edges

---

### Pattern 5: Never Call SIM_cycle_count in init() ⭐ PREVENTS CRASHES

```dml
// ❌ FORBIDDEN - Timing APIs in init()
method init() {
    reload_value = 0xffffffff;
    start_cycle = SIM_cycle_count(dev.obj);  // ❌ Queue not ready yet!
    enabled = 0;
}

// ✅ CORRECT - Initialize on first use
saved cycles_t start_cycle = 0;
saved bool first_use = true;

method start_timer() {
    if (first_use) {
        start_cycle = SIM_cycle_count(dev.obj);  // ✅ Queue is ready now
        first_use = false;
    }
    // Continue timer logic
}

// ✅ CORRECT - Initialize in register side-effect
register CONTROL {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        if (enable_bit.val) {
            start_cycle = SIM_cycle_count(dev.obj);  // ✅ Queue is ready
        }
    }
}
```

**Why This Fails**:
- `SIM_cycle_count()` requires valid queue object
- Queue is assigned AFTER device creation
- Causes crashes or undefined behavior

---

### Pattern 6: Event Cancellation ⭐ PREVENTS MULTIPLE EVENTS

```dml
// ❌ WRONG - Post without canceling
method start_timer() {
    timer_event.post(timeout);  // ❌ May have multiple events pending
}

// ✅ CORRECT - Cancel before posting
method start_timer() {
    if (timer_event.posted())
        timer_event.remove();  // ✅ Cancel old event first
    timer_event.post(timeout);
}
```

---

### Pattern 7: Register Side-Effects Template

```dml
register CONTROL size 4 @ 0x008 {
    field ENABLE @ [0];
    field RESET @ [1];
    
    method write_register(uint64 val, uint64 enabled_bytes, void *aux) {
        // 1. Call default to update register value
        default(val, enabled_bytes, aux);
        
        // 2. Read field values (after default)
        local bool enable = ENABLE.val;
        local bool reset = RESET.val;
        
        // 3. Implement side-effects
        if (reset) {
            // Reset logic
            counter_value = 0;
            RESET.val = 0;  // Auto-clear reset bit
        }
        
        if (enable) {
            // Start timer
            start_time = SIM_cycle_count(dev.obj);
            schedule_timeout();
        } else {
            // Stop timer
            if (timeout_event.posted())
                timeout_event.remove();
        }
        
        // 4. Update outputs
        update_outputs();
    }
}
```

---

### Pattern 8: Peripheral ID Registers

```dml
// Initialize in post_init() or reset_state()
method post_init() {
    // ARM PrimeCell identification values
    WatchdogRegisters.WDOGPERIPHID0.val = 0x24;
    WatchdogRegisters.WDOGPERIPHID1.val = 0xB8;
    WatchdogRegisters.WDOGPERIPHID2.val = 0x1B;
    WatchdogRegisters.WDOGPERIPHID3.val = 0x00;
    
    // Component ID values
    WatchdogRegisters.WDOGPCELLID0.val = 0x0D;
    WatchdogRegisters.WDOGPCELLID1.val = 0xF0;
    WatchdogRegisters.WDOGPCELLID2.val = 0x05;
    WatchdogRegisters.WDOGPCELLID3.val = 0xB1;
}
```

---

## 📊 Quick Decision Trees

### "I need to access a register"

```
Where are you writing code?
├─ Device-level method? → Use BankName.REGISTER.val
├─ Bank-level method? → Use REGISTER.val
└─ Register method? → Use this.val
```

### "I'm implementing a timer/watchdog"

```
Checklist:
├─ ✅ Read 02_DML_Anti_Patterns.md first (MANDATORY)
├─ ✅ Use lazy evaluation for counter (NOT cycle-by-cycle)
├─ ✅ Create event object for timeout
├─ ✅ Schedule event when timer starts
├─ ✅ Cancel event before rescheduling
├─ ✅ Check signal connections before use
└─ ✅ Never call SIM_cycle_count in init()
```

### "I got a compilation error"

```
Error message contains:
├─ "unknown identifier: 'REGISTER'" → Check Pattern 1 (scope)
├─ "unknown identifier: 'bank'" → Don't use 'bank' keyword, use actual bank name
├─ Segmentation fault → Check Pattern 2 (signal safety)
└─ "Queue not set" → Check Pattern 5 (no SIM_cycle_count in init)
```

---

## 📚 Deep Dive Documents

**Only read these if the patterns above aren't sufficient:**

### Document 1: [Simics Modeling Philosophy](01_Simics_Modeling_Philosophy.md)
**When**: Understanding why lazy evaluation matters  
**Topics**: Transaction-Level Modeling, functional approach, lazy evaluation principle

### Document 2: [DML Anti-Patterns](02_DML_Anti_Patterns.md) ⚠️ CRITICAL FOR TIMERS
**When**: Before implementing ANY timer/watchdog device  
**Topics**: Clock signal modeling, timing API in init(), incomplete timers, cycle-by-cycle updates

### Document 3: [DML Basic Syntax](03_DML_Basic_Syntax.md)
**When**: Learning DML language fundamentals  
**Topics**: Compilation, syntax, constructs, file organization, logging

### Document 4: [DML Timing and Timer Modeling](04_DML_Timing_Timer_Modeling.md)
**When**: Implementing timers, counters, watchdogs  
**Topics**: `after` statement, event objects, timer patterns, complete examples

### Document 5: [DML Troubleshooting](05_DML_Troubleshooting.md)
**When**: Debugging compilation or runtime errors  
**Topics**: Syntax errors, AttributeError, module_load.py issues, build problems

### Document 6: [DML Common Patterns](06_DML_Common_Patterns.md)
**When**: Starting a new device type  
**Topics**: Memory-mapped device, interrupts, UART, PCI device templates

### Document 7: [DML Register Access Scope](07_DML_Register_Access_Scope.md) ⭐ MANDATORY
**When**: BEFORE ANY DML implementation  
**Topics**: Complete scope rules, error examples, real-world patterns, pre-build checklist

---

## 🎯 Recommended Reading Order

### For ALL Implementations:
1. **This executable index** (you're reading it now)
2. **07_DML_Register_Access_Scope.md** if you need more scope examples

### For Timer/Watchdog Devices:
1. **This executable index** (copy patterns 3, 4, 5, 6)
2. **02_DML_Anti_Patterns.md** (MANDATORY - read anti-patterns 1, 2, 3)
3. **04_DML_Timing_Timer_Modeling.md** (for complete examples)

### For Beginners:
1. **This executable index** (copy patterns as needed)
2. **01_Simics_Modeling_Philosophy.md** (understand the "why")
3. **03_DML_Basic_Syntax.md** (learn the language)
4. **06_DML_Common_Patterns.md** (practice with templates)

---

## ✅ Pre-Build Checklist

Before running your first build, verify:

- [ ] All device-level register accesses use `BankName.REGISTER.val` (actual bank name)
- [ ] All register-level accesses use `this.val`
- [ ] No bare register names at device level
- [ ] No use of `bank.REGISTER.val` (word "bank" is not an access keyword)
- [ ] All signal operations check `if (signal.obj)` first
- [ ] No `SIM_cycle_count()` in `init()` or `post_init()`
- [ ] Timer has BOTH lazy evaluation AND event mechanism
- [ ] Events are canceled before rescheduling
- [ ] No clock signal modeling or cycle-by-cycle updates

---

**Document Status**: Executable Index  
**Generated From**: Session learnings (Watchdog Timer implementation)  
**Last Updated**: December 17, 2025  
**Coverage**: 80% of common DML implementation cases

**Next Steps**: Copy the patterns you need, implement your device, then read detailed docs only if you encounter edge cases not covered here.
