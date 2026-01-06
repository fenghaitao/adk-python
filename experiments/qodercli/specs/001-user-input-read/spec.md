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
# Watchdog Timer Device Specification

## 1. Device Overview

The Watchdog Timer (WDT) is a 32-bit decrementing counter device compatible with ARM PrimeCell specification. The device provides configurable timeout periods and can generate interrupts and system resets when the counter reaches zero. It includes lock protection mechanisms to prevent unauthorized access and integration test capabilities for verification.

- **Device Name**: Watchdog Timer (WDT)
- **Category**: Timer/Counter
- **Base Address**: 0x1000
- **Address Range**: 0x1000 - 0x1FFF (4KB)
- **Bus Interface**: APB

## 2. Register Map

### 2.1 Register Map Overview

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00 | WDOGLOAD | R/W | 32 | 0xFFFFFFFF | Watchdog reload value |
| 0x04 | WDOGVALUE | R | 32 | 0xFFFFFFFF | Current counter value |
| 0x08 | WDOGCONTROL | R/W | 32 | 0x00 | Control register (INTEN, RESEN, step_value) |
| 0x0C | WDOGINTCLR | W | 32 | 0x00 | Interrupt clear register |
| 0x10 | WDOGRIS | R | 32 | 0x00 | Raw interrupt status |
| 0x14 | WDOGMIS | R | 32 | 0x00 | Masked interrupt status |
| 0xC00 | WDOGLOCK | R/W | 32 | 0x00000000 | Lock register (0x1ACCE551 to unlock) |
| 0xF00 | WDOGITCR | R/W | 32 | 0x00 | Integration test control register |
| 0xF04 | WDOGITOP | W | 32 | 0x00 | Integration test output register |
| 0xFD0 | WDOGPERIPHID4 | R | 8 | 0x04 | Peripheral ID register 4 |
| 0xFD4 | WDOGPERIPHID5 | R | 8 | 0x00 | Peripheral ID register 5 |
| 0xFD8 | WDOGPERIPHID6 | R | 8 | 0x00 | Peripheral ID register 6 |
| 0xFDC | WDOGPERIPHID7 | R | 8 | 0x00 | Peripheral ID register 7 |
| 0xFE0 | WDOGPERIPHID0 | R | 8 | 0x24 | Peripheral ID register 0 |
| 0xFE4 | WDOGPERIPHID1 | R | 8 | 0xB8 | Peripheral ID register 1 |
| 0xFE8 | WDOGPERIPHID2 | R | 8 | 0x1B | Peripheral ID register 2 |
| 0xFEC | WDOGPERIPHID3 | R | 8 | 0x00 | Peripheral ID register 3 |
| 0xFF0 | WDOGPCELLID0 | R | 8 | 0x0D | PrimeCell ID register 0 |
| 0xFF4 | WDOGPCELLID1 | R | 8 | 0xF0 | PrimeCell ID register 1 |
| 0xFF8 | WDOGPCELLID2 | R | 8 | 0x05 | PrimeCell ID register 2 |
| 0xFFC | WDOGPCELLID3 | R | 8 | 0xB1 | PrimeCell ID register 3 |

### 2.2 Register Detailed Descriptions (Side-Effect Registers)

#### 2.2.1 WDOGLOAD (0x00)
- **Access**: Read/Write
- **Width**: 32 bits
- **Reset**: 0xFFFFFFFF
- **Description**: The watchdog reload register sets the initial value for the 32-bit decrementing counter.
- **Read side-effects**: Returns current reload value stored in the register.
- **Write side-effects**: Writing any value to this register updates the reload value. If the timer is enabled, the current counter value is not affected by write to this register until reload occurs (e.g., via WDOGINTCLR or when INTEN transitions from 0 to 1).

#### 2.2.2 WDOGVALUE (0x04)
- **Access**: Read-only
- **Width**: 32 bits
- **Reset**: 0xFFFFFFFF
- **Description**: The current value register provides read access to the current value of the decrementing counter.
- **Read side-effects**: Returns the current counter value which is dynamically changing when the timer is running. This register is volatile.
- **Write side-effects**: No write access allowed. Writes are ignored.

