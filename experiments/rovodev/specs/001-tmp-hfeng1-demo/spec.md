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

**Device Name**: Simics Watchdog Timer (WDT)
**Base Address**: 0x1000 (mapped to QSP-x86 platform memory space)
**Category**: Timer/Counter
**Description**: A 32-bit ARM PrimeCell compatible watchdog timer device that implements a decrementing counter with configurable timeout periods, interrupt generation, and reset functionality.

## 2. Register Map

### 2.1 Register Map Overview Table

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00 | WDOGLOAD | R/W | 32 | 0xFFFFFFFF | Watchdog load value - sets the counter reload value |
| 0x04 | WDOGVALUE | R | 32 | 0xFFFFFFFF | Watchdog current value - read-only current counter value |
| 0x08 | WDOGCONTROL | R/W | 32 | 0x00000000 | Watchdog control register - enables interrupt/reset and sets clock divider |
| 0x0C | WDOGINTCLR | W | 32 | 0x00000000 | Watchdog interrupt clear register - clears interrupt and reloads counter |
| 0x10 | WDOGRIS | R | 32 | 0x00000000 | Watchdog raw interrupt status register - shows unmasked interrupt status |
| 0x14 | WDOGMIS | R | 32 | 0x00000000 | Watchdog masked interrupt status register - shows masked interrupt status |
| 0xC00 | WDOGLOCK | R/W | 32 | 0x00000000 | Watchdog lock register - protects registers from unintended writes |
| 0xF00 | WDOGITCR | R/W | 32 | 0x00000000 | Watchdog integration test control register - enables test mode |
| 0xF04 | WDOGITOP | W | 32 | 0x00000000 | Watchdog integration test output register - controls outputs in test mode |
| 0xFD0 | WDOGPERIPHID4 | R | 32 | 0x00000004 | Watchdog peripheral ID register 4 |
| 0xFD4 | WDOGPERIPHID5 | R | 32 | 0x00000000 | Watchdog peripheral ID register 5 |
| 0xFD8 | WDOGPERIPHID6 | R | 32 | 0x00000000 | Watchdog peripheral ID register 6 |
| 0xFDC | WDOGPERIPHID7 | R | 32 | 0x00000000 | Watchdog peripheral ID register 7 |
| 0xFE0 | WDOGPERIPHID0 | R | 32 | 0x00000024 | Watchdog peripheral ID register 0 |
| 0xFE4 | WDOGPERIPHID1 | R | 32 | 0x000000B8 | Watchdog peripheral ID register 1 |
| 0xFE8 | WDOGPERIPHID2 | R | 32 | 0x0000001B | Watchdog peripheral ID register 2 |
| 0xFEC | WDOGPERIPHID3 | R | 32 | 0x00000000 | Watchdog peripheral ID register 3 |
| 0xFF0 | WDOGPCELLID0 | R | 32 | 0x0000000D | Watchdog PrimeCell ID register 0 |
| 0xFF4 | WDOGPCELLID1 | R | 32 | 0x000000F0 | Watchdog PrimeCell ID register 1 |
| 0xFF8 | WDOGPCELLID2 | R | 32 | 0x00000005 | Watchdog PrimeCell ID register 2 |
| 0xFFC | WDOGPCELLID3 | R | 32 | 0x000000B1 | Watchdog PrimeCell ID register 3 |

### 2.2 Detailed Register Descriptions (Side-Effect Registers)

#### WDOGLOAD (0x00) - Watchdog Load Register
**Type**: R/W | **Width**: 32 bits | **Reset**: 0xFFFFFFFF
- **Purpose**: Sets the 32-bit reload value for the watchdog counter
- **Side Effects**: Writing to this register reloads the current counter value if the watchdog is enabled and was previously disabled

#### WDOGVALUE (0x04) - Watchdog Value Register
**Type**: R | **Width**: 32 bits | **Reset**: 0xFFFFFFFF
- **Purpose**: Returns the current value of the watchdog counter
- **Side Effects**: None (read-only counter value)

