# Create tests for Watchdog Lock register

**Change ID:** `implement-watchdog lock`  
**Status:** Draft  
**Priority:** 2

## Summary

Create comprehensive Python tests for the Watchdog Lock register.

## Motivation

This change implements the Watchdog Lock functionality 
as specified in the hardware specification document.

## Detailed Description

Create comprehensive Python tests for the Watchdog Lock register.

**Test Coverage Requirements:**
1. Test basic read/write operations
2. Test reset behavior (should reset to 32)
3. Test access restrictions (RW)
4. Test all register fields individually
5. Test side effects:
   - 看门狗模块LOCK寄存器，该寄存器控制其他寄存器的写访问权限，保护失控软件对看门狗模块寄存器的恶意更改。当写入0x1ACCE551时使能其他寄存器的写权限；当写入其他值时使其他寄存器丧失写访问权限。读该寄存器时根据写入值是否为0x1ACCE551返回LOCK状态：
   - Ø  0 -- 寄存器写权限使能，unlock；
   - 复位时值：32’h00000000
   - |Bit|Name|R/W|Reset|Description|
   - |31-0|wdog_lock|R/W|32’h00000000|Enable write access to all other registers by writing 0x1ACCE551. Disable write access by writing any other value.<br><br>A read return the lock status:<br><br>0x0 -- 

**Test Template:**
Create a new file: `modules/demo_watchdog/test/test_watchdog lock.py`

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

`task-013`

## Files to Modify

- `modules/demo_watchdog/test/test_watchdog lock.py`

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
