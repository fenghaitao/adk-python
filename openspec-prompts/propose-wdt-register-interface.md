# OpenSpec Proposal: Watchdog Timer Register Interface Specification

Please create an OpenSpec change proposal for adding watchdog timer register interface specification. 

## Context

I have a comprehensive watchdog timer specification already generated at `specs/001-home-hfeng1-demo/spec.md` from spec-kit that includes detailed register definitions and behavior. I want to extract and organize the register interface aspects into a proper OpenSpec specification.

**Project Structure (relative to project root):**
- OpenSpec folder: `openspec/`
- Simics project: `simics-project/`
- Main DML files: `simics-project/modules/wdt/wdt.dml`
- Register definitions: `simics-project/modules/wdt/wdt-registers.dml`
- Test files: `simics-project/modules/wdt/test/`

## Leverage from existing spec

- Section 2: Register Map with 21 registers (WDOGLOAD, WDOGVALUE, WDOGCONTROL, etc.)
- Detailed register behavior descriptions (offsets 0x000-0xFE8)
- Lock mechanism with magic value 0x1ACCE551
- Register access patterns and validation rules
- Reset values and field definitions

## Proposed Change

Create change `add-wdt-register-interface` that:
1. Extracts register interface requirements from the existing comprehensive spec
2. Creates focused specification for register behavior, access patterns, and validation
3. Defines clear requirements for DML implementation of register map
4. Includes lock mechanism and security aspects

## Implementation Context

When creating tasks.md, reference these specific implementation files:
- **DML Implementation**: Update `simics-project/modules/wdt/wdt-registers.dml`
- **Main Device**: Update `simics-project/modules/wdt/wdt.dml`
- **Build System**: Use `simics-project/GNUmakefile`
- **Testing**: Create/update tests in `simics-project/modules/wdt/test/`

Please create the proposal.md, tasks.md, and spec delta following OpenSpec conventions. Ensure tasks.md includes specific file paths and build/test commands.