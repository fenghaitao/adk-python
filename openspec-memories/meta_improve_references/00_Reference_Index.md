# Meta-Improve Reference Analyses Index

## Purpose

This directory contains high-quality reference analyses that demonstrate what excellent meta-analysis looks like. These references are used by the meta_improve_agent to learn and self-improve.

## How to Use These References

### For meta_improve_agent (Self-Improvement Mode)

When running in self-improvement mode, the meta_improve_agent should:

1. **Read all references** - Understand what good analysis looks like
2. **Read own session** - See what you actually did
3. **Compare** - Identify gaps between your output and references
4. **Learn** - Extract patterns and techniques from references
5. **Improve** - Update your instruction based on learnings

### For Humans (Creating New References)

When creating a new reference analysis:

1. **Analyze thoroughly** - Cover all dimensions systematically
2. **Provide evidence** - Quote specific examples from sessions
3. **Be specific** - Give exact text for recommendations
4. **Quantify impact** - Estimate improvements numerically
5. **Add metadata** - Document what makes this analysis good
6. **Include patterns** - Highlight key techniques to learn

## Reference Analyses

### reference_analysis_20251220_apply_improve_text.md

- **Agent Analyzed**: apply_improve_text_agent
- **Session**: apply_improve_apply_improve_20251219_204307.session.txt
- **Analyst**: Human Expert (Kiro AI Assistant)
- **Date**: 2025-12-20
- **Quality Rating**: 9/10
- **Key Strengths**:
  - Comprehensive coverage of 7 improvement areas
  - Specific, actionable recommendations with exact text
  - Evidence-based with session quotes
  - Quantified impact estimates
  - Systematic categorization

**What to Learn from This Reference**:
- How to structure each issue (Problem, Evidence, Root Cause, Recommendation, Location, Impact)
- How to provide evidence (quote actual commands and outputs)
- How to write recommendations (exact text in code blocks)
- How to quantify impact (percentages, time savings, quality metrics)
- How to categorize issues systematically
- How to ensure comprehensive coverage

**Key Patterns**:
1. Issue Structure Template
2. Evidence Collection Methods
3. Recommendation Format
4. Impact Quantification
5. Categorization Approach
6. Prioritization Criteria
7. Completeness Checklist

## Quality Criteria for Reference Analyses

A high-quality reference analysis should:

### 1. Systematic Coverage (9-10 points)
- [ ] Evaluates all relevant dimensions
- [ ] No gaps in coverage
- [ ] Organized by category

### 2. Evidence-Based (9-10 points)
- [ ] Every claim backed by session evidence
- [ ] Quotes actual commands and outputs
- [ ] References specific timestamps or line numbers

### 3. Specific Recommendations (9-10 points)
- [ ] Exact text to add (in code blocks)
- [ ] Clear location guidance
- [ ] Complete examples provided

### 4. Actionable (9-10 points)
- [ ] Can be implemented immediately
- [ ] No ambiguity in recommendations
- [ ] Clear implementation steps

### 5. Quantified Impact (9-10 points)
- [ ] Numerical estimates provided
- [ ] Measurable outcomes specified
- [ ] Prioritization enabled

### 6. Well-Structured (9-10 points)
- [ ] Consistent format throughout
- [ ] Easy to scan and understand
- [ ] Logical organization

### 7. Comprehensive (9-10 points)
- [ ] Covers workflow, tools, output, etc.
- [ ] Addresses immediate and systemic issues
- [ ] Provides quick wins and long-term improvements

**Total Score**: Sum of all categories (max 70 points)
- 63-70: Excellent reference (use for learning)
- 56-62: Good reference (useful but not ideal)
- <56: Needs improvement (don't use as reference)

## Adding New References

To add a new reference analysis:

1. **Create the analysis file**:
   ```bash
   # Format: reference_analysis_YYYYMMDD_[agent_name].md
   touch reference_analysis_20251221_apply_improve_json.md
   ```

2. **Include required sections**:
   - Metadata (session, analyst, date, quality rating, key strengths)
   - Analysis Content (the actual analysis)
   - What Makes This Analysis Good
   - Key Patterns to Learn
   - How to Use This Reference
   - Lessons for meta_improve_agent Instruction

3. **Update this index**:
   - Add entry with metadata
   - Describe key strengths
   - List patterns to learn

4. **Validate quality**:
   - Score against quality criteria
   - Ensure score is 63+ before using as reference

## Self-Improvement Workflow

When meta_improve_agent runs in self-improvement mode:

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Read Own Session                                    │
│ - What did I do?                                             │
│ - What was my output?                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Read All References                                 │
│ - What does good analysis look like?                         │
│ - What patterns do references use?                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Compare Own Output to References                    │
│ - What did references include that I didn't?                 │
│ - What structure did references use?                         │
│ - What depth did references provide?                         │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Identify Gaps in Own Instruction                    │
│ - What parts of my instruction led to missing elements?     │
│ - What examples or guidance would have helped?               │
│ - What structure or templates were missing?                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Generate Self-Improvement Recommendations           │
│ - Specific additions to own instruction                      │
│ - New templates or examples to add                           │
│ - Better workflow steps                                      │
│ - Enhanced output schema                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Save Self-Improvement Report                        │
│ - Document what was learned                                  │
│ - Propose specific instruction updates                       │
│ - Estimate impact of improvements                            │
└─────────────────────────────────────────────────────────────┘
```

## Continuous Improvement

As you accumulate more references:

1. **Track patterns** - What makes analyses consistently good?
2. **Update instruction** - Incorporate learnings into meta_improve_agent
3. **Measure progress** - Compare new analyses to references
4. **Refine references** - Update as understanding improves
5. **Share learnings** - Document insights for the team

## Conclusion

This reference repository enables the meta_improve_agent to self-improve by learning from high-quality examples, avoiding the need for infinite recursion of meta-meta-improve agents.

The key insight: **Learn from examples, not from another agent.**
