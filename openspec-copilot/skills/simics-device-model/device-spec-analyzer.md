# Workflow Overview

1. **Step 1**: Run setup script (creates openspec directory structure)
2. **Step 2**: Parse hardware specification (extract device info, registers, behaviors)
3. **Step 3**: Generate openspec/project.md
4. **Step 4**: Generate openspec/[device-name]-registers.xml
5. **Step 5**: Git commit
6. **Step 6**: Report completion

---

## Step 1: Run Device Initialization Script (MANDATORY - DO THIS FIRST)

**CRITICAL**: Execute these commands BEFORE proceeding to Step 2:

```bash
openspec init --tools github-copilot
bash scripts/device-init.sh --json <device_name>
```

Parse JSON output to extract `DEVICE_NAME`, `REPO_ROOT`, `BRANCH_NAME` for use in subsequent steps.

---

## Step 2: Parse Hardware Specification

### 2.1 Device Overview

Extract fundamental device information:
- **Device name**: Full name and abbreviation
- **Device type/category**: 
  - Timer/Counter
  - UART/Serial Communication
  - DMA Controller
  - Interrupt Controller
  - GPIO
  - Memory Controller
  - Bus Interface
  - Analog Device
  - Custom/Mixed
- **Base address**: Default memory-mapped base address
- **Address range**: Total address space occupied
- **Version information**: Hardware revision, IP version
- **Vendor information**: Manufacturer, IP provider

### 2.2 Register Map (Two-Part Structure)

**Part A: Register Map Overview Table**

Create a COMPACT summary table for ALL registers:

| Offset | Register Name | Type | Width | Reset Value | Description |
|--------|---------------|------|-------|-------------|-------------|
| 0x00   | CTRL          | RW   | 32    | 0x00000000  | Control register |
| 0x04   | STATUS        | RO   | 32    | 0x00000001  | Status register |

**Part B: Detailed Descriptions (ONLY for Side-Effect Registers)**

Only include detailed bit field tables for registers with:
- Read side-effects (value changes on read, clears flags)
- Write side-effects (triggers actions beyond storing value)
- Cross-register dependencies
- Special access behaviors (lock protection, clear-on-read)

**Skip detailed descriptions for**:
- Read-only ID/version registers
- Simple R/W registers without side-effects
- Reserved registers

**Access Type Mapping**:

| HW Spec | IP-XACT | Simics Behavior |
|---------|---------|-----------------|
| RO      | `read_only` | Read returns stored value, writes ignored |
| RW      | `read_write` | Normal read/write operations |
| WO      | `write_only` | Read returns 0 or undefined, write stores |
| W1C     | `read_write` | Write 1 to clear bits, 0 has no effect |
| RW1S    | `read_write` | Write 1 to set bits |
| RW1C    | `read_write` | Write 1 to clear bits |
| RC      | `read_only` | Read clears the value |
| RS      | `read_only` | Read sets the value |

### 2.3 I/O Ports & Signals

Extract all external interfaces:

**Clock Signals**:
- Name, frequency, enable control
- Clock domains if multiple clocks exist

**Reset Signals**:
- Name, polarity (active-high/low), type (synchronous/asynchronous)

**Interrupt Signals**:
- Name, type (level/edge), polarity, assertion/deassertion conditions

**Bus Interfaces**:
- Protocol (AHB, APB, AXI, custom)
- Data width, address width
- Control signals

**GPIO/Custom Signals**:
- Name, direction (input/output/bidirectional), width
- Purpose and behavior

### 2.4 Register Side-Effects & Behaviors

**Categories of Side-Effects**:

1. **Counter/Timer Behaviors**:
   - Overflow/underflow conditions
   - Compare match events
   - Periodic event generation
   - Reload/preset operations

2. **State Machine Transitions**:
   - Mode changes triggered by register writes
   - State progression conditions
   - State-dependent register access

3. **External Interface Effects**:
   - Signal assertion/deassertion
   - Interrupt generation/clearing
   - Pin state changes

4. **Internal State Updates**:
   - Cross-register dependencies
   - Cache/buffer operations
   - Flag updates

**Documentation Format**: Trigger → Action → Dependencies

Example:
```
Register: CONTROL.START [bit 0]
Write Side-Effect:
  - Trigger: Write 1 to CONTROL.START
  - Action: Transition from IDLE to RUNNING state, counter begins decrementing
  - Dependencies: Requires CONTROL.ENABLE=1 and LOCK!=0x1
  - Observable: STATUS.ACTIVE reads as 1, COUNTER value begins changing
```

### 2.5 Device Operational Model (CRITICAL for Simics Implementation)

**⚠️ MANDATORY**: Document device states, transitions, and SW/HW interaction flows.

**Device States**:

Document all operational states:
```
State: [STATE_NAME]
- Entry conditions: [Register writes, signal changes required]
- Observable indicators: [Register values, signal states visible to software]
- Active behaviors: [What hardware does in this state]
- Exit conditions: [How to transition out]
- Simics implementation note: [State variable name, transition logic]
```

