---
name: "openspec-generate-proposal-prompt"
displayName: "OpenSpec Generate Proposal Prompt"
description: "Analyze specifications and generate prompts for the openspec-propose power to create comprehensive task coverage proposals"
keywords: ["openspec", "prompt-generation", "meta", "automation", "task-coverage", "spec-analysis", "requirement-extraction"]
author: "ADK Team"
---

# OpenSpec Generate Proposal Prompt Power

This meta-power analyzes specification files and generates prompts for the `openspec-propose` power, enabling automated creation of comprehensive task coverage proposals.

## What This Power Does

**Input**: Specification file with requirements (FUNC-XXX, REG-XXX, BEHAV-XXX, TEST-XXX)  
**Output**: Multiple prompt files (one per requirement category) for the openspec-propose power  
**Capability**: Semantic understanding of requirements, grouping, and coverage analysis

## Use Case

When you have a detailed specification with many requirements and want to demonstrate OpenSpec's capability to generate comprehensive task coverage, this power:

1. Analyzes the spec file to identify requirement categories
2. Groups requirements by semantic meaning (e.g., "Timer functionality", "Interrupt handling")
3. Optionally analyzes existing tasks to identify coverage gaps
4. Generates N prompt files (one per category) for the openspec-propose power
5. Each prompt instructs openspec-propose to extract ALL requirements for that category

## Execution Order and Dependencies

**CRITICAL**: Proposals must be executed in dependency order for logical implementation flow.

### Dependency Order

1. **REG (Register)** - Define register structure and access patterns
2. **FUNC (Functional)** - Define device functionality using those registers
3. **BEHAV (Behavioral)** - Define edge cases and state transitions
4. **TEST (Test)** - Validate all of the above

### Why Order Matters

**For Proposal Creation**: Order doesn't technically matter (all read from same spec)  
**For Proposal Application**: Order is critical for implementation

- **REG first**: Must know what registers exist before implementing functionality
- **FUNC second**: Must know core functionality before handling edge cases
- **BEHAV third**: Must know all behaviors before writing comprehensive tests
- **TEST last**: Tests validate everything implemented above

### Automated Execution

This power generates an `execute-proposals.sh` script that:
- Executes prompts in the correct dependency order
- Handles errors gracefully
- Provides clear progress feedback
- Includes validation and apply commands

## Workflow

```
spec.md (93 requirements)
    ↓
[openspec-generate-proposal-prompt] ← This power
    ↓
4 prompt files (FUNC, REG, BEHAV, TEST)
    ↓
[openspec-propose] ← Execute each prompt
    ↓
4 proposals with comprehensive task coverage
```

## Input Parameters

**Required:**
- `spec_file`: Path to the specification file (e.g., `specs/001-read-the-simics/spec.md`)
- `output_dir`: Directory to write generated prompt files (e.g., `openspec-prompts/`)

**Optional:**
- `existing_tasks`: Path to existing tasks.md file for coverage analysis
- `workdir`: Working directory for the proposals (default: current directory)
- `change_id_prefix`: Prefix for change IDs (default: `add-missing`)

## Output

Generates prompt files named:
- `propose-func-task-coverage.txt`
- `propose-reg-task-coverage.txt`
- `propose-behav-task-coverage.txt`
- `propose-test-task-coverage.txt`
- ... (one per requirement category found)

Each prompt file contains:
- Context (spec location, existing tasks, demonstration goal)
- Task description (what capability to demonstrate)
- Requirements to cover (with semantic groupings)
- Proposal details (change-id, purpose, coverage target)
- Critical requirements (100% coverage, detailed sub-tasks, validation)

## Example Usage

### Using kiro-cli

```bash
cd /home/hfeng1/adk_openspec_project

kiro-cli chat -a "Read /home/hfeng1/adk-python/powers/openspec-generate-proposal-prompt/POWER.md and generate proposal prompts for:

- Spec file: specs/001-read-the-simics/spec.md
- Output directory: /home/hfeng1/adk-python/openspec-prompts/
- Existing tasks: openspec/changes/implement-watchdog-timer/tasks.md
- Working directory: /home/hfeng1/adk_openspec_project

Follow all instructions in POWER.md to analyze the spec and generate comprehensive prompts."
```

