OpenSpec Propose Power Package
===============================

This is a Kiro Power that provides complete OpenSpec proposal creation workflow
for Simics DML device implementations with domain knowledge and validation tools.

This power is a STANDALONE alternative to proposal_initial_agent:
- proposal_initial_agent: Runs with ADK (adk-python)
- openspec-propose power: Runs with Kiro IDE

Both provide the same OpenSpec proposal workflow capabilities for Simics development.

What This Power Does:
--------------------
Complete OpenSpec Proposal phase execution including:

1. OpenSpec workflow orchestration (STEP 1 → STEP 2 → STEP 3 → STEP 4)
2. Proposal structure creation (proposal.md, tasks.md, spec deltas)
3. DML 1.4 implementation patterns and constraints
4. Anti-pattern prevention (avoid performance killers and crashes)
5. Spec format validation (UPPERCASE keywords, scenarios)
6. Apply agent handoff preparation

Structure:
----------
powers/openspec-propose/
├── POWER.md                    # Complete workflow + domain knowledge
├── README.txt                  # This file
└── mcp.json                    # MCP server configuration (if needed)

Requirements:
-------------
- Simics 7.57.0 or later
- OpenSpec initialized project (changes/ and specs/ directories)
- openspec-memories/ directory in project (copied by setup script)
- OpenSpec CLI tools installed

How to Use:
-----------
This power follows the complete OpenSpec Proposal workflow:

1. Read OpenSpec documentation: openspec/AGENTS.md
2. Load specification context: specs/<branch-name>/spec.md
3. Create proposal with domain knowledge from openspec-memories/
4. Validate proposal: openspec validate <id> --strict
5. Return result: Confirm change_id and summary

Example workflow:
  "Create a proposal to implement the watchdog timer device"
  
  The power will:
  - Read openspec/AGENTS.md for workflow
  - Locate and read specs/<branch>/spec.md
  - Reference openspec-memories/ for DML patterns
  - Create proposal.md, tasks.md, and spec deltas
  - Validate with openspec validate --strict
  - Report change_id and summary

Knowledge Base Location:
-----------------------
All Simics DML documentation is in your project at:

openspec-memories/
├── 00_DML_Best_Practices_Index.md      # START HERE for DML
├── 00_Test_Best_Practices_Index.md     # START HERE for tests
├── 01_Simics_Modeling_Philosophy.md
├── 02_DML_Anti_Patterns.md             # CRITICAL: Read before timer/watchdog
├── 03_DML_Basic_Syntax.md
├── 04_DML_Timing_Timer_Modeling.md
├── 05_DML_Troubleshooting.md
├── 06_DML_Common_Patterns.md
├── 07_DML_Register_Access_Scope.md     # CRITICAL: Read for ANY DML
├── 01_Test_File_Location_Requirements.md
├── 02_Test_Configuration_Setup.md
├── 03_Test_Register_Access.md
├── 04_Test_Device_Outputs.md
├── 05_Test_DMA_Memory.md
└── 06_Test_Events_Timing.md

Key Features:
-------------
1. Memory Loading Protocol: Token-efficient knowledge loading
2. Anti-Pattern Prevention: Prevents proposing "obvious but wrong" implementations
3. Spec Format Validation: Ensures UPPERCASE keywords and scenario sections
4. Apply Agent Handoff: Creates detailed, actionable tasks for implementation
5. Guardrails: Keeps proposals minimal and scoped

Common Use Cases:
----------------
1. Creating OpenSpec proposals for Simics device implementations
2. Planning DML device models (timers, watchdogs, UARTs, etc.)
3. Defining comprehensive test requirements
4. Structuring implementation tasks
5. Validating proposal format and requirements

Quick Reference:
---------------
Spec Format (CRITICAL):
  Keywords: SHALL, SHOULD, MAY, MUST, MUST NOT (UPPERCASE only!)
  Structure: Each requirement needs #### Scenario: subsections
  Sections: ## ADDED Requirements, ## MODIFIED Requirements, etc.

DML Constraints:
  Syntax: DML 1.4 only
  Timing: Event-based (after statement), NOT cycle-by-cycle
  State: Use session keyword for state variables
  Files: NEVER edit *-registers.dml or add new .dml files

Proposal Structure:
  Context: What exists + what spec to use
  Why: Purpose of the change
  Scope: Files modified/added
  Requirements: Extracted from spec with scenarios

OpenSpec Commands:
-----------------
openspec list                           # List active changes
openspec show <id>                      # Display change details
openspec show <id> --json --deltas-only # Get additional context
openspec show <spec> --type spec        # Inspect spec details
openspec validate <id> --strict         # Validate proposal (MANDATORY)

For More Information:
--------------------
See POWER.md for complete workflow documentation and domain knowledge.

Version Information:
-------------------
- Simics Version: 7.57.0
- DML Version: 1.4
- API Version: 7
- Last Updated: December 23, 2025

License:
--------
Apache 2.0
