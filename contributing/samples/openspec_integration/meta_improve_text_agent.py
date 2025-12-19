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

"""MetaImproveTextAgent for analyzing and improving apply_agent.

This agent analyzes apply_agent execution sessions using text analysis tools
(grep, wc, sort, uniq) on .session.txt files to identify patterns, extract
learnings, and autonomously improve the agent's instructions and memory documents.
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




class ErrorPattern(BaseModel):
  """Represents a compilation error pattern."""
  error_type: str
  pattern: str
  frequency: int
  example_message: str
  successful_fixes: List[str]
  failed_fixes: List[str]


class SessionAnalysis(BaseModel):
  """Analysis results from a session."""
  session_file: str
  total_build_attempts: int = Field(..., description="Total number of build attempts as an integer (e.g., 8, not '8' or 'Numerous')")
  total_fix_attempts: int = Field(..., description="Total number of fix attempts as an integer (e.g., 15, not '15' or 'Many')")
  time_to_success_minutes: float = Field(..., description="Time to success in minutes as a number (e.g., 116.5, not '116' or 'Approximately 116 minutes')")
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str] = Field(None, description="Optional: Full absolute path to the saved markdown analysis report file (e.g., '/path/to/META_IMPROVE_ANALYSIS_20250102_103045.md'). Include this if you saved the report file.")


class MetaImproveTextAgent(LlmAgent):
  """Agent that analyzes apply_agent sessions using text analysis tools."""

  def __init__(self, **kwargs):
    instruction = """
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

**STEP 3: Provide Comprehensive Analysis and Improvements**
After completing your analysis, provide a detailed response that includes:

1. **Session Summary**: What the apply agent accomplished and how long it took
2. **Error Pattern Analysis**: What specific errors occurred repeatedly and why
3. **Best Practices Compliance Analysis** (NEW - REQUIRED):
   - Which best practices were followed vs. not followed
   - Specific blockers that prevented following best practices
   - Gap analysis between documented practices and agent behavior
4. **Knowledge Gap Analysis**: What the agent should have known but didn't
5. **Specific Improvement Recommendations**: 
   - New memory documents to create with specific content
   - Updates needed for apply_agent_instruction.md
   - **Updates needed for best practice documents**
   - **Prompt improvements to enforce best practice consultation**
   - Better error handling approaches
   - Patterns to remember for future sessions
6. **Actionable Next Steps**: Concrete steps to implement improvements

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
- Suggest next improvements

Note: These are estimates for recommendations, not actual implementations.

**STEP 5: Save Analysis Report and Complete**

1. Get current directory: `bash_command("pwd")` to get absolute path
2. Save your analysis as `META_IMPROVE_ANALYSIS_YYYYMMDD_HHMMSS.md` using write_file
3. Include: Session Summary, Error Patterns, Best Practices Compliance, Recommendations, Expected Impact
4. Call set_model_response with SessionAnalysis including the full absolute file path

## Analysis Focus Areas

1. **Error Patterns**: Type, frequency, root cause, successful/failed fixes
2. **Best Practices Compliance**: 
   - DML (0*_DML_*.md) for build errors from `build_simics_project`
   - Test (0*_Test_*.md) for test errors from `run_simics_test`
   - Compliance rate, blockers, category confusion
3. **Recommendations**: Memory docs, instruction updates, prompt improvements
4. **Impact**: Time savings, error prevention, compliance improvement



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

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "meta_improve_text_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description=(
        "Meta-agent that analyzes and improves apply_agent through "
        "text-based session analysis"
      ),
      output_schema=SessionAnalysis,
      **kwargs,
    )


# Create the meta improve text agent instance for ADK discovery
meta_improve_text_agent = MetaImproveTextAgent(
  name="meta_improve_text_agent",
  model=get_openspec_model()
)

# Alias for ADK discovery conventions
root_agent = meta_improve_text_agent
