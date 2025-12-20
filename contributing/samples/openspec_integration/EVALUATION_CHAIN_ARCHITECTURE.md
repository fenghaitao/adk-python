# Evaluation Chain Architecture

## The Core Problem

**Question**: How do we know if improvements actually work?

**Answer**: We need a **scoring system at each level** to measure effectiveness.

## The Evaluation Chain

```
┌─────────────────────────────────────────────────────────────┐
│ Level 1: apply_agent                                         │
│ Task: Implement features                                     │
│ Scored by: apply_improve_agent                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Score: 6.5/10
                 │ - build_attempts: 15 (target: <5)
                 │ - time: 8.98 min (target: <5 min)
                 │ - error_types: 3 (target: <2)
                 │ - success: yes
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Level 2: apply_improve_agent                                 │
│ Task: Analyze and improve apply_agent                        │
│ Scored by: meta_improve_agent                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Score: 7.0/10
                 │ - analysis_depth: 7/10
                 │ - recommendation_quality: 8/10
                 │ - coverage: 6/10
                 │ - actionability: 7/10
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Level 3: meta_improve_agent                                  │
│ Task: Analyze and improve apply_improve_agent                │
│ Scored by: Reference comparison + Human validation           │
└─────────────────────────────────────────────────────────────┘
                 │
                 │ Score: 8.5/10
                 │ - vs reference_analysis_20251220: 8.5/10
                 │ - coverage: 9/10
                 │ - specificity: 9/10
                 │ - evidence: 8/10
```

## Scoring System Design

### Level 1: Scoring apply_agent

**Scored by**: apply_improve_agent

**Metrics**:

```python
class ApplyAgentScore(BaseModel):
  """Score for apply_agent performance."""
  
  # Efficiency Metrics
  build_attempts: int  # Actual count
  build_attempts_target: int = 5  # Target
  build_attempts_score: float  # 0-10 scale
  
  time_minutes: float  # Actual time
  time_target: float = 5.0  # Target
  time_score: float  # 0-10 scale
  
  # Quality Metrics
  error_types_count: int  # Unique error types
  error_types_target: int = 2  # Target
  error_types_score: float  # 0-10 scale
  
  # Success Metrics
  final_success: bool  # Did it complete?
  tests_passed: int  # How many tests passed
  tests_total: int  # Total tests
  success_score: float  # 0-10 scale
  
  # Overall Score
  overall_score: float  # Weighted average
  
  # Scoring Formula
  def calculate_overall_score(self):
    """Calculate weighted overall score."""
    self.build_attempts_score = max(0, 10 - (self.build_attempts - self.build_attempts_target) * 2)
    self.time_score = max(0, 10 - (self.time_minutes - self.time_target) * 1)
    self.error_types_score = max(0, 10 - (self.error_types_count - self.error_types_target) * 3)
    self.success_score = 10 if self.final_success else 0
    
    # Weighted average
    self.overall_score = (
      self.build_attempts_score * 0.3 +
      self.time_score * 0.2 +
      self.error_types_score * 0.2 +
      self.success_score * 0.3
    )
    
    return self.overall_score
```

**Example**:
```python
# Session: apply_implement-wdt-watchdog_20251218_175839
score = ApplyAgentScore(
  build_attempts=15,
  build_attempts_target=5,
  time_minutes=8.98,
  time_target=5.0,
  error_types_count=3,
  error_types_target=2,
  final_success=True,
  tests_passed=0,
  tests_total=5
)

score.calculate_overall_score()
# build_attempts_score: 10 - (15-5)*2 = 0
# time_score: 10 - (8.98-5)*1 = 6.02
# error_types_score: 10 - (3-2)*3 = 7
# success_score: 10 (completed)
# overall_score: 0*0.3 + 6.02*0.2 + 7*0.2 + 10*0.3 = 5.6/10
```

### Level 2: Scoring apply_improve_agent

**Scored by**: meta_improve_agent

**Metrics**:

