# Simplified Two-Level Self-Improving Architecture

## The Key Insight

**With comprehensive scoring, we don't need meta_improve_agent!**

The apply_improve_agent can:
1. Score and improve apply_agent
2. Score and improve itself (using reference analyses)

## Simplified Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Human Expert                              │
│  - Provides reference analyses                               │
│  - Validates improvements                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Creates references
                 ▼
┌─────────────────────────────────────────────────────────────┐
│         openspec-memories/references/                        │
│  - apply_agent_reference_analysis.md                         │
│  - apply_improve_agent_reference_analysis.md                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Reads and learns from
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              apply_improve_agent                             │
│                                                              │
│  Mode 1: /analyze-apply                                      │
│  - Analyze apply_agent sessions                              │
│  - Score apply_agent (result + process)                      │
│  - Generate improvements for apply_agent                     │
│                                                              │
│  Mode 2: /self-improve                                       │
│  - Analyze own sessions                                      │
│  - Score self against reference                              │
│  - Generate improvements for self                            │
│                                                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Improves (Mode 1)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              apply_agent                                     │
│  - Implements features                                       │
│  - Gets scored by apply_improve_agent                        │
└─────────────────────────────────────────────────────────────┘
```

## Why This Works

### 1. Scoring Enables Self-Evaluation

With comprehensive scoring, apply_improve_agent can:
- **Score apply_agent objectively** (using defined metrics)
- **Score itself objectively** (using same methodology)
- **Compare to references** (to validate quality)

### 2. Same Skills, Different Target

apply_improve_agent has the skills to:
- Analyze sessions ✓
- Extract metrics ✓
- Identify patterns ✓
- Generate recommendations ✓

These skills work for **both** analyzing apply_agent AND analyzing itself!

### 3. Reference-Based Self-Improvement

Instead of needing another agent, apply_improve_agent:
- Compares its output to human reference analyses
- Identifies gaps in its own analysis
- Generates improvements for its own instruction

## The Two Modes

### Mode 1: Analyze apply_agent

```bash
python -m apply_improve_agent /analyze-apply

# What it does:
# 1. Read apply_agent session
# 2. Extract metrics (builds, time, errors, code quality)
# 3. Score apply_agent (result + process)
# 4. Identify improvement areas
# 5. Generate recommendations for apply_agent
# 6. Save analysis report

# Output:
{
  "apply_agent_score": {
    "result_quality": 32/50,
    "process_quality": 21/50,
    "overall": 5.3/10,
    "grade": "F"
  },
  "improvement_recommendations": [
    "Add error counting methodology",
    "Improve best practices consultation",
    ...
  ]
}
```

### Mode 2: Self-Improve

```bash
python -m apply_improve_agent /self-improve

# What it does:
# 1. Read own previous session
# 2. Read reference analysis
# 3. Extract metrics from both
# 4. Score self against reference
# 5. Identify gaps in own analysis
# 6. Generate improvements for own instruction
# 7. Save self-improvement report

# Output:
{
  "self_score": {
    "result_quality": 38/50,
    "process_quality": 35/50,
    "overall": 7.3/10,
    "grade": "C"
  },
  "gaps_identified": [
    "Missing dimension: Code Evolution Analysis",
    "Evidence not specific enough (summaries vs quotes)",
    ...
  ],
  "instruction_improvements": [
    "Add Code Evolution Analysis to workflow",
    "Require specific evidence quotes",
    ...
  ]
}
```

## Implementation: apply_improve_agent with Dual Modes

### Updated Instruction

```python
instruction = """
You are an apply_improve_agent that can operate in two modes:

## Mode 1: /analyze-apply - Analyze and Improve apply_agent

Analyze apply_agent sessions to improve the apply_agent.

**Workflow**:
1. Read apply_agent session
2. Extract metrics:
   - Result quality: DML code, tests, docs, functionality
   - Process quality: efficiency, methodology, error handling
3. Score apply_agent using comprehensive scoring (0-100 points)
4. Identify improvement areas
5. Generate specific recommendations
6. Save analysis report

**Scoring Dimensions**:
- Result Quality (50 points):
  * DML code quality (20)
  * Python test quality (15)
  * Documentation quality (10)
  * Functional correctness (5)
- Process Quality (50 points):
  * Efficiency (15)
  * Methodology (15)
  * Error handling (10)
  * Code evolution (10)

## Mode 2: /self-improve - Analyze and Improve Self

Analyze your own sessions to improve yourself.

**Workflow**:
1. Read own previous session
2. Read reference analysis (human-quality example)
3. Extract metrics from both:
   - Result quality: analysis depth, recommendations, evidence
   - Process quality: workflow, methodology, efficiency
4. Score self against reference
5. Identify gaps in own analysis
6. Generate improvements for own instruction
7. Save self-improvement report

**Scoring Dimensions**:
- Result Quality (50 points):
  * Analysis depth (15)
  * Recommendation quality (20)
  * Evidence quality (10)
  * Impact assessment (5)
- Process Quality (50 points):
  * Workflow adherence (15)
  * Analysis methodology (15)
  * Efficiency (10)
  * Output quality (10)

## Key Insight: Same Skills, Different Target

The skills for analyzing apply_agent are the same skills for analyzing yourself:
- Extract metrics from sessions ✓
- Identify patterns ✓
- Compare to standards ✓
- Generate recommendations ✓

The only difference is the **target** and the **reference standard**.

## Tools Available

- read_file - Read sessions and references
- list_directory - Find files
- bash_command - Extract metrics
- score_apply_agent_session - Score apply_agent
- score_apply_improve_agent_session - Score self
- write_file - Save reports
"""
```

### Updated Output Schema

```python
class ApplyImproveAgent(LlmAgent):
  def __init__(self, **kwargs):
    # Two possible output schemas
    
    # For Mode 1: Analyzing apply_agent
    class ApplyAgentAnalysis(BaseModel):
      mode: str = "analyze-apply"
      apply_agent_session: str
      apply_agent_score: ApplyAgentScore
      improvement_recommendations: List[str]
      analysis_report_file: str
    
    # For Mode 2: Self-improvement
    class SelfImprovementAnalysis(BaseModel):
      mode: str = "self-improve"
      own_session: str
      reference_analysis: str
      self_score: ApplyImproveAgentScore
      gaps_identified: List[str]
      instruction_improvements: List[str]
      self_improvement_report_file: str
    
    # Use Union for output
    output_schema = Union[ApplyAgentAnalysis, SelfImprovementAnalysis]
