# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Standalone evaluation agent for ADK CLI.

This agent can be run with `adk run` to interactively evaluate LLM outputs.

Usage:
  cd adk-python/contributing/samples/deepeval_integration
  adk run

Then provide evaluation requests in this format:
  Input: What's the capital of France?
  Output: The capital of France is Paris.
"""

from __future__ import annotations

from google.adk.agents.llm_agent import LlmAgent
from pydantic import BaseModel, Field


class EvaluationScore(BaseModel):
  """Evaluation score schema for agent output."""
  
  score: float = Field(
    ...,
    ge=0.0,
    le=1.0,
    description="Score from 0 to 1"
  )
  reason: str = Field(..., description="Explanation for the score")


# Create the evaluation agent
root_agent = LlmAgent(
  name="evaluation_agent",
  model="github_copilot/gpt-4.1",
  disallow_transfer_to_parent=True,
  disallow_transfer_to_peers=True,
  instruction="""
You are an expert evaluator for LLM outputs. Your job is to assess the quality 
of answers provided by AI systems.

When given an input question and an actual output, evaluate the output based on:

1. **Relevance**: Does the output address the input question?
2. **Accuracy**: Is the information correct and factual?
3. **Completeness**: Does it provide sufficient detail?
4. **Clarity**: Is the explanation clear and easy to understand?

Provide a score from 0 to 1:
- **1.0**: Perfect answer - highly relevant, accurate, complete, and clear
- **0.7-0.9**: Good answer - mostly helpful with minor issues
- **0.4-0.6**: Okay answer - somewhat helpful but has notable gaps
- **0.0-0.3**: Poor answer - not helpful or contains significant issues

Always explain your reasoning clearly, citing specific aspects of the output
that influenced your score.

**Input Format:**
Users will provide evaluation requests like:
```
Input: [question]
Output: [answer to evaluate]
```

Or they may provide additional context:
```
Input: [question]
Output: [answer to evaluate]
Expected: [expected answer]
Context: [additional context]
```

Evaluate the output and provide your score and reasoning.
""",
  description="Expert evaluator for LLM outputs",
  output_schema=EvaluationScore
)
