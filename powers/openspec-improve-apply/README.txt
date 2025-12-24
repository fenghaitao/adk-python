OpenSpec Improve Apply Power Package
=====================================

This is a Kiro Power that provides documentation and guidance for analyzing
OpenSpec apply session files to improve agent performance over time.

Structure:
----------
powers/openspec-improve-apply/
├── POWER.md                    # Main documentation (with YAML frontmatter)
└── README.txt                  # This file

What This Power Does:
--------------------
This power provides documentation for analyzing OpenSpec apply execution sessions
from **both ADK and Kiro CLI**. It guides your AI assistant to:

1. Read session text files from adk_openspec_apply_agent/ or kiro-apply/
2. Parse build attempts, errors, and fixes
3. Identify recurring error patterns
4. Compare against agent instructions and memory documents
5. Generate specific improvement recommendations
6. Create markdown analysis reports

Session File Support:
--------------------
- **ADK sessions**: adk_openspec_apply_agent/*.session.txt
- **Kiro CLI sessions**: kiro-apply/*.txt (converted from JSON)

Both formats are analyzed identically - same error patterns, same improvements.

No Installation Required:
------------------------
This is a documentation-only power. Your AI assistant can analyze session
files directly by reading text files - no ADK or Python dependencies needed.

How to Use:
-----------
Simply ask your AI assistant to analyze a session file:

**For ADK sessions:**
  "Analyze the session file adk_openspec_apply_agent/apply_*.session.txt 
   and recommend improvements to the agent instructions and memory documents"

**For Kiro CLI sessions:**
  "Analyze the session file kiro-apply/kiro-apply-session_*.txt
   and recommend improvements to the agent instructions and memory documents"

The assistant will:
- Read the session text file
- Read agent instruction file (apply_agent_instruction.md or POWER.md)
- Read memory documents (openspec-memories/*.md)
- Provide specific recommendations for improvements
- Generate a markdown analysis report in the session directory

Files to Analyze:
----------------
**ADK sessions:**
- Session logs: adk_openspec_apply_agent/*.session.txt
- Instructions: adk_openspec_apply_agent/apply_agent_instruction.md
- Memory docs: openspec-memories/*.md

**Kiro CLI sessions:**
- Session logs: kiro-apply/*.txt (converted from JSON)
- Instructions: adk-python/powers/openspec-apply/POWER.md
- Memory docs: openspec-memories/*.md

Output:
-------
Analysis reports are saved as markdown files:
- adk_openspec_apply_agent/analysis_<timestamp>.md (for ADK)
- kiro-apply/analysis_<timestamp>.md (for Kiro)

For More Information:
--------------------
See POWER.md for complete documentation and example prompts.