#### 2.2.3 WDOGCONTROL (0x08)
- **Access**: Read/Write
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: The control register configures the watchdog timer operation, including enabling interrupts and reset, and setting the clock divider.
- **Read side-effects**: Returns the current control register value.
- **Write side-effects**: 
  - Bit 0 (INTEN): Enabling INTEN (0→1 transition) starts the timer and reloads the counter from WDOGLOAD register.
  - Bit 1 (RESEN): Controls whether a second timeout generates a reset.
  - Bits 4:2 (step_value): Sets the clock divider value (0=÷1, 1=÷2, 2=÷4, 3=÷8, 4=÷16).

#### 2.2.4 WDOGINTCLR (0x0C)
- **Access**: Write-only
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: The interrupt clear register is used to clear the watchdog interrupt and reload the counter.
- **Write side-effects**: Writing any value to this register clears the interrupt flag and reloads the counter from the value in WDOGLOAD register.
- **Read side-effects**: Read returns undefined value (0x00).

#### 2.2.5 WDOGRIS (0x10)
- **Access**: Read-only
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: The raw interrupt status register shows the raw interrupt status of the watchdog timer without masking.
- **Read side-effects**: Returns current raw interrupt status. This register is volatile and reflects the current interrupt state.
- **Write side-effects**: No write access. Writes are ignored.

#### 2.2.6 WDOGMIS (0x14)
- **Access**: Read-only
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: The masked interrupt status register shows the masked interrupt status (WDOGRIS AND INTEN).
- **Read side-effects**: Returns current masked interrupt status. This register is volatile and reflects the current interrupt state.
- **Write side-effects**: No write access. Writes are ignored.

#### 2.2.7 WDOGLOCK (0xC00)
- **Access**: Read/Write
- **Width**: 32 bits
- **Reset**: 0x00000000
- **Description**: The lock register protects other registers from unauthorized write access.
- **Read side-effects**: Returns lock status (0x0 = unlocked, 0x1 = locked).
- **Write side-effects**: Writing 0x1ACCE551 enables write access to other registers. Writing any other value disables write access to other registers.

#### 2.2.8 WDOGITCR (0xF00)
- **Access**: Read/Write
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: The integration test control register enables or disables integration test mode.
- **Read side-effects**: Returns current integration test mode enable status.
- **Write side-effects**: Bit 0 controls integration test mode. When set to 1, normal timer functionality is disabled and direct control of outputs is enabled via WDOGITOP.

#### 2.2.9 WDOGITOP (0xF04)
- **Access**: Write-only
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: The integration test output register provides direct control of interrupt and reset outputs in test mode.
- **Write side-effects**: In integration test mode, directly controls wdogint (bit 1) and wdogres (bit 0) outputs.
- **Read side-effects**: Read returns undefined value (0x00).

## 3. External Interfaces & Signals

### 3.1 Clock and Reset Signals
- **wclk**: Input, working clock for the timer module
- **wclk_en**: Input, clock enable for timer operation (when high, timer decrements on wclk)
- **wrst_n**: Input, working clock domain reset signal (active low)

### 3.2 Output Signals
- **wdogint**: Output, watchdog interrupt signal (edge-triggered)
  - Asserted when counter reaches zero and INTEN=1
  - Cleared by writing to WDOGINTCLR register
- **wdogres**: Output, watchdog reset signal (edge-triggered)
  - Asserted when counter reaches zero a second time without clearing interrupt AND RESEN=1
  - Cannot be cleared by software, only by system reset

## 4. Register Side-Effects & Behaviors

### 4.1 Timer Operation
- The 32-bit decrementing counter counts down at a rate determined by the step_value field in WDOGCONTROL register
- The counter decrements only when INTEN=1 and wclk_en=1
- The counter value can be read from WDOGVALUE register
- When the counter reaches zero and INTEN=1, an interrupt is generated

