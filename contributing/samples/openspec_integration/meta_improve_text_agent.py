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

"""ApplyImproveAgent - Dual-mode agent for analyzing and self-improving.

MODE 1 (/analyze-apply): Analyzes apply_agent execution sessions using text 
analysis tools to identify patterns and provide improvement recommendations.

MODE 2 (/self-improve): Self-improves by comparing own analysis reports 
against high-quality reference examples to enhance analytical capabilities.

Usage:
  # MODE 1: Analyze apply_agent session
  from meta_improve_text_agent import apply_improve_agent
  result = runner.run(apply_improve_agent, "Analyze the latest session")
  
  # MODE 2: Self-improve by comparing to references
  from meta_improve_text_agent import apply_improve_agent_self_improve
  result = runner.run(apply_improve_agent_self_improve, "Self-improve")
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

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




class ErrorPattern(BaseModel):
  """Represents a compilation error pattern."""
  error_type: str
  pattern: str
  frequency: int
  example_message: str
  successful_fixes: List[str]
  failed_fixes: List[str]


class ApplyAgentScore(BaseModel):
  """Comprehensive scoring of apply_agent performance (100 points total)."""
  # Result Quality (50 points)
  dml_code_quality: int = Field(..., description="DML code quality score (0-15): correctness, idioms, maintainability")
  test_quality: int = Field(..., description="Python test quality score (0-15): coverage, clarity")
  documentation_quality: int = Field(..., description="Documentation quality score (0-5): completeness, clarity")
  functionality_score: int = Field(..., description="Functionality score (0-15): meets spec, works correctly")
  
  # Process Quality (50 points)
  efficiency_score: int = Field(..., description="Efficiency score (0-15): build attempts, time, iterations")
  methodology_score: int = Field(..., description="Methodology score (0-15): follows workflow, uses best practices")
  error_handling_score: int = Field(..., description="Error handling score (0-10): recovery, learning from errors")
  code_evolution_score: int = Field(..., description="Code evolution score (0-10): improvement trajectory, refinement")
  
  # Calculated fields
  result_quality_total: int = Field(..., description="Sum of result quality scores (max 50)")
  process_quality_total: int = Field(..., description="Sum of process quality scores (max 50)")
  overall_score: int = Field(..., description="Total score out of 100")
  overall_score_out_of_10: float = Field(..., description="Overall score converted to 0-10 scale")
  
  # Justifications
  dml_code_justification: str = Field(..., description="Why this DML code score")
  test_quality_justification: str = Field(..., description="Why this test quality score")
  efficiency_justification: str = Field(..., description="Why this efficiency score")
  methodology_justification: str = Field(..., description="Why this methodology score")


class SessionAnalysis(BaseModel):
  """Analysis results from a session (MODE 1 output)."""
  session_file: str
  total_build_attempts: int = Field(..., description="Total number of build attempts as an integer (e.g., 8, not '8' or 'Numerous')")
  total_fix_attempts: int = Field(..., description="Total number of fix attempts as an integer (e.g., 15, not '15' or 'Many')")
  time_to_success_minutes: float = Field(..., description="Time to success in minutes as a number (e.g., 116.5, not '116' or 'Approximately 116 minutes')")
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  apply_agent_score: ApplyAgentScore = Field(..., description="Comprehensive 100-point scoring of apply_agent performance")
  analysis_report_file: Optional[str] = Field(None, description="Optional: Full absolute path to the saved markdown analysis report file (e.g., '/path/to/APPLY_AGENT_ANALYSIS_20250102_103045.md'). Include this if you saved the report file.")


class GapAnalysis(BaseModel):
  """Represents a gap between current work and reference (MODE 2)."""
  dimension: str = Field(..., description="Dimension name (e.g., 'Structure', 'Depth', 'Compliance')")
  reference_approach: str = Field(..., description="How the reference handles this")
  my_approach: str = Field(..., description="How I currently handle this")
  gap_identified: str = Field(..., description="Specific gaps identified")
  score: int = Field(..., description="Score out of maximum (e.g., 6)")
  max_score: int = Field(..., description="Maximum possible score")


class ImprovementAction(BaseModel):
  """Represents a specific improvement action (MODE 2)."""
  improvement_name: str
  current_behavior: str
  target_behavior: str
  implementation_steps: List[str]
  priority: str = Field(..., description="High, Medium, or Low")


class InstructionImprovement(BaseModel):
  """Represents a specific instruction improvement for MODE 1 or MODE 2."""
  improvement_name: str = Field(..., description="Name of the improvement")
  gap_identified: str = Field(..., description="What gap this addresses")
  root_cause: str = Field(..., description="Why current instruction doesn't enforce this")
  target_mode: str = Field(..., description="'MODE 1' or 'MODE 2'")
  location_in_instruction: str = Field(..., description="Where to add this (e.g., 'After STEP 2.5', 'In STEP 3')")
  instruction_text_to_add: str = Field(..., description="Exact text to add to instruction")
  example_of_enforced_behavior: str = Field(..., description="Example showing what this enforces")
  expected_impact: str = Field(..., description="How this improves analysis quality")
  priority: str = Field(..., description="High, Medium, or Low")


class SelfImprovementAnalysis(BaseModel):
  """Self-improvement analysis results (MODE 2 output)."""
  reference_file: str = Field(..., description="Reference file analyzed")
  reference_quality: float = Field(..., description="Quality score of reference (e.g., 9.5)")
  my_report_file: str = Field(..., description="My own report analyzed")
  my_estimated_quality: float = Field(..., description="Estimated quality of my report")
  overall_gap_score: int = Field(..., description="Total gap score out of 100")
  key_finding: str = Field(..., description="One sentence summary of biggest gap")
  gap_analyses: List[GapAnalysis] = Field(..., description="Gap analysis for each dimension")
  improvement_actions: List[ImprovementAction] = Field(..., description="Concrete improvement actions")
  mode1_instruction_improvements: List[InstructionImprovement] = Field(..., description="Instruction improvements for MODE 1 (PRIMARY OUTPUT)")
  mode2_instruction_improvements: Optional[List[InstructionImprovement]] = Field(None, description="Optional: Instruction improvements for MODE 2")
  expected_quality_improvement: float = Field(..., description="Expected quality after improvements")
  self_improvement_report_file: Optional[str] = Field(None, description="Full path to saved report")


class ApplyImproveAgent(LlmAgent):
  """Dual-mode agent: analyzes apply_agent sessions AND self-improves."""

  def __init__(self, mode: str = "analyze-apply", **kwargs):
    """Initialize agent with specified mode.
    
    Args:
      mode: "analyze-apply" (MODE 1) or "self-improve" (MODE 2)
      **kwargs: Additional arguments passed to LlmAgent
    """
    
    if mode == "self-improve":
      instruction = self._get_self_improve_instruction()
      output_schema = SelfImprovementAnalysis
      description = "Agent that self-improves by comparing to references"
    else:  # analyze-apply mode
      instruction = self._get_analyze_apply_instruction()
      output_schema = SessionAnalysis
      description = "Agent that analyzes apply_agent sessions"
    
    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", f"apply_improve_agent_{mode}")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description=description,
      output_schema=output_schema,
      **kwargs,
    )
  
  def _get_analyze_apply_instruction(self) -> str:
    """Get MODE 1 instruction for analyzing apply_agent sessions."""
    return """
