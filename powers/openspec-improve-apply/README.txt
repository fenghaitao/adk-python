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
This power provides documentation for analyzing OpenSpec apply execution sessions.
It guides your AI assistant to:

1. Read session JSON files from adk_openspec_apply_agent/
2. Parse build attempts, errors, and fixes
3. Identify recurring error patterns
4. Compare against agent instructions and memory documents
5. Generate specific improvement recommendations

No Installation Required:
------------------------
This is a documentation-only power. Your AI assistant can analyze session
files directly by reading JSON files - no ADK or Python dependencies needed.

How to Use:
-----------
Simply ask your AI assistant to analyze a session file:

  "Analyze the session JSON in adk_openspec_apply_agent/ and recommend 
   improvements to the agent instructions and memory documents"

The assistant will:
- Read the session JSON file
- Read agent instruction file (apply_agent_instruction.md)
- Read memory documents (openspec-memories/*.md)
- Provide specific recommendations for improvements

Files to Analyze:
----------------
- Session logs: adk_openspec_apply_agent/*.session.json
- Instructions: adk_openspec_apply_agent/apply_agent_instruction.md
- Memory docs: openspec-memories/*.md

For More Information:
--------------------
See POWER.md for complete documentation and example prompts.
