---
description: Create hardware IP functional specification and register description from IP hardware specification document.
---

User input: $ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

## Workflow Overview

1. **Step 1**: Run setup script (creates branch and spec file)
2. **Step 2**: Parse hardware specification (extract device info, registers, behaviors)
3. **Step 3**: Generate spec.md
4. **Step 4**: Generate IP-XACT register XML
5. **Step 5**: Git commit
6. **Step 6**: Report completion

---

### Step 1: Run Feature Setup Script

Run `.specify/scripts/bash/create-new-feature.sh --json "$ARGUMENTS"` from repo root → parse JSON for BRANCH_NAME, SPEC_FILE. Use absolute paths.

### Step 2: Parse Hardware Specification

#### 2.1 Device Overview
Extract: Device name, base address, category (Timer/Counter, UART, DMA, Interrupt Controller, GPIO, Memory Controller, Custom)

#### 2.2 Register Map (Two-Part Structure)

**Part A: Register Map Overview Table**
Create a COMPACT summary table for ALL registers:
| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|

**Part B: Detailed Descriptions (ONLY for Side-Effect Registers)**
Only include detailed bit field tables for registers with:
- Read side-effects (value changes on read)
- Write side-effects (triggers actions beyond storing value)
- Cross-register dependencies
- Special access behaviors (lock protection, clear-on-read)

**Skip detailed descriptions for**:
- Read-only ID/version registers
- Simple R/W registers without side-effects
- Reserved registers

**Access Type Mapping**:
| HW Spec | IP-XACT | Notes |
|---------|---------|-------|
| RO | `read_only` | Read returns stored value |
| RW | `read_write` | Normal read/write |
| WO | `write_only` | Read returns 0 or undefined |
| W1C | `read_write` | Write-1-to-clear bits |
| RW1S/RW1C | `read_write` | Custom write behavior |

#### 2.3 I/O Ports & Signals
Extract external interfaces: interrupts, GPIO, clock, bus signals (name, direction, width, description)

#### 2.4 Register Side-Effects & Behaviors
**Categories**:
- Counter/Timer: overflow, compare match, periodic events
- State Machine: transitions, assertions, mode changes
- External Interface: signals, interrupts, pin state
- Internal State: register dependencies, cache, flags

**Document format**: Trigger → Action → Dependencies

**Include in register descriptions**:
- Read side-effects (e.g., "Read clears interrupt flag")
- Write side-effects (e.g., "Write reloads counter from LOAD register")
- Cross-register dependencies (e.g., "Write ignored if LOCK != 0x1ACCE551")

#### 2.5 Device Operational Model (CRITICAL for spec.md)

**⚠️ MANDATORY**: Document device states, transitions, and SW/HW interaction flows.

**Device States**: Identify all operational states (e.g., RESET, IDLE, COUNTING, INTERRUPT_PENDING)
```
State: [STATE_NAME]
- Entry conditions: [How to enter this state]
- Observable indicators: [Register values, signal states]
- Exit conditions: [How to leave this state]
- Test Scenario: [Which scenario validates this state]
```

**State Transitions**: Document all valid transitions
```
[SOURCE_STATE] → [TARGET_STATE]: Trigger condition
- Validate: [Observable change to verify transition]
```

**SW/HW Interaction Flows**: Document complete operational sequences
```
Flow: [Flow Name] (maps to Test Scenario X)
State Transition: [STATE1] → [STATE2] → [STATE3]

| Software Actions | Hardware Responses | Observable State |
|------------------|-------------------|------------------|
| 1. Write X to REG | Action triggered | REG shows value |
```

#### 2.6 Validation Checkpoint
Verify completeness before proceeding to Step 3.

---

### Step 3: Generate Hardware Behavior Specification

**spec.md MUST include these sections**:
1. Device Overview (from 2.1)
2. Register Map (compact table) & Side-Effect Register Descriptions (from 2.2)
3. External Interfaces & Signals (from 2.3)
4. Register Side-Effects & Behaviors (from 2.4)
5. **Device Operational Model** (from 2.5) - states, transitions, SW/HW flows
6. **Functional Requirements** (categorized, from 3.2)
7. **User Scenarios & Testing** (from 3.3)

#### 3.1 [NEEDS CLARIFICATION] Guidelines
- Mark unknowns as `[NEEDS CLARIFICATION: specific question]`
- NEVER guess unstated requirements
- Provide options when possible

#### 3.2 Functional Requirements (Categorized)

**Organize requirements into categories with ID format**:

