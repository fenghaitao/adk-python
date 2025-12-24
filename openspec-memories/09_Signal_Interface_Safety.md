# Signal Interface Safety Patterns

## Overview
Signal interfaces in DML devices must handle the case where signals are not connected. This is common in test configurations where not all signals are needed.

## The Problem

```dml
// ❌ ANTI-PATTERN: No NULL check
connect wdogint {
    interface signal;
    method signal_raise() {
        this.signal.signal_raise();  // Segfault if not connected!
    }
}
```

**Symptom**: Segmentation fault in test runs

**Why This Happens**: In test configurations, signal interfaces may not be connected to anything. When you call `this.signal.signal_raise()` on an unconnected signal, it attempts to dereference a NULL pointer, causing a segmentation fault.

## The Solution

```dml
// ✅ CORRECT: NULL check before signal operations
connect wdogint {
    interface signal;
    
    method signal_raise() {
        if (this.obj != NULL) {
            this.signal.signal_raise();
        }
    }
    
    method signal_lower() {
        if (this.obj != NULL) {
            this.signal.signal_lower();
        }
    }
}
```

**Key Pattern**: Always check `if (this.obj != NULL)` before calling any signal interface methods.

## When to Apply

Apply NULL checks to:
- **ALL signal interface implementations**
- Interrupt signals (wdogint, uart_int, etc.)
- Reset signals (wdogreset, sys_reset, etc.)
- DMA request signals
- Any `connect` object with `interface signal`

## Complete Example: Watchdog Timer

```dml
// Interrupt signal
connect wdogint {
    interface signal;
    
    method signal_raise() {
        if (this.obj != NULL) {
            this.signal.signal_raise();
        }
    }
    
    method signal_lower() {
        if (this.obj != NULL) {
            this.signal.signal_lower();
        }
    }
}

// Reset signal
connect wdogreset {
    interface signal;
    
    method signal_raise() {
        if (this.obj != NULL) {
            this.signal.signal_raise();
        }
    }
    
    method signal_lower() {
        if (this.obj != NULL) {
            this.signal.signal_lower();
        }
    }
}
```

## Test Configuration Context

In tests, signals may be left unconnected:

```python
# Device created without connecting signals
dev = conf.sim.create_object("wdt", "dev", [])
# wdogint signal is NULL - NULL checks prevent crashes
```

This is intentional - not all tests need all signals connected. Your DML code must handle this gracefully.

## Common Mistakes

### Mistake 1: Checking the wrong object
```dml
// ❌ WRONG: Checking signal instead of obj
if (this.signal != NULL) {
    this.signal.signal_raise();
}
```

### Mistake 2: Only checking one method
```dml
// ❌ INCOMPLETE: Only signal_raise has NULL check
method signal_raise() {
    if (this.obj != NULL) {
        this.signal.signal_raise();
    }
}

method signal_lower() {
    this.signal.signal_lower();  // Missing NULL check!
}
```

### Mistake 3: No NULL check at all
```dml
// ❌ DANGEROUS: No NULL checks
method signal_raise() {
    this.signal.signal_raise();  // Segfault if not connected!
}
```

## Debugging Segmentation Faults

If you encounter a segmentation fault in signal operations:

1. **Check the stack trace**: Look for signal interface method names
2. **Verify NULL checks**: Ensure ALL signal methods have `if (this.obj != NULL)`
3. **Test with unconnected signals**: Create a test that doesn't connect signals to verify safety

## Performance Impact

NULL checks have negligible performance impact:
- Single pointer comparison before signal operation
- Only executed when signal operations occur (not in hot loops)
- Prevents crashes, which is far more important than micro-optimization

## Related Patterns

- See `02_DML_Anti_Patterns.md` for other safety patterns
- See `02_Test_Configuration_Setup.md` for test setup examples
- See `06_DML_Common_Patterns.md` for general DML patterns

## Summary

**Rule**: Always add `if (this.obj != NULL)` before calling signal interface methods.

**Why**: Signal interfaces may not be connected in test configurations.

**Impact**: Prevents segmentation faults while allowing tests to run successfully.