### 4.2 Interrupt and Reset Generation
- First timeout: When counter reaches zero and INTEN=1, WDOGRIS[0] is set to 1 and wdogint is asserted
- If interrupt is not cleared and the counter reaches zero again with RESEN=1, wdogres is asserted
- Writing any value to WDOGINTCLR clears the interrupt and reloads the counter from WDOGLOAD

### 4.3 Clock Divider Behavior
- The step_value field in WDOGCONTROL controls the decrement rate:
  - 3'b000: decrement every clock cycle (step = 1)
  - 3'b001: decrement every 2 clock cycles (step = 2)  
  - 3'b010: decrement every 4 clock cycles (step = 4)
  - 3'b011: decrement every 8 clock cycles (step = 8)
  - 3'b100: decrement every 16 clock cycles (step = 16)

### 4.4 Lock Protection Mechanism
- All registers except WDOGLOCK are write-protected when locked
- To unlock: write 0x1ACCE551 to WDOGLOCK
- To lock: write any value other than 0x1ACCE551 to WDOGLOCK

## 5. Device Operational Model

### 5.1 Device States

**State: RESET**
- Entry conditions: wrst_n is low (reset active)
- Observable indicators: All registers in reset state
- Exit conditions: wrst_n goes high
- Test Scenario: Verify registers initialize correctly

**State: IDLE**
- Entry conditions: Device reset complete, INTEN=0 in WDOGCONTROL
- Observable indicators: Counter not decrementing, no interrupts generated
- Exit conditions: INTEN=1 written to WDOGCONTROL
- Test Scenario: Verify counter starts when INTEN set

**State: COUNTING**
- Entry conditions: INTEN=1 in WDOGCONTROL
- Observable indicators: Counter value in WDOGVALUE decrements
- Exit conditions: Counter reaches zero OR INTEN=0 written
- Test Scenario: Verify counter counts down properly

**State: INTERRUPT_PENDING**
- Entry conditions: Counter reaches zero AND INTEN=1 AND RESEN=1
- Observable indicators: WDOGRIS[0]=1, wdogint asserted
- Exit conditions: Write to WDOGINTCLR OR INTEN=0 written
- Test Scenario: Verify interrupt is generated and can be cleared

**State: RESET_PENDING**
- Entry conditions: Counter reaches zero after previous zero with interrupt not cleared AND RESEN=1
- Observable indicators: wdogres asserted
- Exit conditions: System reset occurs
- Test Scenario: Verify reset is generated after second timeout

### 5.2 State Transitions
- [RESET] → [IDLE]: Release of reset
  - Validate: Registers initialize correctly
- [IDLE] → [COUNTING]: Setting INTEN=1 in WDOGCONTROL
  - Validate: Counter begins decrementing
- [COUNTING] → [INTERRUPT_PENDING]: Counter reaches zero AND INTEN=1
  - Validate: WDOGRIS[0]=1, wdogint signal asserted
- [INTERRUPT_PENDING] → [COUNTING]: Write to WDOGINTCLR
  - Validate: WDOGRIS[0]=0, wdogint clears, counter reloads
- [INTERRUPT_PENDING] → [RESET_PENDING]: Counter reaches zero again without clearing interrupt AND RESEN=1
  - Validate: wdogres signal asserted

### 5.3 SW/HW Interaction Flows

**Flow: Basic Timer Operation (maps to Test Scenario 1)**
State Transition: IDLE → COUNTING → INTERRUPT_PENDING

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write value to WDOGLOAD | Value stored | WDOGLOAD shows value |
| 2. Write to WDOGCONTROL with INTEN=1 | Counter starts, reloads from WDOGLOAD | WDOGVALUE starts decrementing |
| 3. Wait for counter to reach zero | Interrupt flag set, wdogint asserted | WDOGRIS[0]=1, WDOGMIS[0]=1 |
| 4. Write to WDOGINTCLR | Interrupt cleared, counter reloads | WDOGRIS[0]=0, WDOGVALUE=WDOGLOAD |

