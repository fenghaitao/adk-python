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
  # From directory with goldens and actual_out folders
  python optimize_instructions.py \\
    --goldens goldens/ \\
    --actual-out actual_out/ \\
    --current-instructions apply_agent_instruction.md \\
    --output optimized_instructions.md \\
    --algorithm miprov2 \\
    --iterations 5
  
  # With MLflow tracking and reference
  python optimize_instructions.py \\
    --goldens goldens/ \\
    --actual-out actual_out/ \\
    --reference reference/ \\
    --current-instructions apply_agent_instruction.md \\
    --output optimized_instructions.md \\
    --algorithm copro \\
    --iterations 5 \\
    --mlflow

Expected directory structure:
  goldens/
    item1/
      adk_openspec_project/  # Actual project folder passed to evaluation
    item2/
      adk_openspec_project/
  actual_out/
    item1/
      adk_openspec_project/  # Created during optimization
    item2/
      adk_openspec_project/
  reference/
    adk_openspec_project/ (optional golden reference)
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


def load_minibatch(goldens_path: Path, actual_out_path: Path, reference_path: Optional[Path] = None) -> List[Golden]:
  """Load minibatch data as Golden dataset from organized folder structure.
  
  Each golden example points to the adk_openspec_project folder within the item folder.
  
  Args:
    goldens_path: Path to directory containing golden test folders (e.g., goldens/item1/adk_openspec_project)
    actual_out_path: Path to directory where actual outputs will be stored (e.g., actual_out/item1/adk_openspec_project)
    reference_path: Optional path to golden reference implementation for comparison
    
  Returns:
    List of Golden test cases with paths pointing to adk_openspec_project folders
  """
  golden_dataset = []
  goldens_path = Path(goldens_path)
  actual_out_path = Path(actual_out_path)

  if not goldens_path.is_dir():
    raise ValueError(f"Goldens path does not exist or is not a directory: {goldens_path}")

  print(f"📁 Scanning goldens directory: {goldens_path}")
  print(f"📁 Actual outputs will be in: {actual_out_path}")
  
  if reference_path:
    reference_path = Path(reference_path)
    print(f"📚 Using reference directory: {reference_path}")

  # Find all subdirectories in goldens path
  golden_folders = []
  for item in sorted(goldens_path.iterdir()):
    if item.is_dir():
      golden_folders.append(item)

  if not golden_folders:
    raise ValueError(f"No folders found in goldens path: {goldens_path}")

  print(f"✅ Found {len(golden_folders)} golden folders")

  # Create Golden dataset entries with organized paths
  for golden_folder in golden_folders:
    folder_name = golden_folder.name
    print(f"  📂 Adding golden: {folder_name}")

    # Input points to the golden project folder (goldens/itemX/adk_openspec_project)
    # actual_output points to corresponding project folder in actual_out (actual_out/itemX/adk_openspec_project)
    # expected_output points to reference project if provided, otherwise same as input
    input_folder = golden_folder / "adk_openspec_project"
    output_folder = actual_out_path / folder_name / "adk_openspec_project"
    
    golden = Golden(
      input=str(input_folder),
      actual_output=str(output_folder),
      expected_output=str(reference_path / "adk_openspec_project") if reference_path else str(input_folder)
    )
    golden_dataset.append(golden)
    print(f"    ✓ Input: {input_folder}")
    print(f"    ✓ Output: {output_folder}")

  return golden_dataset


