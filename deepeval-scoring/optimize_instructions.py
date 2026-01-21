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
  # From directory with multiple project folders
  python optimize_instructions.py \\
    --historical-data /path/to/data \\
    --current-instructions apply_agent_instruction.md \\
    --output optimized_instructions.md \\
    --algorithm miprov2 \\
    --iterations 5
  
  # With MLflow tracking
  python optimize_instructions.py \\
    --historical-data /path/to/data \\
    --current-instructions apply_agent_instruction.md \\
    --output optimized_instructions.md \\
    --algorithm copro \\
    --iterations 5 \\
    --mlflow

Expected directory structure:
  /path/to/data/
    wdt_dbg132/
      adk_openspec_project/
    wdt_dbg134/
      adk_openspec_project/
    wdt_dbg137/
      adk_openspec_project/
"""

from __future__ import annotations

import argparse
import copy
import json
import litellm
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

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
from metrics.compilation_metric import CompilationMetric
from metrics.test_pass_rate_metric import TestPassRateMetric
from metrics.custom_scorer import CustomScorer
from tracking.mlflow_tracker import MLflowTracker
from tracking.utils import is_mlflow_available


def load_historical_sessions(data_path: Path, reference_dir: Optional[str] = None) -> List[Golden]:
  """Load historical session data as Golden dataset from multiple project folders.
  
  Args:
    data_path: Path to directory containing multiple project folders 
               (e.g., wdt_dbg132, wdt_dbg134, wdt_dbg137)
               Each folder should contain an adk_openspec_project subdirectory
    reference_dir: Optional path to golden reference implementation for comparison
    
  Returns:
    List of Golden test cases with project paths
  """
  golden_dataset = []
  data_path = Path(data_path)

  if not data_path.is_dir():
    raise ValueError(f"Path does not exist or is not a directory: {data_path}")

  print(f"📁 Scanning directory for project folders: {data_path}")
  
  if reference_dir:
    print(f"📚 Using reference directory: {reference_dir}")

  # Find all subdirectories that contain adk_openspec_project
  project_folders = []
  for item in sorted(data_path.iterdir()):
    if item.is_dir():
      project_path = item / "adk_openspec_project"
      if project_path.exists():
        project_folders.append((item.name, project_path))

  if not project_folders:
    raise ValueError(f"No project folders with 'adk_openspec_project' found in: {data_path}")

  print(f"✅ Found {len(project_folders)} project folders")

  # Create Golden dataset entries with project paths
  for idx, (folder_name, project_path) in enumerate(project_folders):
    print(f"  📂 Adding {folder_name}/adk_openspec_project...")

    # Create a test folder for this optimization run
    # Format: {folder_name}_opt_test_{idx}
    parent_dir = project_path.parent
    test_folder_name = f"{folder_name}_opt_test_{idx}"
    actual_output_path = parent_dir.parent / test_folder_name / "adk_openspec_project"
    
    # Input points to the original project path
    # actual_output points to where the test run will be executed
    # expected_output points to reference implementation if provided, otherwise same as input
    golden = Golden(
      input=str(project_path),
      actual_output=str(actual_output_path),  # Target path for test execution
      expected_output=reference_dir if reference_dir else str(project_path)
    )
    golden_dataset.append(golden)
    print(f"    ✓ Added {folder_name} -> test folder: {test_folder_name}")

  return golden_dataset


def create_model_callback(model: str):
  """Create model callback for test case evaluation.
  
  This callback runs the actual optimization test by:
  1. Setting up the test project folder from the golden input
  2. Running the run_test.sh script to execute the agent
  3. Returning the project path for evaluation
  
  Args:
    model: Model name (e.g., "iflow/qwen3-coder-plus")
    
  Returns:
    Callable that takes prompt and golden, returns project path
  """
  def model_callback(prompt, golden=None) -> str:
    """Run optimization test with the given prompt and golden example.
    
    Args:
      prompt: The prompt to send to the model (instruction text)
      golden: The golden example containing input/actual_output paths
      
    Returns:
      Path to the actual_output folder (for evaluation)
    """
    import subprocess
    import shutil
    from deepeval.prompt import Prompt
    
    if golden is None:
      raise ValueError("Golden example is required for model callback")
    
    # Get input and actual_output paths from golden
    input_path = Path(str(golden.input))  # Source project path
    actual_output_path = Path(str(golden.actual_output)) if golden.actual_output else None
    
    if actual_output_path is None:
      raise ValueError("Golden actual_output must be set to the target project folder path")
    
    # Step 1: Remove existing actual_output folder if it exists
    if actual_output_path.exists():
      print(f"🗑️  Removing existing folder: {actual_output_path}")
      shutil.rmtree(actual_output_path)
    
    # Step 2: Copy input folder to actual_output location
    print(f"📁 Copying {input_path} -> {actual_output_path}")
    shutil.copytree(input_path, actual_output_path)
    
    # Step 3: Get ADK_ROOT from environment
    adk_root = os.getenv("ADK_ROOT")
    if not adk_root:
      raise ValueError("ADK_ROOT environment variable is not set")
    
    # Step 4: Prepare the bash command
    # Format: run_test.sh <mcp_port> <model> <proj_folder> <stages>
    run_test_script = f"{adk_root}/openspec-scripts/run_test.sh"
    mcp_port = "8051"
    proj_folder = str(actual_output_path.parent / actual_output_path.name)
    stages = "2"  # Stage 2 is the apply stage
    
    # Step 5: Run the test script
    cmd = [run_test_script, mcp_port, model, proj_folder, stages]
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
      result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        cwd=actual_output_path.parent  # Run in parent directory
      )
      print(f"✅ Test completed successfully")
      print(f"Output: {result.stdout[-500:]}")  # Print last 500 chars
      
    except subprocess.CalledProcessError as e:
      print(f"❌ Test failed with exit code {e.returncode}")
      print(f"Error output: {e.stderr[-500:]}")  # Print last 500 chars of error
      # Don't raise - let the scoring handle the failure
    
    # Step 6: Return the actual_output path for evaluation
    return str(actual_output_path)
  
  return model_callback


def create_optimizer(
    model: str,
    algorithm: str,
    iterations: int,
    run_async: bool = False,
    use_custom_scorer: bool = False,
    scoring_mode: str = "llm",
    agent: Optional[str] = None,
    mlflow_tracker=None
) -> PromptOptimizer:
  """Create PromptOptimizer with specified configuration.
  
  Args:
    model: LLM model name
    algorithm: Algorithm name (miprov2, gepa, copro, simba)
    iterations: Number of optimization iterations
    run_async: Whether to run async (default: False to avoid pickle issues)
    use_custom_scorer: Use CustomScorer wrapper instead of individual metrics
    scoring_mode: Scoring mode for custom scorer (llm, deterministic, hybrid)
    agent: Agent type for behavior evaluation
    mlflow_tracker: Optional MLflow tracker for logging
    
  Returns:
    Configured PromptOptimizer
  """
  # Hardcoded rate limiting configuration
  max_concurrent = 1
  throttle_seconds = 30.0
  # Use individual metrics (original approach)
  # These are needed even with custom_scorer for compatibility
  metrics = [
    CodeCorrectnessMetric(model=model, threshold=0.8),
    TestCoverageMetric(model=model, threshold=0.7),
    CodeStyleMetric(model=model, threshold=0.9),
    AgentBehaviorMetric(model=model, threshold=0.7),
    CompilationMetric(model=model, threshold=1.0),
    TestPassRateMetric(model=model, threshold=0.5)
  ]
  
  if use_custom_scorer:
    print(f"📊 Using CustomScorer with {scoring_mode} mode")
  else:
    print(f"📊 Using individual metrics: {len(metrics)} metrics")
  
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
      minibatch_size=2,      # Examples per iteration
      population_size=3,     # Maximum candidates in pool
      proposals_per_step=3   # Child prompts per iteration
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
  
  # Replace the scorer if using custom scorer
  if use_custom_scorer:
    custom_scorer = CustomScorer(
      model_callback=create_model_callback(model),
      metrics=metrics,
      max_concurrent=max_concurrent,
      throttle_seconds=throttle_seconds,
      evaluation_model=model,
      scoring_mode=scoring_mode,
      agent=agent,
      mlflow_tracker=mlflow_tracker
    )
    algo.scorer = custom_scorer

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
    help="Path to directory containing project folders (e.g., wdt_dbg132/adk_openspec_project, wdt_dbg134/adk_openspec_project)"
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
    "--no-async",
    action="store_true",
    help="Disable async mode to avoid pickle issues with thread locks (default: False)"
  )
  parser.add_argument(
    "--use-custom-scorer",
    action="store_true",
    help="Use CustomScorer wrapper for unified metric evaluation (default: False)"
  )
  parser.add_argument(
    "--scoring-mode",
    choices=["llm", "deterministic", "hybrid"],
    default="llm",
    help="Scoring mode for custom scorer: llm, deterministic, or hybrid (default: llm)"
  )
  parser.add_argument(
    "--agent",
    default="adk-python",
    help="Agent type for behavior evaluation (default: adk-python)"
  )
  parser.add_argument(
    "--reference-dir",
    help="Directory containing golden reference implementation for comparison"
  )
  parser.add_argument(
    "--mlflow",
    action="store_true",
    help="Enable MLflow experiment tracking"
  )
  parser.add_argument(
    "--mlflow-tracking-uri",
    help="MLflow tracking URI (overrides config)"
  )
  parser.add_argument(
    "--mlflow-experiment-name",
    help="MLflow experiment name (overrides config pattern)"
  )
  
  args = parser.parse_args()
  
  # Initialize MLflow tracker if requested
  mlflow_tracker = None
  if args.mlflow:
    if not is_mlflow_available():
      print("❌ Error: MLflow is not available. Install with: pip install mlflow")
      sys.exit(1)
    
    try:
      mlflow_tracker = MLflowTracker(
        tracking_uri=args.mlflow_tracking_uri,
        experiment_name=args.mlflow_experiment_name
      )
      print(f"🔬 MLflow tracking enabled: {mlflow_tracker.get_tracking_uri()}")
    except Exception as e:
      print(f"❌ Error initializing MLflow: {e}")
      sys.exit(1)
  
  # Load data
  print(f"📂 Loading historical data from {args.historical_data}...")
  historical_data = load_historical_sessions(
    Path(args.historical_data),
    reference_dir=args.reference_dir
  )
  print(f"✅ Loaded {len(historical_data)} sessions")
  
  print(f"📂 Loading current instructions from {args.current_instructions}...")
  with open(args.current_instructions) as f:
    current_instructions = f.read()
  print(f"✅ Loaded instructions ({len(current_instructions)} chars)")
  
  # Create optimizer with rate limiting
  print(f"🔧 Creating optimizer with {args.algorithm} algorithm...")
  print(f"⏱️  Rate limiting: max_concurrent=1, throttle=30.0s")
  optimizer = create_optimizer(
    model=args.model,
    algorithm=args.algorithm,
    iterations=args.iterations,
    run_async=not args.no_async,  # Invert the flag
    use_custom_scorer=args.use_custom_scorer,
    scoring_mode=args.scoring_mode,
    agent=args.agent,
    mlflow_tracker=mlflow_tracker
  )
  print(f"✅ Optimizer created")
  
  # Start MLflow run if enabled
  if mlflow_tracker:
    try:
      mlflow_tracker.start_run(
        device_name="prompt_optimization",
        model=args.model,
        scoring_mode=args.scoring_mode if args.use_custom_scorer else "optimization",
        workdir=str(Path(args.historical_data)) if Path(args.historical_data).is_dir() else str(Path(args.historical_data).parent),
        algorithm=args.algorithm,
        iterations=args.iterations,
        num_sessions=len(historical_data),
        max_concurrent=1,
        throttle_seconds=30.0,
        use_custom_scorer=args.use_custom_scorer,
        agent=args.agent
      )
    except Exception as e:
      print(f"❌ Error starting MLflow run: {e}")
      mlflow_tracker = None
  
  # Run optimization
  print(f"\n🚀 Starting optimization ({args.iterations} iterations)...")
  print("="*60)
  
  start_time = time.time()
  
  optimized_instructions = optimize_instructions(
    current_instructions=current_instructions,
    historical_data=historical_data,
    optimizer=optimizer
  )
  
  optimization_time = time.time() - start_time
  
  print("="*60)
  print(f"✅ Optimization complete in {optimization_time:.1f} seconds!")
  
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
  
  # Log to MLflow if enabled
  if mlflow_tracker:
    try:
      import mlflow
      import tempfile
      
      # Log metrics
      mlflow.log_metrics({
        "num_sessions": len(historical_data),
        "iterations": args.iterations,
        "optimization_time_seconds": optimization_time,
        "original_lines": len(original_lines),
        "optimized_lines": len(optimized_lines),
        "original_chars": len(current_instructions),
        "optimized_chars": len(optimized_instructions),
        "lines_change": len(optimized_lines) - len(original_lines),
        "chars_change": len(optimized_instructions) - len(current_instructions),
        "max_concurrent": 1,
        "throttle_seconds": 30.0
      })
      
      # Log artifacts
      mlflow.log_artifact(args.historical_data, "input_data")
      mlflow.log_artifact(args.current_instructions, "original_instructions")
      mlflow.log_artifact(str(output_path), "optimized_instructions")
      
      # Create and log a diff file
      import difflib
      diff = difflib.unified_diff(
        original_lines,
        optimized_lines,
        fromfile="original_instructions.md",
        tofile="optimized_instructions.md",
        lineterm=""
      )
      with tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False) as f:
        f.write('\n'.join(diff))
        diff_file = f.name
      mlflow.log_artifact(diff_file, "diff")
      Path(diff_file).unlink()
      
      print(f"\n🔬 Results logged to MLflow run: {mlflow_tracker.get_run_id()}")
      
    except Exception as e:
      print(f"⚠️  Warning: Failed to log to MLflow: {e}")
  
  print(f"\n💡 Next steps:")
  print(f"  1. Review optimized instructions: {output_path}")
  print(f"  2. Test with a new implementation")
  print(f"  3. Compare scores before/after optimization")
  print(f"  4. If improved, replace current instructions")
  
  # End MLflow run
  if mlflow_tracker:
    try:
      mlflow_tracker.end_run(status="FINISHED")
    except Exception as e:
      print(f"⚠️  Warning: Failed to end MLflow run: {e}")


if __name__ == "__main__":
  main()