```python
class ApplyImproveAgentScore(BaseModel):
  """Score for apply_improve_agent performance."""
  
  # Analysis Depth
  dimensions_covered: int  # How many dimensions analyzed
  dimensions_expected: int = 7  # Expected dimensions
  analysis_depth_score: float  # 0-10 scale
  
  # Recommendation Quality
  recommendations_count: int  # Number of recommendations
  recommendations_specific: int  # How many are specific (with code blocks)
  recommendations_actionable: int  # How many are actionable
  recommendation_quality_score: float  # 0-10 scale
  
  # Evidence Quality
  evidence_provided: bool  # Did agent provide evidence?
  evidence_specific: bool  # Is evidence specific (quotes, commands)?
  evidence_quality_score: float  # 0-10 scale
  
  # Coverage
  error_patterns_identified: int  # How many error patterns found
  best_practices_analyzed: bool  # Did agent analyze best practices?
  coverage_score: float  # 0-10 scale
  
  # Actionability
  exact_text_provided: bool  # Did agent provide exact text to add?
  location_specified: bool  # Did agent specify where to add?
  impact_quantified: bool  # Did agent quantify impact?
  actionability_score: float  # 0-10 scale
  
  # Overall Score
  overall_score: float  # Weighted average
  
  def calculate_overall_score(self):
    """Calculate weighted overall score."""
    # Analysis depth: 0-10 based on coverage
    self.analysis_depth_score = (self.dimensions_covered / self.dimensions_expected) * 10
    
    # Recommendation quality: 0-10 based on specificity and actionability
    specificity_rate = self.recommendations_specific / max(1, self.recommendations_count)
    actionability_rate = self.recommendations_actionable / max(1, self.recommendations_count)
    self.recommendation_quality_score = (specificity_rate + actionability_rate) / 2 * 10
    
    # Evidence quality: 0-10 based on presence and specificity
    self.evidence_quality_score = (
      (5 if self.evidence_provided else 0) +
      (5 if self.evidence_specific else 0)
    )
    
    # Coverage: 0-10 based on patterns and best practices
    self.coverage_score = (
      min(10, self.error_patterns_identified * 2) * 0.6 +
      (10 if self.best_practices_analyzed else 0) * 0.4
    )
    
    # Actionability: 0-10 based on completeness
    actionability_checks = [
      self.exact_text_provided,
      self.location_specified,
      self.impact_quantified
    ]
    self.actionability_score = sum(actionability_checks) / len(actionability_checks) * 10
    
    # Weighted average
    self.overall_score = (
      self.analysis_depth_score * 0.25 +
      self.recommendation_quality_score * 0.25 +
      self.evidence_quality_score * 0.15 +
      self.coverage_score * 0.15 +
      self.actionability_score * 0.20
    )
    
    return self.overall_score
```

**Example**:
```python
# Session: apply_improve_apply_improve_20251219_204307
score = ApplyImproveAgentScore(
  dimensions_covered=3,  # Only covered 3 of 7 dimensions
  dimensions_expected=7,
  recommendations_count=5,
  recommendations_specific=3,  # Only 3 had code blocks
  recommendations_actionable=4,
  evidence_provided=True,
  evidence_specific=False,  # Summaries, not quotes
  error_patterns_identified=3,
  best_practices_analyzed=True,  # But superficially
  exact_text_provided=False,
  location_specified=True,
  impact_quantified=True
)

score.calculate_overall_score()
# analysis_depth_score: (3/7)*10 = 4.3
# recommendation_quality_score: ((3/5)+(4/5))/2*10 = 7.0
# evidence_quality_score: 5+0 = 5.0
# coverage_score: min(10,3*2)*0.6 + 10*0.4 = 7.6
# actionability_score: (0+1+1)/3*10 = 6.7
# overall_score: 4.3*0.25 + 7.0*0.25 + 5.0*0.15 + 7.6*0.15 + 6.7*0.20 = 6.0/10
```

### Level 3: Scoring meta_improve_agent

**Scored by**: Reference comparison + Human validation

**Metrics**:

