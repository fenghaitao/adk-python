#!/usr/bin/env python3
"""
OpenSpec DDM Project Orchestrator

This script orchestrates OpenSpec agents to implement Simics DDM (Data-Driven Modeling)
device models by:
1. Parsing hardware specifications to identify registers and side effects
2. Creating OpenSpec change proposals for register implementations
3. Generating Python test stubs for verification
4. Submitting tasks to OpenSpec agents for implementation

Usage:
    python run_openspec_from_ddm.py \\
        --project /path/to/ddm_project \\
        --dml modules/device/device.dml \\
        --spec path/to/hardware_spec.md \\
        [--model iflow/Qwen3-Coder] \\
        [--port 8051] \\
        [--max-tasks 10]

Requirements:
    - OpenSpec framework installed and configured
    - ADK virtual environment set up
    - Bash shell (for OpenSpec venv activation)
"""

import argparse
import json
import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Register:
    """Represents a hardware register with its properties."""
    name: str
    address: str
    width: int
    access: str  # R, W, RW
    reset_value: str
    description: str
    fields: List[Dict[str, str]]  # List of {bit_range, name, access, reset, description}
    side_effects: List[str]  # List of side effect descriptions


@dataclass
class Task:
    """Represents a task to be implemented by OpenSpec agents."""
    task_id: str
    title: str
    description: str
    register: Optional[Register]
    task_type: str  # 'register_impl', 'test_impl', 'integration'
    dependencies: List[str]  # List of task_ids this depends on
    files_to_modify: List[str]
    priority: int  # 1=high, 2=medium, 3=low


