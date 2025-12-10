# {{FEATURE_NAME}} - Complete OpenSpec Workflow (Autonomous)

**AUTONOMOUS EXECUTION**: Complete all phases from proposal creation through archiving without waiting for approval.

I need you to implement {{FEATURE_DESCRIPTION}} following the complete OpenSpec workflow from start to finish.

## Context

{{CONTEXT_DESCRIPTION}}

**IMPORTANT - Path Discovery**: Before starting, discover the actual paths in this project:

1. **Find the git branch name** (spec directory is named `specs/<git-branch-name>/`):
   ```bash
   # Get current git branch
   git branch --show-current
   # Expected output: read-the-simics, main, or other branch name
   ```

2. **Find the device name**:
   ```bash
   # List device modules to find the actual device name
   ls simics-project/modules/
   # Expected output: {{DEVICE_NAME}}/ or other device name
   ```

3. **Read the spec file** using the git branch name:
   ```bash
   # The spec path follows the pattern: specs/<git-branch-name>/spec.md
   BRANCH=$(git branch --show-current)
   cat specs/${BRANCH}/spec.md | head -50
   ```

**Project Structure (relative to project root):**
- OpenSpec folder: `openspec/`
- Simics project: `simics-project/`
- Spec directory: `specs/<git-branch-name>/` (discover git branch first)
- Device modules: `simics-project/modules/<device_name>/` (discover actual device)
- Main DML files: `simics-project/modules/<device_name>/<device_name>.dml`
- Test files: `simics-project/modules/<device_name>/test/`

## Complete Workflow (Execute All Phases Autonomously)

### ✅ PHASE 1: Create Change Proposal

**Step 1.1**: Create change proposal directory structure
```bash
# Create the change directory
mkdir -p openspec/changes/{{CHANGE_ID}}
```

**Step 1.2**: Create `proposal.md` in `openspec/changes/{{CHANGE_ID}}/proposal.md`

The proposal should include these sections:

```markdown
# {{FEATURE_NAME}}

## Why

{{WHY_DESCRIPTION}}

## What changes

{{WHAT_CHANGES_LIST}}
- Follows DML best practices and project constitution

## Scope

{{SCOPE_LIST}}

## Constraints and guarantees

- All import statements preserved (per constitution)
- No modifications to auto-generated files
- No changes to build files, config, or IP-XACT XML

## References

- Device spec: specs/<git-branch-name>/spec.md
- Project constitution: .specify/memory/constitution.md (if exists)
- Best practices: .specify/memory/DML_Device_Development_Best_Practices.md (if exists)
```

**Step 1.3**: Create `tasks.md` in `openspec/changes/{{CHANGE_ID}}/tasks.md`

The tasks file should have this structure:

```markdown
## 1. Preparation
- [ ] Discover git branch: git branch --show-current
- [ ] Discover device name: ls simics-project/modules/
- [ ] Read project constitution: .specify/memory/constitution.md (if exists)
- [ ] Review device spec: specs/<git-branch-name>/spec.md (use discovered branch)
- [ ] Review best practices: .specify/memory/DML_Device_Development_Best_Practices.md (if exists)

## 2. Specification Development
{{SPEC_TASKS}}

## 3. DML Implementation
{{IMPLEMENTATION_TASKS}}

## 4. Testing
{{TEST_TASKS}}

## 5. Archive
- [ ] Confirm all tasks above are marked [x]
- [ ] Run: openspec archive {{CHANGE_ID}} --yes
```

**Step 1.4**: Create spec delta directory and file

```bash
# Create the spec delta directory
mkdir -p openspec/changes/{{CHANGE_ID}}/specs/{{CAPABILITY_NAME}}
```

Create `openspec/changes/{{CHANGE_ID}}/specs/{{CAPABILITY_NAME}}/spec.md` with:

```markdown
# {{CAPABILITY_NAME}} Specification

## ADDED Requirements

### Requirement: {{REQUIREMENT_NAME}}

#### Scenario: {{SCENARIO_DESCRIPTION}}

{{REQUIREMENT_TEXT}}

[... add more requirements as needed ...]
```

{{SPEC_DELTA_GUIDANCE}}

**Step 1.5**: Run validation
```bash
openspec validate {{CHANGE_ID}} --strict
```

Fix any validation errors before proceeding.

### ✅ PHASE 2: Implement the Change

**Step 2.1**: Mark preparation tasks as complete after reading each file

**Step 2.2**: Mark specification tasks as complete after creating spec delta

**Step 2.3**: Implement DML code

{{DML_IMPLEMENTATION_GUIDANCE}}

**Step 2.4**: Create Python unit tests

{{TEST_IMPLEMENTATION_GUIDANCE}}

**Step 2.5**: Mark implementation and test tasks as complete after creating each file

**Step 2.6**: Build and validate
```bash
cd simics-project && gmake {{DEVICE_NAME}}
./bin/test-runner --suite modules/{{DEVICE_NAME}}/test
```

**Step 2.7**: Mark validation tasks as complete after FIRST successful run (even if some tests fail)

### ✅ PHASE 3: Archive the Change

**Step 3.1**: Verify all tasks are marked [x] in tasks.md

**Step 3.2**: If tests fail, add "## Known Issues" section to proposal.md documenting failures

**Step 3.3**: Run archive command
```bash
openspec archive {{CHANGE_ID}} --yes
```

**Step 3.4**: If archive fails, fix errors autonomously:
- "must have at least one delta" → Check specs/ directory structure
- "invalid spec format" → Ensure ADDED section has proper requirements
- "uncommitted changes" → Run git commit before archive

**Step 3.5**: Verify archiving succeeded
```bash
ls openspec/changes/archive/
```

