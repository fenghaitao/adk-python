# 🚀 OpenSpec DDM Orchestrator - Complete Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [What Was Built](#what-was-built)
3. [How It Works](#how-it-works)
4. [Running the Implementation](#running-the-implementation)
5. [Troubleshooting](#troubleshooting)
6. [Architecture](#architecture)

---

## Quick Start

### ⚡ Fastest Way to Start

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
./run_implementation_direct.sh
```

That's it! The script will guide you through implementing all 9 watchdog registers.

---

## What Was Built

### 1. Main Orchestrator (`run_openspec_from_ddm.py`)
**Purpose**: Automate the creation of OpenSpec change proposals from hardware specs

**What it does**:
- ✅ Parses hardware specification (wdt.md) - Chinese/English support
- ✅ Extracts 9 registers with addresses, widths, access types, fields
- ✅ Generates 19 implementation tasks (9 registers + 9 tests + 1 integration)
- ✅ Creates OpenSpec change proposals for each task
- ✅ Initializes Git repository with .gitignore
- ✅ Generates helper scripts

**Bugs Fixed**:
- ✅ Regex catastrophic backtracking (was hanging) → Fixed with line-by-line search
- ✅ Missing spec_file/dml_file attributes → Added to OpenSpecOrchestrator

**Run it**:
```bash
python3 run_openspec_from_ddm.py \
    --project . \
    --dml modules/demo_watchdog/demo_watchdog.dml \
    --spec wdt.md
```

### 2. Direct Implementation Runner (`run_implementation_direct.sh`) ⭐ NEW!
**Purpose**: Guide you through implementing each register step-by-step

**What it does**:
- Shows register details before implementation
- Displays proposal summary and task checklist
- Asks for confirmation before starting
- Launches ADK agent with OpenSpec integration
- Auto-archives completed changes
- Auto-commits to Git with descriptive messages
- Moves to next register

**Why use this**: Easiest way to implement all registers with full control

### 3. Interactive Runner (`run_openspec_interactive.sh`)
**Purpose**: Menu-driven interface for OpenSpec tasks

**Features**:
- Menu: Start fresh / Resume / Specific register / Exit
- Git integration (auto-init if needed)
- Archive and commit automation
- Session management

### 4. Automated Runner (`run_openspec_automated.sh`)
**Purpose**: Fully automated batch processing

**Features**:
- Processes all 9 registers in sequence
- Creates prompts for each register
- Runs OpenSpec agent for each
- Archives and commits automatically
- User confirmation after each task

### 5. OpenSpec Change Proposals (9 generated)
**Location**: `openspec/changes/implement-watchdog-*/`

Each proposal contains:
- `proposal.md` - Full specification, motivation, testing strategy
- `tasks.md` - Checklist of implementation tasks

**Registers**:
1. `implement-watchdog-load` - WDOGLOAD (0x00) - Load/reload value
2. `implement-watchdog-value` - WDOGVALUE (0x04) - Current value
3. `implement-watchdog-control` - WDOGCONTROL (0x08) - Control/enable
4. `implement-watchdog-interrupt-clear` - WDOGINTCLR (0x0C) - Clear interrupt
5. `implement-watchdog-raw-interrupt-status` - WDOGRIS (0x10) - Raw int status
6. `implement-watchdog-interrupt-status` - WDOGMIS (0x14) - Masked int status
7. `implement-watchdog-lock` - WDOGLOCK (0xC00) - Security lock
8. `implement-watchdog-integration-test-control` - WDOGITCR (0xF00) - Test mode
9. `implement-watchdog-integration-test-output-set` - WDOGITOP (0xF04) - Test output

---

## How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Hardware Spec (wdt.md)                                      │
│  - 9 watchdog registers in Chinese                          │
│  - Address, width, fields, side effects                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  run_openspec_from_ddm.py (Orchestrator)                    │
│                                                              │
│  1. HardwareSpecParser                                      │
│     - Parses markdown spec                                  │
│     - Extracts registers with regex                         │
│     - Handles Chinese/English                               │
│                                                              │
│  2. TaskGenerator                                           │
│     - Creates implementation tasks                          │
│     - Creates test tasks                                    │
│     - Builds dependency graph                               │
│                                                              │
│  3. OpenSpecOrchestrator                                    │
│     - Initializes OpenSpec project                          │
│     - Creates change proposals                              │
│     - Initializes Git repository                            │
│     - Generates helper scripts                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Generated Outputs                                          │
│                                                              │
│  ├── openspec/changes/implement-*/  (9 proposals)          │
│  │   ├── proposal.md                                       │
│  │   └── tasks.md                                          │
│  │                                                          │
│  ├── run_all_openspec_tasks.sh     (orchestration)        │
│  ├── openspec_tasks_summary.json   (task list)            │
│  └── .git/                          (version control)      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Implementation Phase (You choose method)                   │
│                                                              │
│  Option A: run_implementation_direct.sh  ⭐ RECOMMENDED     │
│  Option B: run_openspec_interactive.sh                      │
│  Option C: Manual with OpenSpec commands                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  ADK Agent + OpenSpec Integration                           │
│                                                              │
│  - Reads change proposal                                    │
│  - Reviews hardware spec                                    │
│  - Modifies demo_watchdog.dml                               │
│  - Creates tests                                            │
│  - Validates implementation                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  After Each Register                                        │
│                                                              │
│  1. openspec archive <change-id>                           │
│     - Moves proposal to archive/                            │
│     - Updates project state                                 │
│                                                              │
│  2. git commit -am "✅ Implemented WDOGLOAD"                │
│     - Commits all changes                                   │
│     - Clean history per register                            │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
wdt.md (Hardware Spec)
    │
    ├─> Register Name: "Watchdog Load"
    ├─> Address: 0x00
    ├─> Width: 32 bits
    ├─> Access: RW
    ├─> Reset Value: 0xFFFFFFFF
    ├─> Fields: wdog_load[31:0]
    └─> Side Effects: "递减计时器重载值"
         │
         ▼
openspec/changes/implement-watchdog-load/
    │
    ├─> proposal.md
    │    ├─ Overview
    │    ├─ Motivation
    │    ├─ Technical Specifications
    │    ├─ Implementation Details
    │    └─ Testing Strategy
    │
    └─> tasks.md
         ├─ [ ] Add WDOGLOAD register in DML
         ├─ [ ] Implement read method
         ├─ [ ] Implement write method
         ├─ [ ] Handle reset value
         ├─ [ ] Add logging
         └─ [ ] Create tests
              │
              ▼
modules/demo_watchdog/demo_watchdog.dml
    │
    ├─> bank watchdog {
    │       register WDOGLOAD size 4 @ 0x00 {
    │           field wdog_load [31:0];
    │       }
    │       method read_WDOGLOAD() -> (uint32) {
    │           return WDOGLOAD.val;
    │       }
    │       method write_WDOGLOAD(uint32 value) {
    │           WDOGLOAD.val = value;
    │           reload_counter();
    │       }
    │   }
    │
    └─> modules/demo_watchdog/test/test_wdogload.py
         ├─ test_read_initial_value()
         ├─ test_write_value()
         ├─ test_reload_side_effect()
         └─ test_reset_behavior()
```

---

## Running the Implementation

### Method 1: Direct Runner (⭐ RECOMMENDED)

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
./run_implementation_direct.sh
```

**What happens**:
1. Shows register 1/9: WDOGLOAD
2. Displays proposal summary
3. Shows task checklist
4. Asks: "Proceed with WDOGLOAD implementation? [Y/n]"
5. You press Y or Enter
6. Launches ADK agent with OpenSpec MCP server
7. Agent reads proposal and implements register
8. When done, asks: "Archive this change? [Y/n]"
9. You confirm, it archives and commits
10. Moves to register 2/9: WDOGVALUE
11. Repeats until all 9 done

**Interactive Session**:
```
╔════════════════════════════════════════
║ Register 1/9: WDOGLOAD
╚════════════════════════════════════════

📝 Change: implement-watchdog load
📂 Proposal: openspec/changes/implement-watchdog load/

Proposal Summary:
## Change: implement-watchdog load
- Register Name: Watchdog Load
- Address: 0x00
- Width: 32 bits
...

Tasks to Complete:
- [ ] Add WDOGLOAD register definition in DML bank
- [ ] Implement read_WDOGLOAD method
- [ ] Implement write_WDOGLOAD method
...

═══════════════════════════════════════
  Ready to implement WDOGLOAD
═══════════════════════════════════════

This will:
  1. Review: openspec/changes/implement-watchdog load/proposal.md
  2. Review: openspec/changes/implement-watchdog load/tasks.md
  3. Modify: modules/demo_watchdog/demo_watchdog.dml
  4. Create tests
  5. Validate implementation

Proceed with WDOGLOAD implementation? [Y/n]: y

🤖 Launching ADK agent with OpenSpec MCP server...

[ADK Agent starts...]
I'll help you implement the WDOGLOAD register...
[Agent implements the register...]
REGISTER IMPLEMENTATION COMPLETE

═══════════════════════════════════════
  WDOGLOAD Implementation Complete
═══════════════════════════════════════

Archive this change? [Y/n]: y

📦 Archiving implement-watchdog load...
💾 Committing to Git...
✅ WDOGLOAD archived and committed

[Moves to next register...]
```

### Method 2: Interactive Menu

```bash
./run_openspec_interactive.sh
```

**Menu Options**:
```
╔════════════════════════════════════════════════════════════╗
║   OpenSpec Agent Runner for Watchdog Implementation        ║
║   with Auto-Archive & Git Integration                      ║
╚════════════════════════════════════════════════════════════╝

Choose an option:
1) Start fresh implementation (all registers)
2) Resume from saved session
3) Implement specific register
4) Exit

