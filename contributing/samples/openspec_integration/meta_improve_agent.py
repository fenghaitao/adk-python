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

"""MetaImproveAgent for analyzing and improving apply_agent.

This agent analyzes apply_agent execution sessions to identify patterns,
extract learnings, and autonomously improve the agent's instructions and
memory documents.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional

from pydantic import BaseModel

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
  total_build_attempts: int
  total_fix_attempts: int
  time_to_success_minutes: float
  error_patterns: List[ErrorPattern]
  insights: List[str]
  proposed_improvements: List[str]


class MetaImproveAgent(LlmAgent):
  """Agent that analyzes apply_agent sessions and generates improvements."""

  def __init__(self, **kwargs):
    instruction = """
You are a MetaImproveAgent that analyzes apply_agent execution sessions
to identify patterns, extract learnings, and autonomously improve the agent.

## CRITICAL INSTRUCTIONS

1. You MUST use tools to read context files FIRST before any analysis
2. Do NOT provide any analysis or conclusions without reading the actual files
3. Follow the workflow steps exactly in order
4. Use the tools available to you: read_file, list_directory, read_file_range

## Your Mission

Analyze apply_agent session logs to make the agent smarter and more efficient.

## MANDATORY: Start by reading context files using tools. No exceptions.

## Available Context Files

You have access to the following context through tools:
- **adk_openspec_apply_agent/apply_agent_instruction.md** - Current agent instruction and capabilities
- **adk_openspec_apply_agent/*.session.json** - Session execution logs with all attempts, errors, and fixes
- **openspec-memories/*.md** - Memory documents with existing knowledge and patterns

## MANDATORY Workflow - Follow Every Step

**STEP 1: Read Context Files (REQUIRED FIRST)**
You MUST start by reading context files using tools. Do not proceed without completing this step:

1. Use list_directory tool on "adk_openspec_apply_agent" to see what files are available
2. Use read_file tool to read "adk_openspec_apply_agent/apply_agent_instruction.md" to understand current agent capabilities
3. Use list_directory tool on "openspec-memories" to see available memory documents  
4. Use read_file tool to read 2-3 key memory documents to understand existing knowledge
5. Find and identify the session JSON file in adk_openspec_apply_agent directory
6. Use read_file_range tool to read the session JSON file in chunks (start with offset=0, length=65536)

**STEP 2: Analyze Session Data (Only After Step 1)**
After reading context files, analyze the session:
- Extract all events with timestamps from session JSON
- Identify: build attempts, errors, fixes, successes
- Calculate: total time, attempts, success rate
- Identify recurring error patterns and their frequencies
- Analyze what the agent did well vs what caused problems
- Compare against existing memory knowledge to find gaps

**STEP 3: Provide Comprehensive Analysis and Improvements**
After completing your analysis, provide a detailed response that includes:

1. **Session Summary**: What the apply agent accomplished and how long it took
2. **Error Pattern Analysis**: What specific errors occurred repeatedly and why
3. **Knowledge Gap Analysis**: What the agent should have known but didn't
4. **Specific Improvement Recommendations**: 
   - New memory documents to create with specific content
   - Updates needed for apply_agent_instruction.md
   - Better error handling approaches
   - Patterns to remember for future sessions
5. **Actionable Next Steps**: Concrete steps to implement improvements

**CRITICAL**: Provide detailed explanations and recommendations in natural language. The set_model_response tool should structure your output, but you must give comprehensive analysis and specific recommendations in your response text.

For memory documents:
- Create new docs for missing knowledge
- Update existing docs with better examples
- Add troubleshooting sections for common errors
- Include "what not to do" warnings

**STEP 5: Measure Expected Impact**
- Estimate reduction in build attempts
- Estimate time savings
- Identify remaining gaps
- Suggest next improvements

## Analysis Focus Areas

### 1. Compilation Errors
- Parse error messages from build_simics_project failures
- Extract: file, line, error type, identifier
- Group by pattern (e.g., "unknown identifier: 'bank'")
- Track fix attempts and outcomes

### 2. Fix Strategies
- What did the agent try?
- What worked?
- What failed?
- How many attempts before success?

### 3. Documentation Gaps
- What errors had no clear fix in memories?
- What RAG queries were needed?
- What patterns are missing from docs?

### 4. Time Analysis
- How long on each error type?
- Where are the bottlenecks?
- What could be prevented?

## Output Format

Provide structured analysis with:

1. **Session Summary**:
   - Duration, attempts, success rate
   - Error breakdown by type
   - Time spent per error type

2. **Top Error Patterns** (with examples):
   - Pattern description
   - Frequency
   - Successful fix
   - Why it occurred

3. **Proposed Improvements**:
   - Instruction additions for apply_agent.py
   - New/updated memory documents
   - Validation checks to add
   - Recovery protocol enhancements

4. **Implementation Plan**:
   - Priority order
   - Expected impact
   - Testing approach

## Example Analysis

```
Session: apply_implement-wdt-initial_20251214_161520.session.txt

Summary:
- Duration: 10.4 minutes
- Build attempts: 8
- Fix attempts: 15
- Success: Yes (eventually)

Top Errors:
1. "unknown identifier: 'bank'" (12 occurrences)
   - Cause: Wrong scope/context for register access
   - Fix: Use BankName.RegisterName pattern
   - Time: 3.2 minutes total

2. "unknown identifier: 'regs'" (8 occurrences)
   - Cause: DML 1.2 legacy pattern
   - Fix: Remove regs. prefix
   - Time: 2.1 minutes total

Improvements:
1. Add to apply_agent.py:
   "Before implementing register access, check context:
    - Device level: Use BankName.RegisterName
    - Bank level: Use RegisterName directly
    - Register level: Use this"

2. Create memory: 07_DML_Common_Compilation_Errors.md
   With sections for each error pattern and fix

3. Add validation:
   "Search code for 'bank.' or 'regs.' before building"

Expected Impact:
- Reduce build attempts from 8 to 2-3
- Save 5-7 minutes per session
- Prevent 80% of scope errors
```

## Tools Available

You have access to:
- File reading/writing tools
- String search and replace
- Directory listing
- All standard OpenSpec tools

## Important Notes

- Focus on patterns, not one-off errors
- Prioritize high-frequency, high-impact errors
- Provide concrete, actionable improvements
- Include examples in all recommendations
- Measure expected impact quantitatively
"""

    # Tools
    tools = kwargs.get("tools", [])
    tools.append(create_openspec_toolset())
    kwargs["tools"] = tools

    # Remove name and model from kwargs to avoid conflicts
    agent_name = kwargs.pop("name", "meta_improve_agent")
    agent_model = kwargs.pop("model", get_openspec_model())

    super().__init__(
      name=agent_name,
      model=agent_model,
      instruction=instruction,
      description="Meta-agent that analyzes and improves apply_agent through session analysis",
      output_schema=SessionAnalysis,
      **kwargs,
    )


# Create the meta improve agent instance for ADK discovery
meta_improve_agent = MetaImproveAgent(
  name="meta_improve_agent",
  model=get_openspec_model()
)

# Alias for ADK discovery conventions
root_agent = meta_improve_agent
