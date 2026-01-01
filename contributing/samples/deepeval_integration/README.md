# ADK + DeepEval Integration

This directory contains examples and utilities for integrating Google's Agent Development Kit (ADK) with DeepEval for LLM evaluation.

## Overview

**ADK** provides powerful agent capabilities with structured outputs and tool use.
**DeepEval** provides comprehensive LLM evaluation metrics and testing frameworks.

This integration allows you to:
- Use ADK agents as DeepEval metrics
- Evaluate ADK agents with DeepEval's metrics
- Combine both frameworks for comprehensive evaluation

## Files

- `adk_metric.py` - Core integration: Wrap ADK agents as DeepEval metrics
- `example_usage.py` - Simple example showing the integration
- `adk_deepeval_integration.md` - Comprehensive integration guide with multiple approaches

## Quick Start

### 1. Install Dependencies

```bash
pip install deepeval google-adk
```

### 2. Create an ADK Evaluator Agent

```python
from google.adk.agents.llm_agent import LlmAgent
from adk_metric import EvaluationScore

evaluator = LlmAgent(
  name="evaluator",
  model="gemini-2.0-flash-exp",
  instruction="Evaluate if the answer is helpful.",
  output_schema=EvaluationScore
)
```

### 3. Wrap as DeepEval Metric

```python
from adk_metric import AdkMetric

metric = AdkMetric(
  name="Helpfulness",
  agent=evaluator,
  threshold=0.7
)
```

### 4. Use in DeepEval

```python
from deepeval import evaluate
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
  input="What's the weather?",
  actual_output="Paris is sunny at 24°C"
)

evaluate([test_case], [metric])
```

## Running the Example

```bash
# Set your API key (if needed)
export GOOGLE_API_KEY="your-key"

# Run the example
python example_usage.py
```

## Key Concepts

### ADK Agent as Metric

The `AdkMetric` class wraps an ADK `LlmAgent` to work as a DeepEval metric:

```python
class AdkMetric(BaseMetric):
  def measure(self, test_case: LLMTestCase) -> float:
    # Build prompt from test case
    prompt = self._build_prompt(test_case)
    
    # Run ADK agent
    runner = Runner(agent=self.agent)
    result = runner.run(prompt)
    
    # Extract score and reason
    self.score = result.output.score
    self.reason = result.output.reason
    
    return self.score
```

### Output Schema

ADK agents used as metrics must have `EvaluationScore` output schema:

```python
class EvaluationScore(BaseModel):
  score: float = Field(..., ge=0.0, le=1.0)
  reason: str
```

## Comparison: ADK Score Agent vs DeepEval GEval

| Feature | ADK Score Agent | DeepEval GEval |
|---------|----------------|----------------|
| **Approach** | Agent-based | Metric-based |
| **Output** | Structured (Pydantic) | JSON with schema |
| **Tools** | Can use tools | No tool support |
| **Customization** | Full agent capabilities | Criteria + steps |
| **Integration** | Needs wrapper | Native to DeepEval |

## Advanced Usage

See `adk_deepeval_integration.md` for:
- Using score_agent for code evaluation
- Multi-agent systems with DeepEval tracing
- Evaluating ADK agents with DeepEval metrics
- Hybrid approaches

## Benefits

1. **Flexibility**: Use ADK's agent capabilities for complex evaluations
2. **Structured Output**: Leverage Pydantic schemas for type-safe evaluations
3. **Tool Use**: ADK agents can use tools during evaluation
4. **Best of Both**: Combine ADK's agents with DeepEval's evaluation framework

## License

Copyright 2025 Google LLC. Licensed under Apache 2.0.


## Standalone Agent (Interactive CLI)

You can also use the evaluation agent interactively with `adk run`:

```bash
cd adk-python/contributing/samples/deepeval_integration
python -m google.adk.cli run .
```

Then provide evaluation requests:

```
Input: What's the capital of France?
Output: The capital of France is Paris.
```

The agent will return a structured evaluation:

```json
{
  "score": 1.0,
  "reason": "The answer is accurate, directly addresses the question..."
}
```

See `STANDALONE_AGENT_GUIDE.md` for detailed usage instructions.

## All Files

- `agent.py`: Standalone evaluation agent for interactive CLI (`adk run`)
- `adk_metric.py`: Core integration - AdkMetric class for DeepEval
- `example_usage.py`: Programmatic example with multiple test cases
- `adk_deepeval_integration.md`: Comprehensive integration guide
- `STANDALONE_AGENT_GUIDE.md`: Guide for using the interactive agent
- `INTEGRATION_SUMMARY.md`: Technical implementation details
- `FINAL_SUMMARY.md`: Complete summary with test results
- `MODEL_GUIDE.md`: Guide for configuring different LLM models
- `README.md`: This file