Example:
```
State: COUNTING
- Entry conditions: Write 1 to CTRL.ENABLE with non-zero LOAD value
- Observable indicators: STATUS.ACTIVE=1, VALUE register decrementing
- Active behaviors: Counter decrements each clock cycle, compares against MATCH
- Exit conditions: Counter reaches 0, or CTRL.ENABLE cleared
- Simics implementation note: state_var = STATE_COUNTING, check counter in event
```

**State Transitions**:

Document all valid state transitions:
```
[SOURCE_STATE] → [TARGET_STATE]: Trigger condition
- Register writes: [Specific register field changes]
- Hardware events: [Internal conditions, timeouts, matches]
- Observable change: [How software can verify transition occurred]
```

**SW/HW Interaction Flows**:

Complete operational sequences:
```
Flow: [Flow Name] (Example: Timer Countdown with Interrupt)
State Transition: IDLE → CONFIGURED → COUNTING → INTERRUPT_PENDING → IDLE

| Step | Software Actions | Hardware Responses | Observable State |
|------|------------------|-------------------|------------------|
| 1    | Write 100 to LOAD | Value stored | LOAD=100 |
| 2    | Write ENABLE=1 to CTRL | Counter starts | VALUE=100, STATUS.ACTIVE=1 |
| 3    | Wait | Counter decrements | VALUE decreasing |
| 4    | Counter reaches 0 | IRQ asserted, STATUS.IRQ=1 | IRQ pin high, STATUS.IRQ=1 |
| 5    | Write 1 to STATUS.IRQ | IRQ cleared | IRQ pin low, STATUS.IRQ=0 |
```

### 2.6 Validation Checkpoint
Verify completeness before proceeding to Step 3.

---

## Step 3: Generate OpenSpec Project Description

**openspec/project.md MUST include these sections**:
1. Device Overview (from 2.1)
2. Register Map (compact table) & Side-Effect Register Descriptions (from 2.2)
3. External Interfaces & Signals (from 2.3)
4. Register Side-Effects & Behaviors (from 2.4)
5. **Device Operational Model** (from 2.5) - states, transitions, SW/HW flows
6. **Simics Implementation Requirements** (from 3.2)
7. **Verification Scenarios** (from 3.3)

### 3.1 [NEEDS CLARIFICATION] Guidelines
- Mark unknowns as `[NEEDS CLARIFICATION: specific question]`
- NEVER guess unstated requirements
- Provide options when possible

### 3.2 Simics Implementation Requirements (Categorized)

**Organize requirements into categories with ID format**:

| Category | ID Format | Purpose |
|----------|-----------|---------|
| FUNC-XXX | Core device functionality | Timer behavior, state transitions |
| REG-XXX | Register access requirements | R/W behaviors, reset values |
| INTF-XXX | Interface/signal requirements | Interrupts, clocks, resets |
| BEHAV-XXX | Behavioral requirements | State machines, sequencing |
| SIM-XXX | Simics-specific requirements | DML implementation, attributes |

**Example - Watchdog Timer Categories**:

```markdown
## 4. Simics Implementation Requirements

### 4.1 Timer Functionality Requirements
**FUNC-001**: The watchdog timer shall be a 32-bit decrementing counter...
**FUNC-002**: The timer shall decrement at a rate determined by clock divider...

### 4.2 Interrupt and Reset Requirements
**FUNC-005**: When counter reaches zero and INTEN=1, device shall assert wdogint...
**FUNC-007**: If counter reaches zero again while interrupt asserted and RESEN=1...

### 4.3 Register Access Requirements
**REG-001**: WDOGLOAD register supports read and write operations...
**REG-002**: WDOGVALUE register supports read operations only...

### 4.4 Behavioral Requirements
**BEHAV-001**: When INTEN=0, timer shall decrement without generating interrupts...
**BEHAV-002**: When INTEN=1 and timer reaches zero, WDOGRIS[0] shall be set to 1...

### 4.5 Simics-Specific Requirements
**SIM-001**: Device shall be implemented as DML 1.4 device model...
**SIM-002**: Timer decrement shall be implemented using Simics event mechanism...
**SIM-003**: Device shall expose interrupt port for wdogint signal...
```

**Requirement Generation Pattern**:
```
HW Spec: "Bit 0 (ENABLE): Writing 1 enables timer"
→ REG-010: CONTROL.ENABLE bit [0] enables timer when set
→ BEHAV-001: Timer starts counting when CONTROL.ENABLE transitions 0→1
→ SIM-001: Implement timer event callback triggered by CONTROL.ENABLE write
```

### 3.3 Verification Scenario Generation (Structured Format)

**Extract from hardware spec**: Usage examples → Test Scenarios, Expected behavior → Pass/Fail Criteria

**Organize scenarios by functional area**:

