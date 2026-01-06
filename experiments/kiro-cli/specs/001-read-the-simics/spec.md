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
# Watchdog Timer (WDT) Hardware Specification

## 1. Device Overview

- **Device name**: Watchdog Timer (WDT)
- **Category**: Timer/Counter
- **Function**: 32-bit decrementing counter with interrupt and reset capabilities
- **Base Address**: 0x1000
- **Memory Range**: 0x1000-0x1FFF (4KB address space)
- **Bus Interface**: APB (Advanced Peripheral Bus)

The watchdog timer is a 32-bit decrementing counter that generates an interrupt when it reaches zero, and optionally a reset signal on a second timeout if the interrupt is not cleared. The device implements ARM PrimeCell specification and includes lock protection to prevent unauthorized access to registers.

## 2. Register Map

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00 | WDOGLOAD | R/W | 32 | 0xFFFFFFFF | Watchdog reload value |
| 0x04 | WDOGVALUE | R | 32 | 0xFFFFFFFF | Current counter value |
| 0x08 | WDOGCONTROL | R/W | 32 | 0x00 | Control register with enable and clock divider |
| 0x0C | WDOGINTCLR | W | 32 | 0x00 | Interrupt clear register |
| 0x10 | WDOGRIS | R | 32 | 0x00 | Raw interrupt status |
| 0x14 | WDOGMIS | R | 32 | 0x00 | Masked interrupt status |
| 0xC00 | WDOGLOCK | R/W | 32 | 0x00000000 | Lock register for write protection |
| 0xF00 | WDOGITCR | R/W | 32 | 0x00 | Integration test control register |
| 0xF04 | WDOGITOP | W | 32 | 0x00 | Integration test output register |
| 0xFD0 | WDOGPERIPHID4 | R | 32 | 0x04 | Peripheral ID register 4 |
| 0xFD4 | WDOGPERIPHID5 | R | 32 | 0x00 | Peripheral ID register 5 |
| 0xFD8 | WDOGPERIPHID6 | R | 32 | 0x00 | Peripheral ID register 6 |
| 0xFDC | WDOGPERIPHID7 | R | 32 | 0x00 | Peripheral ID register 7 |
| 0xFE0 | WDOGPERIPHID0 | R | 32 | 0x24 | Peripheral ID register 0 |
| 0xFE4 | WDOGPERIPHID1 | R | 32 | 0xB8 | Peripheral ID register 1 |
| 0xFE8 | WDOGPERIPHID2 | R | 32 | 0x1B | Peripheral ID register 2 |
| 0xFEC | WDOGPERIPHID3 | R | 32 | 0x00 | Peripheral ID register 3 |
| 0xFF0 | WDOGPECELLID0 | R | 32 | 0x0D | PrimeCell ID register 0 |
| 0xFF4 | WDOGPECELLID1 | R | 32 | 0xF0 | PrimeCell ID register 1 |
| 0xFF8 | WDOGPECELLID2 | R | 32 | 0x05 | PrimeCell ID register 2 |
| 0xFFC | WDOGPECELLID3 | R | 32 | 0xB1 | PrimeCell ID register 3 |

### 2.1 Side-Effect Register Descriptions

#### WDOGLOAD Register (Offset: 0x00)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0xFFFFFFFF
- **Description**: Watchdog reload value. Writing to this register loads the counter value when the watchdog is enabled or when clearing an interrupt.
- **Side Effects**: Writing to this register does not immediately affect the counter, but the value will be used when the counter is reloaded (on enabling the watchdog or clearing an interrupt).

#### WDOGVALUE Register (Offset: 0x04)
- **Type**: R (Read-Only)
- **Width**: 32 bits
- **Reset**: 0xFFFFFFFF
- **Description**: Current value of the watchdog counter.
- **Side Effects**: This register has read side-effects as reading it doesn't affect the counter's operation, but provides a snapshot of the current counter value.

