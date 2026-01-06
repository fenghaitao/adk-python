# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [Current date in YYYY-MM-DD format]
**Status**: [Update after completing spec - count [NEEDS CLARIFICATION] markers and set to "Ready for Planning" (0 markers) or "Draft (N clarifications needed)"]
**Input**: User description: "$ARGUMENTS" (text provided after /specify command)

---

## Simics DML Device Modeling Guidance

**Note**: For Simics device modeling projects, comprehensive DML learning resources are available:
- **.specify/memory/DML_grammar.md**: Complete DML 1.4 grammar reference with syntax rules and language constructs
- **.specify/memory/DML_Device_Development_Best_Practices.md**: Best practices, patterns, and common pitfalls for DML development
- **spec/[feature-name]/[device-name]-registers.xml**: IP-XACT register description XML

**Functional Modeling Defaults** (unless explicitly stated otherwise):
- **Timing**: Precise timing is NOT required for functional models - focus on functional correctness
- **Checkpoint/Restore**: Checkpoint and restore functionality is NOT required - Simics handles this automatically for register state

---

## Hardware Specification *(mandatory)*

### Register Map

**Summary Table** (ALL registers):
| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00 | CONTROL | R/W | 32 | 0x00000000 | Control register |
| 0x04 | STATUS | R | 32 | 0x00000000 | Status register |
| 0x08 | LOAD | R/W | 32 | 0xFFFFFFFF | Load value |
| 0x0C | VALUE | R | 32 | 0xFFFFFFFF | Current counter value |
| 0x10 | INTCLR | W | 32 | 0x00000000 | Interrupt clear |
| 0x14 | RIS | R | 32 | 0x00000000 | Raw interrupt status |
| 0x18 | MIS | R | 32 | 0x00000000 | Masked interrupt status |
| 0xC00 | LOCK | R/W | 32 | 0x00000000 | Lock register |
| ... | ... | ... | ... | ... | ... |

### Register Descriptions (Side-Effect Registers Only)

**Note**: Only registers with read/write side-effects or special behaviors need detailed descriptions. Skip read-only ID registers and simple R/W registers without side-effects.

#### CONTROL - Control Register [0x08]
**Offset**: 0x08 | **Size**: 32 bits | **Access**: R/W | **Reset**: 0x00

| Field | Bits | Access | Reset | Description |
|-------|------|--------|-------|-------------|
| Reserved | [31:5] | - | - | Reserved |
| step_value | [4:2] | R/W | 0b000 | Clock divider: 000=÷1, 001=÷2, 010=÷4, 011=÷8, 100=÷16 |
| RESEN | [1] | R/W | 0 | Enable reset output (1=enabled) |
| INTEN | [0] | R/W | 0 | Enable interrupt (1=enabled, reloads counter on 0→1 transition) |

#### INTCLR - Interrupt Clear Register [0x0C]
**Offset**: 0x0C | **Size**: 32 bits | **Access**: Write Only | **Reset**: 0x00

**Side-Effect**: Writing any value clears the interrupt and reloads counter from LOAD register.

#### LOCK - Lock Register [0xC00]
**Offset**: 0xC00 | **Size**: 32 bits | **Access**: R/W | **Reset**: 0x00000000

| Field | Bits | Access | Reset | Description |
|-------|------|--------|-------|-------------|
| lock | [31:0] | R/W | 0x00 | Write 0x1ACCE551 to unlock, any other value to lock |

**Side-Effects**:
- **Write 0x1ACCE551**: Enables write access to all other registers (unlocked)
- **Write any other value**: Disables write access to all other registers (locked)
- **Read**: Returns 0x0 if unlocked, 0x1 if locked

### External Interfaces and Signals

**Interrupt Outputs**:
- **Signal Name**: [e.g., "wdogint", or NEEDS CLARIFICATION]
- **Direction**: Output
- **Type**: [e.g., "Edge-triggered", "Level-triggered", or NEEDS CLARIFICATION]
- **Assertion Condition**: [e.g., "Asserted when counter reaches zero and INTEN=1"]
- **Clear Mechanism**: [e.g., "Cleared by writing to INTCLR register"]

**Reset Inputs**:
- **Signal Name**: [e.g., "wrst_n", "prst_n", or NEEDS CLARIFICATION]
- **Direction**: Input
- **Type**: [e.g., "Active-low asynchronous reset"]
- **Effect**: [e.g., "Resets all registers to default values, stops counter"]

**Other Signals**:
- **Signal Name**: [e.g., "wdogres", "status_led", or NEEDS CLARIFICATION]
- **Direction**: [Input/Output/Bidirectional]
- **Purpose**: [e.g., "System reset output on second timeout"]
- **Behavior**: [e.g., "Asserted when counter reaches zero twice consecutively with RESEN=1"]

