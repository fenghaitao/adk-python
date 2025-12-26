# Design: Complex Watchdog Timer Implementation

## Context
Complex watchdog timer device with 105 requirements decomposed into 5 capabilities for independent implementation and testing. Each capability handles distinct functional areas while maintaining proper interactions.

## Goals / Non-Goals

**Goals:**
- Independent implementation of each capability
- Proper capability interactions and dependencies
- Complete functional coverage of all 105 requirements
- Performance-optimized implementation using DML best practices

**Non-Goals:**
- Cycle-accurate timing (functional model only)
- Hardware-level clock signal modeling
- Real-time constraints beyond functional behavior

## Capability Architecture

### Capability Dependencies

```
timer-core (foundation)
    ↓
interrupt-control ← reset-control
    ↓                    ↓
lock-protection ← integration-test
```

**Implementation Order:**
1. **timer-core** (foundation) - Must be implemented first
2. **interrupt-control** - Depends on timer-core events
3. **reset-control** - Depends on interrupt-control status
4. **lock-protection** - Can be implemented in parallel with reset-control
5. **integration-test** - Depends on interrupt-control and reset-control outputs

### Capability Interactions

**timer-core → interrupt-control:**
- Timer expiry events trigger interrupt status updates
- Clock divider settings affect timing calculations
- Counter reload operations coordinate with interrupt clearing

**interrupt-control → reset-control:**
- Interrupt status determines reset generation eligibility
- Interrupt clearing prevents reset generation
- Raw interrupt status feeds reset logic

**lock-protection → all capabilities:**
- Lock status controls write access to all registers except WDOGLOCK itself
- WDOGVALUE remains readable regardless of lock status
- Lock mechanism is orthogonal to functional behavior

**integration-test → interrupt-control + reset-control:**
- Test mode overrides normal interrupt/reset signal generation
- Direct control of wdogint and wdogres outputs
- Bypasses normal timer-driven behavior

## Technical Decisions

### Timer Implementation Pattern
- **Decision**: Use lazy evaluation + event mechanism pattern
- **Rationale**: Avoids cycle-by-cycle updates (Anti-Pattern #1), provides both efficient counter calculation and functional timeout behavior
- **Implementation**: Lazy counter calculation in WDOGVALUE reads, event-based timeout handling for interrupts/resets

### Clock Divider Handling
- **Decision**: Apply divider to event scheduling, not counter calculation
- **Rationale**: Maintains timing accuracy while avoiding performance penalties
- **Implementation**: `cycles_to_timeout = counter_value * step_divider_value`

### State Management
- **Decision**: Use `saved` variables for base timing state, `param configuration = "none"` for calculated registers
- **Rationale**: Proper checkpoint/restore behavior (Anti-Pattern #8)
- **Implementation**: Save counter start time/value, calculate current value on-demand

### Event Coordination
- **Decision**: Single timeout event drives both interrupt and reset logic
- **Rationale**: Ensures proper sequencing and avoids race conditions
- **Implementation**: Event handler updates interrupt status, checks for reset conditions

## Implementation Guidance

### Critical Anti-Patterns to Avoid
1. **NEVER** model clock signals or update counters every cycle
2. **NEVER** call `SIM_cycle_count()` in `init()` or `post_init()`
3. **ALWAYS** implement both lazy evaluation AND event mechanisms
4. **ALWAYS** cancel pending events before posting new ones

### DML Patterns to Use
- Lazy counter evaluation for WDOGVALUE register
- Event-based timeout handling with `simple_cycle_event`
- Register side-effects with proper `write_register()` overrides
- Signal interfaces for interrupt/reset outputs

### Testing Strategy
- Each capability tested independently
- Integration tests verify capability interactions
- Edge cases and error conditions covered per capability
- Performance validation (no cycle-by-cycle updates)

## Risks / Trade-offs

**Risk**: Capability interaction complexity
- **Mitigation**: Clear dependency order, well-defined interfaces, comprehensive integration tests

**Risk**: Timer performance with multiple divider settings
- **Mitigation**: Use proven lazy evaluation pattern, avoid cycle-by-cycle calculations

**Trade-off**: Implementation complexity vs. maintainability
- **Decision**: Accept higher initial complexity for better long-term maintainability through capability separation

## Migration Plan

1. Implement timer-core capability (foundation)
2. Add interrupt-control capability (builds on timer events)
3. Add reset-control capability (extends interrupt behavior)
4. Add lock-protection capability (orthogonal security feature)
5. Add integration-test capability (test infrastructure)
6. Integration testing across all capabilities
7. Performance validation and optimization

## Open Questions

None - all requirements clearly specified in primary spec.
