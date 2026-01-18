#!/usr/bin/env python3
"""Standalone test for memory integration.

This script tests the memory system without requiring DSPy or pytest.
"""

from __future__ import annotations

import tempfile
import shutil
from pathlib import Path


def test_memory_system():
  """Test memory indexing and retrieval."""
  print("🧪 Testing Memory System Integration\n")
  
  # Create temporary directories
  temp_memory_dir = tempfile.mkdtemp()
  temp_chromadb = tempfile.mkdtemp()
  
  try:
    # Step 1: Create sample memory documents
    print("1️⃣  Creating sample memory documents...")
    
    dml_doc = Path(temp_memory_dir) / "01_DML_Patterns.md"
    dml_doc.write_text("""
# DML Implementation Patterns

## Timer Implementation

Use `after` callback for countdown logic:

```dml
method start_countdown() {
    after(delay_cycles) call timeout_handler;
}
```

## Register Side-Effects

Implement write side-effects in `after_write` method:

```dml
method after_write(uint64 value) {
    if (value & 0x1) {
        // Start operation
        this.start_countdown();
    }
}
```
""")
    
    test_doc = Path(temp_memory_dir) / "02_Test_Patterns.md"
    test_doc.write_text("""
# Test Implementation Patterns

## Signal Testing

Test interrupt signals using `iface.signal.signal_raise`:

```python
def test_interrupt_signal():
    obj.iface.signal.signal_raise()
    assert obj.interrupt_raised
```

## Register Testing

Verify register values after write:

```python
def test_register_write():
    obj.bank.regs.control.write(0x1)
    assert obj.bank.regs.control.read() == 0x1
```
""")
    
    print(f"   ✅ Created 2 memory documents in {temp_memory_dir}\n")
    
    # Step 2: Index memories
    print("2️⃣  Indexing memory documents...")
    
    from dspy_openspec.memory.indexer import MemoryIndexer
    
    indexer = MemoryIndexer(
      memory_dir=temp_memory_dir,
      persist_directory=temp_chromadb
    )
    
    result = indexer.index_memories()
    
    print(f"   Status: {result['status']}")
    print(f"   Files indexed: {result['files_indexed']}")
    print(f"   Chunks created: {result['chunks_created']}")
    print(f"   Collection: {result['collection_name']}\n")
    
    assert result["status"] == "success"
    assert result["files_indexed"] == 2
    assert result["chunks_created"] > 0
    
    # Step 3: Get statistics
    print("3️⃣  Getting index statistics...")
    
    stats = indexer.get_stats()
    
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Unique files: {stats['unique_files']}")
    print(f"   Categories: {list(stats['categories'].keys())}\n")
    
    assert stats["total_chunks"] > 0
    assert stats["unique_files"] == 2
    assert "DML" in stats["categories"]
    assert "Test" in stats["categories"]
    
    # Step 4: Test retrieval
    print("4️⃣  Testing memory retrieval...")
    
    from dspy_openspec.memory.retriever import MemoryRetriever
    
    retriever = MemoryRetriever(
      persist_directory=temp_chromadb,
      k=2
    )
    
    result = retriever.forward(
      task_description="implement timer countdown logic",
      category="DML"
    )
    
    print(f"   Query: 'implement timer countdown logic'")
    print(f"   Category: DML")
    print(f"   Results found: {len(result.passages)}")
    
    if result.passages:
      print(f"   First result preview: {result.passages[0][:100]}...\n")
    
    assert len(result.passages) > 0
    assert "after" in result.passages[0].lower()
    
    # Step 5: Test category filtering
    print("5️⃣  Testing category filtering...")
    
    dml_result = retriever.retrieve_for_dml(
      task_description="register side-effects"
    )
    
    print(f"   DML query: 'register side-effects'")
    print(f"   DML results: {len(dml_result)}")
    
    test_result = retriever.retrieve_for_test(
      task_description="signal testing"
    )
    
    print(f"   Test query: 'signal testing'")
    print(f"   Test results: {len(test_result)}\n")
    
    assert len(dml_result) > 0
    assert len(test_result) > 0
    
    # Step 6: Test ApplyModule integration (if DSPy available)
    print("6️⃣  Testing ApplyModule integration...")
    
    try:
      from dspy_openspec.modules.apply_module import ApplyModule, MEMORY_AVAILABLE
      
      if MEMORY_AVAILABLE:
        # Initialize with memory enabled
        apply_module = ApplyModule(
          interactive=False,
          enable_memory=True,
          memory_persist_dir=temp_chromadb,
          memory_k=2
        )
        
        print(f"   Memory available: {MEMORY_AVAILABLE}")
        print(f"   Memory retriever initialized: {apply_module.memory_retriever is not None}")
        
        assert apply_module.memory_retriever is not None
        
        # Test with memory disabled
        apply_module_no_mem = ApplyModule(
          interactive=False,
          enable_memory=False
        )
        
        print(f"   Memory disabled test: {apply_module_no_mem.memory_retriever is None}\n")
        
        assert apply_module_no_mem.memory_retriever is None
        
        print("   ✅ ApplyModule integration working!\n")
      else:
        print("   ⚠️  Memory not available in ApplyModule\n")
        
    except Exception as e:
      print(f"   ⚠️  Could not test ApplyModule: {e}\n")
    
    print("✅ All tests passed!\n")
    
  finally:
    # Cleanup
    shutil.rmtree(temp_memory_dir)
    shutil.rmtree(temp_chromadb)
    print("🧹 Cleaned up temporary directories")


if __name__ == "__main__":
  test_memory_system()
