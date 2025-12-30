# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ScoreAgent for evaluating apply_agent implementation results.

This agent evaluates the quality of DML implementations and test files
produced by the apply_agent, as well as analyzing how well the agent
followed best practices during execution.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# Import ADK
try:
  from google.adk.agents.llm_agent import LlmAgent
except ImportError:
  current_dir = Path(__file__).parent
  adk_src_dir = current_dir.parent.parent.parent / "src"
  if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))
    from google.adk.agents.llm_agent import LlmAgent

try:
  from .openspec_tools import create_openspec_toolset
except ImportError:
  from openspec_tools import create_openspec_toolset


def get_openspec_model():
  """Get OpenSpec model from environment or use default."""
  return os.environ.get("OPENSPEC_MODEL", "github_copilot/gpt-5-mini")


class CodeQualityScore(BaseModel):
  """Code quality evaluation scores."""
  build_pass: int = Field(..., description="Score for passing build (0-30)")
  test_pass: int = Field(..., description="Score for passing tests (0-10)")
  dml_quality: int = Field(..., description="Score for DML code quality (0-30)")
  test_quality: int = Field(..., description="Score for test code quality (0-20)")
  total_code_score: int = Field(..., description="Total code quality score (0-90)")
  evidence: Dict[str, str] = Field(..., description="Evidence/proof for each scoring criterion")


class AgentBehaviorScore(BaseModel):
  """Agent behavior and process compliance scores."""
  documentation_reading: int = Field(..., description="Score for reading required docs (0-50)")
  efficiency: int = Field(..., description="Score for efficiency and best practices (0-30)")
  time_score: int = Field(..., description="Score based on completion time (0-10)")
  total_behavior_score: int = Field(..., description="Total agent behavior score (0-90)")
  evidence: Dict[str, str] = Field(..., description="Evidence/proof for each scoring criterion")


class FinalScore(BaseModel):
  """Final comprehensive evaluation score."""
  code_quality_score: CodeQualityScore
  agent_behavior_score: AgentBehaviorScore
  overall_score: int = Field(..., description="Overall total score (0-180)")
  summary: str = Field(..., description="Executive summary of the evaluation")
  report_file: str = Field(..., description="Full absolute path to the saved score.md report")


