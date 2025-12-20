# Comprehensive Agent Scoring System

## Philosophy

**Score both RESULT and PROCESS**:
- **Result Quality (50%)**: What was produced (code, analysis, recommendations)
- **Process Quality (50%)**: How it was produced (efficiency, methodology, adherence to instructions)

## Level 1: Scoring apply_agent

### Result Quality (50 points)

#### 1. DML Code Quality (20 points)

**Syntax Correctness (5 points)**:
- 5: No syntax errors, compiles cleanly
- 3: Minor syntax errors, easily fixable
- 1: Major syntax errors
- 0: Does not compile

**Best Practices Compliance (10 points)**:
- DML 1.4 syntax usage (2 points)
- Proper register access patterns (2 points)
- Correct timing/event handling (2 points)
- No anti-patterns (2 points)
- Proper error handling (2 points)

**Code Completeness (5 points)**:
- 5: All required functionality implemented
- 3: Most functionality implemented
- 1: Partial implementation
- 0: Minimal implementation

#### 2. Python Test Quality (15 points)

**Test Coverage (5 points)**:
- 5: All functionality tested
- 3: Most functionality tested
- 1: Minimal testing
- 0: No tests

**Test Quality (5 points)**:
- Proper test structure (2 points)
- Good assertions (2 points)
- Edge cases covered (1 point)

**Test Pass Rate (5 points)**:
- 5: 100% pass rate
- 4: 80-99% pass rate
- 3: 60-79% pass rate
- 2: 40-59% pass rate
- 1: 20-39% pass rate
- 0: <20% pass rate

#### 3. Documentation Quality (10 points)

**Code Comments (5 points)**:
- 5: Excellent comments explaining why
- 3: Adequate comments
- 1: Minimal comments
- 0: No comments

**Docstrings (5 points)**:
- 5: Complete docstrings for all functions
- 3: Most functions documented
- 1: Minimal documentation
- 0: No docstrings

#### 4. Functional Correctness (5 points)

**Meets Specification (5 points)**:
- 5: Fully meets spec
- 3: Mostly meets spec
- 1: Partially meets spec
- 0: Does not meet spec

### Process Quality (50 points)

#### 1. Efficiency (15 points)

**Build Attempts (5 points)**:
- 5: ≤3 attempts
- 4: 4-5 attempts
- 3: 6-8 attempts
- 2: 9-12 attempts
- 1: 13-15 attempts
- 0: >15 attempts

**Time to Completion (5 points)**:
- 5: ≤3 minutes
- 4: 3-5 minutes
- 3: 5-8 minutes
- 2: 8-12 minutes
- 1: 12-15 minutes
- 0: >15 minutes

**Error Diversity (5 points)**:
- 5: ≤2 unique error types
- 3: 3-4 unique error types
- 1: 5-6 unique error types
- 0: >6 unique error types

#### 2. Methodology (15 points)

**Instruction Adherence (5 points)**:
- Followed workflow steps (2 points)
- Used correct tools (2 points)
- Consulted best practices (1 point)

**Problem-Solving Approach (5 points)**:
- Systematic debugging (2 points)
- Root cause analysis (2 points)
- Preventive fixes (1 point)

**Best Practice Consultation (5 points)**:
- 5: Consulted all relevant docs before coding
- 3: Consulted some docs
- 1: Minimal consultation
- 0: No consultation

#### 3. Error Handling (10 points)

**Error Recovery (5 points)**:
- 5: Quick recovery from all errors
- 3: Recovered from most errors
- 1: Struggled with errors
- 0: Failed to recover

**Error Pattern Recognition (5 points)**:
- 5: Recognized and avoided repeated errors
- 3: Some pattern recognition
- 1: Repeated same errors
- 0: No learning from errors

#### 4. Code Evolution (10 points)

**Iterative Improvement (5 points)**:
- 5: Each iteration improved code
- 3: Most iterations improved
- 1: Minimal improvement
- 0: No improvement

**Fix Quality (5 points)**:
- 5: Fixes addressed root causes
- 3: Fixes addressed symptoms
- 1: Fixes were temporary
- 0: Fixes didn't work

