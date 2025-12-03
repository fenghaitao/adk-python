# OpenSpec Prompts - Template Variables

This folder contains prompt templates for the OpenSpec workflow. The templates use placeholder variables that should be replaced with actual values before use.

## Template Variables

The following placeholders are used in the prompt templates and are automatically replaced by the `test_openspec.sh` script:

- **`<device_name>`** - The name of the Simics device being implemented (e.g., `wdt`, `uart`, `timer`)
  - Used in: file paths, import statements, device references
  - Replaced by: `--device` parameter or environment variable

- **`<git_branch_name>`** - The git branch name where specs are located
  - Used in: spec file paths
  - Replaced by: current git branch name from the project

- **`<project_name>`** - The name of the OpenSpec project
  - Used in: project references, session IDs
  - Replaced by: first argument to `run_openspec.sh`

## Automatic Replacement

The `test_openspec.sh` script automatically replaces these placeholders when copying prompt templates:

```bash
# From test_openspec.sh
mkdir -p "$proj_dir/openspec-prompts"
cp "$ADK_ROOT/openspec-prompts/"*.md "$proj_dir/openspec-prompts/"
# Customize prompts: replace <device_name> placeholder with actual device name
sed -i "s/<device_name>/$device_name/g" "$proj_dir/openspec-prompts/"*.md
# Customize prompts: replace <git_branch_name> placeholder with actual git branch name
sed -i "s/<git_branch_name>/$git_branch_name/g" "$proj_dir/openspec-prompts/"*.md
```

## Files Using Templates

- **`1.md`** - Original implementation-focused prompt (bypasses OpenSpec workflow - NOT recommended)
- **`1.SIMPLE.md`** - **NEW**: Ultra-short prompt that relies on agent's default autonomous workflow (recommended for testing)
- **`1.FIXED.md`** - Updated prompt that triggers OpenSpec workflow with autonomous execution through all phases
- **`1.AUTONOMOUS.md`** - Ultra-explicit autonomous workflow with detailed commands and verification steps (recommended for complex workflows)
- **`2.md`** - Error fixing prompt (if exists)
- **`3.md`** - Test implementation prompt (if exists)

## Choosing the Right Prompt Template

### `1.SIMPLE.md` - ✅ **RECOMMENDED** for Testing Agent Intelligence

**Content**:
```markdown
Implement the simics <device_name> device and python tests as the spec describes, 
based on the current project skeleton.

Follow the DML best practices and ensure all tests pass.
```

- ✅ **Ultra-short**: Only 2 sentences
- ✅ **Tests agent intelligence**: Relies on agent's default behavior from AGENTS.md
- ✅ **Autonomous execution**: Agent should complete all phases without explicit instructions
- ✅ **Natural language**: Sounds like a real user request
- **When to use**: 
  - Testing the new autonomous workflow feature
  - Verifying agent follows AGENTS.md default behavior
  - Quick prototyping
  - When you trust the agent to do the right thing

### `1.md` (Original) - ⚠️ Not Recommended
- ❌ Bypasses OpenSpec workflow
- ❌ Goes straight to implementation
- ❌ No proposal, tasks, or archiving
- **When to use**: Never for OpenSpec workflows

### `1.FIXED.md` - ✅ Recommended for Standard Use
- ✅ Triggers complete OpenSpec workflow
- ✅ Autonomous execution (all 3 phases)
- ✅ Creates proposal, implements, archives
- ✅ Uses OpenSpec commands
- **When to use**: Standard device implementation workflows

### `1.AUTONOMOUS.md` - ✅ Recommended for Complex Workflows
- ✅ Maximum explicitness on autonomous execution
- ✅ Includes concrete bash commands
- ✅ Provides complete tasks.md template
- ✅ Multiple reminders to complete all phases
- ✅ Verification steps for each phase
- **When to use**: 
  - Complex implementations with many steps
  - When agent tends to stop after proposal
  - When you need maximum clarity on workflow
  - For long-running automated workflows

## Key Differences: Autonomous vs Non-Autonomous

**Non-Autonomous** (old approach - NOT recommended):
```markdown
## Expected OpenSpec Workflow

1. Create a change proposal
2. Write proposal.md and tasks.md
3. Validate the proposal

Let me know when you've created the proposal and are ready to begin implementation.
```
**Problem**: Agent stops after Phase 1, waits for approval ❌

**Autonomous** (new approach - recommended):
```markdown
## Expected OpenSpec Workflow

Please follow the complete OpenSpec workflow autonomously from start to finish:

### Phase 1: Create Change Proposal
1. Create proposal directory
2. Write proposal.md and tasks.md
3. Run openspec validate

### Phase 2: Implement the Change
4. Implement all tasks
5. Mark tasks complete

### Phase 3: Archive the Change
6. Run openspec archive --yes
7. Commit implementation

**Important**: Complete all three phases autonomously. Do NOT stop and wait.
```
**Result**: Agent completes all phases without stopping ✅

## Usage Example

**Before replacement** (in repository):
```markdown
# Create Change Proposal for DML Device Implementation

I need to create an OpenSpec change proposal for implementing the Simics <device_name> device.

Please read the device spec from: `specs/<git_branch_name>/spec.md`
```

**After replacement** (in project):
```markdown
# Create Change Proposal for DML Device Implementation

I need to create an OpenSpec change proposal for implementing the Simics wdt device.

Please read the device spec from: `specs/001-simics-wdt-device/spec.md`
```

## Adding New Templates

When creating new prompt templates:

1. Use the standard placeholder format: `<variable_name>`
2. Document any new placeholders in this README
3. Update `test_openspec.sh` to handle new placeholders if needed
4. Keep templates generic and reusable across different device types

## Best Practices

✅ **DO:**
- Use placeholders for all device-specific values
- Keep prompts generic and reusable
- Document the expected workflow clearly
- Include OpenSpec workflow triggers ("create proposal", "plan change")

❌ **DON'T:**
- Hardcode specific device names (e.g., "wdt", "uart")
- Hardcode project names (e.g., "wdt_test", "my_project")
- Use absolute paths
- Include environment-specific details

---

**Note**: This automated replacement ensures that the same prompt templates can be reused across different projects and device types without manual editing.
