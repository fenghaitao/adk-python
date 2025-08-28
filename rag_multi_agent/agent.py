#!/usr/bin/env python3
"""
Multi-Agent RAG System with Document Indexing and Retrieval
===========================================================

This example demonstrates a sophisticated multi-agent RAG system that:
1. Document Ingestion Agent - Processes and indexes documents
2. Embedding Agent - Creates vector embeddings for documents
3. Database Agent - Manages document storage and retrieval
4. Query Processing Agent - Analyzes user queries and retrieval strategies
5. Retrieval Agent - Finds relevant documents using vector similarity
6. Synthesis Agent - Combines retrieved information with LLM generation
7. Coordinator Agent - Orchestrates the entire RAG workflow

The system can index various document types and provide intelligent retrieval
with context-aware responses.
"""

import os
import json
import sqlite3
import hashlib
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.tools.function_tool import FunctionTool
from google.adk.models.google_llm import Gemini
from google.genai import types


# =============================================================================
# DATABASE AND STORAGE UTILITIES
# =============================================================================

def initialize_document_database(db_path: str = "rag_documents.db") -> str:
    """Initialize SQLite database for document storage."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                file_path TEXT,
                file_type TEXT,
                content_hash TEXT UNIQUE,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER,
                chunk_text TEXT,
                embedding_vector TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        """)
        
        # Create queries table for tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                retrieved_docs TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        return f"Database initialized successfully at {db_path}"
    except Exception as e:
        return f"Error initializing database: {str(e)}"


