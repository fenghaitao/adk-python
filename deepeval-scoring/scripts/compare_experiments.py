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

"""Compare MLflow experiments and runs for deepeval scoring."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracking.experiment_manager import ExperimentManager
from tracking.utils import is_mlflow_available


def main():
  parser = argparse.ArgumentParser(
    description="Compare MLflow experiments and runs"
  )
  parser.add_argument(
    "--tracking-uri",
    help="MLflow tracking URI"
  )
  parser.add_argument(
    "--experiment",
    help="Experiment name to analyze"
  )
  parser.add_argument(
    "--device",
    help="Filter experiments by device name"
  )
  parser.add_argument(
    "--runs",
    nargs="+",
    help="Specific run IDs to compare"
  )
  parser.add_argument(
    "--metric",
    default="overall_score",
    help="Metric to use for best run selection (default: overall_score)"
  )
  parser.add_argument(
    "--list-experiments",
    action="store_true",
    help="List all experiments"
  )
  parser.add_argument(
    "--list-runs",
    action="store_true",
    help="List runs in the specified experiment"
  )
  
  args = parser.parse_args()
  
  if not is_mlflow_available():
    print("❌ Error: MLflow is not available. Install with: pip install mlflow")
    sys.exit(1)
  
  try:
    manager = ExperimentManager(tracking_uri=args.tracking_uri)
    
    if args.list_experiments:
      experiments = manager.list_experiments(device_filter=args.device)
      print("📊 Available Experiments:")
      print("=" * 50)
      for exp in experiments:
        print(f"  • {exp.name} (ID: {exp.experiment_id})")
        print(f"    Created: {exp.creation_time}")
        print(f"    Lifecycle: {exp.lifecycle_stage}")
        print()
    
    elif args.list_runs and args.experiment:
      runs = manager.get_experiment_runs(args.experiment)
      print(f"🏃 Runs in experiment '{args.experiment}':")
      print("=" * 50)
      for run in runs:
        print(f"  • {run.get('tags.mlflow.runName', run['run_id'])}")
        print(f"    Run ID: {run['run_id']}")
        print(f"    Status: {run['status']}")
        if 'metrics.overall_score' in run:
          print(f"    Overall Score: {run['metrics.overall_score']:.1%}")
        print(f"    Started: {run['start_time']}")
        print()
    
    elif args.runs:
      comparison = manager.compare_runs(args.runs)
      print("🔍 Run Comparison:")
      print("=" * 50)
      
      for run_data in comparison["runs"]:
        print(f"\n📋 {run_data['run_name']}")
        print(f"   Run ID: {run_data['run_id']}")
        print(f"   Status: {run_data['status']}")
        
        # Show key metrics
        metrics = run_data["metrics"]
        if "overall_score" in metrics:
          print(f"   Overall Score: {metrics['overall_score']:.1%}")
        if "deterministic_overall_score" in metrics:
          print(f"   Deterministic Score: {metrics['deterministic_overall_score']:.1%}")
        if "llm_code_overall_score" in metrics:
          print(f"   LLM Code Score: {metrics['llm_code_overall_score']:.1%}")
        if "behavior_overall_score" in metrics:
          print(f"   Behavior Score: {metrics['behavior_overall_score']:.1%}")
        
        # Show parameters
        params = run_data["params"]
        print(f"   Model: {params.get('model', 'N/A')}")
        print(f"   Scoring Mode: {params.get('scoring_mode', 'N/A')}")
        print(f"   Device: {params.get('device_name', 'N/A')}")
      
      # Show comparison metrics
      if comparison["comparison_metrics"]:
        print("\n📈 Metric Comparison:")
        for metric, stats in comparison["comparison_metrics"].items():
          print(f"   {metric}:")
          print(f"     Min: {stats['min']:.3f}")
          print(f"     Max: {stats['max']:.3f}")
          print(f"     Avg: {stats['avg']:.3f}")
    
    elif args.experiment:
      best_run = manager.get_best_run(args.experiment, args.metric)
      if best_run:
        print(f"🏆 Best run in '{args.experiment}' by {args.metric}:")
        print("=" * 50)
        print(f"  Run Name: {best_run.get('tags.mlflow.runName', best_run['run_id'])}")
        print(f"  Run ID: {best_run['run_id']}")
        print(f"  {args.metric}: {best_run.get(f'metrics.{args.metric}', 'N/A')}")
        print(f"  Model: {best_run.get('params.model', 'N/A')}")
        print(f"  Scoring Mode: {best_run.get('params.scoring_mode', 'N/A')}")
        print(f"  Started: {best_run['start_time']}")
      else:
        print(f"❌ No runs found in experiment '{args.experiment}'")
    
    else:
      print("❌ Please specify an action: --list-experiments, --list-runs, --runs, or --experiment")
      sys.exit(1)
  
  except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()