# MetaImproveTextAgent Enhancements

## Overview

This document explains the enhancements made to the `meta_improve_text_agent` to enable it to generate comprehensive analysis similar to human-level meta-analysis.

## Files Created

1. **meta_improve_text_agent_v2.py** - Enhanced version with comprehensive instruction
2. **meta_improve_text_agent_enhanced_instruction.md** - Standalone instruction document
3. **META_IMPROVE_AGENT_ENHANCEMENTS.md** - This document

## Key Enhancements

### 1. Meta-Analysis Framework

Added a structured framework for evaluating agent performance across 6 dimensions:

- **Workflow Adherence** - Did the agent follow prescribed steps?
- **Tool Usage Effectiveness** - Were tools used correctly and efficiently?
- **Error Counting Methodology** - Were counts accurate?
- **Best Practices Analysis Depth** - Was analysis thorough?
- **Output Quality** - Were recommendations actionable?
- **Instruction Clarity Issues** - What was unclear or missing?

### 2. Enhanced Output Schema

Added `InstructionIssue` model to capture structured recommendations:

```python
class InstructionIssue(BaseModel):
  category: str  # Issue type
  problem: str  # What went wrong
  evidence: List[str]  # Specific examples
  root_cause: str  # Why instruction failed
  recommendation: str  # Specific text to add
  suggested_location: str  # Where to add it
  expected_impact: str  # Quantified improvement
```

### 3. Comprehensive Workflow

**STEP 1: Read Context Files**
- Checklist-based approach
- Ensures all context is loaded before analysis

**STEP 2: Analyze Session Data**
- Extract basic metrics (duration, tool calls, status)
- Analyze agent behavior patterns
- Extract error patterns in agent behavior

**STEP 3: Deep Analysis**
- 3.1 Workflow Adherence Analysis
- 3.2 Tool Usage Effectiveness Analysis
- 3.3 Error Counting Methodology Analysis
- 3.4 Best Practices Analysis Depth
- 3.5 Output Quality Analysis

**STEP 4: Identify Instruction Gaps**
- Create InstructionIssue objects for each gap
- Provide evidence, root cause, and recommendations

**STEP 5: Generate Comprehensive Recommendations**
- Cover all analysis dimensions
- Provide specific, actionable improvements

**STEP 6: Create Structured Analysis Report**
- Detailed markdown template
- All required sections specified

**STEP 7: Save and Complete**
- Save report with timestamp
- Call set_model_response with structured data

### 4. Specific Bash Command Patterns

Added concrete examples for analyzing agent behavior:

```bash
# What tools did the agent use?
bash_command("grep 'TOOL_CALL' session.txt | grep -o '\\w\\+(' | sort | uniq -c | sort -rn")

# Did the agent read the right files?
bash_command("grep 'read_file' session.txt | grep -o 'file_path=[^)]*' | sort | uniq")

# Did the agent repeat the same action?
bash_command("grep 'TOOL_CALL' session.txt | grep -o '\\w\\+(' | uniq -c | awk '$1 > 3 {print}'")
```

### 5. Instruction Gap Analysis Template

Provided detailed template for each issue:

```markdown
### [N]. [Issue Category]

**Problem**: [Describe what the agent did wrong]

**Evidence from Session**:
- [Quote or describe specific agent behavior]
- [Show tool calls or outputs that demonstrate the issue]

**Root Cause**: [Why the instruction didn't prevent this]

**Recommendation**: Add this to the instruction:
```
[Exact text to add, with proper formatting]
```

**Suggested Location**: [Where in the instruction to add this]

**Expected Impact**: [Quantify improvement]
```

### 6. Comprehensive Report Template

Added detailed markdown template with all required sections:

- Executive Summary
- Session Overview
- Workflow Adherence Analysis
- Tool Usage Effectiveness Analysis
- Error Counting Methodology Analysis
- Best Practices Analysis Depth
- Output Quality Analysis
- Instruction Enhancement Recommendations
- Expected Impact Summary
- Implementation Priority
- Conclusion

## Comparison: Original vs. Enhanced

### Original Instruction

- Basic workflow (5 steps)
- Generic analysis guidance
- No structured output for instruction issues
- Limited examples for bash commands
- No framework for evaluating agent performance

### Enhanced Instruction (V2)

- Comprehensive workflow (7 steps with sub-steps)
- Meta-analysis framework with 6 evaluation dimensions
- Structured InstructionIssue output schema
- Concrete bash command patterns for agent behavior analysis
- Detailed templates for recommendations and reports
- Checklist-based approach to ensure completeness
- Specific guidance for identifying instruction gaps

## Usage

### Option 1: Use V2 Agent Directly

```python
from meta_improve_text_agent_v2 import meta_improve_text_agent_v2

# Use the enhanced agent
agent = meta_improve_text_agent_v2
```

### Option 2: Update Original Agent

Replace the instruction in `meta_improve_text_agent.py` with the content from `meta_improve_text_agent_enhanced_instruction.md`.

### Option 3: Load Instruction from File

Modify `meta_improve_text_agent.py` to load instruction from the markdown file:

```python
def __init__(self, **kwargs):
  instruction_file = Path(__file__).parent / "meta_improve_text_agent_enhanced_instruction.md"
  if instruction_file.exists():
    instruction = instruction_file.read_text()
  else:
    # Fallback to basic instruction
    instruction = "..."
```

## Expected Improvements

With the enhanced instruction, the meta_improve agent should:

1. **Identify specific instruction gaps** - Not just general issues
2. **Provide concrete examples** - Show exactly what went wrong
3. **Propose actionable improvements** - Give specific text to add
4. **Categorize issues systematically** - Group by type
5. **Estimate impact quantitatively** - Provide measurable improvements
6. **Be comprehensive** - Cover all aspects of agent performance

## Example Output

The enhanced agent will generate analysis like:

### 1. Error Counting Accuracy Issue

**Problem**: The agent counted tool calls (15 build_simics_project calls) but didn't count individual compilation errors within builds. One build can have 12+ errors.

**Evidence from Session**:
- Agent used: `grep -c 'build_simics_project' session.txt`
- Agent reported: 15 build attempts
- Agent did NOT extract individual error messages from each build

**Root Cause**: Instruction doesn't distinguish between build attempts (tool invocations) and individual compilation errors within each build.

**Recommendation**: Add explicit guidance:

```
**CRITICAL - Error Counting Methodology**:
- **Build Attempts**: Count of `build_simics_project` tool calls
- **Individual Errors**: Count each unique error message within builds
  * One build failure may contain 12+ distinct errors
  * Extract and count: `grep 'error:' | wc -l` for total errors
  * Group by type: `grep 'error:' | sed 's/.*error: //' | sort | uniq -c`
- **Fix Attempts**: Count of code modification actions between builds
```

**Suggested Location**: Add new section after 'CRITICAL INSTRUCTIONS' and before 'Available Context Files'

**Expected Impact**: 100% accuracy in error counting, enabling better analysis of error patterns

## Next Steps

1. Test the enhanced agent on existing apply_improve agent sessions
2. Validate that it generates comprehensive analysis
3. Iterate on the instruction based on results
4. Consider replacing the original agent with V2 once validated
5. Use the same enhancement pattern for other meta-agents

## Conclusion

The enhanced meta_improve_text_agent provides a structured, comprehensive approach to analyzing and improving apply_improve agents. By focusing on instruction gaps rather than just agent mistakes, it enables systematic improvement of the entire agent ecosystem.
