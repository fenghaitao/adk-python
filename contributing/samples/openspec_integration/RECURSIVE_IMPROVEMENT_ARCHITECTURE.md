# Recursive Improvement Architecture

## The Problem

How do we improve the meta_improve agent that improves the apply_improve agent?

```
apply_agent → apply_improve_agent → meta_improve_agent → ???
```

## The Solution: Self-Improvement with Reference Examples

Instead of infinite recursion, use **reference-based self-improvement**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Human Expert                              │
│  Provides reference analyses as examples                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Creates reference examples
                 ▼
┌─────────────────────────────────────────────────────────────┐
│         openspec-memories/meta_improve_references/           │
│  - reference_analysis_001.md (human-quality analysis)        │
│  - reference_analysis_002.md                                 │
│  - ...                                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Reads and learns from
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              meta_improve_agent                              │
│  Mode 1: Analyze apply_improve_agent sessions                │
│  Mode 2: Self-improve by comparing to references             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Improves
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           apply_improve_agent                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Improves
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              apply_agent                                     │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### 1. Create Reference Analysis Repository

Store high-quality human analyses as learning examples:

```
openspec-memories/
  meta_improve_references/
    00_Reference_Index.md
    reference_analysis_20251220_apply_improve_text.md
    reference_analysis_20251220_apply_improve_json.md
    ...
```

Each reference includes:
- The session that was analyzed
- The high-quality analysis (like the one I provided)
- Key insights and patterns
- What made this analysis good

### 2. Add Self-Improvement Mode to meta_improve_agent

```python
class MetaImproveAgent:
  def run(self, command: str):
    if command == "/analyze":
      # Normal mode: analyze apply_improve_agent session
      return self.analyze_improve_agent()
    
    elif command == "/self-improve":
      # Self-improvement mode: analyze own session
      return self.self_improve()
```

### 3. Self-Improvement Workflow

When meta_improve_agent runs in self-improvement mode:

**Step 1: Read Own Session**
- Read the meta_improve_agent session file
- Extract what the agent did

**Step 2: Read Reference Analyses**
- Read all reference analyses from openspec-memories/meta_improve_references/
- Understand what high-quality analysis looks like

**Step 3: Compare Own Output to References**
- What did the reference analysis include that mine didn't?
- What structure did the reference use?
- What depth of analysis did the reference provide?
- What specific recommendations did the reference make?

**Step 4: Identify Gaps in Own Instruction**
- What parts of my instruction led to missing those elements?
- What examples or guidance would have helped?
- What structure or templates were missing?

**Step 5: Generate Self-Improvement Recommendations**
- Specific additions to own instruction
- New templates or examples to add
- Better workflow steps
- Enhanced output schema

**Step 6: Save Self-Improvement Report**
- Document what was learned
- Propose specific instruction updates
- Estimate impact of improvements

### 4. Reference Analysis Format

Each reference analysis should include metadata:

```markdown
# Reference Analysis: [Agent Name] Session [Date]

## Metadata
- **Session Analyzed**: apply_improve_apply_improve_20251219_204307.session.txt
- **Analyst**: Human Expert
- **Quality Rating**: 9/10
- **Key Strengths**: 
  - Comprehensive coverage of all dimensions
  - Specific, actionable recommendations
  - Concrete examples with code blocks
  - Quantified impact estimates

## Analysis Content
[The actual analysis content]

## What Makes This Analysis Good
1. **Systematic Coverage**: Evaluated 7 distinct dimensions
2. **Specific Recommendations**: Each recommendation includes exact text to add
3. **Evidence-Based**: Every claim backed by session evidence
4. **Actionable**: Clear implementation guidance
5. **Quantified Impact**: Estimated improvements numerically

## Key Patterns to Learn
- Use of structured templates for recommendations
- Distinction between different types of errors
- Bash command patterns for extracting specific information
- Report structure with all required sections
```

## Usage

### Normal Mode: Improve apply_improve_agent

```bash
# Run meta_improve_agent to analyze apply_improve_agent session
python -m meta_improve_text_agent /analyze
```