#### WDOGCONTROL (0x08) - Watchdog Control Register
**Type**: R/W | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Controls the watchdog timer enable, interrupt enable, reset enable, and clock divider
- **Bit Fields**:
  - Bits [31:5]: Reserved (read as 0)
  - Bits [4:2]: step_value (R/W) - Clock divider selection
    - 000: Divide by 1 (step_value = 1)
    - 001: Divide by 2 (step_value = 2)
    - 010: Divide by 4 (step_value = 4)
    - 011: Divide by 8 (step_value = 8)
    - 100: Divide by 16 (step_value = 16)
  - Bit [1]: RESEN (R/W) - Reset enable (1=enable watchdog reset output)
  - Bit [0]: INTEN (R/W) - Interrupt enable (1=enable counter and interrupt)
- **Side Effects**: Writing to INTEN bit can trigger counter reload from WDOGLOAD when enabled after being disabled

#### WDOGINTCLR (0x0C) - Watchdog Interrupt Clear Register
**Type**: W | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Writing any value clears the watchdog interrupt and reloads the counter from WDOGLOAD
- **Side Effects**: 
  - Clears the interrupt flag
  - Reloads the counter value from WDOGLOAD register
  - Affects WDOGRIS and WDOGMIS register values

#### WDOGRIS (0x10) - Watchdog Raw Interrupt Status Register
**Type**: R | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Shows the raw interrupt status from the counter (not masked by control register)
- **Bit Fields**:
  - Bits [31:1]: Reserved (read as 0)
  - Bit [0]: raw watchdog interrupt (R) - Raw interrupt status from the counter
- **Side Effects**: None (read-only status register)

#### WDOGMIS (0x14) - Watchdog Masked Interrupt Status Register
**Type**: R | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Shows the masked interrupt status (WDOGRIS & INTEN)
- **Bit Fields**:
  - Bits [31:1]: Reserved (read as 0)
  - Bit [0]: watchdog interrupt (R) - Masked interrupt status (WDOGRIS & INTEN)
- **Side Effects**: None (read-only status register)

#### WDOGLOCK (0xC00) - Watchdog Lock Register
**Type**: R/W | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Controls write access to other registers for protection against unintended changes
- **Side Effects**:
  - Writing 0x1ACCE551: Unlocks other registers for write access
  - Writing any other value: Locks other registers, preventing writes
  - Reading returns lock status: 0x0 = unlocked, 0x1 = locked
  - Affects write access to all other registers

#### WDOGITCR (0xF00) - Watchdog Integration Test Control Register
**Type**: R/W | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Controls the integration test mode for direct signal control
- **Bit Fields**:
  - Bits [31:1]: Reserved (read as 0)
  - Bit [0]: Integration test mode enable (R/W)
    - 1 = Enter integration test mode
    - 0 = Normal decrementing counter mode
- **Side Effects**: 
  - When set to 1, allows direct control of wdogint and wdogres outputs via WDOGITOP
  - When set to 0, returns to normal timer operation

#### WDOGITOP (0xF04) - Watchdog Integration Test Output Register
**Type**: W | **Width**: 32 bits | **Reset**: 0x00000000
- **Purpose**: Controls watchdog outputs in integration test mode
- **Bit Fields**:
  - Bits [31:2]: Reserved 
  - Bit [1]: Integration test mode WDOGINT value (W) - Controls wdogint output in test mode
  - Bit [0]: Integration test mode WDOGRES value (W) - Controls wdogres output in test mode
- **Side Effects**: Directly drives wdogint and wdogres outputs when integration test mode is enabled

## 3. External Interfaces & Signals

### 3.1 Clock and Reset Signals
- **wclk**: Working clock input (input, 1-bit) - Main working clock for the timer
- **wclk_en**: Clock enable signal (input, 1-bit) - Enables the timer when high
- **wrst_n**: Working clock domain reset (input, 1-bit) - Asynchronous active-low reset for working clock domain
- **prst_n**: APB bus reset (input, 1-bit) - Asynchronous active-low reset for APB interface