Enter choice [1-4]: 1
```

### Method 3: Manual Control

```bash
# Activate OpenSpec venv
source /nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate

# List changes
openspec list changes

# View a specific change
openspec show implement-watchdog-load

# Implement in your editor (Cursor, VSCode, etc.)
cursor modules/demo_watchdog/demo_watchdog.dml

# After implementation
openspec archive implement-watchdog-load --message "Completed WDOGLOAD"

# Commit
git add .
git commit -m "✅ Implemented WDOGLOAD register"
```

---

## Troubleshooting

### Issue: Script hangs during parsing
**Status**: ✅ FIXED in latest version

**What was wrong**: Regex with `re.DOTALL` caused catastrophic backtracking

**How it was fixed**: Changed to simple line-by-line search

**Verify fix works**:
```bash
python3 test_regex.py  # Should complete in < 1 second, show 9 registers
```

### Issue: AttributeError: 'OpenSpecOrchestrator' object has no attribute 'spec_file'
**Status**: ✅ FIXED in latest version

**What was wrong**: Missing `spec_file` and `dml_file` in `__init__`

**How it was fixed**: Added parameters to OpenSpecOrchestrator.__init__()

**Verify fix works**:
```bash
python3 run_openspec_from_ddm.py --project . --dml modules/demo_watchdog/demo_watchdog.dml --spec wdt.md
# Should complete successfully
```

### Issue: "No module named agent_loop"
**Status**: ✅ FIXED in latest version

**What was wrong**: Direct runner tried to run `python -m agent_loop` which doesn't exist

**How it was fixed**: Changed to use `run_openspec.sh` wrapper which handles ADK setup

**Verify fix works**:
```bash
./run_implementation_direct.sh
# Should start ADK agent successfully
```

### Issue: OpenSpec commands not found
**Solution**: Activate the venv first

```bash
source /nfs/pdx/home/yongzhuo/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv/bin/activate
which openspec  # Should show: .../OpenSpec/python_port/.venv/bin/openspec
```

### Issue: Git not initialized
**Solution**: Already handled automatically, but if needed:

```bash
cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
git init
git add .
git commit -m "Initial commit"
```

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│  User Interface Layer                                    │
├─────────────────────────────────────────────────────────┤
│  • run_implementation_direct.sh (guided)                │
│  • run_openspec_interactive.sh (menu)                   │
│  • Manual commands (full control)                       │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  Orchestration Layer                                     │
├─────────────────────────────────────────────────────────┤
│  • run_openspec_from_ddm.py                             │
│    ├─ HardwareSpecParser                                │
│    ├─ TaskGenerator                                     │
│    └─ OpenSpecOrchestrator                              │
│  • run_openspec.sh (ADK wrapper)                        │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  OpenSpec Layer                                          │
├─────────────────────────────────────────────────────────┤
│  • Change proposals (proposal.md, tasks.md)             │
│  • Project config (openspec/project.md)                 │
│  • Archive management                                   │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  ADK Agent Layer                                         │
├─────────────────────────────────────────────────────────┤
│  • adk run adk_openspec_agent                           │
│  • MCP server integration (port 8051)                   │
│  • Session management                                   │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  Implementation Layer                                    │
├─────────────────────────────────────────────────────────┤
│  • DML file modifications                               │
│  • Test creation                                        │
│  • Validation                                           │
└────────────┬───────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  Version Control Layer                                   │
├─────────────────────────────────────────────────────────┤
│  • Git repository                                        │
│  • Commits per register                                 │
│  • Change history                                       │
└─────────────────────────────────────────────────────────┘
```

