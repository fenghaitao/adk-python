# TestFixAgent - Code Doctor for OpenSpec Implementations

The TestFixAgent is a specialized agent that runs after the ApplyAgent to fix build and test failures while preserving the original implementation. It acts as a "code doctor" - fixing grammar, syntax, and logic errors without removing or rewriting the core functionality.

## Overview

### Purpose
- Fix build/test failures after ApplyAgent completes
- Preserve all original functionality implemented by ApplyAgent
- Apply minimal fixes based on DML/Test best practices
- Report improvements and provide comprehensive summaries

### Key Principles
1. **PRESERVE, DON'T REPLACE**: Fix errors without deleting ApplyAgent's code
2. **MINIMAL CHANGES**: Make the smallest possible changes to fix issues
3. **FOLLOW BEST PRACTICES**: Use DML/Test best practices to guide fixes
4. **INCREMENTAL FIXING**: Fix one error at a time, test, then move to next

## Usage

### Basic Usage
```bash
# Run the test fix agent for a specific change
python run_test_fix_agent.py --id implement-wdt-initial

# With verbose output
python run_test_fix_agent.py --id implement-wdt-initial --verbose
```

### Slash Command Usage (in ADK)
```
/fix --id CHANGE_ID
```

## What TestFixAgent Fixes

### DML Build Errors (Grammar/Syntax)
- **Unknown identifier errors**: Wrong register scope patterns
- **Syntax errors**: Missing semicolons, wrong brackets, typos
- **Type errors**: Incorrect variable types, method signatures
- **Timer/event errors**: Anti-patterns in timing implementation

### Python Test Errors (Logic/Setup)
- **Test file location**: Tests in wrong directories
- **Register access errors**: Wrong Python API usage
- **Configuration errors**: Missing test setup, clock configuration
- **Timing/event errors**: Incorrect test timing patterns

## What TestFixAgent Preserves

### Always Preserved:
- All functional logic and business rules
- Device behavior and state management
- Register side-effects and interrupt handling
- Timer implementations and event logic
- Test scenarios and validation logic
- Overall architecture and design approach

### Never Removed:
- Core functionality implemented by ApplyAgent
- Complex logic or algorithms
- Error handling or edge cases
- Comments and documentation

## Example Fix Session

```
INITIAL ASSESSMENT:
- Build: FAILED (8 compilation errors)
- Tests: NOT_TESTED (can't run due to build failure)

INCREMENTAL FIXES:
✅ Fix #1: Unknown identifier 'WDOGLOAD' → 'WatchdogRegisters.WDOGLOAD'
✅ Fix #2: Missing semicolon in method declaration
✅ Fix #3: Timer anti-pattern → Event-based lazy evaluation
✅ Fix #4: Test file moved to correct location
✅ Fix #5: Python register access syntax corrected

FINAL STATUS:
- Build: PASSED ✅
- Tests: PARTIAL (4/5 passing) ⚠️
- Preserved: All watchdog timer logic, interrupt handling
- Improved: Code follows DML/Test best practices
```

## Output Schema

The TestFixAgent returns a structured `TestFixResult` with:

```python
class TestFixResult(BaseModel):
    change_id: str
    initial_build_status: str    # "passed", "failed", "not_tested"
    initial_test_status: str     # "passed", "failed", "not_tested"  
    final_build_status: str      # "passed", "failed"
    final_test_status: str       # "passed", "failed", "partial"
    fixes_applied: List[FixAttempt]
    preserved_functionality: List[str]
    improvements_made: List[str]
    remaining_issues: List[str]
    summary: str
```

## Best Practices Integration

The TestFixAgent automatically loads the appropriate best practice documents:

### For DML Build Errors:
- `00_DML_Best_Practices_Index.md` - Index and roadmap
- `07_DML_Register_Access_Scope.md` - For unknown identifier errors
- `03_DML_Basic_Syntax.md` - For syntax errors
- `04_DML_Timing_Timer_Modeling.md` - For timer issues
- `02_DML_Anti_Patterns.md` - To avoid common mistakes

### For Python Test Errors:
- `00_Test_Best_Practices_Index.md` - Index and roadmap
- `01_Test_File_Location_Requirements.md` - For file location issues
- `03_Test_Register_Access.md` - For register access errors
- `02_Test_Configuration_Setup.md` - For configuration issues
- `06_Test_Events_Timing.md` - For timing/event errors

## Workflow Integration

### Typical OpenSpec Workflow:
1. **ProposeAgent**: Creates the proposal and design
2. **ApplyAgent**: Implements the DML code and tests
3. **TestFixAgent**: Fixes any build/test failures ← **YOU ARE HERE**
4. **MetaImproveTextAgent**: Analyzes sessions for improvements

### When to Use TestFixAgent:
- After ApplyAgent completes but build/tests fail
- When you have working code that needs technical fixes
- To apply best practices to existing implementations
- To preserve functionality while fixing errors

## Success Criteria

### Ideal Success:
- ✅ Build: PASSED (no compilation errors)
- ✅ Tests: PASSED (all tests passing)
- ✅ Preservation: 100% of original functionality preserved
- ✅ Best Practices: All fixes follow documented patterns

### Acceptable Success:
- ✅ Build: PASSED (no compilation errors)
- ⚠️ Tests: PARTIAL (some tests passing, may need more implementation)
- ✅ Preservation: 100% of original functionality preserved
- ✅ Best Practices: All fixes follow documented patterns

## Common Fix Patterns

### DML Register Scope Fix:
```dml
// BEFORE (error)
if (WDOGLOAD.val > 0) {  // ❌ Unknown identifier

// AFTER (fixed)
if (WatchdogRegisters.WDOGLOAD.val > 0) {  // ✅ Correct scope
```

### Python Test Register Access Fix:
```python
# BEFORE (error)
dev.WDOGLOAD.val = 100  # ❌ DML syntax in Python

# AFTER (fixed)  
regs.WDOGLOAD.write(100)  # ✅ Python API
```

### Timer Anti-Pattern Fix:
```dml
// BEFORE (anti-pattern)
event timer_tick;
method init() {
    timer_tick.post(1);  // ❌ Cycle-by-cycle updates
}

// AFTER (proper pattern)
method start_timer(uint32 timeout) {
    after (timeout) call timer_expired();  // ✅ Event-based lazy evaluation
}
```

## Troubleshooting

### If TestFixAgent Can't Fix Everything:
1. **Check Remaining Issues**: Review the `remaining_issues` list
2. **Manual Review**: Some issues may need human intervention
3. **Spec Compliance**: Verify implementation matches spec requirements
4. **Best Practice Gaps**: May need new best practice documentation

### If Fixes Break Functionality:
1. **Review Preservation**: Check `preserved_functionality` list
2. **Incremental Validation**: Each fix is tested immediately
3. **Rollback Capability**: Changes are minimal and documented
4. **Best Practice Compliance**: All fixes follow documented patterns

## Files Created

- `test_fix_agent.py` - Main agent implementation
- `test_fix_agent_instruction.md` - Detailed agent instructions
- `run_test_fix_agent.py` - Example usage script
- `TEST_FIX_AGENT_README.md` - This documentation

## Integration with Other Agents

The TestFixAgent is designed to work seamlessly with other OpenSpec agents:

- **Receives**: Code from ApplyAgent that may have build/test failures
- **Provides**: Fixed, working code that preserves all original functionality
- **Enables**: MetaImproveTextAgent to analyze successful fix patterns

This creates a robust pipeline: Propose → Apply → Fix → Analyze → Improve.