#!/usr/bin/env python3
"""
Sample Usage Examples for RAG Multi-Agent System
===============================================

This script provides practical examples of how to use the RAG system
for different types of queries and document management tasks.
"""

import asyncio
from google.adk.runners import InMemoryRunner
from agent import root_agent


async def sample_document_ingestion():
    """Example: Document ingestion and indexing workflow."""
    
    print("📚 Document Ingestion Example")
    print("=" * 40)
    
    runner = InMemoryRunner(agent=root_agent, app_name="rag_sample")
    session = await runner.session_service.create_session(
        app_name="rag_sample", user_id="sample_user"
    )
    
    # Step 1: Initialize the system
    print("Step 1: Initializing RAG system...")
    async for event in runner.run_async(
        user_id="sample_user",
        session_id=session.id,
        new_message_text="Initialize the RAG system database and create sample documents about AI, cloud computing, and cybersecurity."
    ):
        if event.content and event.content.parts:
            print(f"Response: {event.content.parts[0].text[:200]}...")
    
    # Step 2: Check system status
    print("\nStep 2: Checking system status...")
    async for event in runner.run_async(
        user_id="sample_user",
        session_id=session.id,
        new_message_text="Show me the current document statistics and system status."
    ):
        if event.content and event.content.parts:
            print(f"Status: {event.content.parts[0].text[:200]}...")


