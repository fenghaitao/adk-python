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

"""Export MLflow experiment results to various formats."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracking.experiment_manager import ExperimentManager
from tracking.utils import is_mlflow_available


def export_to_csv(runs_data: list, output_path: str):
  """Export runs data to CSV format."""
  if not runs_data:
    return
  
  # Collect all unique columns
  all_columns = set()
  for run in runs_data:
    all_columns.update(run.get("params", {}).keys())
    all_columns.update(run.get("metrics", {}).keys())
    all_columns.update(["run_id", "run_name", "status", "start_time"])
  
  all_columns = sorted(all_columns)
  
  with open(output_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=all_columns)
    writer.writeheader()
    
    for run in runs_data:
      row = {
        "run_id": run["run_id"],
        "run_name": run["run_name"],
        "status": run["status"],
        "start_time": run["start_time"]
      }
      
      # Add parameters
      row.update(run.get("params", {}))
      
      # Add metrics
      row.update(run.get("metrics", {}))
      
      writer.writerow(row)


def export_to_json(runs_data: list, output_path: str):
  """Export runs data to JSON format."""
  with open(output_path, 'w') as f:
    json.dump(runs_data, f, indent=2, default=str)


def main():
  parser = argparse.ArgumentParser(
    description="Export MLflow experiment results"
  )
  parser.add_argument(
    "--tracking-uri",
    help="MLflow tracking URI"
  )
  parser.add_argument(
    "--experiment",
    required=True,
    help="Experiment name to export"
  )
  parser.add_argument(
    "--output",
    required=True,
    help="Output file path"
  )
  parser.add_argument(
    "--format",
    choices=["csv", "json"],
    default="csv",
    help="Export format (default: csv)"
  )
  parser.add_argument(
    "--max-runs",
    type=int,
    default=100,
    help="Maximum number of runs to export (default: 100)"
  )
  
  args = parser.parse_args()
  
  if not is_mlflow_available():
    print("❌ Error: MLflow is not available. Install with: pip install mlflow")
    sys.exit(1)
  
  try:
    manager = ExperimentManager(tracking_uri=args.tracking_uri)
    
    print(f"📊 Exporting experiment '{args.experiment}'...")
    runs = manager.get_experiment_runs(args.experiment, max_results=args.max_runs)
    
    if not runs:
      print(f"❌ No runs found in experiment '{args.experiment}'")
      sys.exit(1)
    
    print(f"📋 Found {len(runs)} runs")
    
    # Convert runs to export format
    export_data = []
    for run in runs:
      export_data.append({
        "run_id": run["run_id"],
        "run_name": run.get("tags.mlflow.runName", run["run_id"]),
        "status": run["status"],
        "start_time": run["start_time"],
        "params": {k.replace("params.", ""): v for k, v in run.items() if k.startswith("params.")},
        "metrics": {k.replace("metrics.", ""): v for k, v in run.items() if k.startswith("metrics.")},
        "tags": {k.replace("tags.", ""): v for k, v in run.items() if k.startswith("tags.")}
      })
    
    # Export based on format
    if args.format == "csv":
      export_to_csv(export_data, args.output)
    elif args.format == "json":
      export_to_json(export_data, args.output)
    
    print(f"✅ Exported to: {args.output}")
    
  except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()