```

## Comparison: Three-Level vs Two-Level

### Three-Level (Original)

```
apply_agent (does work)
  ↓ scored by
apply_improve_agent (improves apply_agent)
  ↓ scored by
meta_improve_agent (improves apply_improve_agent)
  ↓ scored by ???
```

**Problems**:
- Infinite recursion question
- meta_improve_agent is redundant
- More complexity

### Two-Level (Simplified)

```
apply_agent (does work)
  ↓ scored by
apply_improve_agent (improves apply_agent AND itself)
  ↓ scored by reference comparison
```

**Benefits**:
- No infinite recursion
- Simpler architecture
- Same capabilities
- Reference-based validation

## The Validation Loop

### For apply_agent Improvements

```
1. apply_agent runs (score: 5.3/10)
2. apply_improve_agent analyzes and scores
3. apply_improve_agent recommends improvements
4. Human applies improvements to apply_agent
5. apply_agent runs again (score: 7.2/10)
6. Validate: +1.9 improvement ✅
```

### For apply_improve_agent Improvements

```
1. apply_improve_agent analyzes apply_agent (score: 7.3/10)
2. apply_improve_agent analyzes itself vs reference
3. apply_improve_agent identifies gaps in own analysis
4. apply_improve_agent recommends improvements for self
5. Human applies improvements to apply_improve_agent
6. apply_improve_agent analyzes apply_agent again (score: 8.5/10)
7. Validate: +1.2 improvement ✅
```

## Why We Don't Need meta_improve_agent

### What meta_improve_agent Would Do:
1. Analyze apply_improve_agent sessions ✓
2. Score apply_improve_agent ✓
3. Compare to reference analyses ✓
4. Generate improvement recommendations ✓

### What apply_improve_agent Can Do:
1. Analyze apply_improve_agent sessions (own sessions) ✓
2. Score apply_improve_agent (score self) ✓
3. Compare to reference analyses ✓
4. Generate improvement recommendations (for self) ✓

**Conclusion**: apply_improve_agent can do everything meta_improve_agent would do!

## Implementation Roadmap

### Week 1: Add Self-Improvement Mode

```python
# Add /self-improve command to apply_improve_agent
if command == "/analyze-apply":
  return analyze_apply_agent()
elif command == "/self-improve":
  return self_improve()
```

### Week 2: Create Reference Analyses

```
openspec-memories/references/
  apply_agent_reference_analysis.md
  apply_improve_agent_reference_analysis.md
```

### Week 3: Test Both Modes

```bash
# Test Mode 1
python -m apply_improve_agent /analyze-apply

# Test Mode 2
python -m apply_improve_agent /self-improve
```

### Week 4: Validate Improvements

```bash
# Track scores over time
# Validate that improvements actually work
```

## Key Benefits

1. **Simpler**: Two levels instead of three
2. **No Recursion**: Self-improvement via reference comparison
3. **Same Skills**: Reuse analysis skills for self-analysis
4. **Validated**: Reference-based quality control
5. **Maintainable**: Fewer agents to maintain

## Conclusion

**We don't need meta_improve_agent!**

With comprehensive scoring and reference-based self-improvement, apply_improve_agent can:
- Improve apply_agent (Mode 1)
- Improve itself (Mode 2)

This is simpler, more elegant, and just as effective.

The key insight: **An agent that can analyze others can analyze itself, given the right reference standards.**