**Flow: Reset Generation (maps to Test Scenario 2)**
State Transition: IDLE → COUNTING → INTERRUPT_PENDING → RESET_PENDING

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write value to WDOGLOAD | Value stored | WDOGLOAD shows value |
| 2. Write to WDOGCONTROL with INTEN=1, RESEN=1 | Counter starts, reloads from WDOGLOAD | WDOGVALUE starts decrementing |
| 3. Allow counter to reach zero (don't clear) | Interrupt flag set, wdogint asserted | WDOGRIS[0]=1, WDOGMIS[0]=1 |
| 4. Allow counter to reach zero again | Reset flag set, wdogres asserted | wdogres=1 (system reset) |

## 6. Functional Requirements

### 6.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter that starts counting when INTEN=1 in WDOGCONTROL.
**FUNC-002**: The timer shall decrement at a rate determined by the step_value field in WDOGCONTROL register.
**FUNC-003**: The timer shall reload from WDOGLOAD register value when INTEN transitions from 0 to 1.
**FUNC-004**: The current counter value shall be readable from WDOGVALUE register.

### 6.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1, device shall set WDOGRIS[0] to 1 and assert wdogint signal.
**FUNC-006**: The WDOGMIS[0] register bit shall reflect the logical AND of WDOGRIS[0] and INTEN bit.
**FUNC-007**: If counter reaches zero again while interrupt asserted and RESEN=1, device shall assert wdogres signal.
**FUNC-008**: Writing any value to WDOGINTCLR shall clear the interrupt and reload the counter from WDOGLOAD.

### 6.3 Register Access Requirements
**FUNC-009**: Register access shall be performed via APB bus interface.
**FUNC-010**: WDOGLOAD register supports read and write operations.
**FUNC-011**: WDOGVALUE register supports read operations only and returns current counter value.
**FUNC-012**: WDOGCONTROL register supports read and write operations with bit-specific functionality.
**FUNC-013**: WDOGINTCLR register supports write operations only.
**FUNC-014**: WDOGRIS register supports read operations only and returns raw interrupt status.
**FUNC-015**: WDOGMIS register supports read operations only and returns masked interrupt status.
**FUNC-016**: WDOGLOCK register supports read and write operations for lock protection.
**FUNC-017**: WDOGITCR register supports read and write operations to control test mode.
**FUNC-018**: WDOGITOP register supports write operations only for test mode output control.

### 6.4 Clock Divider Requirements
**FUNC-019**: Clock divider setting in step_value field shall determine timer decrement rate as follows: 0=÷1, 1=÷2, 2=÷4, 3=÷8, 4=÷16.
**FUNC-020**: The timer shall decrement based on wclk_en signal being high along with the step_value setting.
**FUNC-021**: Invalid step_value settings (5-7) shall result in undefined behavior.

### 6.5 Lock Protection Requirements
**FUNC-022**: When WDOGLOCK register contains 0x1ACCE551, other registers shall be writable.
**FUNC-023**: When WDOGLOCK register contains any value other than 0x1ACCE551, other registers shall be read-only.
**FUNC-024**: Reading WDOGLOCK register shall return 0x0 when unlocked, 0x1 when locked.

### 6.6 Integration Test Mode Requirements
**FUNC-025**: When WDOGITCR[0]=1, device shall enter integration test mode and disable normal timer functionality.
**FUNC-026**: In integration test mode, writing to WDOGITOP shall directly control wdogint (bit 1) and wdogres (bit 0) outputs.
**FUNC-027**: In integration test mode, normal timer counting and interrupt/reset generation shall be disabled.

### 6.7 Identification Requirements
**FUNC-028**: Device shall implement PrimeCell identification registers at 0xFF0-0xFFC.
**FUNC-029**: Device shall implement peripheral identification registers at 0xFD0-0xFEC.

## 7. Register Access Requirements
**REG-001**: WDOGLOAD register allows 32-bit read and write access.
**REG-002**: WDOGVALUE register allows 32-bit read-only access, returns current counter value.
**REG-003**: WDOGCONTROL register allows 32-bit read and write access with individual bit control.
**REG-004**: WDOGINTCLR register allows 32-bit write access, with any value performing interrupt clear.
**REG-005**: WDOGRIS register allows 32-bit read-only access, returns current raw interrupt status.
**REG-006**: WDOGMIS register allows 32-bit read-only access, returns current masked interrupt status.
**REG-007**: WDOGLOCK register allows 32-bit read and write access for lock control.
**REG-008**: WDOGITCR register allows 32-bit read and write access for test mode control.
**REG-009**: WDOGITOP register allows 32-bit write-only access for direct output control.
**REG-010**: Identification registers allow 8-bit read-only access.

## 8. Behavioral Requirements
**BEHAV-001**: When INTEN=0, timer shall remain in idle state without decrementing.
**BEHAV-002**: When INTEN=1 and timer reaches zero, WDOGRIS[0] shall be set to 1.
**BEHAV-003**: When RESEN=0 and timer reaches zero again, no reset shall be generated.
**BEHAV-004**: When wclk_en=0, timer shall not decrement regardless of other settings.
**BEHAV-005**: After writing to WDOGINTCLR, WDOGRIS[0] and WDOGMIS[0] shall become 0.
**BEHAV-006**: The counter shall wrap from 0x00000000 to 0xFFFFFFFF when decremented.
**BEHAV-007**: All registers except WDOGLOCK shall be write-protected when device is locked.
**BEHAV-008**: The wdogint signal shall be edge-triggered, not level-triggered.
**BEHAV-009**: The wdogres signal shall remain asserted until system reset occurs.

## 9. Test Scenarios

### 9.1 Basic Timer Operation Test
**TEST-001**: Verify basic timer countdown functionality.
- Setup: Write small value to WDOGLOAD, set INTEN=1 in WDOGCONTROL
- Action: Verify counter decrements in WDOGVALUE register
- Expected: Counter value decreases, interrupt is generated at zero

**TEST-002**: Verify timer reload functionality.
- Setup: Write value to WDOGLOAD, enable timer with INTEN=1
- Action: Allow counter to count down partially, then set INTEN=0, then INTEN=1 again
- Expected: Counter reloads from WDOGLOAD when INTEN is re-enabled

### 9.2 Interrupt and Reset Generation Test
**TEST-003**: Verify interrupt and reset generation sequence.
- Setup: Write value to WDOGLOAD, set INTEN=1, RESEN=1
- Action: Allow timer to count to zero twice without clearing interrupt
- Expected: First zero generates interrupt, second generates reset

**TEST-004**: Verify interrupt clearing functionality.
- Setup: Configure timer to generate interrupt
- Action: Write to WDOGINTCLR after interrupt occurs
- Expected: Interrupt clears, counter reloads from WDOGLOAD

### 9.3 Lock Protection Test
**TEST-005**: Verify lock protection mechanism.
- Setup: Write 0x1ACCE551 to WDOGLOCK to unlock
- Action: Write to WDOGLOAD (should succeed), then lock, then try again
- Expected: First write succeeds, second write fails (locked)

**TEST-006**: Verify lock status read functionality.
- Setup: Lock and unlock the device
- Action: Read WDOGLOCK register in both states
- Expected: Returns 0x0 when unlocked, 0x1 when locked

### 9.4 Clock Divider Test
**TEST-007**: Verify different clock divider settings.
- Setup: Configure timer with same value but different step_value
- Action: Measure time to reach zero for each setting
- Expected: Larger divider → proportionally longer countdown

### 9.5 Integration Test Mode Test
**TEST-008**: Verify integration test mode functionality.
- Setup: Set WDOGITCR[0]=1 to enable test mode
- Action: Write different values to WDOGITOP register
- Expected: Direct control of wdogint and wdogres outputs

### 9.6 Identification Register Test
**TEST-009**: Verify identification registers.
- Setup: Device is powered on and reset released
- Action: Read all identification registers (WDOGPERIPHID0-7, WDOGPCELLID0-3)
- Expected: Registers return expected ID values matching PrimeCell specification