### Expected Output

```
Generated 4 prompt files:
✓ openspec-prompts/propose-func-task-coverage.txt (24 requirements)
✓ openspec-prompts/propose-reg-task-coverage.txt (9 requirements)
✓ openspec-prompts/propose-behav-task-coverage.txt (8 requirements)
✓ openspec-prompts/propose-test-task-coverage.txt (8 requirements)

Total: 49 requirements across 4 categories

Next steps:
1. Review generated prompts
2. Execute each prompt with openspec-propose power
3. Validate generated proposals
```

## Execution Steps (CRITICAL - Follow in Order)

### STEP 1: Read and Analyze Spec File

**Read the ENTIRE spec file** to understand:
- All requirement categories (FUNC, REG, BEHAV, TEST, INTF, etc.)
- Requirement IDs and their descriptions
- Semantic groupings (which requirements relate to which features)
- Total requirement count per category

**Example analysis:**
```
FUNC-001: Timer shall be 32-bit decrementing counter
FUNC-002: Timer shall decrement based on clock divider
FUNC-003: Timer shall reload from LOAD register
FUNC-004: Timer shall continue after reaching zero

→ Semantic group: "Timer functionality (FUNC-001 to FUNC-004)"
```

### STEP 2: Analyze Existing Tasks (Optional)

If `existing_tasks` provided:
- Read the existing tasks.md file
- Identify which requirements are already covered
- Calculate coverage percentage per category
- Focus prompts on uncovered requirements

**Coverage calculation:**
```
Total FUNC requirements: 24
Covered by existing tasks: 4
Uncovered: 20
Coverage: 17%
```

### STEP 3: Group Requirements Semantically

For each category, group requirements by semantic meaning:

**Example for FUNC category:**
```
- Timer functionality (FUNC-001 to FUNC-004)
- Interrupt and reset (FUNC-005 to FUNC-008)
- Register access (FUNC-009 to FUNC-016)
- Clock divider (FUNC-017 to FUNC-019)
- Integration test mode (FUNC-020 to FUNC-022)
- Identification (FUNC-023 to FUNC-024)
```

**Grouping guidelines:**
- Group by feature area (timer, interrupt, register, etc.)
- Keep groups to 3-8 requirements each
- Use clear, descriptive names
- Maintain requirement ID ranges

### STEP 4: Generate Prompt Files

For each requirement category, generate a prompt file using this template:

```
Read /home/hfeng1/adk-python/powers/openspec-propose/POWER.md and create an OpenSpec change proposal following these instructions:

CONTEXT:
- Working directory: {workdir}
- Source spec: {spec_file} ({total_requirements} requirements total)
- Existing tasks: {existing_tasks} (covers ~{coverage_percent}% of requirements)
- Demonstration goal: Show OpenSpec's capability to generate comprehensive task coverage from specifications

TASK:
Create a proposal demonstrating OpenSpec's capability to extract {CATEGORY} requirements from a spec and generate comprehensive, actionable implementation tasks.

REQUIREMENTS TO COVER:
{requirement_id_range} ({count} {category} requirements total)
{semantic_groupings}

PROPOSAL DETAILS:
- Change ID: {change_id_prefix}-{category}-tasks
- Purpose: Demonstrate systematic requirement extraction → task generation capability
- Target: Create new tasks.md with tasks for all {CATEGORY}-XXX requirements
- Coverage: Extract ALL {count} {category} requirements from source spec into actionable tasks

CRITICAL REQUIREMENTS:
1. Read the ENTIRE source spec at {spec_file}
2. Extract ALL {count} {CATEGORY} requirements (not just a sample)
3. Create detailed, actionable tasks with 3-5 sub-tasks each
4. Reference specific requirement IDs (e.g., 'Implements {CATEGORY}-012')
5. Include BOTH DML implementation tasks AND test tasks
6. Ensure 100% coverage of {CATEGORY} requirements ({count}/{count})
7. Follow Task Decomposition Requirements from POWER.md
8. Validate with: openspec validate {change_id} --strict

Follow ALL instructions in POWER.md, especially:
- Pre-Flight Checklist (read spec, understand requirements)
- Execution Steps (STEP 1-6 in exact order)
- Spec Delta Completeness Requirements (100% coverage for this category)
- Task Structure Requirements (DML + Test sections)
- Task Decomposition Requirements (specific sub-tasks)
```