class HardwareSpecParser:
    """Parse hardware specifications to extract register information."""
    
    def __init__(self, spec_path: str):
        self.spec_path = Path(spec_path)
        self.content = self._load_spec()
        
    def _load_spec(self) -> str:
        """Load the specification file."""
        with open(self.spec_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def parse_registers(self) -> List[Register]:
        """Parse all registers from the specification."""
        registers = []
        
        # Pattern to find register sections (adjust based on your spec format)
        # Supports both markdown headers and bold text with register sections
        # Pattern 1: **Watchdog Load register [0x00]**
        # Pattern 2: ## RegisterName register [0xAddress]
        # Captures multi-word register names like "Watchdog Integration Test Control"
        register_pattern = r'(?:\*\*|#{2,4}\s*)([A-Z][\w\s]+?)\s+register\s+\[0x([0-9A-Fa-f]+)\]'
        
        matches = list(re.finditer(register_pattern, self.content, re.IGNORECASE))
        
        for i, match in enumerate(matches):
            reg_name = match.group(1)
            reg_address = f"0x{match.group(2)}"
            
            # Extract the section content (from this match to the next or end)
            start_pos = match.end()
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(self.content)
            
            section_content = self.content[start_pos:end_pos]
            
            # Extract register properties
            register = self._parse_register_section(reg_name, reg_address, section_content)
            if register:
                registers.append(register)
        
        return registers
    
    def _parse_register_section(self, name: str, address: str, content: str) -> Optional[Register]:
        """Parse a single register section."""
        # Extract basic properties
        width = self._extract_width(content)
        access = self._extract_access_type(content)
        reset_value = self._extract_reset_value(content)
        description = self._extract_description(content)
        fields = self._extract_fields(content)
        side_effects = self._extract_side_effects(content, name)
        
        return Register(
            name=name,
            address=address,
            width=width,
            access=access,
            reset_value=reset_value,
            description=description,
            fields=fields,
            side_effects=side_effects
        )
    
    def _extract_width(self, content: str) -> int:
        """Extract register width from content."""
        # Look for patterns like "位宽：32位" or "Width: 32"
        pattern = r'(?:位\s*宽|width)\s*[:：]\s*(\d+)'
        match = re.search(pattern, content, re.IGNORECASE)
        return int(match.group(1)) if match else 32
    
    def _extract_access_type(self, content: str) -> str:
        """Extract access type (R/W/RW)."""
        pattern = r'(?:类\s*型|type)\s*[:：]\s*(读写|只读|只写|R/W|R|W|RW)'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            access_str = match.group(1).upper()
            if '读写' in access_str or 'R/W' in access_str or access_str == 'RW':
                return 'RW'
            elif '只读' in access_str or access_str == 'R':
                return 'R'
            elif '只写' in access_str or access_str == 'W':
                return 'W'
        return 'RW'
    
    def _extract_reset_value(self, content: str) -> str:
        """Extract reset value."""
        pattern = r'(?:复位时值|reset)\s*[:：]\s*(0x[0-9A-Fa-f]+|[0-9]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1) if match else '0x0'
    
    def _extract_description(self, content: str) -> str:
        """Extract register description."""
        # Get first paragraph or sentence after the header
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('|'):
                return line[:200]  # First 200 chars
        return ""
    
    def _extract_fields(self, content: str) -> List[Dict[str, str]]:
        """Extract register fields from table."""
        fields = []
        # Look for markdown tables with field information
        table_pattern = r'\|.*?\|.*?\|.*?\|.*?\|'
        table_matches = re.findall(table_pattern, content)
        
        for row in table_matches:
            # Skip header and separator rows
            if '---' in row or 'Bit' in row or 'Name' in row:
                continue
            
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if len(cells) >= 4:
                fields.append({
                    'bit_range': cells[0],
                    'name': cells[1],
                    'access': cells[2] if len(cells) > 2 else '',
                    'description': cells[3] if len(cells) > 3 else ''
                })
        
        return fields
    
    def _extract_side_effects(self, content: str, reg_name: str) -> List[str]:
        """Extract side effects from register description."""
        side_effects = []
        
        # Common side effect keywords
        effect_keywords = [
            'interrupt', '中断', 'reset', '复位', 'reload', '重载',
            'clear', '清除', 'trigger', '触发', 'enable', '使能',
            'disable', '禁用', 'counter', '计数', 'timer', '定时'
        ]
        
        # Search for side effect descriptions line by line (avoid catastrophic backtracking)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for keyword in effect_keywords:
                if keyword.lower() in line.lower():
                    # Found a line with a keyword, add it
                    clean_match = line[:200]  # Limit length
                    if clean_match and clean_match not in side_effects:
                        side_effects.append(clean_match)
                        break  # One effect per line
        
        return side_effects[:5]  # Limit to 5 most relevant


class TaskGenerator:
    """Generate tasks for OpenSpec agents."""
    
    def __init__(self, project_path: str, dml_file: str, spec_file: str):
        self.project_path = Path(project_path)
        self.dml_file = dml_file
        self.spec_file = spec_file
        self.tasks: List[Task] = []
        
    def generate_tasks(self, registers: List[Register]) -> List[Task]:
        """Generate tasks from parsed registers."""
        self.tasks = []
        task_counter = 1
        
        # Generate register implementation tasks
        for reg in registers:
            # Task 1: Implement register read/write logic
            impl_task = Task(
                task_id=f"task-{task_counter:03d}",
                title=f"Implement {reg.name} register logic",
                description=self._create_register_impl_description(reg),
                register=reg,
                task_type='register_impl',
                dependencies=[],
                files_to_modify=[self.dml_file],
                priority=1 if reg.side_effects else 2
            )
            self.tasks.append(impl_task)
            task_counter += 1
            
            # Task 2: Create tests for this register
            test_task = Task(
                task_id=f"task-{task_counter:03d}",
                title=f"Create tests for {reg.name} register",
                description=self._create_test_description(reg),
                register=reg,
                task_type='test_impl',
                dependencies=[impl_task.task_id],
                files_to_modify=[f"modules/{Path(self.dml_file).parent.name}/test/test_{reg.name.lower()}.py"],
                priority=2
            )
            self.tasks.append(test_task)
            task_counter += 1
        
        # Generate integration task
        if self.tasks:
            integration_task = Task(
                task_id=f"task-{task_counter:03d}",
                title="Integration testing and verification",
                description="Run all tests and verify the complete watchdog implementation",
                register=None,
                task_type='integration',
                dependencies=[t.task_id for t in self.tasks if t.task_type == 'test_impl'],
                files_to_modify=["modules/*/test/*.py"],
                priority=3
            )
            self.tasks.append(integration_task)
        
        return self.tasks
    
    def _create_register_impl_description(self, reg: Register) -> str:
        """Create detailed description for register implementation task."""
        desc = f"""Implement the {reg.name} register in the DML device model.

**Register Specifications:**
- Name: {reg.name}
- Address: {reg.address}
- Width: {reg.width} bits
- Access: {reg.access}
- Reset Value: {reg.reset_value}
- Description: {reg.description}

**Fields:**
"""
        for field in reg.fields:
            desc += f"- Bits {field['bit_range']}: {field['name']} - {field.get('description', '')}\n"
        
        if reg.side_effects:
            desc += f"\n**Side Effects to Implement:**\n"
            for i, effect in enumerate(reg.side_effects, 1):
                desc += f"{i}. {effect}\n"
        
        desc += f"""
**Implementation Requirements:**
1. Add register field in the DML bank structure
2. Implement read logic following the access type ({reg.access})
3. Implement write logic with proper side effects
4. Handle reset behavior (reset to {reg.reset_value})
5. Add logging for debugging
6. Follow DML 1.4 best practices

**Reference:**
- Hardware spec: {self.spec_file}
- DML file: {self.dml_file}
"""
        return desc
    
    def _create_test_description(self, reg: Register) -> str:
        """Create detailed description for test implementation task."""
        desc = f"""Create comprehensive Python tests for the {reg.name} register.

**Test Coverage Requirements:**
1. Test basic read/write operations
2. Test reset behavior (should reset to {reg.reset_value})
3. Test access restrictions ({reg.access})
4. Test all register fields individually
"""
        if reg.side_effects:
            desc += "5. Test side effects:\n"
            for i, effect in enumerate(reg.side_effects, 1):
                desc += f"   - {effect}\n"
        
        desc += f"""
**Test Template:**
Create a new file: `modules/{Path(self.dml_file).parent.name}/test/test_{reg.name.lower()}.py`

The test should:
- Use Python Simics API to interact with the device model
- Follow the existing test patterns in the test directory
- Include both positive and negative test cases
- Verify expected behavior and side effects
- Use proper assertions and error messages

**Reference:**
- Hardware spec: {self.spec_file}
- Existing tests in: modules/{Path(self.dml_file).parent.name}/test/
"""
        return desc


class OpenSpecOrchestrator:
    """Orchestrate OpenSpec agents to implement tasks."""
    
    def __init__(self, project_path: str, model: str = "iflow/Qwen3-Coder", 
                 port: int = 8051, openspec_venv: str = None, 
                 dml_file: str = None, spec_file: str = None):
        self.project_path = Path(project_path)
        self.model = model
        self.port = port
        self.dml_file = dml_file
        self.spec_file = spec_file
        self.openspec_venv = openspec_venv or os.path.expanduser(
            "~/wp5/ai_agents/adk-openspec/OpenSpec/python_port/.venv"
        )
    
    def initialize_git_repo(self) -> bool:
        """Initialize Git repository if it doesn't exist."""
        git_dir = self.project_path / ".git"
        
        if git_dir.exists():
            print(f"✅ Git repository already exists")
            return True
        
        try:
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=self.project_path,
                check=True,
                capture_output=True
            )
            
            # Create .gitignore if it doesn't exist
            gitignore_path = self.project_path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# Build artifacts
