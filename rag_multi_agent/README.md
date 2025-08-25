# Multi-Agent RAG System with Document Indexing and Retrieval

## 🚀 Overview

This example demonstrates a sophisticated **Retrieval-Augmented Generation (RAG) system** using multiple specialized agents that work together to index documents and provide intelligent information retrieval with context-aware responses.

## 🏗️ System Architecture

### **6 Specialized Agents Working Together:**

1. **📚 Document Ingestion Agent** - Processes and indexes documents into the database
2. **🔢 Embedding Agent** - Creates vector embeddings for semantic search
3. **🔍 Query Processing Agent** - Analyzes user queries and determines retrieval strategies
4. **📖 Retrieval Agent** - Finds relevant documents using vector similarity search
5. **✍️ Synthesis Agent** - Combines retrieved information with LLM generation
6. **🎯 RAG Coordinator** - Orchestrates the entire workflow

### **Three Workflow Patterns:**

- **Coordinated Workflow**: Interactive agent coordination for complex queries
- **Sequential Pipeline**: Automated query → analysis → retrieval → synthesis
- **Parallel Processing**: Simultaneous document ingestion and embedding generation

## 🚀 How to Use

### **Method 1: Interactive CLI**
```bash
cd rag_multi_agent
adk run .

# Example interactions:
"Initialize the database and create sample documents about AI, cloud computing, and cybersecurity"
"What are the main types of machine learning and their applications?"
"How can AI improve cybersecurity in cloud environments?"
```

### **Method 2: Web Interface**
```bash
cd rag_multi_agent
adk web . --port 8080
# Open browser and interact with the RAG system
```

### **Method 3: Demo Script**
```bash
cd rag_multi_agent
python demo.py

# Choose from scenarios:
# 1. Document ingestion setup
# 2. AI/ML queries
# 3. Cloud computing questions
# 4. Cybersecurity information
# 5. Cross-domain synthesis
```

## 📋 Key Features

### **Document Management**
- **SQLite Database**: Stores documents, chunks, and embeddings
- **Multiple File Types**: Support for text, markdown, and other formats
- **Metadata Extraction**: Automatic extraction of document properties
- **Deduplication**: Content hash-based duplicate detection
- **Statistics Tracking**: Monitor document collection growth

### **Vector Embeddings**
- **Semantic Chunking**: Intelligent document splitting with overlap
- **Vector Generation**: Creates embeddings for semantic similarity
- **Similarity Search**: Cosine similarity-based document retrieval
- **Scalable Storage**: Efficient embedding storage and retrieval

### **Intelligent Retrieval**
- **Query Analysis**: Understanding user intent and information needs
- **Semantic Search**: Vector-based similarity matching
- **Relevance Ranking**: Scored results with confidence indicators
- **Multi-Document Synthesis**: Combining information from multiple sources

### **Response Generation**
- **Context-Aware Synthesis**: LLM generation augmented with retrieved content
- **Source Attribution**: Clear citations and references
- **Structured Responses**: Well-organized, coherent answers
- **Gap Identification**: Acknowledging limitations in available information

## 🗄️ Database Schema

### **Documents Table**
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    file_path TEXT,
    file_type TEXT,
    content_hash TEXT UNIQUE,
    metadata TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### **Embeddings Table**
```sql
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY,
    document_id INTEGER,
    chunk_index INTEGER,
    chunk_text TEXT,
    embedding_vector TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id)
);
```

### **Queries Table**
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY,
    query_text TEXT NOT NULL,
    retrieved_docs TEXT,
    response TEXT,
    created_at TIMESTAMP
);
```

## 📚 Example Usage Scenarios

### **1. Document Ingestion**
```
"Initialize the RAG system database and create sample documents about AI, 
cloud computing, and cybersecurity. Then index all documents with embeddings."
```

**What happens:**
1. **Document Ingestion Agent** → Creates database, generates sample documents
2. **Embedding Agent** → Splits documents into chunks, generates embeddings
3. **System** → Ready for intelligent querying

### **2. Technical Queries**
```
"What are the main types of machine learning and their applications in different industries?"
```

**What happens:**
1. **Query Processing Agent** → Analyzes query for ML concepts
2. **Retrieval Agent** → Finds relevant ML document chunks
3. **Synthesis Agent** → Combines information into comprehensive response

### **3. Cross-Domain Analysis**
```
"How do AI and machine learning technologies help improve cybersecurity in cloud environments?"
```

**What happens:**
1. **Query Processing Agent** → Identifies multi-domain query (AI + cybersecurity + cloud)
2. **Retrieval Agent** → Searches across multiple document types
3. **Synthesis Agent** → Synthesizes information from different domains

### **4. System Management**
```
"Show me the current status of the RAG system including document statistics."
```

**What happens:**
1. **Document Ingestion Agent** → Retrieves database statistics
2. **System** → Reports document count, embedding progress, recent additions

## 🔧 Technical Implementation

### **Vector Embeddings**
```python
# Mock embedding generation (replace with real embeddings in production)
def create_mock_embedding(text: str) -> List[float]:
    # In production, use:
    # - OpenAI embeddings
    # - Sentence Transformers
    # - Google Universal Sentence Encoder
    # - Cohere embeddings
    pass