### STEP 5: Write Prompt Files

Write each generated prompt to the output directory:
- Filename: `propose-{category}-task-coverage.txt` (lowercase)
- Location: `{output_dir}/propose-{category}-task-coverage.txt`
- Encoding: UTF-8

### STEP 6: Generate Execution Script

Create a bash script that executes prompts in the correct dependency order:

**Filename**: `{output_dir}/execute-proposals.sh`

**Script template**:
```bash
#!/bin/bash

# Auto-generated script to execute proposal prompts in dependency order
# Generated by openspec-generate-proposal-prompt power

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="{repo_root}"
WORKDIR="{workdir}"

echo "================================"
echo "🚀 Executing Proposal Prompts"
echo "================================"
echo "Working Directory: $WORKDIR"
echo "Prompt Directory: $SCRIPT_DIR"
echo ""

# Execution order based on logical dependencies:
# 1. REG (Register) - Define register structure
# 2. FUNC (Functional) - Define device functionality
# 3. BEHAV (Behavioral) - Define edge cases and state transitions
# 4. TEST (Test) - Validate all of the above

{execution_commands}

echo ""
echo "================================"
echo "✅ All Proposals Created"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Validate all proposals:"
{validation_commands}
echo ""
echo "2. Apply proposals in order:"
{apply_commands}
```

**Execution commands template** (one per category in dependency order):
```bash
echo "📋 Step {N}: Creating {CATEGORY} proposal..."
"$REPO_ROOT/openspec-scripts/run-kiro-propose-custom.sh" \
  "$WORKDIR" \
  "$SCRIPT_DIR/propose-{category}-task-coverage.txt"

if [ $? -ne 0 ]; then
  echo "❌ Error: Failed to create {CATEGORY} proposal"
  exit 1
fi
echo "✅ {CATEGORY} proposal created"
echo ""
```

**Dependency order**:
1. REG (Register requirements)
2. FUNC (Functional requirements)
3. BEHAV (Behavioral requirements)
4. TEST (Test requirements)
5. Any other categories (alphabetically)

### STEP 7: Generate Summary Report

### STEP 7: Generate Summary Report

Create a summary report showing:
- Total requirements analyzed
- Requirements per category (in dependency order)
- Coverage analysis (if existing tasks provided)
- Generated prompt files (in dependency order)
- Generated execution script
- Next steps for execution

**Report format**:
```markdown
# Task Coverage Proposal Generation Summary

**Generated**: {timestamp}
**Spec File**: {spec_file}
**Total Requirements**: {total_count}

## Requirements by Category (Dependency Order)

1. **REG (Register)**: {reg_count} requirements
2. **FUNC (Functional)**: {func_count} requirements
3. **BEHAV (Behavioral)**: {behav_count} requirements
4. **TEST (Test)**: {test_count} requirements

## Coverage Analysis

{coverage_analysis_if_provided}

## Generated Files

### Prompt Files (in dependency order):
1. propose-reg-task-coverage.txt
2. propose-func-task-coverage.txt
3. propose-behav-task-coverage.txt
4. propose-test-task-coverage.txt

### Execution Script:
- execute-proposals.sh (executable)

## Execution

Run the generated script to create all proposals in the correct order:

\`\`\`bash
cd {output_dir}
chmod +x execute-proposals.sh
./execute-proposals.sh
\`\`\`

Or execute prompts individually in dependency order:
1. Register requirements first
2. Functional requirements second
3. Behavioral requirements third
4. Test requirements last

## Dependency Rationale

- **REG → FUNC**: Can't define functionality without knowing register structure
- **FUNC → BEHAV**: Can't define edge cases without knowing core functionality
- **BEHAV → TEST**: Can't write comprehensive tests without knowing all behaviors
```

