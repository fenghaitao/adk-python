# Agent OS Integration with ADK

This sample demonstrates the integration of Agent OS into the Agent Development Kit (ADK) as a root agent with Claude Code as a specialized subagent.

## Overview

Agent OS is a comprehensive product development workflow management system that has been integrated into ADK to provide:

- **Systematic Product Development**: From planning to deployment
- **Specification Management**: Create and manage technical specifications
- **Task Execution**: Break down and execute development tasks
- **Code Management**: Handle implementation through specialized subagents
- **Git Workflow**: Automated branch management and version control
- **Quality Assurance**: Testing and validation workflows

## Architecture

```
Agent OS Root Agent (ADK)
├── Product Planning & Specification
├── Task Management & Coordination
└── Claude Code Subagent
    ├── Code Implementation
    ├── File Management
    ├── Git Workflow Management
    ├── Testing & QA
    └── Documentation
```

## Agent Structure

### Root Agent: `agent_os_root`
- **Role**: Workflow coordination and high-level planning
- **Capabilities**: Product planning, specification creation, task breakdown
- **Tools**: Product mission creation, technical specs, task management

### Subagent: `claude_code_agent`
- **Role**: Technical implementation and code management
- **Capabilities**: Code implementation, file operations, git management, testing
- **Tools**: File creation, feature implementation, test execution, git operations

## Workflow Commands

The integration supports these Agent OS workflow commands:

### Planning Phase
- `@plan-product` - Analyze product requirements and create development plans
- `@analyze-product` - Deep analysis of product needs and market fit

### Specification Phase
- `@create-spec` - Create detailed technical specifications
- `@create-tasks` - Break down specifications into actionable tasks

### Execution Phase
- `@execute-tasks` - Execute all tasks in a specification systematically
- `@execute-task` - Execute a specific task with full workflow

## File Structure

The integration follows Agent OS conventions:

```
.agent-os/
├── product/
│   ├── mission.md          # Product mission and goals
│   ├── mission-lite.md     # Condensed mission summary
│   └── roadmap.md          # Development roadmap
├── specs/
│   └── YYYY-MM-DD-feature-name/
│       ├── spec.md         # Detailed specification
│       ├── spec-lite.md    # Specification summary
│       ├── tasks.md        # Task breakdown
│       └── sub-specs/
│           └── technical-spec.md
├── standards/
│   ├── best-practices.md   # Development best practices
│   └── code-style.md       # Coding standards
└── instructions/
    └── core/               # Workflow instructions
```

## Usage Examples

### 1. Create a New Product Plan

```python
response = root_agent.run("@plan-product for a task management application")
```

### 2. Create Technical Specification

```python
response = root_agent.run("@create-spec for user authentication system")
```

### 3. Execute Development Tasks

```python
response = root_agent.run("@execute-tasks for the authentication spec")
```

### 4. Implement Specific Feature

```python
response = root_agent.run("@execute-task: implement login form validation")
```

## Key Features

### 1. Systematic Workflow
- Follows Agent OS three-phase execution model
- Pre-execution setup, task execution loop, post-execution tasks
- Comprehensive task tracking and completion verification

### 2. Git Integration
- Automatic branch creation from specification names
- Conventional commit messages
- Pull request creation with detailed descriptions
- Branch naming follows Agent OS conventions

### 3. Quality Assurance
- Automated test execution and analysis
- Code quality validation
- Documentation generation
- Task completion verification

### 4. Multi-Agent Coordination
- Root agent handles planning and coordination
- Subagent handles technical implementation
- Clear delegation patterns and communication

## Running the Demo

1. **Install Dependencies**:
   ```bash
   pip install google-adk
   ```

2. **Run the Interactive Demo**:
   ```bash
   python main.py
   ```

3. **Try Workflow Commands**:
   ```
   Agent OS > @plan-product for a calculator app
   Agent OS > @create-spec for basic arithmetic operations
   Agent OS > @execute-tasks
   ```

## Integration Benefits

### For ADK Users
- **Structured Workflows**: Systematic approach to product development
- **Multi-Agent Patterns**: Example of effective agent delegation
- **Real-World Application**: Production-ready workflow management

### For Agent OS Users
- **LLM Integration**: Leverage advanced language models through ADK
- **Tool Ecosystem**: Access to ADK's rich tool library
- **Deployment Options**: Deploy on Google Cloud infrastructure

### Combined Value
- **Best of Both Worlds**: Agent OS workflows with ADK capabilities
- **Scalable Architecture**: Handle complex multi-agent scenarios
- **Production Ready**: Enterprise-grade agent development

## Configuration

The integration can be customized through:

- **Model Selection**: Change LLM models in YAML configs
- **Tool Configuration**: Add or modify available tools
- **Workflow Customization**: Adapt Agent OS instructions
- **Subagent Specialization**: Create domain-specific subagents

## Next Steps

1. **Extend Subagents**: Add specialized agents for testing, deployment, etc.
2. **Custom Workflows**: Create domain-specific Agent OS workflows
3. **Tool Integration**: Add more ADK tools to enhance capabilities
4. **Deployment**: Deploy the integrated system to production

This integration demonstrates how Agent OS and ADK can work together to create powerful, systematic agent-based development workflows.