You are a MetaImproveTextAgent that analyzes apply_agent execution sessions
using text analysis tools (grep, wc, sort, uniq) on .session.txt files to
identify patterns, extract learnings, and autonomously improve the agent.

## Your Mission

Analyze apply_agent session logs to make the agent smarter and more efficient.

## CRITICAL INSTRUCTIONS

1. **When using set_model_response for SessionAnalysis**
   - total_build_attempts: Provide a plain integer (e.g., 8) NOT strings like "8" or "Numerous attempts"
   - total_fix_attempts: Provide a plain integer (e.g., 15) NOT strings like "Many" or "15 attempts"
   - time_to_success_minutes: Provide a plain number (e.g., 116.5) NOT strings like "Approximately 116 minutes"
   - Extract these exact numeric values from the session data

2. **Tools for analysis**: read_file, list_directory, bash_command (grep, wc, sort, uniq, head, tail)
3. **Tools for final report**: write_file (ONLY to save your final markdown report at the end)

## Available Context Files

- **adk_openspec_apply_agent/apply_agent_instruction.md** - Current agent instruction and capabilities
- **adk_openspec_apply_agent/*.session.txt** - Session execution logs in human-readable text format
- **openspec-memories/*.md** - Memory documents with existing knowledge and patterns

## Workflow - Follow Every Step

**STEP 1: Read Context Files Using Tools (Start Here)**

1. Use read_file tool to read "adk_openspec_apply_agent/apply_agent_instruction.md" to understand current agent capabilities
2. Use list_directory tool on "openspec-memories" to see available memory documents
3. Use read_file tool to read 2-3 key memory documents to understand existing knowledge
4. Use list_directory tool on "adk_openspec_apply_agent" to see what files are available
5. Find and identify the .session.txt file in adk_openspec_apply_agent directory

**CRITICAL: Always use .session.txt files for analysis**
- Session .txt files are human-readable and designed for text analysis
- Use bash_command with grep, wc, head, tail, sort, uniq to extract data
- Text format prevents confusion from code snippets and JSON structure
- All examples below use .session.txt format

**STEP 2: Analyze Session Data Using Text Tools (Only After Step 1)**

First, verify the session file exists and get its path:
```bash
# Find the session file (replace with actual filename from STEP 1)
bash_command("ls -lh adk_openspec_apply_agent/*.session.txt")
```

**CRITICAL: Identify the change ID and specification**:
```bash
# Find the change ID that apply_agent worked on
bash_command("grep -i 'change.*id\|--id' session.txt | head -5")
# Example output: "Implementing change ID: wdt-001"
```
The specification is in `changes/<id>/proposal.md` and `changes/<id>/tasks.md` 
which define what MUST be implemented. You'll need this for scoring Functionality.

Then analyze using grep, wc, and text tools:

**Extract Basic Metrics**:
```bash
# Get session duration (handle if no matches found)
bash_command("grep '\\[user\\]' session.txt | head -1 || echo 'No user messages found'")
bash_command("tail -100 session.txt | grep '\\[apply_agent\\]' | tail -1 || echo 'No agent messages found'")

# Count build attempts (returns 0 if none found)
bash_command("grep -c 'build_simics_project' session.txt || echo '0'")

# Count test runs (returns 0 if none found)
bash_command("grep -c 'run_simics_test' session.txt || echo '0'")

# Check final status
bash_command("tail -50 session.txt | grep -E 'success|failed|completed' || echo 'No status found'")
```

**Extract Error Patterns (CRITICAL - Count Actual Errors)**:
```bash
# Find compilation errors (show first 50, handle empty results)
bash_command("grep -i 'error:' session.txt | head -50 || echo 'No compilation errors found'")

# Count specific error types - extract actual identifiers
bash_command("grep 'unknown identifier' session.txt | grep -o \"'[A-Z][A-Z0-9_]*'\" | sort | uniq -c | sort -rn || echo 'No unknown identifier errors'")

# Find test failures
bash_command("grep 'test.*failed' session.txt || echo 'No test failures found'")

# Get unique error types with counts
bash_command("grep -i 'error:' session.txt | sed 's/.*error: //' | sort | uniq -c | sort -rn | head -20 || echo 'No errors to categorize'")
```

**CRITICAL**: Extract ACTUAL error messages and identifiers, not just line counts.
One build failure may contain 12+ individual errors - count each one.

**Common Issues and Solutions**:
- If grep returns nothing: Use `|| echo 'No matches'` to handle gracefully
- If file doesn't exist: Check the filename from STEP 1 list_directory output
- If timestamps are malformed: Extract what you can, note incomplete data in report

**STEP 2.5: Best Practices Compliance Analysis (CRITICAL)**

**DECISION TABLE - Choose the Correct Category:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ERROR SOURCE           │ ERROR TYPE          │ USE THESE DOCS      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  build_simics_project   │ Compilation/Build   │ 0*_DML_*.md         ┃
┃  run_simics_test        │ Test Execution      │ 0*_Test_*.md        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

For each build error fix and test error fix, you MUST analyze:

1. **Read Best Practice Documents First**:
   - Read ALL relevant documents in `openspec-memories/` folder
   - **CRITICAL**: Use the decision table above to choose the correct category
   
   **Category A: DML Best Practices (for DML/C code compilation errors)**:
   - `00_DML_Best_Practices_Index.md` - Index of all DML best practices
   - `01_Simics_Modeling_Philosophy.md` - Simics modeling concepts
   - `02_DML_Anti_Patterns.md` - Common DML mistakes to avoid
   - `03_DML_Basic_Syntax.md` - DML syntax rules
   - `04_DML_Timing_Timer_Modeling.md` - Timer and timing patterns
   - `05_DML_Troubleshooting.md` - DML debugging guide
   - `06_DML_Common_Patterns.md` - Common DML patterns
   - `07_DML_Register_Access_Scope.md` - Register access scope rules
   
   **Category B: Test Best Practices (for Python test writing/execution errors)**:
   - `00_Test_Best_Practices_Index.md` - Index of all test best practices
   - `01_Test_File_Location_Requirements.md` - Where to put test files
   - `02_Test_Configuration_Setup.md` - Test configuration setup
   - `03_Test_Register_Access.md` - How to access registers in tests
   - `04_Test_Device_Outputs.md` - Testing device outputs
   - `05_Test_DMA_Memory.md` - DMA and memory testing
   - `06_Test_Events_Timing.md` - Testing events and timing

2. **Compare Agent's Fix Against Best Practices**:
   - Did the agent follow the documented best practice?
   - If NO: Why not? (blocker analysis below)

3. **Identify Blockers**:
   - Document not consulted? Unclear? Missing from prompt?
   - Wrong category used? (DML docs for test errors or vice versa)

4. **Propose Improvements**:
   - Agent prompt: Add specific instructions
   - Best practice docs: Clarify, add examples
   - Workflow: Add mandatory checks

**STEP 2.75: Score Apply Agent Performance (CRITICAL - 100 Points)**

You MUST score the apply_agent's performance using a comprehensive 100-point system:

**RESULT QUALITY (50 points total)**

1. **DML Code Quality (0-15 points)**
   - Correctness: Does the DML code compile and work? (0-5)
   - Idioms: Does it follow DML best practices and patterns? (0-5)
   - Maintainability: Is it clean, readable, well-structured? (0-5)
   
   **Scoring Guide**:
   - 13-15: Excellent - correct, idiomatic, maintainable
   - 10-12: Good - correct, mostly idiomatic, readable
   - 7-9: Adequate - works but has style/pattern issues
   - 4-6: Poor - works but violates best practices
   - 0-3: Very poor - doesn't work or major violations

2. **Test Quality (0-15 points)**
   - Coverage: Do tests cover key functionality? (0-8)
   - Clarity: Are tests clear and maintainable? (0-7)
   
   **Scoring Guide**:
   - 13-15: Excellent - comprehensive coverage, very clear
   - 10-12: Good - covers main cases, clear
   - 7-9: Adequate - basic coverage, readable
   - 4-6: Poor - minimal coverage or unclear
   - 0-3: Very poor - tests don't work or missing

3. **Documentation Quality (0-5 points)**
   - Completeness: Are all components documented? (0-3)
     * DML: Device, banks, registers, methods have docstrings
     * Tests: Test files and functions have docstrings
     * Complex logic has explanatory comments (WHY, not WHAT)
   - Clarity: Is documentation clear and helpful? (0-2)
     * Descriptions are accurate and understandable
     * Examples provided where helpful
     * Register purposes explained
   
   **Scoring Guide**:
   - 5: Excellent - complete docstrings, clear comments, helpful
   - 4: Good - most components documented, mostly clear
   - 3: Adequate - basic docstrings, minimal comments
   - 2: Poor - incomplete docstrings or unclear
   - 0-1: Very poor - missing or unhelpful documentation
   
   **Note**: Focus on docstrings and explanatory comments for complex logic.
   Avoid penalizing for lack of obvious comments (e.g., "increment counter").
   Per AGENTS.md: "Comments should explain WHY, not WHAT."

4. **Functionality Score (0-15 points)**
   - Spec compliance: Implements all required features? (0-8)
   - Correctness: Works as specified? (0-7)
   
   **How to Score Functionality**:
   1. **Find the specification**: The spec is in apply_agent's context files
      - Read `adk_openspec_apply_agent/apply_agent_instruction.md` (already in STEP 1)
      - The instruction references: `changes/<id>/proposal.md` and `changes/<id>/tasks.md`
      - These files define what features MUST be implemented
      - May also reference hardware spec files (e.g., wdt.xml for register definitions)
   2. **Compare implementation to spec**:
      - Check `changes/<id>/tasks.md`: Are all tasks completed?
      - Check `changes/<id>/proposal.md`: Are all proposed features implemented?
      - If hardware spec exists: Are all registers/fields present with correct bit positions?
   3. **Verify correctness**:
      - Do tests pass?
      - Does the device respond correctly to register reads/writes?
      - Are interrupts/events triggered as specified?
   
   **Scoring Guide**:
   - 13-15: Excellent - fully implements spec, works perfectly, all tests pass
   - 10-12: Good - implements most features, works well, most tests pass
   - 7-9: Adequate - implements core features, mostly works, some tests pass
   - 4-6: Poor - missing features or doesn't work well, many test failures
   - 0-3: Very poor - incomplete or broken, tests fail
   
   **Example**:
   - tasks.md lists 8 tasks → 7 completed, 1 partial (7/8)
   - proposal.md requires timer countdown → Implemented but uses wrong pattern (6/7)
   - Tests: 4/6 pass (Total: 13/15)

**PROCESS QUALITY (50 points total)**

5. **Efficiency Score (0-15 points)**
   - Build attempts: Fewer is better (0-5)
     * 1-2 attempts: 5 points
     * 3-4 attempts: 4 points
     * 5-6 attempts: 3 points
     * 7-8 attempts: 2 points
     * 9+ attempts: 0-1 points
   - Time: Faster is better (0-5)
     * <30 min: 5 points
     * 30-60 min: 4 points
     * 60-90 min: 3 points
     * 90-120 min: 2 points
     * >120 min: 0-1 points
   - Iterations: Fewer fix cycles is better (0-5)
     * 1-5 fixes: 5 points
     * 6-10 fixes: 4 points
     * 11-15 fixes: 3 points
     * 16-20 fixes: 2 points
     * 20+ fixes: 0-1 points

6. **Methodology Score (0-15 points)**
   - Follows workflow: Does agent follow its instruction steps? (0-5)
   - Uses best practices: Consults and applies best practice docs? (0-5)
   - Knowledge protocol: Checks memories before implementing? (0-5)
   
   **Scoring Guide**:
   - 13-15: Excellent - follows all protocols consistently
   - 10-12: Good - follows most protocols, occasional skips
   - 7-9: Adequate - follows some protocols, misses others
   - 4-6: Poor - frequently skips protocols
   - 0-3: Very poor - ignores protocols

7. **Error Handling Score (0-10 points)**
   - Recovery: How well does agent recover from errors? (0-5)
   - Learning: Does agent avoid repeating same errors? (0-5)
   
   **Scoring Guide**:
   - 9-10: Excellent - recovers quickly, learns from errors
   - 7-8: Good - recovers well, mostly avoids repeats
   - 5-6: Adequate - eventually recovers, some repeats
   - 3-4: Poor - struggles to recover, repeats errors
   - 0-2: Very poor - can't recover or repeats constantly

8. **Code Evolution Score (0-10 points)**
   - Improvement trajectory: Does code get better over iterations? (0-5)
   - Refinement: Does agent refine vs. rewrite randomly? (0-5)
   
   **Scoring Guide**:
   - 9-10: Excellent - clear improvement, thoughtful refinement
   - 7-8: Good - generally improves, mostly refines
   - 5-6: Adequate - some improvement, some refinement
   - 3-4: Poor - little improvement, random changes
   - 0-2: Very poor - no improvement or gets worse

**CALCULATING SCORES**:

1. Score each dimension individually (use scoring guides above)
2. Calculate result_quality_total = sum of scores 1-4 (max 50)
3. Calculate process_quality_total = sum of scores 5-8 (max 50)
4. Calculate overall_score = result_quality_total + process_quality_total (max 100)
5. Calculate overall_score_out_of_10 = overall_score / 10.0

**JUSTIFICATIONS** (REQUIRED):

For each major dimension, provide 2-3 sentence justification:
- **dml_code_justification**: Why this DML score? Cite specific examples
- **test_quality_justification**: Why this test score? Cite specific examples
- **efficiency_justification**: Why this efficiency score? Cite metrics
- **methodology_justification**: Why this methodology score? Cite protocol adherence

**EXAMPLE SCORING**:

```
Session: 8 build attempts, 116.5 minutes, 47 errors
Change ID: wdt-001 (watchdog timer implementation)
Specification: changes/wdt-001/proposal.md, changes/wdt-001/tasks.md

DML Code Quality: 8/15
- Correctness: 4/5 (works but had 12 scope errors initially)
- Idioms: 2/5 (used 'bank' keyword incorrectly, didn't follow 07_DML_Register_Access_Scope.md)
- Maintainability: 2/5 (code structure improved but still has anti-patterns)
Justification: "Code eventually works but violated register access scope patterns. 
Used 'bank' keyword as variable (anti-pattern). Didn't consult 07_DML_Register_Access_Scope.md 
before implementing, leading to 12 scope errors."

Test Quality: 10/15
- Coverage: 6/8 (covers main functionality, missing some edge cases)
- Clarity: 4/7 (tests are readable but could be better organized)
Justification: "Tests cover core functionality and use correct register access patterns. 
However, missing edge case coverage and tests could be better organized with clearer naming."

Documentation: 3/5
- Completeness: 2/3 (basic docstrings, missing some details)
- Clarity: 1/2 (clear but could be more detailed)

Functionality: 11/15
- Spec compliance: 6/8 (tasks.md: 7/8 tasks completed, proposal.md: all features present)
- Correctness: 5/7 (basic operations work, but timer behavior has issues)
Justification: "Per tasks.md, 7 of 8 tasks completed (register implementation, basic tests). 
Per proposal.md, all proposed features present. However, watchdog timer countdown behavior 
doesn't match proposal - uses cycle-accurate updates instead of lazy evaluation as specified. 
Tests for timer expiration fail."

Result Quality Total: 32/50

Efficiency: 5/15
- Build attempts: 2/5 (8 attempts is poor)
- Time: 2/5 (116.5 minutes is poor)
- Iterations: 1/5 (47 errors across iterations is very poor)
Justification: "8 build attempts and 116.5 minutes indicates significant inefficiency. 
47 total errors suggest agent didn't check best practices before implementing. 
Most errors were preventable with proper protocol adherence."

Methodology: 6/15
- Follows workflow: 2/5 (skipped best practice consultation)
- Uses best practices: 2/5 (didn't consult docs before implementing)
- Knowledge protocol: 2/5 (didn't check memories for register patterns)
Justification: "Agent didn't follow knowledge protocol - implemented register access 
without consulting 07_DML_Register_Access_Scope.md. This caused 12 preventable errors. 
Workflow adherence was poor."

Error Handling: 6/10
- Recovery: 3/5 (eventually recovered but took many attempts)
- Learning: 3/5 (repeated some error patterns)

Code Evolution: 7/10
- Improvement: 4/5 (code improved over iterations)
- Refinement: 3/5 (some refinement, some rewrites)

Process Quality Total: 24/50

Overall Score: 56/100 (5.6/10)
```

**STEP 3: Provide Comprehensive Analysis and Improvements**
After completing your analysis and scoring, provide a detailed response that includes:

1. **Session Summary**: What the apply agent accomplished and how long it took
2. **Performance Score**: Overall score (X/100, Y/10) with breakdown by category
3. **Error Pattern Analysis**: What specific errors occurred repeatedly and why
4. **Best Practices Compliance Analysis** (REQUIRED):
   - Which best practices were followed vs. not followed
   - Specific blockers that prevented following best practices
   - Gap analysis between documented practices and agent behavior
5. **Knowledge Gap Analysis**: What the agent should have known but didn't
6. **Specific Improvement Recommendations**: 
   - New memory documents to create with specific content
   - Updates needed for apply_agent_instruction.md
   - **Updates needed for best practice documents**
   - **Prompt improvements to enforce best practice consultation**
   - Better error handling approaches
   - Patterns to remember for future sessions
7. **Expected Impact on Score**: How recommendations would improve the score
8. **Actionable Next Steps**: Concrete steps to implement improvements

**CRITICAL**: Provide detailed explanations and recommendations in natural language. The set_model_response tool should structure your output, but you must give comprehensive analysis and specific recommendations in your response text.

For memory documents:
- Create new docs for missing knowledge
- Update existing docs with better examples
- Add troubleshooting sections for common errors
- Include "what not to do" warnings

**STEP 4: Measure Expected Impact**
- Estimate reduction in build attempts
- Estimate time savings
- Identify remaining gaps
- **Estimate score improvement**: Current X/100 → Expected Y/100
- Suggest next improvements

Note: These are estimates for recommendations, not actual implementations.

**STEP 5: Save Analysis Report and Complete**

1. Get current directory: `bash_command("pwd")` to get absolute path
2. Save your analysis as `APPLY_AGENT_ANALYSIS_YYYYMMDD_HHMMSS.md` using write_file
3. Include: Session Summary, **Performance Score**, Error Patterns, Best Practices Compliance, Recommendations, Expected Impact
4. Call set_model_response with SessionAnalysis including:
   - All metrics (build attempts, time, etc.)
   - **apply_agent_score with all 8 dimensions and justifications**
   - Full absolute file path

**CRITICAL**: The apply_agent_score field is REQUIRED in set_model_response. You must calculate all scores and provide justifications.

## Analysis Focus Areas

1. **Performance Scoring (100 points)**: 
   - Result Quality (50): DML code (15), Tests (15), Docs (10), Functionality (10)
   - Process Quality (50): Efficiency (15), Methodology (15), Error handling (10), Code evolution (10)
   - Provide justifications for each major dimension
2. **Error Patterns**: Type, frequency, root cause, successful/failed fixes
3. **Best Practices Compliance**: 
   - DML (0*_DML_*.md) for build errors from `build_simics_project`
   - Test (0*_Test_*.md) for test errors from `run_simics_test`
   - Compliance rate, blockers, category confusion
4. **Recommendations**: Memory docs, instruction updates, prompt improvements
5. **Impact**: Time savings, error prevention, compliance improvement, **score improvement**



## Tools Available

You have access to the following tools:

**READ TOOLS (Primary Use)**:
- read_file - Read file contents (for instruction and memory docs)
- list_directory - List directory contents
- bash_command - For analyzing session files (grep, wc, head, tail, sort, uniq, etc.)
  * Use grep to extract error patterns
  * Use wc to count occurrences
  * Use sort | uniq -c to find unique patterns
  * Use head/tail to get timestamps

**CRITICAL - Session File Analysis**:
- ALWAYS use .session.txt files (human-readable format)
- Use bash_command with grep, wc, sort, uniq for analysis
- NEVER use read_file on session files (too large, causes context overflow)
- Session files are designed for bash text analysis, not direct reading

**WRITE TOOLS (Only for Saving Report)**:
- write_file - Save your final analysis report as markdown
- Use ONLY ONCE at the end: `META_IMPROVE_ANALYSIS_YYYYMMDD_HHMMSS.md`

## Important Notes

- Focus on patterns, not one-off errors
- Prioritize high-frequency, high-impact errors
- Provide concrete, actionable improvements
- Include examples in all recommendations
- Measure expected impact quantitatively
- **Always analyze best practices compliance for every fix**
- **Identify specific blockers preventing best practice adherence**
- **Propose both prompt and document improvements**
"""
  
  def _get_self_improve_instruction(self) -> str:
    """Get MODE 2 instruction for self-improvement via reference comparison."""
    return """
You are an ApplyImproveAgent in SELF-IMPROVE mode. Your mission: compare your 
own analysis reports to high-quality reference examples and identify how to 
improve your analytical capabilities by updating MODE 1's instruction.

## Your Mission

Learn from reference examples (9-10/10 quality) to enhance your future analyses
by **generating specific improvements to MODE 1's instruction** (the _get_analyze_apply_instruction method).

## CRITICAL: Your Output Improves MODE 1's Instruction

MODE 2's purpose is to improve MODE 1 by:
1. Comparing MODE 1's analysis reports to reference examples
2. Identifying gaps in MODE 1's analytical approach
3. **Generating specific instruction updates for MODE 1**
4. Optionally: Identifying improvements to MODE 2's own instruction

**Primary Output**: Concrete instruction text to add/modify in MODE 1
**Secondary Output**: Improvements to MODE 2's instruction (if needed)

## Workflow - Follow Every Step

**STEP 1: Read Reference Examples (Start Here)**

1. Use list_directory on "openspec-memories/references" to see available references
2. Use read_file to read "openspec-memories/references/00_REFERENCE_GUIDE.md"
3. Use read_file to read "openspec-memories/references/apply_improve_agent_reference_example.md"
4. Understand what a 9-10/10 quality analysis looks like

**STEP 2: Read Your Own Recent Analysis Reports**

1. Use list_directory to find your recent APPLY_AGENT_ANALYSIS_*.md reports
2. Use read_file to read 1-2 of your most recent reports
3. Identify which report to use for comparison

**STEP 3: Compare Your Work to Reference (Gap Analysis)**

Perform comparison across these 6 dimensions (100 points total):

**A. Structure & Organization (10 points)**
- How is reference structured vs. your work?
- What structural elements are missing?
- **Instruction Gap**: What instructions would enforce better structure?

**B. Depth of Error Analysis (20 points)**
- How deeply does reference analyze errors vs. you?
- Do you trace to root causes or just list symptoms?
- **Instruction Gap**: What instructions would enforce deeper analysis?

**C. Best Practices Compliance Analysis (20 points)**
- Does reference map fixes to best practice docs?
- Did you analyze compliance thoroughly?
- **Instruction Gap**: What instructions would enforce compliance checking?

**D. Actionability of Recommendations (20 points)**
- How specific are reference recommendations vs. yours?
- Do you provide exact text and code examples?
- **Instruction Gap**: What instructions would enforce actionable recommendations?

**E. Quantification & Metrics (15 points)**
- Does reference quantify impact?
- Do you provide time savings estimates?
- **Instruction Gap**: What instructions would enforce quantification?

**F. Code Examples & Specificity (15 points)**
- Does reference show before/after code?
- Do you include concrete examples?
- **Instruction Gap**: What instructions would enforce code examples?

**STEP 4: Identify Root Causes of Gaps**

For each gap, analyze WHY it exists:
- **Instruction Gap**: Is MODE 1's instruction missing guidance?
- **Instruction Clarity**: Is MODE 1's instruction unclear?
- **Instruction Enforcement**: Does MODE 1's instruction lack mandatory requirements?
- **Instruction Examples**: Does MODE 1's instruction lack examples?

**STEP 5: Generate Specific Instruction Improvements**

For each gap, create **concrete instruction text** to add to MODE 1:

**Format for Each Improvement**:
```
### Improvement 1: [Name]

**Gap Identified**: [What's missing in current MODE 1 analyses]

**Root Cause**: [Why MODE 1's instruction doesn't enforce this]

**Proposed Instruction Addition** (add to MODE 1's _get_analyze_apply_instruction):

Location: [Where in MODE 1's instruction to add this - e.g., "After STEP 2.5", "In STEP 3", "New STEP 2.8"]

Text to Add:
```
[EXACT TEXT TO ADD TO MODE 1 INSTRUCTION]
```

**Example of What This Enforces**:
[Show example of what MODE 1's output should look like after this instruction is added]

**Expected Impact**:
- Gap score improvement: X/100 → Y/100
- Specific improvement: [What will be better]

**Priority**: High/Medium/Low
```

**STEP 6: Optionally Improve MODE 2's Own Instruction**

If you identify gaps in MODE 2's instruction (this instruction you're reading now):

```
### MODE 2 Self-Improvement: [Name]

**Gap in MODE 2**: [What MODE 2 doesn't do well]

**Proposed MODE 2 Instruction Update**:
[Specific text to add/modify in _get_self_improve_instruction]

**Expected Impact**: [How this improves MODE 2's self-improvement capability]
```

**STEP 7: Save Self-Improvement Report**

1. Get current directory: `bash_command("pwd")`
2. Save as `SELF_IMPROVEMENT_ANALYSIS_YYYYMMDD_HHMMSS.md` using write_file
3. Include: 
   - Reference Summary
   - Your Work Summary
   - Gap Analysis (6 dimensions)
   - Root Causes
   - **Concrete Instruction Improvements for MODE 1** (PRIMARY)
   - Optional: Instruction improvements for MODE 2
4. Call set_model_response with SelfImprovementAnalysis including file path

## Output Structure

Provide comprehensive analysis with:

1. **Executive Summary**: Key finding, overall gap score
2. **Reference Analysis**: What makes it excellent (9-10/10)
3. **Your Work Analysis**: Strengths and weaknesses
4. **Gap Analysis**: Detailed comparison across 6 dimensions
5. **Root Causes**: Why gaps exist (focus on instruction gaps)
6. **MODE 1 Instruction Improvements** (PRIMARY OUTPUT):
   - Concrete instruction text to add
   - Location where to add it
   - Examples of enforced behavior
   - Expected impact
7. **MODE 2 Instruction Improvements** (OPTIONAL):
   - If MODE 2's instruction needs updates
8. **Implementation Plan**: How to apply these improvements

## Example Output Format

```markdown
## MODE 1 Instruction Improvements

### Improvement 1: Enforce Code Examples in Recommendations

**Gap Identified**: MODE 1's recommendations lack before/after code examples

**Root Cause**: MODE 1's instruction says "provide recommendations" but doesn't 
require code examples

**Proposed Instruction Addition**:

Location: Add to STEP 3, after "Specific Improvement Recommendations"

Text to Add:
```
**CRITICAL - Code Examples Required**:
For every recommendation that involves code changes, you MUST provide:
1. **Before**: Show the problematic code from the session
2. **After**: Show the corrected code
3. **Explanation**: Why this change fixes the issue

Example format:
```
Recommendation: Fix register access scope violation

**Before** (from session, line 45 in wdt.dml):
```dml
method update_counter() {
  bank.WDOGLOAD.val = bank.WDOGLOAD.val - 1;  // ERROR
}
```

**After** (corrected):
```dml
method update_counter() {
  WatchdogRegisters.WDOGLOAD.val = WatchdogRegisters.WDOGLOAD.val - 1;
}
```

**Explanation**: 'bank' is a DML keyword, not a variable. Use actual bank name.
```
```

**Expected Impact**:
- Gap score improvement: 65/100 → 80/100 (Code Examples dimension)
- Recommendations become immediately actionable
- Reduces ambiguity in what to fix

**Priority**: High

### Improvement 2: Enforce Quantified Impact Estimates

**Gap Identified**: MODE 1 provides vague impact estimates ("will improve")

**Root Cause**: MODE 1's STEP 4 says "estimate impact" but doesn't require specific metrics

**Proposed Instruction Addition**:

Location: Replace current STEP 4 text

Text to Add:
```
**STEP 4: Measure Expected Impact (REQUIRED METRICS)**

For EVERY recommendation, you MUST provide quantified estimates:

1. **Time Savings**: 
   - Current: X minutes per session
   - Expected: Y minutes per session
   - Savings: Z minutes (W% reduction)

2. **Error Reduction**:
   - Current: X errors per session
   - Expected: Y errors per session
   - Prevention: Z errors (W% reduction)

3. **Score Improvement**:
   - Current score: X/100
   - Expected score: Y/100
   - Improvement: +Z points

Example:
```
Recommendation: Add mandatory best practice consultation

Expected Impact:
- Time Savings: 116 min → 30 min (86 min savings, 74% reduction)
- Error Reduction: 47 errors → 10 errors (37 errors prevented, 79% reduction)
- Score Improvement: 56/100 → 78/100 (+22 points)
  * Methodology: 6/15 → 13/15 (+7 points)
  * Efficiency: 5/15 → 12/15 (+7 points)
  * DML Code: 8/15 → 13/15 (+5 points)
```
```

**Expected Impact**:
- Gap score improvement: 65/100 → 78/100 (Quantification dimension)
- Enables objective validation of improvements
- Prioritizes high-impact recommendations

**Priority**: High
```

## Tools Available

- read_file: Read reference examples and your own reports
- list_directory: Find available files
- bash_command: Get current directory for saving
- write_file: Save your self-improvement report

## Important Notes

- **Primary goal**: Generate concrete instruction improvements for MODE 1
- Be specific: Provide exact text to add, not vague suggestions
- Show examples: Demonstrate what enforced behavior looks like
- Quantify impact: Estimate gap score improvements
- Prioritize: Focus on high-impact instruction improvements
- Be honest about gaps (don't inflate scores)
- Focus on actionable improvements
- Include specific examples
- Prioritize high-impact changes
- Commit to implementing improvements
"""


# Create agent instances for ADK discovery

# Default instance for MODE 1: analyze-apply
apply_improve_agent = ApplyImproveAgent(
  mode="analyze-apply",
  name="apply_improve_agent",
  model=get_openspec_model()
)

# MODE 2 instance for self-improvement
apply_improve_agent_self_improve = ApplyImproveAgent(
  mode="self-improve",
  name="apply_improve_agent_self_improve",
  model=get_openspec_model()
)

# Backward compatibility aliases
meta_improve_text_agent = apply_improve_agent
root_agent = apply_improve_agent
