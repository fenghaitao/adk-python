# Create tests for Watchdog Load register

**Change ID:** `implement-watchdog load`  
**Status:** Draft  
**Priority:** 2

## Summary

Create comprehensive Python tests for the Watchdog Load register.

## Why

This change implements the Watchdog Load functionality 
as specified in the hardware specification document.

## What Changes

- Create comprehensive Python tests for the Watchdog Load register.
- Implement the WDOGLOAD register functionality in DML with proper reset value and behavior.

**Test Coverage Requirements:**
1. Test basic read/write operations
2. Test reset behavior (should reset to 0xFFFFFFFF)
3. Test access restrictions (RW)
4. Test all register fields individually
5. Test side effects:
   - 看门狗模块重载值寄存器
   - 复位时值：0xFFFFFFFF
   - |Bit|Name|R/W|Reset|Description|
   - |31-0|wdog_load|R/W|0xFFFFFFFF|看门狗递减计时器重载值|

**Test Template:**
Create a new file: `modules/demo_watchdog/test/test_watchdog load.py`

The test should:
- Use Python Simics API to interact with the device model
- Follow the existing test patterns in the test directory
- Include both positive and negative test cases
- Verify expected behavior and side effects
- Use proper assertions and error messages

**Reference:**
- Hardware spec: /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj/wdt.md
- Existing tests in: modules/demo_watchdog/test/


## Dependencies

`task-001`

## Files to Modify

- `modules/demo_watchdog/test/test_watchdog load.py`
- `modules/demo_watchdog/demo_watchdog.dml`

## Testing Strategy

Integration tests will verify:
1. All register operations work in sequence
2. Side effects interact correctly
3. System behavior matches specification


## Risks and Mitigations

- **Risk:** Incorrect register behavior implementation
  - **Mitigation:** Comprehensive unit tests and reference to hardware spec
  
- **Risk:** Side effects not properly handled
  - **Mitigation:** Test all documented side effects individually

## Timeline

- Implementation: 1-2 hours
- Testing: 1 hour
- Review: 30 minutes