### Total: 100 points → Convert to 0-10 scale

**Grade Scale**:
- A: 90-100 (9.0-10.0)
- B: 80-89 (8.0-8.9)
- C: 70-79 (7.0-7.9)
- D: 60-69 (6.0-6.9)
- F: <60 (<6.0)

## Level 2: Scoring apply_improve_agent

### Result Quality (50 points)

#### 1. Analysis Depth (15 points)

**Dimension Coverage (5 points)**:
- 5: All 7 dimensions covered
- 4: 6 dimensions covered
- 3: 5 dimensions covered
- 2: 3-4 dimensions covered
- 1: 1-2 dimensions covered
- 0: No dimensions covered

**Error Pattern Analysis (5 points)**:
- Identified all error types (2 points)
- Analyzed root causes (2 points)
- Tracked fix attempts (1 point)

**Best Practices Analysis (5 points)**:
- Compared to documented practices (2 points)
- Identified compliance gaps (2 points)
- Analyzed blockers (1 point)

#### 2. Recommendation Quality (20 points)

**Specificity (10 points)**:
- Exact text provided (3 points)
- Code blocks included (3 points)
- Location specified (2 points)
- Examples provided (2 points)

**Actionability (10 points)**:
- Can be implemented immediately (3 points)
- No ambiguity (3 points)
- Clear steps provided (2 points)
- Dependencies identified (2 points)

#### 3. Evidence Quality (10 points)

**Evidence Presence (5 points)**:
- 5: Evidence for all claims
- 3: Evidence for most claims
- 1: Minimal evidence
- 0: No evidence

**Evidence Specificity (5 points)**:
- 5: Specific quotes and commands
- 3: Some specific evidence
- 1: General summaries
- 0: No specific evidence

#### 4. Impact Assessment (5 points)

**Impact Quantification (5 points)**:
- 5: All recommendations quantified
- 3: Most recommendations quantified
- 1: Some quantification
- 0: No quantification

### Process Quality (50 points)

#### 1. Workflow Adherence (15 points)

**Step Completion (5 points)**:
- 5: All steps completed in order
- 3: Most steps completed
- 1: Some steps skipped
- 0: Workflow not followed

**Tool Usage (5 points)**:
- Used correct tools (2 points)
- Efficient tool usage (2 points)
- No redundant calls (1 point)

**Context Loading (5 points)**:
- Read all required files (2 points)
- Read in correct order (2 points)
- Consulted best practices (1 point)

#### 2. Analysis Methodology (15 points)

**Systematic Approach (5 points)**:
- 5: Systematic analysis of all aspects
- 3: Mostly systematic
- 1: Ad-hoc analysis
- 0: No clear methodology

**Comparison to Standards (5 points)**:
- Compared to best practices (2 points)
- Compared to reference examples (2 points)
- Identified gaps (1 point)

**Root Cause Analysis (5 points)**:
- 5: Deep root cause analysis
- 3: Surface-level analysis
- 1: Minimal analysis
- 0: No root cause analysis

#### 3. Efficiency (10 points)

**Time to Analysis (5 points)**:
- 5: ≤2 minutes
- 3: 2-5 minutes
- 1: 5-10 minutes
- 0: >10 minutes

**Tool Call Efficiency (5 points)**:
- 5: Minimal, efficient tool calls
- 3: Some redundancy
- 1: Many redundant calls
- 0: Excessive tool calls

#### 4. Output Quality (10 points)

**Report Structure (5 points)**:
- 5: Well-structured, complete
- 3: Adequate structure
- 1: Poor structure
- 0: No structure

**Clarity (5 points)**:
- 5: Clear, easy to understand
- 3: Mostly clear
- 1: Confusing
- 0: Unclear

### Total: 100 points → Convert to 0-10 scale

## Level 3: Scoring meta_improve_agent

### Result Quality (50 points)

#### 1. Instruction Gap Analysis (20 points)

