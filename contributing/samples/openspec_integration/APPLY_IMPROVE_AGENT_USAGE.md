# ApplyImproveAgent Usage Guide (Simplified)

## Overview

The `ApplyImproveAgent` is a dual-mode agent that analyzes apply_agent sessions AND self-improves by comparing to reference examples.

## Two Modes

### MODE 1: /analyze-apply
Analyzes apply_agent execution sessions to identify patterns and provide recommendations.

**Input**: apply_agent session files (`.session.txt`)  
**Output**: `APPLY_AGENT_ANALYSIS_YYYYMMDD_HHMMSS.md`  
**Schema**: `SessionAnalysis`

### MODE 2: /self-improve
Self-improves by comparing own analysis reports to high-quality reference examples.

**Input**: Own previous analysis reports + reference examples  
**Output**: `SELF_IMPROVEMENT_ANALYSIS_YYYYMMDD_HHMMSS.md`  
**Schema**: `SelfImprovementAnalysis`

## Quick Start

### Using MODE 1: Analyze Apply Agent

```python
from google.adk.runners import Runner
from contributing.samples.openspec_integration.meta_improve_text_agent import apply_improve_agent

runner = Runner()
result = runner.run(
  apply_improve_agent,
  "Analyze the latest apply_agent session"
)
# Output: APPLY_AGENT_ANALYSIS_*.md with error patterns and recommendations
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
2. **Run MODE 1** to analyze the session
3. **Run MODE 2** to self-improve by comparing to references
4. **Implement improvements** to prompts and documents
5. **Validate** with next apply_agent run

## Output Schemas

### SessionAnalysis (MODE 1)
```python
class SessionAnalysis(BaseModel):
  session_file: str
  total_build_attempts: int
  total_fix_attempts: int
  time_to_success_minutes: float
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str]
```

### SelfImprovementAnalysis (MODE 2)
```python
class SelfImprovementAnalysis(BaseModel):
  reference_file: str
  reference_quality: float
  my_report_file: str
  my_estimated_quality: float
  overall_gap_score: int  # out of 100
  key_finding: str
  gap_analyses: List[GapAnalysis]  # 6 dimensions
  improvement_actions: List[ImprovementAction]
  expected_quality_improvement: float
  self_improvement_report_file: Optional[str]
```

## Gap Analysis Dimensions (MODE 2)

1. **Structure & Organization** (10 points)
2. **Depth of Error Analysis** (20 points)
3. **Best Practices Compliance Analysis** (20 points)
4. **Actionability of Recommendations** (20 points)
5. **Quantification & Metrics** (15 points)
6. **Code Examples & Specificity** (15 points)

**Total**: 100 points

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
