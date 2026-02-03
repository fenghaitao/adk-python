# DSPy Retrieval Patterns

This guide covers DSPy retrieval patterns and best practices for integrating memory retrieval into AI agents.

## DSPy Module Pattern

### Basic Retriever Module

```python
import dspy

class MemoryRetriever(dspy.Module):
    """Retrieve relevant passages from memory."""
    
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.retriever = dspy.Retrieve(k=k)
    
    def forward(self, query):
        """Retrieve passages for query."""
        passages = self.retriever(query).passages
        return dspy.Prediction(passages=passages)
```

### Usage in Agent

```python
class AgentWithMemory(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retriever = MemoryRetriever(k=3)
        self.generate = dspy.ChainOfThought("context, query -> answer")
    
    def forward(self, query):
        # Retrieve context
        retrieval = self.retriever(query)
        context = "\n\n".join(retrieval.passages)
        
        # Generate answer with context
        return self.generate(context=context, query=query)
```

## Retrieval Strategies

### 1. Simple Retrieval

```python
class SimpleRetriever(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=k)
    
    def forward(self, query):
        return self.retrieve(query)
```

### 2. Multi-Hop Retrieval

```python
class MultiHopRetriever(dspy.Module):
    """Retrieve, then retrieve again based on initial results."""
    
    def __init__(self, k=3, hops=2):
        super().__init__()
        self.k = k
        self.hops = hops
        self.retrieve = dspy.Retrieve(k=k)
    
    def forward(self, query):
        all_passages = []
        current_query = query
        
        for hop in range(self.hops):
            result = self.retrieve(current_query)
            all_passages.extend(result.passages)
            
            # Generate new query from retrieved context
            if hop < self.hops - 1:
                current_query = self._refine_query(
                    query, 
                    result.passages
                )
        
        return dspy.Prediction(passages=all_passages)
```

### 3. Category-Aware Retrieval

```python
class CategoryRetriever(dspy.Module):
    """Retrieve from specific categories."""
    
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.dml_retriever = MemoryRetriever(k=k)
        self.test_retriever = MemoryRetriever(k=k)
    
    def forward(self, query, category=None):
        if category == "DML":
            return self.dml_retriever(query, category="DML")
        elif category == "Test":
            return self.test_retriever(query, category="Test")
        else:
            # Retrieve from both
            dml = self.dml_retriever(query, category="DML")
            test = self.test_retriever(query, category="Test")
            
            # Combine results
            passages = dml.passages + test.passages
            return dspy.Prediction(passages=passages[:self.k])
```

### 4. Reranking Retriever

```python
class RerankingRetriever(dspy.Module):
    """Retrieve many, then rerank to select best."""
    
    def __init__(self, k=3, initial_k=10):
        super().__init__()
        self.k = k
        self.initial_k = initial_k
        self.retrieve = dspy.Retrieve(k=initial_k)
        self.rerank = dspy.ChainOfThought(
            "query, passages -> ranked_passages"
        )
    
    def forward(self, query):
        # Initial broad retrieval
        result = self.retrieve(query)
        
        # Rerank based on relevance
        reranked = self.rerank(
            query=query,
            passages=result.passages
        )
        
        # Return top k
        return dspy.Prediction(
            passages=reranked.ranked_passages[:self.k]
        )
```

## Integration Patterns

### Pattern 1: RAG (Retrieval-Augmented Generation)

```python
class RAGModule(dspy.Module):
    """Classic RAG pattern."""
    
    def __init__(self):
        super().__init__()
        self.retriever = MemoryRetriever(k=3)
        self.generate = dspy.ChainOfThought(
            "context, question -> answer"
        )
    
    def forward(self, question):
        # 1. Retrieve context
        retrieval = self.retriever(question)
        context = "\n\n".join(retrieval.passages)
        
        # 2. Generate answer
        return self.generate(context=context, question=question)
```

### Pattern 2: ReAct with Retrieval

```python
class ReActWithMemory(dspy.Module):
    """ReAct agent with memory tool."""
    
    def __init__(self):
        super().__init__()
        self.retriever = MemoryRetriever(k=3)
        
        # Define retrieval as a tool
        def search_memory(query: str) -> str:
            result = self.retriever(query)
            return "\n\n".join(result.passages)
        
        # ReAct with tools
        self.react = dspy.ReAct(
            "task -> result",
            tools=[search_memory]
        )
    
    def forward(self, task):
        return self.react(task=task)
```

### Pattern 3: Iterative Refinement

```python
class IterativeRetrieval(dspy.Module):
    """Refine query based on retrieved results."""
    
    def __init__(self, max_iters=3):
        super().__init__()
        self.max_iters = max_iters
        self.retriever = MemoryRetriever(k=3)
        self.refiner = dspy.ChainOfThought(
            "query, passages -> refined_query"
        )
    
    def forward(self, initial_query):
        query = initial_query
        all_passages = []
        
        for i in range(self.max_iters):
            # Retrieve with current query
            result = self.retriever(query)
            all_passages.extend(result.passages)
            
            # Check if we have enough context
            if self._has_sufficient_context(all_passages):
                break
            
            # Refine query for next iteration
            if i < self.max_iters - 1:
                refined = self.refiner(
                    query=query,
                    passages=result.passages
                )
                query = refined.refined_query
        
        return dspy.Prediction(
            passages=all_passages,
            iterations=i+1
        )
```

### Pattern 4: Ensemble Retrieval