```

### **Similarity Search**
```python
# Cosine similarity calculation
similarity = dot_product / (norm_query * norm_chunk)

# Ranking and retrieval
top_results = sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:top_k]
```

### **Document Chunking**
```python
# Overlapping chunks for better context
chunk_size = 500  # tokens
overlap = 50      # token overlap
chunks = create_overlapping_chunks(document, chunk_size, overlap)
```

## 🎯 Advanced Features

### **Query Types Supported**
- **Factual Questions**: "What is machine learning?"
- **Comparative Analysis**: "Compare AWS vs Azure vs GCP"
- **Procedural Queries**: "How to implement API authentication?"
- **Cross-Domain Synthesis**: "AI applications in cybersecurity"

### **Retrieval Strategies**
- **Semantic Similarity**: Vector-based matching
- **Keyword Matching**: Traditional text search
- **Hybrid Retrieval**: Combining multiple approaches
- **Re-ranking**: Post-retrieval relevance optimization

### **Response Quality**
- **Source Citations**: Clear attribution to source documents
- **Confidence Indicators**: Reliability scores for information
- **Gap Identification**: Acknowledging missing information
- **Structured Output**: Well-organized, readable responses

## 🔄 Workflow Examples

### **Document Ingestion Workflow**
```
User Request → Document Ingestion Agent → Database Storage → 
Embedding Agent → Chunk Creation → Vector Generation → 
Ready for Retrieval
```

### **Query Processing Workflow**
```
User Query → Query Processing Agent → Intent Analysis → 
Retrieval Agent → Vector Search → Document Ranking → 
Synthesis Agent → Response Generation → User Response
```

### **Parallel Processing Workflow**
```
Multiple Documents → Parallel Ingestion Team → 
Simultaneous Processing → Faster Indexing → 
Reduced Processing Time
```

## 🛠️ Customization Options

### **Adding New Document Types**
```python
def process_pdf_document(file_path: str) -> str:
    # Add PDF processing logic
    pass

def process_word_document(file_path: str) -> str:
    # Add Word document processing
    pass
```

### **Custom Embedding Models**
```python
from sentence_transformers import SentenceTransformer

def create_real_embedding(text: str) -> List[float]:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text)
    return embedding.tolist()
```

### **Advanced Retrieval**
```python
def hybrid_search(query: str, alpha: float = 0.7) -> List[Dict]:
    # Combine vector search with keyword search
    vector_results = vector_search(query)
    keyword_results = keyword_search(query)
    return combine_results(vector_results, keyword_results, alpha)
```

## 📊 Performance Considerations

### **Scalability**
- **Database Indexing**: Proper indexes on frequently queried columns
- **Embedding Storage**: Efficient vector storage and retrieval
- **Caching**: Cache frequently accessed embeddings and results
- **Batch Processing**: Process multiple documents simultaneously

### **Quality Optimization**
- **Chunk Size Tuning**: Optimize for your document types
- **Embedding Model Selection**: Choose appropriate models for your domain
- **Retrieval Thresholds**: Tune similarity thresholds for quality
- **Response Validation**: Implement quality checks for generated responses

## 🔍 Troubleshooting

### **Common Issues**
1. **No Documents Found**: Ensure database is initialized and documents are ingested
2. **Poor Retrieval Quality**: Check embedding generation and similarity thresholds
3. **Slow Performance**: Consider database indexing and caching strategies
4. **Memory Issues**: Optimize chunk sizes and batch processing

### **Debug Commands**
```bash
# Check database status
"Show me the current document statistics"

# Verify embeddings
"How many documents have embeddings generated?"

# Test retrieval
"Search for documents about [specific topic]"
```

This RAG system demonstrates how multiple specialized agents can work together to create a sophisticated document indexing and retrieval system that provides intelligent, context-aware responses to user queries.