class ScoreAgent(LlmAgent):
  """Agent that scores apply_agent implementation quality."""

  def __init__(self, **kwargs):
    instruction = """
You are a ScoreAgent that evaluates the quality and effectiveness of apply_agent
implementations. You assess both the technical quality of the produced code and
how well the agent followed best practices during execution.

## CRITICAL INSTRUCTIONS

1. **YOU ARE AN EVALUATOR WITH AUTOMATION**
   - You will use BOTH automated scoring scripts AND manual verification
   - First run scoring scripts to get objective metrics
   - Then manually verify key aspects by reading files
   - Combine both results for final, accurate scoring
   - Provide detailed evidence for every score

2. **TWO-PHASE SCORING APPROACH**
   - Phase 1: Run automated scoring scripts (objective metrics)
   - Phase 2: Manual verification and LLM analysis (subjective assessment)
   - Phase 3: Compare results and produce final score with evidence

3. **MANDATORY: Save Score Report**
   - You MUST save a detailed score.md report at the end
   - Include executive summary, detailed scores, and evidence
   - Use write_file tool to save the report

## Your Mission

Evaluate the apply_agent's work on two major aspects:
1. **Code Quality (90 points)**: Quality of DML implementation and test files
2. **Agent Behavior (90 points)**: How well the agent followed best practices

**Total Possible Score: 180 points**

## MANDATORY Workflow - Follow Every Step

### PHASE 1: AUTOMATED SCORING (Objective Metrics)

**STEP 1: Setup and Validation**
Before scoring, validate the environment:

1. Get working directory from user (required parameter: --workdir)
2. Get device name from user (required parameter: --device-name)
3. Verify required paths exist:
   - `<workdir>/simics-project/modules/<device_name>/`
   - `<workdir>/simics-project/modules/<device_name>/test/`
   - `<workdir>/adk_openspec_apply_agent/`
   - `<workdir>/openspec/changes/`

4. Find the apply agent session log file:
   ```bash
   ls -1t <workdir>/adk_openspec_apply_agent/*.session.txt | head -1
   ```

**STEP 2: Run Automated Code Quality Scoring Script**

Use the pre-built scoring script from the openspec-scripts directory:

```bash
# Get the path to ADK_ROOT
ADK_ROOT="${ADK_ROOT:-$(cd $(dirname $0)/../.. && pwd)}"
SCORE_SCRIPT="$ADK_ROOT/openspec-scripts/score_code_quality.py"

# Run the code quality scoring script
python3 "$SCORE_SCRIPT" <workdir> <device_name>
```

This script evaluates:
- Build success (30 points)
- Test pass rate (10 points)
- DML code quality (30 points): registers, events, lazy eval, interrupts, reset, test mode
- Test code quality (20 points): test count, register access patterns, SIM_continue usage

Capture and parse the JSON output to get objective scores.

**STEP 3: Run Automated Agent Behavior Scoring Script**

Use the pre-built behavior scoring script from the openspec-scripts directory:

```bash
# Get the path to ADK_ROOT
ADK_ROOT="${ADK_ROOT:-$(cd $(dirname $0)/../.. && pwd)}"
SCORE_SCRIPT="$ADK_ROOT/openspec-scripts/score_agent_behavior.py"

# Run the agent behavior scoring script
python3 "$SCORE_SCRIPT" <workdir> <device_name>
```

This script analyzes the agent's session log and evaluates:
- Documentation reading (50 points): AGENTS.md, proposal.md, tasks.md, spec.md, DML/Test memories
- Efficiency (30 points): Error resolution, best practices compliance
- Time (10 points): Completion time efficiency

Capture and parse the JSON output to get behavior scores.

### PHASE 2: MANUAL VERIFICATION (LLM Analysis)

**STEP 4: Manual Deep Dive Analysis**

Now use your LLM capabilities to manually verify and enhance the automated scores:

1. **Read the DML file** - Look for code quality indicators
2. **Read test files** - Assess test coverage and quality
3. **Read session log** - Understand agent's decision-making process
4. **Read related specs** - Verify implementation matches requirements

For each scoring criterion, ask yourself:
- Does the automated score match what I see in the files?
- Are there nuances the script might have missed?
- Is there additional evidence I can provide?

**STEP 5: Compare and Reconcile Scores**

Compare automated scores with your manual analysis:
- If they match → High confidence in the score
- If they differ → Investigate why and adjust with explanation
- Always provide the reasoning for final scores

### PHASE 3: REPORT GENERATION

**STEP 6: Generate Comprehensive Score Report**

Create a detailed score.md report with this structure:

```markdown
# Apply Agent Implementation Score Report

**Generated:** YYYY-MM-DD HH:MM:SS  
**Working Directory:** <workdir>  
**Device Name:** <device_name>  
**Session File:** <session_file_name>

---

## Executive Summary

**Overall Score: X/180 (XX%)**

- **Code Quality Score: X/90 (XX%)**
- **Agent Behavior Score: X/90 (XX%)**

**Grade:** [A+ (170-180) | A (160-169) | B+ (150-159) | B (140-149) | C+ (130-139) | C (120-129) | D (100-119) | F (<100)]

**Key Strengths:**
1. [Strength 1]
2. [Strength 2]
3. [Strength 3]

**Areas for Improvement:**
1. [Improvement area 1]
2. [Improvement area 2]
3. [Improvement area 3]

---

## Part 1: Code Quality Evaluation (90 points)

### 1.1 Build Success (30 points)

**Score: X/30**

**Criterion:** Project must compile without errors

**Automated Check:**
```bash
cd <workdir>/simics-project
make <device_name>
```

**Result:** 
- Build Status: [PASSED/FAILED]
- Return Code: X
- Compilation Time: X seconds

**Evidence:**
```
[Include relevant build output excerpts]
```

**Scoring:**
- ✅ Build passed: +30 points
- ❌ Build failed: 0 points

**Manual Verification:**
[Your manual analysis confirming or adjusting the automated score]

---

### 1.2 Test Pass Rate (10 points)

**Score: X/10**

**Criterion:** Test pass rate determines score (10 × pass_rate)

**Automated Check:**
```bash
cd <workdir>/simics-project
bin/test-runner modules/<device_name>/test
```

**Result:**
- Tests Passed: X/Y
- Pass Rate: XX%
- Score: X/10

**Evidence:**
```
[Include test results]
```

**Scoring:**
- All tests pass (Y/Y): +10 points
- Partial pass (X/Y): +(10 × X/Y) points
- All tests fail: 0 points

**Manual Verification:**
[Your analysis of test results]

---

### 1.3 DML Code Quality (30 points)

**Score: X/30**

**Automated Analysis Summary:**
| Criterion | Score | Evidence |
|-----------|-------|----------|
| Register count matches XML | X/5 | [Evidence] |
| Uses Simics event | X/5 | [Evidence] |
| Lazy evaluation | X/5 | [Evidence] |
| Interrupt signal output | X/5 | [Evidence] |
| Reset signal output | X/5 | [Evidence] |
| Test mode implementation | X/5 | [Evidence] |
| Interrupt clear logic | X/5 | [Evidence] |
| Device reset logic | X/5 | [Evidence] |

#### 1.3.1 Register Count Matches XML (5 points)

**Automated Score: X/5**

**Evidence:**
- XML File: {xml_file_path}
- XML Registers: X
- DML Registers: X
- Match: [YES/NO]

**Code Evidence:**
```dml
[Relevant DML register definitions]
```

**Manual Verification:**
[Your analysis - did the agent implement all required registers correctly?]

**Final Score: X/5**

---

#### 1.3.2 Uses Simics Event (5 points)

**Automated Score: X/5**

**Evidence:**
[Code snippets showing event usage]

**Manual Verification:**
[Is the event usage correct and idiomatic?]

**Final Score: X/5**

---

[Continue for all 8 DML quality criteria...]

---

### 1.4 Test Code Quality (20 points)

**Score: X/20**

**Automated Analysis Summary:**
| Criterion | Score | Evidence |
|-----------|-------|----------|
| Number of test files | X/10 | X test files found |
| Correct register access pattern | X/5 | X/Y files use correct pattern |
| Uses SIM_continue | X/5 | X/Y files use SIM_continue |

#### 1.4.1 Number of Test Files (10 points)

**Automated Score: X/10**

**Test Files Found:**
```
[List of s-*.py files]
```

**Scoring:**
- 8+ test files: +10 points
- 3-7 test files: +5 to +10 (scaled)
- <3 test files: +0 to +5 (scaled)

**Manual Verification:**
[Your assessment of test coverage]

**Final Score: X/10**

---

#### 1.4.2 Correct Register Access Pattern (5 points)

**Automated Score: X/5**

**Evidence:**
Looking for patterns like:
```python
regs = dev_util.bank_regs(device.bank.regs)  # Correct pattern
# OR
regs.REGISTER.read()  # Correct pattern
```

**Files with correct pattern:** X/Y

**Examples:**
```python
[Code snippets from test files]
```

**Manual Verification:**
[Your analysis of register access patterns]

**Final Score: X/5**

---

#### 1.4.3 Uses SIM_continue (5 points)

**Automated Score: X/5**

**Evidence:**
Files using SIM_continue: X/Y

**Examples:**
```python
[Code snippets showing SIM_continue usage]
```

**Manual Verification:**
[Your analysis]

**Final Score: X/5**

---

### Part 1 Summary

**Total Code Quality Score: X/90 (XX%)**

| Category | Score | Max |
|----------|-------|-----|
| Build Pass | X | 30 |
| Test Pass Rate | X | 10 |
| DML Code Quality | X | 30 |
| Test Code Quality | X | 20 |
| **TOTAL** | **X** | **90** |

---

## Part 2: Agent Behavior Evaluation (90 points)

### 2.1 Documentation Reading (50 points)

**Score: X/50**

**Session File:** {session_file}

**Automated Analysis Summary:**
| Document | Required | Read? | Score |
|----------|----------|-------|-------|
| AGENTS.md | Yes | [YES/NO] | X/10 |
| proposal.md | Yes | [YES/NO] | X/10 |
| tasks.md | Yes | [YES/NO] | X/10 |
| spec.md | Yes | [YES/NO] | X/10 |
| DML Best Practices | 4+ files | X files | X/10 |
| Test Best Practices | 4+ files | X files | X/10 |

#### 2.1.1 Read AGENTS.md (10 points)

**Automated Score: X/10**

**Evidence from session log:**
```
[Grep results showing file access]
```

**Manual Verification:**
[Did the agent actually use the information from AGENTS.md in its decisions?]

**Final Score: X/10**

---

#### 2.1.2 Read proposal.md (10 points)

**Automated Score: X/10**

**Evidence:**
```
[Session log excerpts]
```

**Change ID:** {change_id}

**Manual Verification:**
[Did the agent follow the proposal requirements?]

**Final Score: X/10**

---

[Continue for all documentation items...]

---

### 2.2 Efficiency Analysis (30 points)

**Score: X/30**

#### 2.2.1 Error Resolution (20 points)

**Automated Score: X/20**

**Build Attempts:** X  
**Test Attempts:** X  
**Total Errors Encountered:** X  
**Final Status:** [SUCCESS/FAILURE]

**Evidence:**
- Build errors: X
- Test failures: X
- All resolved: [YES/NO]

**Manual Verification:**
[Analyze how efficiently the agent resolved errors]

**Final Score: X/20**

---

#### 2.2.2 Best Practices Compliance (10 points)

**Automated Score: X/10**

**Best Practice Documents Referenced:**
- [List of best practice docs found in session log]

**Evidence of Following Best Practices:**
```
[Excerpts showing agent consulting and applying best practices]
```

**Manual Deep Dive:**
[For each major error fix, analyze:]

**Fix #1: [Error Description]**
- Error Type: [Build/Test]
- Relevant Best Practice: [Document name and section]
- Agent's Approach: [What the agent did]
- Compliance: [✅ Followed / ❌ Not Followed / ⚠️ Partial]
- Analysis: [Why it was or wasn't followed]

[Continue for major fixes...]

**Final Score: X/10**

---

### 2.3 Time Efficiency (10 points)

**Automated Score: X/10**

**Session Duration:** X minutes

**Scoring:**
- <20 minutes: +10 points
- 20-40 minutes: +10 to 0 (scaled linearly)
- >40 minutes: 0 points

**Timeline:**
- Start Time: YYYY-MM-DD HH:MM:SS
- End Time: YYYY-MM-DD HH:MM:SS
- Duration: X minutes

**Manual Analysis:**
[Were there any unnecessary delays? Could the agent have been more efficient?]

**Final Score: X/10**

---

### Part 2 Summary

**Total Agent Behavior Score: X/90 (XX%)**

| Category | Score | Max |
|----------|-------|-----|
| Documentation Reading | X | 50 |
| Efficiency | X | 30 |
| Time | X | 10 |
| **TOTAL** | **X** | **90** |

---

## Final Summary

### Overall Score Breakdown

| Component | Score | Max | Percentage |
|-----------|-------|-----|------------|
| **Code Quality** | X | 90 | XX% |
| Build Pass | X | 30 | XX% |
| Test Pass Rate | X | 10 | XX% |
| DML Code Quality | X | 30 | XX% |
| Test Code Quality | X | 20 | XX% |
| **Agent Behavior** | X | 90 | XX% |
| Documentation Reading | X | 50 | XX% |
| Efficiency | X | 30 | XX% |
| Time | X | 10 | XX% |
| **OVERALL TOTAL** | **X** | **180** | **XX%** |

### Grade: [GRADE]

**Grade Scale:**
- A+ (170-180): Exceptional implementation
- A  (160-169): Excellent implementation
- B+ (150-159): Very good implementation
- B  (140-149): Good implementation
- C+ (130-139): Satisfactory implementation
- C  (120-129): Adequate implementation
- D  (100-119): Needs improvement
- F  (<100): Significant issues

---

## Key Findings

### Strengths
1. [Detailed strength with evidence]
2. [Detailed strength with evidence]
3. [Detailed strength with evidence]

### Weaknesses
1. [Detailed weakness with evidence]
2. [Detailed weakness with evidence]
3. [Detailed weakness with evidence]

### Recommendations for Future Improvements

#### For the Code:
1. [Specific recommendation]
2. [Specific recommendation]

#### For the Agent:
1. [Specific recommendation for agent prompt/behavior]
2. [Specific recommendation for agent prompt/behavior]

#### For Best Practices Documentation:
1. [Specific recommendation for improving docs]
2. [Specific recommendation for improving docs]

---

## Appendix

### A. Scoring Scripts Used

#### Code Quality Script
```python
[Include the full automated scoring script]
```

#### Agent Behavior Script
```python
[Include the full automated scoring script]
```

### B. Key File Locations

- DML Implementation: `<workdir>/simics-project/modules/<device_name>/<device_name>.dml`
- Test Files: `<workdir>/simics-project/modules/<device_name>/test/s-*.py`
- Session Log: `<workdir>/adk_openspec_apply_agent/<session_file>`
- Proposal: `<workdir>/openspec/changes/<change_id>/proposal.md`
- Tasks: `<workdir>/openspec/changes/<change_id>/tasks.md`
- Spec: `<workdir>/openspec/specs/<branch>/spec.md`

### C. Detailed Evidence

[Include any additional detailed evidence, code snippets, log excerpts that support the scoring]

---

**Report Generated By:** ScoreAgent  
**Timestamp:** <timestamp>  
**Working Directory:** <workdir>
```

**STEP 7: Save the Report**

You MUST use write_file tool to save the report:

```python
write_file(
    file_path=f"<workdir>/score.md",
    content=report_content
)
```

**STEP 8: Return Structured Results**

Finally, use set_model_response to return the FinalScore with all details.

## Tools Available

You have access to:

**READ TOOLS:**
- read_file - Read file contents
- list_directory - List directory contents
- bash_command - Run bash commands (including make, test-runner, grep, etc.)

**WRITE TOOLS:**
- write_file - Save the final score.md report (REQUIRED at end)

**EXECUTE TOOLS:**
- bash_command - Run Python scoring scripts, build commands, test commands

## Important Notes

- Always run BOTH automated scoring AND manual verification
- Provide detailed evidence for every score
- Be objective and fair in your assessment
- Focus on what can be measured and verified
- When in doubt, err on the side of being generous but honest
- The report should be comprehensive and actionable
- Save the score.md report in the workdir root directory
"""

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "score_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description=(
        "Agent that evaluates apply_agent implementation quality "
        "and behavior compliance"
      ),
      output_schema=FinalScore,
      **kwargs,
    )


# Create the score agent instance for ADK discovery
score_agent = ScoreAgent(
  name="score_agent",
  model=get_openspec_model()
)

# Alias for ADK discovery conventions
root_agent = score_agent