### Device Operational Model

**CRITICAL**: Document device states, transitions, and software/hardware interaction flows that drive test scenarios.

#### Device States and Transitions

**State Diagram Format**:
```
[STATE_1] → [STATE_2] → [STATE_3] → [STATE_4]
              ↑____________↓
```

**State Documentation Template**:
For each identified state, document:
1. **[STATE_NAME]**: Brief description
   - Entry conditions: [How device enters this state]
   - Observable indicators: [Register values, signal states that indicate this state]
   - Exit conditions: [What causes transition to other states]
   - *Test Scenario*: [Which scenario verifies this state]

**Common Device States**: RESET (initial), IDLE (configured), ACTIVE (operating), ERROR (fault detected), DISABLED (intentionally off)

**State Transition Template**: **[SOURCE] → [TARGET]**: Trigger condition, *Validate*: [Observable change]

**Example - Generic Transitions**:
- **RESET → IDLE**: Configuration write completes successfully
  - *Validate*: STATUS register shows ready flag, control register reflects configuration
- **IDLE → ACTIVE**: Enable bit set in control register
  - *Validate*: STATUS register shows active flag, output signals change state

#### Software/Hardware Interaction Flows

**Flow Documentation Template**:
```
Flow [N]: [Flow Name] (maps to Test Scenario [X])

State Transition: [INITIAL_STATE] → [INTERMEDIATE_STATE] → [FINAL_STATE]

Software Actions                    Hardware Responses                Observable State
─────────────────────────────────────────────────────────────────────────────────────
1. [Software action description]  → [Hardware response]            → [What software can observe]
2. [Next action...]               → [Response...]                  → [Observable change...]

Test Validation:
- [What to verify for step 1]
- [What to verify for step 2]
```

**Common Flow Patterns**: Device Initialization (RESET → IDLE → ACTIVE), Interrupt Handling (ACTIVE → INTERRUPT_PENDING → ACTIVE), Error Recovery (ACTIVE → ERROR → IDLE)

#### Register Access Ordering Requirements

**Critical Ordering Constraints** (enforce in tests):
[List any ordering requirements extracted from specification, e.g.:]
1. **[Operation A] before [Operation B]**: [Reason/consequence if violated]

**Common Patterns**: Configure before enable, Disable before reconfigure, Clear status before operation, Unlock before protected writes

**Observable vs. Non-Observable**:
- **Software CAN observe**: Register values, interrupt signals, output pins
- **Software CANNOT observe**: Internal clock dividers, FSM states, pipeline stages (must infer from observable behavior)

### Memory Interface Requirements

**Address Space**:
- **Base Address**: [e.g., "0x1000", or NEEDS CLARIFICATION]
- **Size**: [e.g., "4KB (0x1000 bytes)", or NEEDS CLARIFICATION]
- **Alignment**: [e.g., "4-byte aligned for 32-bit registers"]

**Access Patterns**:
- **Supported Widths**: [e.g., "32-bit only", "8/16/32-bit", or NEEDS CLARIFICATION]
- **Unaligned Access**: [e.g., "Not supported - must be aligned", or NEEDS CLARIFICATION]
- **Burst Access**: [e.g., "Not supported", "Supported for data registers", or NEEDS CLARIFICATION]

**Timing Requirements**:
- **Register Access Latency**: [e.g., "Single cycle", "2-3 cycles", or NEEDS CLARIFICATION]
- **Counter Precision**: [e.g., "Decrements once per clock cycle", or NEEDS CLARIFICATION]
- **Interrupt Latency**: [e.g., "Asserted within 1 clock cycle of timeout", or NEEDS CLARIFICATION]

---

## Functional Requirements *(mandatory)*

**Purpose**: Define testable, verifiable requirements derived from the Hardware Specification. Each requirement must be traceable to hardware behaviors and validated by test scenarios.

**Organization**: Group requirements by functional area with standard ID prefixes:
- **FUNC-XXX**: Core device functionality (timer behavior, state transitions)
- **REG-XXX**: Register access requirements (R/W behaviors, reset values, protection)
- **INTF-XXX**: Interface/signal requirements (interrupts, clocks, resets)
- **BEHAV-XXX**: Behavioral requirements (state machines, sequencing)
- **TEST-XXX**: Test verification requirements (validation criteria)

---

### 4.1 Timer Functionality Requirements

**FUNC-001**: The device shall be a 32-bit decrementing counter that starts counting from the value in LOAD register.

**FUNC-002**: The timer shall decrement at a rate determined by the clock divider specified in CONTROL[4:2].

**FUNC-003**: The timer shall reload with the value in LOAD when it reaches zero.

