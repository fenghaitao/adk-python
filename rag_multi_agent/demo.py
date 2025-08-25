#!/usr/bin/env python3
"""
RAG Multi-Agent System Demo
===========================

This script demonstrates the multi-agent RAG system capabilities:
1. Document ingestion and indexing
2. Vector embedding generation
3. Intelligent query processing
4. Semantic document retrieval
5. Context-aware response synthesis
"""

import asyncio
import os
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService

# Import our RAG multi-agent system
from agent import root_agent


async def demo_rag_system():
    """Demonstrate the RAG multi-agent system capabilities."""
    
    print("🤖 Multi-Agent RAG System Demo")
    print("=" * 50)
    
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
            "title": "📚 Document Ingestion Setup",
            "query": "Initialize the RAG system database and create sample documents about AI, cloud computing, and cybersecurity. Then index all documents with embeddings.",
            "description": "Sets up the document database, creates sample documents, and generates embeddings for semantic search."
        },
        {
            "title": "🔍 AI and Machine Learning Query",
            "query": "What are the main types of machine learning and their applications in different industries?",
            "description": "Tests retrieval and synthesis for AI/ML concepts from indexed documents."
        },
        {
            "title": "☁️ Cloud Computing Query",
            "query": "Explain the different cloud service models and their benefits for businesses.",
            "description": "Retrieves information about IaaS, PaaS, SaaS and cloud computing benefits."
        },
        {
            "title": "🔒 Cybersecurity Query",
            "query": "What are the most common cyber threats and how can organizations protect themselves?",
            "description": "Searches for cybersecurity threats and protection strategies."
        },
        {
            "title": "🔄 Cross-Domain Query",
            "query": "How do AI and machine learning technologies help improve cybersecurity in cloud environments?",
            "description": "Tests retrieval across multiple documents to synthesize information from different domains."
        },
        {
            "title": "📊 System Status Check",
            "query": "Show me the current status of the RAG system including document statistics and database information.",
            "description": "Displays system statistics and document collection status."
        }
    ]
    
    print("Available RAG system demonstrations:")
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
    print(f"Query: {selected_scenario['query']}")
    print(f"\n🔄 Processing with RAG multi-agent system...")
    
    try:
        # Create session
        session = await session_service.create_session(
            app_name="rag_demo",
            user_id="demo_user"
        )
        
        # Run the query
        response_parts = []
        async for response in runner.run_stream(
            session=session,
            user_input=selected_scenario['query']
        ):
            if hasattr(response, 'content') and response.content:
                for part in response.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_parts.append(part.text)
                        # Print progress updates
                        if any(keyword in part.text.lower() for keyword in 
                               ['processing', 'analyzing', 'retrieving', 'synthesizing', 'indexing']):
                            print(f"📍 {part.text[:100]}...")
        
        print(f"\n✅ RAG processing completed!")
        print(f"📄 Full response:")
        print("=" * 60)
        for part in response_parts:
            print(part)
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Error during RAG processing: {str(e)}")
        print("Note: This demo requires proper ADK setup with API keys.")


