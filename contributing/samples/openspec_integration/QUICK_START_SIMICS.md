# Quick Start: Simics Hardware Device Modeling with OpenSpec

This guide shows you how to use OpenSpec for hardware device modeling with Simics.

## Prerequisites

1. **Simics 7.x** installed and in PATH
2. **DML 1.4** support (included with Simics 7.x)
3. **Simics MCP Server** available
4. **ADK** installed in virtual environment

## Setup (One-Time)

### 1. Start Simics MCP Server

```bash
# In a separate terminal, start the server
cd path/to/simics-mcp-server
python src/simics_mcp_server/server.py --transport sse --port 8051

# You should see:
# Server running on http://127.0.0.1:8051
```

Keep this terminal running while you work.

### 2. Verify Integration

```bash
# Run verification script
.venv/bin/python contributing/samples/openspec_integration/verify_simics_integration.py

# You should see:
# ✓ Simics MCP tools loaded successfully (includes RAG documentation search)
# ✓ All expected Simics tools available
```

## Create Your First Hardware Device

### Step 1: Initialize Project

```bash
./run_openspec.sh my_watchdog_timer
```

You should see:
```
✓ Simics MCP tools loaded successfully (includes RAG documentation search)
```

### Step 2: Create Change Proposal

In the agent chat:
```
You: I want to create an ARM watchdog timer device model with the following features:
     - 32-bit control register at offset 0x00 (enable/disable)
     - 32-bit load register at offset 0x04 (timeout value)
     - 32-bit value register at offset 0x08 (current count, read-only)
     - Interrupt generation on first timeout
     - System reset on second timeout
     
     Please create an OpenSpec change proposal for this Simics device.

Agent: I'll create an OpenSpec change proposal for the watchdog timer device.
       *Detects hardware keywords: "watchdog timer", "device model"*
       *Creates openspec/changes/add-watchdog-timer/ with:*
       - proposal.md: Feature description
       - specs/watchdog-timer/spec.md: Hardware requirements with register map
       - design.md: DML implementation approach
       - tasks.md: Implementation tasks using Simics MCP tools
```

### Step 3: Review Specifications

```
You: Show me the spec delta for the watchdog timer

Agent: *Displays the spec delta with register map and behavioral requirements*
```

The spec will include:
- Register map with offsets and bit definitions
- Behavioral requirements (WHEN/THEN scenarios)
- Interface definitions
- Test scenarios

### Step 4: Implement Using Simics Tools

```
You: The specs look good. Let's implement this change.

Agent: I'll work through the tasks:
       
       Task 1.1: Verify Simics installation
       *Uses: get_simics_version()*
       ✓ Simics 7.0 detected
       
       Task 1.2: Create project structure
       *Uses: create_simics_project(project_name="watchdog-timer", project_path=".")*
       ✓ Project created with modules/ directory
       
       Task 1.3: Add device skeleton
       *Uses: add_dml_device_skeleton(project_path=".", device_name="watchdog-timer")*
       ✓ DML skeleton created
       
       Task 2.1: Write register tests
       *Creates: modules/watchdog-timer/test/test_registers.py*
       ✓ Tests written
       
       Task 3.1: Implement registers
       *Creates: modules/watchdog-timer/registers.dml*
       ✓ Registers implemented
       
       Task 3.2: Implement device logic
       *Creates: modules/watchdog-timer/watchdog-timer.dml*
       ✓ Device logic implemented
       
       Task 3.3: Build device
       *Uses: build_simics_project(project_path=".", module="watchdog-timer")*
       ✓ Build successful
       
       Task 4.1: Run tests
       *Uses: run_simics_test(project_path=".", suite="all")*
       ✓ All tests passed
```

### Step 5: Use RAG Documentation Search

During implementation, you can search Simics documentation:

```
You: How do I define a register with read/write callbacks in DML 1.4?

Agent: Let me search the DML documentation.
       *Uses: perform_rag_query("register read write callbacks", source_type="dml")*
       
       In DML 1.4, you define registers with callbacks like this:
       
       register control_reg size 4 @ 0x00 {
           method read() -> (uint64) {
               return this.val;
           }
           
           method write(uint64 value) {
               this.val = value;
               // Trigger side effects
               if (value & 0x1) {
                   start_watchdog();
               }
           }
       }
```

### Step 6: Archive Completed Device

```
You: The watchdog timer is complete and tested. Please archive the change.

Agent: *Runs: openspec archive add-watchdog-timer --yes*
       ✓ Device implementation archived
       ✓ Specs updated in openspec/specs/watchdog-timer/
       ✓ Ready for the next hardware device!
```

## Project Structure

After implementation, your project will look like:

```
my_watchdog_timer/
├── AGENTS.md
├── openspec/
│   ├── project.md
│   ├── specs/
│   │   └── watchdog-timer/
│   │       └── spec.md                    # Archived specification
│   └── changes/
│       └── archive/
│           └── add-watchdog-timer/        # Archived change
├── modules/
│   └── watchdog-timer/
│       ├── watchdog-timer.dml             # Main device
│       ├── registers.dml                  # Register definitions
│       ├── interfaces.dml                 # External interfaces
│       ├── utility.dml                    # Utilities
│       └── test/
│           ├── test_registers.py          # Register tests
│           ├── test_interfaces.py         # Interface tests
│           └── s-watchdog-timer.py        # Main test script
└── Makefile                               # Simics build config
```

## Available Simics Tools

The agent has access to these Simics MCP tools:

**Project Management:**
- `get_simics_version()` - Verify Simics installation
- `create_simics_project(project_name, project_path)` - Create project
- `add_dml_device_skeleton(project_path, device_name)` - Add device template

**Build & Test:**
- `build_simics_project(project_path, module)` - Build device module
- `run_simics_test(project_path, suite)` - Run test suites

**Documentation Search:**
- `perform_rag_query(query, source_type, match_count)` - Search docs
  - `source_type="dml"` - DML 1.4 documentation
  - `source_type="python"` - Simics Python API
  - `source_type="docs"` - General Simics docs
  - `source_type="all"` - Search everything

**Package Management:**
- `list_installed_packages()` - List installed packages
- `search_packages(query)` - Search available packages

## Tips

1. **Always start with specs**: Define register map and behavior before coding
2. **Use RAG search**: Search DML docs when you need syntax examples
3. **Test-driven development**: Write tests before implementing device logic
4. **Validate frequently**: Build and test after each major change
5. **Archive when done**: Keep your changes organized

## Troubleshooting

**Issue**: "Simics MCP tools not available"
- **Solution**: Start the Simics MCP server on port 8051

**Issue**: Build fails with DML syntax errors
- **Solution**: Use `perform_rag_query(source_type="dml")` to search for correct syntax

**Issue**: Tests fail
- **Solution**: Check register read/write operations match specification

**Issue**: "Simics 7.x required"
- **Solution**: Upgrade Simics installation (DML 1.2 is not supported)

## Next Steps

- Read the full documentation in `README.md`
- Check out example workflows in `IMPLEMENTATION_COMPLETE.md`
- Explore the Simics MCP server capabilities
- Create your own hardware device models!

## Resources

- [OpenSpec Documentation](https://github.com/Fission-AI/OpenSpec)
- [Simics Documentation](https://www.intel.com/content/www/us/en/developer/articles/tool/simics-simulator.html)
- [DML 1.4 Reference](https://software.intel.com/content/www/us/en/develop/documentation/simics-reference-manual/)
