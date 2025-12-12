# Simics Watchdog Timer (WDT) — Device Context (Short)

- Purpose: Model a simple WDT for Simics.
- Use: Context only. Workflow/guardrails come from the Proposal/Apply/Archive agents.

Constraints
- DML 1.4, preserve imports, minimal scope.
- Simics DML skeleton is already generated; implement side effects by filling TODOs in the device logic only.
- Do not modify register definition files (e.g., *-registers.dml) or any auto-generated artifacts.