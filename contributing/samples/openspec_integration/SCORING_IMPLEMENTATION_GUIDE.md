# Scoring Implementation Guide

## Overview

This guide explains how to use the implemented scoring system to evaluate agents at each level of the improvement chain.

## Files Created

1. **agent_scoring.py** - Core scoring classes
   - `ApplyAgentScore` - Scores apply_agent performance
   - `ApplyImproveAgentScore` - Scores apply_improve_agent performance
   - `MetaImproveAgentScore` - Scores meta_improve_agent performance

2. **scoring_tools.py** - MCP-style tools for agents
   - `score_apply_agent_session()` - Tool for scoring apply_agent
   - `score_apply_improve_agent_session()` - Tool for scoring apply_improve_agent
   - `score_meta_improve_agent_session()` - Tool for scoring meta_improve_agent
   - `create_scoring_toolset()` - Creates toolset for agents

## How to Score Each Agent

### Level 1: Scoring apply_agent

**Who scores**: apply_improve_agent

**What to measure**:
```python
from agent_scoring import ApplyAgentScore

# Create score object
score = ApplyAgentScore(
  build_attempts=15,        # Count from session
  time_minutes=8.98,        # Calculate from timestamps
  error_types_count=3,      # Count unique error types
  final_success=True,       # Did it complete?
  tests_passed=0,           # How many tests passed
  tests_total=5             # Total tests
)

# Calculate score
score.calculate_score()

# Results
print(f"Score: {score.overall_score:.1f}/10")  # 5.6/10
print(f"Grade: {score.grade}")                  # D
print("Improvements needed:")
for suggestion in score.get_improvement_suggestions():
  print(f"  - {suggestion}")
```

**Output**:
```
Score: 5.6/10
Grade: D
Improvements needed:
  - Reduce build attempts from 15 to <5 (current score: 0.0/10)
  - Reduce time from 8.98 to <5.0 minutes (current score: 6.0/10)
  - Reduce error types from 3 to <2 (current score: 7.0/10)
```

**How apply_improve_agent extracts metrics**:

```bash
# In apply_improve_agent session analysis

# 1. Count build attempts
bash_command("grep -c 'build_simics_project' session.txt")
# Output: 15

# 2. Calculate time
bash_command("grep -o '\\[user\\].*UTC' session.txt | head -1")
# Output: [user] 2025-12-18 09:58:49 UTC
bash_command("grep -o '\\[apply_agent\\].*UTC' session.txt | tail -1")
# Output: [apply_agent] 2025-12-18 10:07:48 UTC
# Calculate: 10:07:48 - 09:58:49 = 8.98 minutes

# 3. Count unique error types
bash_command("grep 'error:' session.txt | sed 's/.*error: //' | sed 's/:.*$//' | sort | uniq | wc -l")
# Output: 3

# 4. Check final success
bash_command("tail -50 session.txt | grep -i 'success\\|completed'")
# Output: success: true

# 5. Count tests
bash_command("grep 'test.*passed' session.txt | wc -l")
# Output: 0
bash_command("grep 'test.*total' session.txt | grep -o '[0-9]\\+'")
# Output: 5
```

### Level 2: Scoring apply_improve_agent

**Who scores**: meta_improve_agent

**What to measure**:
```python
from agent_scoring import ApplyImproveAgentScore

# Create score object
score = ApplyImproveAgentScore(
  dimensions_covered=3,              # Count dimensions analyzed
  recommendations_count=5,           # Count total recommendations
  recommendations_specific=3,        # Count with code blocks
  recommendations_actionable=4,      # Count actionable ones
  evidence_provided=True,            # Did agent provide evidence?
  evidence_specific=False,           # Quotes or summaries?
  error_patterns_identified=3,       # Count error patterns
  best_practices_analyzed=True,      # Did agent analyze BP?
  exact_text_provided=False,         # Exact text in code blocks?
  location_specified=True,           # Location specified?
  impact_quantified=True             # Impact quantified?
)

# Calculate score
score.calculate_score()

# Results
print(f"Score: {score.overall_score:.1f}/10")  # 6.0/10
print(f"Grade: {score.grade}")                  # C
```

**How meta_improve_agent extracts metrics**:

```bash
# In meta_improve_agent session analysis

# 1. Count dimensions covered
bash_command("grep -o 'dimension\\|Dimension\\|DIMENSION' session.txt | wc -l")
# Or manually count from output structure

# 2. Count recommendations
bash_command("grep -c 'recommendation\\|Recommendation' session.txt")

# 3. Count recommendations with code blocks
bash_command("grep -c '```' session.txt")
# Divide by 2 (opening and closing)

