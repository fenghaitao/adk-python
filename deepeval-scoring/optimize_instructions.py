#!/usr/bin/env python3
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

"""Optimize ApplyAgent instructions using DeepEval's PromptOptimizer.

This script uses DeepEval's PromptOptimizer with our custom metrics to
automatically improve agent instructions based on historical session outcomes.

Usage:
  python optimize_instructions.py \\
    --historical-data sessions.json \\
    --current-instructions apply_agent_instruction.md \\
    --output optimized_instructions.md \\
    --algorithm miprov2 \\
    --iterations 5
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

from deepeval.optimizer import PromptOptimizer
from deepeval.optimizer.algorithms import MIPROV2, GEPA, COPRO, SIMBA
from deepeval.prompt import Prompt
from deepeval.dataset import Golden
from deepeval.test_case import LLMTestCase
from deepeval.models import LiteLLMModel

from metrics.code_correctness import CodeCorrectnessMetric
from metrics.test_coverage import TestCoverageMetric
from metrics.code_style import CodeStyleMetric
from metrics.agent_behavior import AgentBehaviorMetric


def load_historical_sessions(data_file: Path) -> List[Golden]:
  """Load historical session data as Golden dataset.
  
  Args:
    data_file: JSON file with session data
    
  Returns:
    List of Golden test cases
  """
  with open(data_file) as f:
    sessions = json.load(f)
  
  golden_dataset = []
  for session in sessions:
    golden = Golden(
      input=session["task_description"],
      actual_output=session["implementation"],
      expected_output=session.get("expected_output", ""),
      context=[
        session.get("session_log", ""),
        session.get("spec", ""),
        session.get("tests", "")
      ],
      additional_metadata={
        "device_name": session["device_name"],
        "score": session.get("score", 0.0),
        "metrics": session.get("metrics", {})
      }
    )
    golden_dataset.append(golden)
  
  return golden_dataset


def create_deepeval_model(model: str) -> LiteLLMModel:
  """Create DeepEval LiteLLMModel instance for optimizer.
  
  Args:
    model: Model name (e.g., "iflow/qwen3-coder-plus" or "github_copilot/gpt-5-mini")
    
  Returns:
    LiteLLMModel instance configured for the specified model
  """
  if model.startswith("iflow/"):
    # Convert iflow model to LiteLLM format
    model_name = model.replace("iflow/", "dashscope/")
    
    # Check if API key is available
    api_key = os.getenv("IFLOW_API_KEY")
    if not api_key:
      raise ValueError(
        "IFLOW_API_KEY environment variable not set. "
        "Please set it with: export IFLOW_API_KEY='your-key'"
      )
    
    # Create LiteLLMModel instance for iflow
    return LiteLLMModel(
      model=model_name,
      api_key=api_key,
      base_url="https://apis.iflow.cn/v1/",
      generation_kwargs={
        "temperature": 0.7,
        "logprobs": False,
        "top_logprobs": None
      }
    )
  elif model.startswith("github_copilot/"):
    # GitHub Copilot models use the model name as-is
    return LiteLLMModel(
      model=model,
      generation_kwargs={
        "extra_headers": {
          "Editor-Version": "vscode/1.85.0",
          "Editor-Plugin-Version": "copilot-chat/0.11.1",
          "Openai-Organization": "github-copilot",
          "Copilot-Integration-Id": "vscode-chat"
        }
      }
    )
  else:
    # Generic LiteLLM model (OpenAI, Anthropic, etc.)
    return LiteLLMModel(
      model=model,
      generation_kwargs={"temperature": 0.7}
    )


def create_model_callback(model: str):
  """Create model callback for test case evaluation.
  
  Args:
    model: Model name (e.g., "iflow/qwen3-coder-plus")
    
  Returns:
    Callable that takes prompt and returns response
  """
  def model_callback(prompt: str) -> str:
    """Call LLM with prompt."""
    import litellm
    
    # Configure litellm for iflow
    if model.startswith("iflow/"):
      litellm_model = model.replace("iflow/", "dashscope/")
      api_key = os.getenv("IFLOW_API_KEY")
      response = litellm.completion(
        model=litellm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        api_key=api_key,
        base_url="https://apis.iflow.cn/v1/"
      )
    else:
      response = litellm.completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
      )
    
    return response.choices[0].message.content
  
  return model_callback


def create_optimizer(
    model: str,
    algorithm: str,
    iterations: int,
    weights: Dict[str, float]
) -> PromptOptimizer:
  """Create PromptOptimizer with specified configuration.
  
  Args:
    model: LLM model name
    algorithm: Algorithm name (miprov2, gepa, copro, simba)
    iterations: Number of optimization iterations
    weights: Metric weights for weighted objective
    
  Returns:
    Configured PromptOptimizer
  """
  # Create metrics with weights
  metrics = [
    CodeCorrectnessMetric(model=model, threshold=0.8),
    TestCoverageMetric(model=model, threshold=0.7),
    CodeStyleMetric(model=model, threshold=0.9),
    AgentBehaviorMetric(model=model, threshold=0.7)
  ]
  
  # Select algorithm
  algorithm_map = {
    "miprov2": MIPROV2(
      num_candidates=10,     # Number of instruction candidates to propose
      num_trials=iterations, # Number of Bayesian Optimization trials
      minibatch_size=25,     # Examples per minibatch evaluation
      num_demo_sets=5        # Number of demo sets to create
    ),
    "gepa": GEPA(
      iterations=iterations,
      minibatch_size=8,      # Examples per iteration
      pareto_size=3          # Size of Pareto validation subset
    ),
    "copro": COPRO(
      iterations=iterations,
      minibatch_size=8,      # Examples per iteration
      population_size=4,     # Maximum candidates in pool
      proposals_per_step=4   # Child prompts per iteration
    ),
    "simba": SIMBA(
      iterations=iterations,
      minibatch_size=8,      # Examples per iteration
      population_size=4,     # Maximum candidates in pool
      proposals_per_step=4   # Child prompts per iteration
    )
  }
  
  algo = algorithm_map.get(algorithm.lower())
  if not algo:
    raise ValueError(f"Unknown algorithm: {algorithm}")
  
  # Create DeepEval model for optimizer (generates candidate prompts)
  optimizer_model = create_deepeval_model(model)
  
  # Create optimizer with both model_callback (for eval) and optimizer_model (for generation)
  optimizer = PromptOptimizer(
    model_callback=create_model_callback(model),
    optimizer_model=optimizer_model,
    metrics=metrics,
    algorithm=algo
  )
  
  return optimizer


def optimize_instructions(
    current_instructions: str,
    historical_data: List[Golden],
    optimizer: PromptOptimizer
) -> str:
  """Optimize instructions using PromptOptimizer.
  
  Args:
    current_instructions: Current instruction text
    historical_data: Historical session data
    optimizer: Configured PromptOptimizer
    
  Returns:
    Optimized instruction text
  """
  # Create prompt with text_template (not 'template')
  # The prompt will be optimized based on historical data
  prompt = Prompt(
    text_template=current_instructions
  )
  
  print(f"🔍 Optimizing instructions with {len(historical_data)} historical sessions...")
  print(f"📊 Using {len(optimizer.metrics)} metrics for evaluation")
  
  # Run optimization
  optimized_prompt = optimizer.optimize(
    prompt=prompt,
    goldens=historical_data
  )
  
  # Return the optimized text template
  return optimized_prompt.text_template


def main():
  parser = argparse.ArgumentParser(
    description="Optimize ApplyAgent instructions using DeepEval"
  )
  parser.add_argument(
    "--historical-data",
    required=True,
    help="JSON file with historical session data"
  )
  parser.add_argument(
    "--current-instructions",
    required=True,
    help="Current instruction file (markdown)"
  )
  parser.add_argument(
    "--output",
    required=True,
    help="Output file for optimized instructions"
  )
  parser.add_argument(
    "--model",
    default="iflow/qwen3-coder-plus",
    help="LLM model for optimization (default: iflow/qwen3-coder-plus)"
  )
  parser.add_argument(
    "--algorithm",
    choices=["miprov2", "gepa", "copro", "simba"],
    default="miprov2",
    help="Optimization algorithm (default: miprov2)"
  )
  parser.add_argument(
    "--iterations",
    type=int,
    default=5,
    help="Number of optimization iterations (default: 5)"
  )
  parser.add_argument(
    "--weight-correctness",
    type=float,
    default=0.3,
    help="Weight for code correctness metric (default: 0.3)"
  )
  parser.add_argument(
    "--weight-coverage",
    type=float,
    default=0.3,
    help="Weight for test coverage metric (default: 0.3)"
  )
  parser.add_argument(
    "--weight-style",
    type=float,
    default=0.2,
    help="Weight for code style metric (default: 0.2)"
  )
  parser.add_argument(
    "--weight-behavior",
    type=float,
    default=0.2,
    help="Weight for agent behavior metric (default: 0.2)"
  )
  
  args = parser.parse_args()
  
  # Validate weights sum to 1.0
  total_weight = (
    args.weight_correctness +
    args.weight_coverage +
    args.weight_style +
    args.weight_behavior
  )
  if abs(total_weight - 1.0) > 0.01:
    print(f"❌ Error: Weights must sum to 1.0 (got {total_weight})")
    sys.exit(1)
  
  # Load data
  print(f"📂 Loading historical data from {args.historical_data}...")
  historical_data = load_historical_sessions(Path(args.historical_data))
  print(f"✅ Loaded {len(historical_data)} sessions")
  
  print(f"📂 Loading current instructions from {args.current_instructions}...")
  with open(args.current_instructions) as f:
    current_instructions = f.read()
  print(f"✅ Loaded instructions ({len(current_instructions)} chars)")
  
  # Create optimizer
  print(f"🔧 Creating optimizer with {args.algorithm} algorithm...")
  weights = {
    "Code Correctness": args.weight_correctness,
    "Test Coverage": args.weight_coverage,
    "Code Style": args.weight_style,
    "Agent Behavior": args.weight_behavior
  }
  optimizer = create_optimizer(
    model=args.model,
    algorithm=args.algorithm,
    iterations=args.iterations,
    weights=weights
  )
  print(f"✅ Optimizer created")
  
  # Run optimization
  print(f"\n🚀 Starting optimization ({args.iterations} iterations)...")
  print("="*60)
  
  optimized_instructions = optimize_instructions(
    current_instructions=current_instructions,
    historical_data=historical_data,
    optimizer=optimizer
  )
  
  print("="*60)
  print(f"✅ Optimization complete!")
  
  # Save optimized instructions
  output_path = Path(args.output)
  output_path.write_text(optimized_instructions)
  print(f"💾 Optimized instructions saved to: {output_path}")
  
  # Print diff summary
  original_lines = current_instructions.split("\n")
  optimized_lines = optimized_instructions.split("\n")
  
  print(f"\n📊 Summary:")
  print(f"  Original: {len(original_lines)} lines, {len(current_instructions)} chars")
  print(f"  Optimized: {len(optimized_lines)} lines, {len(optimized_instructions)} chars")
  print(f"  Change: {len(optimized_lines) - len(original_lines):+d} lines")
  
  print(f"\n💡 Next steps:")
  print(f"  1. Review optimized instructions: {output_path}")
  print(f"  2. Test with a new implementation")
  print(f"  3. Compare scores before/after optimization")
  print(f"  4. If improved, replace current instructions")


if __name__ == "__main__":
  main()
