#!/usr/bin/env python3
"""Basic usage examples for ChromaDB Memory skill.

This file demonstrates common usage patterns without requiring
actual execution (no dependencies needed to read).
"""

# Example 1: Index memories from a directory
def example_index():
    """Index markdown documents into ChromaDB."""
    from chromadb_memory import MemoryIndexer
    
    indexer = MemoryIndexer(
        memory_dir="openspec-memories",
        persist_directory=".chromadb"
    )
    
    result = indexer.index_memories()
    print(f"Indexed {result['files_indexed']} files")
    print(f"Created {result['chunks_created']} chunks")


# Example 2: Search for relevant passages
def example_search():
    """Search indexed memories."""
    from chromadb_memory import MemoryRetriever
    import dspy
    
    # Configure DSPy (required)
    dspy.settings.configure(lm=dspy.LM("openai/gpt-4"))
    
    # Create retriever
    retriever = MemoryRetriever(k=3)
    
    # Search
    result = retriever(
        task_description="How to implement timer in DML?",
        category="DML"
    )
    
    # Print results
    for i, passage in enumerate(result.passages, 1):
        print(f"\n--- Passage {i} ---")
        print(passage)


# Example 3: RAG (Retrieval-Augmented Generation)
def example_rag():
    """Use retrieval with generation."""
    import dspy
    from chromadb_memory import MemoryRetriever
    
    class RAGModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.retriever = MemoryRetriever(k=3)
            self.generate = dspy.ChainOfThought("context, query -> answer")
        
        def forward(self, query):
            # Retrieve context
            retrieval = self.retriever(query)
            context = "\n\n".join(retrieval.passages)
            
            # Generate answer
            return self.generate(context=context, query=query)
    
    # Configure and use
    dspy.settings.configure(lm=dspy.LM("openai/gpt-4"))
    rag = RAGModule()
    
    result = rag("How do I create a timer event in DML?")
    print(result.answer)


# Example 4: Category-filtered search
def example_category_search():
    """Search within specific categories."""
    from chromadb_memory import MemoryRetriever
    import dspy
    
    dspy.settings.configure(lm=dspy.LM("openai/gpt-4"))
    retriever = MemoryRetriever(k=5)
    
    # Search DML category
    dml_results = retriever(
        task_description="register access patterns",
        category="DML"
    )
    
    # Search Test category
    test_results = retriever(
        task_description="test register access",
        category="Test"
    )
    
    print(f"DML results: {len(dml_results.passages)}")
    print(f"Test results: {len(test_results.passages)}")


# Example 5: Force reindexing
def example_force_reindex():
    """Force reindex even if collection exists."""
    from chromadb_memory import MemoryIndexer
    
    indexer = MemoryIndexer(
        memory_dir="openspec-memories",
        persist_directory=".chromadb"
    )
    
    # Force reindex (deletes existing and rebuilds)
    result = indexer.index_memories(force_reindex=True)
    print(f"Reindexed: {result['status']}")


# Example 6: Get statistics
def example_stats():
    """Get indexing statistics."""
    from chromadb_memory import MemoryIndexer
    
    indexer = MemoryIndexer(
        memory_dir="openspec-memories",
        persist_directory=".chromadb"
    )
    
    stats = indexer.get_stats()
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Unique files: {stats['unique_files']}")
    print("Categories:")
    for category, count in stats['categories'].items():
        print(f"  {category}: {count} chunks")


# Example 7: Custom chunk size
def example_custom_chunking():
    """Use custom chunking parameters."""
    from chromadb_memory import MemoryIndexer
    
    class CustomIndexer(MemoryIndexer):
        def chunk_text(self, text, chunk_size=300, overlap=30):
            # Smaller chunks for more granular retrieval
            return super().chunk_text(text, chunk_size, overlap)
    
    indexer = CustomIndexer(
        memory_dir="docs",
        persist_directory=".custom_db"
    )
    
    result = indexer.index_memories()
    print(f"Created {result['chunks_created']} smaller chunks")


if __name__ == "__main__":
    print(__doc__)
    print("\nAvailable examples:")
    print("  1. example_index() - Index memories")
    print("  2. example_search() - Search memories")
    print("  3. example_rag() - RAG with generation")
    print("  4. example_category_search() - Category filtering")
    print("  5. example_force_reindex() - Force reindex")
    print("  6. example_stats() - View statistics")
    print("  7. example_custom_chunking() - Custom chunking")
    print("\nNote: These are example code snippets.")
    print("Use the CLI for actual operations:")
    print("  uv run scripts/chromadb_memory.py --help")
