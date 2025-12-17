# OpenSpec Apply (User-Level Instructions)

Arguments (JSON):
$ARGUMENT

Instructions:
- Treat this as user-level guidance. Core safety and guardrails remain in the agent system instruction.
- Use the change id above and follow the OpenSpec Apply workflow.
- Load proposal context and tasks, then implement per the Memory Loading Protocol.
- Build and test iteratively using MCP tools (absolute paths only).
- Return ApplyResult output schema with completed/remaining tasks.