## Prompt Template Variables

Variables to substitute in the template:

| Variable | Description | Example |
|----------|-------------|---------|
| `{workdir}` | Working directory | `/home/hfeng1/adk_openspec_project` |
| `{spec_file}` | Spec file path | `specs/001-read-the-simics/spec.md` |
| `{total_requirements}` | Total requirement count | `93` |
| `{existing_tasks}` | Existing tasks path | `openspec/changes/implement-watchdog-timer/tasks.md` |
| `{coverage_percent}` | Coverage percentage | `27` |
| `{CATEGORY}` | Category name (uppercase) | `FUNCTIONAL`, `REGISTER`, `BEHAVIORAL`, `TEST` |
| `{category}` | Category name (lowercase) | `func`, `reg`, `behav`, `test` |
| `{requirement_id_range}` | ID range | `FUNC-001 through FUNC-024` |
| `{count}` | Requirement count | `24` |
| `{semantic_groupings}` | Grouped requirements | See grouping example above |
| `{change_id_prefix}` | Change ID prefix | `add-missing` |
| `{change_id}` | Full change ID | `add-missing-func-tasks` |

## Quality Checks

Before writing prompt files, verify:

1. **Completeness**: All requirement categories identified
2. **Accuracy**: Requirement counts match spec file
3. **Semantic groupings**: Meaningful and descriptive
4. **Template substitution**: All variables replaced correctly
5. **File naming**: Consistent lowercase with hyphens

## Example Output Structure

```
openspec-prompts/
├── propose-reg-task-coverage.txt       # 9 REG requirements (execute 1st)
├── propose-func-task-coverage.txt      # 24 FUNC requirements (execute 2nd)
├── propose-behav-task-coverage.txt     # 8 BEHAV requirements (execute 3rd)
├── propose-test-task-coverage.txt      # 8 TEST requirements (execute 4th)
├── execute-proposals.sh                # Auto-generated execution script
└── README-task-coverage.md             # Summary and usage instructions
```

**Execution**:
```bash
cd openspec-prompts
chmod +x execute-proposals.sh
./execute-proposals.sh
```

The script will execute prompts in dependency order: REG → FUNC → BEHAV → TEST

## Integration with openspec-propose

Generated prompts are designed to work with:
- `openspec-scripts/run-kiro-propose-custom.sh` script
- Direct `kiro-cli` execution
- Batch processing for multiple categories

**Example execution:**
```bash
# Execute generated prompts
for prompt in openspec-prompts/propose-*-task-coverage.txt; do
  ./openspec-scripts/run-kiro-propose-custom.sh \
    /home/hfeng1/adk_openspec_project \
    "$prompt"
done
```

## Benefits

1. **Automation**: Generate prompts for any spec automatically
2. **Consistency**: All prompts follow the same structure
3. **Semantic understanding**: Groups requirements meaningfully
4. **Coverage analysis**: Identifies gaps in existing tasks
5. **Scalability**: Works for any device spec, any size
6. **Reusability**: Generate prompts for multiple devices

## Limitations

- Requires well-structured spec files with clear requirement IDs
- Semantic grouping quality depends on requirement descriptions
- Cannot generate prompts for specs without explicit requirement IDs
- Best suited for Simics device specifications

## Version Information

- **Power Version**: 1.0.0
- **Compatible with**: openspec-propose power v1.0+
- **Last Updated**: December 25, 2024

---

**Power Type**: Meta-Power (generates input for other powers)  
**Dependencies**: openspec-propose power  
**License**: Apache 2.0
