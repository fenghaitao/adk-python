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

"""Experiment management utilities for MLflow integration."""

from __future__ import annotations

from typing import Dict, List, Optional

import mlflow
from mlflow.entities import Experiment, Run


class ExperimentManager:
  """Manages MLflow experiments for deepeval scoring."""
  
  def __init__(self, tracking_uri: Optional[str] = None):
    """Initialize experiment manager.
    
    Args:
      tracking_uri: MLflow tracking URI
    """
    if tracking_uri:
      mlflow.set_tracking_uri(tracking_uri)
  
  def list_experiments(self, device_filter: Optional[str] = None) -> List[Experiment]:
    """List all experiments, optionally filtered by device.
    
    Args:
      device_filter: Filter experiments by device name
    
    Returns:
      List of MLflow experiments
    """
    experiments = mlflow.search_experiments()
    
    if device_filter:
      experiments = [
        exp for exp in experiments 
        if device_filter in exp.name
      ]
    
    return experiments
  
  def get_experiment_runs(
      self,
      experiment_name: str,
      max_results: int = 100
  ) -> List[Run]:
    """Get runs for a specific experiment.
    
    Args:
      experiment_name: Name of the experiment
      max_results: Maximum number of runs to return
    
    Returns:
      List of MLflow runs
    """
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
      return []
    
    runs = mlflow.search_runs(
      experiment_ids=[experiment.experiment_id],
      max_results=max_results,
      order_by=["start_time DESC"]
    )
    
    return runs.to_dict('records') if not runs.empty else []
  
  def compare_runs(
      self,
      run_ids: List[str],
      metrics: Optional[List[str]] = None
  ) -> Dict:
    """Compare multiple runs.
    
    Args:
      run_ids: List of run IDs to compare
      metrics: Specific metrics to compare (if None, compares all)
    
    Returns:
      Comparison data
    """
    if not run_ids:
      return {}
    
    runs_data = []
    
    for run_id in run_ids:
      run = mlflow.get_run(run_id)
      run_data = {
        "run_id": run_id,
        "run_name": run.data.tags.get("mlflow.runName", run_id),
        "start_time": run.info.start_time,
        "status": run.info.status,
        "params": run.data.params,
        "metrics": run.data.metrics,
        "tags": run.data.tags
      }
      runs_data.append(run_data)
    
    # Filter metrics if specified
    if metrics:
      for run_data in runs_data:
        run_data["metrics"] = {
          k: v for k, v in run_data["metrics"].items() 
          if k in metrics
        }
    
    return {
      "runs": runs_data,
      "comparison_metrics": self._extract_comparison_metrics(runs_data)
    }
  
  def get_best_run(
      self,
      experiment_name: str,
      metric_name: str = "overall_score",
      ascending: bool = False
  ) -> Optional[Run]:
    """Get the best run from an experiment based on a metric.
    
    Args:
      experiment_name: Name of the experiment
      metric_name: Metric to optimize for
      ascending: Whether lower values are better
    
    Returns:
      Best run or None if no runs found
    """
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if not experiment:
      return None
    
    order = "ASC" if ascending else "DESC"
    runs = mlflow.search_runs(
      experiment_ids=[experiment.experiment_id],
      filter_string=f"metrics.{metric_name} IS NOT NULL",
      order_by=[f"metrics.{metric_name} {order}"],
      max_results=1
    )
    
    if runs.empty:
      return None
    
    return runs.iloc[0].to_dict()
  
  def delete_experiment(self, experiment_name: str) -> bool:
    """Delete an experiment.
    
    Args:
      experiment_name: Name of the experiment to delete
    
    Returns:
      True if successful, False otherwise
    """
    try:
      experiment = mlflow.get_experiment_by_name(experiment_name)
      if experiment:
        mlflow.delete_experiment(experiment.experiment_id)
        return True
      return False
    except Exception:
      return False
  
  def _extract_comparison_metrics(self, runs_data: List[Dict]) -> Dict:
    """Extract metrics for comparison across runs."""
    if not runs_data:
      return {}
    
    # Get all unique metrics
    all_metrics = set()
    for run_data in runs_data:
      all_metrics.update(run_data["metrics"].keys())
    
    comparison = {}
    for metric in all_metrics:
      values = []
      for run_data in runs_data:
        if metric in run_data["metrics"]:
          values.append(run_data["metrics"][metric])
      
      if values:
        comparison[metric] = {
          "min": min(values),
          "max": max(values),
          "avg": sum(values) / len(values),
          "count": len(values)
        }
    
    return comparison