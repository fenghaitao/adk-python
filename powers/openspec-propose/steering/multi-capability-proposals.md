---
inclusion: manual
---

# Multi-Capability Proposal Guide

This steering file provides detailed guidance for creating proposals with multiple capability-based spec deltas. Load this when working with complex devices (50+ requirements).

## When to Use Multi-Capability Structure

Use multi-capability structure when:
- ✅ Device has 50+ requirements
- ✅ Device has distinct functional subsystems
- ✅ Different capabilities have different test strategies
- ✅ Implementation will be done in phases

Use single-capability structure when:
- ❌ Simple devices with <20 requirements
- ❌ Tightly coupled behaviors that can't be separated

## Capability Decomposition Process

### Step 1: Identify Capabilities

**Capability Identification Criteria**:
- **Functional Independence**: Can be understood and tested independently
- **Clear Boundaries**: Has well-defined inputs, outputs, and responsibilities
- **Cohesive Behavior**: Groups related requirements and behaviors together
- **Testable Separately**: Can have dedicated test scenarios

### Step 2: Name Capabilities

**Naming Convention**:
- Use kebab-case: `timer-core`, `interrupt-controller`, `lock-protection`
- Be specific and descriptive: `register-interface` not `registers`
- Focus on functionality: `interrupt-reset-control` not `signals`
- Avoid generic names: `timer-core` not `core` or `timer`

### Step 3: Map Requirements to Capabilities

Group requirements by functional area:
```
timer-core: FUNC-001 to FUNC-004, BEHAV-001 to BEHAV-003
interrupt-reset-control: FUNC-005 to FUNC-009, BEHAV-004 to BEHAV-006
lock-protection: FUNC-012 to FUNC-013, REG-008
register-interface: REG-001 to REG-010, FUNC-010, FUNC-011
integration-test-mode: FUNC-016 to FUNC-018
```

## Directory Structure

```
changes/<change-id>/
├── proposal.md
├── design.md          # MANDATORY for multi-capability
├── tasks.md
└── specs/
    ├── <capability-1>/
    │   └── spec.md
    ├── <capability-2>/
    │   └── spec.md
    └── <capability-3>/
        └── spec.md
```

## design.md Template

```markdown
# Design: <Change Title>

## Capability Decomposition

### Overview
[Brief explanation of why the device was decomposed into these capabilities]

### Capabilities

#### 1. <capability-1>
- **Purpose**: [What this capability does]
- **Requirements**: [List of FUNC-XXX, REG-XXX, etc.]
- **Dependencies**: [Other capabilities this depends on]
- **Key Behaviors**: [Main functionality]

[... repeat for each capability ...]

## Capability Interactions

### Dependency Graph
```
register-interface
    ↓
timer-core ←→ interrupt-reset-control
    ↓
lock-protection
```

### Integration Points

#### timer-core → interrupt-reset-control
- **Interface**: Counter value reaches zero
- **Data Flow**: Counter state → Interrupt/reset logic
- **Contract**: Timer signals timeout event, interrupt controller responds

[... document all integration points ...]

## Implementation Order

### Phase 1: Foundation (register-interface)
- **Rationale**: All other capabilities depend on register access
- **Deliverable**: APB bus interface, register read/write
- **Test**: Register access validation

[... document all phases ...]

## Testing Strategy

### Unit Testing (Per Capability)
- **timer-core**: Test counter decrement, clock divider, reload independently
- **interrupt-reset-control**: Test interrupt/reset logic with mocked timer events

### Integration Testing (Cross-Capability)
- **timer-core + interrupt-reset-control**: Full timeout → interrupt → reset sequence
- **All capabilities**: Complete device operation from reset to timeout

## Design Decisions

### Decision 1: [Decision Name]
- **Rationale**: [Why this approach]
- **Alternative Considered**: [Other options]
- **Why Chosen**: [Selection criteria]

## Risks and Mitigations

### Risk 1: [Risk Description]
- **Mitigation**: [How to address]

## Open Questions

- [ ] [Question 1]
- [ ] [Question 2]
```

## Task Organization

Organize tasks by capability:

```markdown
## 1. Capability: timer-core
### 1.1 DML Implementation
- [ ] 1.1.1 Implement counter decrement logic
- [ ] 1.1.2 Implement clock divider functionality
- [ ] 1.1.3 Implement reload behavior

### 1.2 Test Implementation
- [ ] 1.2.1 Test counter decrement at different rates
- [ ] 1.2.2 Test clock divider settings
- [ ] 1.2.3 Test reload on zero

## 2. Capability: interrupt-reset-control
### 2.1 DML Implementation
- [ ] 2.1.1 Implement interrupt generation logic
- [ ] 2.1.2 Implement reset generation logic

### 2.2 Test Implementation
- [ ] 2.2.1 Test interrupt generation on first timeout
- [ ] 2.2.2 Test reset generation on second timeout

## 3. Integration Testing
- [ ] 3.1 Test timer-core + interrupt-reset-control integration
- [ ] 3.2 Test complete device operation end-to-end
```

## Per-Capability Spec Delta Content

Each capability's `spec.md` should contain ONLY the requirements relevant to that capability:

```markdown
# Capability: timer-core

## ADDED Requirements

### Requirement: Counter Decrement
The timer counter SHALL decrement at a rate determined by the clock divider setting.

#### Scenario: Counter Decrements at Configured Rate
- **WHEN** timer is enabled with clock divider set to ÷1
- **THEN** counter SHALL decrement by 1 every clock cycle

[... more requirements for timer-core only ...]
```

## Validation Checklist

For multi-capability proposals, verify:
- [ ] design.md exists and documents all capabilities
- [ ] design.md includes capability decomposition rationale
- [ ] design.md includes integration points between capabilities
- [ ] design.md includes implementation order with dependencies
- [ ] design.md includes testing strategy (unit + integration)
- [ ] Each capability has separate spec delta directory
- [ ] Each capability spec.md contains only relevant requirements
- [ ] tasks.md organized by capability
- [ ] Integration tests included in tasks.md
- [ ] proposal.md Context section lists all capabilities
- [ ] `openspec validate --strict` passes

## Example: Watchdog Timer Decomposition

```
Source: specs/001-home-hfeng1-demo/spec.md (96 requirements)

Identified Capabilities:
1. timer-core (FUNC-001 to FUNC-004, BEHAV-001 to BEHAV-003)
   - Counter decrement logic
   - Clock divider functionality
   - Reload behavior
   
2. interrupt-reset-control (FUNC-005 to FUNC-009, BEHAV-004 to BEHAV-006)
   - Interrupt generation on first timeout
   - Reset generation on second timeout
   - Signal assertion/clearing logic
   
3. lock-protection (FUNC-012 to FUNC-013, REG-008)
   - Lock/unlock mechanism
   - Write protection when locked
   - Magic value validation (0x1ACCE551)
   
4. register-interface (REG-001 to REG-010, FUNC-010, FUNC-011)
   - APB bus interface
   - Register read/write behaviors
   - PrimeCell identification registers
   
5. integration-test-mode (FUNC-016 to FUNC-018)
   - Test mode enable/disable
   - Direct signal control
   - Test output registers
```

## Benefits

Multi-capability structure provides:
1. **Clear Separation of Concerns**: Each capability is independently understandable
2. **Parallel Development**: Different capabilities can be implemented in parallel
3. **Focused Testing**: Each capability can be tested independently
4. **Better Documentation**: design.md explains how capabilities interact
5. **Phased Implementation**: Capabilities can be implemented in dependency order
6. **Easier Maintenance**: Changes to one capability don't affect others
