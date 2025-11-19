# Create tests for Watchdog Interrupt Status register

**Change ID:** `implement-watchdog interrupt status`  
**Status:** Draft  
**Priority:** 2

## Summary

Create comprehensive Python tests for the Watchdog Interrupt Status register.

## Motivation

This change implements the Watchdog Interrupt Status functionality 
as specified in the hardware specification document.

## Detailed Description

Create comprehensive Python tests for the Watchdog Interrupt Status register.

**Test Coverage Requirements:**
1. Test basic read/write operations
2. Test reset behavior (should reset to 1)
3. Test access restrictions (R)
4. Test all register fields individually
5. Test side effects:
   - 看门狗模块屏蔽中断状态寄存器，该寄存器bit[0]为WDOGRIS寄存器的WS0和WDOGCONTROL寄存器的INTEN的逻辑与，即WS0 & INTEN，与中断输出值相同。
   - 复位时值：1’b0
   - |Bit|Name|R/W|Reset|Description|
   - |0|watchdog interrupt|R|1’b0|Enable interrupt status from the counter|

**Test Template:**
Create a new file: `modules/demo_watchdog/test/test_watchdog interrupt status.py`

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

`task-011`

## Files to Modify

- `modules/demo_watchdog/test/test_watchdog interrupt status.py`

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
