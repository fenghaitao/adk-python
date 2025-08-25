#!/usr/bin/env python3
"""
Demo Script for Software Development Multi-Agent Workflow
=========================================================

This script demonstrates how the multi-agent development system works
by processing sample specifications and creating complete projects.
"""

import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService

# Import our multi-agent system
from agent import root_agent


async def demo_development_workflow():
    """Demonstrate the complete development workflow."""
    
    print("🚀 Software Development Multi-Agent System Demo")
    print("=" * 60)
    
    # Set up ADK services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    credential_service = InMemoryCredentialService()
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        artifact_service=artifact_service,
        credential_service=credential_service
    )
    
    # Demo scenarios
    scenarios = [
        {
            "title": "📋 Simple Calculator Specification",
            "spec": """
Create a Python calculator module with the following requirements:

## Features
1. Basic arithmetic operations: add, subtract, multiply, divide
2. Advanced operations: power, square root, factorial
3. Input validation and error handling
4. Command-line interface
5. Memory functions (store, recall, clear)

## Technical Requirements
- Python 3.8+
- Use classes for organization
- Include comprehensive tests
- Handle division by zero
- Support floating-point numbers
- Save calculation history

## File Structure
- calculator.py (main calculator class)
- cli.py (command-line interface)
- tests/ (test files)
- README.md (documentation)
            """,
            "description": "This will create a complete calculator application with tests and git commit."
        },
        {
            "title": "📝 Task Manager from Specification File",
            "spec": f"Please read the specification from the file: {os.path.abspath('sample_spec.md')} and implement the complete task manager application.",
            "description": "This will read the detailed spec file and create a full task management system."
        },
        {
            "title": "🔧 File Utility Specification",
            "spec": """
Build a Python file utility with these capabilities:

## Core Features
1. Read and write text files safely
2. Create file backups with timestamps
3. Search for text within files
4. Get file size and modification date info
5. Batch operations on multiple files
6. Comprehensive error handling

## Technical Requirements
- Python 3.8+
- Use pathlib for file operations
- Include logging for operations
- Handle file permissions gracefully
- Support different text encodings
- Create comprehensive test suite

## File Structure
- file_utility.py (main utility class)
- cli.py (command-line interface)
- tests/ (comprehensive test suite)
- examples/ (usage examples)
            """,
            "description": "This will create a file utility with backup and search capabilities."
        }
    ]
    
    print("Available demo scenarios:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   {scenario['description']}")
    
    print(f"\nChoose a scenario (1-{len(scenarios)}) or 'q' to quit: ", end="")
    choice = input().strip()
    
    if choice.lower() == 'q':
        print("👋 Demo cancelled.")
        return
    
    try:
        scenario_index = int(choice) - 1
        if scenario_index < 0 or scenario_index >= len(scenarios):
            print("❌ Invalid choice.")
            return
    except ValueError:
        print("❌ Invalid choice.")
        return
    
    selected_scenario = scenarios[scenario_index]
    
    print(f"\n🎯 Running: {selected_scenario['title']}")
    print("=" * 60)
    print(f"Specification: {selected_scenario['spec'][:200]}...")
    print("\n🔄 Processing with multi-agent system...")
    
    try:
        # Create session
        session = await session_service.create_session(
            app_name="multi_agent_demo",
            user_id="demo_user"
        )
        
        # Run the query
        response_parts = []
        async for response in runner.run_stream(
            session=session,
            user_input=selected_scenario['spec']
        ):
            if hasattr(response, 'content') and response.content:
                for part in response.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_parts.append(part.text)
                        # Print progress updates
                        if any(keyword in part.text.lower() for keyword in 
                               ['analyzing', 'creating', 'generating', 'building', 'testing', 'committing']):
                            print(f"📍 {part.text[:100]}...")
        
        print(f"\n✅ Development workflow completed!")
        print(f"📄 Full response:")
        print("=" * 60)
        for part in response_parts:
            print(part)
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error during development workflow: {str(e)}")
        print("Note: This demo requires proper ADK setup with API keys.")


def demo_workflow_explanation():
    """Explain how the multi-agent workflow works."""
    
    print("🏗️  Multi-Agent Development Workflow Explanation")
    print("=" * 60)
    
    workflow_steps = [
        {
            "agent": "Spec Reader Agent",
            "role": "Requirements Analyst", 
            "tasks": [
                "Read and parse specification documents",
                "Extract functional and non-functional requirements",
                "Identify technology stack and architecture",
                "Create development plan and component breakdown",
                "Set up project directory structure"
            ]
        },
        {
            "agent": "Code Generator Agent",
            "role": "Senior Developer",
            "tasks": [
                "Implement core functionality based on requirements",
                "Follow coding best practices and standards",
                "Add proper error handling and validation",
                "Include comprehensive documentation",
                "Create modular, maintainable code"
            ]
        },
        {
            "agent": "Test Generator Agent", 
            "role": "Test Engineer",
            "tasks": [
                "Create comprehensive unit tests",
                "Write integration tests for components",
                "Include edge case and error condition tests",
                "Ensure high test coverage (>90%)",
                "Use pytest framework with proper structure"
            ]
        },
        {
            "agent": "Build Agent",
            "role": "Build Engineer", 
            "tasks": [
                "Install project dependencies",
                "Validate syntax and imports",
                "Check project structure",
                "Report build status and issues",
                "Ensure compilation success"
            ]
        },
        {
            "agent": "Test Runner Agent",
            "role": "QA Engineer",
            "tasks": [
                "Execute complete test suite",
                "Analyze test results and coverage",
                "Identify failing tests and causes",
                "Provide recommendations for fixes",
                "Validate code quality standards"
            ]
        },
        {
            "agent": "Git Agent",
            "role": "DevOps Engineer",
            "tasks": [
                "Initialize git repository",
                "Stage and commit all files",
                "Create meaningful commit messages",
                "Set up proper git configuration",
                "Handle version control best practices"
            ]
        }
    ]
    
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n{i}. {step['agent']} ({step['role']})")
        print("   " + "─" * 50)
        for task in step['tasks']:
            print(f"   • {task}")
    
    print(f"\n🔄 Workflow Coordination:")
    print("• Sequential execution ensures each step completes before the next")
    print("• State is passed between agents via output_key mechanism")
    print("• Error handling at each step prevents cascading failures")
    print("• Coordinator agent can handle complex decision-making")
    
    print(f"\n🎯 Benefits of Multi-Agent Approach:")
    print("• Specialized expertise for each development phase")
    print("• Parallel development of different aspects")
    print("• Consistent quality standards across all phases")
    print("• Automated end-to-end development pipeline")
    print("• Reproducible and scalable development process")


if __name__ == "__main__":
    print("Software Development Multi-Agent System")
    print("=" * 50)
    print("Choose an option:")
    print("1. Run interactive development workflow demo")
    print("2. View workflow explanation")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting development workflow demo...")
        print("Note: This requires proper ADK setup with API keys.")
        try:
            asyncio.run(demo_development_workflow())
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user.")
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print("Make sure you have ADK properly installed and configured.")
    elif choice == "2":
        demo_workflow_explanation()
    else:
        print("👋 Goodbye!")