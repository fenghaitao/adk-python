#!/usr/bin/env python3
"""
MCP Development Workflow Demo
============================

This script demonstrates the MCP-enhanced multi-agent development system
that uses Model Context Protocol servers for enhanced capabilities.
"""

import asyncio
import os

# Import our MCP multi-agent system
from agent import agent as root_agent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types


async def demo_mcp_development_workflow():
    """Demonstrate the MCP-enhanced development workflow."""

    print("🔧 MCP Multi-Agent Development Workflow Demo")
    print("=" * 60)

    # Set up ADK services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()

    # Create runner
    runner = Runner(
        app_name="mcp_dev_demo",
        agent=root_agent,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service,
    )

    # Demo scenarios
    scenarios = [
        {
            "title": "📋 Simple Calculator with MCP",
            "spec": """
Create a Python calculator module with MCP-enhanced development:

## Requirements
1. Basic arithmetic operations: add, subtract, multiply, divide
2. Advanced operations: power, square root, factorial
3. Input validation and comprehensive error handling
4. Command-line interface with user-friendly prompts
5. Memory functions (store, recall, clear)
6. Calculation history with persistence

## Technical Specifications
- Python 3.8+ with type hints and dataclasses
- Use MCP file operations for robust file handling
- Implement proper logging and error reporting
- Include comprehensive docstrings and comments
- Follow PEP 8 standards with automated formatting
- Create modular, testable code architecture

## Testing Requirements
- Unit tests for all calculator functions
- Integration tests for CLI interface
- Edge case testing (division by zero, invalid inputs)
- Performance tests for complex calculations
- Minimum 95% test coverage

## Quality Standards
- Use MCP build tools for code quality checks
- Automated formatting with black and isort
- Type checking with mypy
- Comprehensive error handling
- Professional documentation
            """,
            "description": "Creates a calculator using MCP servers for enhanced file operations, build tools, and git management.",
        },
        {
            "title": "🌐 Web API with MCP Enhancement",
            "spec": """
Create a RESTful API service with MCP-enhanced development workflow:

## Core Features
1. User authentication and authorization (JWT)
2. CRUD operations for user management
3. Rate limiting and request validation
4. API documentation with OpenAPI/Swagger
5. Database integration with SQLAlchemy
6. Comprehensive logging and monitoring

## Technical Architecture
- FastAPI framework with async/await
- PostgreSQL database with migrations
- Redis for caching and session management
- Docker containerization
- Environment-based configuration
- Comprehensive error handling and validation

## MCP Integration Points
- Use MCP file operations for configuration management
- Leverage MCP build tools for dependency management
- Employ MCP testing frameworks for API testing
- Utilize MCP git operations for version control

## Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- Database migration testing
- Performance and load testing
- Security testing for authentication
            """,
            "description": "Builds a complete web API using MCP servers for enhanced development capabilities.",
        },
        {
            "title": "🤖 CLI Tool with MCP Workflow",
            "spec": """
Create a command-line productivity tool with full MCP integration:

## Tool Features
1. File organization and management utilities
2. Text processing and transformation tools
3. Data analysis and reporting capabilities
4. Configuration management system
5. Plugin architecture for extensibility
6. Interactive and batch operation modes

## Implementation Details
- Click framework for CLI interface
- Rich library for beautiful terminal output
- Configurable via YAML/TOML files
- Comprehensive help and documentation
- Cross-platform compatibility
- Professional error handling and logging

## MCP-Enhanced Development
- File operations through MCP filesystem server
- Build automation with MCP build tools
- Version control with MCP git integration
- Quality assurance with MCP testing tools

## Quality Requirements
- Comprehensive test suite with pytest
- Code coverage above 90%
- Type checking with mypy
- Documentation with Sphinx
- Professional packaging and distribution
            """,
            "description": "Develops a CLI tool showcasing full MCP server integration throughout the development lifecycle.",
        },
        {
            "title": "📊 Data Processing Pipeline with MCP",
            "spec": """
Create a data processing pipeline with MCP-enhanced development:

## Pipeline Components
1. Data ingestion from multiple sources (CSV, JSON, APIs)
2. Data validation and cleaning operations
3. Transformation and aggregation logic
4. Output generation (reports, visualizations)
5. Error handling and recovery mechanisms
6. Monitoring and logging capabilities

## Technical Implementation
- Pandas for data manipulation
- Pydantic for data validation
- Matplotlib/Plotly for visualizations
- Configurable processing stages
- Parallel processing capabilities
- Comprehensive error reporting

## MCP Integration Benefits
- Robust file handling for data sources
- Automated testing of pipeline components
- Quality assurance with build tools
- Version control for pipeline configurations

## Testing and Quality
- Unit tests for each pipeline stage
- Integration tests for end-to-end processing
- Data quality validation tests
- Performance benchmarking
- Error scenario testing
            """,
            "description": "Creates a data processing pipeline demonstrating MCP server capabilities for file handling and testing.",
        },
    ]

    print("Available MCP development workflow demonstrations:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   {scenario['description']}")

    # For automated testing, use the first scenario (calculator)
    scenario_index = 0
    print(
        f"\nAutomatically selecting scenario {scenario_index + 1} for automated testing."
    )
    # Comment out interactive input for automated testing:
    # print(f"\nChoose a scenario (1-{len(scenarios)}) or 'q' to quit: ", end="")
    # choice = input().strip()
    #
    # if choice.lower() == "q":
    #     print("👋 Demo cancelled.")
    #     return
    #
    # try:
    #     scenario_index = int(choice) - 1
    #     if scenario_index < 0 or scenario_index >= len(scenarios):
    #         print("❌ Invalid choice.")
    #         return
    # except ValueError:
    #     print("❌ Invalid choice.")
    #     return

    selected_scenario = scenarios[scenario_index]

    print(f"\n🎯 Running: {selected_scenario['title']}")
    print("=" * 70)
    print(f"Specification: {selected_scenario['spec'][:200]}...")
    print(f"\n🔄 Processing with MCP-enhanced multi-agent system...")

    try:
        # Create session
        session = await session_service.create_session(
            app_name="mcp_dev_demo", user_id="demo_user"
        )

        # Run the specification through MCP-enhanced workflow
        response_parts = []
        content = types.Content(
            role="user", parts=[types.Part(text=selected_scenario["spec"])]
        )
        async for response in runner.run_async(
            user_id="demo_user",
            session_id=session.id,
            new_message=content,
        ):
            if hasattr(response, "content") and response.content:
                for part in response.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_parts.append(part.text)
                        # Print progress updates
                        if any(
                            keyword in part.text.lower()
                            for keyword in [
                                "mcp",
                                "processing",
                                "analyzing",
                                "building",
                                "testing",
                                "committing",
                            ]
                        ):
                            print(f"📍 {part.text[:100]}...")

        print(f"\n✅ MCP development workflow completed!")
        print(f"📄 Full response:")
        print("=" * 70)
        for part in response_parts:
            print(part)
            print("-" * 50)

    except Exception as e:
        print(f"❌ Error during MCP workflow: {str(e)}")
        print(
            "Note: This demo requires proper ADK setup with API keys and MCP servers."
        )


