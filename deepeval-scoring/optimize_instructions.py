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
    # Use expected_output for the reference implementation, not actual_output
    # actual_output should be None initially (filled by model during optimization)
    golden = Golden(
      input=session["task_description"],
      actual_output=None,  # Will be filled by model during optimization
      expected_output=session["implementation"],  # Reference implementation
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





def create_model_callback(model: str):
  """Create model callback for test case evaluation.
  
  Args:
    model: Model name (e.g., "iflow/qwen3-coder-plus")
    
  Returns:
    Callable that takes prompt and golden, returns response
  """
  def model_callback(prompt, golden=None) -> str:
    """Call LLM with prompt with exponential backoff retry.
    
    Args:
      prompt: The prompt to send to the model (can be string or Prompt object)
      golden: The golden/reference data (unused but required by interface)
    """
    import litellm
    import time
    import copy
    from deepeval.prompt import Prompt
    
    # Convert Prompt object to string if needed
    if isinstance(prompt, Prompt):
      prompt_text = prompt.text_template or ""
    else:
      prompt_text = str(prompt)
    
    # Monkey-patch deepcopy to avoid pickle issues with thread locks
    # Store original deepcopy
    original_deepcopy = copy.deepcopy
    
    # Define a shallow copy function that avoids pickle issues
    def safe_deepcopy(obj, memo=None):
      try:
        return original_deepcopy(obj, memo)
      except (TypeError, AttributeError) as e:
        if "pickle" in str(e) or "thread.lock" in str(e):
          # Return a shallow copy for unpicklable objects
          if isinstance(obj, list):
            return [item if isinstance(item, (str, int, float, bool, type(None))) else item for item in obj]
          elif isinstance(obj, dict):
            return {k: v if isinstance(v, (str, int, float, bool, type(None))) else v for k, v in obj.items()}
          else:
            return obj
        raise
    
    # Apply monkey patch
    copy.deepcopy = safe_deepcopy
    
    max_retries = 1
    base_delay = 30.0
    
    for attempt in range(max_retries):
      try:
        # Configure litellm for iflow
        if model.startswith("iflow/"):
          litellm_model = model.replace("iflow/", "dashscope/")
          api_key = os.getenv("IFLOW_API_KEY")
          response = litellm.completion(
            model=litellm_model,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.7,
            api_key=api_key,
            base_url="https://apis.iflow.cn/v1/"
          )
        elif model.startswith("github_copilot/"):
          # GitHub Copilot models use litellm.completion with special headers
          response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.7,
            extra_headers={
              "Editor-Version": "vscode/1.85.0",
              "Editor-Plugin-Version": "copilot-chat/0.11.1",
              "Openai-Organization": "github-copilot",
              "Copilot-Integration-Id": "vscode-chat"
            }
          )
        else:
          response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.7
          )
        
        return response.choices[0].message.content
        
      except Exception as e:
        error_msg = str(e).lower()
        # Check if it's a rate limit error
        if "rate limit" in error_msg or "429" in error_msg or "449" in error_msg:
          if attempt < max_retries - 1:
            # Exponential backoff: 2s, 4s, 8s, 16s, 32s
            delay = base_delay * (2 ** attempt)
            print(f"⚠️  Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}...")
            time.sleep(delay)
            continue
        # Re-raise non-rate-limit errors or final attempt
        raise
    
    raise Exception(f"Failed after {max_retries} retries")
  
  return model_callback


def create_optimizer(
    model: str,
    algorithm: str,
    iterations: int,
    weights: Dict[str, float],
    max_concurrent: int = 5,
    throttle_seconds: float = 2.0,
    run_async: bool = False
) -> PromptOptimizer:
  """Create PromptOptimizer with specified configuration.
  
  Args:
    model: LLM model name
    algorithm: Algorithm name (miprov2, gepa, copro, simba)
    iterations: Number of optimization iterations
    weights: Metric weights for weighted objective
    max_concurrent: Maximum concurrent API calls (default: 5 for rate limiting)
    throttle_seconds: Seconds to wait between batches (default: 2.0)
    run_async: Whether to run async (default: False to avoid pickle issues)
    
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
  
  # Pass model string directly to optimizer - DeepEval's initialize_model() will handle it
  # This avoids pickle issues with LiteLLMModel objects containing thread locks
  
  # Import AsyncConfig for rate limiting
  from deepeval.optimizer.configs import AsyncConfig
  
  # Create optimizer with rate limiting configuration
  optimizer = PromptOptimizer(
    model_callback=create_model_callback(model),
    optimizer_model=model,  # Pass string instead of LiteLLMModel object
    metrics=metrics,
    algorithm=algo,
    async_config=AsyncConfig(
      run_async=run_async,  # Use parameter instead of hardcoded True
      max_concurrent=max_concurrent,
      throttle_value=throttle_seconds
    )
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
  parser.add_argument(
    "--max-concurrent",
    type=int,
    default=3,
    help="Maximum concurrent API calls for rate limiting (default: 3)"
  )
  parser.add_argument(
    "--throttle-seconds",
    type=float,
    default=2.0,
    help="Seconds to wait between API call batches (default: 2.0)"
  )
  parser.add_argument(
    "--no-async",
    action="store_true",
    help="Disable async mode to avoid pickle issues with thread locks (default: False)"
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
  
  # Create optimizer with rate limiting
  print(f"🔧 Creating optimizer with {args.algorithm} algorithm...")
  print(f"⏱️  Rate limiting: max_concurrent={args.max_concurrent}, throttle={args.throttle_seconds}s")
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
    weights=weights,
    max_concurrent=args.max_concurrent,
    throttle_seconds=args.throttle_seconds,
    run_async=not args.no_async  # Invert the flag
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
