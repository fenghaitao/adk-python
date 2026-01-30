#!/usr/bin/env python3
"""
LightRAG Visual Demonstration
Shows how LightRAG processes documents and builds knowledge graphs
"""

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def visualize_chunking():
    """Visualize how documents are chunked"""
    print_section("STEP 1: Document Chunking")
    
    document = """
    The Agent Development Kit (ADK) is a Python toolkit developed by Google.
    ADK supports multiple AI models including Gemini and OpenAI's GPT.
    LightRAG is a knowledge graph-based RAG system. It extracts entities
    and relationships from documents to improve retrieval quality.
    """
    
    print("\n📄 Original Document:")
    print(document.strip())
    
    print("\n✂️  After Chunking (simplified):")
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │ Chunk 1:                                                 │
    │ "The Agent Development Kit (ADK) is a Python toolkit    │
    │  developed by Google. ADK supports multiple AI models   │
    │  including Gemini and OpenAI's GPT."                    │
    └─────────────────────────────────────────────────────────┘
              ↓ (100 token overlap)
    ┌─────────────────────────────────────────────────────────┐
    │ Chunk 2:                                                 │
    │ "ADK supports multiple AI models including Gemini and   │
    │  OpenAI's GPT. LightRAG is a knowledge graph-based RAG  │
    │  system. It extracts entities and relationships..."     │
    └─────────────────────────────────────────────────────────┘
    """)

def visualize_entity_extraction():
    """Visualize entity and relationship extraction"""
    print_section("STEP 2: Entity & Relationship Extraction")
    
    print("\n🤖 LLM analyzes each chunk and extracts:")
    print("""
    ENTITIES FOUND:
    ┌──────────────────────┬─────────────┬────────────────────────┐
    │ Entity Name          │ Type        │ Description            │
    ├──────────────────────┼─────────────┼────────────────────────┤
    │ ADK                  │ TECHNOLOGY  │ Python toolkit for AI  │
    │ Google               │ ORGANIZATION│ Technology company     │
    │ Gemini               │ PRODUCT     │ AI model by Google     │
    │ OpenAI               │ ORGANIZATION│ AI research company    │
    │ GPT                  │ PRODUCT     │ Language model         │
    │ LightRAG             │ TECHNOLOGY  │ Knowledge graph RAG    │
    └──────────────────────┴─────────────┴────────────────────────┘

    RELATIONSHIPS FOUND:
    ┌──────────────┬──────────────────┬──────────────────────────┐
    │ Source       │ Relationship     │ Target                   │
    ├──────────────┼──────────────────┼──────────────────────────┤
    │ ADK          │ developed_by     │ Google                   │
    │ ADK          │ supports         │ Gemini                   │
    │ ADK          │ supports         │ GPT                      │
    │ GPT          │ created_by       │ OpenAI                   │
    │ Gemini       │ created_by       │ Google                   │
    │ LightRAG     │ type_of          │ RAG system               │
    └──────────────┴──────────────────┴──────────────────────────┘
    """)

def visualize_knowledge_graph():
    """Visualize the resulting knowledge graph"""
    print_section("STEP 3: Knowledge Graph Construction")
    
    print("\n🕸️  Knowledge Graph Structure:")
    print("""
                    ┌──────────┐
                    │  Google  │
                    └─────┬────┘
                          │
              ┌───────────┴───────────┐
              │                       │
         developed_by            created_by
              │                       │
         ┌────▼────┐              ┌──▼───┐
         │   ADK   │              │Gemini│
         └────┬────┘              └──────┘
              │
         ┌────┴────┐
         │         │
      supports  supports
         │         │
    ┌────▼─┐   ┌──▼───┐         ┌────────┐
    │ GPT  │   │Gemini│         │ OpenAI │
    └──────┘   └──────┘         └───┬────┘
                                    │
                              created_by
                                    │
                                ┌───▼──┐
                                │ GPT  │
                                └──────┘

    Another subgraph:
    ┌──────────┐  type_of   ┌────────────┐
    │ LightRAG ├───────────►│ RAG System │
    └──────────┘            └────────────┘
    """)

def visualize_storage():
    """Visualize how data is stored"""
    print_section("STEP 4: Multi-Layer Storage")
    
    print("""
    📦 Storage Architecture:

    ┌─────────────────────────────────────────────────────────────┐
    │                    VECTOR STORAGE                            │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ Entity Embeddings:                                   │   │
    │  │  - "ADK: Python toolkit..." → [0.23, 0.45, ...]    │   │
    │  │  - "Google: Technology company..." → [0.67, ...]    │   │
    │  │                                                       │   │
    │  │ Relationship Embeddings:                             │   │
    │  │  - "ADK developed_by Google" → [0.12, 0.89, ...]   │   │
    │  │                                                       │   │
    │  │ Chunk Embeddings:                                    │   │
    │  │  - "The Agent Development..." → [0.34, 0.78, ...]   │   │
    │  └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                    GRAPH STORAGE                             │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ Nodes:                                               │   │
    │  │  {id: "ADK", type: "TECHNOLOGY", description: ...}  │   │
    │  │  {id: "Google", type: "ORGANIZATION", ...}          │   │
    │  │                                                       │   │
    │  │ Edges:                                               │   │
    │  │  {src: "ADK", tgt: "Google", rel: "developed_by"}   │   │
    │  │  {src: "ADK", tgt: "Gemini", rel: "supports"}       │   │
    │  └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────┐
    │                    KEY-VALUE STORAGE                         │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │ text_chunks:                                         │   │
    │  │  {chunk_id: "abc123", content: "The Agent...", ...} │   │
    │  │                                                       │   │
    │  │ full_docs:                                           │   │
    │  │  {doc_id: "doc001", content: "...", status: ...}    │   │
    │  │                                                       │   │
    │  │ llm_cache:                                           │   │
    │  │  {query_hash: "...", response: "..."}               │   │
    │  └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘
    """)

def visualize_query_modes():
    """Visualize different query modes"""
    print_section("QUERY MODES: How LightRAG Retrieves Information")
    
    print("\n❓ Query: 'What AI models does ADK support?'\n")
    
    print("🔹 NAIVE MODE (Vector Similarity Only):")
    print("""
    1. Generate query embedding
    2. Find similar chunk embeddings
    3. Return matching chunks
    
    Result: "...ADK supports multiple AI models including Gemini and GPT..."
    
    ✓ Fast, simple
    ✗ Doesn't use graph relationships
    """)
    
    print("\n🔶 LOCAL MODE (Entity + Neighbors):")
    print("""
    1. Find entity "ADK" in graph
    2. Get immediate neighbors:
         ADK --[supports]--> Gemini
         ADK --[supports]--> GPT
         ADK --[developed_by]--> Google
    3. Retrieve chunks for ADK, Gemini, GPT
    
    Result: Comprehensive answer with entity relationships
    
    ✓ Uses graph structure
    ✓ Gets connected entities
    ✗ Limited to direct neighbors
    """)
    
    print("\n🔷 GLOBAL MODE (Whole Graph Analysis):")
    print("""
    1. Analyze entire graph structure
    2. Find entity communities/clusters
    3. Generate high-level summaries
    4. Consider global patterns
    
    Result: Thematic answer about AI ecosystem
    
    ✓ Holistic view
    ✓ Finds patterns
    ✗ Slower
    ✗ May miss specific details
    """)
    
    print("\n⭐ HYBRID MODE (Best of Both):")
    print("""
    1. Run LOCAL search (entity neighbors)
    2. Run GLOBAL search (graph patterns)
    3. Combine results
    4. Generate comprehensive answer
    
    Result: Detailed + contextual answer
    
    ✓✓ Best quality
    ✓ Balanced detail and context
    ✗ Slightly slower
    """)

def visualize_query_process():
    """Visualize the complete query process"""
    print_section("COMPLETE QUERY FLOW (Hybrid Mode)")
    
    print("""
    Query: "What does ADK support?"
    
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 1: Query Processing                                     │
    ├─────────────────────────────────────────────────────────────┤
    │ • Generate query embedding                                   │
    │ • Identify key entities: "ADK"                              │
    └─────────────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 2: LOCAL Retrieval                                      │
    ├─────────────────────────────────────────────────────────────┤
    │ Graph Traversal:                                             │
    │   ADK --[supports]--> Gemini                                │
    │   ADK --[supports]--> GPT                                   │
    │   ADK --[developed_by]--> Google                            │
    │                                                              │
    │ Entities: [ADK, Gemini, GPT, Google]                        │
    │ Relations: [supports, developed_by]                         │
    │ Chunks: 5 relevant text chunks                              │
    └─────────────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 3: GLOBAL Retrieval                                     │
    ├─────────────────────────────────────────────────────────────┤
    │ Graph Analysis:                                              │
    │   • AI models cluster: [Gemini, GPT, Claude]                │
    │   • Tech companies: [Google, OpenAI, Anthropic]            │
    │   • Tools/Frameworks: [ADK, LightRAG]                       │
    │                                                              │
    │ Global Context: "ADK is part of AI development ecosystem..." │
    └─────────────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 4: Context Assembly                                     │
    ├─────────────────────────────────────────────────────────────┤
    │ Combined Context:                                            │
    │ ┌─────────────────────────────────────────────────────┐    │
    │ │ Entities & Relations (from LOCAL):                   │    │
    │ │  - ADK supports Gemini                              │    │
    │ │  - ADK supports GPT                                 │    │
    │ │  - ADK developed by Google                          │    │
    │ │                                                       │    │
    │ │ Text Chunks (from LOCAL):                            │    │
    │ │  - "ADK supports multiple AI models..."             │    │
    │ │  - "Gemini is Google's AI model..."                 │    │
    │ │                                                       │    │
    │ │ Global Context (from GLOBAL):                        │    │
    │ │  - "Part of AI development ecosystem"               │    │
    │ │  - "Integrates with major LLM providers"            │    │
    │ └─────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────┘
                            ↓
    ┌─────────────────────────────────────────────────────────────┐
    │ STEP 5: LLM Generation                                       │
    ├─────────────────────────────────────────────────────────────┤
    │ Prompt:                                                      │
    │   System: "Use this knowledge graph context to answer..."   │
    │   Context: [assembled from step 4]                          │
    │   Query: "What does ADK support?"                           │
    │                                                              │
    │ LLM Response:                                                │
    │ "ADK (Agent Development Kit) supports multiple AI models     │
    │  including Google's Gemini and OpenAI's GPT. It was         │
    │  developed by Google as a Python toolkit for building AI    │
    │  agents..."                                                  │
    └─────────────────────────────────────────────────────────────┘
    """)

def main():
    """Run all visualizations"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        LightRAG: Visual Understanding Guide                    ║")
    print("║        How Knowledge Graph RAG Really Works                    ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    visualize_chunking()
    visualize_entity_extraction()
    visualize_knowledge_graph()
    visualize_storage()
    visualize_query_modes()
    visualize_query_process()
    
    print("\n")
    print("="*70)
    print("  Summary: Key Takeaways")
    print("="*70)
    print("""
    1. 📄 Documents are chunked with overlap for context preservation
    
    2. 🤖 LLM extracts entities and relationships from each chunk
    
    3. 🕸️  Knowledge graph connects related entities
    
    4. 💾 Multi-layer storage: vectors + graph + key-value
    
    5. 🔍 Four retrieval modes for different query types
    
    6. ⭐ Hybrid mode combines local + global for best results
    
    7. 🎯 Graph traversal finds connected context, not just similar text
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    💡 Key Advantage: LightRAG understands RELATIONSHIPS between entities,
       not just textual similarity. This enables multi-hop reasoning and
       better context retrieval for complex queries.
    
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)
    
    print("\n📚 For more details, read: UNDERSTANDING_LIGHTRAG.md")
    print("🚀 To try it yourself, run: ./run_lightrag_examples.sh\n")

if __name__ == "__main__":
    main()
