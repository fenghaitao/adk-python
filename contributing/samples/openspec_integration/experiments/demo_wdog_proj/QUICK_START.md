# 🚀 Quick Start Guide - OpenSpec for DDM Watchdog Implementation

This guide will get you started implementing the watchdog device model using OpenSpec AI agents.

## 📋 What Has Been Set Up

✅ **Hardware Spec Parsed**: 9 registers extracted from `wdt.md`  
✅ **Change Proposals Created**: 9 OpenSpec proposals in `openspec/changes/`  
✅ **Scripts Ready**: Orchestrator and interactive runner scripts  
✅ **Git Integration**: Automatic repository initialization and commits  
✅ **OpenSpec Archiving**: Automatic archiving after task completion  
✅ **Documentation Complete**: Full user guide and setup summary  

## 🆕 New Features

### 1. Automatic Git Integration
- **Auto-Initialize**: Git repository created automatically if it doesn't exist
- **Auto-Commit**: Changes committed to Git after each task completion
- **Proper .gitignore**: Generated automatically to exclude build artifacts
- **Commit Messages**: Descriptive messages with change IDs

### 2. OpenSpec Archiving
- **Auto-Archive**: Completed changes moved to `openspec/changes/archive/`
- **Spec Updates**: OpenSpec automatically updates specs after archiving
- **Clean Workflow**: Active changes vs. completed changes clearly separated  

## 🎯 Three Ways to Start

### Method 1: Interactive Helper Script (Easiest) ⭐

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj

# Run the interactive helper
./run_openspec_interactive.sh

# Then choose:
# 1 - Start fresh (implement all registers)
# 2 - Resume previous session
# 3 - Implement specific register
```

### Method 2: Direct OpenSpec Command

```bash
# Activate OpenSpec environment
source ~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate

# Run OpenSpec with context
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj

~/wp5/ai_agents/adk-openspec/run_openspec.sh \
    demo_wdog_openspec \
    "Help me implement the watchdog registers. Start by reviewing openspec/changes/ and implementing the proposals one by one. Begin with implement-watchdog-load." \
    --model iflow/Qwen3-Coder \
    --save-session
```

### Method 3: Regenerate Tasks for Different Project

```bash
# Use the general orchestrator for any DDM project
python3 run_openspec_from_ddm.py \
    --project /path/to/your/project \
    --dml modules/your_device/your_device.dml \
    --spec /path/to/spec.md \
    --model iflow/Qwen3-Coder
```

## 📁 What's in Your Project

```
demo_wdog_proj/
│
├── 📄 Quick Starts
│   ├── QUICK_START.md                    ← YOU ARE HERE
│   ├── run_openspec_interactive.sh       ← Interactive helper (Method 1)
│   └── run_openspec_from_ddm.py          ← Task generator (Method 3)
│
├── 📚 Documentation
│   ├── README_OPENSPEC_DDM.md            ← Comprehensive user guide
│   ├── OPENSPEC_SETUP_SUMMARY.md         ← What was created
│   └── wdt.md                            ← Hardware specification
│
├── 🎯 OpenSpec Proposals (AI will implement these)
│   └── openspec/changes/
│       ├── implement-watchdog-load/
│       ├── implement-watchdog-value/
│       ├── implement-watchdog-control/
│       └── ... (6 more)
│
├── 💻 Implementation (AI will edit these)
│   └── modules/demo_watchdog/
│       ├── demo_watchdog.dml             ← Device model (to be implemented)
│       └── test/                         ← Tests (to be created)
│
└── 🔧 Generated Helpers
    ├── run_all_openspec_tasks.sh         ← Batch runner
    └── openspec_tasks_summary.json       ← Machine-readable task list
```

## 🎬 Example Session

Here's what a typical session looks like:

```bash
# 1. Start the interactive script
$ ./run_openspec_interactive.sh

# Git repository initialized automatically if needed
📦 Initializing Git repository...
✅ Git repository initialized

# 2. Choose option 1 (Start fresh)
Choose an option:
1) Start fresh implementation (all registers)
2) Resume from saved session
3) Implement specific register
Enter choice [1-4]: 1

# 3. OpenSpec AI agent starts
# The agent will:
# - Read the change proposals
# - Review wdt.md specification
# - Implement registers in modules/demo_watchdog/demo_watchdog.dml
# - Create tests in modules/demo_watchdog/test/

# 4. Interact with the agent
You: "Start with the WDOGLOAD register"
AI: "I'll implement the WDOGLOAD register. Let me review the proposal..."
    [Implements the register]
    "Done! The WDOGLOAD register is now implemented with read/write logic and tests."

You: "Great! It's complete."

# 5. Automatic archiving and Git commit
📦 Archiving change: implement-watchdog-load
💾 Committing changes to Git
✅ Change archived and committed to Git

Commit: ✅ Completed: implement watchdog load
        Change ID: implement-watchdog-load

