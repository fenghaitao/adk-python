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

"""Script to clean up MLflow runs and experiments."""

from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import yaml


def load_mlflow_config():
  """Load MLflow configuration."""
  config_path = Path(__file__).parent.parent / "config" / "mlflow_config.yaml"
  with open(config_path, 'r') as f:
    config = yaml.safe_load(f)
  return config["mlflow"]["tracking_uri"]


def list_experiments():
  """List all experiments."""
  experiments = mlflow.search_experiments()
  print("\n📊 Available Experiments:")
  for exp in experiments:
    print(f"  ID: {exp.experiment_id}, Name: {exp.name}")
  return experiments


def list_runs(experiment_id: str = None):
  """List runs in an experiment."""
  if experiment_id:
    runs = mlflow.search_runs(experiment_ids=[experiment_id])
    print(f"\n🏃 Runs in experiment {experiment_id}:")
  else:
    runs = mlflow.search_runs()
    print("\n🏃 All runs:")
  
  for _, run in runs.iterrows():
    print(f"  Run ID: {run['run_id'][:8]}... | "
          f"Name: {run.get('tags.mlflow.runName', 'N/A')} | "
          f"Status: {run['status']}")
  return runs


def delete_run(run_id: str):
  """Delete a specific run."""
  try:
    mlflow.delete_run(run_id)
    print(f"✅ Deleted run: {run_id}")
  except Exception as e:
    print(f"❌ Failed to delete run {run_id}: {e}")


def delete_experiment_runs(experiment_id: str):
  """Delete all runs in an experiment."""
  runs = mlflow.search_runs(experiment_ids=[experiment_id])
  
  if runs.empty:
    print(f"No runs found in experiment {experiment_id}")
    return
  
  print(f"Found {len(runs)} runs in experiment {experiment_id}")
  confirm = input("Delete all runs? (y/N): ")
  
  if confirm.lower() == 'y':
    for _, run in runs.iterrows():
      delete_run(run['run_id'])
    print(f"✅ Deleted all runs from experiment {experiment_id}")
  else:
    print("❌ Cancelled")


def delete_experiment(experiment_id: str):
  """Delete an entire experiment (and all its runs)."""
  try:
    # First delete all runs
    runs = mlflow.search_runs(experiment_ids=[experiment_id])
    for _, run in runs.iterrows():
      mlflow.delete_run(run['run_id'])
    
    # Then delete the experiment
    mlflow.delete_experiment(experiment_id)
    print(f"✅ Deleted experiment: {experiment_id}")
  except Exception as e:
    print(f"❌ Failed to delete experiment {experiment_id}: {e}")


def main():
  parser = argparse.ArgumentParser(description="Clean up MLflow runs and experiments")
  parser.add_argument("--list-experiments", action="store_true", 
                     help="List all experiments")
  parser.add_argument("--list-runs", metavar="EXP_ID", 
                     help="List runs in experiment (or all if no ID)")
  parser.add_argument("--delete-run", metavar="RUN_ID", 
                     help="Delete specific run")
  parser.add_argument("--delete-experiment-runs", metavar="EXP_ID", 
                     help="Delete all runs in experiment")
  parser.add_argument("--delete-experiment", metavar="EXP_ID", 
                     help="Delete entire experiment")
  parser.add_argument("--tracking-uri", 
                     help="Override tracking URI")
  
  args = parser.parse_args()
  
  # Set up MLflow
  tracking_uri = args.tracking_uri or load_mlflow_config()
  mlflow.set_tracking_uri(tracking_uri)
  print(f"🔗 Using tracking URI: {tracking_uri}")
  
  if args.list_experiments:
    list_experiments()
  
  elif args.list_runs is not None:
    if args.list_runs:
      list_runs(args.list_runs)
    else:
      list_runs()
  
  elif args.delete_run:
    delete_run(args.delete_run)
  
  elif args.delete_experiment_runs:
    delete_experiment_runs(args.delete_experiment_runs)
  
  elif args.delete_experiment:
    delete_experiment(args.delete_experiment)
  
  else:
    # Interactive mode
    print("🧹 MLflow Cleanup Tool")
    experiments = list_experiments()
    
    print("\nOptions:")
    print("1. List runs in an experiment")
    print("2. Delete specific run")
    print("3. Delete all runs in experiment")
    print("4. Delete entire experiment")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ")
    
    if choice == "1":
      exp_id = input("Enter experiment ID: ")
      list_runs(exp_id)
    
    elif choice == "2":
      run_id = input("Enter run ID: ")
      delete_run(run_id)
    
    elif choice == "3":
      exp_id = input("Enter experiment ID: ")
      delete_experiment_runs(exp_id)
    
    elif choice == "4":
      exp_id = input("Enter experiment ID: ")
      delete_experiment(exp_id)
    
    elif choice == "5":
      print("👋 Goodbye!")
    
    else:
      print("❌ Invalid choice")


if __name__ == "__main__":
  main()