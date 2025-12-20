# ApplyImproveAgent Usage Guide (Simplified)

## Overview

The `ApplyImproveAgent` is a dual-mode agent that analyzes apply_agent sessions AND self-improves by comparing to reference examples.

## Two Modes

### MODE 1: /analyze-apply
Analyzes apply_agent execution sessions with comprehensive 100-point scoring system.

**Input**: apply_agent session files (`.session.txt`)  
**Output**: `APPLY_AGENT_ANALYSIS_YYYYMMDD_HHMMSS.md`  
**Schema**: `SessionAnalysis` (includes `ApplyAgentScore`)

**Scoring System (100 points)**:
- **Result Quality (50 points)**
  - DML Code Quality (15): Correctness, idioms, maintainability
  - Test Quality (15): Coverage, assertions, clarity
  - Documentation (10): Completeness, clarity
  - Functionality (10): Spec compliance, correctness
- **Process Quality (50 points)**
  - Efficiency (15): Build attempts, time, iterations
  - Methodology (15): Workflow adherence, best practices usage
  - Error Handling (10): Recovery, learning from errors
  - Code Evolution (10): Improvement trajectory, refinement

### MODE 2: /self-improve
Self-improves by generating concrete instruction improvements for MODE 1 (and optionally MODE 2).

**Input**: Own previous analysis reports + reference examples  
**Output**: `SELF_IMPROVEMENT_ANALYSIS_YYYYMMDD_HHMMSS.md`  
**Schema**: `SelfImprovementAnalysis` (includes `InstructionImprovement` list)

**Primary Output**: Concrete instruction text to add/modify in MODE 1's `_get_analyze_apply_instruction` method

**Example Output**:
```python
mode1_instruction_improvements = [
  InstructionImprovement(
    improvement_name="Enforce Code Examples in Recommendations",
    gap_identified="Recommendations lack before/after code examples",
    root_cause="MODE 1 instruction doesn't require code examples",
    target_mode="MODE 1",
    location_in_instruction="Add to STEP 3, after recommendations section",
    instruction_text_to_add="**CRITICAL**: For every code recommendation, provide before/after examples...",
    example_of_enforced_behavior="Shows exact format MODE 1 should follow",
    expected_impact="Gap score 65/100 → 80/100, recommendations become actionable",
    priority="High"
  )
]
```

## Quick Start

### Using MODE 1: Analyze Apply Agent with Scoring

```python
from google.adk.runners import Runner
from contributing.samples.openspec_integration.meta_improve_text_agent import apply_improve_agent

runner = Runner()
result = runner.run(
  apply_improve_agent,
  "Analyze the latest apply_agent session"
)

# Access the score
score = result.apply_agent_score
print(f"Overall Score: {score.overall_score}/100 ({score.overall_score_out_of_10}/10)")
print(f"Result Quality: {score.result_quality_total}/50")
print(f"Process Quality: {score.process_quality_total}/50")
print(f"DML Code: {score.dml_code_quality}/15")
print(f"Efficiency: {score.efficiency_score}/15")
```

### Using MODE 2: Self-Improve

```python
from google.adk.runners import Runner
from contributing.samples.openspec_integration.meta_improve_text_agent import apply_improve_agent_self_improve

runner = Runner()
result = runner.run(
  apply_improve_agent_self_improve,
  "Compare my latest analysis to references"
)
# Output: SELF_IMPROVEMENT_ANALYSIS_*.md with gap analysis and improvement plan
```

## Complete Improvement Cycle

1. **Run apply_agent** to implement a feature
2. **Run MODE 1** to analyze the session and get performance score
3. **Review score breakdown** to identify weaknesses
4. **Run MODE 2** to self-improve by comparing to references
5. **Implement improvements** to prompts and documents
6. **Validate** with next apply_agent run and compare scores

## Output Schemas

### SessionAnalysis (MODE 1)
```python
class ApplyAgentScore(BaseModel):
  # Result Quality (50 points)
  dml_code_quality: int  # 0-15
  test_quality: int  # 0-15
  documentation_quality: int  # 0-10
  functionality_score: int  # 0-10
  
  # Process Quality (50 points)
  efficiency_score: int  # 0-15
  methodology_score: int  # 0-15
  error_handling_score: int  # 0-10
  code_evolution_score: int  # 0-10
  
  # Totals
  result_quality_total: int  # max 50
  process_quality_total: int  # max 50
  overall_score: int  # max 100
  overall_score_out_of_10: float  # 0-10 scale
  
  # Justifications
  dml_code_justification: str
  test_quality_justification: str
  efficiency_justification: str
  methodology_justification: str

class SessionAnalysis(BaseModel):
  session_file: str
  total_build_attempts: int
  total_fix_attempts: int
  time_to_success_minutes: float
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  apply_agent_score: ApplyAgentScore  # NEW: Comprehensive scoring
  analysis_report_file: Optional[str]
```

### SelfImprovementAnalysis (MODE 2)
```python
class InstructionImprovement(BaseModel):
  improvement_name: str
  gap_identified: str
  root_cause: str
  target_mode: str  # 'MODE 1' or 'MODE 2'
  location_in_instruction: str
  instruction_text_to_add: str
  example_of_enforced_behavior: str
  expected_impact: str
  priority: str

class SelfImprovementAnalysis(BaseModel):
  reference_file: str
  reference_quality: float
  my_report_file: str
  my_estimated_quality: float
  overall_gap_score: int  # out of 100
  key_finding: str
  gap_analyses: List[GapAnalysis]  # 6 dimensions
  improvement_actions: List[ImprovementAction]
  mode1_instruction_improvements: List[InstructionImprovement]  # PRIMARY OUTPUT
  mode2_instruction_improvements: Optional[List[InstructionImprovement]]  # Optional
  expected_quality_improvement: float
  self_improvement_report_file: Optional[str]
```

