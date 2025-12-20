# Agent Improvement System - Quick Start Guide

## Overview

This guide helps you quickly get started with the agent improvement system.

## 5-Minute Quick Start

### Step 1: Run apply_agent

```bash
cd adk-python
python -m apply_agent /implement --spec=wdt-watchdog
```

**Output**: `apply_implement-wdt-watchdog_YYYYMMDD_HHMMSS.session.txt`

### Step 2: Analyze with apply_improve_agent

```bash
python -m apply_improve_agent /analyze-apply
```

**Output**: `APPLY_AGENT_ANALYSIS_YYYYMMDD_HHMMSS.md`

**Contains**:
- apply_agent score (e.g., 5.3/10, Grade: F)
- Detailed breakdown (result + process quality)
- Specific recommendations with code blocks
- Expected impact (quantified)

### Step 3: Review and Apply Recommendations

```bash
# Read the analysis
cat APPLY_AGENT_ANALYSIS_*.md

# Apply recommendations to apply_agent
vim apply_agent_instruction.md
# Add recommended improvements
```

### Step 4: Validate Improvement

```bash
# Run apply_agent again
python -m apply_agent /implement --spec=timer

# Analyze again
python -m apply_improve_agent /analyze-apply

# Compare scores
# Before: 5.3/10
# After: 7.2/10
# Improvement: +1.9 ✅
```

## Understanding the System

### Two Agents, Two Modes

```
apply_agent (does work)
  ↓
apply_improve_agent (analyzes and improves)
  ├─ Mode 1: /analyze-apply → Improve apply_agent
  └─ Mode 2: /self-improve → Improve self
```

### Scoring System

**100-point scale** (converted to 0-10):
- **Result Quality** (50 points): What was produced
- **Process Quality** (50 points): How it was produced

**Grades**:
- A (9-10): Excellent
- B (8-9): Good
- C (7-8): Satisfactory
- D (6-7): Needs Improvement
- F (<6): Failing

## Common Tasks

### Task 1: Improve apply_agent

```bash
# 1. Run apply_agent
python -m apply_agent /implement --spec=YOUR_SPEC

# 2. Analyze
python -m apply_improve_agent /analyze-apply

# 3. Read recommendations
cat APPLY_AGENT_ANALYSIS_*.md

# 4. Apply improvements
vim apply_agent_instruction.md

# 5. Validate
python -m apply_agent /implement --spec=ANOTHER_SPEC
python -m apply_improve_agent /analyze-apply
# Check if score improved
```

### Task 2: Improve apply_improve_agent

```bash
# 1. Run apply_improve_agent (Mode 1)
python -m apply_improve_agent /analyze-apply

# 2. Self-improve (Mode 2)
python -m apply_improve_agent /self-improve

# 3. Read self-improvement recommendations
cat SELF_IMPROVEMENT_ANALYSIS_*.md

# 4. Apply improvements
vim apply_improve_text_agent.py

# 5. Validate
python -m apply_improve_agent /analyze-apply
# Check if analysis quality improved
```

### Task 3: Create a Reference Analysis

```bash
# 1. Manually create high-quality analysis
# Follow structure in apply_improve_agent_reference_example.md

# 2. Save as reference
cp my_excellent_analysis.md openspec-memories/references/

# 3. Update reference guide
vim openspec-memories/references/00_REFERENCE_GUIDE.md

# 4. Use in self-improvement
python -m apply_improve_agent /self-improve
# Agent will compare to your new reference
```

## Key Files

### Implementation Files
- `agent_scoring.py` - Scoring classes
- `scoring_tools.py` - Scoring tools
- `apply_improve_text_agent.py` - Main agent

### Documentation Files
- `AGENT_IMPROVEMENT_SYSTEM_DESIGN.md` - Complete design
- `COMPREHENSIVE_SCORING_DESIGN.md` - Scoring details
- `QUICK_START_GUIDE.md` - This file

### Reference Files
- `openspec-memories/references/00_REFERENCE_GUIDE.md`
- `openspec-memories/references/apply_improve_agent_reference_example.md`

## Troubleshooting

### Issue: Low Score for apply_agent

**Symptoms**: Score < 6.0/10

**Solutions**:
1. Check which dimension scored lowest
2. Read relevant best practice documents
3. Apply specific recommendations from analysis
4. Focus on high-priority improvements first