| Category | ID Format | Purpose |
|----------|-----------|---------|
| FUNC-XXX | Core device functionality | Timer behavior, state transitions |
| REG-XXX | Register access requirements | R/W behaviors, reset values |
| INTF-XXX | Interface/signal requirements | Interrupts, clocks, resets |
| BEHAV-XXX | Behavioral requirements | State machines, sequencing |
| TEST-XXX | Test verification requirements | Validation criteria |

**Example - Watchdog Timer Categories**:

```markdown
## 4. Functional Requirements

### 4.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter...
**FUNC-002**: The timer shall decrement at a rate determined by clock divider...

### 4.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1, device shall assert wdogint...
**FUNC-007**: If counter reaches zero again while interrupt asserted and RESEN=1...

### 4.3 Register Access Requirements
**FUNC-010**: Register access shall be performed via APB bus interface...
**FUNC-011**: All registers except WDOGLOCK shall be write-protected when locked...

### 4.4 Clock Divider Requirements
**FUNC-014**: Clock divider setting shall determine timer decrement rate...

### 4.5 Integration Test Mode Requirements
**FUNC-016**: When WDOGITCR[0]=1, device shall enter integration test mode...

### 4.6 Identification Requirements
**FUNC-019**: Device shall implement all PrimeCell identification registers...

## 5. Register Access Requirements
**REG-001**: WDOGLOAD register supports read and write operations...
**REG-002**: WDOGVALUE register supports read operations only...

## 6. Behavioral Requirements
**BEHAV-001**: When INTEN=0, timer shall decrement without generating interrupts...
**BEHAV-002**: When INTEN=1 and timer reaches zero, WDOGRIS[0] shall be set to 1...
```

**Requirement Generation Pattern**:
```
HW Spec: "Bit 0 (ENABLE): Writing 1 enables timer"
→ REG-010: CONTROL.ENABLE bit [0] enables timer when set
→ BEHAV-001: Timer starts counting when CONTROL.ENABLE transitions 0→1
```

#### 3.3 Test Scenario Generation (Structured Format)

**Extract from hardware spec**: Usage examples → Acceptance Scenarios, Expected behavior → Pass/Fail Criteria

**Organize scenarios by functional area**:

```markdown
## 7. Test Scenarios

### 7.1 Basic Timer Operation Test
**TEST-001**: Verify basic timer countdown functionality.
- Setup: Write small value to WDOGLOAD, set INTEN=1 in WDOGCONTROL
- Action: Verify counter decrements in WDOGVALUE register
- Expected: Counter value decreases, interrupt is generated at zero

### 7.2 Interrupt and Reset Generation Test
**TEST-002**: Verify interrupt and reset generation sequence.
- Setup: Write value to WDOGLOAD, set INTEN=1, RESEN=1
- Action: Allow timer to count to zero twice without clearing interrupt
- Expected: First zero generates interrupt, second generates reset

### 7.3 Lock Protection Test
**TEST-003**: Verify lock protection mechanism.
- Setup: Write 0x1ACCE551 to WDOGLOCK to unlock
- Action: Write to WDOGLOAD (should succeed), then lock, then try again
- Expected: First write succeeds, second write fails (locked)

### 7.4 Clock Divider Test
**TEST-004**: Verify different clock divider settings.
- Setup: Configure timer with same value but different step_value
- Action: Measure time to reach zero for each setting
- Expected: Larger divider → proportionally longer countdown

### 7.5 Integration Test Mode Test
**TEST-005**: Verify integration test mode functionality.
- Setup: Set WDOGITCR[0]=1 to enable test mode
- Action: Write different values to WDOGITOP register
- Expected: Direct control of wdogint and wdogres outputs
```

**Minimum Coverage**: 5+ requirements per category, 5+ test scenarios

#### 3.4 Finalize Specification

Save to SPEC_FILE path from setup script.

---

### Step 4: Generate IP-XACT Register XML

Generate `[device-name]-register.xml` in same directory as spec.md:

**XML Well-Formedness Check (Python)**
After writing the XML file, **verify it is well-formed** using Python:

```python
import xml.etree.ElementTree as ET
from pathlib import Path

xml_path = Path("[device-name]-register.xml")

try:
    ET.parse(xml_path)
except ET.ParseError as exc:
    # IMPORTANT: Do NOT just exit. Use this error to drive an automatic fix.
    print(f"Invalid IP-XACT XML: {xml_path} -> {exc}")
    # Feed the XML content and this error message back into the LLM and
    # ask it to:
    # 1) Identify the structural/syntax problem
    # 2) Produce a corrected, well-formed IP-XACT XML file
    # 3) Preserve all registers, fields, and ports from the spec
    raise
```