*.o
*.so
*.pyc
__pycache__/
.venv/
*.egg-info/

# IDE
.vscode/
.idea/

# Simics specific
linux64/
*.d

# Temporary files
*.log
*.tmp
"""
                gitignore_path.write_text(gitignore_content)
            
            # Initial commit
            subprocess.run(
                ["git", "add", "."],
                cwd=self.project_path,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit - OpenSpec DDM project setup"],
                cwd=self.project_path,
                check=True,
                capture_output=True
            )
            
            print(f"✅ Git repository initialized with initial commit")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to initialize Git repository: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Error during Git initialization: {e}")
            return False
        
    def initialize_openspec_project(self) -> bool:
        """Initialize OpenSpec framework in the project."""
        # Check if openspec directory already exists
        openspec_dir = self.project_path / "openspec"
        if not openspec_dir.exists():
            print(f"⚠️  OpenSpec directory not found at {openspec_dir}")
            print("Please run the initialization manually or ensure the project is set up correctly.")
            return False
        
        print(f"✅ Found OpenSpec directory: {openspec_dir}")
        return True
    
    def create_change_proposals(self, tasks: List[Task]) -> Dict[str, str]:
        """Create OpenSpec change proposals for tasks."""
        proposals = {}
        
        for task in tasks:
            if task.task_type == 'integration':
                continue  # Skip integration task for proposals
            
            change_id = self._generate_change_id(task)
            proposal_dir = self.project_path / "openspec" / "changes" / change_id
            proposal_dir.mkdir(parents=True, exist_ok=True)
            
            # Create proposal.md
            proposal_path = proposal_dir / "proposal.md"
            proposal_content = self._generate_proposal_content(task, change_id)
            proposal_path.write_text(proposal_content)
            
            # Create tasks.md
            tasks_path = proposal_dir / "tasks.md"
            tasks_content = self._generate_tasks_content(task)
            tasks_path.write_text(tasks_content)
            
            proposals[task.task_id] = change_id
            print(f"✅ Created proposal: {change_id}")
        
        return proposals
    
    def _generate_change_id(self, task: Task) -> str:
        """Generate a change ID from task."""
        if task.register:
            return f"implement-{task.register.name.lower().replace('_', '-')}"
        else:
            return task.task_id.replace('_', '-')
    
    def _generate_proposal_content(self, task: Task, change_id: str) -> str:
        """Generate proposal.md content."""
        return f"""# {task.title}

