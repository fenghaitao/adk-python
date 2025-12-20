# Self-Improvement Implementation Guide

## How meta_improve_agent Actually Improves Its Own Instruction

This document explains the practical implementation of self-improvement for the meta_improve_agent.

## The Three Phases

### Phase 1: Recommendation Generation (Current)

**Status**: ✅ Already implemented

The meta_improve_agent generates recommendations but doesn't apply them:

```python
# Output from meta_improve_agent in self-improvement mode
{
  "session_file": "meta_improve_meta_improve_20251220.session.txt",
  "instruction_issues": [
    {
      "category": "Error Counting Accuracy",
      "problem": "Agent counted tool calls instead of individual errors",
      "evidence": ["grep -c 'build_simics_project'", "..."],
      "root_cause": "Instruction doesn't distinguish between attempts and errors",
      "recommendation": "Add section: **CRITICAL - Error Counting Methodology**...",
      "suggested_location": "After CRITICAL INSTRUCTIONS",
      "expected_impact": "100% accuracy in error counting"
    }
  ],
  "proposed_improvements": [
    "Add error counting methodology section",
    "Add bash command best practices",
    "..."
  ]
}
```

**What happens next**: Human reads recommendations and manually edits the instruction.

### Phase 2: Patch Generation (Next Step)

**Status**: ❌ Not yet implemented

Add a tool to generate instruction patches:

```python
# New tool for meta_improve_agent
def generate_instruction_patch(
  instruction_file: str,
  recommendations: List[InstructionIssue]
) -> PatchResult:
  """Generate a unified diff patch for instruction improvements.
  
  Args:
    instruction_file: Path to current instruction (e.g., meta_improve_text_agent.py)
    recommendations: List of InstructionIssue objects with improvements
    
  Returns:
    PatchResult with patch file path and summary
  """
  # Read current instruction
  current = read_file(instruction_file)
  
  # Apply recommendations to create new version
  modified = apply_recommendations(current, recommendations)
  
  # Generate unified diff
  patch = create_diff(current, modified)
  
  # Save patch file
  patch_file = f"instruction_improvements_{timestamp()}.patch"
  write_file(patch_file, patch)
  
  return PatchResult(
    patch_file=patch_file,
    changes_count=len(recommendations),
    summary="Added error counting methodology, bash best practices, ..."
  )
```

**Usage**:
```bash
# Run meta_improve_agent in self-improvement mode
python -m meta_improve_text_agent /self-improve

# Output:
# ✅ Generated patch: instruction_improvements_20251220_143022.patch
# 📝 Changes: 7 improvements
# 📄 Review patch: cat instruction_improvements_20251220_143022.patch
# 🔧 Apply patch: git apply instruction_improvements_20251220_143022.patch
```

**What happens next**: Human reviews the patch and applies it manually.

### Phase 3: Supervised Auto-Apply (Future)

**Status**: ❌ Not yet implemented

Add approval and auto-apply mechanism:

```python
# New tool for meta_improve_agent
def apply_instruction_improvements(
  patch_file: str,
  instruction_file: str,
  require_approval: bool = True,
  run_validation: bool = True
) -> ApplyResult:
  """Apply instruction improvements with safeguards.
  
  Args:
    patch_file: Path to patch file
    instruction_file: Path to instruction file to modify
    require_approval: If True, ask human for approval
    run_validation: If True, validate after applying
    
  Returns:
    ApplyResult with success status and details
  """
  # Show patch summary
  print(f"📋 Patch: {patch_file}")
  print(f"🎯 Target: {instruction_file}")
  print(f"📝 Changes: {count_changes(patch_file)}")
  
  # Require approval
  if require_approval:
    print("\n🔍 Review patch:")
    print(read_file(patch_file))
    print("\n❓ Apply these changes? (y/n): ")
    if input().lower() != 'y':
      return ApplyResult(
        applied=False,
        reason="User rejected changes"
      )
  
  # Backup current version
  backup_file = f"{instruction_file}.backup_{timestamp()}"
  copy_file(instruction_file, backup_file)
  print(f"💾 Backup created: {backup_file}")
  
  # Apply patch
  try:
    apply_patch(patch_file, instruction_file)
    print(f"✅ Patch applied to {instruction_file}")
  except Exception as e:
    print(f"❌ Failed to apply patch: {e}")
    return ApplyResult(applied=False, reason=str(e))
  
  # Validate
  if run_validation:
    print("🧪 Running validation tests...")
    if not validate_instruction(instruction_file):
      print("❌ Validation failed! Rolling back...")
      copy_file(backup_file, instruction_file)
      return ApplyResult(
        applied=False,
        reason="Validation failed, rolled back to backup"
      )
    print("✅ Validation passed!")
  
  return ApplyResult(
    applied=True,
    backup_file=backup_file,
    changes_applied=count_changes(patch_file)
  )
```