**FUNC-004**: The timer shall continue decrementing after reaching zero if INTEN is not set.

### 4.2 Interrupt and Reset Requirements

**FUNC-005**: When the counter reaches zero and INTEN=1, the device shall assert the interrupt signal.

**FUNC-006**: The interrupt signal shall remain asserted until cleared by writing to INTCLR.

**FUNC-007**: If the counter reaches zero again while interrupt is asserted and RESEN=1, the device shall assert the reset signal.

**FUNC-008**: The reset signal shall remain asserted until a system reset occurs.

**FUNC-009**: Writing any value to INTCLR shall clear the interrupt and reload the counter from LOAD.

### 4.3 Register Access Requirements

**FUNC-010**: Register access shall be performed via the bus interface.

**FUNC-011**: All registers except LOCK shall be write-protected when locked.

**FUNC-012**: VALUE register shall always be readable regardless of lock status.

**FUNC-013**: LOCK register itself shall always be readable and writable.

### 4.4 Clock Divider Requirements

**FUNC-014**: The clock divider setting shall determine the timer decrement rate:
- 000: No division (÷1)
- 001: Divide by 2
- 010: Divide by 4
- 011: Divide by 8
- 100: Divide by 16

**FUNC-015**: Values 101-111 for the clock divider shall be treated as invalid.

### 4.5 Integration Test Mode Requirements

**FUNC-016**: When ITCR[0] is set to 1, the device shall enter integration test mode.

**FUNC-017**: In integration test mode, writing to ITOP shall directly control output signals.

**FUNC-018**: In integration test mode, normal timer behavior shall be overridden.

### 4.6 Identification Requirements

**FUNC-019**: The device shall implement all identification registers with the specified values.

**FUNC-020**: The identification registers shall be readable at all times and not affected by lock mechanism.

## 5. Register Access Requirements

### 5.1 Register Access Behavior

**REG-001**: LOAD register supports read and write operations, with reset value 0xFFFFFFFF.

**REG-002**: VALUE register supports read operations only, returning current counter value.

**REG-003**: CONTROL register supports read and write operations, with reset value 0x00000000.

**REG-004**: INTCLR register supports write operations only, any write clears interrupt and reloads counter.

**REG-005**: RIS register supports read operations, showing raw interrupt status.

**REG-006**: MIS register supports read operations, showing masked interrupt status.

**REG-007**: LOCK register supports read and write operations with special locking behavior.

### 5.2 Lock Protection Requirements

**REG-010**: Writing unlock code to LOCK register shall unlock write access to protected registers.

**REG-011**: Writing any value other than unlock code to LOCK register shall lock write access.

**REG-012**: Reading LOCK register shall return 0x00000000 when unlocked, 0x00000001 when locked.

## 6. Behavioral Requirements

### 6.1 Timer State Machine

**BEHAV-001**: When INTEN=0, the timer shall decrement and reload at zero without generating interrupts.

**BEHAV-002**: When INTEN=1 and the timer reaches zero, the raw interrupt status shall be set to 1.

**BEHAV-003**: When RESEN=1, INTEN=1, and the timer reaches zero for the second consecutive time without interrupt clear, the reset signal shall be asserted.

**BEHAV-004**: The timer shall be paused when clock enable signal is deasserted.

### 6.2 Interrupt Handling

**BEHAV-005**: The interrupt output signal shall be asserted when MIS[0] is 1.

**BEHAV-006**: The interrupt signal shall be deasserted when INTCLR is written, regardless of counter state.

**BEHAV-007**: The reset signal shall remain asserted until system reset occurs.

### 6.3 Reset Behavior

**BEHAV-008**: Reset signals shall reset the device to its initial state.

**BEHAV-009**: When reset occurs, all registers shall return to their specified reset values.

---

## User Scenarios & Testing *(mandatory)*

**Purpose**: Define comprehensive, testable scenarios that drive specification clarity, state machine design, and test case development. Each scenario maps to device states, transitions, and operational flows.

### 7. Test Scenarios

### 7.1 Basic Timer Operation Test

**TEST-001**: Verify basic timer countdown functionality.
- **Setup**: Write a small value (e.g., 0x10) to LOAD, set INTEN=1 in CONTROL
- **Action**: Verify counter decrements in VALUE register
- **Expected**: Counter value decreases from 0x10 to 0x0, interrupt is generated

### 7.2 Interrupt and Reset Generation Test

**TEST-002**: Verify interrupt and reset generation sequence.
- **Setup**: Write value to LOAD, set INTEN=1, RESEN=1 in CONTROL
- **Action**: Allow timer to count to zero, then count to zero again without clearing interrupt
- **Expected**: First zero generates interrupt, second zero generates reset

### 7.3 Lock Protection Test

