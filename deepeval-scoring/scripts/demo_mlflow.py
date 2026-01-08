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

"""Demonstration script for MLflow integration."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracking.mlflow_tracker import MLflowTracker
from tracking.experiment_manager import ExperimentManager
from tracking.utils import is_mlflow_available


def demo_mlflow_integration():
  """Demonstrate MLflow integration features."""
  print("🔬 MLflow Integration Demo")
  print("=" * 50)
  
  # Check availability
  if not is_mlflow_available():
    print("❌ MLflow is not available. Please install MLflow first.")
    return
  
  print("✅ MLflow is available")
  
  # Create temporary tracking directory
  with tempfile.TemporaryDirectory() as temp_dir:
    tracking_uri = f"sqlite:///{Path(__file__).parent.parent}/mlflow.db"
    print(f"📁 Using local tracking URI: {tracking_uri}")
    
    # Initialize tracker
    tracker = MLflowTracker(tracking_uri=tracking_uri)
    print("🔧 Initialized MLflow tracker")
    
    # Start a demo run
    run_id = tracker.start_run(
      device_name="demo_device",
      model="demo_model",
      scoring_mode="hybrid",
      workdir="/tmp/demo",
      agent="demo_agent"
    )
    print(f"🚀 Started run: {run_id}")
    
    # Log some demo metrics
    demo_results = {
      "code_results": {
        "overall_score": 0.85,
        "metrics": {
          "code_correctness": {"score": 0.90, "success": True, "threshold": 0.8},
          "test_coverage": {"score": 0.80, "success": True, "threshold": 0.7}
        }
      },
      "deterministic_results": {
        "overall_score": 0.75,
        "component_scores": {
          "build_success": 1.0,
          "register_coverage": 0.80,
          "test_coverage": 0.70
        },
        "details": {
          "registers_found": 10,
          "methods_found": 5,
          "test_files_found": 3
        }
      }
    }
    
    tracker.log_metrics(
      code_results=demo_results["code_results"],
      deterministic_results=demo_results["deterministic_results"],
      scoring_mode="hybrid"
    )
    print("📊 Logged demo metrics")
    
    # Log demo artifacts
    demo_report = "# Demo Report\n\nThis is a demo evaluation report."
    tracker.log_artifacts(
      workdir="/tmp/demo",
      report_content=demo_report,
      report_format="markdown",
      code_results=demo_results["code_results"],
      deterministic_results=demo_results["deterministic_results"]
    )
    print("📁 Logged demo artifacts")
    
    # End run
    tracker.end_run("FINISHED")
    print("🏁 Ended run")
    
    # Demonstrate experiment management
    print("\n📊 Experiment Management Demo")
    print("-" * 30)
    
    manager = ExperimentManager(tracking_uri=tracking_uri)
    
    # List experiments
    experiments = manager.list_experiments()
    print(f"📋 Found {len(experiments)} experiments:")
    for exp in experiments:
      print(f"  • {exp.name}")
    
    # Get runs from the demo experiment
    if experiments:
      exp_name = experiments[0].name
      runs = manager.get_experiment_runs(exp_name)
      print(f"🏃 Found {len(runs)} runs in '{exp_name}'")
      
      if runs:
        # Show run details
        run = runs[0]
        print(f"  • Run: {run.get('tags.mlflow.runName', 'N/A')}")
        print(f"    Overall Score: {run.get('metrics.overall_score', 'N/A')}")
        print(f"    Model: {run.get('params.model', 'N/A')}")
    
    print("\n✅ Demo completed successfully!")
    print("💡 To view results in MLflow UI:")
    print("   Already running at http://localhost:5002")
    print("   Or start manually: mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5002")


if __name__ == "__main__":
  demo_mlflow_integration()