**Usage**:
```bash
# Run with approval
python -m meta_improve_text_agent /self-improve --apply --require-approval

# Output:
# 📋 Patch: instruction_improvements_20251220_143022.patch
# 🎯 Target: meta_improve_text_agent.py
# 📝 Changes: 7 improvements
# 
# 🔍 Review patch:
# [shows diff]
# 
# ❓ Apply these changes? (y/n): y
# 💾 Backup created: meta_improve_text_agent.py.backup_20251220_143022
# ✅ Patch applied to meta_improve_text_agent.py
# 🧪 Running validation tests...
# ✅ Validation passed!
```

## Implementation Roadmap

### Step 1: Add Patch Generation Tool (Week 1)

Create `instruction_patch_tools.py`:

```python
from typing import List
from pydantic import BaseModel

class InstructionPatch(BaseModel):
  """Represents a patch to an instruction file."""
  section: str
  line_number: int
  current_text: str
  new_text: str
  reason: str

def generate_patch(
  instruction_file: str,
  issues: List[InstructionIssue]
) -> str:
  """Generate unified diff patch from instruction issues."""
  # Implementation
  pass

def create_patch_toolset():
  """Create toolset for patch generation."""
  return Toolset(
    name="instruction_patch_tools",
    tools=[generate_patch]
  )
```

Add to meta_improve_agent:

```python
tools = kwargs.get("tools", [])
tools.append(create_openspec_toolset())
tools.append(create_patch_toolset())  # NEW
kwargs["tools"] = tools
```

### Step 2: Add Validation Tests (Week 2)

Create `instruction_validation.py`:

```python
def validate_instruction(instruction_file: str) -> bool:
  """Validate that instruction file is correct."""
  # Check 1: File is valid Python
  try:
    compile(open(instruction_file).read(), instruction_file, 'exec')
  except SyntaxError:
    return False
  
  # Check 2: Can import the agent
  try:
    import_agent(instruction_file)
  except ImportError:
    return False
  
  # Check 3: Agent has required methods
  agent = import_agent(instruction_file)
  if not hasattr(agent, 'run'):
    return False
  
  # Check 4: Run smoke test
  try:
    result = agent.run("/test")
    if not result:
      return False
  except Exception:
    return False
  
  return True
```

### Step 3: Add Auto-Apply Tool (Week 3)

Create `instruction_apply_tools.py`:

```python
def apply_instruction_patch(
  patch_file: str,
  instruction_file: str,
  require_approval: bool = True
) -> ApplyResult:
  """Apply patch with safeguards."""
  # Implementation from Phase 3 above
  pass

def create_apply_toolset():
  """Create toolset for applying patches."""
  return Toolset(
    name="instruction_apply_tools",
    tools=[apply_instruction_patch]
  )
```

### Step 4: Add Self-Improvement Command (Week 4)

Update meta_improve_agent instruction:

```python
instruction = """
...

## Commands

### /analyze
Analyze apply_improve_agent sessions (normal mode)

### /self-improve
Analyze own sessions and generate improvement recommendations

Usage:
  /self-improve                    # Generate recommendations only
  /self-improve --generate-patch   # Generate patch file
  /self-improve --apply            # Generate and apply with approval
  /self-improve --apply --auto     # Apply without approval (dangerous!)

### /self-improve Workflow

**STEP 1: Read Own Session**
- Use list_directory to find own session file
- Use bash_command to analyze own behavior

**STEP 2: Read Reference Analyses**
- Use list_directory on openspec-memories/meta_improve_references/
- Use read_file to read all reference analyses

**STEP 3: Compare to References**
- What did references include that I didn't?
- What structure did references use?
- What depth did references provide?

**STEP 4: Identify Instruction Gaps**
- Create InstructionIssue for each gap
- Provide evidence from own session
- Recommend specific text to add

**STEP 5: Generate Patch (if --generate-patch)**
- Use generate_patch tool
- Create unified diff
- Save patch file

**STEP 6: Apply Patch (if --apply)**
- Use apply_instruction_patch tool
- Backup current instruction
- Apply patch
- Validate
- Rollback if validation fails

...
"""
```