```markdown
## 5. Verification Scenarios

### 5.1 Basic Timer Operation Test
**TEST-001**: Verify basic timer countdown functionality.
- Setup: Write small value to WDOGLOAD, set INTEN=1 in WDOGCONTROL
- Action: Step simulation, verify counter decrements in WDOGVALUE register
- Expected: Counter value decreases, interrupt is generated at zero

### 5.2 Interrupt and Reset Generation Test
**TEST-002**: Verify interrupt and reset generation sequence.
- Setup: Write value to WDOGLOAD, set INTEN=1, RESEN=1
- Action: Allow timer to count to zero twice without clearing interrupt
- Expected: First zero generates interrupt, second generates reset

### 5.3 Lock Protection Test
**TEST-003**: Verify lock protection mechanism.
- Setup: Write 0x1ACCE551 to WDOGLOCK to unlock
- Action: Write to WDOGLOAD (should succeed), then lock, then try again
- Expected: First write succeeds, second write fails (locked)

### 5.4 Clock Divider Test
**TEST-004**: Verify different clock divider settings.
- Setup: Configure timer with same value but different step_value
- Action: Measure simulation cycles to reach zero for each setting
- Expected: Larger divider → proportionally longer countdown
```

**Minimum Coverage**: 5+ requirements per category, 5+ test scenarios

### 3.4 Finalize Project Description

Save to `openspec/project.md` in current directory.

---

## Step 4: Generate IP-XACT Register XML

Generate `openspec/[device-name]-registers.xml` in current directory:

**XML Well-Formedness Check (Python)**
After writing the XML file, **verify it is well-formed** using Python:

```python
import xml.etree.ElementTree as ET
from pathlib import Path

xml_path = Path("openspec/[device-name]-registers.xml")

try:
    ET.parse(xml_path)
except ET.ParseError as exc:
    print(f"Invalid IP-XACT XML: {xml_path} -> {exc}")
    # Feed the XML content and error back to LLM for automatic fix
    # 1) Identify the structural/syntax problem
    # 2) Produce corrected, well-formed IP-XACT XML file
    # 3) Preserve all registers, fields, and ports from the spec
    raise
```

**XML MUST include**:

1. Component metadata (vendor, library, name, version)
2. Memory maps with all registers
3. **Register descriptions with side-effects** (read/write behaviors)
4. **Ports section** for all external signals (clocks, resets, interrupts)

### 4.1 XML Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ipxact:component xmlns:ipxact="http://www.accellera.org/XMLSchema/IPXACT/1685-2014"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://www.accellera.org/XMLSchema/IPXACT/1685-2014
                                      http://www.accellera.org/XMLSchema/IPXACT/1685-2014/index.xsd">
  
  <!-- Component Identity -->
  <ipxact:vendor>[vendor or "unknown"]</ipxact:vendor>
  <ipxact:library>[library or "simics"]</ipxact:library>
  <ipxact:name>[device-name]</ipxact:name>
  <ipxact:version>1.0</ipxact:version>
  
  <!-- Memory Maps -->
  <ipxact:memoryMaps>
    <ipxact:memoryMap>
      <ipxact:name>[device-name]_map</ipxact:name>
      <ipxact:addressBlock>
        <ipxact:name>[device-name]_regs</ipxact:name>
        <ipxact:baseAddress>0x0</ipxact:baseAddress>
        <ipxact:range>[address-range-in-hex]</ipxact:range>
        <ipxact:width>[register-width-bits]</ipxact:width>
        <ipxact:usage>register</ipxact:usage>
        
        <!-- Register Definitions -->
        [Register elements here]
        
      </ipxact:addressBlock>
    </ipxact:memoryMap>
  </ipxact:memoryMaps>
  
  <!-- External Ports -->
  <ipxact:ports>
    [Port elements here]
  </ipxact:ports>
  
</ipxact:component>
```

### 4.2 Register Element Template

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

### 4.3 Port Element Template

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

## Step 5: Git Commit

```bash
git add openspec/project.md openspec/[device-name]-registers.xml
git commit -m "device-init: [device-name] - Initialize OpenSpec project with hardware specification and register definitions"
```

## Step 6: Report Completion

```
✅ device-spec-analyzer command complete
Device: [device-name] | Category: [category]
Files: openspec/project.md ([X] reqs), openspec/[device-name]-registers.xml ([Y] registers)
Git Commit: [hash]
Ready For: Simics device feature planning and implementation
```

---

# Key Principles

1. **Hardware Behavior Focus**: Document WHAT hardware does for Simics simulation
2. **Software Visibility**: Emphasize observable behavior (registers, interrupts, outputs)
3. **Side-Effect Documentation**: Thoroughly document ALL register read/write side-effects
4. **Simics Integration**: Requirements must map to DML implementation patterns
5. **Verification First**: Every requirement MUST be testable in Simics environment
6. **Precision Over Assumptions**: Mark ambiguities with [NEEDS CLARIFICATION]
7. **Comprehensive Coverage**: Extract from ALL specification aspects (minimum: 5+ requirements, 3+ scenarios)

---

# Output File Locations

- **openspec/project.md**: Device overview, requirements, and verification scenarios (created in current directory)
- **openspec/[device-name]-registers.xml**: IP-XACT register definitions (created in current directory)

Both files should be created in an `openspec/` subdirectory of the current working directory, not in a feature branch directory structure.