### Issue: apply_improve_agent Analysis Not Comprehensive

**Symptoms**: Missing dimensions, vague recommendations

**Solutions**:
1. Run self-improvement mode
2. Compare to reference analysis
3. Apply instruction improvements
4. Validate with another analysis

### Issue: Improvements Not Working

**Symptoms**: Score doesn't improve after changes

**Solutions**:
1. Verify recommendations were applied correctly
2. Check if task is similar enough for comparison
3. Review root cause analysis
4. Try different recommendations

## Best Practices

### For apply_agent
1. ✅ Consult best practices BEFORE coding
2. ✅ Build incrementally (don't implement everything at once)
3. ✅ Learn from error patterns (don't repeat same errors)
4. ✅ Validate against anti-patterns
5. ✅ Document as you code

### For apply_improve_agent
1. ✅ Cover all 7 dimensions
2. ✅ Provide specific evidence (bash commands, quotes)
3. ✅ Include code blocks for all recommendations
4. ✅ Quantify expected impact
5. ✅ Prioritize recommendations (high/medium/low)

### For Humans
1. ✅ Review recommendations before applying
2. ✅ Apply high-priority improvements first
3. ✅ Validate improvements with metrics
4. ✅ Create references for excellent analyses
5. ✅ Track metrics over time

## Metrics to Track

### apply_agent Metrics
```python
{
  "build_attempts": 15 → 5,  # Target: ≤3
  "time_minutes": 8.98 → 4.5,  # Target: ≤5
  "error_types": 3 → 1,  # Target: ≤2
  "score": 5.3 → 8.5,  # Target: ≥8.0
  "grade": "F" → "B"
}
```

### apply_improve_agent Metrics
```python
{
  "dimensions_covered": 3 → 7,  # Target: 7/7
  "recommendations_with_code": 3 → 7,  # Target: all
  "evidence_quotes": 5 → 21,  # Target: specific
  "score": 6.0 → 8.5,  # Target: ≥8.5
  "grade": "D" → "B+"
}
```

## Next Steps

### Week 1: Get Familiar
- Run through quick start
- Read design document
- Understand scoring system

### Week 2: First Improvements
- Improve apply_agent
- Validate improvements
- Track metrics

### Week 3: Self-Improvement
- Run self-improvement mode
- Create first reference
- Improve apply_improve_agent

### Week 4: Iteration
- Continue improvement cycle
- Add more references
- Monitor trends

## Resources

### Documentation
- [Complete Design](AGENT_IMPROVEMENT_SYSTEM_DESIGN.md)
- [Scoring Details](COMPREHENSIVE_SCORING_DESIGN.md)
- [Architecture](SIMPLIFIED_TWO_LEVEL_ARCHITECTURE.md)

### Examples
- [Reference Analysis Example](../openspec-memories/references/apply_improve_agent_reference_example.md)
- [Reference Guide](../openspec-memories/references/00_REFERENCE_GUIDE.md)

### Code
- [Scoring Classes](agent_scoring.py)
- [Scoring Tools](scoring_tools.py)
- [Main Agent](apply_improve_text_agent.py)

## FAQ

**Q: How often should I run improvements?**
A: After every 3-5 apply_agent runs, or when score plateaus.

**Q: How do I know if improvements are working?**
A: Compare before/after scores. Improvement of ≥1.0 points is good.

**Q: What if self-improvement doesn't help?**
A: Create better references, or manually review instruction gaps.

**Q: Can I automate this?**
A: Partially. Metric extraction can be automated, but human review is recommended.

**Q: How long does analysis take?**
A: Mode 1: 1-3 minutes. Mode 2: 2-5 minutes.

**Q: What's a good target score?**
A: apply_agent: ≥8.0/10. apply_improve_agent: ≥8.5/10.

## Support

For issues or questions:
1. Check troubleshooting section
2. Review design documentation
3. Examine reference examples
4. Create an issue with details

## Summary

**Quick Start in 4 Steps**:
1. Run apply_agent
2. Analyze with apply_improve_agent
3. Apply recommendations
4. Validate improvement

**Key Concepts**:
- Two agents, two modes
- Comprehensive scoring (result + process)
- Reference-based learning
- Outcome validation

**Success Criteria**:
- Scores improving over time
- Fewer build attempts
- Better code quality
- Faster completion

Start improving your agents today! 🚀