async def sample_technical_queries():
    """Example: Technical question answering."""
    
    print("\n🔍 Technical Query Examples")
    print("=" * 40)
    
    runner = InMemoryRunner(agent=root_agent, app_name="rag_sample")
    session = await runner.session_service.create_session(
        app_name="rag_sample", user_id="sample_user"
    )
    
    queries = [
        "What are the main types of machine learning and their applications?",
        "Explain the different cloud service models (IaaS, PaaS, SaaS).",
        "What are the most common cybersecurity threats organizations face?",
        "How can AI and machine learning improve cybersecurity in cloud environments?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 50)
        
        async for event in runner.run_async(
            user_id="sample_user",
            session_id=session.id,
            new_message_text=query
        ):
            if event.content and event.content.parts:
                response = event.content.parts[0].text
                print(f"Answer: {response[:300]}...")
                if len(response) > 300:
                    print("(Response truncated for display)")


async def sample_cross_domain_analysis():
    """Example: Cross-domain information synthesis."""
    
    print("\n🔄 Cross-Domain Analysis Example")
    print("=" * 40)
    
    runner = InMemoryRunner(agent=root_agent, app_name="rag_sample")
    session = await runner.session_service.create_session(
        app_name="rag_sample", user_id="sample_user"
    )
    
    # Complex query that requires information from multiple domains
    complex_query = """
    I'm planning to implement an AI-powered cybersecurity solution for a cloud-native application. 
    Can you provide insights on:
    1. How machine learning can detect security threats
    2. Cloud security best practices for AI applications
    3. Integration challenges between AI systems and cloud security tools
    """
    
    print(f"Complex Query: {complex_query}")
    print("-" * 50)
    
    async for event in runner.run_async(
        user_id="sample_user",
        session_id=session.id,
        new_message_text=complex_query
    ):
        if event.content and event.content.parts:
            response = event.content.parts[0].text
            print(f"Comprehensive Answer: {response}")


def demonstrate_query_types():
    """Demonstrate different types of queries the system can handle."""
    
    print("\n💡 Query Types and Examples")
    print("=" * 40)
    
    query_types = {
        "Factual Questions": [
            "What is machine learning?",
            "Define cloud computing.",
            "What is a DDoS attack?",
            "Explain what APIs are."
        ],
        
        "Comparative Analysis": [
            "Compare supervised vs unsupervised learning.",
            "What are the differences between public and private clouds?",
            "Compare symmetric vs asymmetric encryption.",
            "AWS vs Azure vs Google Cloud - which is better?"
        ],
        
        "Procedural Questions": [
            "How do I implement OAuth2 authentication?",
            "What are the steps to migrate to the cloud?",
            "How can I set up a machine learning pipeline?",
            "What's the process for conducting a security audit?"
        ],
        
        "Cross-Domain Synthesis": [
            "How does AI improve cloud security?",
            "What role does machine learning play in DevOps?",
            "How do blockchain and cloud computing intersect?",
            "AI applications in cybersecurity threat detection."
        ],
        
        "Best Practices": [
            "What are cloud security best practices?",
            "How to structure a machine learning project?",
            "Cybersecurity guidelines for small businesses.",
            "API design best practices for scalability."
        ],
        
        "Troubleshooting": [
            "Why is my cloud application slow?",
            "How to debug machine learning model performance?",
            "Common causes of security breaches.",
            "API rate limiting issues and solutions."
        ]
    }
    
    for category, examples in query_types.items():
        print(f"\n📂 {category}")
        print("   " + "-" * 30)
        for example in examples:
            print(f"   • \"{example}\"")


def show_system_commands():
    """Show system management commands."""
    
    print("\n🛠️ System Management Commands")
    print("=" * 40)
    
    commands = {
        "Database Management": [
            "Initialize the RAG system database",
            "Show document statistics and system status",
            "Create sample documents for testing",
            "Clear all documents from the database"
        ],
        
        "Document Operations": [
            "Add the file 'document.pdf' to the knowledge base",
            "Index all documents in the 'docs' folder",
            "Generate embeddings for all documents",
            "Show recently added documents"
        ],
        
        "Search and Retrieval": [
            "Search for documents about machine learning",
            "Find the most similar documents to this query",
            "Show retrieval statistics for recent queries",
            "Test the embedding quality for document chunks"
        ],
        
        "System Diagnostics": [
            "Check the health of the RAG system",
            "Show embedding generation progress",
            "Display query processing statistics",
            "Validate database integrity"
        ]
    }
    
    for category, command_list in commands.items():
        print(f"\n📂 {category}")
        print("   " + "-" * 30)
        for command in command_list:
            print(f"   • \"{command}\"")


async def interactive_demo():
    """Interactive demo allowing user to try different queries."""
    
    print("\n🎮 Interactive RAG Demo")
    print("=" * 30)
    print("Enter your queries to test the RAG system.")
    print("Type 'quit' to exit, 'help' for examples.")
    
    runner = InMemoryRunner(agent=root_agent, app_name="rag_interactive")
    session = await runner.session_service.create_session(
        app_name="rag_interactive", user_id="interactive_user"
    )
    
    # Initialize the system first
    print("\nInitializing RAG system...")
    async for event in runner.run_async(
        user_id="interactive_user",
        session_id=session.id,
        new_message_text="Initialize the database and create sample documents."
    ):
        if event.content and event.content.parts:
            print("✅ System initialized!")
            break
    
    while True:
        try:
            user_input = input("\nYour query: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                demonstrate_query_types()
                continue
            
            if not user_input:
                continue
            
            print("🤖 Processing...")
            async for event in runner.run_async(
                user_id="interactive_user",
                session_id=session.id,
                new_message_text=user_input
            ):
                if event.content and event.content.parts:
                    print(f"\nResponse: {event.content.parts[0].text}")
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("RAG Multi-Agent System - Sample Usage")
    print("=" * 45)
    print("Choose an option:")
    print("1. Document ingestion example")
    print("2. Technical query examples")
    print("3. Cross-domain analysis example")
    print("4. Show query types and examples")
    print("5. Show system management commands")
    print("6. Interactive demo")
    print("7. Exit")
    
    choice = input("\nEnter choice (1-7): ").strip()
    
    try:
        if choice == "1":
            asyncio.run(sample_document_ingestion())
        elif choice == "2":
            asyncio.run(sample_technical_queries())
        elif choice == "3":
            asyncio.run(sample_cross_domain_analysis())
        elif choice == "4":
            demonstrate_query_types()
        elif choice == "5":
            show_system_commands()
        elif choice == "6":
            asyncio.run(interactive_demo())
        else:
            print("👋 Goodbye!")
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure you have ADK properly installed and configured.")