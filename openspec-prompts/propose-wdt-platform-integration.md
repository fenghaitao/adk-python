# OpenSpec Proposal: Watchdog Timer Platform Integration Specification

Please create an OpenSpec change proposal for adding watchdog timer platform integration specification.

## Context

Using the comprehensive specification at `specs/001-home-hfeng1-demo/spec.md` as foundation, I want to create a specification focused on how the watchdog timer integrates with the Simics platform and external systems.

**Project Structure (relative to project root):**
- OpenSpec folder: `openspec/`
- Simics project: `simics-project/`
- Main DML files: `simics-project/modules/wdt/wdt.dml`
- Integration tests: `simics-project/modules/wdt/test/s-integration-test-mode.py`

## Leverage from existing spec

- Section 3: External Interfaces & Signals (WDOGINT, WDOGRES signals)
- Memory Interface Requirements (APB4 bus interface, address mapping)
- Integration with QSP-x86 platform components
- Signal routing and connection requirements
- Platform-specific constraints and dependencies

## Proposed Change

Create change `add-wdt-platform-integration` that:
1. Defines APB4 bus interface requirements and memory mapping
2. Specifies external signal connections (interrupt, reset)
3. Describes integration with Simics platform infrastructure
4. Includes platform-specific testing and validation requirements
5. Defines dependency management and component interface contracts

## Implementation Context

When creating tasks.md, reference these specific implementation files:
- **Platform Integration**: Update `simics-project/modules/wdt/wdt.dml`
- **Integration Testing**: Use `simics-project/modules/wdt/test/s-integration-test-mode.py`
- **Module Loading**: Update `simics-project/modules/wdt/module_load.py`
- **Build Configuration**: Use `simics-project/GNUmakefile`

Please create the proposal.md, tasks.md, and spec delta following OpenSpec conventions. Ensure tasks.md includes specific file paths and build/test commands.