### Self-Improvement Mode: Improve meta_improve_agent itself

```bash
# Run meta_improve_agent to analyze its own session
python -m meta_improve_text_agent /self-improve --reference=reference_analysis_20251220.md
```

The agent will:
1. Read its own previous session
2. Read the reference analysis
3. Compare its output to the reference
4. Identify what it missed
5. Generate recommendations for improving its own instruction

## Benefits

1. **No Infinite Recursion**: Uses reference examples instead of another agent
2. **Human-in-the-Loop**: Humans provide high-quality examples
3. **Continuous Improvement**: Agent learns from references over time
4. **Measurable Progress**: Can track improvement against references
5. **Scalable**: Add more references as you find good examples

## Example Self-Improvement Output

```markdown
# Self-Improvement Analysis: meta_improve_agent Session 20251220

## What I Did
- Analyzed apply_improve_text_agent session
- Generated 5 recommendations
- Saved report in 1.3 minutes

## What the Reference Did Better
1. **Systematic Framework**: Reference used 6 evaluation dimensions
   - I only covered 3 dimensions
   - Missing: Tool Usage Effectiveness, Output Quality, Instruction Clarity

2. **Specific Recommendations**: Reference provided exact text to add
   - I gave general suggestions
   - Missing: Code blocks with exact instruction text

3. **Evidence-Based**: Reference quoted specific session examples
   - I summarized without quotes
   - Missing: Actual bash commands and outputs from session

## Gaps in My Instruction
1. **No Evaluation Framework**: My instruction doesn't list dimensions to evaluate
2. **No Recommendation Template**: No structure for formatting recommendations
3. **No Evidence Requirement**: Doesn't require quoting session examples

## Self-Improvement Recommendations

### 1. Add Evaluation Framework
**Add to instruction after "Your Mission":**
```
## Meta-Analysis Framework

Evaluate these dimensions:
1. Workflow Adherence
2. Tool Usage Effectiveness
3. Error Counting Methodology
4. Best Practices Analysis Depth
5. Output Quality
6. Instruction Clarity Issues
```

### 2. Add Recommendation Template
**Add to instruction in STEP 4:**
```
For each issue, provide:
- category: Type of issue
- problem: What went wrong
- evidence: Specific examples (quoted from session)
- root_cause: Why instruction didn't prevent this
- recommendation: Exact text to add (with code blocks)
- suggested_location: Where to add it
- expected_impact: Quantified improvement
```

### 3. Require Evidence Quotes
**Add to instruction in STEP 3:**
```
For every claim, provide evidence:
- Quote actual bash commands used
- Show actual tool calls made
- Display actual outputs received
```

## Expected Impact
- Coverage: 3 dimensions → 6 dimensions (100% increase)
- Recommendation quality: General → Specific with code blocks
- Evidence: Summaries → Direct quotes
- Overall analysis quality: 6/10 → 9/10
```

## Implementation Steps

1. **Create reference repository**:
   ```bash
   mkdir -p openspec-memories/meta_improve_references
   ```

2. **Save my analysis as first reference**:
   - Save the analysis I provided as `reference_analysis_20251220_apply_improve_text.md`
   - Add metadata about what makes it good

3. **Add self-improvement mode to meta_improve_agent**:
   - Add `/self-improve` command
   - Add logic to read references
   - Add comparison logic

4. **Test the self-improvement workflow**:
   - Run meta_improve_agent normally
   - Run meta_improve_agent in self-improve mode
   - Verify it identifies gaps
   - Apply recommended improvements

5. **Iterate**:
   - Add more reference analyses over time
   - Continuously improve meta_improve_agent
   - Track improvement metrics

## Conclusion

This architecture solves the recursive improvement problem by:
- Using human-provided reference examples instead of another agent
- Enabling self-improvement through comparison to references
- Maintaining human-in-the-loop for quality control
- Avoiding infinite recursion while enabling continuous improvement

The meta_improve_agent becomes a **learning agent** that improves itself by studying high-quality examples, rather than requiring yet another meta-meta-improve agent.