def ingest_document(file_path: str, title: str = None, metadata: Dict = None) -> str:
    """Ingest a document into the database."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate content hash for deduplication
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract title from filename if not provided
        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0]
        
        # Determine file type
        file_type = os.path.splitext(file_path)[1].lower()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        metadata.update({
            "file_size": len(content),
            "word_count": len(content.split()),
            "ingestion_date": datetime.now().isoformat()
        })
        
        # Insert into database
        conn = sqlite3.connect("rag_documents.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO documents (title, content, file_path, file_type, content_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, content, file_path, file_type, content_hash, json.dumps(metadata)))
            
            document_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return f"Document '{title}' ingested successfully with ID {document_id}"
            
        except sqlite3.IntegrityError:
            conn.close()
            return f"Document '{title}' already exists in database (duplicate content hash)"
            
    except Exception as e:
        return f"Error ingesting document: {str(e)}"


def chunk_document(document_id: int, chunk_size: int = 500, overlap: int = 50) -> str:
    """Split document into chunks for embedding."""
    try:
        conn = sqlite3.connect("rag_documents.db")
        cursor = conn.cursor()
        
        # Get document content
        cursor.execute("SELECT content FROM documents WHERE id = ?", (document_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return f"Document with ID {document_id} not found"
        
        content = result[0]
        words = content.split()
        chunks = []
        
        # Create overlapping chunks
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        # Store chunks (clear existing chunks first)
        cursor.execute("DELETE FROM embeddings WHERE document_id = ?", (document_id,))
        
        for idx, chunk in enumerate(chunks):
            cursor.execute("""
                INSERT INTO embeddings (document_id, chunk_index, chunk_text, embedding_vector)
                VALUES (?, ?, ?, ?)
            """, (document_id, idx, chunk, ""))  # Embedding vector will be added later
        
        conn.commit()
        conn.close()
        
        return f"Document {document_id} split into {len(chunks)} chunks"
        
    except Exception as e:
        return f"Error chunking document: {str(e)}"


def create_mock_embedding(text: str) -> List[float]:
    """Create a mock embedding vector for demonstration purposes."""
    # In a real implementation, you would use a proper embedding model
    # like OpenAI embeddings, Sentence Transformers, etc.
    
    # Simple hash-based mock embedding (384 dimensions)
    hash_obj = hashlib.md5(text.encode())
    hash_bytes = hash_obj.digest()
    
    # Convert to float vector
    embedding = []
    for i in range(0, len(hash_bytes), 4):
        chunk = hash_bytes[i:i+4]
        if len(chunk) == 4:
            value = int.from_bytes(chunk, byteorder='big') / (2**32)
            embedding.append(value)
    
    # Pad to 384 dimensions
    while len(embedding) < 384:
        embedding.append(0.0)
    
    return embedding[:384]


def generate_embeddings(document_id: int) -> str:
    """Generate embeddings for document chunks."""
    try:
        conn = sqlite3.connect("rag_documents.db")
        cursor = conn.cursor()
        
        # Get chunks without embeddings
        cursor.execute("""
            SELECT id, chunk_text FROM embeddings 
            WHERE document_id = ? AND embedding_vector = ''
        """, (document_id,))
        
        chunks = cursor.fetchall()
        
        if not chunks:
            conn.close()
            return f"No chunks found for document {document_id} or embeddings already exist"
        
        # Generate embeddings for each chunk
        for chunk_id, chunk_text in chunks:
            embedding = create_mock_embedding(chunk_text)
            embedding_json = json.dumps(embedding)
            
            cursor.execute("""
                UPDATE embeddings SET embedding_vector = ? WHERE id = ?
            """, (embedding_json, chunk_id))
        
        conn.commit()
        conn.close()
        
        return f"Generated embeddings for {len(chunks)} chunks in document {document_id}"
        
    except Exception as e:
        return f"Error generating embeddings: {str(e)}"


def search_similar_documents(query: str, top_k: int = 5) -> str:
    """Search for similar documents using vector similarity."""
    try:
        # Generate embedding for query
        query_embedding = create_mock_embedding(query)
        
        conn = sqlite3.connect("rag_documents.db")
        cursor = conn.cursor()
        
        # Get all chunks with embeddings
        cursor.execute("""
            SELECT e.id, e.document_id, e.chunk_text, e.embedding_vector, d.title
            FROM embeddings e
            JOIN documents d ON e.document_id = d.id
            WHERE e.embedding_vector != ''
        """)
        
        chunks = cursor.fetchall()
        
        if not chunks:
            conn.close()
            return "No embedded documents found in database"
        
        # Calculate similarities
        similarities = []
        for chunk_id, doc_id, chunk_text, embedding_json, doc_title in chunks:
            try:
                chunk_embedding = json.loads(embedding_json)
                
                # Calculate cosine similarity
                dot_product = np.dot(query_embedding, chunk_embedding)
                norm_query = np.linalg.norm(query_embedding)
                norm_chunk = np.linalg.norm(chunk_embedding)
                
                if norm_query > 0 and norm_chunk > 0:
                    similarity = dot_product / (norm_query * norm_chunk)
                else:
                    similarity = 0.0
                
                similarities.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "document_title": doc_title,
                    "chunk_text": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                    "similarity": similarity
                })
            except:
                continue
        
        # Sort by similarity and get top k
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        top_results = similarities[:top_k]
        
        conn.close()
        
        # Format results
        result_text = f"Found {len(top_results)} similar documents for query: '{query}'\n\n"
        for i, result in enumerate(top_results, 1):
            result_text += f"{i}. Document: {result['document_title']}\n"
            result_text += f"   Similarity: {result['similarity']:.4f}\n"
            result_text += f"   Content: {result['chunk_text']}\n\n"
        
        return result_text
        
    except Exception as e:
        return f"Error searching documents: {str(e)}"


def get_document_statistics() -> str:
    """Get statistics about the document database."""
    try:
        conn = sqlite3.connect("rag_documents.db")
        cursor = conn.cursor()
        
        # Count documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        # Count chunks
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        chunk_count = cursor.fetchone()[0]
        
        # Count embedded chunks
        cursor.execute("SELECT COUNT(*) FROM embeddings WHERE embedding_vector != ''")
        embedded_count = cursor.fetchone()[0]
        
        # Get recent documents
        cursor.execute("""
            SELECT title, created_at FROM documents 
            ORDER BY created_at DESC LIMIT 5
        """)
        recent_docs = cursor.fetchall()
        
        conn.close()
        
        stats = f"Document Database Statistics:\n"
        stats += f"- Total Documents: {doc_count}\n"
        stats += f"- Total Chunks: {chunk_count}\n"
        stats += f"- Embedded Chunks: {embedded_count}\n"
        stats += f"- Embedding Progress: {embedded_count}/{chunk_count} ({embedded_count/chunk_count*100:.1f}%)\n\n"
        
        if recent_docs:
            stats += "Recent Documents:\n"
            for title, created_at in recent_docs:
                stats += f"- {title} (added: {created_at})\n"
        
        return stats
        
    except Exception as e:
        return f"Error getting statistics: {str(e)}"


def create_sample_documents() -> str:
    """Create sample documents for demonstration."""
    try:
        # Create sample documents directory
        os.makedirs("sample_docs", exist_ok=True)
        
        # Sample document 1: AI and Machine Learning
        doc1_content = """
        Artificial Intelligence and Machine Learning: A Comprehensive Overview
        
        Artificial Intelligence (AI) represents one of the most transformative technologies of our time. 
        Machine Learning, a subset of AI, enables computers to learn and improve from experience without 
        being explicitly programmed for every task.
        
        Key concepts in machine learning include:
        
        1. Supervised Learning: Training models on labeled data to make predictions on new, unseen data.
        Examples include classification (predicting categories) and regression (predicting continuous values).
        
        2. Unsupervised Learning: Finding patterns in data without labeled examples. This includes 
        clustering (grouping similar data points) and dimensionality reduction.
        
        3. Reinforcement Learning: Learning through interaction with an environment, receiving rewards 
        or penalties for actions taken.
        
        Deep Learning, using neural networks with multiple layers, has revolutionized fields like 
        computer vision, natural language processing, and speech recognition.
        
        Applications of AI and ML span across industries:
        - Healthcare: Medical diagnosis, drug discovery, personalized treatment
        - Finance: Fraud detection, algorithmic trading, risk assessment
        - Transportation: Autonomous vehicles, route optimization
        - Technology: Recommendation systems, search engines, virtual assistants
        
        The future of AI promises even more advanced capabilities, including artificial general 
        intelligence (AGI) that could match or exceed human cognitive abilities across all domains.
        """
        
        # Sample document 2: Cloud Computing
        doc2_content = """
        Cloud Computing: Transforming Modern IT Infrastructure
        
        Cloud computing has fundamentally changed how organizations deploy, manage, and scale their 
        IT infrastructure. By providing on-demand access to computing resources over the internet, 
        cloud computing offers unprecedented flexibility and cost efficiency.
        
        The three main service models are:
        
        1. Infrastructure as a Service (IaaS): Provides virtualized computing resources including 
        servers, storage, and networking. Examples: Amazon EC2, Google Compute Engine, Azure VMs.
        
        2. Platform as a Service (PaaS): Offers a platform for developing, running, and managing 
        applications without dealing with underlying infrastructure. Examples: Google App Engine, 
        Heroku, Azure App Service.
        
        3. Software as a Service (SaaS): Delivers software applications over the internet on a 
        subscription basis. Examples: Salesforce, Microsoft 365, Google Workspace.
        
        Deployment models include:
        - Public Cloud: Services offered over the public internet and shared across organizations
        - Private Cloud: Cloud infrastructure operated solely for a single organization
        - Hybrid Cloud: Combination of public and private clouds
        - Multi-cloud: Use of multiple cloud computing services from different providers
        
        Benefits of cloud computing:
        - Cost Efficiency: Pay-as-you-use model reduces capital expenditure
        - Scalability: Easily scale resources up or down based on demand
        - Accessibility: Access services from anywhere with internet connectivity
        - Reliability: Built-in redundancy and disaster recovery capabilities
        - Innovation: Faster deployment of new applications and services
        
        Major cloud providers include Amazon Web Services (AWS), Microsoft Azure, Google Cloud 
        Platform (GCP), and IBM Cloud, each offering comprehensive suites of services.
        """
        
        # Sample document 3: Cybersecurity
        doc3_content = """
        Cybersecurity: Protecting Digital Assets in the Modern Era
        
        Cybersecurity has become a critical concern as our world becomes increasingly digital. 
        Organizations and individuals face evolving threats that require comprehensive security 
        strategies and constant vigilance.
        
        Common types of cyber threats include:
        
        1. Malware: Malicious software designed to damage, disrupt, or gain unauthorized access 
        to computer systems. Types include viruses, worms, trojans, ransomware, and spyware.
        
        2. Phishing: Fraudulent attempts to obtain sensitive information by disguising as 
        trustworthy entities in electronic communications.
        
        3. Social Engineering: Psychological manipulation of people to divulge confidential 
        information or perform actions that compromise security.
        
        4. Advanced Persistent Threats (APTs): Prolonged and targeted cyberattacks where 
        attackers gain access to networks and remain undetected for extended periods.
        
        5. Denial of Service (DoS) and Distributed Denial of Service (DDoS): Attacks that 
        make online services unavailable by overwhelming them with traffic.
        
        Essential cybersecurity practices:
        - Multi-factor Authentication (MFA): Adding extra layers of security beyond passwords
        - Regular Software Updates: Patching vulnerabilities in operating systems and applications
        - Network Segmentation: Isolating critical systems from general network traffic
        - Employee Training: Educating staff about security best practices and threat recognition
        - Incident Response Planning: Preparing for and responding to security breaches
        - Data Encryption: Protecting sensitive data both in transit and at rest
        
        Emerging cybersecurity challenges include securing IoT devices, protecting cloud 
        environments, defending against AI-powered attacks, and ensuring privacy compliance 
        with regulations like GDPR and CCPA.
        
        The cybersecurity workforce shortage remains a significant challenge, with millions 
        of unfilled positions globally, highlighting the need for continued investment in 
        cybersecurity education and training.
        """
        
        # Write sample documents
        with open("sample_docs/ai_machine_learning.txt", "w") as f:
            f.write(doc1_content)
        
        with open("sample_docs/cloud_computing.txt", "w") as f:
            f.write(doc2_content)
        
        with open("sample_docs/cybersecurity.txt", "w") as f:
            f.write(doc3_content)
        
        return "Created 3 sample documents: ai_machine_learning.txt, cloud_computing.txt, cybersecurity.txt"
        
    except Exception as e:
        return f"Error creating sample documents: {str(e)}"


# =============================================================================
# SPECIALIZED AGENTS FOR RAG WORKFLOW
# =============================================================================

# 1. Document Ingestion Agent
document_ingestion_agent = LlmAgent(
    name="document_ingestion_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Processes and ingests documents into the RAG system",
    instruction="""
    You are a Document Ingestion Specialist responsible for processing and indexing documents 
    into the RAG system database.
    
    Your responsibilities:
    1. Initialize the document database if needed
    2. Ingest documents from file paths provided by users
    3. Create sample documents for demonstration purposes
    4. Provide statistics about the document collection
    5. Ensure proper document formatting and metadata extraction
    
    When users want to add documents:
    - Use initialize_document_database to set up the database
    - Use ingest_document to add files to the system
    - Use create_sample_documents to generate demo content
    - Use get_document_statistics to show current status
    
    Always provide clear feedback about the ingestion process and any issues encountered.
    """,
    tools=[
        FunctionTool(initialize_document_database),
        FunctionTool(ingest_document),
        FunctionTool(create_sample_documents),
        FunctionTool(get_document_statistics)
    ],
    output_key="ingestion_results"
)

# 2. Embedding Agent
embedding_agent = LlmAgent(
    name="embedding_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Creates vector embeddings for documents and chunks",
    instruction="""
    You are an Embedding Specialist responsible for creating vector representations of documents 
    for semantic search and retrieval.
    
    Your responsibilities:
    1. Split documents into manageable chunks for embedding
    2. Generate vector embeddings for each chunk
    3. Optimize chunk size and overlap for better retrieval
    4. Monitor embedding progress and quality
    
    Process for embedding documents:
    - Use chunk_document to split documents into overlapping chunks
    - Use generate_embeddings to create vector representations
    - Consider optimal chunk sizes (typically 300-800 tokens)
    - Ensure proper overlap between chunks (10-20% of chunk size)
    
    Based on ingestion results: {ingestion_results}
    
    Process all newly ingested documents for embedding generation.
    """,
    tools=[
        FunctionTool(chunk_document),
        FunctionTool(generate_embeddings),
        FunctionTool(get_document_statistics)
    ],
    output_key="embedding_results"
)

# 3. Query Processing Agent
query_processing_agent = LlmAgent(
    name="query_processing_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Analyzes user queries and determines retrieval strategies",
    instruction="""
    You are a Query Processing Specialist responsible for analyzing user queries and determining 
    the best retrieval strategy.
    
    Your responsibilities:
    1. Analyze user queries for intent and key concepts
    2. Determine appropriate search parameters (top_k, similarity thresholds)
    3. Reformulate queries for better retrieval if needed
    4. Identify the type of information being requested
    
    Query analysis considerations:
    - Factual questions: Focus on specific information retrieval
    - Conceptual questions: Broader semantic search
    - Comparative questions: Retrieve multiple relevant sources
    - How-to questions: Look for procedural information
    
    For the user query, determine:
    - Key search terms and concepts
    - Appropriate number of documents to retrieve (top_k)
    - Whether query reformulation would improve results
    
    Provide a clear analysis of the query and recommended retrieval strategy.
    """,
    output_key="query_analysis"
)

# 4. Retrieval Agent
retrieval_agent = LlmAgent(
    name="retrieval_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Retrieves relevant documents using vector similarity search",
    instruction="""
    You are a Document Retrieval Specialist responsible for finding the most relevant documents 
    for user queries using vector similarity search.
    
    Your responsibilities:
    1. Execute similarity search based on query analysis
    2. Retrieve top-k most relevant document chunks
    3. Evaluate retrieval quality and relevance
    4. Provide context about retrieved documents
    
    Based on query analysis: {query_analysis}
    
    Use the search_similar_documents tool to find relevant information.
    Consider the recommended retrieval parameters from the query analysis.
    
    Evaluate the retrieved results for:
    - Relevance to the user's question
    - Diversity of information sources
    - Completeness of information
    - Quality of similarity scores
    
    Provide a summary of retrieved documents and their relevance.
    """,
    tools=[
        FunctionTool(search_similar_documents),
        FunctionTool(get_document_statistics)
    ],
    output_key="retrieval_results"
)

# 5. Synthesis Agent
synthesis_agent = LlmAgent(
    name="synthesis_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Synthesizes retrieved information with LLM generation",
    instruction="""
    You are an Information Synthesis Specialist responsible for combining retrieved documents 
    with language model generation to provide comprehensive, accurate responses.
    
    Your responsibilities:
    1. Analyze retrieved documents for relevant information
    2. Synthesize information from multiple sources
    3. Generate coherent, well-structured responses
    4. Cite sources and provide context
    5. Identify gaps in available information
    
    Based on retrieval results: {retrieval_results}
    
    Synthesis guidelines:
    - Prioritize information from highly relevant sources
    - Combine information from multiple documents when appropriate
    - Maintain accuracy and avoid hallucination
    - Provide clear citations to source documents
    - Acknowledge limitations or gaps in available information
    - Structure responses logically with clear sections
    
    Generate a comprehensive response that addresses the user's query using the retrieved information.
    Include source citations and confidence indicators where appropriate.
    """,
    output_key="synthesized_response"
)

# 6. RAG Coordinator Agent
rag_coordinator_agent = LlmAgent(
    name="rag_coordinator",
    model=Gemini(model="gemini-1.5-flash"),
    description="Coordinates the entire RAG workflow from query to response",
    instruction="""
    You are the RAG System Coordinator responsible for orchestrating the complete 
    Retrieval-Augmented Generation workflow.
    
    You manage a team of specialized agents:
    - document_ingestion_agent: Processes and indexes documents
    - embedding_agent: Creates vector embeddings for semantic search
    - query_processing_agent: Analyzes queries and determines retrieval strategy
    - retrieval_agent: Finds relevant documents using vector similarity
    - synthesis_agent: Combines retrieved information with LLM generation
    
    Workflow coordination:
    1. For document ingestion requests: Route to document_ingestion_agent and embedding_agent
    2. For user queries: Route through query_processing_agent → retrieval_agent → synthesis_agent
    3. For system status: Use document_ingestion_agent for statistics
    
    Always explain which agents you're using and why, and provide clear status updates 
    throughout the RAG process.
    """,
    sub_agents=[
        document_ingestion_agent,
        embedding_agent,
        query_processing_agent,
        retrieval_agent,
        synthesis_agent
    ]
)

# =============================================================================
# SEQUENTIAL RAG PIPELINE
# =============================================================================

# Create separate agent instances for the sequential pipeline
pipeline_query_processor = LlmAgent(
    name="pipeline_query_processor",
    model=Gemini(model="gemini-1.5-flash"),
    description="Analyzes user queries for the pipeline",
    instruction=query_processing_agent.instruction,
    output_key="query_analysis"
)

pipeline_retrieval_agent = LlmAgent(
    name="pipeline_retrieval_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Retrieves documents for the pipeline",
    instruction=retrieval_agent.instruction,
    tools=retrieval_agent.tools,
    output_key="retrieval_results"
)

pipeline_synthesis_agent = LlmAgent(
    name="pipeline_synthesis_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Synthesizes responses for the pipeline",
    instruction=synthesis_agent.instruction,
    output_key="synthesized_response"
)

# Sequential RAG pipeline for automated query processing
rag_pipeline = SequentialAgent(
    name="automated_rag_pipeline",
    description="Automated RAG pipeline: Query Analysis → Retrieval → Synthesis",
    sub_agents=[
        pipeline_query_processor,
        pipeline_retrieval_agent,
        pipeline_synthesis_agent
    ]
)

# =============================================================================
# PARALLEL DOCUMENT PROCESSING PIPELINE
# =============================================================================

# Parallel processing for multiple document ingestion
parallel_ingestion_agent = LlmAgent(
    name="parallel_ingestion_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Handles document ingestion in parallel",
    instruction=document_ingestion_agent.instruction,
    tools=document_ingestion_agent.tools,
    output_key="parallel_ingestion_results"
)

parallel_embedding_agent = LlmAgent(
    name="parallel_embedding_agent",
    model=Gemini(model="gemini-1.5-flash"),
    description="Handles embedding generation in parallel",
    instruction=embedding_agent.instruction,
    tools=embedding_agent.tools,
    output_key="parallel_embedding_results"
)

# Parallel document processing team
document_processing_team = ParallelAgent(
    name="document_processing_team",
    description="Parallel document ingestion and embedding generation",
    sub_agents=[parallel_ingestion_agent, parallel_embedding_agent]
)

# =============================================================================
# ROOT AGENT - MAIN ENTRY POINT
# =============================================================================

root_agent = LlmAgent(
    name="rag_system",
    model=Gemini(model="gemini-1.5-flash"),
    description="Multi-Agent RAG System with Document Indexing and Retrieval",
    instruction="""
    You are the Multi-Agent RAG (Retrieval-Augmented Generation) System that can index documents 
    and provide intelligent information retrieval with context-aware responses.
    
    You have three main workflow options:
    
    1. **RAG Coordinator** (rag_coordinator): Interactive workflow for complex queries and 
       document management with full agent coordination.
    
    2. **Automated RAG Pipeline** (rag_pipeline): Streamlined sequential processing for 
       standard query → retrieval → response workflows.
    
    3. **Document Processing Team** (document_processing_team): Parallel processing for 
       efficient document ingestion and embedding generation.
    
    Capabilities:
    - Document ingestion from various file types
    - Vector embedding generation for semantic search
    - Intelligent query processing and analysis
    - Similarity-based document retrieval
    - Context-aware response synthesis
    - Database management and statistics
    
    When users interact with you:
    - For document ingestion: Use the coordinator or processing team
    - For questions/queries: Use the coordinator or automated pipeline
    - For system status: Use the coordinator for comprehensive information
    
    Always explain which workflow you're using and provide clear, helpful responses.
    """,
    sub_agents=[rag_coordinator_agent, rag_pipeline, document_processing_team]
)

# Export the root agent for ADK
agent = root_agent