**TEST-003**: Verify lock protection mechanism.
- **Setup**: Write unlock code to LOCK to unlock
- **Action**: Write new value to LOAD, verify write succeeds
- **Subsequently**: Write non-magic value to LOCK to lock
- **Action**: Attempt to write to LOAD again
- **Expected**: First write succeeds, second write fails (register unchanged)

### 7.4 Clock Divider Test

**TEST-004**: Verify different clock divider settings.
- **Setup**: Configure timer with same initial value but different step_value settings
- **Action**: Measure time to reach zero for each divider setting
- **Expected**: Timer with larger divider values takes proportionally longer to reach zero

### 7.5 Integration Test Mode Test

**TEST-005**: Verify integration test mode functionality.
- **Setup**: Set ITCR[0]=1 to enable test mode
- **Action**: Write different values to ITOP register
- **Expected**: Direct control of interrupt and reset output signals

---

*Mark any unclear cases with [NEEDS CLARIFICATION: specific behavior under [condition]]?*

### 8. Input/Output Signals

### 8.1 Clock and Reset Signals
- **clk**: Work clock input (input)
- **clk_en**: Work clock enable (input)
- **rst_n**: Reset (active low, input)

### 8.2 Output Signals
- **irq**: Interrupt output (output)
- **res**: Reset output (output, if applicable)

## 9. Implementation Notes

### 9.1 Modeling Scope
- This specification covers register behavior, state transitions, interrupt/reset conditions, and lock protection
- Functional model implementation - precise cycle-accurate timing is not required
- Base clock frequency is not specified - this is a functional model
- Checkpoint/restore is handled automatically by Simics

### 9.2 Performance Considerations
- The implementation should achieve minimal simulation overhead
- Follow Simics device development best practices for performance

---

## Clarifications Required

**INSTRUCTIONS**: After completing the specification, list all `[NEEDS CLARIFICATION: ...]` markers found in the document above (excluding this instructions section and headers).

**Format**:
1. **[Section Name]**: [NEEDS CLARIFICATION text]
2. **[Section Name]**: [NEEDS CLARIFICATION text]
...

**Status Update**:
- **Total Clarifications**: [N] items
- **Specification Status**: [If N=0: "Ready for Planning", else: "Draft (N clarifications needed)"]

*If no clarifications are needed, write:*
- **Total Clarifications**: 0 items
- **Specification Status**: Ready for Planning

---

## Review & Acceptance Checklist

### AUTOMATED CHECKS (AI Agent MUST verify)

**Content Quality**:
- [ ] No implementation details (DML syntax, code structure, algorithms)
- [ ] Focused on hardware behavior and device operation
- [ ] All mandatory sections completed

**Hardware Specification Completeness**:
- [ ] Register map table included (all registers with offset, name, size, access, reset, description)
- [ ] Side-effect register descriptions included (detailed bit fields for registers with side-effects)
- [ ] External interfaces documented (I/O signals with direction/type/behavior)
- [ ] Device operational model documented (states, transitions, SW/HW interaction flows)

**Functional Requirements Completeness**:
- [ ] Requirements organized by category (FUNC, REG, BEHAV, INTF, TEST)
- [ ] At least 15+ requirements across all categories
- [ ] At least 5 test scenarios included (Setup/Action/Expected format)

---

## Specification Generation Status
*AI Agent: Mark [x] as each section is completed*

### Section Completion
- [ ] **Register Map**: Summary table + detailed descriptions for side-effect registers
- [ ] **External Interfaces**: I/O signals documented
- [ ] **Device Operational Model**: States, transitions, SW/HW flows documented
- [ ] **Functional Requirements**: Categorized requirements generated (FUNC, REG, BEHAV)
- [ ] **Test Scenarios**: 5+ scenarios with Setup/Action/Expected format

### Quality Validation
- [ ] **Clarifications Listed**: All [NEEDS CLARIFICATION] markers documented
- [ ] **Status Updated**: Clarification count complete, Status field at top updated

**COMPLETION CRITERIA**: All checkboxes marked [x] = Specification ready for planning phase
# Simics Watchdog Timer (WDT) Device Specification

## 1. Device Overview

The Watchdog Timer (WDT) is a 32-bit decrementing counter device compatible with ARM PrimeCell specification. The device generates an interrupt when the counter reaches zero and can generate a system reset if the interrupt is not cleared before the counter reaches zero again. The device includes lock protection to prevent unauthorized access to configuration registers and supports integration test mode for validation.

- Device Name: Watchdog Timer (WDT)
- Base Address: 0x1000
- Address Range: 0x1000 - 0x1FFF (4KB)
- Category: Timer/Counter
- Interface: APB bus
- Primary Function: System monitoring and reset generation