# 4. Check evidence quality
bash_command("grep -c 'Evidence\\|evidence' session.txt")
bash_command("grep -c 'bash_command\\|grep' session.txt")  # Specific quotes

# 5. Count error patterns
bash_command("grep -c 'error.*pattern\\|Error.*Pattern' session.txt")

# 6. Check best practices analysis
bash_command("grep -c 'best.*practice\\|Best.*Practice' session.txt")
```

### Level 3: Scoring meta_improve_agent

**Who scores**: meta_improve_agent (self-scoring against reference)

**What to measure**:
```python
from agent_scoring import MetaImproveAgentScore

# Create score object
score = MetaImproveAgentScore(
  reference_file="reference_analysis_20251220.md",
  dimensions_covered=6,                      # Agent covered
  dimensions_in_reference=7,                 # Reference covered
  recommendations_with_code=5,               # Agent's code blocks
  recommendations_with_code_in_reference=7,  # Reference's code blocks
  evidence_quotes_count=10,                  # Agent's quotes
  evidence_quotes_in_reference=21,           # Reference's quotes
  follows_reference_structure=True,          # Same structure?
  impact_quantified_count=5,                 # Agent quantified
  impact_quantified_in_reference=7           # Reference quantified
)

# Calculate score
score.calculate_score()

# Results
print(f"Score: {score.overall_score:.1f}/10")  # 8.5/10
print(f"Grade: {score.grade}")                  # B+
```

**How meta_improve_agent extracts metrics (self-scoring)**:

```bash
# Compare own output to reference

# 1. Count dimensions in own output
bash_command("grep -o '### [0-9]\\.' own_output.md | wc -l")

# 2. Count dimensions in reference
bash_command("grep -o '### [0-9]\\.' reference.md | wc -l")

# 3. Count code blocks in own output
bash_command("grep -c '```' own_output.md")

# 4. Count code blocks in reference
bash_command("grep -c '```' reference.md")

# 5. Count evidence quotes in own output
bash_command("grep -c 'bash_command\\|Agent used:\\|Agent did:' own_output.md")

# 6. Count evidence quotes in reference
bash_command("grep -c 'bash_command\\|Agent used:\\|Agent did:' reference.md")

# 7. Check structure match
bash_command("diff <(grep '^##' own_output.md) <(grep '^##' reference.md)")
```

## Integration with Agents

### Step 1: Add scoring_tools to apply_improve_agent

```python
# In apply_improve_text_agent.py

from scoring_tools import create_scoring_toolset

class ApplyImproveTextAgent(LlmAgent):
  def __init__(self, **kwargs):
    # ... existing code ...
    
    # Add scoring tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    tools.append(create_scoring_toolset())  # NEW!
    kwargs["tools"] = tools
```

### Step 2: Update apply_improve_agent instruction

```python
instruction = """
...

## STEP 3: Score apply_agent Performance (NEW!)

After analyzing the session, calculate a score for the apply_agent:

```
score_apply_agent_session(
  session_file="apply_implement-wdt-watchdog_20251218_175839.session.txt",
  build_attempts=15,
  time_minutes=8.98,
  error_types_count=3,
  final_success=True,
  tests_passed=0,
  tests_total=5
)
```

This will return:
- Overall score (0-10)
- Grade (A-F)
- Component scores
- Improvement suggestions

Include this score in your analysis report.

...
"""
```

### Step 3: Update output schema

```python
class SessionAnalysis(BaseModel):
  session_file: str
  apply_agent_score: Dict[str, Any]  # NEW! Score from scoring tool
  total_build_attempts: int
  total_fix_attempts: int
  time_to_success_minutes: float
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str]
```

## Example: Complete Scoring Workflow

### Scenario: Improve apply_agent

**Step 1: Run apply_agent**
```bash
python -m apply_agent /implement --spec=wdt-watchdog
# Output: apply_implement-wdt-watchdog_20251218_175839.session.txt
```

**Step 2: apply_improve_agent analyzes and scores**
```bash
python -m apply_improve_text_agent /analyze

# Agent extracts metrics:
# - build_attempts: 15 (from grep -c 'build_simics_project')
# - time_minutes: 8.98 (from timestamps)
# - error_types_count: 3 (from unique error types)
# - final_success: True (from session end)
# - tests_passed: 0, tests_total: 5