**Change ID:** `{change_id}`  
**Status:** Draft  
**Priority:** {task.priority}

## Summary

{task.description.split('**')[0].strip()}

## Motivation

This change implements the {task.register.name if task.register else 'required'} functionality 
as specified in the hardware specification document.

## Detailed Description

{task.description}

## Dependencies

{', '.join([f'`{dep}`' for dep in task.dependencies]) if task.dependencies else 'None'}

## Files to Modify

{chr(10).join([f'- `{f}`' for f in task.files_to_modify])}

## Testing Strategy

{self._get_testing_strategy(task)}

## Risks and Mitigations

- **Risk:** Incorrect register behavior implementation
  - **Mitigation:** Comprehensive unit tests and reference to hardware spec
  
- **Risk:** Side effects not properly handled
  - **Mitigation:** Test all documented side effects individually

## Timeline

- Implementation: 1-2 hours
- Testing: 1 hour
- Review: 30 minutes
"""
    
    def _generate_tasks_content(self, task: Task) -> str:
        """Generate tasks.md content."""
        return f"""# Tasks for {task.title}

## Implementation Tasks

- [ ] Read and understand hardware specification
- [ ] Implement register structure in DML
- [ ] Implement read logic
- [ ] Implement write logic
- [ ] Implement side effects
- [ ] Add logging and error handling
- [ ] Review code quality

## Testing Tasks

- [ ] Create test file
- [ ] Implement basic read/write tests
- [ ] Implement reset tests
- [ ] Implement side effect tests
- [ ] Run and verify all tests pass
- [ ] Document test coverage

## Documentation Tasks

- [ ] Update code comments
- [ ] Update README if needed
- [ ] Document any deviations from spec
"""
    
    def _get_testing_strategy(self, task: Task) -> str:
        """Get testing strategy based on task type."""
        if task.task_type == 'register_impl':
            return """Unit tests will verify:
1. Correct register read/write behavior
2. Reset value is correctly set
3. Access restrictions are enforced
4. Side effects are triggered correctly
5. Edge cases are handled
"""
        elif task.task_type == 'test_impl':
            return """Integration tests will verify:
1. All register operations work in sequence
2. Side effects interact correctly
3. System behavior matches specification
"""
        else:
            return "Standard testing approach"
    
    def create_orchestration_script(self, tasks: List[Task], proposals: Dict[str, str]) -> str:
        """Create a script to run ADK agents for each task with archiving and Git commits."""
        script_path = self.project_path / "run_all_openspec_tasks.sh"
        
        # Get the ADK directory path
        adk_dir = os.path.expanduser("~/wp5/ai_agents/adk-openspec")
        openspec_integration_dir = f"{adk_dir}/contributing/samples/openspec_integration"
        
        script_content = f"""#!/bin/bash
# Generated OpenSpec Orchestration Script with ADK Agent
# This script runs ADK agents for each task with:
# - ADK agent execution per task
# - Automatic archiving after completion
# - Git commits after each task

set -e

# Colors
GREEN='\\033[0;32m'
BLUE='\\033[0;34m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

# Configuration
MODEL="{self.model}"
PORT={self.port}
OPENSPEC_VENV="{self.openspec_venv}"
ADK_VENV="{adk_dir}/.venv"
PROJECT_DIR="{self.project_path}"
OPENSPEC_INTEGRATION_DIR="{openspec_integration_dir}"

echo -e "${{BLUE}}🚀 Starting OpenSpec DDM Orchestration with ADK Agents${{NC}}"
echo "Model: $MODEL"
echo "Port: $PORT"
echo "Project: $PROJECT_DIR"
echo "ADK venv: $ADK_VENV"
echo ""

# Check ADK venv exists
if [ ! -d "$ADK_VENV" ]; then
    echo -e "${{RED}}❌ Error: ADK virtual environment not found at $ADK_VENV${{NC}}"
    exit 1
fi

# Check OpenSpec integration exists
if [ ! -d "$OPENSPEC_INTEGRATION_DIR" ]; then
    echo -e "${{RED}}❌ Error: OpenSpec integration not found at $OPENSPEC_INTEGRATION_DIR${{NC}}"
    exit 1
fi

# Create agent directory for ADK if it doesn't exist
mkdir -p adk_openspec_agent

# Function to create agent.py for ADK
create_adk_agent() {{
    cat > adk_openspec_agent/agent.py << 'AGENT_EOF'
import sys
sys.path.insert(0, '{openspec_integration_dir}')
sys.path.insert(0, '{adk_dir}/contributing/samples')

# Import the root_agent from the openspec_integration package
import importlib.util
spec = importlib.util.spec_from_file_location(
    "openspec_agent_module",
    "{openspec_integration_dir}/agent.py"
)
openspec_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openspec_agent_module)
root_agent = openspec_agent_module.root_agent
AGENT_EOF
}}

# Function to archive change and commit to git
archive_and_commit() {{
    local change_id=$1
    local task_title=$2
    
    echo -e "${{YELLOW}}📦 Archiving change: $change_id${{NC}}"
    
    # Activate OpenSpec venv for archive command
    source "$OPENSPEC_VENV/bin/activate"
    
    # Archive with openspec (this moves proposal to archive and updates specs)
    openspec archive "$change_id" --yes || true
    
    deactivate
    
    echo -e "${{YELLOW}}💾 Committing changes to Git${{NC}}"
    
    # Git commit all changes
    cd "$PROJECT_DIR"
    git add .
    git commit -m "✅ Completed: $task_title

Change ID: $change_id
Task completed and archived by OpenSpec orchestrator.
" || echo "No changes to commit"
    
    echo -e "${{GREEN}}✅ Change archived and committed${{NC}}"
    echo ""
}}

# Export environment variables for ADK agent
export OPENSPEC_MODEL="$MODEL"
export MCP_PORT="$PORT"

# Create the ADK agent
echo -e "${{BLUE}}📝 Creating ADK agent for OpenSpec integration...${{NC}}"
create_adk_agent
echo -e "${{GREEN}}✅ ADK agent created${{NC}}"
echo ""

"""
        
        # Add commands for each task
        for task in tasks:
            if task.task_id in proposals:
                change_id = proposals[task.task_id]
                
                script_content += f"""