## 2. Register Map

### 2.1 Register Map Overview

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00 | WDOGLOAD | R/W | 32 | 0xFFFFFFFF | Watchdog decrement timer reload value |
| 0x04 | WDOGVALUE | R | 32 | 0xFFFFFFFF | Current value of watchdog counter |
| 0x08 | WDOGCONTROL | R/W | 32 | 0x00 | Control register for step value and enable bits |
| 0x0C | WDOGINTCLR | W | 32 | 0x00 | Interrupt clear register |
| 0x10 | WDOGRIS | R | 32 | 0x00 | Raw interrupt status register |
| 0x14 | WDOGMIS | R | 32 | 0x00 | Masked interrupt status register |
| 0xC00 | WDOGLOCK | R/W | 32 | 0x00000000 | Register lock/unlock protection |
| 0xF00 | WDOGITCR | R/W | 32 | 0x00 | Integration test mode control |
| 0xF04 | WDOGITOP | W | 32 | 0x00 | Integration test output control |
| 0xFD0 | WDOGPERIPHID4 | R | 8 | 0x04 | Peripheral ID register 4 |
| 0xFD4 | WDOGPERIPHID5 | R | 8 | 0x00 | Peripheral ID register 5 |
| 0xFD8 | WDOGPERIPHID6 | R | 8 | 0x00 | Peripheral ID register 6 |
| 0xFDC | WDOGPERIPHID7 | R | 8 | 0x00 | Peripheral ID register 7 |
| 0xFE0 | WDOGPERIPHID0 | R | 8 | 0x24 | Peripheral ID register 0 |
| 0xFE4 | WDOGPERIPHID1 | R | 8 | 0xB8 | Peripheral ID register 1 |
| 0xFE8 | WDOGPERIPHID2 | R | 8 | 0x1B | Peripheral ID register 2 |
| 0xFEC | WDOGPERIPHID3 | R | 8 | 0x00 | Peripheral ID register 3 |
| 0xFF0 | WDOGPECELLID0 | R | 8 | 0x0D | PrimeCell ID register 0 |
| 0xFF4 | WDOGPECELLID1 | R | 8 | 0xF0 | PrimeCell ID register 1 |
| 0xFF8 | WDOGPECELLID2 | R | 8 | 0x05 | PrimeCell ID register 2 |
| 0xFFC | WDOGPECELLID3 | R | 8 | 0xB1 | PrimeCell ID register 3 |

### 2.2 Side-Effect Register Descriptions

#### WDOGLOAD (Offset: 0x00)
- Width: 32 bits
- Access: Read/Write
- Reset: 0xFFFFFFFF
- Description: This register sets the initial value for the watchdog decrementing counter.
- Side effects: When INTEN bit is set to 1 after previously being 0, the counter reloads from this value.

#### WDOGVALUE (Offset: 0x04)
- Width: 32 bits
- Access: Read Only
- Reset: 0xFFFFFFFF
- Description: Shows the current value of the watchdog counter.
- Side effects: [NEEDS CLARIFICATION: Does reading this register have side effects?]

#### WDOGCONTROL (Offset: 0x08)
- Width: 32 bits
- Access: Read/Write
- Reset: 0x00000000
- Description: Controls the behavior of the watchdog timer.
- Side effects: Setting INTEN bit [0] to 1 reloads the counter from WDOGLOAD if previously disabled.

| Bit(s) | Name | Type | Reset | Description |
|--------|------|------|-------|-------------|
| 31-5 | Reserved | - | - | Reserved |
| 4-2 | step_value | R/W | 3'b000 | Clock divider value: 000 (÷1), 001 (÷2), 010 (÷4), 011 (÷8), 100 (÷16) |
| 1 | RESEN | R/W | 1'b0 | Enable watchdog reset output. Set to 1 to enable reset, 0 to disable |
| 0 | INTEN | R/W | 1'b0 | Enable interrupt. Set to 1 to enable timer and interrupt |

#### WDOGINTCLR (Offset: 0x0C)
- Width: 32 bits
- Access: Write Only
- Reset: 0x00000000
- Description: Writing any value to this register clears the watchdog interrupt and reloads the counter from WDOGLOAD.
- Side effects: Clears the interrupt and reloads the counter.

#### WDOGRIS (Offset: 0x10)
- Width: 32 bits
- Access: Read Only
- Reset: 0x00000000
- Description: Shows the raw interrupt status from the counter.
- Side effects: Value changes based on timer state (read-only status register).

| Bit(s) | Name | Type | Reset | Description |
|--------|------|------|-------|-------------|
| 31-1 | Reserved | - | - | Reserved |
| 0 | raw_watchdog_int | R | 1'b0 | Raw interrupt status from the counter |

