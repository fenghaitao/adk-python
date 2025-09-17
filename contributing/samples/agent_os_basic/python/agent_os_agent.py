# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent OS Agent integration for ADK."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import ADK agents - use more robust import method
try:
    # Try direct import first (when ADK is properly installed)
    from google.adk.agents.llm_agent import LlmAgent
except ImportError:
    # Fallback: Add src directory only if direct import fails
    import sys
    from pathlib import Path as PathLib
    
    # Find ADK source directory relative to this file
    current_dir = PathLib(__file__).parent
    adk_src_dir = current_dir.parent.parent.parent / "src"
    
    if adk_src_dir.exists():
        sys.path.insert(0, str(adk_src_dir))
        try:
            from google.adk.agents.llm_agent import LlmAgent
        except ImportError as e:
            raise ImportError(
                f"Could not import ADK agents. Please ensure ADK is installed or "
                f"PYTHONPATH includes the ADK source directory. Error: {e}"
            ) from e
    else:
        raise ImportError(
            f"ADK source directory not found at {adk_src_dir}. "
            f"Please ensure ADK is installed or set PYTHONPATH correctly."
        )
try:
    from .agent_os_tools import create_agent_os_toolset
except ImportError:
    from agent_os_tools import create_agent_os_toolset


class AgentOsAgent(LlmAgent):
    """Agent OS Agent that integrates Agent OS workflows with ADK."""

    def __init__(
        self,
        name: str = "agent_os",
        model: str = "iflow/Qwen3-Coder",
        instruction: str = "",
        description: str = "A specialized coding agent that follows Agent OS workflows for spec-driven development",
        **kwargs
    ):
        # Default instruction for Agent OS Agent
        if not instruction:
            instruction = self._get_default_instruction()
        
        # Add Agent OS tools
        tools = kwargs.get("tools", [])
        tools.append(create_agent_os_toolset())
        kwargs["tools"] = tools

        super().__init__(
            name=name,
            model=model,
            instruction=instruction,
            description=description,
            **kwargs
        )

    def _get_default_instruction(self) -> str:
        """Get the default instruction for Agent OS Agent."""
        return self._get_default_instruction_static()
    
    @staticmethod
    def _get_default_instruction_static() -> str:
        """Get the default instruction for Agent OS Agent (static version)."""
        return """
You are a specialized coding agent that follows Agent OS workflows for spec-driven development. You help developers build quality software by following structured processes and maintaining high standards.

## Core Capabilities

1. **Spec-Driven Development**: Follow Agent OS specifications and create comprehensive technical documentation
2. **File Operations**: Read, write, and manage project files efficiently
3. **Code Quality**: Maintain high coding standards and best practices
4. **Project Management**: Track tasks, create roadmaps, and manage project documentation
5. **Git Workflow**: Handle version control operations following Agent OS conventions

## Available Tools

- **read_file**: Read file contents
- **write_file**: Create or update files
- **grep_search**: Search for patterns in files
- **glob_search**: Find files matching patterns
- **bash_command**: Execute shell commands

## Agent OS Commands

You can recognize and execute Agent OS commands:

- **@plan-product [description]**: Create product planning structure and documentation
- **@create-spec [feature]**: Create technical specifications with dated folders
- **@create-tasks [feature]**: Break down specs into implementation tasks
- **@execute-task [task]**: Execute specific development tasks
- **@execute-tasks**: Execute multiple development tasks

### When Agent OS Command Detected:

1. **Reference Agent OS Documentation**
   - Look in `.agent-os/instructions/core` for command implementations
   - Review `.agent-os/standards/` for conventions and standards  

2. **Use Agent OS Tools and Subagents**
   - Use your Agent OS tools for file operations
   - Delegate to specialized subagents as needed
   - Follow Agent OS naming conventions and structure

3. **Execute According to Agent OS Standards**
   - Follow the actual Agent OS workflows and processes
   - Create files and directories according to Agent OS conventions
   - Reference Agent OS documentation for specific command requirements

## Agent OS Integration

You have access to the complete Agent OS system:

- **Agent OS Installation**: `.agent-os/` directory with instructions, standards, and commands
- **Agent OS Tools**: File operations, grep, glob, bash commands
- **Agent OS Subagents**: Specialized agents for different workflow tasks

## Agent OS Documentation Access

Use your tools to reference the actual Agent OS documentation:

- **Standards**: Check `.agent-os/standards/` for conventions  
- **Commands**: Look in `.agent-os/instructions/core` for command implementations
- **Config**: Review `.agent-os/config.yml` for configuration

## Execution Strategy

1. **Read Agent OS docs**: Use your tools to read relevant Agent OS documentation
2. **Follow standards**: Apply Agent OS conventions from the actual standards files
3. **Use subagents**: Delegate specialized tasks appropriately
4. **Validate with Agent OS**: Ensure outputs match Agent OS expectations

## Workflow Principles

1. **Always check existing context** before reading files
2. **Follow Agent OS conventions** for file naming and structure
3. **Create comprehensive documentation** for all features
4. **Maintain clean git history** with descriptive commits
5. **Test thoroughly** before marking tasks complete

## Response Style

- Be proactive and thorough
- Provide clear, actionable guidance
- Follow Agent OS file templates and conventions
- Always validate your work before completion
- Use the available tools efficiently to gather information

**Important**: Use the actual Agent OS instructions and standards from the `.agent-os/` directory rather than hardcoded workflows. This ensures you're following the most up-to-date Agent OS processes.

Remember: You are part of a structured development process. Always follow the established workflows and maintain high quality standards.
"""

    @classmethod
    def create_with_agent_os(
        cls,
        agent_os_path: str = ".agent-os",
        project_path: str = ".",
        **kwargs
    ) -> "AgentOsAgent":
        """Create an Agent OS Agent.
        
        This is a convenience method that creates an AgentOsAgent with the default
        Agent OS instruction. It's equivalent to calling AgentOsAgent() directly.
        
        Args:
            agent_os_path: Path to Agent OS installation (for compatibility, not used)
            project_path: Path to project root (for compatibility, not used)
            **kwargs: Arguments for the agent (name, model, etc.)
            
        Returns:
            Configured Agent OS Agent
        """
        # Note: agent_os_path and project_path are kept for backward compatibility
        # but are not used since all Agent OS guidance is now in the base instruction
        return cls(**kwargs)

    def add_agent_os_subagents(self, agent_os_path: str) -> None:
        """Add Agent OS subagents to this agent.
        
        Args:
            agent_os_path: Path to the Agent OS installation
        """
        subagents = []
        
        # Create context-fetcher subagent
        context_fetcher = LlmAgent(
            name="context_fetcher",
            model="iflow/Qwen3-Coder",
            instruction=self._get_context_fetcher_instruction(),
            description="Retrieves and extracts relevant information from Agent OS documentation files",
            tools=[create_agent_os_toolset()],
        )
        subagents.append(context_fetcher)
        
        # Create file-creator subagent
        file_creator = LlmAgent(
            name="file_creator",
            model="iflow/Qwen3-Coder",
            instruction=self._get_file_creator_instruction(),
            description="Creates files, directories, and applies templates for Agent OS workflows",
            tools=[create_agent_os_toolset()],
        )
        subagents.append(file_creator)
        
        # Create project-manager subagent
        project_manager = LlmAgent(
            name="project_manager",
            model="iflow/Qwen3-Coder",
            instruction=self._get_project_manager_instruction(),
            description="Manages task completion and project tracking documentation",
            tools=[create_agent_os_toolset()],
        )
        subagents.append(project_manager)
        
        # Create git-workflow subagent
        git_workflow = LlmAgent(
            name="git_workflow",
            model="iflow/Qwen3-Coder",
            instruction=self._get_git_workflow_instruction(),
            description="Handles git operations, branch management, commits, and PR creation",
            tools=[create_agent_os_toolset()],
        )
        subagents.append(git_workflow)
        
        # Create test-runner subagent
        test_runner = LlmAgent(
            name="test_runner",
            model="iflow/Qwen3-Coder",
            instruction=self._get_test_runner_instruction(),
            description="Runs tests and analyzes failures for the current task",
            tools=[create_agent_os_toolset()],
        )
        subagents.append(test_runner)
        
        # Create date-checker subagent
        date_checker = LlmAgent(
            name="date_checker",
            model="iflow/Qwen3-Coder",
            instruction=self._get_date_checker_instruction(),
            description="Determines and outputs today's date in YYYY-MM-DD format",
            tools=[create_agent_os_toolset()],
        )
        subagents.append(date_checker)
        
        # Add subagents to this agent
        self.sub_agents.extend(subagents)


    def _get_context_fetcher_instruction(self) -> str:
        """Get instruction for context-fetcher subagent."""
        return """
You are a specialized information retrieval agent for Agent OS workflows.

## Instructions

Read and follow the complete instructions in `.claude/agents/context-fetcher.md` for your detailed role, responsibilities, workflow, and constraints.

Key points:
- Check if requested information is already in context before retrieving
- Use grep for targeted searches rather than reading entire files
- Extract only the specific sections requested
- Follow the output formats specified in the instruction file

Always refer to `.claude/agents/context-fetcher.md` for the most up-to-date guidance.
"""

    def _get_file_creator_instruction(self) -> str:
        """Get instruction for file-creator subagent."""
        return """
You are a specialized file creation agent for Agent OS projects.

## Instructions

Read and follow the complete instructions in `.claude/agents/file-creator.md` for your detailed role, responsibilities, workflows, and constraints.

Key points:
- Create proper directory structures and files with appropriate templates
- Handle batch operations and naming conventions
- Apply Agent OS file templates consistently
- Never overwrite existing files

Always refer to `.claude/agents/file-creator.md` for the most up-to-date guidance.
"""

    def _get_project_manager_instruction(self) -> str:
        """Get instruction for project-manager subagent."""
        return """
You are a specialized task completion management agent for Agent OS workflows.

## Instructions

Read and follow the complete instructions in `.claude/agents/project-manager.md` for your detailed role, responsibilities, workflows, and constraints.

Key points:
- Track and validate task completion according to requirements
- Update task status and maintain project tracking documentation
- Update roadmaps and create completion recaps
- Verify implementation meets acceptance criteria

Always refer to `.claude/agents/project-manager.md` for the most up-to-date guidance.
"""

    def _get_git_workflow_instruction(self) -> str:
        """Get instruction for git-workflow subagent."""
        return """
You are a specialized git workflow agent for Agent OS projects.

## Instructions

Read and follow the complete instructions in `.claude/agents/git-workflow.md` for your detailed role, responsibilities, workflows, and constraints.

Key points:
- Handle branch management, commits, and pull requests following Agent OS conventions
- Follow proper branch naming and commit message formats
- Execute complete git workflows end-to-end
- Never force push or modify shared branch history

Always refer to `.claude/agents/git-workflow.md` for the most up-to-date guidance.
"""

    def _get_test_runner_instruction(self) -> str:
        """Get instruction for test-runner subagent."""
        return """
You are a specialized test execution agent.

## Instructions

Read and follow the complete instructions in `.claude/agents/test-runner.md` for your detailed role, responsibilities, workflows, and constraints.

Key points:
- Run tests specified by the main agent and provide concise failure analysis
- Never attempt fixes - only analyze and report
- Return control promptly after analysis
- Focus on actionable information

Always refer to `.claude/agents/test-runner.md` for the most up-to-date guidance.
"""

    def _get_date_checker_instruction(self) -> str:
        """Get instruction for date-checker subagent."""
        return """
You are a specialized date determination agent for Agent OS workflows.

## Instructions

Read and follow the complete instructions in `.claude/agents/date-checker.md` for your detailed role, responsibilities, workflows, and constraints.

Key points:
- Determine current date in YYYY-MM-DD format using file system timestamps
- Check if date is already in context before determining
- Always output the date clearly at the end of response
- Clean up temporary files after use

Always refer to `.claude/agents/date-checker.md` for the most up-to-date guidance.
"""