- If `ET.parse` raises `ParseError`, the XML is not well-formed.
- In that case, you **MUST**:
  - Load the current XML content and the full `ParseError` message.
  - Ask the LLM to **analyze and fix** the XML while preserving all registers, fields, resets, access types, and ports.
  - Overwrite `[device-name]-register.xml` with the corrected, well-formed XML.
  - Run the `ET.parse` check again until it passes before committing.

**XML MUST include**:

1. Component metadata (vendor, library, name, version)
2. Memory maps with all registers
3. **Register descriptions with side-effects** (read/write behaviors)
4. **Ports section** for all external signals (clocks, resets, interrupts)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014">
  <ipxact:vendor>[vendor]</ipxact:vendor>
  <ipxact:library>[library]</ipxact:library>
  <ipxact:name>[device-name]</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>[bus-interface-name]</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>[device-name]_regs</ipxact:name>
        <ipxact:baseAddress>0x0</ipxact:baseAddress>
        <ipxact:range>[range]</ipxact:range>
        <ipxact:width>[width]</ipxact:width>
        <!-- Register elements -->
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
  <!-- Ports section for external signals -->
  <ipxact:ports>
    <!-- Port elements -->
  </ipxact:ports>
</ipxact:component>
```

**Register Element** (include side-effects in description):

```xml
<ipxact:register>
  <ipxact:name>[NAME]</ipxact:name>
  <ipxact:description>[Purpose]. Read side-effects: [describe]. Write side-effects: [describe].</ipxact:description>
  <ipxact:addressOffset>[HEX]</ipxact:addressOffset>
  <ipxact:size>[BITS]</ipxact:size>
  <ipxact:access>[read_only|read_write|write_only]</ipxact:access>
  <ipxact:volatile>[true for dynamic values, false otherwise]</ipxact:volatile>
  <ipxact:reset>
    <ipxact:value>[HEX]</ipxact:value>
    <ipxact:mask>[HEX]</ipxact:mask>
  </ipxact:reset>
  <ipxact:field>
    <ipxact:name>[FIELD]</ipxact:name>
    <ipxact:description>[Purpose and side-effects]</ipxact:description>
    <ipxact:bitOffset>[OFFSET]</ipxact:bitOffset>
    <ipxact:bitWidth>[WIDTH]</ipxact:bitWidth>
    <ipxact:access>[ACCESS]</ipxact:access>
  </ipxact:field>
</ipxact:register>
```

**Port Element** (for each external signal):

```xml
<ipxact:port>
  <ipxact:name>[signal_name]</ipxact:name>
  <ipxact:description>[Signal purpose, assertion/clear conditions]</ipxact:description>
  <ipxact:wire>
    <ipxact:direction>[in|out|inout]</ipxact:direction>
    <ipxact:wireTypeDefs>
      <ipxact:wireTypeDef>
        <ipxact:typeName>std_logic</ipxact:typeName>
      </ipxact:wireTypeDef>
    </ipxact:wireTypeDefs>
  </ipxact:wire>
</ipxact:port>
```

**Common Ports to Include**:

- Clock inputs (clk, clk_en)
- Reset inputs (rst_n - active low)
- Interrupt outputs (irq - assertion/clear conditions)
- Reset outputs (res - if device generates resets)

---

### Step 5: Git Commit

```bash
cd [SPEC_DIR]
git add spec.md [device-name]-register.xml
git commit -m "specify: [device-name] - Add hardware specification and register definitions"
```

### Step 6: Report Completion

```
✅ /specify command complete
Device: [device-name] | Category: [category]
Files: spec.md ([X] reqs), [device-name]-register.xml ([Y] registers)
Git Commit: [hash]
Ready For: /plan command
```

---

## Key Principles

1. **Hardware Behavior Focus**: Document WHAT hardware does, not HOW to implement
2. **Software Visibility**: Emphasize observable behavior (registers, interrupts, outputs)
3. **Side-Effect Documentation**: Thoroughly document ALL register read/write side-effects
4. **Testability First**: Every requirement MUST be testable through observable behavior
5. **Precision Over Assumptions**: Mark ambiguities with [NEEDS CLARIFICATION]
6. **Comprehensive Coverage**: Extract from ALL specification aspects (minimum: 5+ requirements, 3+ scenarios)