#### WDOGCONTROL Register (Offset: 0x08)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: Controls the watchdog timer operation including enable and clock divider settings.
- **Bit Fields**:
  - Bits [31:5]: Reserved
  - Bits [4:2]: step_value (R/W) - Clock divider settings:
    - 000: step_value = 1 (÷1 divider)
    - 001: step_value = 2 (÷2 divider)
    - 010: step_value = 4 (÷4 divider)
    - 011: step_value = 8 (÷8 divider)
    - 100: step_value = 16 (÷16 divider)
  - Bit [1]: RESEN (R/W) - Reset enable bit (1 to enable system reset on second timeout)
  - Bit [0]: INTEN (R/W) - Interrupt enable bit (1 to enable counter and interrupt)
- **Side Effects**: Changing the INTEN bit can reload the counter from WDOGLOAD register when enabled after previously being disabled.

#### WDOGINTCLR Register (Offset: 0x0C)
- **Type**: W (Write-Only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: Writing any value to this register clears the watchdog interrupt and reloads the counter from WDOGLOAD.
- **Side Effects**: Writing any value clears the interrupt status and reloads the counter value.

#### WDOGRIS Register (Offset: 0x10)
- **Type**: R (Read-Only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: Shows the raw interrupt status of the counter.
- **Bit Fields**:
  - Bits [31:1]: Reserved
  - Bit [0]: Raw watchdog interrupt status
- **Side Effects**: This register reflects the internal state of the counter reaching zero, but reading doesn't change the state.

#### WDOGMIS Register (Offset: 0x14)
- **Type**: R (Read-Only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: Shows the masked interrupt status (WDOGRIS & INTEN).
- **Bit Fields**:
  - Bits [31:1]: Reserved
  - Bit [0]: Masked watchdog interrupt status
- **Side Effects**: This register reflects the final interrupt status that is output to the system.

#### WDOGLOCK Register (Offset: 0xC00)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0x00000000
- **Description**: Controls write access to all other registers.
- **Side Effects**:
  - Writing 0x1ACCE551 unlocks other registers for write access
  - Writing any other value locks other registers from write access
  - Reading returns lock status: 0x0 = unlocked, 0x1 = locked

#### WDOGITCR Register (Offset: 0xF00)
- **Type**: R/W
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: Controls integration test mode.
- **Bit Fields**:
  - Bits [31:1]: Reserved
  - Bit [0]: Integration test mode enable (1 = enable test mode, 0 = normal mode)
- **Side Effects**:
  - Writing 1 enables integration test mode
  - Writing 0 returns to normal countdown mode

#### WDOGITOP Register (Offset: 0xF04)
- **Type**: W (Write-Only)
- **Width**: 32 bits
- **Reset**: 0x00
- **Description**: Directly controls watchdog output signals in integration test mode.
- **Bit Fields**:
  - Bits [31:2]: Reserved
  - Bit [1]: WDOGINT output value in test mode
  - Bit [0]: WDOGRES output value in test mode
- **Side Effects**: Writing to this register directly drives the interrupt and reset outputs when in integration test mode.

## 3. External Interfaces & Signals

- **wclk**: Input, 1 bit - Working clock input
- **wclk_en**: Input, 1 bit - Clock enable for the working clock domain
- **wrst_n**: Input, 1 bit - Reset signal for the working clock domain (active low)
- **wdogint**: Output, 1 bit - Watchdog interrupt signal, asserted when timeout occurs
- **wdogres**: Output, 1 bit - Watchdog reset signal, asserted when second timeout occurs without interrupt clearing

## 4. Register Side-Effects & Behaviors

### 4.1 Counter/Timer Behaviors
- The watchdog implements a 32-bit decrementing counter that decrements based on the step_value clock divider
- When the counter reaches zero and INTEN is set, wdogint is asserted
- If RESEN is set and the counter reaches zero again without clearing the interrupt, wdogres is asserted
- Writing to WDOGINTCLR clears the interrupt and reloads the counter from WDOGLOAD

### 4.2 State Machine Behaviors
- Normal operation: Counter counts down based on clock divider
- Interrupt pending: When counter reaches zero and INTEN=1, interrupt is asserted
- Reset pending: When counter reaches zero again without clearing interrupt and RESEN=1, reset is asserted
- Lock protection: WDOGLOCK controls write access to other registers
- Test mode: WDOGITCR enables direct control of output signals

### 4.3 External Interface Behaviors
- wdogint: Edge-triggered interrupt signal that remains asserted until cleared by writing to WDOGINTCLR
- wdogres: Reset signal that remains asserted until system is reset
- wclk_en: Gates the counter operation when low

### 4.4 Trigger → Action → Dependencies
1. Counter reaches zero → Assert wdogint → Depends on INTEN=1
2. Counter reaches zero again → Assert wdogres → Depends on RESEN=1 and interrupt still asserted
3. Write to WDOGINTCLR → Clear interrupt and reload counter → Depends on WDOGLOCK=unlocked
4. Write 0x1ACCE551 to WDOGLOCK → Unlock other registers → No dependencies
5. Write other value to WDOGLOCK → Lock other registers → No dependencies
6. Write 1 to WDOGITCR[0] → Enter integration test mode → No dependencies
7. Write to WDOGITOP → Directly control outputs → Depends on test mode enabled

## 5. Device Operational Model

### 5.1 Device States

**RESET**: Initial state after system reset
- Entry conditions: wrst_n or prst_n is low
- Observable indicators: All registers at reset values
- Exit conditions: Reset signal returns high
- Test Scenario: Verify all registers return to reset values

**IDLE**: State when timer is not enabled
- Entry conditions: WDOGCONTROL[0] (INTEN) is 0
- Observable indicators: Counter value is static
- Exit conditions: INTEN bit set to 1
- Test Scenario: Verify counter doesn't decrement when disabled

**COUNTING**: State when timer is actively counting down
- Entry conditions: INTEN=1 in WDOGCONTROL
- Observable indicators: WDOGVALUE register value decreases over time
- Exit conditions: Counter reaches zero
- Test Scenario: Verify counter decrements at proper rate

**INTERRUPT_PENDING**: State when counter has reached zero and interrupt is asserted
- Entry conditions: Counter reaches zero and INTEN=1
- Observable indicators: WDOGRIS[0]=1, WDOGMIS[0]=1, wdogint output asserted
- Exit conditions: Write to WDOGINTCLR or RESEN=1 and counter reaches zero again
- Test Scenario: Verify interrupt is generated when counter reaches zero

**RESET_PENDING**: State when second timeout occurs without clearing interrupt
- Entry conditions: Counter reaches zero with interrupt still pending and RESEN=1
- Observable indicators: wdogres output asserted
- Exit conditions: System reset occurs
- Test Scenario: Verify reset is generated on second timeout

### 5.2 State Transitions
- [IDLE] → [COUNTING]: When INTEN bit transitions from 0 to 1
  - Validate: Counter starts decrementing from WDOGLOAD value

- [COUNTING] → [INTERRUPT_PENDING]: When counter reaches zero and INTEN=1
  - Validate: WDOGRIS[0] and WDOGMIS[0] become 1, wdogint asserted

- [INTERRUPT_PENDING] → [COUNTING]: When WDOGINTCLR is written
  - Validate: Interrupt is cleared, counter reloads from WDOGLOAD

- [INTERRUPT_PENDING] → [RESET_PENDING]: When counter reaches zero again and RESEN=1
  - Validate: wdogres output is asserted

### 5.3 SW/HW Interaction Flows

**Flow: Basic Timer Operation** (maps to Test Scenario 1)
State Transition: IDLE → COUNTING → INTERRUPT_PENDING

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write value to WDOGLOAD | Value stored in register | WDOGLOAD shows written value |
| 2. Set INTEN=1 in WDOGCONTROL | Timer starts counting | WDOGVALUE shows decreasing values |
| 3. Wait for counter to reach zero | Counter decrements, interrupt generated | WDOGRIS[0]=1, WDOGMIS[0]=1, wdogint asserted |

**Flow: Interrupt Clear Operation** (maps to Test Scenario 2)
State Transition: INTERRUPT_PENDING → COUNTING

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Observe interrupt status | Counter has reached zero | WDOGRIS[0]=1, WDOGMIS[0]=1 |
| 2. Write to WDOGINTCLR | Interrupt cleared, counter reloaded | wdogint deasserted, WDOGVALUE shows reload value |

**Flow: Lock Protection** (maps to Test Scenario 3)
State Transition: N/A

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write 0x1ACCE551 to WDOGLOCK | Other registers unlocked | WDOGLOCK reads as 0x0 |
| 2. Write to other registers | Registers accept writes | Register values update |
| 3. Write different value to WDOGLOCK | Other registers locked | WDOGLOCK reads as 0x1 |

## 6. Functional Requirements

### 6.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter.
**FUNC-002**: The timer shall decrement at a rate determined by the step_value in WDOGCONTROL register.
**FUNC-003**: The step_value field shall support 5 different clock divider settings (÷1, ÷2, ÷4, ÷8, ÷16).
**FUNC-004**: The WDOGVALUE register shall always contain the current value of the decrementing counter.

### 6.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1, device shall assert wdogint.
**FUNC-006**: The wdogint signal shall remain asserted until cleared by writing to WDOGINTCLR.
**FUNC-007**: If counter reaches zero again while interrupt asserted and RESEN=1, device shall assert wdogres.
**FUNC-008**: The wdogres signal shall remain asserted until system reset occurs.
**FUNC-009**: Writing to WDOGINTCLR shall clear the interrupt and reload the counter from WDOGLOAD.

### 6.3 Register Access Requirements
**FUNC-010**: Register access shall be performed via APB bus interface.
**FUNC-011**: All registers except WDOGLOCK shall be write-protected when locked.
**FUNC-012**: WDOGLOAD register supports read and write operations.
**FUNC-013**: WDOGVALUE register supports read operations only and reflects current counter value.
**FUNC-014**: WDOGCONTROL register supports read and write operations for controlling timer.
**FUNC-015**: WDOGINTCLR register supports write operations only for clearing interrupt.
**FUNC-016**: WDOGRIS register supports read operations only and shows raw interrupt status.
**FUNC-017**: WDOGMIS register supports read operations only and shows masked interrupt status.
**FUNC-018**: WDOGLOCK register controls write access to all other registers.
**FUNC-019**: WDOGITCR register controls integration test mode.
**FUNC-020**: WDOGITOP register supports write operations only in test mode to control outputs.

### 6.4 Clock Divider Requirements
**FUNC-021**: Clock divider setting in WDOGCONTROL[4:2] shall determine timer decrement rate.
**FUNC-022**: The step_value 000 shall configure the timer to decrement every clock cycle (÷1).
**FUNC-023**: The step_value 001 shall configure the timer to decrement every 2 clock cycles (÷2).
**FUNC-024**: The step_value 010 shall configure the timer to decrement every 4 clock cycles (÷4).
**FUNC-025**: The step_value 011 shall configure the timer to decrement every 8 clock cycles (÷8).
**FUNC-026**: The step_value 100 shall configure the timer to decrement every 16 clock cycles (÷16).

### 6.5 Integration Test Mode Requirements
**FUNC-027**: When WDOGITCR[0]=1, device shall enter integration test mode.
**FUNC-028**: In test mode, writing to WDOGITOP shall directly control wdogint and wdogres outputs.
**FUNC-029**: In test mode, WDOGITOP[1] shall control wdogint output directly.
**FUNC-030**: In test mode, WDOGITOP[0] shall control wdogres output directly.

### 6.6 Identification Requirements
**FUNC-031**: Device shall implement all PrimeCell identification registers (WDOGPECELLID0-3).
**FUNC-032**: Device shall implement all peripheral identification registers (WDOGPERIPHID0-7).

## 7. Register Access Requirements
**REG-001**: WDOGLOAD register supports read and write operations with 32-bit width.
**REG-002**: WDOGVALUE register supports read operations only with 32-bit width.
**REG-003**: WDOGCONTROL register supports read and write operations with 32-bit width.
**REG-004**: WDOGINTCLR register supports write operations only with 32-bit width.
**REG-005**: WDOGRIS register supports read operations only with 32-bit width.
**REG-006**: WDOGMIS register supports read operations only with 32-bit width.
**REG-007**: WDOGLOCK register supports read and write operations with 32-bit width.
**REG-008**: WDOGITCR register supports read and write operations with 32-bit width.
**REG-009**: WDOGITOP register supports write operations only with 32-bit width.
**REG-010**: All ID registers support read operations only.

## 8. Behavioral Requirements
**BEHAV-001**: When INTEN=0, timer shall not decrement regardless of other settings.
**BEHAV-002**: When INTEN=1 and timer reaches zero, WDOGRIS[0] shall be set to 1.
**BEHAV-003**: WDOGMIS[0] shall always equal WDOGRIS[0] AND INTEN.
**BEHAV-004**: When WDOGLOCK contains 0x1ACCE551, other registers shall be writable.
**BEHAV-005**: When WDOGLOCK contains any value other than 0x1ACCE551, other registers shall not be writable.
**BEHAV-006**: When RESEN=1, wdogres shall be generated on second timeout without interrupt clearing.
**BEHAV-007**: Writing any value to WDOGINTCLR shall clear WDOGRIS[0] and WDOGMIS[0].
**BEHAV-008**: When INTEN transitions from 0 to 1, counter shall reload from WDOGLOAD value.
**BEHAV-009**: When the device is reset, all registers shall return to their reset values.
**BEHAV-010**: When in integration test mode, normal timer operation shall be suspended.

## 9. Test Scenarios

### 9.1 Basic Timer Operation Test
**TEST-001**: Verify basic timer countdown functionality.
- Setup: Write small value to WDOGLOAD, set INTEN=1 in WDOGCONTROL
- Action: Verify counter decrements in WDOGVALUE register
- Expected: Counter value decreases, interrupt is generated at zero

### 9.2 Interrupt and Reset Generation Test
**TEST-002**: Verify interrupt and reset generation sequence.
- Setup: Write value to WDOGLOAD, set INTEN=1, RESEN=1
- Action: Allow timer to count to zero twice without clearing interrupt
- Expected: First zero generates interrupt, second generates reset

### 9.3 Lock Protection Test
**TEST-003**: Verify lock protection mechanism.
- Setup: Write 0x1ACCE551 to WDOGLOCK to unlock
- Action: Write to WDOGLOAD (should succeed), then lock, then try again
- Expected: First write succeeds, second write fails (locked)

### 9.4 Clock Divider Test
**TEST-004**: Verify different clock divider settings.
- Setup: Configure timer with same value but different step_value
- Action: Measure time to reach zero for each setting
- Expected: Larger divider → proportionally longer countdown

### 9.5 Integration Test Mode Test
**TEST-005**: Verify integration test mode functionality.
- Setup: Set WDOGITCR[0]=1 to enable test mode
- Action: Write different values to WDOGITOP register
- Expected: Direct control of wdogint and wdogres outputs

### 9.6 Interrupt Clear Test
**TEST-006**: Verify interrupt clearing functionality.
- Setup: Configure timer to generate interrupt
- Action: Allow interrupt to occur, then write to WDOGINTCLR
- Expected: Interrupt is cleared, counter reloads

### 9.7 Reset Generation Test
**TEST-007**: Verify reset generation when interrupt not cleared.
- Setup: Set RESEN=1, configure timer for interrupt
- Action: Allow timer to reach zero twice without clearing interrupt
- Expected: First timeout generates interrupt, second generates reset

### 9.8 Register Read/Write Test
**TEST-008**: Verify all register read/write functionality.
- Setup: N/A
- Action: Read and write to all accessible registers
- Expected: Register values read back as written (where allowed)

### 9.9 ID Registers Test
**TEST-009**: Verify all ID registers return expected values.
- Setup: N/A
- Action: Read all ID registers
- Expected: ID registers return expected PrimeCell and peripheral IDs

### 9.10 Counter Reload Test
**TEST-010**: Verify counter reload behavior.
- Setup: N/A
- Action: Write to WDOGLOAD, disable/enable timer, clear interrupt
- Expected: Counter reloads in all appropriate scenarios