```python
class EnsembleRetriever(dspy.Module):
    """Combine multiple retrieval strategies."""
    
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.semantic = MemoryRetriever(k=k*2)
        self.keyword = KeywordRetriever(k=k*2)
    
    def forward(self, query):
        # Get results from multiple retrievers
        semantic_result = self.semantic(query)
        keyword_result = self.keyword(query)
        
        # Combine and deduplicate
        all_passages = list(set(
            semantic_result.passages + keyword_result.passages
        ))
        
        # Score and select top k
        scored = self._score_passages(query, all_passages)
        top_k = sorted(scored, key=lambda x: x[1], reverse=True)[:self.k]
        
        return dspy.Prediction(
            passages=[p for p, score in top_k]
        )
```

## Optimization Techniques

### 1. Few-Shot Optimization

```python
from dspy.teleprompt import BootstrapFewShot

# Define training examples
train_data = [
    dspy.Example(
        query="How to implement timer?",
        passages=["DML timer using after keyword..."]
    ).with_inputs("query"),
    # ... more examples
]

# Define metric
def retrieval_quality(example, pred, trace=None):
    # Check if retrieved passages contain answer
    return compute_relevance(example.passages, pred.passages)

# Optimize
optimizer = BootstrapFewShot(metric=retrieval_quality)
optimized_retriever = optimizer.compile(
    MemoryRetriever(),
    trainset=train_data
)
```

### 2. Prompt Optimization

```python
from dspy.teleprompt import MIPRO

# Optimize prompts and examples together
optimizer = MIPRO(
    metric=retrieval_quality,
    num_candidates=10,
    init_temperature=1.0
)

optimized = optimizer.compile(
    RAGModule(),
    trainset=train_data,
    valset=val_data
)
```

### 3. Parameter Tuning

```python
# Grid search for k parameter
def evaluate_k(k_value):
    retriever = MemoryRetriever(k=k_value)
    score = evaluate(retriever, test_data)
    return score

best_k = max(range(1, 10), key=evaluate_k)
print(f"Best k: {best_k}")
```

## Best Practices

### 1. Context Length Management

```python
class ContextAwareRetriever(dspy.Module):
    def __init__(self, max_tokens=2000):
        super().__init__()
        self.max_tokens = max_tokens
        self.retriever = MemoryRetriever(k=10)
    
    def forward(self, query):
        result = self.retriever(query)
        
        # Select passages that fit in context
        selected = []
        token_count = 0
        
        for passage in result.passages:
            passage_tokens = len(passage.split())
            if token_count + passage_tokens <= self.max_tokens:
                selected.append(passage)
                token_count += passage_tokens
            else:
                break
        
        return dspy.Prediction(passages=selected)
```

### 2. Caching

```python
from functools import lru_cache

class CachedRetriever(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.retriever = MemoryRetriever(k=k)
    
    @lru_cache(maxsize=128)
    def _cached_retrieve(self, query):
        return self.retriever(query)
    
    def forward(self, query):
        return self._cached_retrieve(query)
```

### 3. Error Handling

```python
class RobustRetriever(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.retriever = MemoryRetriever(k=k)
        self.fallback_passages = [
            "Default context when retrieval fails..."
        ]
    
    def forward(self, query):
        try:
            return self.retriever(query)
        except Exception as e:
            print(f"Retrieval failed: {e}")
            return dspy.Prediction(passages=self.fallback_passages)
```

### 4. Logging and Monitoring

```python
class MonitoredRetriever(dspy.Module):
    def __init__(self, k=3):
        super().__init__()
        self.k = k
        self.retriever = MemoryRetriever(k=k)
        self.query_log = []
    
    def forward(self, query):
        import time
        start = time.time()
        
        result = self.retriever(query)
        
        # Log metrics
        self.query_log.append({
            "query": query,
            "num_results": len(result.passages),
            "latency_ms": (time.time() - start) * 1000
        })
        
        return result
```

## Testing Strategies

### Unit Tests

```python
def test_retriever():
    retriever = MemoryRetriever(k=3)
    result = retriever("test query")
    
    assert len(result.passages) <= 3
    assert all(isinstance(p, str) for p in result.passages)

def test_category_filter():
    retriever = MemoryRetriever(k=3)
    result = retriever("DML syntax", category="DML")
    
    # Verify all results are from DML category
    assert all("DML" in passage for passage in result.passages)
```

### Integration Tests

```python
def test_rag_pipeline():
    rag = RAGModule()
    answer = rag("How to implement timer?")
    
    assert answer is not None
    assert len(answer.answer) > 0

def test_react_with_memory():
    agent = ReActWithMemory()
    result = agent("Find timer examples and summarize")
    
    assert result is not None
    assert "timer" in result.result.lower()
```

### Evaluation Metrics

```python
def evaluate_retrieval(retriever, test_set):
    """Compute retrieval metrics."""
    metrics = {
        "precision": 0,
        "recall": 0,
        "mrr": 0,  # Mean reciprocal rank
    }
    
    for example in test_set:
        result = retriever(example.query)
        
        # Compute metrics
        relevant = set(example.relevant_docs)
        retrieved = set(result.passages)
        
        tp = len(relevant & retrieved)
        metrics["precision"] += tp / len(retrieved) if retrieved else 0
        metrics["recall"] += tp / len(relevant) if relevant else 0
    
    # Average
    n = len(test_set)
    return {k: v/n for k, v in metrics.items()}
```

## Reference Links

- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
