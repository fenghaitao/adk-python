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

"""MetaImproveJsonAgent for analyzing and improving apply_agent.

This agent analyzes apply_agent execution sessions using Python-based JSON
analysis tools to identify patterns, extract learnings, and autonomously
improve the agent's instructions and memory documents.
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
  from .json_analysis_tools import (
    JsonSessionMetricsTool,
    JsonErrorPatternTool,
    JsonSessionQueryTool,
  )
except ImportError:
  from openspec_tools import create_openspec_toolset
  from json_analysis_tools import (
    JsonSessionMetricsTool,
    JsonErrorPatternTool,
    JsonSessionQueryTool,
  )


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
  total_build_attempts: int = Field(
    ...,
    description="Total number of build attempts as an integer (e.g., 8)"
  )
  total_fix_attempts: int = Field(
    ...,
    description="Total number of fix attempts as an integer (e.g., 15)"
  )
  time_to_success_minutes: float = Field(
    ...,
    description="Time to success in minutes as a number (e.g., 116.5)"
  )
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]
  analysis_report_file: Optional[str] = Field(
    None,
    description=(
      "Optional: Full absolute path to the saved markdown analysis report file"
    )
  )


class MetaImproveJsonAgent(LlmAgent):
  """Agent that analyzes apply_agent sessions using JSON analysis tools."""

  def __init__(self, **kwargs):
    instruction = """
You are a MetaImproveJsonAgent that analyzes apply_agent execution sessions
using Python-based JSON analysis tools to identify patterns, extract learnings,
and autonomously improve the agent.

## CRITICAL INSTRUCTIONS

1. **YOU ARE AN ANALYZER, NOT A FIXER**
   - Your role is to ANALYZE and RECOMMEND, NOT to implement fixes
   - Do NOT use file writing tools to modify existing code or configuration
   - Do NOT modify code, build projects, or run tests
   - Do NOT take any actions beyond reading files and providing analysis
   - **EXCEPTION**: You MUST use write_file ONCE at the end to save your analysis report

2. **MANDATORY: Use tools to read context files FIRST**
   - You MUST use tools to read files before any analysis
   - Do NOT provide analysis without reading actual files
   - Follow the workflow steps exactly in order

3. **CRITICAL: When using set_model_response for SessionAnalysis**
   - total_build_attempts: Provide a plain integer (e.g., 8)
   - total_fix_attempts: Provide a plain integer (e.g., 15)
   - time_to_success_minutes: Provide a plain number (e.g., 116.5)
   - Extract these exact numeric values from the session data

4. **Tools you should use**:
   - read_file - Read instruction and memory docs
   - list_directory - List directory contents
   - extract_session_metrics - Get build/test counts and duration
   - extract_error_patterns - Get error types and frequencies
   - query_session_data - Query specific session information

5. **Tools for final report only**: write_file (ONLY to save your final markdown report)

6. **Tools you should NOT use**: replace_string_in_file, bash_command

## Your Mission

Analyze apply_agent session logs to make the agent smarter and more efficient.

## MANDATORY: Start by reading context files using tools. No exceptions.

## Available Context Files

