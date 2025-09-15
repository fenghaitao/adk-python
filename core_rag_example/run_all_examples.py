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
            "title": "Local Files RAG + Web Search Agent",
            "description": "RAG with local documents combined with web search capabilities",
            "requirements": "✅ No cloud setup needed for basic functionality"
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
        ("GOOGLE_CLOUD_PROJECT", "Google Cloud Project ID (optional for web search)"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Service Account Key (optional)"),
    ]
    
    for var, description in env_vars:
        value = os.environ.get(var)
        if value:
            # Show first 20 chars for security
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"ℹ️  {var}: Not set ({description})")
    
    print()


def main():
    """Main function."""
    print("🎉 Welcome to Core RAG Examples!")
    print("This script will automatically run the Local Files RAG + Web Search Agent example.")
    
    # Show environment status
    show_environment_status()
    
    # Automatically run the files_rag_agent example
    print("🚀 Automatically running the Local Files RAG + Web Search Agent example...")
    run_example("files_rag_agent.py", "Local Files RAG + Web Search Agent")
    
    print("\n✨ Example execution completed!")


if __name__ == "__main__":
    main()