#### WDOGMIS (Offset: 0x14)
- Width: 32 bits
- Access: Read Only
- Reset: 0x00000000
- Description: Shows the masked interrupt status (WDOGRIS[0] AND WDOGCONTROL.INTEN).
- Side effects: Value changes based on timer state and INTEN setting.

| Bit(s) | Name | Type | Reset | Description |
|--------|------|------|-------|-------------|
| 31-1 | Reserved | - | - | Reserved |
| 0 | masked_watchdog_int | R | 1'b0 | Masked interrupt status from the counter |

#### WDOGLOCK (Offset: 0xC00)
- Width: 32 bits
- Access: Read/Write
- Reset: 0x00000000
- Description: Lock register to protect other registers from unauthorized access.
- Side effects: Writing 0x1ACCE551 enables write access to all other registers; any other value disables write access.

| Bit(s) | Name | Type | Reset | Description |
|--------|------|------|-------|-------------|
| 31-0 | wdog_lock | R/W | 32'h00000000 | Write 0x1ACCE551 to enable write access, any other value to disable. Read returns 0 if unlocked, 1 if locked. |

#### WDOGITCR (Offset: 0xF00)
- Width: 32 bits
- Access: Read/Write
- Reset: 0x00000000
- Description: Integration test mode control register.
- Side effects: Writing 1 enables integration test mode (disables normal timer operation), writing 0 disables test mode.

| Bit(s) | Name | Type | Reset | Description |
|--------|------|------|-------|-------------|
| 31-1 | Reserved | - | - | Reserved |
| 0 | int_test_enable | R/W | 1'b0 | 1 = enter integration test mode, 0 = normal decrementing counter mode |

#### WDOGITOP (Offset: 0xF04)
- Width: 32 bits
- Access: Write Only
- Reset: 0x00000000
- Description: Integration test output register, used when in integration test mode.
- Side effects: Directly drives wdogint and wdogres outputs when in test mode.

| Bit(s) | Name | Type | Reset | Description |
|--------|------|------|-------|-------------|
| 31-2 | Reserved | - | - | Reserved |
| 1 | int_test_wdogint | W | 1'b0 | Integration test mode WDOGINT value |
| 0 | int_test_wdogres | W | 1'b0 | Integration test mode WDOGRES value |

#### WDOGPERIPHID4-7 (Offset: 0xFD0-0xFDC)
- Width: 8 bits each
- Access: Read Only
- Description: Peripheral identification registers.
- Side effects: None (read-only identification registers).

#### WDOGPERIPHID0-3 (Offset: 0xFE0-0xFEC)
- Width: 8 bits each
- Access: Read Only
- Description: Peripheral identification registers.
- Side effects: None (read-only identification registers).

#### WDOGPCELLID0-3 (Offset: 0xFF0-0xFFC)
- Width: 8 bits each
- Access: Read Only
- Description: PrimeCell identification registers.
- Side effects: None (read-only identification registers).

## 3. External Interfaces & Signals

| Signal | Direction | Width | Description |
|--------|-----------|-------|-------------|
| wclk | Input | 1 | Work clock input |
| wclk_en | Input | 1 | Work clock gate (timer works on rising edge when enabled) |
| wrst_n | Input | 1 | Work clock domain reset (active low, asynchronous) |
| wdogint | Output | 1 | Watchdog interrupt signal (edge-triggered, stays asserted until cleared) |
| wdogres | Output | 1 | Watchdog reset signal (stays asserted until system reset) |

## 4. Register Side-Effects & Behaviors

### 4.1 Counter/Timer Behavior
- When the counter reaches zero and WDOGCONTROL.INTEN=1, the hardware sets WDOGRIS[0] and WDOGMIS[0] to 1 and asserts the wdogint signal.
- If the counter reaches zero again while the interrupt is still asserted and WDOGCONTROL.RESEN=1, the hardware asserts the wdogres signal.
- The counter decrements by the value specified in WDOGCONTROL.step_value on each enabled wclk rising edge.

### 4.2 State Machine Behavior
- The device operates in different states based on control register settings and counter values.
- In integration test mode (WDOGITCR[0]=1), normal timer operation is disabled and outputs are directly controlled via WDOGITOP register.
- In locked state, register writes to most registers are ignored.

## 5. Device Operational Model

### 5.1 Device States

State: RESET
- Entry conditions: wrst_n is low (asserted)
- Observable indicators: All registers have reset values
- Exit conditions: wrst_n goes high (deasserted)
- Test Scenario: Verify reset behavior

State: IDLE
- Entry conditions: Device is reset and INTEN=0 in WDOGCONTROL
- Observable indicators: Counter is not decrementing, no interrupts asserted
- Exit conditions: INTEN is set to 1
- Test Scenario: Basic timer operation test

