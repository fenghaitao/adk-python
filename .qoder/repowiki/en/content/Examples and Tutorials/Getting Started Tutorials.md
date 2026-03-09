# Getting Started Tutorials

<cite>
**Referenced Files in This Document**
- [hello_world/agent.py](file://contributing/samples/hello_world/agent.py)
- [hello_world/main.py](file://contributing/samples/hello_world/main.py)
- [quickstart/agent.py](file://contributing/samples/quickstart/agent.py)
- [core_basic_config/root_agent.yaml](file://contributing/samples/core_basic_config/root_agent.yaml)
- [core_basic_config/README.md](file://contributing/samples/core_basic_config/README.md)
- [AGENTS.md](file://AGENTS.md)
- [README.md](file://README.md)
- [src/google/adk/__init__.py](file://src/google/adk/__init__.py)
- [src/google/adk/runners.py](file://src/google/adk/runners.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites and Environment Setup](#prerequisites-and-environment-setup)
3. [Hello World Tutorial](#hello-world-tutorial)
4. [Quickstart Guide](#quickstart-guide)
5. [Core Basic Config Sample](#core-basic-config-sample)
6. [Understanding Agent Configuration](#understanding-agent-configuration)
7. [Agent Lifecycle and Execution Flow](#agent-lifecycle-and-execution-flow)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Best Practices](#best-practices)
10. [Next Steps](#next-steps)

## Introduction
Welcome to the ADK Getting Started Tutorials. This guide will help you create your first AI agents using the Agent Development Kit (ADK), a code-first Python framework for building, evaluating, and deploying sophisticated AI agents. You'll learn how to create agents, configure them, and run them locally for rapid prototyping.

ADK provides a flexible and modular framework that applies software development principles to AI agent creation. It supports single agents, multi-agent systems, and integrates with tools, memory, and session management services.

## Prerequisites and Environment Setup
Before you begin, ensure you have:
- Python 3.10+ (Python 3.11+ recommended)
- A working Python environment with pip
- Basic familiarity with Python programming
- Understanding of asynchronous programming concepts (async/await) is helpful

Key installation and setup information:
- ADK can be installed via pip from PyPI
- Development setup includes using uv for faster dependency management
- Virtual environments are required for development

For detailed installation instructions and development setup, refer to the main project documentation and AGENTS.md guide.

**Section sources**
- [README.md](file://README.md#L62-L84)
- [AGENTS.md](file://AGENTS.md#L166-L229)

## Hello World Tutorial
The hello_world sample is the perfect starting point for beginners. It demonstrates a simple agent that can roll dice and check for prime numbers, showcasing agent creation, tool integration, and execution.

### Creating Your First Agent
The hello_world agent demonstrates the core concepts:
- Agent definition with model selection, name, description, and instructions
- Tool integration for dice rolling and prime number checking
- Configuration of safety settings and generation parameters
- Asynchronous execution using the Runner

Key components of the hello_world agent:
- Model configuration: Uses a Gemini model for reasoning and tool execution
- Tool functions: roll_die and check_prime demonstrate custom tool creation
- Instruction design: Clear guidance on when and how to use tools
- Safety configuration: Custom safety settings for content moderation

### Running the Hello World Example
To run the hello_world example:
1. Navigate to the hello_world sample directory
2. Install dependencies using the project's development setup
3. Execute the main script to see the agent in action

The example demonstrates:
- Creating an InMemoryRunner with your agent
- Establishing sessions for user interactions
- Sending user messages and receiving agent responses
- Working with artifacts and session state

### Understanding the Execution Flow
The hello_world example shows the complete agent lifecycle:
- Session creation and management
- Message processing through the Runner
- Tool execution and result handling
- Response generation and streaming

**Section sources**
- [hello_world/agent.py](file://contributing/samples/hello_world/agent.py#L67-L109)
- [hello_world/main.py](file://contributing/samples/hello_world/main.py#L30-L104)

## Quickstart Guide
The quickstart sample provides a minimal example of agent creation with two simple tools: weather reporting and time lookup. This sample focuses on the essential elements needed to create a functional agent quickly.

### Minimal Agent Implementation
The quickstart agent demonstrates:
- Simple tool functions with clear docstrings
- Direct agent configuration without complex setup
- Straightforward execution pattern
- Practical tool usage for common tasks

### Key Elements of Quickstart
- Weather tool: Provides current weather information for specific cities
- Time tool: Returns current time in specified cities with timezone handling
- Minimal configuration: Focuses on essential agent parameters
- Simple execution: Demonstrates basic agent interaction patterns

This sample is ideal for understanding the fundamental concepts before moving to more complex configurations.

**Section sources**
- [quickstart/agent.py](file://contributing/samples/quickstart/agent.py#L18-L83)

## Core Basic Config Sample
The core_basic_config sample demonstrates configuration-driven agent creation using YAML files. This approach allows you to define agents without writing Python code, focusing on essential configuration parameters.

### YAML Configuration Structure
The core_basic_config sample shows:
- Name, description, and model configuration
- Instruction definition for agent behavior
- Minimal YAML schema for agent definition
- Integration with the ADK configuration system

### Configuration File Components
The root_agent.yaml includes:
- Agent name for identification
- Model selection for LLM integration
- Description for agent purpose
- Instruction text for behavioral guidance
- YAML schema reference for validation

This sample is perfect for teams that prefer declarative configuration or need to manage agents through configuration files.

**Section sources**
- [core_basic_config/root_agent.yaml](file://contributing/samples/core_basic_config/root_agent.yaml#L1-L10)
- [core_basic_config/README.md](file://contributing/samples/core_basic_config/README.md#L1-L8)

## Understanding Agent Configuration
ADK supports multiple approaches to agent configuration, each suited for different use cases and complexity levels.

### Configuration Approaches
1. **Code-based configuration**: Direct Python agent creation with full control
2. **YAML configuration**: Declarative agent definition for simpler setups
3. **Hybrid approach**: Combining code and configuration for complex scenarios

### Configuration Parameters
Essential agent configuration includes:
- Model selection and tuning parameters
- Instruction design and behavioral guidance
- Tool registration and function declarations
- Safety settings and content moderation
- Generation configuration for response handling

### Configuration Best Practices
- Keep instructions clear and specific
- Define tools with proper documentation
- Configure safety settings appropriately
- Test configuration changes systematically
- Validate configuration against schema requirements

**Section sources**
- [AGENTS.md](file://AGENTS.md#L138-L165)
- [core_basic_config/root_agent.yaml](file://contributing/samples/core_basic_config/root_agent.yaml#L1-L10)

## Agent Lifecycle and Execution Flow
Understanding the agent lifecycle is crucial for effective ADK development. The lifecycle encompasses session management, message processing, tool execution, and response generation.

### Invocation Lifecycle
Each agent execution follows a structured lifecycle:
1. Session retrieval or creation
2. Invocation context establishment
3. Agent reasoning and planning
4. Tool execution when needed
5. Response generation and streaming
6. Event persistence and session updates

### Runner Responsibilities
The Runner orchestrates the entire execution process:
- Manages agent execution within sessions
- Handles message processing and event generation
- Coordinates with persistence services (artifacts, memory, sessions)
- Integrates with plugins and middleware
- Supports different execution modes (sync, async, live)

### Event-Driven Architecture
ADK uses an event-driven approach:
- Each step generates structured Event objects
- Events stream back to callers for real-time interaction
- Events persist to sessions for continuity
- Plugins can intercept and modify events
- State management through session events

### Execution Modes
Different execution modes serve various purposes:
- Synchronous execution for local testing
- Asynchronous execution for production workloads
- Live streaming for real-time interactions
- Rewind functionality for session correction

**Section sources**
- [AGENTS.md](file://AGENTS.md#L37-L72)
- [src/google/adk/runners.py](file://src/google/adk/runners.py#L112-L149)
- [src/google/adk/runners.py](file://src/google/adk/runners.py#L493-L622)

## Troubleshooting Guide
Common issues and solutions when working with ADK agents:

### Environment and Setup Issues
- **Python version conflicts**: Ensure Python 3.10+ is installed and properly configured
- **Virtual environment problems**: Always use the project's virtual environment setup
- **Dependency resolution**: Use the project's dependency management system (uv)
- **Module import errors**: Verify proper installation and PYTHONPATH configuration

### Agent Configuration Problems
- **Model availability**: Ensure selected models are supported and accessible
- **Tool function issues**: Verify tool functions are properly defined and imported
- **Instruction clarity**: Provide clear, specific instructions for desired behavior
- **Safety setting conflicts**: Review and adjust safety settings appropriately

### Runtime Execution Issues
- **Session management**: Check session creation and retrieval logic
- **Message formatting**: Ensure Content objects are properly constructed
- **Async execution**: Handle async/await patterns correctly
- **Event processing**: Verify event handling and streaming logic

### Common Error Patterns
- **Missing dependencies**: Install all required packages for your agent tools
- **Configuration validation**: Validate YAML and Python configuration files
- **Resource limits**: Monitor memory and processing time constraints
- **Network connectivity**: Ensure proper access to external services and APIs

**Section sources**
- [AGENTS.md](file://AGENTS.md#L166-L229)
- [src/google/adk/runners.py](file://src/google/adk/runners.py#L384-L394)

## Best Practices
Follow these guidelines for effective ADK development:

### Agent Design Principles
- **Clear separation of concerns**: Keep agent logic focused and modular
- **Well-defined tools**: Create tools with specific, documented purposes
- **Robust error handling**: Implement comprehensive error handling strategies
- **State management**: Use session state judiciously and consistently
- **Security considerations**: Implement appropriate safety measures and validation

### Configuration Management
- **Version control**: Track agent configurations alongside code changes
- **Environment-specific settings**: Use separate configurations for different environments
- **Validation**: Regularly validate configuration files and schemas
- **Documentation**: Maintain clear documentation for configuration parameters

### Performance Optimization
- **Efficient tool design**: Optimize tool functions for performance
- **Memory management**: Monitor and control memory usage in long-running sessions
- **Asynchronous patterns**: Use async/await effectively for I/O-bound operations
- **Resource pooling**: Reuse connections and resources where possible

### Testing and Quality Assurance
- **Unit testing**: Test individual components and tools thoroughly
- **Integration testing**: Verify end-to-end agent functionality
- **Performance testing**: Measure and optimize agent response times
- **Edge case handling**: Test boundary conditions and error scenarios

## Next Steps
After completing the getting started tutorials, consider these advanced topics:

### Multi-Agent Systems
Explore creating complex agent interactions and coordination patterns
- Sub-agent hierarchies and delegation
- Agent communication protocols
- Workflow orchestration and task distribution

### Advanced Tool Integration
Expand beyond basic tools to include:
- External API integrations
- Database operations and data access
- File system operations and artifact management
- Custom tool development and validation

### Deployment and Production
Prepare agents for production environments:
- Containerization and deployment strategies
- Scaling considerations and load balancing
- Monitoring and observability implementation
- Security and access control mechanisms

### Evaluation and Improvement
Implement systematic agent evaluation:
- Performance metrics and measurement
- User feedback integration
- Continuous improvement processes
- A/B testing and experimentation frameworks

Continue your learning journey by exploring the comprehensive documentation, sample repositories, and community resources available through the ADK ecosystem.