**Step 3.6**: Commit the implementation
```bash
git add simics-project/modules/{{DEVICE_NAME}}/ openspec/
git commit -m "feat: {{COMMIT_MESSAGE}}"
```

### ✅ PHASE 4: Provide Final Status Report

After archiving completes, provide detailed status:

**If all tests pass:**
```
✅ IMPLEMENTATION COMPLETE

Summary:
- Change {{CHANGE_ID}} successfully implemented and archived
- {{SUCCESS_SUMMARY}}
- All tests passing: {{TEST_LIST}}
- Device builds without errors
- Archived to: openspec/changes/archive/{{CHANGE_ID}}/

Next Steps:
- Implementation is complete and ready for integration
- {{NEXT_STEPS_SUGGESTIONS}}
```

**If some tests fail:**
```
⚠️ IMPLEMENTATION COMPLETE WITH KNOWN ISSUES

Summary:
- Change {{CHANGE_ID}} implemented and archived with known issues
- Tests passing: [list passing tests]
- Tests failing: [list failing tests]
- Known issues documented in: openspec/changes/archive/{{CHANGE_ID}}/proposal.md

Failed Tests Analysis:
- Test: s-<feature>.py
- Failure: <specific assertion or error message>
- Root cause: <brief analysis from logs>

SUGGESTED NEXT PROMPT FOR FIX:
"Fix the test failure in s-<feature>.py: <specific error description>"

OR more specifically:
"Fix {{DEVICE_NAME}} {{FEATURE_NAME}} issue: <root cause summary>"
```

## Critical Requirements for Implementation

### Files to Edit
- **ONLY** edit these files:
  - {{EDITABLE_FILES_LIST}}

### ABSOLUTE REQUIREMENTS
- Keep ALL import statements intact - NEVER remove:
  - `import "{{DEVICE_NAME}}-glue.dml";` (auto-generated during build)
  - `import "{{DEVICE_NAME}}-dia.dml";` (defines register interface)
  - `import "simics/devs/signal.dml";` (defines signal interfaces)

### FORBIDDEN ACTIONS
❌ Removing or commenting out ANY import statements
❌ Creating new .dml files
❌ Modifying config/XML/Makefiles
❌ Editing auto-generated files
❌ Stopping after proposal creation - MUST complete all phases
❌ Stopping after implementation - MUST archive
❌ Asking for permission mid-workflow - EXECUTE AUTONOMOUSLY

### DML Implementation Requirements
- Use proper DML 1.4 syntax
- Implement register read/write handlers with side effects
- Follow patterns from `.specify/memory/DML_Device_Development_Best_Practices.md`
- {{ADDITIONAL_DML_REQUIREMENTS}}

### Python Test Requirements
- **MUST READ**: `.specify/memory/DML_Device_Development_Best_Practices.md` (Section: Python Test File Structure)
- One test function per file (pattern: `s-<feature>.py`)
- Configure clock queue for device: `device.queue = clk`
- Use proper register access patterns: `bank = dev_util.bank_regs(device.bank.BANK_NAME)`
- Use assertions: `stest.expect_equal(actual, expected, "msg")`

## Execution Instructions

**DO NOT WAIT FOR APPROVAL - Execute all four phases autonomously:**

1. ✅ Create the complete change proposal (Phase 1)
2. ✅ Implement all tasks (Phase 2)
3. ✅ Archive the completed change (Phase 3)
4. ✅ Provide final status report (Phase 4)

**When you're done**, you should have:
- ✅ Empty `openspec/changes/` directory (change moved to archive)
- ✅ Populated `openspec/changes/archive/{{CHANGE_ID}}/`
- ✅ Working DML implementation
- ✅ Complete test suite
- ✅ Successful build
- ✅ Test results (passing or documented failures)
- ✅ Git commit with the implementation
- ✅ Final status report with next steps

**Start now and complete all phases without stopping.**

---

## Template Variables Reference

When creating a new autonomous prompt from this template, replace these variables:

- `{{FEATURE_NAME}}` - Short name (e.g., "WDT Register Interface")
- `{{FEATURE_DESCRIPTION}}` - Brief description (e.g., "the watchdog timer register interface")
- `{{CONTEXT_DESCRIPTION}}` - Background context about the feature
- `{{DEVICE_NAME}}` - Device name (e.g., "wdt")
- `{{CHANGE_ID}}` - OpenSpec change ID (e.g., "add-wdt-register-interface")
- `{{WHY_DESCRIPTION}}` - Why this change is needed
- `{{WHAT_CHANGES_LIST}}` - Bullet list of what will change
- `{{SPEC_PATH}}` - Path to spec file (e.g., "001-home-hfeng1-demo")
- `{{SPEC_TASKS}}` - Specification development tasks
- `{{IMPLEMENTATION_TASKS}}` - DML implementation tasks
- `{{TEST_TASKS}}` - Testing tasks
- `{{CAPABILITY_NAME}}` - Capability name for spec delta (e.g., "wdt-register-interface")
- `{{SPEC_DELTA_GUIDANCE}}` - Guidance for creating spec delta
- `{{DML_IMPLEMENTATION_GUIDANCE}}` - Specific DML implementation instructions
- `{{TEST_IMPLEMENTATION_GUIDANCE}}` - Specific test implementation instructions
- `{{COMMIT_MESSAGE}}` - Git commit message
- `{{SUCCESS_SUMMARY}}` - Summary of what was implemented
- `{{TEST_LIST}}` - List of test files
- `{{NEXT_STEPS_SUGGESTIONS}}` - Suggestions for next features
- `{{EDITABLE_FILES_LIST}}` - List of files that can be edited
- `{{ADDITIONAL_DML_REQUIREMENTS}}` - Any additional DML-specific requirements