State: COUNTING
- Entry conditions: Device is initialized and INTEN=1 in WDOGCONTROL
- Observable indicators: Counter value in WDOGVALUE is decrementing
- Exit conditions: Counter reaches zero or INTEN is set to 0
- Test Scenario: Basic timer operation test

State: INTERRUPT_PENDING
- Entry conditions: Counter reaches zero and INTEN=1
- Observable indicators: WDOGRIS[0]=1, WDOGMIS[0]=1, wdogint asserted
- Exit conditions: WDOGINTCLR is written or RESET occurs
- Test Scenario: Interrupt and reset generation test

State: RESET_GENERATION
- Entry conditions: Counter reaches zero again while wdogint asserted and RESEN=1
- Observable indicators: wdogres asserted
- Exit conditions: System reset occurs
- Test Scenario: Interrupt and reset generation test

State: INTEGRATION_TEST
- Entry conditions: WDOGITCR[0]=1
- Observable indicators: Normal timer operation disabled, direct control via WDOGITOP possible
- Exit conditions: WDOGITCR[0]=0
- Test Scenario: Integration test mode test

### 5.2 State Transitions

[RESET] → [IDLE]: wrst_n deasserted
- Validate: Registers show reset values, no activity

[IDLE] → [COUNTING]: INTEN set to 1
- Validate: Counter starts decrementing from WDOGLOAD value

[COUNTING] → [INTERRUPT_PENDING]: Counter reaches zero with INTEN=1
- Validate: WDOGRIS[0]=1, WDOGMIS[0]=1, wdogint asserted

[INTERRUPT_PENDING] → [COUNTING]: WDOGINTCLR written
- Validate: Counter reloads from WDOGLOAD, interrupt cleared

[INTERRUPT_PENDING] → [RESET_GENERATION]: Counter reaches zero again with RESEN=1
- Validate: wdogres signal asserted

[COUNTING/INTERRUPT_PENDING] → [INTEGRATION_TEST]: WDOGITCR[0] set to 1
- Validate: Normal timer operation disabled

[INTEGRATION_TEST] → [COUNTING]: WDOGITCR[0] set to 0
- Validate: Normal timer operation resumed

### 5.3 SW/HW Interaction Flows

Flow: Basic Timer Operation (maps to Test Scenario 1)
State Transition: [IDLE] → [COUNTING] → [INTERRUPT_PENDING]

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write value to WDOGLOAD | Load value stored | WDOGLOAD shows value |
| 2. Write control settings to WDOGCONTROL (INTEN=1) | Counter starts counting | WDOGVALUE shows decreasing values |
| 3. Wait for counter to reach zero | wdogint asserted, WDOGRIS[0]=1 | WDOGMIS[0]=1 |

Flow: Interrupt Clear (maps to Test Scenario 1)
State Transition: [INTERRUPT_PENDING] → [COUNTING]

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write any value to WDOGINTCLR | Counter reloads from WDOGLOAD | WDOGVALUE shows reload value |
| 2. wdogint signal cleared | Interrupt cleared | WDOGMIS[0]=0, WDOGRIS[0]=0 |

Flow: Lock Protection (maps to Test Scenario 3)
State Transition: [LOCKED] ↔ [UNLOCKED]

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write 0x1ACCE551 to WDOGLOCK | Other registers unlocked | WDOGLOCK returns 0x0 |
| 2. Write other value to WDOGLOCK | Other registers locked | WDOGLOCK returns 0x1 |

Flow: Integration Test Mode (maps to Test Scenario 5)
State Transition: [COUNTING] ↔ [INTEGRATION_TEST]

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write 0x1 to WDOGITCR[0] | Normal timer disabled | Timer stops counting |
| 2. Write values to WDOGITOP | Direct control of outputs | wdogint/wdogres follow WDOGITOP |

## 6. Functional Requirements

### 6.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter.
**FUNC-002**: The timer shall decrement at a rate determined by the step_value field in the control register.
**FUNC-003**: The timer shall reload from WDOGLOAD register when WDOGINTCLR is written.
**FUNC-004**: The timer shall support 5 different clock divider values: ÷1, ÷2, ÷4, ÷8, ÷16.

### 6.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1, device shall assert wdogint.
**FUNC-006**: When wdogint is asserted, WDOGRIS[0] and WDOGMIS[0] shall be set to 1.
**FUNC-007**: If counter reaches zero again while interrupt asserted and RESEN=1, device shall assert wdogres.
**FUNC-008**: Writing any value to WDOGINTCLR shall clear the wdogint signal.
**FUNC-009**: The wdogint signal shall remain asserted until WDOGINTCLR is written.

