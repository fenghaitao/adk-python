#!/usr/bin/env python3
"""
Run All RAG Examples Script

This script provides a menu to run different RAG examples and
demonstrates the capabilities of each approach.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_setup():
    """Check if the environment is properly set up."""
    print("🔍 Checking setup...")
    
    # Check if we're in the right directory
    if not Path("files_rag_agent.py").exists():
        print("❌ Please run this script from the core_rag_example directory")
        return False
    
    # Check basic dependencies
    try:
        import google.adk
        print("✅ ADK is installed")
    except ImportError:
        print("❌ ADK not installed. Run: pip install -r requirements.txt")
        return False
    
    return True


def run_example(script_name, description):
    """Run a specific example script."""
    print(f"\n🚀 Running: {description}")
    print("=" * 60)
    
    try:
        # Run the script
        result = subprocess.run([sys.executable, script_name], check=True)
        print(f"\n✅ {description} completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with error code {e.returncode}")
        print("   Check the error messages above for details.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  {description} interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Unexpected error running {description}: {e}")


def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("🎯 Core RAG Examples Menu")
    print("=" * 60)
    
    examples = [
        {
            "key": "1",
            "script": "files_rag_agent.py",
            "title": "Local Files RAG Agent",
            "description": "RAG with local documents (no cloud setup required)",
            "requirements": "✅ No cloud setup needed"
        },
        {
            "key": "2", 
            "script": "basic_rag_agent.py",
            "title": "Basic Vertex AI RAG Agent",
            "description": "Simple RAG using Vertex AI RAG corpus",
            "requirements": "🔧 Requires: RAG_CORPUS environment variable"
        },
        {
            "key": "3",
            "script": "memory_rag_agent.py", 
            "title": "Memory-Powered RAG Agent",
            "description": "RAG with persistent memory using Vertex AI",
            "requirements": "🔧 Requires: RAG_CORPUS environment variable"
        },
        {
            "key": "4",
            "script": "multi_tool_rag_agent.py",
            "title": "Multi-Tool RAG Agent", 
            "description": "RAG combining multiple tools and search methods",
            "requirements": "🔧 Requires: Full cloud setup (RAG_CORPUS, VERTEX_AI_SEARCH_DATASTORE)"
        },
        {
            "key": "s",
            "script": "setup_environment.py",
            "title": "Setup Environment",
            "description": "Check setup and create configuration files",
            "requirements": "🛠️  Setup and configuration helper"
        }
    ]
    
    for example in examples:
        print(f"{example['key']}. {example['title']}")
        print(f"   {example['description']}")
        print(f"   {example['requirements']}")
        print()
    
    print("q. Quit")
    print("=" * 60)


def show_environment_status():
    """Show current environment configuration status."""
    print("\n📊 Environment Status:")
    print("-" * 30)
    
    env_vars = [
        ("GOOGLE_CLOUD_PROJECT", "Google Cloud Project ID"),
        ("RAG_CORPUS", "Vertex AI RAG Corpus"),
        ("VERTEX_AI_SEARCH_DATASTORE", "Vertex AI Search Datastore"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Service Account Key"),
    ]
    
    for var, description in env_vars:
        value = os.environ.get(var)
        if value:
            # Show first 20 chars for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")
    
    print()


def main():
    """Main function."""
    print("🎉 Welcome to Core RAG Examples!")
    print("This interactive menu helps you explore different RAG approaches in ADK.")
    
    if not check_setup():
        print("\n❌ Setup check failed. Please fix the issues above.")
        return
    
    while True:
        show_environment_status()
        show_menu()
        
        choice = input("👉 Select an option: ").strip().lower()
        
        if choice == 'q' or choice == 'quit':
            print("👋 Goodbye!")
            break
            
        elif choice == '1':
            run_example("files_rag_agent.py", "Local Files RAG Agent")
            
        elif choice == '2':
            if not os.environ.get("RAG_CORPUS"):
                print("\n⚠️  Warning: RAG_CORPUS not set in environment")
                print("   This example may not work without proper configuration.")
                proceed = input("   Continue anyway? (y/N): ").strip().lower()
                if proceed != 'y':
                    continue
            run_example("basic_rag_agent.py", "Basic Vertex AI RAG Agent")
            
        elif choice == '3':
            if not os.environ.get("RAG_CORPUS"):
                print("\n⚠️  Warning: RAG_CORPUS not set in environment")
                print("   This example may not work without proper configuration.")
                proceed = input("   Continue anyway? (y/N): ").strip().lower()
                if proceed != 'y':
                    continue
            run_example("memory_rag_agent.py", "Memory-Powered RAG Agent")
            
        elif choice == '4':
            missing = []
            if not os.environ.get("RAG_CORPUS"):
                missing.append("RAG_CORPUS")
            if not os.environ.get("VERTEX_AI_SEARCH_DATASTORE"):
                missing.append("VERTEX_AI_SEARCH_DATASTORE")
                
            if missing:
                print(f"\n⚠️  Warning: Missing environment variables: {', '.join(missing)}")
                print("   This example may not work without proper configuration.")
                proceed = input("   Continue anyway? (y/N): ").strip().lower()
                if proceed != 'y':
                    continue
            run_example("multi_tool_rag_agent.py", "Multi-Tool RAG Agent")
            
        elif choice == 's' or choice == 'setup':
            run_example("setup_environment.py", "Environment Setup")
            
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\n⏸️  Press Enter to continue...")


if __name__ == "__main__":
    main()