### File Organization

```
demo_wdog_proj/
├── run_openspec_from_ddm.py          # Main orchestrator
├── run_implementation_direct.sh       # Direct runner ⭐
├── run_openspec_interactive.sh        # Interactive menu
├── run_openspec_automated.sh          # Batch automation
├── run_all_openspec_tasks.sh          # Generated script
├── openspec_tasks_summary.json        # Task list
├── wdt.md                              # Hardware spec
│
├── openspec/
│   ├── project.md                     # Project overview
│   ├── AGENTS.md                      # Agent instructions
│   ├── changes/
│   │   ├── implement-watchdog-load/
│   │   │   ├── proposal.md
│   │   │   └── tasks.md
│   │   ├── implement-watchdog-value/
│   │   └── ... (7 more)
│   └── specs/
│
├── modules/
│   └── demo_watchdog/
│       ├── demo_watchdog.dml          # DML to modify
│       └── test/                      # Tests to create
│
├── documentation/
│   ├── START_HERE.md                  # Quick start
│   ├── IMPLEMENTATION_READY.md        # Complete guide
│   ├── QUICK_START.md                 # 5-min guide
│   ├── README_OPENSPEC_DDM.md         # Full manual
│   ├── GIT_AND_ARCHIVING_GUIDE.md     # Git features
│   └── FEATURES_UPDATE.md             # What's new
│
└── .git/                               # Version control
```

---

## Next Steps

1. **Read this guide** - You're doing it! ✅
2. **Run the implementation**:
   ```bash
   cd /nfs/site/disks/ssm_yongzhuo_001/ai_agents/tests/adk-mcp-rag/q3_openspec/demo_wdog_proj
   ./run_implementation_direct.sh
   ```
3. **Follow the prompts** - The script guides you through everything
4. **Review implementations** - Check the DML code and tests
5. **Build and test**:
   ```bash
   make
   make test
   ```

**You're all set! Happy coding! 🚀**