echo -e "${{BLUE}}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${{NC}}"
echo -e "${{BLUE}}📋 Task {task.task_id}: {task.title}${{NC}}"
echo -e "${{BLUE}}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${{NC}}"
echo "Change ID: {change_id}"
echo "Type: {task.task_type}"
echo "Priority: {task.priority}"
echo ""

# Prepare the prompt for ADK agent
TASK_PROMPT="You are a Simics DML implementation agent. Complete ALL deliverables for this task.

WORKING DIRECTORY: {self.project_path}
All file paths are relative to this directory.

REFERENCE DOCUMENTS (you can read these for details):
- Hardware Spec: {self.spec_file}
- Change Proposal: openspec/changes/{change_id}/proposal.md
- Task Details: openspec/changes/{change_id}/tasks.md
- DML File: {self.dml_file}

═══════════════════════════════════════════════════════════
TASK: {task.title}
TYPE: {task.task_type}
CHANGE ID: {change_id}
═══════════════════════════════════════════════════════════

READ the change proposal and task details for complete requirements.
The proposal at openspec/changes/{change_id}/proposal.md contains all specifications.

═══════════════════════════════════════════════════════════
DELIVERABLE 1: IMPLEMENT DML CODE
═══════════════════════════════════════════════════════════

FILE TO EDIT: {self.dml_file}
WHERE: In the bank section where registers are defined
PATTERN: Follow existing register patterns in the file

Required method signature for write:
    method write_register(uint64 value, uint64 enabled_bytes, void *aux) {{
        log info, 1: \\\">>> REGNAME write_register() CALLED with value=0x%x\\\", value;
        default(value, enabled_bytes, aux);
        log info, 1: \\\">>> REGNAME updated, value=0x%x\\\", this.val;
    }}

Required method signature for read:
    method read_register(uint64 enabled_bytes, void *aux) -> (uint64) {{
        log info, 1: \\\">>> REGNAME read_register() CALLED\\\";
        return this.val;
    }}

✓ DELIVERABLE 1 COMPLETE WHEN: {self.dml_file} contains the register implementation

═══════════════════════════════════════════════════════════
DELIVERABLE 2: CREATE TEST FILE
═══════════════════════════════════════════════════════════

FILE TO CREATE: Test file for this register in modules/demo_watchdog/test/

