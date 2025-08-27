#!/usr/bin/env python3
"""
Local Files RAG Agent Example using FilesRetrieval

This example demonstrates how to use ADK's FilesRetrieval for local file-based RAG
without requiring cloud services. Perfect for testing or when working with local documents.
"""

import os
from pathlib import Path
from google.adk.agents.llm_agent import Agent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval


def create_sample_documents():
    """Creates sample documents for testing if they don't exist."""
    docs_dir = Path("core_rag_example/sample_documents")
    docs_dir.mkdir(exist_ok=True)
    
    sample_docs = {
        "ai_basics.txt": """
# Artificial Intelligence Basics

Artificial Intelligence (AI) is a branch of computer science that aims to create 
intelligent machines that can perform tasks that typically require human intelligence.

## Types of AI:
1. **Narrow AI**: AI designed for specific tasks (like image recognition)
2. **General AI**: AI with human-level intelligence across all domains
3. **Super AI**: AI that surpasses human intelligence

## Machine Learning:
Machine Learning is a subset of AI that enables computers to learn and improve 
from experience without being explicitly programmed.

### Types of Machine Learning:
- **Supervised Learning**: Learning with labeled data
- **Unsupervised Learning**: Finding patterns in unlabeled data
- **Reinforcement Learning**: Learning through trial and error

## Applications:
- Natural Language Processing
- Computer Vision
- Robotics
- Autonomous Vehicles
- Healthcare Diagnostics
""",
        
        "cloud_computing.txt": """
# Cloud Computing Guide

Cloud computing is the delivery of computing services over the internet ("the cloud") 
to offer faster innovation, flexible resources, and economies of scale.

## Service Models:
1. **IaaS (Infrastructure as a Service)**: Virtual machines, storage, networks
2. **PaaS (Platform as a Service)**: Development platforms and tools
3. **SaaS (Software as a Service)**: Complete applications over the internet

## Deployment Models:
- **Public Cloud**: Services offered over the public internet
- **Private Cloud**: Services maintained on a private network
- **Hybrid Cloud**: Combination of public and private clouds

## Benefits:
- Cost reduction
- Scalability
- Flexibility
- Automatic updates
- Disaster recovery
- Global accessibility

## Major Providers:
- Amazon Web Services (AWS)
- Microsoft Azure
- Google Cloud Platform (GCP)
- IBM Cloud
""",
        
        "cybersecurity.txt": """
# Cybersecurity Fundamentals

Cybersecurity is the practice of protecting systems, networks, and programs 
from digital attacks.

## Common Threats:
1. **Malware**: Viruses, worms, trojans, ransomware
2. **Phishing**: Fraudulent emails to steal sensitive information
3. **Social Engineering**: Manipulating people to divulge information
4. **DDoS Attacks**: Overwhelming systems with traffic
5. **Insider Threats**: Threats from within the organization

## Security Principles:
- **Confidentiality**: Ensuring information is accessible only to authorized users
- **Integrity**: Maintaining accuracy and completeness of data
- **Availability**: Ensuring systems are accessible when needed

## Best Practices:
- Use strong, unique passwords
- Enable two-factor authentication
- Keep software updated
- Regular security training
- Backup data regularly
- Network segmentation
- Incident response planning

## Security Tools:
- Firewalls
- Antivirus software
- Intrusion detection systems
- Security information and event management (SIEM)
- Vulnerability scanners
""",
        
        "python_programming.txt": """
# Python Programming Guide

Python is a high-level, interpreted programming language known for its 
simplicity and readability.

## Key Features:
- Easy to learn and use
- Extensive standard library
- Cross-platform compatibility
- Large community support
- Versatile applications

## Common Use Cases:
1. **Web Development**: Django, Flask frameworks
2. **Data Science**: NumPy, Pandas, Matplotlib
3. **Machine Learning**: Scikit-learn, TensorFlow, PyTorch
4. **Automation**: Scripting and task automation
5. **Desktop Applications**: Tkinter, PyQt

## Basic Syntax:
```python
# Variables
name = "Python"
version = 3.9

# Functions
def greet(name):
    return f"Hello, {name}!"

# Classes
class Calculator:
    def add(self, a, b):
        return a + b
```

## Popular Libraries:
- **NumPy**: Numerical computing
- **Pandas**: Data manipulation
- **Requests**: HTTP library
- **Beautiful Soup**: Web scraping
- **Matplotlib**: Data visualization
"""
    }
    
    for filename, content in sample_docs.items():
        file_path = docs_dir / filename
        if not file_path.exists():
            file_path.write_text(content.strip())
            print(f"📄 Created sample document: {filename}")
    
    return docs_dir