```python
class MetaImproveAgentScore(BaseModel):
  """Score for meta_improve_agent performance."""
  
  # Comparison to Reference
  reference_file: str  # Which reference to compare against
  
  # Coverage Comparison
  dimensions_covered: int  # Agent covered
  dimensions_in_reference: int  # Reference covered
  coverage_score: float  # 0-10 scale
  
  # Specificity Comparison
  recommendations_with_code: int  # Agent provided
  recommendations_with_code_in_reference: int  # Reference provided
  specificity_score: float  # 0-10 scale
  
  # Evidence Comparison
  evidence_quotes_count: int  # Agent provided
  evidence_quotes_in_reference: int  # Reference provided
  evidence_score: float  # 0-10 scale
  
  # Structure Comparison
  follows_reference_structure: bool  # Same sections?
  structure_score: float  # 0-10 scale
  
  # Impact Quantification
  impact_quantified_count: int  # Agent quantified
  impact_quantified_in_reference: int  # Reference quantified
  impact_score: float  # 0-10 scale
  
  # Overall Score
  overall_score: float  # Weighted average
  
  def calculate_overall_score(self):
    """Calculate weighted overall score."""
    # Coverage: How many dimensions vs reference
    self.coverage_score = min(10, (self.dimensions_covered / self.dimensions_in_reference) * 10)
    
    # Specificity: How many code blocks vs reference
    self.specificity_score = min(10, (self.recommendations_with_code / self.recommendations_with_code_in_reference) * 10)
    
    # Evidence: How many quotes vs reference
    self.evidence_score = min(10, (self.evidence_quotes_count / self.evidence_quotes_in_reference) * 10)
    
    # Structure: Binary score
    self.structure_score = 10 if self.follows_reference_structure else 5
    
    # Impact: How many quantified vs reference
    self.impact_score = min(10, (self.impact_quantified_count / self.impact_quantified_in_reference) * 10)
    
    # Weighted average
    self.overall_score = (
      self.coverage_score * 0.25 +
      self.specificity_score * 0.25 +
      self.evidence_score * 0.20 +
      self.structure_score * 0.10 +
      self.impact_score * 0.20
    )
    
    return self.overall_score
```

## The Evaluation Workflow

### Step 1: Run apply_agent

```bash
# Run apply_agent
python -m apply_agent /implement --spec=wdt-watchdog

# Output: apply_implement-wdt-watchdog_20251218_175839.session.txt
```

### Step 2: apply_improve_agent analyzes and SCORES apply_agent

```bash
# Run apply_improve_agent
python -m apply_improve_text_agent /analyze

# Output: META_IMPROVE_ANALYSIS_20251218_180748.md
# INCLUDES: ApplyAgentScore
```

**Key Addition**: apply_improve_agent now calculates a score:

```python
# In apply_improve_agent output
{
  "session_file": "apply_implement-wdt-watchdog_20251218_175839.session.txt",
  "apply_agent_score": {
    "build_attempts": 15,
    "time_minutes": 8.98,
    "error_types_count": 3,
    "overall_score": 5.6,
    "grade": "D",
    "improvement_needed": [
      "Reduce build attempts from 15 to <5",
      "Reduce time from 8.98 to <5 minutes",
      "Reduce error types from 3 to <2"
    ]
  },
  "error_patterns": [...],
  "proposed_improvements": [...]
}
```

### Step 3: meta_improve_agent analyzes and SCORES apply_improve_agent

```bash
# Run meta_improve_agent
python -m meta_improve_text_agent /analyze

# Output: META_META_IMPROVE_ANALYSIS_20251220_120000.md
# INCLUDES: ApplyImproveAgentScore
```

**Key Addition**: meta_improve_agent now calculates a score:

```python
# In meta_improve_agent output
{
  "session_file": "apply_improve_apply_improve_20251219_204307.session.txt",
  "apply_improve_agent_score": {
    "dimensions_covered": 3,
    "dimensions_expected": 7,
    "recommendations_specific": 3,
    "recommendations_actionable": 4,
    "overall_score": 6.0,
    "grade": "C",
    "improvement_needed": [
      "Cover all 7 dimensions (currently only 3)",
      "Provide code blocks for all recommendations (currently 3/5)",
      "Provide specific evidence quotes (currently summaries only)"
    ]
  },
  "instruction_issues": [...],
  "proposed_improvements": [...]
}
```

### Step 4: meta_improve_agent SCORES itself against references

```bash
# Run meta_improve_agent in self-improvement mode
python -m meta_improve_text_agent /self-improve

# Output: SELF_IMPROVEMENT_ANALYSIS_20251220_120500.md
# INCLUDES: MetaImproveAgentScore
```

**Key Addition**: meta_improve_agent scores itself:

```python
# In meta_improve_agent self-improvement output
{
  "own_session_file": "meta_improve_meta_improve_20251220_120000.session.txt",
  "reference_file": "reference_analysis_20251220_apply_improve_text.md",
  "meta_improve_agent_score": {
    "dimensions_covered": 6,
    "dimensions_in_reference": 7,
    "recommendations_with_code": 5,
    "recommendations_with_code_in_reference": 7,
    "evidence_quotes_count": 10,
    "evidence_quotes_in_reference": 21,
    "overall_score": 8.5,
    "grade": "B+",
    "improvement_needed": [
      "Cover all 7 dimensions (currently 6/7)",
      "Provide code blocks for all recommendations (currently 5/7)",
      "Provide more evidence quotes (currently 10/21)"
    ]
  },
  "instruction_issues": [...],
  "proposed_improvements": [...]
}
```