You: "Now do WDOGVALUE"
AI: "Implementing WDOGVALUE register..."
    [Continues implementation]

# 6. Session is auto-saved, changes are archived, Git history is clean
```

## 🔍 Verify the Setup

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj

# Check proposals exist
ls -la openspec/changes/implement-*/

# Count proposals (should be 9)
ls -d openspec/changes/implement-* | wc -l

# View a proposal
cat openspec/changes/implement-watchdog-load/proposal.md

# Check scripts are executable
ls -l run_openspec_*.sh run_openspec_from_ddm.py

# Check Git repository
git status
git log --oneline
```

## 🎓 Understanding the Proposals

Each proposal contains:

### Register Information
- Name, address, width, access type
- Reset value
- Field definitions

### Implementation Guidance
- DML structure to create
- Read/write logic requirements
- Side effects to implement
- Logging and error handling

### Testing Requirements
- Test file location
- Coverage requirements
- Side effects to verify

### Example: WDOGLOAD Register

```
Name: WDOGLOAD
Address: 0x00
Width: 32-bit
Access: RW (Read/Write)
Reset: 0xFFFFFFFF

Implementation needed:
1. DML register definition
2. Read logic (return current value)
3. Write logic (update counter reload value)
4. Side effect: Reload counter when written
5. Tests: read/write, reset, side effects
```

## 💡 Pro Tips

### 1. Start with High-Priority Registers
Registers with side effects are marked as priority 1. Start with these:
- WDOGLOAD (counter reload)
- WDOGCONTROL (enable/disable)
- WDOGINTCLR (interrupt clear)

### 2. Use Session Saving
Always use `--save-session` flag so you can resume work:
```bash
~/wp5/ai_agents/adk-openspec/run_openspec.sh demo_wdog_openspec \
    "..." --model iflow/Qwen3-Coder --save-session
```

### 3. Test as You Go
After implementing each register:
```bash
# Build the model
make

# Run tests
cd modules/demo_watchdog/test
python3 test_wdogload.py

# Check Git history
git log --oneline
git show HEAD  # See last commit details
```

### 4. Validate Implementations
```bash
# Validate a specific change (if not archived yet)
openspec validate implement-watchdog-load

# Validate all active changes
openspec validate --all

# View archived changes
ls openspec/changes/archive/
```

### 5. Use Git for Tracking
```bash
# View commit history
git log --oneline --all

# See what was changed in each task
git log --stat

# Compare implementations
git diff HEAD~2 HEAD  # Compare last 2 commits

# Create a branch for experiments
git checkout -b experimental-feature
```

## 🆘 Common Issues

### Issue: "OpenSpec not found"
**Solution:** Activate the environment first
```bash
source ~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate
```

### Issue: "No proposals found"
**Solution:** Run the orchestrator to generate them
```bash
python3 run_openspec_from_ddm.py \
    --project . \
    --dml modules/demo_watchdog/demo_watchdog.dml \
    --spec wdt.md
```

### Issue: Agent doesn't understand context
**Solution:** Be more specific in your prompts
```
Bad:  "Implement the registers"
Good: "Implement the WDOGLOAD register according to the proposal in 
       openspec/changes/implement-watchdog-load/. Reference wdt.md 
       section 4.2.2 for the specification."
```

## 📚 More Information

- **Full User Guide**: `README_OPENSPEC_DDM.md`
- **Setup Summary**: `OPENSPEC_SETUP_SUMMARY.md`
- **Hardware Spec**: `wdt.md`
- **OpenSpec Docs**: https://github.com/fission-ai/openspec (or your OpenSpec location)

## 🎯 Your Next Step

**Choose one and run it now:**

```bash
# Easiest - Interactive helper
./run_openspec_interactive.sh

# OR Direct command
source ~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate
~/wp5/ai_agents/adk-openspec/run_openspec.sh demo_wdog_openspec \
    "Help me implement the watchdog registers" \
    --model iflow/Qwen3-Coder --save-session

# OR For other projects
python3 run_openspec_from_ddm.py --project /your/project --dml ... --spec ...
```

## ✅ Success Criteria

You'll know you're done when:
- [ ] All 9 registers implemented in `demo_watchdog.dml`
- [ ] All side effects working correctly
- [ ] Tests passing in `modules/demo_watchdog/test/`
- [ ] All changes archived in `openspec/changes/archive/`
- [ ] Clean Git history with one commit per register
- [ ] `openspec validate --all` passes (no active changes)
- [ ] `make test` completes successfully
- [ ] `git log` shows clear progression of implementation

---

**Ready?** Pick a method above and start implementing! 🚀

The system will automatically:
✅ Initialize Git repository  
✅ Archive completed changes  
✅ Commit each task to Git  
✅ Maintain clean history  

For detailed instructions, see `README_OPENSPEC_DDM.md`