def create_model_callback(model: str, mcp_port: str = "8051"):
  """Create model callback for test case evaluation.
  
  This callback runs the actual optimization test by:
  1. Copying the golden folder (goldens/itemX) to actual_out folder
  2. Replacing the instruction file in actual_out/itemX/adk_openspec_project
  3. Running the run_test.sh script to execute the agent
  4. Returning the project path (actual_out/itemX/adk_openspec_project) for evaluation
  
  Args:
    model: Model name (e.g., "iflow/qwen3-coder-plus")
    mcp_port: MCP server port (default: "8051")
    
  Returns:
    Callable that takes prompt and golden, returns project path for evaluation
  """
  def model_callback(prompt, golden=None) -> str:
    """Run optimization test with the given prompt and golden example.
    
    Args:
      prompt: The prompt to send to the model (instruction text)
      golden: The golden example with paths:
              - input: goldens/itemX/adk_openspec_project
              - actual_output: actual_out/itemX/adk_openspec_project
      
    Returns:
      Path to the actual_output project folder (actual_out/itemX/adk_openspec_project)
    """
    import subprocess
    import shutil
    from deepeval.prompt import Prompt
    
    if golden is None:
      raise ValueError("Golden example is required for model callback")
    
    # Get input and actual_output paths from golden
    input_path = Path(str(golden.input))  # Source project path (goldens/itemX/adk_openspec_project)
    actual_output_path = Path(str(golden.actual_output)) if golden.actual_output else None
    
    if actual_output_path is None:
      raise ValueError("Golden actual_output must be set to the target project folder path")
    
    # Get parent folder paths for copying
    input_parent = input_path.parent  # goldens/itemX
    actual_output_parent = actual_output_path.parent  # actual_out/itemX
    
    # Step 1: Remove existing actual_output parent folder if it exists
    if actual_output_parent.exists():
      print(f"🗑️  Removing existing folder: {actual_output_parent}")
      shutil.rmtree(actual_output_parent)
    
    # Step 2: Copy input parent folder to actual_output parent location
    # Use symlinks=True to copy symlinks as symlinks, and ignore_dangling_symlinks=True
    # to skip broken symlinks instead of raising an error
    print(f"📁 Copying {input_parent} -> {actual_output_parent}")
    try:
      shutil.copytree(
        input_parent, 
        actual_output_parent,
        symlinks=True,  # Copy symlinks as symlinks
        ignore_dangling_symlinks=True  # Skip broken symlinks
      )
      print(f"✅ Successfully copied folder")
    except Exception as e:
      print(f"⚠️  Warning during copy: {e}")
      # Try again with more permissive settings if first attempt fails
      if actual_output_parent.exists():
        shutil.rmtree(actual_output_parent)
      shutil.copytree(
        input_parent,
        actual_output_parent,
        symlinks=False,  # Resolve and copy symlink contents
        ignore_dangling_symlinks=True,  # Skip broken symlinks
        dirs_exist_ok=True  # Allow overwriting
      )
      print(f"✅ Copied folder with fallback method")
    
    # Step 3: Replace the apply_agent_instruction.md with optimized prompt
    # The original file is a symlink, so we need to remove it and create a new file
    instruction_file = actual_output_path / "adk_openspec_apply_agent" / "apply_agent_instruction.md"
    if instruction_file.exists():
      print(f"📝 Replacing instruction file: {instruction_file}")
      instruction_file.unlink()  # Remove the symlink or original file
    else:
      print(f"📝 Creating instruction file: {instruction_file}")
      instruction_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the optimized prompt to the instruction file
    instruction_file.write_text(str(prompt))
    print(f"✅ Instruction file updated with optimized prompt")
    
    # Step 4: Get ADK_ROOT from environment
    adk_root = os.getenv("ADK_ROOT")
    if not adk_root:
      raise ValueError("ADK_ROOT environment variable is not set")
    
    # Step 5: Prepare the bash command
    # Format: run_test.sh <mcp_port> <model> <proj_folder> <stages>
    run_test_script = f"{adk_root}/openspec-scripts/run_test.sh"
    proj_folder = str(actual_output_parent)  # Pass the parent folder (actual_out/itemX)
    stages = "2"  # Stage 2 is the apply stage
    
    # Step 6: Run the test script
    cmd = [run_test_script, mcp_port, model, proj_folder, stages]
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
      result = subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        cwd=actual_output_parent.parent  # Run in parent directory of actual_out
      )
      print(f"✅ Test completed successfully")
      print(f"Output: {result.stdout[-500:]}")  # Print last 500 chars
      
    except subprocess.CalledProcessError as e:
      print(f"❌ Test failed with exit code {e.returncode}")
      print(f"Error output: {e.stderr[-500:]}")  # Print last 500 chars of error
      # Don't raise - let the scoring handle the failure
    
    # Step 7: Return the actual_output path (adk_openspec_project) for evaluation
    return str(actual_output_path)
  
  return model_callback


def create_optimizer(
    model: str,
    algorithm: str,
    iterations: int,
    mcp_port: str = "8051",
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
    mcp_port: MCP server port (default: "8051")
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
      population_size=4,     # Maximum candidates in pool
      proposals_per_step=2   # Child prompts per iteration
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
    model_callback=create_model_callback(model, mcp_port),
    optimizer_model=model,  # Pass string instead of LiteLLMModel object
    metrics=metrics,
    algorithm=algo,
    async_config=AsyncConfig(
      run_async=False,  # Always False to avoid pickle issues with thread locks
      max_concurrent=max_concurrent,
      throttle_value=throttle_seconds
    )
  )
  
  # Replace the scorer if using custom scorer
  if use_custom_scorer:
    custom_scorer = CustomScorer(
      model_callback=create_model_callback(model, mcp_port),
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
    "--goldens",
    required=True,
    help="Path to goldens directory containing test folders (e.g., goldens/item1, goldens/item2)"
  )
  parser.add_argument(
    "--actual-out",
    required=True,
    help="Path to actual outputs directory where test results will be stored"
  )
  parser.add_argument(
    "--reference",
    help="Path to reference directory containing golden implementation for comparison"
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
    "--mcp-port",
    default="8051",
    help="MCP server port (default: 8051)"
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
  print(f"📂 Loading minibatch data...")
  print(f"   Goldens: {args.goldens}")
  print(f"   Actual outputs: {args.actual_out}")
  if args.reference:
    print(f"   Reference: {args.reference}")
  
  minibatch_data = load_minibatch(
    Path(args.goldens),
    Path(args.actual_out),
    Path(args.reference) if args.reference else None
  )
  print(f"✅ Loaded {len(minibatch_data)} test cases")
  
  print(f"📂 Loading current instructions from {args.current_instructions}...")
  with open(args.current_instructions) as f:
    current_instructions = f.read()
  print(f"✅ Loaded instructions ({len(current_instructions)} chars)")
  
  # Create optimizer with rate limiting
  print(f"🔧 Creating optimizer with {args.algorithm} algorithm...")
  print(f"⏱️  Rate limiting: max_concurrent=1, throttle=30.0s")
  print(f"🔌 MCP server port: {args.mcp_port}")
  optimizer = create_optimizer(
    model=args.model,
    algorithm=args.algorithm,
    iterations=args.iterations,
    mcp_port=args.mcp_port,
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
        workdir=str(Path(args.actual_out)),
        algorithm=args.algorithm,
        iterations=args.iterations,
        num_sessions=len(minibatch_data),
        max_concurrent=1,
        throttle_seconds=30.0,
        use_custom_scorer=args.use_custom_scorer,
        agent=args.agent,
        mcp_port=args.mcp_port
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
    historical_data=minibatch_data,
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
        "num_sessions": len(minibatch_data),
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
      mlflow.log_artifact(args.goldens, "goldens")
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