### 3.2 Interrupt and Reset Output Signals
- **wdogint**: Watchdog interrupt output (output, 1-bit) - Edge-triggered interrupt signal, generated when counter reaches zero and INTEN=1
- **wdogres**: Watchdog reset output (output, 1-bit) - Reset signal, generated when counter reaches zero again while interrupt is still asserted and RESEN=1

### 3.3 APB Bus Interface Signals
- **paddr**: APB address (input) - Address bus for register access
- **pwdata**: APB write data (input) - Write data bus
- **pwrite**: APB write enable (input) - Write/Read control (1=write, 0=read)
- **psel**: APB select (input) - Device selection signal
- **penable**: APB enable (input) - Second phase of APB transaction
- **prdata**: APB read data (output) - Read data bus
- **pready**: APB ready (output) - Transaction complete signal

## 4. Register Side-Effects & Behaviors

### 4.1 Counter/Timer Behaviors
- The watchdog implements a 32-bit decrementing counter that decrements at intervals determined by the step_value field
- The counter decrements on wclk rising edges when wclk_en is high
- When the counter reaches zero and INTEN is set, it triggers the wdogint signal
- If the interrupt is not cleared and the counter reaches zero again while RESEN is set, it triggers the wdogres reset signal

### 4.2 Read Side-Effects
- WDOGVALUE register: Returns current counter value without affecting the counter operation
- WDOGRIS register: Returns raw interrupt status without clearing the interrupt flag
- WDOGMIS register: Returns masked interrupt status without clearing the interrupt flag
- WDOGLOCK register: Returns lock status value based on previous writes to this register

### 4.3 Write Side-Effects
- WDOGLOAD register: Reloads the counter value (only when enabled after previously being disabled)
- WDOGINTCLR register: Clears interrupt flag and reloads counter from WDOGLOAD value
- WDOGCONTROL register: Writing INTEN bit can cause counter reload when transitioning from disabled to enabled
- WDOGITCR register: Switches between normal operation and integration test mode
- WDOGITOP register: Directly controls wdogint and wdogres signals in test mode
- WDOGLOCK register: Controls write access to all other registers

### 4.4 Cross-Register Dependencies
- WDOGMIS[0] = WDOGRIS[0] AND WDOGCONTROL[0] (INTEN bit)
- WDOGINTCLR operation affects WDOGRIS and WDOGMIS register values
- WDOGITCR[0] enables control of wdogint and wdogres through WDOGITOP register
- WDOGLOCK value controls access to all other writable registers

## 5. Device Operational Model

### 5.1 Device States

**State: RESET**
- Entry conditions: prst_n or wrst_n is low
- Observable indicators: All registers in reset state, wdogint and wdogres inactive
- Exit conditions: Both reset signals go high
- Test Scenario: Verify reset operation and register values

**State: IDLE_LOCKED**
- Entry conditions: Device is out of reset and WDOGLOCK does not contain 0x1ACCE551
- Observable indicators: WDOGLOCK read returns non-zero, writes to other registers are ignored
- Exit conditions: Write 0x1ACCE551 to WDOGLOCK register
- Test Scenario: Verify lock protection mechanism

**State: IDLE_UNLOCKED**
- Entry conditions: Device is out of reset and WDOGLOCK contains 0x1ACCE551
- Observable indicators: WDOGLOCK read returns 0x0, writes to other registers are accepted
- Exit conditions: Write any non-0x1ACCE551 value to WDOGLOCK or disable timer
- Test Scenario: Verify register write access after unlocking

**State: COUNTING**
- Entry conditions: INTEN bit in WDOGCONTROL is set to 1 and timer is not in integration test mode
- Observable indicators: WDOGVALUE register decrements, no interrupts generated yet
- Exit conditions: Counter reaches zero or timer disabled
- Test Scenario: Verify timer decrementing behavior

**State: INTERRUPT_PENDING**
- Entry conditions: Counter reaches zero and INTEN=1 and RESEN=0, or counter reached zero again after interrupt was asserted but not cleared
- Observable indicators: WDOGRIS[0] and WDOGMIS[0] are high, wdogint signal asserted
- Exit conditions: Write to WDOGINTCLR to clear interrupt
- Test Scenario: Verify interrupt generation and clearing