### 6.3 Register Access Requirements
**FUNC-010**: Register access shall be performed via APB bus interface.
**FUNC-011**: All registers except WDOGLOCK shall be write-protected when locked.
**FUNC-012**: WDOGLOCK register shall accept 0x1ACCE551 to unlock other registers.
**FUNC-013**: WDOGLOCK register shall lock other registers when any value except 0x1ACCE551 is written.
**FUNC-014**: WDOGRIS register shall be read-only showing raw interrupt status.
**FUNC-015**: WDOGMIS register shall be read-only showing masked interrupt status.
**FUNC-016**: WDOGVALUE register shall be read-only showing current counter value.

### 6.4 Clock Divider Requirements
**FUNC-017**: Clock divider setting shall determine timer decrement rate according to step_value mapping.
**FUNC-018**: The step_value field shall support 5 valid settings: 000 (÷1), 001 (÷2), 010 (÷4), 011 (÷8), 100 (÷16).
**FUNC-019**: Other step_value settings shall be invalid.
**FUNC-020**: The timer shall decrement by the specified step_value on each enabled clock cycle.

### 6.5 Integration Test Mode Requirements
**FUNC-021**: When WDOGITCR[0]=1, device shall enter integration test mode.
**FUNC-022**: In integration test mode, normal timer operation shall be disabled.
**FUNC-023**: When in test mode, WDOGITOP register shall allow direct control of wdogint and wdogres outputs.
**FUNC-024**: When WDOGITCR[0]=0, device shall return to normal mode.

### 6.6 Identification Requirements
**FUNC-025**: Device shall implement all PrimeCell identification registers (WDOGPCELLID0-3).
**FUNC-026**: Device shall implement all peripheral identification registers (WDOGPERIPHID0-7).

## 7. Behavioral Requirements
**BEHAV-001**: When INTEN=0, timer shall decrement without generating interrupts.
**BEHAV-002**: When INTEN=1 and timer reaches zero, WDOGRIS[0] shall be set to 1.
**BEHAV-003**: When INTEN=1 and timer reaches zero, WDOGMIS[0] shall be set to 1.
**BEHAV-004**: When RESEN=0 and timer reaches zero again, wdogres shall not be asserted.
**BEHAV-005**: When wdogres is asserted, it shall remain asserted until system reset occurs.
**BEHAV-006**: Reading WDOGLOCK register shall return 0 when unlocked and 1 when locked.
**BEHAV-007**: When WDOGINTCLR is written, counter shall reload from WDOGLOAD value.
**BEHAV-008**: Counter shall stop when INTEN is changed from 1 to 0.

## 8. Test Scenarios

### 8.1 Basic Timer Operation Test
**TEST-001**: Verify basic timer countdown functionality.
- Setup: Write small value to WDOGLOAD, set INTEN=1 in WDOGCONTROL
- Action: Verify counter decrements in WDOGVALUE register
- Expected: Counter value decreases, interrupt is generated at zero

### 8.2 Interrupt and Reset Generation Test
**TEST-002**: Verify interrupt and reset generation sequence.
- Setup: Write value to WDOGLOAD, set INTEN=1, RESEN=1
- Action: Allow timer to count to zero twice without clearing interrupt
- Expected: First zero generates interrupt, second generates reset

### 8.3 Lock Protection Test
**TEST-003**: Verify lock protection mechanism.
- Setup: Write 0x1ACCE551 to WDOGLOCK to unlock
- Action: Write to WDOGLOAD (should succeed), then lock, then try again
- Expected: First write succeeds, second write fails (locked)

### 8.4 Clock Divider Test
**TEST-004**: Verify different clock divider settings.
- Setup: Configure timer with same value but different step_value
- Action: Measure time to reach zero for each setting
- Expected: Larger divider → proportionally longer countdown

### 8.5 Integration Test Mode Test
**TEST-005**: Verify integration test mode functionality.
- Setup: Set WDOGITCR[0]=1 to enable test mode
- Action: Write different values to WDOGITOP register
- Expected: Direct control of wdogint and wdogres outputs

### 8.6 Register Read/Write Test
**TEST-006**: Verify register access behaviors.
- Setup: Configure timer and check various register values
- Action: Read and write to different registers
- Expected: All registers behave according to their access types and descriptions

### 8.7 Reset Behavior Test
**TEST-007**: Verify reset behavior.
- Setup: Configure timer with various settings
- Action: Assert and deassert wrst_n signal
- Expected: All registers return to reset values during reset

### 8.8 Counter Reload Test
**TEST-008**: Verify counter reload functionality.
- Setup: Set up timer with specific WDOGLOAD value
- Action: Write to WDOGINTCLR after interrupt
- Expected: Counter reloads from WDOGLOAD value