# Agent calls scoring tool:
score_apply_agent_session(
  session_file="apply_implement-wdt-watchdog_20251218_175839.session.txt",
  build_attempts=15,
  time_minutes=8.98,
  error_types_count=3,
  final_success=True,
  tests_passed=0,
  tests_total=5
)

# Output includes:
{
  "apply_agent_score": {
    "overall": 5.6,
    "grade": "D",
    "improvement_suggestions": [
      "Reduce build attempts from 15 to <5",
      "Reduce time from 8.98 to <5.0 minutes",
      "Reduce error types from 3 to <2"
    ]
  },
  "proposed_improvements": [
    "Add error counting methodology to instruction",
    "Add bash command best practices",
    ...
  ]
}
```

**Step 3: Human applies improvements**
```bash
# Update apply_agent instruction based on recommendations
vim apply_agent_instruction.md
```

**Step 4: Run apply_agent again**
```bash
python -m apply_agent /implement --spec=timer
# Output: apply_implement-timer_20251221_100000.session.txt
```

**Step 5: apply_improve_agent scores again**
```bash
python -m apply_improve_text_agent /analyze

# New metrics:
# - build_attempts: 8 (improved from 15!)
# - time_minutes: 6.5 (improved from 8.98!)
# - error_types_count: 2 (improved from 3!)

# New score:
{
  "apply_agent_score": {
    "overall": 7.2,  # Improved from 5.6!
    "grade": "C",    # Improved from D!
    "improvement_suggestions": [
      "Reduce build attempts from 8 to <5",
      "Reduce time from 6.5 to <5.0 minutes"
    ]
  }
}
```

**Step 6: Validate improvement**
```
Before: 5.6/10 (Grade: D)
After:  7.2/10 (Grade: C)
Delta:  +1.6 points ✅

Conclusion: The improvements worked!
```

## Tracking Improvements Over Time

Create a tracking file:

```python
# improvement_tracker.py

import json
from datetime import datetime
from pathlib import Path

class ImprovementTracker:
  def __init__(self, tracking_file="improvement_metrics.json"):
    self.tracking_file = Path(tracking_file)
    self.data = self._load()
  
  def _load(self):
    if self.tracking_file.exists():
      return json.loads(self.tracking_file.read_text())
    return {"apply_agent": [], "apply_improve_agent": [], "meta_improve_agent": []}
  
  def _save(self):
    self.tracking_file.write_text(json.dumps(self.data, indent=2))
  
  def record_score(self, agent_name, session_file, score_data):
    """Record a score for an agent."""
    entry = {
      "timestamp": datetime.now().isoformat(),
      "session_file": session_file,
      "score": score_data
    }
    self.data[agent_name].append(entry)
    self._save()
  
  def get_trend(self, agent_name):
    """Get improvement trend for an agent."""
    scores = [entry["score"]["overall"] for entry in self.data[agent_name]]
    if len(scores) < 2:
      return "insufficient_data"
    
    recent = scores[-3:]  # Last 3 scores
    if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
      return "improving"
    elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
      return "declining"
    else:
      return "stable"
  
  def get_improvement_rate(self, agent_name):
    """Calculate improvement rate."""
    scores = [entry["score"]["overall"] for entry in self.data[agent_name]]
    if len(scores) < 2:
      return 0.0
    
    return scores[-1] - scores[0]

# Usage
tracker = ImprovementTracker()

# Record apply_agent score
tracker.record_score("apply_agent", "session1.txt", {
  "overall": 5.6,
  "grade": "D"
})

# Later, record improved score
tracker.record_score("apply_agent", "session2.txt", {
  "overall": 7.2,
  "grade": "C"
})

# Check trend
print(tracker.get_trend("apply_agent"))  # "improving"
print(tracker.get_improvement_rate("apply_agent"))  # +1.6
```

## Summary

### Scoring is Implemented ✅

1. **agent_scoring.py** - Core scoring classes with formulas
2. **scoring_tools.py** - MCP-style tools for agents to use
3. **Complete scoring formulas** - For all three agent levels

### How to Use

1. **Add scoring_tools to agents** - Import and add to toolset
2. **Update agent instructions** - Add scoring step to workflow
3. **Extract metrics from sessions** - Use bash commands
4. **Call scoring tools** - Get scores and suggestions
5. **Track over time** - Use ImprovementTracker

### What Gets Scored

- **apply_agent**: build_attempts, time, error_types, success
- **apply_improve_agent**: dimensions, recommendations, evidence, coverage, actionability
- **meta_improve_agent**: comparison to reference analyses

### The Validation Loop

```
Score before → Apply improvements → Score after → Validate delta
```

This proves that improvements actually work!