**State: INTEGRATION_TEST**
- Entry conditions: WDOGITCR[0] is set to 1
- Observable indicators: Direct control of outputs possible, counter operation disabled
- Exit conditions: Write 0 to WDOGITCR[0]
- Test Scenario: Verify integration test mode functionality

### 5.2 State Transitions

**[RESET] → [IDLE_LOCKED]**: After reset deassertion and default lock state
- Validate: WDOGLOCK returns 0x0 (unlocked in reset), other registers in reset state

**[IDLE_LOCKED] → [IDLE_UNLOCKED]**: When 0x1ACCE551 is written to WDOGLOCK
- Validate: WDOGLOCK read returns 0x0, writes to other registers now succeed

**[IDLE_UNLOCKED] → [IDLE_LOCKED]**: When any value other than 0x1ACCE551 is written to WDOGLOCK
- Validate: WDOGLOCK read returns 0x1, writes to other registers now fail

**[IDLE_UNLOCKED] → [COUNTING]**: When INTEN bit in WDOGCONTROL is set to 1
- Validate: WDOGVALUE begins decrementing, WDOGMIS[0] remains low

**[COUNTING] → [INTERRUPT_PENDING]**: When counter reaches zero and INTEN=1
- Validate: WDOGRIS[0] and WDOGMIS[0] become high, wdogint signal asserted

**[INTERRUPT_PENDING] → [COUNTING]**: When WDOGINTCLR register is written
- Validate: WDOGVALUE reloads from WDOGLOAD, WDOGRIS[0] and WDOGMIS[0] become low

**[COUNTING] → [IDLE_UNLOCKED]**: When INTEN bit in WDOGCONTROL is set to 0
- Validate: WDOGVALUE stops decrementing

### 5.3 SW/HW Interaction Flows

**Flow: Basic Timer Operation** (maps to Test Scenario 1)
State Transition: IDLE_UNLOCKED → COUNTING → INTERRUPT_PENDING

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write 0x1ACCE551 to WDOGLOCK | Register unlocked | WDOGLOCK returns 0x0 |
| 2. Write 0x1000 to WDOGLOAD | Load value stored | WDOGLOAD=0x1000 |
| 3. Write 0x1 to WDOGCONTROL[INTEN] | Timer starts counting | WDOGVALUE begins decrementing |
| 4. Wait for counter to reach zero | Counter continues decrementing | WDOGVALUE approaches 0 |

**Flow: Interrupt Generation and Clearing** (maps to Test Scenario 2)
State Transition: COUNTING → INTERRUPT_PENDING → COUNTING

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Wait for interrupt condition | Counter reaches zero | WDOGRIS[0] and WDOGMIS[0] set |
| 2. Verify WDOGMIS[0] = 1 | Interrupt asserted | wdogint signal active |
| 3. Write any value to WDOGINTCLR | Interrupt cleared, counter reloaded | WDOGMIS[0] becomes 0 |

**Flow: Lock Protection** (maps to Test Scenario 3)
State Transition: IDLE_UNLOCKED ↔ IDLE_LOCKED

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write 0x1ACCE551 to WDOGLOCK | Other registers unlocked | WDOGLOCK returns 0x0, other writes succeed |
| 2. Write different value to WDOGPERIPHID0 | Register write ignored | WDOGPERIPHID0 unchanged |
| 3. Write different value to WDOGLOCK | Register access locked | WDOGLOCK returns 0x1, other writes fail |

## 6. Functional Requirements

### 6.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter that decrements when INTEN is enabled and wclk_en is high.
**FUNC-002**: The timer shall decrement at a rate determined by the step_value field in WDOGCONTROL register.
**FUNC-003**: The timer shall reload with the value from WDOGLOAD when enabled after previously being disabled.
**FUNC-004**: The WDOGVALUE register shall always return the current value of the decrementing counter.

