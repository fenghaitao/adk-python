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

"""Extract session data from MLflow runs for optimizer.

This tool extracts session_data.json artifacts from MLflow runs and combines
them into a format suitable for optimize_instructions.py and
optimize_memory_file.py.

Usage:
  # Extract all sessions from an experiment
  python extract_mlflow_sessions.py --experiment wdt-evaluation --output sessions.json
  
  # Extract sessions with score below threshold
  python extract_mlflow_sessions.py --experiment wdt-evaluation --max-score 0.8 --output sessions.json
  
  # Extract from specific runs
  python extract_mlflow_sessions.py --run-ids abc123,def456 --output sessions.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
  import mlflow
  from mlflow.tracking import MlflowClient
except ImportError:
  print("❌ Error: MLflow is not installed. Install with: pip install mlflow")
  sys.exit(1)


def extract_sessions_from_experiment(
    experiment_name: str,
    tracking_uri: Optional[str] = None,
    max_score: Optional[float] = None,
    min_score: Optional[float] = None
) -> List[Dict]:
  """Extract session data from all runs in an experiment.
  
  Args:
    experiment_name: Name of the MLflow experiment
    tracking_uri: MLflow tracking URI (optional)
    max_score: Only include runs with score <= max_score
    min_score: Only include runs with score >= min_score
    
  Returns:
    List of session data dictionaries
  """
  if tracking_uri:
    mlflow.set_tracking_uri(tracking_uri)
  
  client = MlflowClient()
  
  # Get experiment
  experiment = client.get_experiment_by_name(experiment_name)
  if not experiment:
    print(f"❌ Error: Experiment '{experiment_name}' not found")
    return []
  
  print(f"📊 Extracting sessions from experiment: {experiment_name}")
  
  # Get all runs
  runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    order_by=["start_time DESC"]
  )
  
  sessions = []
  for run in runs:
    # Check score filters
    if max_score is not None or min_score is not None:
      overall_score = run.data.metrics.get("overall_score")
      if overall_score is None:
        continue
      if max_score is not None and overall_score > max_score:
        continue
      if min_score is not None and overall_score < min_score:
        continue
    
    # Extract session data
    session_data = extract_session_from_run(run.info.run_id, client)
    if session_data:
      sessions.append(session_data)
      print(f"  ✓ Extracted run {run.info.run_id[:8]} (score: {run.data.metrics.get('overall_score', 0):.1%})")
  
  return sessions


def extract_sessions_from_runs(
    run_ids: List[str],
    tracking_uri: Optional[str] = None
) -> List[Dict]:
  """Extract session data from specific runs.
  
  Args:
    run_ids: List of MLflow run IDs
    tracking_uri: MLflow tracking URI (optional)
    
  Returns:
    List of session data dictionaries
  """
  if tracking_uri:
    mlflow.set_tracking_uri(tracking_uri)
  
  client = MlflowClient()
  
  sessions = []
  for run_id in run_ids:
    session_data = extract_session_from_run(run_id, client)
    if session_data:
      sessions.append(session_data)
      print(f"  ✓ Extracted run {run_id[:8]}")
    else:
      print(f"  ✗ Failed to extract run {run_id[:8]}")
  
  return sessions


def extract_session_from_run(
    run_id: str,
    client: MlflowClient
) -> Optional[Dict]:
  """Extract session data from a single run.
  
  Args:
    run_id: MLflow run ID
    client: MLflow client
    
  Returns:
    Session data dictionary or None if not found
  """
  try:
    # Download session_data.json artifact
    artifact_path = "session_data/session_data.json"
    local_path = client.download_artifacts(run_id, artifact_path)
    
    # Load session data
    with open(local_path, 'r') as f:
      session_data = json.load(f)
    
    return session_data
    
  except Exception as e:
    print(f"  ⚠️  Warning: Could not extract session data from run {run_id[:8]}: {e}")
    return None


def main():
  parser = argparse.ArgumentParser(
    description="Extract session data from MLflow runs for optimizer"
  )
  parser.add_argument(
    "--experiment",
    help="MLflow experiment name"
  )
  parser.add_argument(
    "--run-ids",
    help="Comma-separated list of run IDs"
  )
  parser.add_argument(
    "--tracking-uri",
    help="MLflow tracking URI (overrides default)"
  )
  parser.add_argument(
    "--max-score",
    type=float,
    help="Only include runs with score <= max_score"
  )
  parser.add_argument(
    "--min-score",
    type=float,
    help="Only include runs with score >= min_score"
  )
  parser.add_argument(
    "--output",
    default="sessions.json",
    help="Output file path (default: sessions.json)"
  )
  
  args = parser.parse_args()
  
  # Validate arguments
  if not args.experiment and not args.run_ids:
    print("❌ Error: Must specify either --experiment or --run-ids")
    sys.exit(1)
  
  if args.experiment and args.run_ids:
    print("❌ Error: Cannot specify both --experiment and --run-ids")
    sys.exit(1)
  
  # Extract sessions
  sessions = []
  
  if args.experiment:
    sessions = extract_sessions_from_experiment(
      experiment_name=args.experiment,
      tracking_uri=args.tracking_uri,
      max_score=args.max_score,
      min_score=args.min_score
    )
  elif args.run_ids:
    run_ids = [rid.strip() for rid in args.run_ids.split(",")]
    sessions = extract_sessions_from_runs(
      run_ids=run_ids,
      tracking_uri=args.tracking_uri
    )
  
  if not sessions:
    print("❌ No sessions extracted")
    sys.exit(1)
  
  # Save to file
  output_path = Path(args.output)
  with open(output_path, 'w') as f:
    json.dump(sessions, f, indent=2)
  
  print(f"\n✅ Extracted {len(sessions)} sessions to: {output_path}")
  
  # Print summary
  if sessions:
    scores = [s.get("score", 0) for s in sessions]
    avg_score = sum(scores) / len(scores)
    print(f"📊 Average score: {avg_score:.1%}")
    print(f"📊 Score range: {min(scores):.1%} - {max(scores):.1%}")


if __name__ == "__main__":
  main()
