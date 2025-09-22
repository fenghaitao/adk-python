#!/usr/bin/env python3

"""Test script for the integrated Spec-Kit and Simics workflow with natural LLM detection."""

import asyncio
import os
import sys
from pathlib import Path

# Add ADK to path
current_dir = Path(__file__).parent
adk_src_dir = current_dir.parent.parent.parent / "src"
if adk_src_dir.exists():
    sys.path.insert(0, str(adk_src_dir))

try:
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from agent import root_agent
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure ADK is properly installed and accessible.")
    sys.exit(1)


async def test_hardware_simulation_project_workflow():
    """Test complete workflow for a hardware simulation project."""
    print("=== Testing Hardware Simulation Project Workflow ===")
    
    runner = InMemoryRunner(root_agent)
    
    # Create session first
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user", 
        session_id="test_session_1"
    )
    
    # Test 1: Create a specification for a hardware simulation project
    print("\n1. Creating specification for hardware simulation project...")
    hardware_spec_request = "/specify Create an x86 processor simulator with memory management unit and PCI device support for embedded systems development"
    
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_1", 
            new_message=types.Content(parts=[types.Part(text=hardware_spec_request)])
        ):
            events.append(event)
        
        if events:
            final_event = events[-1]
            if hasattr(final_event, 'content') and final_event.content:
                response_text = str(final_event.content)
                print(f"Specification result: {response_text[:200]}...")
            else:
                print("Specification completed but no content found")
        else:
            print("No events received")
    except Exception as e:
        print(f"Error in specification: {e}")
    
    # Test 2: Generate implementation plan
    print("\n2. Generating implementation plan...")
    plan_request = "/plan Use Simics simulation environment with x86 architecture, include memory controller and PCI bus simulation"
    
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_1",
            new_message=types.Content(parts=[types.Part(text=plan_request)])
        ):
            events.append(event)
        
        if events and events[-1].content:
            print(f"Plan result: {str(events[-1].content)[:200]}...")
    except Exception as e:
        print(f"Error in planning: {e}")
    
    # Test 3: Generate tasks
    print("\n3. Generating tasks...")
    tasks_request = "/tasks Break down into TDD tasks including Simics environment setup and hardware simulation validation"
    
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_1",
            new_message=types.Content(parts=[types.Part(text=tasks_request)])
        ):
            events.append(event)
        
        if events and events[-1].content:
            print(f"Tasks result: {str(events[-1].content)[:200]}...")
    except Exception as e:
        print(f"Error in tasks: {e}")


async def test_software_project_workflow():
    """Test workflow for a software project (should not trigger Simics)."""
    print("\n=== Testing Software Project Workflow ===")
    
    runner = InMemoryRunner(root_agent)
    
    # Create session first
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user",
        session_id="test_session_2"
    )
    
    # Test: Create a specification for a software project
    print("\n1. Creating specification for software project...")
    software_spec_request = "/specify Create a web-based user authentication system with email/password login and JWT tokens"
    
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_2",
            new_message=types.Content(parts=[types.Part(text=software_spec_request)])
        ):
            events.append(event)
        
        if events and events[-1].content:
            print(f"Software specification result: {str(events[-1].content)[:200]}...")
    except Exception as e:
        print(f"Error in software specification: {e}")


async def test_llm_hardware_detection():
    """Test the LLM's natural hardware simulation detection capability."""
    print("\n=== Testing LLM Hardware Detection ===")
    
    runner = InMemoryRunner(root_agent)
    
    # Create sessions first
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user",
        session_id="test_session_3"
    )
    await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="test_user", 
        session_id="test_session_4"
    )
    
    # Test LLM hardware simulation detection through natural workflow
    print("\nTesting LLM detection with hardware simulation content...")
    hardware_request = "/specify Create a RISC-V processor simulation with memory controller and peripheral devices for firmware development"
    
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_3",
            new_message=types.Content(parts=[types.Part(text=hardware_request)])
        ):
            events.append(event)
        
        if events and events[-1].content:
            response_text = str(events[-1].content).lower()
            
            # Check if LLM detected hardware simulation elements
            detected_simics = "simics" in response_text
            detected_hardware = any(term in response_text for term in ["risc-v", "processor", "simulation", "firmware"])
            
            print(f"Simics mentioned: {detected_simics}")
            print(f"Hardware terms detected: {detected_hardware}")
            print(f"Response preview: {str(events[-1].content)[:200]}...")
        
    except Exception as e:
        print(f"Error in LLM hardware detection test: {e}")
    
    print("\nTesting LLM with software-only content...")
    software_request = "/specify Build a REST API with FastAPI and PostgreSQL database for user management"
    
    try:
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session_4",
            new_message=types.Content(parts=[types.Part(text=software_request)])
        ):
            events.append(event)
        
        if events and events[-1].content:
            response_text = str(events[-1].content).lower()
            
            # Should not detect hardware simulation elements
            detected_simics = "simics" in response_text
            print(f"Simics mentioned in software project: {detected_simics}")
        
    except Exception as e:
        print(f"Error in software detection test: {e}")


def check_folder_setup():
    """Check if ~/.adk and ~/.specify folders are set up correctly."""
    print("=== Checking Folder Setup ===")
    
    adk_dir = Path.home() / ".adk"
    specify_dir = Path.home() / ".specify"
    
    print(f"~/.adk exists: {adk_dir.exists()}")
    if adk_dir.exists():
        print(f"  Commands directory: {(adk_dir / 'commands').exists()}")
        commands = list((adk_dir / 'commands').glob('*.md')) if (adk_dir / 'commands').exists() else []
        print(f"  Available commands: {[cmd.stem for cmd in commands]}")
    
    print(f"~/.specify exists: {specify_dir.exists()}")
    if specify_dir.exists():
        print(f"  Templates directory: {(specify_dir / 'templates').exists()}")
        templates = list((specify_dir / 'templates').glob('*.md')) if (specify_dir / 'templates').exists() else []
        print(f"  Available templates: {[tmpl.stem for tmpl in templates]}")
        print("  Note: No project metadata storage - LLM handles detection naturally")


async def main():
    """Run all tests."""
    print("Starting Spec-Kit Integration Tests...")
    
    # Check folder setup
    check_folder_setup()
    
    # Test LLM hardware detection
    await test_llm_hardware_detection()
    
    # Test hardware simulation workflow
    await test_hardware_simulation_project_workflow()
    
    # Test software workflow  
    await test_software_project_workflow()
    
    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    asyncio.run(main())