### 6.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1, device shall assert wdogint signal and set WDOGRIS[0] and WDOGMIS[0] to 1.
**FUNC-006**: When interrupt is asserted and timer reaches zero again without being cleared, device shall assert wdogres signal if RESEN=1.
**FUNC-007**: Writing to WDOGINTCLR register shall clear the interrupt flag and reload the counter from WDOGLOAD.
**FUNC-008**: The WDOGMIS register shall return the logical AND of WDOGRIS[0] and WDOGCONTROL[0] (INTEN bit).

### 6.3 Register Access Requirements
**FUNC-009**: Register access shall be performed via APB bus interface with proper address decoding.
**FUNC-010**: All registers except WDOGLOCK shall be write-protected when WDOGLOCK does not contain 0x1ACCE551.
**FUNC-011**: Writing 0x1ACCE551 to WDOGLOCK shall enable write access to protected registers.
**FUNC-012**: WDOGVALUE register shall be read-only and return current timer value without side effects.

### 6.4 Clock Divider Requirements
**FUNC-013**: The step_value field in WDOGCONTROL shall control the timer decrement rate with 5 valid settings (÷1, ÷2, ÷4, ÷8, ÷16).
**FUNC-014**: Clock divider setting shall determine timer decrement rate where larger values cause slower decrementing.

### 6.5 Integration Test Mode Requirements
**FUNC-015**: When WDOGITCR[0]=0, device shall operate in normal timer mode.
**FUNC-016**: When WDOGITCR[0]=1, device shall enter integration test mode allowing direct control of outputs.
**FUNC-017**: In integration test mode, WDOGITOP register shall directly control wdogint and wdogres output signals.

### 6.6 Identification Requirements
**FUNC-018**: Device shall implement WDOGPERIPHID0-7 registers containing ARM PrimeCell peripheral identification values.
**FUNC-019**: Device shall implement WDOGPCELLID0-3 registers containing ARM PrimeCell component identification values.

## 7. Register Access Requirements
**REG-001**: WDOGLOAD register supports read and write operations and returns the current load value.
**REG-002**: WDOGVALUE register supports read-only operations and returns the current decrementing counter value.
**REG-003**: WDOGCONTROL register supports read and write operations with bit-field access control.
**REG-004**: WDOGINTCLR register supports write-only operations that trigger side effects on read access.
**REG-005**: WDOGRIS register supports read-only operations and returns the raw interrupt status.
**REG-006**: WDOGMIS register supports read-only operations and returns the masked interrupt status.
**REG-007**: WDOGLOCK register supports read and write operations with special lock/unlock functionality.
**REG-008**: WDOGITCR register supports read and write operations for test mode control.
**REG-009**: WDOGITOP register supports write-only operations for direct output control in test mode.

## 8. Behavioral Requirements
**BEHAV-001**: When INTEN=0, timer shall not decrement and no interrupts shall be generated.
**BEHAV-002**: When INTEN=1 and timer reaches zero, WDOGRIS[0] shall be set to 1 and wdogint signal asserted.
**BEHAV-003**: When wdogres signal is asserted, it shall remain active until system reset occurs.
**BEHAV-004**: The wdogint signal shall remain asserted until cleared by writing to WDOGINTCLR register.
**BEHAV-005**: When the watchdog timer is locked, any write attempts to protected registers shall be ignored.
**BEHAV-006**: The timer shall only decrement when both INTEN=1 and wclk_en=1.

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

### 9.6 Register Access Test
**TEST-006**: Verify all registers can be read with correct reset values.
- Setup: Device in reset state
- Action: Read all registers
- Expected: All registers return expected reset values

### 9.7 Interrupt Status Test
**TEST-007**: Verify interrupt status register behavior.
- Setup: Configure timer to generate interrupt
- Action: Check values of WDOGRIS and WDOGMIS registers
- Expected: WDOGRIS shows raw status, WDOGMIS shows masked status

### 9.8 Counter Reload Test
**TEST-008**: Verify counter reload functionality.
- Setup: Set timer with small value
- Action: Write to WDOGINTCLR when interrupt pending
- Expected: Counter reloads from WDOGLOAD value, interrupt cleared