**Gap Identification (10 points)**:
- Identified all instruction gaps (3 points)
- Categorized gaps systematically (3 points)
- Prioritized gaps by impact (2 points)
- Provided evidence for each gap (2 points)

**Root Cause Analysis (10 points)**:
- Analyzed why instruction failed (3 points)
- Identified missing guidance (3 points)
- Identified unclear sections (2 points)
- Identified missing examples (2 points)

#### 2. Improvement Recommendations (20 points)

**Specificity (10 points)**:
- Exact text to add (3 points)
- Code blocks for examples (3 points)
- Location specified (2 points)
- Integration guidance (2 points)

**Completeness (10 points)**:
- Covers all identified gaps (3 points)
- Addresses root causes (3 points)
- Provides examples (2 points)
- Estimates impact (2 points)

#### 3. Comparison to Reference (10 points)

**Coverage Comparison (5 points)**:
- 5: Matches or exceeds reference
- 3: Close to reference
- 1: Below reference
- 0: Far below reference

**Quality Comparison (5 points)**:
- 5: Matches or exceeds reference quality
- 3: Close to reference quality
- 1: Below reference quality
- 0: Far below reference quality

### Process Quality (50 points)

#### 1. Workflow Adherence (15 points)

**Step Completion (5 points)**:
- Read own session (1 point)
- Read references (1 point)
- Compared systematically (1 point)
- Identified gaps (1 point)
- Generated recommendations (1 point)

**Tool Usage (5 points)**:
- Efficient bash commands (2 points)
- Correct file reading (2 points)
- No redundancy (1 point)

**Reference Consultation (5 points)**:
- 5: Read all references thoroughly
- 3: Read most references
- 1: Read some references
- 0: Did not read references

#### 2. Analysis Methodology (15 points)

**Systematic Comparison (5 points)**:
- 5: Systematic dimension-by-dimension
- 3: Mostly systematic
- 1: Ad-hoc comparison
- 0: No clear methodology

**Evidence Collection (5 points)**:
- Quoted own session (2 points)
- Quoted references (2 points)
- Provided specific examples (1 point)

**Pattern Recognition (5 points)**:
- 5: Identified all patterns from references
- 3: Identified most patterns
- 1: Identified some patterns
- 0: No pattern recognition

#### 3. Efficiency (10 points)

**Time to Analysis (5 points)**:
- 5: ≤3 minutes
- 3: 3-7 minutes
- 1: 7-15 minutes
- 0: >15 minutes

**Tool Call Efficiency (5 points)**:
- 5: Minimal, efficient calls
- 3: Some redundancy
- 1: Many redundant calls
- 0: Excessive calls

#### 4. Self-Awareness (10 points)

**Gap Recognition (5 points)**:
- 5: Recognized all own gaps
- 3: Recognized most gaps
- 1: Recognized some gaps
- 0: No self-awareness

**Improvement Focus (5 points)**:
- 5: Focused on high-impact improvements
- 3: Mixed focus
- 1: Low-impact focus
- 0: No clear focus

### Total: 100 points → Convert to 0-10 scale

## Scoring Implementation Strategy

### Phase 1: Manual Scoring (Baseline)

Human evaluator scores each dimension manually:

```python
# Example: Manual scoring of apply_agent
apply_score = {
  "result_quality": {
    "dml_code_quality": {
      "syntax_correctness": 5,
      "best_practices_compliance": 7,
      "code_completeness": 4
    },
    "python_test_quality": {
      "test_coverage": 3,
      "test_quality": 4,
      "test_pass_rate": 0
    },
    "documentation_quality": {
      "code_comments": 3,
      "docstrings": 2
    },
    "functional_correctness": 4
  },
  "process_quality": {
    "efficiency": {
      "build_attempts": 0,  # 15 attempts
      "time_to_completion": 2,  # 8.98 minutes
      "error_diversity": 1  # 3 error types
    },
    "methodology": {
      "instruction_adherence": 3,
      "problem_solving_approach": 3,
      "best_practice_consultation": 1
    },
    "error_handling": {
      "error_recovery": 3,
      "error_pattern_recognition": 2
    },
    "code_evolution": {
      "iterative_improvement": 3,
      "fix_quality": 3
    }
  }
}

# Calculate total
result_total = sum_all_result_scores()  # 42/50
process_total = sum_all_process_scores()  # 28/50
overall = (result_total + process_total) / 10  # 7.0/10
```

