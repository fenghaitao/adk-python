# OpenSpec Always-Autonomous Mode - Quick Reference

## Key Point

**The agent ALWAYS runs in full autonomous mode.** No configuration needed.

## What Changed

### Before (Problem)
```
Agent: "I created tests and OpenSpec change."
Agent: "Would you like me to implement the DML runtime logic now?"
Agent: [WAITS FOREVER]
Result: test_dev.dml still has TODOs ❌
```

### After (Fixed)
```
Agent: "I created tests and OpenSpec change."
Agent: "Now implementing DML code..."
Agent: [Implements complete register side-effects]
Agent: [Implements timer logic]
Agent: [Builds and tests]
Agent: "All done! Change archived."
Result: test_dev.dml has complete working code ✅
```

## Usage Examples

### Standard Usage (Default and Only Mode)
```bash
./run_openspec.sh wdt_project openspec-prompts/1.SIMPLE.md --device test_dev
# Completes everything automatically - no intervention needed
```

### Batch Processing
```bash
./run_spec_kit_phased.sh wdt_batch_01
./run_spec_kit_phased.sh wdt_batch_02
./run_spec_kit_phased.sh wdt_batch_03
# All complete automatically
```

## What "Implementation" Means

### ❌ NOT Implementation (Old Behavior)
```dml
register WDOGLOAD {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        // TODO: Implement side effects for WDOGLOAD
        log info, 1: "WDOGLOAD write called";
    }
}
```

### ✅ REAL Implementation (Current Behavior)
```dml
register WDOGLOAD {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        
        // Check lock status
        local uint32 lock_val = cast(dev.bank.WatchdogRegisters.WDOGLOCK.val, uint32);
        if (lock_val != 0x1ACCE551) {
            log info, 2: "WDOGLOAD write ignored - locked";
            return;
        }
        
        // Update load value and reset counter
        dev.load_value = cast(value, uint32);
        dev.counter_start_time = SIM_time();
        
        log info, 1: "WDOGLOAD updated to 0x%x", dev.load_value;
    }
}
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent stops after creating tests | This should no longer happen - check agent.py is updated |
| DML file still has TODOs | Agent didn't complete - check logs for errors |
| Tests exist but no build | Check if build step failed - see error messages |

## Verification

Check if implementation is complete:
```bash
# After running, DML file should NOT have TODOs
grep -c "TODO" simics-project/modules/test_dev/test_dev.dml
# Expected: 0 (or very few for truly optional items)

# Check if change was archived
ls -la openspec/changes/archive/
# Should see timestamped change directory
```

## What Changed

### Before (Problem)
```
Agent: "I created tests and OpenSpec change."
Agent: "Would you like me to implement the DML runtime logic now?"
Agent: [WAITS FOREVER]
Result: test_dev.dml still has TODOs ❌
```

### After (Fixed - Autonomous Mode)
```
Agent: "I created tests and OpenSpec change."
Agent: "Now implementing DML code..."
Agent: [Implements complete register side-effects]
Agent: [Implements timer logic]
Agent: [Builds and tests]
Agent: "All done! Change archived."
Result: test_dev.dml has complete working code ✅
```

### After (Fixed - Interactive Mode with OPENSPEC_AUTONOMOUS=no)
```
Agent: "I created tests and OpenSpec change."
Agent: "Would you like me to implement the DML runtime logic now?"
User: "yes"
Agent: [Implements code]
Agent: "Would you like me to archive the change?"
User: "yes"
Agent: "All done!"
```

## Usage Examples

### Batch Processing (No Human Interaction)
```bash
export OPENSPEC_AUTONOMOUS=yes
./run_spec_kit_phased.sh wdt_batch_01
./run_spec_kit_phased.sh wdt_batch_02
./run_spec_kit_phased.sh wdt_batch_03
# All complete automatically
```

### Learning Mode (Review Each Step)
```bash
export OPENSPEC_AUTONOMOUS=no
./run_openspec.sh wdt_learn openspec-prompts/1.SIMPLE.md --device test_dev
# Agent pauses for approval at key steps
```

### One-Off Override
```bash
# Usually autonomous, but this time want to review
OPENSPEC_AUTONOMOUS=no ./run_openspec.sh special_case prompt.md --device mydev
```

## What "Implementation" Means Now

### ❌ NOT Implementation (What Agent Used to Do)
```dml
register WDOGLOAD {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        // TODO: Implement side effects for WDOGLOAD
        log info, 1: "WDOGLOAD write called";
    }
}
```

### ✅ REAL Implementation (What Agent Does Now)
```dml
register WDOGLOAD {
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {
        default(value, enabled_bytes, aux);
        
        // Check lock status
        local uint32 lock_val = cast(dev.bank.WatchdogRegisters.WDOGLOCK.val, uint32);
        if (lock_val != 0x1ACCE551) {
            log info, 2: "WDOGLOAD write ignored - locked";
            return;
        }
        
        // Update load value and reset counter
        dev.load_value = cast(value, uint32);
        dev.counter_start_time = SIM_time();
        
        log info, 1: "WDOGLOAD updated to 0x%x", dev.load_value;
    }
}
```

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent stops after creating tests | `export OPENSPEC_AUTONOMOUS=yes` |
| Want to review before implementation | `export OPENSPEC_AUTONOMOUS=no` |
| DML file still has TODOs | Agent didn't implement - check mode setting |
| Tests exist but no build | Agent stopped early - check autonomous mode |
| Want default autonomous | Don't set variable (defaults to yes) |

## Integration with Existing Scripts

Add to `run_openspec.sh`:
```bash
# Near the top of the script
export OPENSPEC_AUTONOMOUS=${OPENSPEC_AUTONOMOUS:-yes}  # Default to yes
```

Add to documentation:
```bash
# In INSTALL.md or README.md
export OPENSPEC_AUTONOMOUS=yes  # For automated batch processing
# Or
export OPENSPEC_AUTONOMOUS=no   # For interactive learning mode
```

## Verification

Check if autonomous mode is working:
```bash
# Should see "ENABLED" in agent output
export OPENSPEC_AUTONOMOUS=yes
./run_openspec.sh test prompt.md --device testdev 2>&1 | grep "AUTONOMOUS MODE"
# Expected: "**AUTONOMOUS MODE: ENABLED**"

# Should see "DISABLED" 
export OPENSPEC_AUTONOMOUS=no
./run_openspec.sh test prompt.md --device testdev 2>&1 | grep "AUTONOMOUS MODE"
# Expected: "**AUTONOMOUS MODE: DISABLED**"
```

Check if implementation is complete:
```bash
# After running, DML file should NOT have TODOs
grep -c "TODO" simics-project/modules/test_dev/test_dev.dml
# Expected: 0 (or very few for truly optional items)
```
