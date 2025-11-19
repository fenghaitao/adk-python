# DML Method Signature Correction

## Issue Identified

The example code in the prompts was using incorrect DML method signatures that don't match the existing codebase.

## Incorrect Method Signatures (OLD)

```dml
register WDOGLOAD size 4 @ 0x00 "Watchdog Load register" {
    method write(uint64 value) {
        default(value);
        log info: "WDOGLOAD written: 0x%x", value;
    }
    
    method read() -> (uint64) {
        local uint64 value = default();
        return value;
    }
}
```

### Problems:
- ❌ Method name: `write()` instead of `write_register()`
- ❌ Method name: `read()` instead of `read_register()`
- ❌ Missing parameters: `enabled_bytes` and `aux`
- ❌ Wrong default() call signature
- ❌ Included unnecessary metadata (size, @address, field definitions)

## Correct Method Signatures (NEW)

Based on the existing DML file (`modules/demo_watchdog/demo_watchdog.dml`):

```dml
register WDOGLOAD {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        log info, 1: ">>> WDOGLOAD write_register() CALLED with value=0x%x", value;
        
        // Call default write behavior first
        default(value, enabled_bytes, aux);
        
        // TODO: Implement side effects for WDOGLOAD
        // Description: Watchdog Load Register
        // Fields:
        //   - wdog_load: [31:0] - Watchdog decrement timer reload value
        // TODO: Add your implementation here
        
        log info, 1: ">>> WDOGLOAD updated, value=0x%x", this.val;
    }
}
```

For read-only registers:
```dml
register WDOGVALUE {
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {
        log info, 1: ">>> WDOGVALUE read_register() CALLED";
        
        // TODO: Implement read-only register logic
        // Return the current register value
        
        return this.val;
    }
}
```

## Key Differences

1. **Method Names**:
   - ✅ `write_register()` NOT `write()`
   - ✅ `read_register()` NOT `read()`

2. **Parameters**:
   - ✅ `write_register(uint64 value, uint64 enabled_bytes, void *aux)`
   - ✅ `read_register(uint64 enabled_bytes, void *aux) -> (uint64)`

3. **Default Call**:
   - ✅ `default(value, enabled_bytes, aux)` for writes
   - ✅ Just `return this.val` for reads (not calling default())

4. **Register Value Access**:
   - ✅ Use `this.val` to access the register's current value

5. **Logging**:
   - ✅ `log info, 1:` (with log level)
   - ✅ `>>>` prefix to indicate method entry (matches existing style)

6. **Structure**:
   - ✅ No size/address metadata (that's in the glue layer)
   - ✅ No explicit field definitions (handled by DDM library)
   - ✅ Just the method implementations with side effects

## Why This Matters

The DDM (Data-Driven Modeling) library generates:
- Register structure from IP-XACT spec
- Field definitions and bit ranges
- Default read/write behavior
- Address mapping in the bank

The DML file only needs to implement **side effects** using the correct method signatures.

## Files Updated

1. **test_first_task.sh** - Updated example code in STEP 4
2. **run_openspec_from_ddm.py** - Updated template instructions for register implementation

Both files now show the correct method signatures matching the existing codebase pattern.

## Testing

The improved prompt should now guide the agent to:
1. Look at existing registers (WDOGLOAD, WDOGVALUE, etc.) as examples
2. Follow the same pattern with correct method signatures
3. Implement side effects without duplicating DDM-generated code

This should result in code that compiles and matches the project's architecture.