REQUIRED TEST CONTENT (adjust register name and address):
    import simics
    
    def test_register_basic():
        '''Test basic register operations'''
        obj = simics.SIM_get_object('demo_watchdog')
        # Test write and read operations
        # Add your test logic here based on the register spec
        print(\\\"✓ Test PASSED\\\")
    
    if __name__ == '__main__':
        test_register_basic()
        print(\\\"\\\\n✓✓✓ ALL TESTS PASSED ✓✓✓\\\")

✓ DELIVERABLE 2 COMPLETE WHEN: Test file created with actual test cases

═══════════════════════════════════════════════════════════
DELIVERABLE 3: COMPILE AND VERIFY
═══════════════════════════════════════════════════════════

STEPS:
1. Compile: Run 'make' in project root to build DML code
2. Check compilation output for errors
3. Fix any compilation errors if they occur
4. Verify the build succeeds

✓ DELIVERABLE 3 COMPLETE WHEN: Code compiles successfully without errors

═══════════════════════════════════════════════════════════
COMPLETION SIGNAL
═══════════════════════════════════════════════════════════

When ALL THREE deliverables are complete, respond EXACTLY with:

IMPLEMENTATION COMPLETE - {task.title}

DO NOT respond with this message until:
✓ DML code implemented and edited
✓ Test file created
✓ Code compiles successfully
═══════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════

✗ DO NOT just read files without taking action
✗ DO NOT skip any deliverable
✗ DO NOT ask for more information - you have everything you need
✓ DO read the reference documents if you need details
✓ DO edit files using your file editing tools
✓ DO compile the code after editing DML
✓ DO create complete, working test code
✓ START NOW by reading {self.dml_file} to understand the current code

REFERENCE FILES AVAILABLE:
- Hardware Spec: {self.spec_file}
- DML Implementation: {self.dml_file}  
- Change Proposal: openspec/changes/{change_id}/proposal.md
- Task Details: openspec/changes/{change_id}/tasks.md

BEGIN WITH DELIVERABLE 1 NOW!"

# Run the ADK agent for this task
echo -e "${{YELLOW}}🤖 Running ADK agent for task {task.task_id}...${{NC}}"

# Build ADK command with session management
ADK_CMD="$ADK_VENV/bin/adk run adk_openspec_agent"
ADK_CMD="$ADK_CMD --save_session --session_id task_{task.task_id}_openspec"

# Execute ADK agent
cd "$PROJECT_DIR"
echo "$TASK_PROMPT" | $ADK_CMD

echo -e "${{GREEN}}✅ Task {task.task_id} completed${{NC}}"
echo ""

# Archive and commit
archive_and_commit "{change_id}" "{task.title}"

"""
        
        script_content += f"""
echo -e "${{BLUE}}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${{NC}}"
echo -e "${{GREEN}}🎉 All {len(tasks)} tasks completed!${{NC}}"
echo -e "${{BLUE}}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${{NC}}"
echo ""
echo "Next steps:"
echo "1. Review the Git commit history: git log --oneline"
echo "2. Check the DML implementation: {self.dml_file}"
echo "3. Build and test the module: make -C modules/demo_watchdog"
echo "4. Run integration tests if available"
echo ""
"""
        
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        return str(script_path)
    
    def generate_task_summary(self, tasks: List[Task], output_path: str):
        """Generate a JSON summary of all tasks."""
        summary = {
            'project': str(self.project_path),
            'total_tasks': len(tasks),
            'tasks_by_type': {},
            'tasks': []
        }
        
        # Count by type
        for task in tasks:
            summary['tasks_by_type'][task.task_type] = \
                summary['tasks_by_type'].get(task.task_type, 0) + 1
        
        # Add task details
        for task in tasks:
            task_dict = asdict(task)
            # Convert Register to dict if present
            if task_dict['register']:
                task_dict['register'] = asdict(task.register)
            summary['tasks'].append(task_dict)
        
        output_file = Path(output_path)
        output_file.write_text(json.dumps(summary, indent=2))
        print(f"✅ Task summary saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate OpenSpec agents for DDM device model implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python run_openspec_from_ddm.py \\
      --project /path/to/demo_wdog_proj \\
      --dml modules/demo_watchdog/demo_watchdog.dml \\
      --spec wdt.md

  # With custom model and port
  python run_openspec_from_ddm.py \\
      --project /path/to/demo_wdog_proj \\
      --dml modules/demo_watchdog/demo_watchdog.dml \\
      --spec wdt.md \\
      --model iflow/qwen3-coder-plus \\
      --port 8052

  # Limit number of tasks
  python run_openspec_from_ddm.py \\
      --project /path/to/demo_wdog_proj \\
      --dml modules/demo_watchdog/demo_watchdog.dml \\
      --spec wdt.md \\
      --max-tasks 5
        """
    )
    
    parser.add_argument('--project', required=True, 
                        help='Path to the DDM project root directory')
    parser.add_argument('--dml', required=True,
                        help='Relative path to the DML file from project root')
    parser.add_argument('--spec', required=True,
                        help='Path to hardware specification (absolute or relative to project)')
    parser.add_argument('--model', default='iflow/Qwen3-Coder',
                        help='LLM model to use (default: iflow/Qwen3-Coder)')
    parser.add_argument('--port', type=int, default=8051,
                        help='MCP server port (default: 8051)')
    parser.add_argument('--max-tasks', type=int,
                        help='Maximum number of tasks to generate')
    parser.add_argument('--openspec-venv',
                        help='Path to OpenSpec virtual environment')
    parser.add_argument('--output-summary', default='openspec_tasks_summary.json',
                        help='Output file for task summary JSON')
    
    args = parser.parse_args()
    
    # Validate paths
    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"❌ Error: Project directory not found: {project_path}")
        sys.exit(1)
    
    dml_file = args.dml
    dml_full_path = project_path / dml_file
    if not dml_full_path.exists():
        print(f"❌ Error: DML file not found: {dml_full_path}")
        sys.exit(1)
    
    # Resolve spec path
    spec_path = Path(args.spec)
    if not spec_path.is_absolute():
        spec_path = project_path / spec_path
    if not spec_path.exists():
        print(f"❌ Error: Specification file not found: {spec_path}")
        sys.exit(1)
    
    print("=" * 80)
    print("OpenSpec DDM Project Orchestrator")
    print("=" * 80)
    print(f"Project: {project_path}")
    print(f"DML File: {dml_file}")
    print(f"Spec File: {spec_path}")
    print(f"Model: {args.model}")
    print(f"Port: {args.port}")
    print("=" * 80)
    print()
    
    # Step 1: Parse hardware specification
    print("📖 Step 1: Parsing hardware specification...")
    parser = HardwareSpecParser(str(spec_path))
    registers = parser.parse_registers()
    print(f"✅ Found {len(registers)} registers")
    for reg in registers:
        print(f"   - {reg.name} @ {reg.address} ({reg.width}-bit, {reg.access})")
    print()
    
    # Step 2: Generate tasks
    print("📋 Step 2: Generating implementation tasks...")
    task_gen = TaskGenerator(str(project_path), dml_file, str(spec_path))
    tasks = task_gen.generate_tasks(registers)
    
    if args.max_tasks and len(tasks) > args.max_tasks:
        print(f"⚠️  Limiting to {args.max_tasks} tasks (from {len(tasks)})")
        tasks = tasks[:args.max_tasks]
    
    print(f"✅ Generated {len(tasks)} tasks:")
    for task in tasks:
        deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
        print(f"   [{task.task_id}] {task.title}{deps}")
    print()
    
    # Step 3: Initialize OpenSpec
    print("🔧 Step 3: Setting up OpenSpec integration...")
    orchestrator = OpenSpecOrchestrator(
        str(project_path), 
        model=args.model, 
        port=args.port,
        openspec_venv=args.openspec_venv,
        dml_file=dml_file,
        spec_file=str(spec_path)
    )
    
    if not orchestrator.initialize_openspec_project():
        print("⚠️  OpenSpec not fully initialized, but continuing...")
    print()
    
    # Step 3.5: Initialize Git repository
    print("🔧 Step 3.5: Setting up Git repository...")
    orchestrator.initialize_git_repo()
    print()
    
    # Step 4: Create change proposals
    print("📝 Step 4: Creating OpenSpec change proposals...")
    proposals = orchestrator.create_change_proposals(tasks)
    print(f"✅ Created {len(proposals)} change proposals")
    print()
    
    # Step 5: Generate orchestration script
    print("🤖 Step 5: Generating orchestration script...")
    script_path = orchestrator.create_orchestration_script(tasks, proposals)
    print(f"✅ Created orchestration script: {script_path}")
    print()
    
    # Step 6: Generate task summary
    print("📊 Step 6: Generating task summary...")
    summary_path = project_path / args.output_summary
    orchestrator.generate_task_summary(tasks, str(summary_path))
    print()
    
    # Final summary
    print("=" * 80)
    print("✅ Setup Complete!")
    print("=" * 80)
    print()
    print("📁 Generated Files:")
    print(f"   - Task summary: {summary_path}")
    print(f"   - Orchestration script: {script_path}")
    print(f"   - Change proposals: {project_path}/openspec/changes/")
    print()
    print("🚀 Next Steps:")
    print()
    print("1. Review the generated change proposals:")
    print(f"   cd {project_path}")
    print("   ls -la openspec/changes/")
    print()
    print("2. Review the task summary:")
    print(f"   cat {summary_path}")
    print()
    print("3. Run the orchestration script to start OpenSpec agents:")
    print(f"   bash {script_path}")
    print()
    print("   OR manually run OpenSpec for each task:")
    print(f"   cd {project_path}")
    print(f"   source {orchestrator.openspec_venv}/bin/activate")
    print("   # Then use openspec commands to work on changes")
    print()
    print("4. Validate implementations:")
    print("   openspec validate --all")
    print()
    print("5. Run tests:")
    print(f"   cd {project_path}")
    print("   make test")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
