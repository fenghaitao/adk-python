# Simics Device Model Skill

This is a comprehensive Simics device model developer skill that orchestrates the complete device modeling workflow from specification analysis to implementation.

## Structure

```
simics-device-model/
├── SKILL.md                        # Main skill entry point with request routing logic
├── device-spec-analyzer.md         # Hardware spec analysis workflow
├── device-feature-proposal.md      # OpenSpec proposal creation workflow
├── device-implement.md             # DML/Python implementation workflow
├── simics-knowledge-search.md      # Simics/DML knowledge search workflow
└── memories/                       # Symlink to ../simics-knowledge-search/memories
```

## Workflow

The skill routes requests to the appropriate specialized workflow:

1. **Analyze spec** → Follow `device-spec-analyzer.md`
2. **Propose feature changes** → Follow `device-feature-proposal.md`
3. **Implement/apply [change-id]** → Follow `device-implement.md`
4. **Search Simics knowledge** → Follow `simics-knowledge-search.md`

## Usage

The LLM reads `SKILL.md` first, which provides routing logic based on user intent:
- Analyzing hardware specifications
- Creating feature proposals and task decomposition
- Implementing device models with DML 1.4
- Searching for Simics/DML documentation

Each specialized workflow document is self-contained with complete instructions.

## Integration with Existing Skills

The four original skills remain in their directories for backward compatibility:
- `device-spec-analyzer/` - Contains additional files like project.md
- `device-feature-proposal/` - Contains backup files
- `device-implement/` - Contains backup files
- `simics-knowledge-search/` - Contains memories/ directory (symlinked from here)

The unified skill consolidates the workflow instructions while preserving access to shared resources.