def explain_mcp_integration():
    """Explain MCP integration in the development workflow."""

    print("🔧 MCP Integration in Development Workflow")
    print("=" * 50)

    mcp_capabilities = [
        {
            "server": "MCP Filesystem Server",
            "purpose": "Enhanced File Operations",
            "capabilities": [
                "Robust file reading with size limits and validation",
                "Safe file writing with directory creation",
                "Directory listing with metadata",
                "Path validation and access control",
                "Encoding detection and handling",
            ],
            "benefits": [
                "Improved error handling for file operations",
                "Security through access control",
                "Better performance with streaming",
                "Metadata extraction and analysis",
            ],
        },
        {
            "server": "MCP Build Server",
            "purpose": "Advanced Build Operations",
            "capabilities": [
                "Command execution with timeout protection",
                "Dependency installation and management",
                "Code quality checks (mypy, black, isort)",
                "Test execution with coverage analysis",
                "Build artifact generation",
            ],
            "benefits": [
                "Consistent build environments",
                "Automated quality assurance",
                "Parallel build processing",
                "Comprehensive build reporting",
            ],
        },
        {
            "server": "MCP Git Server",
            "purpose": "Professional Version Control",
            "capabilities": [
                "Repository initialization and management",
                "Intelligent commit message generation",
                "Branch management and merging",
                "Automated .gitignore creation",
                "Repository analysis and reporting",
            ],
            "benefits": [
                "Consistent git workflows",
                "Professional commit practices",
                "Automated repository setup",
                "Enhanced git operation safety",
            ],
        },
    ]

    for i, mcp_info in enumerate(mcp_capabilities, 1):
        print(f"\n{i}. {mcp_info['server']}")
        print(f"   Purpose: {mcp_info['purpose']}")
        print("   " + "─" * 50)

        print("   Capabilities:")
        for capability in mcp_info["capabilities"]:
            print(f"   • {capability}")

        print("   Benefits:")
        for benefit in mcp_info["benefits"]:
            print(f"   ✓ {benefit}")

    print(f"\n🔄 MCP Workflow Advantages:")
    print("• **Enhanced Reliability**: MCP servers provide robust, tested operations")
    print(
        "• **Improved Security**: Access control and validation at the protocol level"
    )
    print("• **Better Performance**: Optimized operations with caching and streaming")
    print("• **Consistent Environments**: Standardized tools across development stages")
    print("• **Professional Quality**: Enterprise-grade development operations")

    print(f"\n🎯 Integration Points:")
    print(
        "• **Specification Reading**: MCP file operations for robust document parsing"
    )
    print("• **Code Generation**: MCP filesystem for safe code creation and validation")
    print("• **Test Creation**: MCP build tools for test framework integration")
    print(
        "• **Build Process**: MCP build server for reliable compilation and validation"
    )
    print("• **Test Execution**: MCP testing tools for comprehensive quality assurance")
    print(
        "• **Version Control**: MCP git operations for professional repository management"
    )


if __name__ == "__main__":
    print("MCP Multi-Agent Development Workflow Demo")
    print("=" * 45)
    print("Choose an option:")
    print("1. Run MCP development workflow demo")
    print("2. Explain MCP integration benefits")
    print("3. Exit")

    # For automated testing, run option 1 directly
    # choice = input("\nEnter choice (1-3): ").strip()
    choice = "1"

    if choice == "1":
        print("\n🚀 Starting MCP development workflow demo...")
        print("Note: This requires proper ADK setup with API keys and MCP servers.")
        try:
            asyncio.run(demo_mcp_development_workflow())
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user.")
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print(
                "Make sure you have ADK properly installed and MCP servers configured."
            )
    elif choice == "2":
        explain_mcp_integration()
    else:
        print("👋 Goodbye!")
