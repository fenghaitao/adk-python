# Reference Analysis Guide

## What is a Reference Analysis?

A **reference analysis** is a high-quality example that demonstrates what excellent agent analysis looks like. It serves as a **gold standard** that agents can compare themselves against for self-improvement.

## Purpose of References

1. **Training**: Show agents what good analysis looks like
2. **Benchmarking**: Provide a standard to measure against
3. **Self-Improvement**: Enable agents to identify gaps in their own analysis
4. **Quality Control**: Ensure consistent analysis quality over time

## Structure of a Reference Analysis

### Required Sections

#### 1. Metadata
```markdown
## Metadata
- **Session Analyzed**: [filename]
- **Analyst**: Human Expert / AI Assistant
- **Date**: YYYY-MM-DD
- **Analysis Duration**: X minutes
- **Quality Rating**: X/10
```

#### 2. Executive Summary
- Brief overview of what was analyzed
- Key findings (2-3 sentences)
- Overall score and grade

#### 3. Detailed Scoring
- Result Quality breakdown (50 points)
- Process Quality breakdown (50 points)
- Justification for each score

#### 4. Root Cause Analysis
- Why did issues occur?
- What patterns emerged?
- Evidence from session

#### 5. Improvement Recommendations
- Specific, actionable recommendations
- Exact text to add (in code blocks)
- Expected impact (quantified)
- Priority (high/medium/low)

#### 6. Expected Overall Impact
- Before/after comparison
- Quantified improvements
- Validation plan

#### 7. What Makes This Analysis High Quality
- Self-reflection on analysis quality
- Key patterns demonstrated
- Lessons for other agents

## Quality Criteria

### Excellent Reference (9-10/10)

✅ **Comprehensive Coverage**
- All 7 dimensions covered
- No gaps in analysis

✅ **Specific and Actionable**
- Exact text provided
- Code blocks included
- Location specified
- Clear implementation steps

✅ **Evidence-Based**
- Every claim backed by data
- Bash commands shown
- Counts and metrics provided
- Patterns documented

✅ **Quantified Impact**
- Numerical estimates
- Before/after comparisons
- Percentage improvements

✅ **Well-Structured**
- Clear organization
- Easy to follow
- Logical flow

✅ **Prioritized**
- High/medium/low priority
- Impact vs effort considered
- Quick wins identified

✅ **Validated**
- Validation plan included
- Success criteria defined
- Measurement approach clear

### Good Reference (7-8/10)

✅ Most dimensions covered
✅ Mostly specific recommendations
✅ Some evidence provided
✅ Some quantification
✅ Reasonable structure
⚠️ Missing some details
⚠️ Some gaps in coverage

### Poor Reference (<7/10)

❌ Missing dimensions
❌ Vague recommendations
❌ No evidence
❌ No quantification
❌ Poor structure
❌ Not actionable

## How to Create a Reference

### Step 1: Analyze Thoroughly

Spend 20-30 minutes on comprehensive analysis:
- Read entire session
- Extract all metrics
- Identify all patterns
- Document all evidence

### Step 2: Score Objectively

Use the comprehensive scoring system:
- Result Quality (50 points)
- Process Quality (50 points)
- Justify each score with evidence

### Step 3: Provide Specific Recommendations

For each issue:
- Describe the problem
- Show evidence
- Provide exact fix (with code)
- Specify location
- Quantify impact

### Step 4: Validate Quality

Before saving as reference:
- [ ] All 7 dimensions covered?
- [ ] All recommendations specific?
- [ ] All claims evidence-based?
- [ ] All impacts quantified?
- [ ] Structure clear and logical?
- [ ] Validation plan included?

### Step 5: Add Metadata

Document what makes this analysis high quality:
- Key patterns demonstrated
- Lessons for other agents
- Quality score (9-10/10)

## Example References

### apply_improve_agent_reference_example.md

**What it demonstrates**:
- Comprehensive 7-dimension analysis
- Specific recommendations with code blocks
- Evidence-based claims with bash commands
- Quantified impact estimates
- Clear prioritization
- Validation plan

**Key patterns**:
- Root cause analysis methodology
- Evidence extraction techniques
- Impact quantification formulas
- Recommendation formatting

**Use this reference when**:
- Learning how to analyze apply_agent sessions
- Comparing your analysis quality
- Identifying gaps in your own analysis

## How Agents Use References

### For Self-Improvement

```python
# Step 1: Read own session
own_analysis = read_file("my_analysis.md")

# Step 2: Read reference
reference = read_file("apply_improve_agent_reference_example.md")

# Step 3: Compare
comparison = {
  "dimensions_covered": {
    "self": count_dimensions(own_analysis),
    "reference": count_dimensions(reference),
    "gap": reference - self
  },
  "recommendations_with_code": {
    "self": count_code_blocks(own_analysis),
    "reference": count_code_blocks(reference),
    "gap": reference - self
  },
  # ... more comparisons
}

# Step 4: Identify gaps
gaps = [
  "Missing dimension: Code Evolution Analysis",
  "Only 3/7 recommendations have code blocks (reference has 7/7)",
  "Evidence is summaries, not specific quotes",
  ...
]

# Step 5: Generate improvements
improvements = [
  "Add Code Evolution Analysis section",
  "Provide code blocks for all recommendations",
  "Use specific bash commands as evidence",
  ...
]
```

### For Benchmarking

```python
# Calculate quality score vs reference
quality_score = {
  "coverage": (self.dimensions / reference.dimensions) * 25,
  "specificity": (self.code_blocks / reference.code_blocks) * 25,
  "evidence": (self.evidence_quotes / reference.evidence_quotes) * 25,
  "impact": (self.quantified / reference.quantified) * 25,
  "total": sum(scores) / 100 * 10  # Convert to 0-10 scale
}

# If quality_score >= 9.0: Excellent
# If quality_score >= 7.0: Good
# If quality_score < 7.0: Needs improvement
```

## Creating New References

### When to Create a Reference

Create a new reference when:
- You produce an exceptionally high-quality analysis
- You discover a new analysis pattern
- You want to demonstrate a specific technique
- You need a benchmark for a new agent type

### Reference Naming Convention

```
[agent_type]_reference_[description]_[date].md

Examples:
- apply_improve_agent_reference_example.md
- apply_improve_agent_reference_timing_analysis_20251220.md
- apply_improve_agent_reference_test_quality_20251221.md
```

### Reference Repository Structure

```
openspec-memories/references/
  00_REFERENCE_GUIDE.md (this file)
  apply_improve_agent_reference_example.md
  apply_improve_agent_reference_timing_analysis.md
  apply_improve_agent_reference_test_quality.md
  ...
```

## Maintaining References

### Review Periodically

Every month:
- Review existing references
- Update if analysis methods improve
- Add new references for new patterns
- Archive outdated references

### Version References

When updating:
- Keep old version as `_v1.md`
- Create new version as `_v2.md`
- Document what changed

### Quality Control

Before adding to repository:
- Peer review by another human
- Validate against quality criteria
- Score must be ≥9.0/10
- All sections must be complete

## Conclusion

References are the **foundation of self-improvement**. They provide:
- Clear examples of excellence
- Measurable standards
- Learning opportunities
- Quality benchmarks

By maintaining high-quality references, we enable agents to continuously improve themselves without requiring infinite meta-agents.

**Key Principle**: An agent that can compare itself to excellent examples can improve itself.
