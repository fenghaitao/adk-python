# OpenSpec Implementation: Execute Watchdog Timer Register Interface Tasks

Please implement the tasks defined in the OpenSpec change proposal for watchdog timer register interface.

## Context

I have a completed and validated OpenSpec change proposal at `openspec/changes/add-wdt-register-interface/` that includes:
- Comprehensive specification with 16 register interface requirements
- Detailed implementation tasks across 3 phases
- Specific file paths and build commands

## Project Structure (relative to project root)

- OpenSpec change: `openspec/changes/add-wdt-register-interface/`
- Tasks file: `openspec/changes/add-wdt-register-interface/tasks.md`
- Spec delta: `openspec/changes/add-wdt-register-interface/specs/wdt-register-interface/spec.md`
- Simics project: `simics-project/`
- Main DML files: `simics-project/modules/wdt/wdt.dml`
- Register definitions: `simics-project/modules/wdt/wdt-registers.dml`

## Implementation Request

Please execute the tasks in `openspec/changes/add-wdt-register-interface/tasks.md`:

### Phase 1: Already Complete (Specification Development)
- ✅ Register interface specification document created
- ✅ Register map requirements extracted
- ✅ Register access behavior requirements defined
- ✅ Lock mechanism requirements documented

### Phase 2: DML Implementation (Execute These Tasks)
1. **Task 2.1**: Update register definitions in `simics-project/modules/wdt/wdt-registers.dml`
2. **Task 2.2**: Implement lock mechanism in `wdt-registers.dml`
3. **Task 2.3**: Update main device file `simics-project/modules/wdt/wdt.dml`
4. **Task 2.4**: Implement register access validation logic
5. **Task 2.5**: Add integration test mode functionality

### Phase 3: Testing (Execute These Tasks)
1. **Task 3.1**: Create register access tests in `simics-project/modules/wdt/test/`
2. **Task 3.2**: Create lock mechanism tests
3. **Task 3.3**: Create integration test mode tests
4. **Task 3.4**: Run register validation tests
5. **Task 3.5**: Perform build validation

## Implementation Guidelines

- Use the detailed requirements from `openspec/changes/add-wdt-register-interface/specs/wdt-register-interface/spec.md`
- Reference the comprehensive specification at `specs/001-home-hfeng1-demo/spec.md` for implementation details
- Follow the specific file paths and commands listed in tasks.md
- Update task status from TODO to COMPLETED as you complete each task
- Use proper DML 1.4 syntax and conventions
- Ensure all changes build successfully with `simics-project/GNUmakefile`

Please implement these tasks systematically, starting with Phase 2 DML implementation.