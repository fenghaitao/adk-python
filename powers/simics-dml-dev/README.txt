Simics DML Development Power Package
=====================================

This is a Kiro Power that provides complete OpenSpec workflow execution for
Simics DML device implementation with domain knowledge and build/test tools.

This power is a STANDALONE alternative to apply_agent:
- apply_agent: Runs with ADK (adk-python)
- simics-dml-dev power: Runs with Kiro IDE

Both provide the same OpenSpec workflow capabilities for Simics development.

What This Power Does:
--------------------
Complete OpenSpec Apply phase execution including:

1. OpenSpec workflow orchestration (STEP 1 → STEP 2 → STEP 2.5 → STEP 3 → STEP 4)
2. DML 1.4 implementation patterns and best practices
3. Register access scope rules (prevents 100% of scope errors)
4. Event-based timing for timers and watchdogs
5. Python test creation and configuration
6. Anti-pattern prevention (avoid performance killers and crashes)
7. Implementation completeness checks
8. Build and test automation via MCP tools

Structure:
----------
powers/simics-dml-dev/
├── POWER.md                    # Complete workflow + domain knowledge
├── README.txt                  # This file
└── mcp.json                    # MCP server configuration

Requirements:
-------------
- Simics 7.57.0 or later
- OpenSpec initialized project (changes/ and specs/ directories)
- openspec-memories/ directory in project (copied by setup script)
- MCP server running at localhost:8056 (SSE transport)

How to Use:
-----------
This power follows the complete OpenSpec Apply workflow:

1. Read OpenSpec documentation: openspec/AGENTS.md
2. Load proposal context: changes/<id>/proposal.md, tasks.md
3. Implement with domain knowledge from openspec-memories/
4. Build iteratively: build_simics_project MCP tool
5. Check completeness: Verify behavior, not just structure
6. Test and validate: run_simics_test MCP tool
7. Report status: Update tasks.md, explain results

Example workflow:
  "Implement the watchdog timer from change add-wdt-device"
  
  The power will:
  - Read openspec/AGENTS.md for workflow
  - Load proposal and tasks from changes/add-wdt-device/
  - Reference openspec-memories/ for DML patterns
  - Build and test iteratively
  - Check implementation completeness
  - Report status and update tasks

MCP Tools Available:
-------------------
- build_simics_project: Compile DML device modules
- run_simics_test: Execute Python test suites

Both tools require ABSOLUTE paths (SSE transport requirement).

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
2. Implementation Completeness Check: Prevents "structure without behavior"
3. Anti-Pattern Prevention: Avoids 100-1000x performance issues
4. Guardrails: Keeps changes minimal and scoped
5. Absolute Path Handling: Correct MCP tool usage

Common Use Cases:
----------------
1. Implementing OpenSpec changes for Simics devices
2. Creating DML device models (timers, watchdogs, UARTs, etc.)
3. Writing comprehensive Python tests
4. Debugging compilation and runtime errors
5. Following TDD approach with build/test automation

Quick Reference:
---------------
Register Access (CRITICAL):
  Device level: ActualBankName.REGISTER.val  (e.g., WatchdogRegisters.WDTCR.val)
  Bank level:   REGISTER.val
  Register level: this.val
  
  NOTE: "bank" is a declaration keyword, NOT an access keyword!

Timing:
  Use: after (cycles) call event.event();
  Don't: Model cycle-by-cycle updates (causes 100-1000x slowdown)

Tests:
  Location: modules/<device>/test/test.py or s-*.py
  Functions: Any name (test_*, check_*, etc.)
  Clock: MUST set freq_mhz BEFORE instantiation
  Queue: MUST assign dev.queue = clk for timing devices

OpenSpec Commands:
-----------------
openspec list                           # List active changes
openspec show <id>                      # Display change details
openspec show <id> --json --deltas-only # Get additional context
openspec validate <id>                  # Validate changes

For More Information:
--------------------
See POWER.md for complete workflow documentation and domain knowledge.

Version Information:
-------------------
- Simics Version: 7.57.0
- DML Version: 1.4
- API Version: 7
- Last Updated: December 16, 2025

License:
--------
Apache 2.0