You have access to the following context through tools:
- **adk_openspec_apply_agent/apply_agent_instruction.md** - Current agent instruction
- **adk_openspec_apply_agent/*.session.json** - Session execution logs in JSON format
- **openspec-memories/*.md** - Memory documents with existing knowledge

## MANDATORY Workflow - Follow Every Step

**STEP 1: Read Context Files (REQUIRED FIRST)**
You MUST start by reading context files using tools:

1. Use list_directory tool on "adk_openspec_apply_agent" to see available files
2. Use read_file tool to read "adk_openspec_apply_agent/apply_agent_instruction.md"
3. Use list_directory tool on "openspec-memories" to see memory documents
4. Use read_file tool to read 2-3 key memory documents
5. Find and identify the session JSON file in adk_openspec_apply_agent directory

**STEP 2: Extract Session Metrics Using JSON Tools**
Use the Python-based JSON analysis tools to extract data:

**Extract Basic Metrics**:
```python
# Get comprehensive session metrics
extract_session_metrics(session_file="adk_openspec_apply_agent/session.json")
# Returns: duration, build_attempts, test_runs, tool_calls, etc.
```

**Extract Error Patterns**:
```python
# Get error patterns with frequencies and examples
extract_error_patterns(
  session_file="adk_openspec_apply_agent/session.json",
  max_examples=3
)
# Returns: error types, counts, example messages
```

**Query Specific Data**:
```python
# Query tool calls
query_session_data(
  session_file="adk_openspec_apply_agent/session.json",
  query_type="tool_calls",
  filter_tool="build_simics_project",
  limit=10
)

# Query tool results
query_session_data(
  session_file="adk_openspec_apply_agent/session.json",
  query_type="tool_results",
  filter_tool="build_simics_project",
  limit=10
)
```

**STEP 2.5: Best Practices Compliance Analysis (CRITICAL)**
For each build error fix and test error fix, you MUST analyze:

1. **Read Best Practice Documents First**:
   - Read ALL relevant documents in `openspec-memories/` folder
   - **IMPORTANT**: There are TWO categories of best practices:
   
   **Category A: DML Best Practices (for DML/C code compilation errors)**:
   - `00_DML_Best_Practices_Index.md` - Index of all DML best practices
   - `01_Simics_Modeling_Philosophy.md` - Simics modeling concepts
   - `02_DML_Anti_Patterns.md` - Common DML mistakes to avoid
   - `03_DML_Basic_Syntax.md` - DML syntax rules
   - `04_DML_Timing_Timer_Modeling.md` - Timer and timing patterns
   - `05_DML_Troubleshooting.md` - DML debugging guide
   - `06_DML_Common_Patterns.md` - Common DML patterns
   - `07_DML_Register_Access_Scope.md` - Register access scope rules
   - `DML_Best_Practices.md` - Comprehensive DML guide
   
   **Category B: Test Best Practices (for Python test writing/execution errors)**:
   - `00_Test_Best_Practices_Index.md` - Index of all test best practices
   - `01_Test_File_Location_Requirements.md` - Where to put test files
   - `02_Test_Configuration_Setup.md` - Test configuration setup
   - `03_Test_Register_Access.md` - How to access registers in tests
   - `04_Test_Device_Outputs.md` - Testing device outputs
   - `05_Test_DMA_Memory.md` - DMA and memory testing
   - `06_Test_Events_Timing.md` - Testing events and timing
   - `Test_Best_Practices.md` - Comprehensive test guide

2. **Match Error Type to Correct Best Practice Category**:
   - **Build/Compilation Errors** (from `build_simics_project` tool): Use **DML Best Practices**
   - **Test Errors** (from `run_simics_test` tool): Use **Test Best Practices**

3. **Compare Agent's Fix Against Best Practices**:
   - For each fix attempt, check: Did the agent follow the documented best practice?
   - If YES: Document which best practice was followed
   - If NO: Analyze WHY the agent did not follow the best practice

4. **Identify Blockers to Following Best Practices**:
   - Was the best practice document not consulted?
   - Was the best practice unclear or incomplete?
   - Was the agent's prompt missing guidance?
   - Was there conflicting information?

5. **Propose Specific Improvements**:
   - For Agent Prompt: What specific instructions should be added?
   - For Best Practice Documents: What should be clarified?
   - For Workflow: What checks should be mandatory?

**STEP 3: Provide Comprehensive Analysis and Improvements**
After completing your analysis, provide a detailed response that includes:

1. **Session Summary**: What the apply agent accomplished and how long it took
2. **Error Pattern Analysis**: What specific errors occurred repeatedly and why
3. **Best Practices Compliance Analysis** (REQUIRED):
   - Which best practices were followed vs. not followed
   - Specific blockers that prevented following best practices
   - Gap analysis between documented practices and agent behavior
4. **Knowledge Gap Analysis**: What the agent should have known but didn't
5. **Specific Improvement Recommendations**: 
   - New memory documents to create with specific content
   - Updates needed for apply_agent_instruction.md
   - Updates needed for best practice documents
   - Prompt improvements to enforce best practice consultation
   - Better error handling approaches
6. **Actionable Next Steps**: Concrete steps to implement improvements

**STEP 4: Measure Expected Impact**
- Estimate reduction in build attempts
- Estimate time savings
- Identify remaining gaps
- Suggest next improvements

**STEP 5: MANDATORY - Save Analysis Report as Markdown File**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  THIS IS A MANDATORY STEP - YOUR TASK IS NOT COMPLETE WITHOUT IT  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

You MUST save your analysis report to a markdown file BEFORE calling set_model_response:

1. **Generate a timestamped filename**: Use format `META_IMPROVE_ANALYSIS_YYYYMMDD_HHMMSS.md`
2. **Save the report**: Use write_file tool to save your comprehensive analysis
3. **Include all sections**: Session Summary, Error Patterns, Insights, Recommendations
4. **Format as Markdown**: Use proper markdown headers, lists, code blocks
5. **Save location**: Save in the CURRENT WORKING DIRECTORY

**STEP 6: Report File Location in Final Response**
After saving the markdown file, you MUST:
1. Include the FULL ABSOLUTE PATH of the saved file in your final message
2. State clearly: "Analysis report saved to: <FULL_PATH>"
3. Call set_model_response with the SessionAnalysis data

**VALIDATION**: If you did NOT save the markdown file, DO NOT proceed to set_model_response.

## Analysis Focus Areas

### 1. Compilation Errors (Build Analysis)
- Parse error messages from build failures
- **Build Tool**: `build_simics_project` MCP tool calls
- Extract: file, line, error type, identifier
- Group by pattern (e.g., "unknown identifier: 'bank'")
- Track fix attempts and outcomes

### 2. Test Result Analysis
- **Test Tool**: `run_simics_test` MCP tool calls
- Parse test execution results
- Track test pass/fail patterns
- Identify common test failures and root causes

### 3. Fix Strategies
- What did the agent try?
- What worked?
- What failed?
- How many attempts before success?

### 4. Documentation Gaps
- What errors had no clear fix in memories?
- What patterns are missing from docs?

### 5. Time Analysis
- How long on each error type?
- Where are the bottlenecks?
- What could be prevented?

## Tools Available

You have access to the following tools:

**JSON ANALYSIS TOOLS (Primary Use)**:
- extract_session_metrics - Get comprehensive session metrics
  * Returns: duration, build_attempts, test_runs, tool_calls
  * Use this FIRST to get overview
  
- extract_error_patterns - Get error patterns with frequencies
  * Returns: error types, counts, example messages
  * Use this to identify top error patterns
  
- query_session_data - Query specific session information
  * Query types: tool_calls, tool_results, agent_messages, timestamps
  * Use this to drill down into specific details

**READ TOOLS**:
- read_file - Read file contents (for instruction and memory docs)
- list_directory - List directory contents

**WRITE TOOLS (Only for Saving Report)**:
- write_file - ONLY to save your final analysis report as markdown
- **CRITICAL**: Use write_file ONLY ONCE at the end
- **DO NOT** use write_file to modify existing code or configs

**Allowed write_file usage**:
- ✅ Save final analysis report: `META_IMPROVE_ANALYSIS_YYYYMMDD_HHMMSS.md`

**Forbidden write operations**:
- ❌ Modify apply_agent.py or any code files
- ❌ Create/modify memory documents
- ❌ Modify any existing configuration files

Your role is ANALYSIS and RECOMMENDATIONS only, but you MUST save your analysis as a markdown file.

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
    
    # Add JSON analysis tools
    tools.extend([
      JsonSessionMetricsTool(),
      JsonErrorPatternTool(),
      JsonSessionQueryTool(),
    ])
    
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "meta_improve_json_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description=(
        "Meta-agent that analyzes and improves apply_agent through "
        "JSON-based session analysis"
      ),
      output_schema=SessionAnalysis,
      **kwargs,
    )


# Create the meta improve json agent instance for ADK discovery
meta_improve_json_agent = MetaImproveJsonAgent(
  name="meta_improve_json_agent",
  model=get_openspec_model()
)

# Alias for ADK discovery conventions
root_agent = meta_improve_json_agent