def explain_rag_architecture():
    """Explain the RAG multi-agent architecture."""
    
    print("🏗️  RAG Multi-Agent System Architecture")
    print("=" * 50)
    
    agents = [
        {
            "name": "Document Ingestion Agent",
            "role": "Document Processor",
            "responsibilities": [
                "Initialize document database (SQLite)",
                "Ingest documents from various file types",
                "Extract metadata and content",
                "Create sample documents for demo",
                "Provide document collection statistics"
            ]
        },
        {
            "name": "Embedding Agent", 
            "role": "Vector Specialist",
            "responsibilities": [
                "Split documents into semantic chunks",
                "Generate vector embeddings for chunks",
                "Optimize chunk size and overlap",
                "Store embeddings in database",
                "Monitor embedding generation progress"
            ]
        },
        {
            "name": "Query Processing Agent",
            "role": "Query Analyst", 
            "responsibilities": [
                "Analyze user queries for intent",
                "Identify key concepts and search terms",
                "Determine optimal retrieval parameters",
                "Reformulate queries if needed",
                "Classify query types (factual, conceptual, etc.)"
            ]
        },
        {
            "name": "Retrieval Agent",
            "role": "Search Specialist",
            "responsibilities": [
                "Execute vector similarity search",
                "Rank documents by relevance",
                "Retrieve top-k most similar chunks",
                "Evaluate retrieval quality",
                "Provide retrieval context and metadata"
            ]
        },
        {
            "name": "Synthesis Agent",
            "role": "Response Generator",
            "responsibilities": [
                "Analyze retrieved document chunks",
                "Synthesize information from multiple sources",
                "Generate coherent, structured responses",
                "Provide source citations",
                "Identify information gaps"
            ]
        },
        {
            "name": "RAG Coordinator",
            "role": "Workflow Orchestrator",
            "responsibilities": [
                "Coordinate between all specialized agents",
                "Route requests to appropriate agents",
                "Manage workflow state and context",
                "Handle complex multi-step processes",
                "Provide status updates and error handling"
            ]
        }
    ]
    
    for i, agent in enumerate(agents, 1):
        print(f"\n{i}. {agent['name']} ({agent['role']})")
        print("   " + "─" * 50)
        for responsibility in agent['responsibilities']:
            print(f"   • {responsibility}")
    
    print(f"\n🔄 Workflow Patterns:")
    print("• **Coordinated Workflow**: Interactive agent coordination for complex queries")
    print("• **Sequential Pipeline**: Automated query → analysis → retrieval → synthesis")
    print("• **Parallel Processing**: Simultaneous document ingestion and embedding")
    
    print(f"\n🗄️ Database Schema:")
    print("• **Documents Table**: Stores document content, metadata, and file information")
    print("• **Embeddings Table**: Stores document chunks and their vector representations")
    print("• **Queries Table**: Tracks user queries and system responses")
    
    print(f"\n🎯 Key Features:")
    print("• **Vector Similarity Search**: Semantic document retrieval using embeddings")
    print("• **Chunking Strategy**: Overlapping chunks for better context preservation")
    print("• **Multi-Source Synthesis**: Combines information from multiple documents")
    print("• **Source Attribution**: Provides citations and confidence indicators")
    print("• **Scalable Architecture**: Handles large document collections efficiently")


def show_usage_examples():
    """Show practical usage examples for the RAG system."""
    
    print("💡 RAG System Usage Examples")
    print("=" * 40)
    
    examples = [
        {
            "category": "Document Management",
            "examples": [
                "Initialize the database and create sample documents",
                "Add the file 'research_paper.pdf' to the knowledge base",
                "Show me statistics about the current document collection",
                "Index all documents in the 'company_docs' folder"
            ]
        },
        {
            "category": "Technical Queries",
            "examples": [
                "What are the best practices for cloud security?",
                "Explain the differences between supervised and unsupervised learning",
                "How do microservices architecture patterns work?",
                "What are the latest trends in cybersecurity?"
            ]
        },
        {
            "category": "Comparative Analysis",
            "examples": [
                "Compare AWS, Azure, and Google Cloud Platform services",
                "What are the pros and cons of different machine learning algorithms?",
                "How do traditional databases compare to NoSQL solutions?",
                "Compare different authentication methods for web applications"
            ]
        },
        {
            "category": "Cross-Domain Queries",
            "examples": [
                "How can AI improve cybersecurity in cloud environments?",
                "What role does machine learning play in modern DevOps practices?",
                "How do blockchain technologies impact cloud computing?",
                "What are the security implications of edge computing?"
            ]
        },
        {
            "category": "Procedural Questions",
            "examples": [
                "How do I implement a secure API authentication system?",
                "What steps are needed to migrate to a cloud-native architecture?",
                "How can I set up a machine learning pipeline?",
                "What's the process for conducting a security audit?"
            ]
        }
    ]
    
    for category_info in examples:
        print(f"\n📂 {category_info['category']}")
        print("   " + "─" * 30)
        for example in category_info['examples']:
            print(f"   • \"{example}\"")
    
    print(f"\n🔧 System Commands:")
    print("   • \"Show system status and document statistics\"")
    print("   • \"Initialize the RAG database\"")
    print("   • \"Create sample documents for testing\"")
    print("   • \"Generate embeddings for all documents\"")


if __name__ == "__main__":
    print("Multi-Agent RAG System Demo")
    print("=" * 30)
    print("Choose an option:")
    print("1. Run interactive RAG system demo")
    print("2. View RAG system architecture explanation")
    print("3. Show usage examples")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting RAG system demo...")
        print("Note: This requires proper ADK setup with API keys.")
        try:
            asyncio.run(demo_rag_system())
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user.")
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print("Make sure you have ADK properly installed and configured.")
    elif choice == "2":
        explain_rag_architecture()
    elif choice == "3":
        show_usage_examples()
    else:
        print("👋 Goodbye!")