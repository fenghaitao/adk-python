# OpenSpec Integration - Quick Start Guide

## 30-Second Start

```bash
# From the adk-python repository root (uses default prompt)
./run_openspec.sh my_project

# Or pure interactive mode
./run_openspec.sh my_project --interactive

# Or with session saving for resuming later
./run_openspec.sh my_project --save-session
```

That's it! The script will:
1. ✅ Check prerequisites (OpenSpec CLI, ADK)
2. ✅ Initialize OpenSpec project structure
3. ✅ Launch the ADK agent
4. ✅ Automatically help you populate project.md (unless `--interactive` is used)
5. ✅ Optionally save session for resuming

**Default Prompt**: The agent automatically asks to help fill out `openspec/project.md` with your project details, tech stack, and conventions. This establishes important context before creating change proposals.

**Interactive Mode**: Use `--interactive` to skip the default prompt and start with a blank slate where you can type your own queries.

## First Interaction

Once the agent starts, try:

```
You: Please read the AGENTS.md file and explain the OpenSpec workflow

Agent: *Reads AGENTS.md and explains the proposal → review → implement → archive workflow*

You: Create a change proposal for adding user authentication

Agent: *Creates openspec/changes/add-user-auth/ with proposal.md, tasks.md, and spec deltas*
```

## Common Commands

### List Active Changes
```
You: List all active changes
Agent: *Runs: openspec list*
```

### Show Change Details
```
You: Show me the details of add-user-auth
Agent: *Runs: openspec show add-user-auth*
```

### Validate Specs
```
You: Validate the add-user-auth change
Agent: *Runs: openspec validate add-user-auth*
```

### Archive Completed Work
```
You: Archive the add-user-auth change
Agent: *Runs: openspec archive add-user-auth --yes*
```

## Project Structure

After initialization, your project has:

```
my_project/
├── AGENTS.md              # AI agent instructions
└── openspec/
    ├── project.md         # Project context
    ├── specs/             # Current specs (truth)
    ├── changes/           # Active proposals
    │   └── archive/       # Completed changes
```

## Next Steps

1. **Populate project context**: Ask the agent to help fill out `openspec/project.md`
2. **Create your first change**: Describe a feature you want to add
3. **Review and refine**: Iterate on specs until they're clear
4. **Implement**: Let the agent work through the tasks
5. **Archive**: Merge completed changes into specs

## Need Help?

- Read the full [README.md](README.md) for detailed documentation
- Check [Troubleshooting](README.md#troubleshooting) for common issues
- See [Examples](README.md#examples) for real-world usage patterns

## Session Management

Save your work and resume later:

```bash
# Save session
./run_openspec.sh my_project --save-session

# Resume later
./run_openspec.sh my_project --resume

# Use different model when resuming
./run_openspec.sh my_project --resume --model iflow/qwen3-coder-plus
```

## Tips

- Always read `AGENTS.md` first to understand project conventions
- Use spec deltas (ADDED/MODIFIED/REMOVED) for clarity
- Validate specs before implementation
- Archive completed work to keep changes/ clean
- Save sessions with `--save-session` for long-running work
- Resume sessions with `--resume` to continue where you left off