## Safety Mechanisms

### 1. Backup Before Modify

Always create backup before applying changes:

```python
backup_file = f"{instruction_file}.backup_{timestamp()}"
shutil.copy(instruction_file, backup_file)
```

### 2. Validation After Modify

Always validate after applying changes:

```python
if not validate_instruction(instruction_file):
  # Rollback
  shutil.copy(backup_file, instruction_file)
  raise ValidationError("Instruction validation failed")
```

### 3. Human Approval (Default)

Require human approval by default:

```python
if require_approval:
  print("Review and approve? (y/n): ")
  if input().lower() != 'y':
    return ApplyResult(applied=False)
```

### 4. Version Control Integration

Use git for safety:

```python
# Before applying
subprocess.run(["git", "add", instruction_file])
subprocess.run(["git", "commit", "-m", "Backup before self-improvement"])

# After applying
if validation_passed:
  subprocess.run(["git", "add", instruction_file])
  subprocess.run(["git", "commit", "-m", "Self-improvement: {summary}"])
else:
  subprocess.run(["git", "reset", "--hard", "HEAD"])
```

### 5. Rate Limiting

Prevent too many self-modifications:

```python
MAX_SELF_IMPROVEMENTS_PER_DAY = 3

def check_rate_limit():
  today_improvements = count_improvements_today()
  if today_improvements >= MAX_SELF_IMPROVEMENTS_PER_DAY:
    raise RateLimitError("Max self-improvements per day reached")
```

## Example: Complete Self-Improvement Flow

```bash
# 1. Run meta_improve_agent normally
python -m meta_improve_text_agent /analyze
# Generates: META_IMPROVE_ANALYSIS_20251220_120000.md

# 2. Run meta_improve_agent in self-improvement mode
python -m meta_improve_text_agent /self-improve --generate-patch
# Reads: meta_improve_meta_improve_20251220_120000.session.txt
# Reads: openspec-memories/meta_improve_references/*.md
# Compares: own output vs references
# Generates: instruction_improvements_20251220_120500.patch

# 3. Review the patch
cat instruction_improvements_20251220_120500.patch

# 4. Apply the patch (with approval)
python -m meta_improve_text_agent /apply-patch instruction_improvements_20251220_120500.patch
# Prompts: Review and approve? (y/n): y
# Creates: meta_improve_text_agent.py.backup_20251220_120600
# Applies: patch to meta_improve_text_agent.py
# Validates: instruction is still valid
# Result: ✅ Improvements applied successfully

# 5. Test the improved agent
python -m meta_improve_text_agent /analyze
# Verify: improvements are working
```

## Monitoring Self-Improvement

Track improvements over time:

```python
# improvement_log.json
{
  "improvements": [
    {
      "timestamp": "2025-12-20T12:05:00Z",
      "patch_file": "instruction_improvements_20251220_120500.patch",
      "changes_count": 7,
      "categories": ["Error Counting", "Bash Commands", "Workflow"],
      "expected_impact": "30% better analysis quality",
      "actual_impact": null,  # Measured later
      "validation_passed": true,
      "applied": true
    }
  ]
}
```

## Conclusion

The meta_improve_agent improves its own instruction through a **three-phase approach**:

1. **Phase 1 (Current)**: Generate recommendations → Human applies manually
2. **Phase 2 (Next)**: Generate patches → Human reviews and applies
3. **Phase 3 (Future)**: Generate and auto-apply → With safeguards and approval

This progressive approach ensures safety while moving toward autonomy.

**Key Insight**: The agent doesn't need to be fully autonomous from day one. Start with human-in-the-loop and gradually increase automation as confidence grows.