## Scoring Guide (MODE 1)

### Result Quality (50 points)

**DML Code Quality (0-15)**
- 13-15: Excellent - correct, idiomatic, maintainable
- 10-12: Good - correct, mostly idiomatic
- 7-9: Adequate - works but has style issues
- 4-6: Poor - works but violates best practices
- 0-3: Very poor - doesn't work or major violations

**Test Quality (0-15)**
- 13-15: Excellent - comprehensive, meaningful, clear
- 10-12: Good - covers main cases
- 7-9: Adequate - basic coverage
- 4-6: Poor - minimal coverage
- 0-3: Very poor - tests don't work

**Documentation (0-10)**
- 9-10: Excellent - complete, clear, helpful
- 7-8: Good - mostly complete
- 5-6: Adequate - basic documentation
- 3-4: Poor - incomplete
- 0-2: Very poor - missing

**Functionality (0-10)**
- 9-10: Excellent - fully implements spec
- 7-8: Good - implements most features
- 5-6: Adequate - implements core features
- 3-4: Poor - missing features
- 0-2: Very poor - incomplete or broken

### Process Quality (50 points)

**Efficiency (0-15)**
- Build attempts: 1-2 (5pts), 3-4 (4pts), 5-6 (3pts), 7-8 (2pts), 9+ (0-1pts)
- Time: <30min (5pts), 30-60 (4pts), 60-90 (3pts), 90-120 (2pts), >120 (0-1pts)
- Iterations: 1-5 (5pts), 6-10 (4pts), 11-15 (3pts), 16-20 (2pts), 20+ (0-1pts)

**Methodology (0-15)**
- 13-15: Excellent - follows all protocols
- 10-12: Good - follows most protocols
- 7-9: Adequate - follows some protocols
- 4-6: Poor - frequently skips protocols
- 0-3: Very poor - ignores protocols

**Error Handling (0-10)**
- 9-10: Excellent - recovers quickly, learns
- 7-8: Good - recovers well
- 5-6: Adequate - eventually recovers
- 3-4: Poor - struggles to recover
- 0-2: Very poor - can't recover

**Code Evolution (0-10)**
- 9-10: Excellent - clear improvement
- 7-8: Good - generally improves
- 5-6: Adequate - some improvement
- 3-4: Poor - little improvement
- 0-2: Very poor - no improvement

## Gap Analysis Dimensions (MODE 2)

1. **Structure & Organization** (10 points)
2. **Depth of Error Analysis** (20 points)
3. **Best Practices Compliance Analysis** (20 points)
4. **Actionability of Recommendations** (20 points)
5. **Quantification & Metrics** (15 points)
6. **Code Examples & Specificity** (15 points)

**Total**: 100 points

## Example Score Interpretation

```
Overall Score: 56/100 (5.6/10)

Result Quality: 32/50
- DML Code: 8/15 (works but violated scope patterns)
- Tests: 10/15 (good coverage, could be more specific)
- Docs: 6/10 (basic but adequate)
- Functionality: 8/10 (works correctly)

Process Quality: 24/50
- Efficiency: 5/15 (8 builds, 116 min - poor)
- Methodology: 6/15 (didn't consult best practices)
- Error Handling: 6/10 (recovered but repeated errors)
- Code Evolution: 7/10 (improved over time)

Key Issues:
- Didn't consult 07_DML_Register_Access_Scope.md before implementing
- 12 preventable scope errors
- Poor efficiency (8 builds, 116 minutes)

Recommendations:
- Add mandatory best practice consultation to workflow
- Improve register access scope documentation
- Add validation checks before building

Expected Improvement: 56/100 → 78/100 (22 point gain)
```

## Example MODE 2 Output (Instruction Improvements)

```
MODE 1 Instruction Improvement #1:

Improvement Name: Enforce Code Examples in Recommendations
Gap Identified: MODE 1's recommendations lack before/after code examples
Root Cause: MODE 1 instruction says "provide recommendations" but doesn't require code examples
Target Mode: MODE 1
Location: Add to STEP 3, after "Specific Improvement Recommendations"

Instruction Text to Add:
```
**CRITICAL - Code Examples Required**:
For every recommendation involving code changes, provide:
1. **Before**: Problematic code from session
2. **After**: Corrected code
3. **Explanation**: Why this fixes the issue
```

Example of Enforced Behavior:
```
Recommendation: Fix register access scope

**Before** (line 45 in wdt.dml):
```dml
bank.WDOGLOAD.val = bank.WDOGLOAD.val - 1;
```

**After**:
```dml
WatchdogRegisters.WDOGLOAD.val = WatchdogRegisters.WDOGLOAD.val - 1;
```

**Explanation**: 'bank' is keyword, use actual bank name
```

Expected Impact: Gap score 65/100 → 80/100 (Code Examples dimension)
Priority: High
```

## Reference System

References are located in `openspec-memories/references/`:
- `00_REFERENCE_GUIDE.md` - How to use references
- `apply_improve_agent_reference_example.md` - 9.5/10 quality example

## Backward Compatibility

The following aliases are maintained:
- `meta_improve_text_agent` → `apply_improve_agent` (MODE 1)
- `root_agent` → `apply_improve_agent` (MODE 1)

## Related Documentation

- [Dual Mode Implementation Summary](./DUAL_MODE_IMPLEMENTATION_SUMMARY.md)