## Tracking Improvement Over Time

### Improvement Metrics Database

```python
# improvement_metrics.json
{
  "apply_agent": {
    "sessions": [
      {
        "date": "2025-12-18",
        "session": "apply_implement-wdt-watchdog_20251218_175839",
        "score": 5.6,
        "build_attempts": 15,
        "time_minutes": 8.98,
        "error_types": 3
      },
      {
        "date": "2025-12-21",
        "session": "apply_implement-timer-20251221_100000",
        "score": 7.2,  # IMPROVED!
        "build_attempts": 8,  # Better!
        "time_minutes": 6.5,  # Better!
        "error_types": 2  # Better!
      }
    ],
    "trend": "improving",
    "improvement_rate": "+1.6 points in 3 days"
  },
  
  "apply_improve_agent": {
    "sessions": [
      {
        "date": "2025-12-19",
        "session": "apply_improve_apply_improve_20251219_204307",
        "score": 6.0,
        "dimensions_covered": 3,
        "recommendations_specific": 3
      },
      {
        "date": "2025-12-21",
        "session": "apply_improve_apply_improve_20251221_110000",
        "score": 8.2,  # IMPROVED!
        "dimensions_covered": 6,  # Better!
        "recommendations_specific": 6  # Better!
      }
    ],
    "trend": "improving",
    "improvement_rate": "+2.2 points in 2 days"
  },
  
  "meta_improve_agent": {
    "sessions": [
      {
        "date": "2025-12-20",
        "session": "meta_improve_meta_improve_20251220_120000",
        "score": 8.5,
        "vs_reference": "reference_analysis_20251220_apply_improve_text.md"
      }
    ],
    "trend": "stable",
    "improvement_rate": "baseline established"
  }
}
```

## The Validation Loop

```
┌─────────────────────────────────────────────────────────────┐
│ 1. apply_agent runs (score: 5.6/10)                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. apply_improve_agent analyzes and scores (6.0/10)         │
│    - Identifies: apply_agent needs improvement               │
│    - Recommends: Add error counting methodology              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Human applies recommendations to apply_agent              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. apply_agent runs again (score: 7.2/10) ✅ IMPROVED!      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Validate: Did the improvement work?                       │
│    - Before: 5.6/10                                          │
│    - After: 7.2/10                                           │
│    - Delta: +1.6 points ✅                                   │
│    - Conclusion: apply_improve_agent's recommendations work! │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Priority

### Phase 1: Add Scoring to apply_improve_agent (Week 1)

```python
# Update apply_improve_text_agent.py output schema
class SessionAnalysis(BaseModel):
  session_file: str
  apply_agent_score: ApplyAgentScore  # NEW!
  total_build_attempts: int
  total_fix_attempts: int
  time_to_success_minutes: float
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str]
```

### Phase 2: Add Scoring to meta_improve_agent (Week 2)

```python
# Update meta_improve_text_agent.py output schema
class SessionAnalysis(BaseModel):
  session_file: str
  apply_improve_agent_score: ApplyImproveAgentScore  # NEW!
  instruction_issues: List[InstructionIssue]
  insights: List[str]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str]
```

### Phase 3: Add Self-Scoring to meta_improve_agent (Week 3)

```python
# Update meta_improve_text_agent.py for self-improvement mode
class SelfImprovementAnalysis(BaseModel):
  own_session_file: str
  reference_file: str
  meta_improve_agent_score: MetaImproveAgentScore  # NEW!
  instruction_issues: List[InstructionIssue]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str]
```

### Phase 4: Track Metrics Over Time (Week 4)

```python
# Create improvement_tracker.py
class ImprovementTracker:
  def record_score(self, agent_name, session, score):
    """Record score for tracking."""
    pass
  
  def get_trend(self, agent_name):
    """Get improvement trend."""
    pass
  
  def validate_improvement(self, agent_name, before_session, after_session):
    """Validate that improvement actually happened."""
    pass
```

## Conclusion

**The Key Insight**: Score at each level to validate improvements!

1. **apply_improve_agent scores apply_agent** → Validates apply_agent performance
2. **meta_improve_agent scores apply_improve_agent** → Validates apply_improve_agent performance
3. **meta_improve_agent scores itself vs references** → Validates meta_improve_agent performance

This creates a **closed-loop evaluation system** where:
- Every improvement can be measured
- Every recommendation can be validated
- Progress can be tracked over time
- Regressions can be detected

**Without scoring**: We don't know if improvements work
**With scoring**: We can prove improvements work and track progress!