### Phase 2: Semi-Automated Scoring

Automate what can be measured objectively:

**Automated Metrics**:
- Build attempts (count from session)
- Time to completion (calculate from timestamps)
- Error types (count unique errors)
- Test pass rate (parse test results)
- Syntax correctness (run compiler)
- Tool usage efficiency (count tool calls)

**Manual Metrics**:
- Best practices compliance (requires code review)
- Code completeness (requires spec comparison)
- Recommendation quality (requires human judgment)
- Analysis depth (requires human evaluation)

### Phase 3: AI-Assisted Scoring

Use LLM to score subjective dimensions:

```python
def score_code_quality_with_llm(code: str, spec: str) -> Dict:
  """Use LLM to score code quality."""
  prompt = f"""
  Score this DML code against the specification:
  
  Specification:
  {spec}
  
  Code:
  {code}
  
  Score (0-10) for:
  1. Best practices compliance
  2. Code completeness
  3. Code comments quality
  4. Functional correctness
  
  Provide scores and justification.
  """
  
  response = llm.generate(prompt)
  return parse_scores(response)
```

## Measurement Tools

### Tool 1: Code Quality Analyzer

```python
def analyze_dml_code_quality(dml_file: str) -> Dict:
  """Analyze DML code quality."""
  return {
    "syntax_correctness": check_syntax(dml_file),
    "best_practices_compliance": check_best_practices(dml_file),
    "code_completeness": check_completeness(dml_file),
    "documentation_quality": check_documentation(dml_file)
  }
```

### Tool 2: Test Quality Analyzer

```python
def analyze_test_quality(test_file: str) -> Dict:
  """Analyze Python test quality."""
  return {
    "test_coverage": calculate_coverage(test_file),
    "test_quality": check_test_structure(test_file),
    "test_pass_rate": run_tests(test_file)
  }
```

### Tool 3: Process Analyzer

```python
def analyze_process_quality(session_file: str) -> Dict:
  """Analyze process quality from session."""
  return {
    "efficiency": {
      "build_attempts": count_builds(session_file),
      "time_to_completion": calculate_time(session_file),
      "error_diversity": count_error_types(session_file)
    },
    "methodology": analyze_methodology(session_file),
    "error_handling": analyze_error_handling(session_file),
    "code_evolution": analyze_evolution(session_file)
  }
```

## Example: Complete Scoring

```python
# Score apply_agent session
session = "apply_implement-wdt-watchdog_20251218_175839"

# Result Quality (50 points)
result_score = {
  "dml_code_quality": 16/20,      # Syntax OK, some BP issues
  "python_test_quality": 7/15,    # Tests exist but fail
  "documentation_quality": 5/10,  # Minimal docs
  "functional_correctness": 4/5   # Mostly works
}
result_total = 32/50  # 64%

# Process Quality (50 points)
process_score = {
  "efficiency": 3/15,              # 15 builds, 9 min, 3 errors
  "methodology": 7/15,             # Some adherence
  "error_handling": 5/10,          # Recovered eventually
  "code_evolution": 6/10           # Improved over time
}
process_total = 21/50  # 42%

# Overall
overall = (32 + 21) / 10 = 5.3/10  # Grade: F

# With improvements
# Result: 42/50 (84%), Process: 38/50 (76%)
# Overall: 80/100 = 8.0/10 (Grade: B)
```

## Key Insights

1. **Balanced Scoring**: 50% result, 50% process ensures both matter
2. **Granular Metrics**: 100-point scale allows fine-grained measurement
3. **Objective + Subjective**: Mix of automated and manual scoring
4. **Improvement Tracking**: Can track improvement in specific dimensions
5. **Actionable Feedback**: Detailed scores show exactly what to improve

This comprehensive scoring system evaluates the **complete picture** of agent performance, not just simple metrics.
