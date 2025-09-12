# Agent OS Integration Demo

This demo showcases both Python and YAML agent implementations working with the ADK Runner class for Agent OS workflow management.

## What This Demo Shows

✅ **Python Agent**: Fully functional agent defined in `python_agent/agent.py`  
✅ **YAML Agent**: Configuration-based agent defined in `yaml_agent/root_agent.yaml`  
✅ **Runner Integration**: Both agents work with ADK's `InMemoryRunner` class  
✅ **Agent OS Workflows**: Support for Agent OS commands like `@plan-product`, `@create-spec`, etc.

## Running the Demo

```bash
# From the agent_os_advanced directory
python demo_runner.py
```

## Demo Output

The demo will show:

1. **Python Agent Loading**: Displays agent details, tools, and sub-agents
2. **YAML Agent Loading**: Shows the same information for the YAML-configured agent
3. **Runner Integration Testing**: Verifies both agents work with InMemoryRunner
4. **Usage Examples**: Complete code snippets for integration

## Agent Capabilities

Both agents support these Agent OS workflow commands:

- `@plan-product` - Analyze and plan product development
- `@create-spec` - Create detailed technical specifications  
- `@create-tasks` - Break down specs into actionable tasks
- `@execute-tasks` - Execute development tasks systematically
- `@execute-task` - Execute a specific task

## Agent Tools

### Python Agent (7 tools)
- `create_product_mission` - Create product mission documents
- `create_technical_spec` - Generate technical specifications
- `create_task_breakdown` - Break specs into actionable tasks
- `analyze_project_structure` - Analyze current project layout
- `create_api_workflow` - Create API-specific workflows
- `create_frontend_workflow` - Create frontend-specific workflows
- `list_available_workflows` - List all available workflows

### YAML Agent (4 tools)
- `create_product_mission` - Create product mission documents
- `create_technical_spec` - Generate technical specifications
- `create_task_breakdown` - Break specs into actionable tasks
- `analyze_project_structure` - Analyze current project layout

### Sub-Agent Tools (Claude Code Agent)
Both agents include a `claude_code_agent` sub-agent with these tools:
- `create_file_structure` - Set up project file structure
- `implement_feature` - Implement specific features
- `run_tests` - Execute test suites and analyze results
- `manage_git_workflow` - Handle git operations
- `update_task_status` - Mark tasks as complete
- `create_documentation` - Generate project documentation

## Using the Agents

### With ADK CLI

```bash
# Run Python agent
adk run python_agent/agent.py

# Run YAML agent  
adk run yaml_agent/root_agent.yaml
```

### With Runner Class

```python
from google.adk.runners import InMemoryRunner
from google.adk.agents.config_agent_utils import from_config
from google.genai import types
import asyncio

# Load agent (Python or YAML)
from python_agent.agent import agent  # Python agent
# OR
agent = from_config('yaml_agent/root_agent.yaml')  # YAML agent

# Create runner
runner = InMemoryRunner(agent)

# Run with session management
async def run_agent():
    user_id = "user123"
    session_id = "session456"
    message = types.Content(parts=[types.Part(text="@plan-product for my app")])
    
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message
    ):
        if event.author == 'model':
            print(event.content.parts[0].text)

# Run the agent
asyncio.run(run_agent())
```

## File Structure

```
agent_os_advanced/
├── demo_runner.py              # This demo script
├── DEMO_README.md              # This documentation
├── python_agent/
│   ├── __init__.py
│   └── agent.py                # Python agent implementation
├── yaml_agent/
│   ├── __init__.py
│   ├── root_agent.yaml         # Root agent configuration
│   ├── claude_code_agent.yaml  # Sub-agent configuration
│   └── tools.py                # Tool implementations for YAML agent
└── .agent-os/                  # Created by agents during execution
    ├── product/                # Product mission and roadmap
    ├── specs/                  # Technical specifications
    └── standards/              # Development standards
```

## Key Features Demonstrated

1. **Multi-Agent Architecture**: Root agent with specialized sub-agents
2. **Agent OS Integration**: Full workflow management capabilities
3. **Flexible Configuration**: Both code-based and YAML-based agent definitions
4. **Tool Ecosystem**: Rich set of development and workflow tools
5. **Session Management**: Proper ADK session handling
6. **File Structure Management**: Agent OS directory conventions

This demo proves that both Python and YAML agents are fully functional and ready for Agent OS-style product development workflows! 🚀