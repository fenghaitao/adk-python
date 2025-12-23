OpenSpec Improve Propose Power Package
=======================================

This is a Kiro Power that provides documentation and guidance for analyzing
OpenSpec proposal creation session files to improve agent performance over time.

Structure:
----------
powers/openspec-improve-propose/
├── POWER.md                    # Main documentation (with YAML frontmatter)
└── README.txt                  # This file

What This Power Does:
--------------------
This power provides documentation for analyzing OpenSpec proposal creation sessions.
It guides your AI assistant to:

1. Read session text files from adk_openspec_proposal_initial_agent/
2. Parse validation attempts, errors, and fixes
3. Identify recurring error patterns
4. Compare against agent instructions and memory documents
5. Generate specific improvement recommendations

No Installation Required:
------------------------
This is a documentation-only power. Your AI assistant can analyze session
files directly by reading text files - no ADK or Python dependencies needed.

How to Use:
-----------
Simply ask your AI assistant to analyze a session file:

  "Analyze the session text in adk_openspec_proposal_initial_agent/ and recommend 
   improvements to the agent instructions and memory documents"

The assistant will:
- Read the session text file
- Read agent instruction file (proposal_initial_agent_instruction.md)
- Read memory documents (openspec-memories/*.md)
- Provide specific recommendations for improvements

Files to Analyze:
----------------
- Session logs: adk_openspec_proposal_initial_agent/*.session.txt
- Instructions: adk_openspec_proposal_initial_agent/proposal_initial_agent_instruction.md
- Memory docs: openspec-memories/*.md

Common Error Patterns:
---------------------
1. Lowercase Keywords: Using "shall" instead of "SHALL"
2. Missing Scenarios: Requirements without #### Scenario: subsections
3. Invalid Structure: Wrong section headers or format
4. Incomplete Tasks: Vague tasks without specific sub-tasks
5. Missing Context: Insufficient implementation context

Quick Reference:
---------------
Validation Attempts:
  Count: grep -c "openspec validate" session.txt
  
Error Extraction:
  Keywords: grep "lowercase keyword" session.txt | grep -o "'[a-z]*'"
  Scenarios: grep "missing scenario" session.txt | wc -l

Spec Format (CRITICAL):
  Keywords: SHALL, SHOULD, MAY, MUST, MUST NOT (UPPERCASE only!)
  Structure: Each requirement needs #### Scenario: subsections
  Sections: ## ADDED Requirements, ## MODIFIED Requirements, etc.

Expected Impact:
---------------
After improvements:
- Validation attempts: 4 → 1 (75% reduction)
- Time to success: 6 min → 3 min (50% reduction)
- Error reduction: 90-100% fewer repeated errors
- Success rate: 25% → 80-90% (65% improvement)

For More Information:
--------------------
See POWER.md for complete documentation and example prompts.

Related Powers:
--------------
- openspec-improve-apply: Analyze implementation sessions
- openspec-propose: Create proposals
- openspec-apply: Implement changes

Version Information:
-------------------
- Last Updated: December 23, 2025

License:
--------
Apache 2.0