def create_files_rag_agent(documents_path):
    """Creates a RAG agent using local files retrieval."""
    
    # Configure the Files Retrieval tool
    files_retrieval_tool = FilesRetrieval(
        name="search_local_documents",
        description=(
            "Use this tool to search through local documents and files "
            "to find relevant information. This searches through text files, "
            "documentation, and other local resources."
        ),
        # Path to the directory containing documents
        file_paths=[str(documents_path)],
        # Number of top results to return
        top_k=3,
        # Chunk size for document processing
        chunk_size=1000,
        # Overlap between chunks
        chunk_overlap=200,
    )
    
    # Create the agent
    agent = Agent(
        model="gemini-2.0-flash-001",
        name="files_rag_agent",
        instruction=(
            "You are a helpful AI assistant with access to local documents. "
            "When users ask questions, use the search_local_documents tool to "
            "find relevant information from the available files, then provide "
            "comprehensive answers based on the retrieved content.\n\n"
            
            "Available document topics include:\n"
            "- Artificial Intelligence and Machine Learning\n"
            "- Cloud Computing\n"
            "- Cybersecurity\n"
            "- Python Programming\n\n"
            
            "Always:\n"
            "- Search the documents first before answering\n"
            "- Cite which documents provided the information\n"
            "- Combine information from multiple sources when relevant\n"
            "- Be clear about what information comes from the documents vs. general knowledge"
        ),
        tools=[files_retrieval_tool],
    )
    
    return agent


def main():
    """Main function to run the files-based RAG agent."""
    print("📁 Starting Local Files RAG Agent Example")
    print("=" * 50)
    
    try:
        # Create sample documents
        print("📚 Setting up sample documents...")
        docs_path = create_sample_documents()
        print(f"✅ Documents ready in: {docs_path}")
        print()
        
        # Create the agent
        agent = create_files_rag_agent(docs_path)
        print("✅ Files RAG agent created successfully!")
        print()
        
        # Show available documents
        print("📋 Available documents:")
        for doc_file in docs_path.glob("*.txt"):
            print(f"   - {doc_file.name}")
        print()
        
        # Example queries
        example_queries = [
            "What are the different types of machine learning?",
            "What are the benefits of cloud computing?",
            "What are common cybersecurity threats?",
            "How is Python used in data science?",
            "Compare supervised and unsupervised learning",
            "What security tools are mentioned in the documents?",
        ]
        
        print("💡 Example queries you can try:")
        for i, query in enumerate(example_queries, 1):
            print(f"   {i}. {query}")
        print()
        
        # Interactive mode
        print("💬 Interactive mode - Ask questions about the documents!")
        print("   Type 'docs' to see available documents, or 'quit' to exit.")
        print("-" * 50)
        
        while True:
            user_input = input("\n📖 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'docs':
                print("\n📋 Available documents:")
                for doc_file in docs_path.glob("*.txt"):
                    print(f"   - {doc_file.name}")
                continue
                
            if user_input.lower() == 'examples':
                print("\n💡 Example queries:")
                for i, query in enumerate(example_queries, 1):
                    print(f"   {i}. {query}")
                continue
                
            if not user_input:
                continue
                
            try:
                print("\n🔍 Searching local documents...")
                response = agent.run(user_input)
                print(f"\n🤖 Agent Response:\n{response}")
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
                print("   Please check that the sample documents exist and try again.")
                
    except Exception as e:
        print(f"❌ Error setting up files RAG agent: {e}")
        print("   Please check your installation and try again.")


if __name__ == "__main__":
    main()